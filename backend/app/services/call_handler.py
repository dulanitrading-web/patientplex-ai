"""Missed call detection and automated WhatsApp follow-up.

Flow:
1. Patient calls clinic number (Twilio/Exotel virtual number)
2. Call is forwarded to doctor's real phone
3. If doctor doesn't answer (missed/busy) → system detects this
4. Within 30 seconds, patient gets a WhatsApp message:
   "Hi! Sorry we missed your call at [clinic name]. Our AI assistant
    can help you book an appointment right now. What treatment are
    you looking for?"
5. AI receptionist takes over from there → books appointment
6. Doctor gets WhatsApp notification with patient details + booked time
7. Google Calendar event created
8. Conversion tracked at every step
"""

import asyncio
import logging
from datetime import datetime, timezone
from uuid import UUID

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.config import settings
from app.models.call_log import CallDirection, CallLog, CallStatus, ConversionEvent, ConversionStage
from app.models.conversation import Conversation, ConversationStatus
from app.models.doctor import Doctor
from app.services.whatsapp import whatsapp_service
from app.services.conversion_tracker import ConversionTracker

logger = logging.getLogger(__name__)


class CallHandler:
    """Handles inbound calls, missed call detection, and automated follow-up."""

    def __init__(self, db: AsyncSession):
        self.db = db
        self.tracker = ConversionTracker(db)

    async def handle_inbound_call(
        self,
        caller_phone: str,
        clinic_phone: str,
        call_sid: str,
        doctor_id: UUID | None = None,
    ) -> CallLog:
        """Log an inbound call when it starts ringing.

        Called by the Twilio/Exotel webhook when a call comes in.
        """
        # Find the doctor by their clinic phone number
        doctor = await self._find_doctor_by_phone(clinic_phone, doctor_id)
        if not doctor:
            logger.warning("No doctor found for clinic phone %s", clinic_phone)
            # Still log the call
            doctor_id_val = doctor_id or UUID("00000000-0000-0000-0000-000000000000")
        else:
            doctor_id_val = doctor.id

        call_log = CallLog(
            doctor_id=doctor_id_val,
            caller_phone=caller_phone,
            clinic_phone=clinic_phone,
            direction=CallDirection.INBOUND,
            status=CallStatus.RINGING,
            started_at=datetime.now(timezone.utc),
            platform_call_sid=call_sid,
            platform_provider=settings.CALL_PROVIDER,
        )
        self.db.add(call_log)
        await self.db.flush()

        # Track conversion event
        await self.tracker.track(
            doctor_id=doctor_id_val,
            patient_phone=caller_phone,
            stage=ConversionStage.CALL_ATTEMPTED,
            source_channel="call",
            call_log_id=call_log.id,
        )

        return call_log

    async def handle_call_completed(
        self,
        call_sid: str,
        status: str,
        duration: int = 0,
        recording_url: str | None = None,
    ) -> CallLog | None:
        """Handle call completion — detect missed calls and trigger WhatsApp.

        Called by the Twilio/Exotel status callback webhook.

        Args:
            call_sid: Platform call identifier
            status: "completed", "no-answer", "busy", "failed", "canceled"
            duration: Call duration in seconds
            recording_url: URL of call recording if enabled
        """
        # Find the call log
        result = await self.db.execute(
            select(CallLog).where(CallLog.platform_call_sid == call_sid)
        )
        call_log = result.scalar_one_or_none()
        if not call_log:
            logger.error("Call log not found for SID %s", call_sid)
            return None

        # Update call log
        call_log.ended_at = datetime.now(timezone.utc)
        call_log.duration_seconds = duration
        if recording_url:
            call_log.recording_url = recording_url

        # Map platform status to our enum
        if status in ("completed",) and duration > 0:
            call_log.status = CallStatus.ANSWERED
            await self.tracker.track(
                doctor_id=call_log.doctor_id,
                patient_phone=call_log.caller_phone,
                stage=ConversionStage.CALL_CONNECTED,
                source_channel="call",
                call_log_id=call_log.id,
                extra_data={"duration": duration},
            )
        elif status in ("no-answer", "canceled"):
            call_log.status = CallStatus.MISSED
            call_log.direction = CallDirection.MISSED
            await self._handle_missed_call(call_log)
        elif status == "busy":
            call_log.status = CallStatus.BUSY
            await self._handle_missed_call(call_log)
        elif status == "failed":
            call_log.status = CallStatus.FAILED
        else:
            call_log.status = CallStatus.MISSED
            await self._handle_missed_call(call_log)

        await self.db.commit()
        return call_log

    async def _handle_missed_call(self, call_log: CallLog) -> None:
        """Handle a missed call by sending an immediate WhatsApp message.

        This is the KEY conversion moment — a missed call is a warm lead
        that's about to go cold. We have ~30 seconds to recover them.
        """
        logger.info(
            "Missed call from %s to doctor %s — triggering WhatsApp follow-up",
            call_log.caller_phone, call_log.doctor_id,
        )

        # Track missed call event
        await self.tracker.track(
            doctor_id=call_log.doctor_id,
            patient_phone=call_log.caller_phone,
            stage=ConversionStage.CALL_MISSED,
            source_channel="call",
            call_log_id=call_log.id,
        )

        # Find the doctor for personalization
        result = await self.db.execute(
            select(Doctor).where(Doctor.id == call_log.doctor_id)
        )
        doctor = result.scalar_one_or_none()
        if not doctor:
            return

        clinic_name = doctor.clinic_name or f"Dr. {doctor.full_name}'s clinic"

        # Send WhatsApp message to the patient
        message = (
            f"Hi! We noticed you just called {clinic_name}. "
            f"Sorry we couldn't pick up right now. 😊\n\n"
            f"I'm the AI assistant for Dr. {doctor.full_name}. "
            f"I can help you book an appointment right away!\n\n"
            f"What treatment are you looking for? "
            f"Or just tell me when you'd like to visit, and I'll check available slots."
        )

        result = await whatsapp_service.send_message(
            to=call_log.caller_phone,
            message=message,
        )

        if "error" not in result:
            call_log.whatsapp_followup_sent = True
            call_log.status = CallStatus.WHATSAPP_TRIGGERED

            # Create a conversation so the AI receptionist picks it up
            conversation = Conversation(
                doctor_id=doctor.id,
                patient_phone=call_log.caller_phone,
                status=ConversationStatus.ACTIVE,
                source="missed_call",
                messages=[{
                    "role": "assistant",
                    "content": message,
                    "timestamp": datetime.now(timezone.utc).isoformat(),
                }],
            )
            self.db.add(conversation)
            await self.db.flush()

            call_log.conversation_id = conversation.id

            # Track WhatsApp triggered
            await self.tracker.track(
                doctor_id=doctor.id,
                patient_phone=call_log.caller_phone,
                stage=ConversionStage.WHATSAPP_STARTED,
                source_channel="missed_call",
                call_log_id=call_log.id,
                conversation_id=conversation.id,
            )

            logger.info("WhatsApp follow-up sent to %s for missed call", call_log.caller_phone)
        else:
            logger.error("Failed to send WhatsApp follow-up: %s", result)

    async def _find_doctor_by_phone(
        self, clinic_phone: str, doctor_id: UUID | None = None
    ) -> Doctor | None:
        """Find doctor by their registered phone/WhatsApp number or by ID."""
        if doctor_id:
            result = await self.db.execute(select(Doctor).where(Doctor.id == doctor_id))
            return result.scalar_one_or_none()

        # Try matching by phone number (strip formatting)
        clean = clinic_phone.replace("+", "").replace(" ", "").replace("-", "")
        result = await self.db.execute(
            select(Doctor).where(
                Doctor.whatsapp_number.contains(clean[-10:])
                | Doctor.phone.contains(clean[-10:])
            )
        )
        return result.scalar_one_or_none()


class TwilioVoiceHandler:
    """Generate Twilio TwiML for call routing.

    The call flow:
    1. Patient calls the Twilio virtual number
    2. Twilio asks our webhook for instructions (TwiML)
    3. We tell Twilio to dial the doctor's real phone
    4. If doctor doesn't answer in 20 seconds → play a message + hang up
    5. Status callback fires → we detect missed call → WhatsApp follow-up
    """

    @staticmethod
    def generate_call_twiml(doctor: Doctor) -> str:
        """Generate TwiML to forward the call to the doctor.

        Returns XML string for Twilio to execute.
        """
        doctor_phone = doctor.whatsapp_number or doctor.phone
        clinic_name = doctor.clinic_name or f"Dr. {doctor.full_name}'s clinic"
        callback_url = f"{settings.GOOGLE_REDIRECT_URI.rsplit('/', 3)[0]}/api/v1/calls/status"

        return f"""<?xml version="1.0" encoding="UTF-8"?>
<Response>
    <Dial timeout="20" action="{callback_url}" method="POST"
          record="record-from-answer-dual" recordingStatusCallback="{callback_url}/recording">
        <Number>{doctor_phone}</Number>
    </Dial>
    <Say voice="Polly.Aditi" language="en-IN">
        Thank you for calling {clinic_name}.
        The doctor is currently busy. We will send you a WhatsApp message
        shortly to help you book an appointment. Thank you!
    </Say>
</Response>"""

    @staticmethod
    def generate_missed_call_twiml(clinic_name: str) -> str:
        """TwiML response when call goes to voicemail/missed."""
        return f"""<?xml version="1.0" encoding="UTF-8"?>
<Response>
    <Say voice="Polly.Aditi" language="en-IN">
        Thank you for calling {clinic_name}.
        We will reach you on WhatsApp shortly to help you book an appointment.
        Thank you!
    </Say>
</Response>"""
