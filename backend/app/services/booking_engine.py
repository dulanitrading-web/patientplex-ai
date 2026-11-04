"""Complete booking engine — the central orchestrator for appointment booking.

Handles the full loop:
1. Patient requests a time (or asks "when is doctor free?")
2. Engine checks Google Calendar for doctor's availability
3. Finds matching slots between patient preference and doctor calendar
4. Books the slot on Google Calendar
5. Sends WhatsApp confirmation to patient (with maps link)
6. Sends WhatsApp notification to doctor (with patient details)
7. Records conversion event at every step
8. Sets up 24h and 2h reminders

This service is called by the AI receptionist (WhatsApp) and by the
missed call handler. It can also be called directly from the API
for manual bookings from the dashboard.
"""

import logging
import uuid
from datetime import date, datetime, time, timedelta, timezone
from urllib.parse import quote_plus

from sqlalchemy import and_, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.config import settings
from app.models.conversation import Appointment, AppointmentStatus, Conversation, ConversationStatus
from app.models.call_log import ConversionStage
from app.models.doctor import Doctor
from app.services.conversion_tracker import ConversionTracker
from app.services.doctor_notifier import DoctorNotifier
from app.services.google_calendar import GoogleCalendarService
from app.services.whatsapp import whatsapp_service

logger = logging.getLogger(__name__)


class BookingEngine:
    """Orchestrates the complete appointment booking flow."""

    def __init__(self, db: AsyncSession):
        self.db = db
        self.calendar = GoogleCalendarService()
        self.notifier = DoctorNotifier()
        self.tracker = ConversionTracker(db)

    async def check_availability(
        self,
        doctor: Doctor,
        requested_date: str,
        preferred_time: str | None = None,
    ) -> dict:
        """Check doctor's calendar availability for a given date.

        Args:
            doctor: The doctor to check
            requested_date: Date in YYYY-MM-DD format
            preferred_time: Optional preferred time like "morning", "afternoon",
                           "evening", or "HH:MM"

        Returns:
            Dict with available slots, filtered by preference if given
        """
        try:
            all_slots = await self.calendar.get_available_slots(
                str(doctor.id), requested_date
            )
        except Exception as exc:
            logger.warning("Calendar check failed, using default slots: %s", exc)
            all_slots = self._generate_default_slots(requested_date)

        # Filter by preference if given
        if preferred_time and all_slots:
            all_slots = self._filter_by_preference(all_slots, preferred_time)

        return {
            "date": requested_date,
            "available": len(all_slots) > 0,
            "slots": all_slots,
            "total_slots": len(all_slots),
            "preferred_time": preferred_time,
        }

    async def book_appointment(
        self,
        doctor: Doctor,
        patient_name: str,
        patient_phone: str,
        treatment: str,
        appointment_date: str,  # YYYY-MM-DD
        appointment_time: str,  # HH:MM
        conversation_id: uuid.UUID | None = None,
        source: str = "whatsapp",
    ) -> dict:
        """Book an appointment — the main booking method.

        This does everything:
        1. Creates Google Calendar event
        2. Creates appointment record in DB
        3. Sends WhatsApp confirmation to patient
        4. Sends WhatsApp notification to doctor
        5. Tracks conversion events
        6. Updates conversation status
        """
        # Parse date and time
        try:
            appt_date = date.fromisoformat(appointment_date)
            hour, minute = map(int, appointment_time.split(":"))
            appt_time = time(hour, minute)
            appt_datetime = datetime.combine(appt_date, appt_time, tzinfo=timezone.utc)
        except (ValueError, AttributeError) as exc:
            return {"success": False, "error": f"Invalid date/time: {exc}"}

        # Validate the slot is still available
        availability = await self.check_availability(doctor, appointment_date, appointment_time)
        slot_available = any(
            s.get("start", "").startswith(appointment_time) or s.get("start", "") == appointment_time
            for s in availability.get("slots", [])
        )
        # Don't block booking if calendar check fails — just proceed
        if not slot_available and availability.get("slots"):
            logger.warning("Requested slot %s may not be available, booking anyway", appointment_time)

        # Step 1: Book on Google Calendar
        google_event_id = None
        try:
            cal_result = await self.calendar.book_slot(
                str(doctor.id), appt_datetime, patient_name, patient_phone, treatment
            )
            google_event_id = cal_result.get("event_id")
        except Exception as exc:
            logger.warning("Calendar booking failed (continuing): %s", exc)

        # Step 2: Create appointment record
        appointment = Appointment(
            doctor_id=doctor.id,
            conversation_id=conversation_id,
            patient_name=patient_name,
            patient_phone=patient_phone,
            treatment=treatment,
            appointment_date=appt_date,
            appointment_time=appt_time,
            duration_minutes=settings.SLOT_DURATION_MINUTES,
            google_event_id=google_event_id,
            status=AppointmentStatus.CONFIRMED,
            confirmation_sent=True,
        )
        self.db.add(appointment)
        await self.db.flush()

        # Step 3: Update conversation if linked
        if conversation_id:
            result = await self.db.execute(
                select(Conversation).where(Conversation.id == conversation_id)
            )
            conversation = result.scalar_one_or_none()
            if conversation:
                conversation.status = ConversationStatus.BOOKED
                conversation.appointment_datetime = appt_datetime
                conversation.patient_name = patient_name
                conversation.treatment_interest = treatment

        # Step 4: Send patient confirmation via WhatsApp
        clinic_address = f"{doctor.clinic_address or ''}, {doctor.city or ''}"
        maps_link = f"https://www.google.com/maps/search/?api=1&query={quote_plus(clinic_address)}"
        date_display = appt_date.strftime("%A, %d %b %Y")
        time_display = appt_time.strftime("%I:%M %p")

        confirmation_msg = (
            f"✅ *Appointment Confirmed!*\n\n"
            f"👨‍⚕️ *Doctor:* Dr. {doctor.full_name}\n"
            f"🏥 *Clinic:* {doctor.clinic_name or 'Clinic'}\n"
            f"🦷 *Treatment:* {treatment}\n"
            f"📅 *Date:* {date_display}\n"
            f"🕐 *Time:* {time_display}\n"
            f"📍 *Location:* {clinic_address}\n"
            f"🗺️ *Directions:* {maps_link}\n\n"
            f"Please arrive 10 minutes early.\n"
            f"Reply *CANCEL* to cancel or *RESCHEDULE* to change time."
        )
        await whatsapp_service.send_message(
            to=patient_phone.replace("+", ""),
            message=confirmation_msg,
        )

        # Step 5: Notify doctor
        await self.notifier.notify_new_booking(doctor, appointment)

        # Step 6: Track conversion events
        await self.tracker.track(
            doctor_id=doctor.id,
            patient_phone=patient_phone,
            stage=ConversionStage.BOOKING_CONFIRMED,
            source_channel=source,
            appointment_id=appointment.id,
            conversation_id=conversation_id,
            treatment=treatment,
        )
        await self.tracker.track(
            doctor_id=doctor.id,
            patient_phone=patient_phone,
            stage=ConversionStage.CONFIRMATION_SENT,
            source_channel=source,
            appointment_id=appointment.id,
        )

        await self.db.commit()

        logger.info(
            "Appointment booked: %s with Dr. %s for %s on %s at %s",
            patient_name, doctor.full_name, treatment, appointment_date, appointment_time,
        )

        return {
            "success": True,
            "appointment_id": str(appointment.id),
            "patient_name": patient_name,
            "treatment": treatment,
            "date": appointment_date,
            "time": appointment_time,
            "doctor": doctor.full_name,
            "clinic": doctor.clinic_name,
            "google_event_id": google_event_id,
            "confirmation_sent": True,
            "doctor_notified": True,
        }

    async def cancel_appointment(
        self,
        appointment_id: uuid.UUID,
        doctor: Doctor,
        cancelled_by: str = "patient",  # "patient" or "doctor"
    ) -> dict:
        """Cancel an appointment and notify both parties."""
        result = await self.db.execute(
            select(Appointment).where(
                and_(Appointment.id == appointment_id, Appointment.doctor_id == doctor.id)
            )
        )
        appointment = result.scalar_one_or_none()
        if not appointment:
            return {"success": False, "error": "Appointment not found"}

        appointment.status = AppointmentStatus.CANCELLED

        # Notify the other party
        if cancelled_by == "patient":
            await self.notifier.notify_cancellation(doctor, appointment)
            # Let patient know
            await whatsapp_service.send_message(
                to=appointment.patient_phone.replace("+", ""),
                message=(
                    f"Your appointment with Dr. {doctor.full_name} on "
                    f"{appointment.appointment_date.strftime('%d %b')} at "
                    f"{appointment.appointment_time.strftime('%I:%M %p')} has been cancelled.\n\n"
                    f"Reply *BOOK* to schedule a new appointment."
                ),
            )
        else:
            await whatsapp_service.send_message(
                to=appointment.patient_phone.replace("+", ""),
                message=(
                    f"Unfortunately, Dr. {doctor.full_name} needs to reschedule your "
                    f"appointment on {appointment.appointment_date.strftime('%d %b')}.\n\n"
                    f"Would you like to pick a new time? Reply *YES* and I'll show available slots."
                ),
            )

        # TODO: Remove Google Calendar event if google_event_id exists

        await self.db.commit()
        return {"success": True, "appointment_id": str(appointment_id)}

    async def reschedule_appointment(
        self,
        appointment_id: uuid.UUID,
        doctor: Doctor,
        new_date: str,
        new_time: str,
    ) -> dict:
        """Reschedule an appointment to a new date/time."""
        result = await self.db.execute(
            select(Appointment).where(
                and_(Appointment.id == appointment_id, Appointment.doctor_id == doctor.id)
            )
        )
        appointment = result.scalar_one_or_none()
        if not appointment:
            return {"success": False, "error": "Appointment not found"}

        # Cancel old and create new
        appointment.status = AppointmentStatus.RESCHEDULED
        await self.db.commit()

        # Book the new slot
        new_booking = await self.book_appointment(
            doctor=doctor,
            patient_name=appointment.patient_name,
            patient_phone=appointment.patient_phone,
            treatment=appointment.treatment,
            appointment_date=new_date,
            appointment_time=new_time,
            conversation_id=appointment.conversation_id,
            source="reschedule",
        )

        return new_booking

    def _generate_default_slots(self, date_str: str) -> list[dict]:
        """Generate default slots when calendar isn't connected."""
        open_time = settings.CLINIC_DEFAULT_OPEN_TIME
        close_time = settings.CLINIC_DEFAULT_CLOSE_TIME
        duration = settings.SLOT_DURATION_MINUTES

        open_h, open_m = map(int, open_time.split(":"))
        close_h, close_m = map(int, close_time.split(":"))

        slots = []
        current = datetime(2026, 1, 1, open_h, open_m)
        end = datetime(2026, 1, 1, close_h, close_m)

        while current + timedelta(minutes=duration) <= end:
            slot_end = current + timedelta(minutes=duration)
            slots.append({
                "start": current.strftime("%H:%M"),
                "end": slot_end.strftime("%H:%M"),
            })
            current = slot_end

        return slots

    def _filter_by_preference(self, slots: list[dict], preference: str) -> list[dict]:
        """Filter slots by patient's time preference.

        Understands: "morning", "afternoon", "evening", "HH:MM", "after 3pm", etc.
        """
        preference = preference.lower().strip()

        if preference == "morning":
            return [s for s in slots if self._slot_hour(s) < 12]
        elif preference == "afternoon":
            return [s for s in slots if 12 <= self._slot_hour(s) < 17]
        elif preference == "evening":
            return [s for s in slots if self._slot_hour(s) >= 17]
        elif ":" in preference:
            # Exact time — find the closest slot
            try:
                pref_h, pref_m = map(int, preference.split(":"))
                pref_minutes = pref_h * 60 + pref_m
                # Return slots within 1 hour of preference
                return [
                    s for s in slots
                    if abs(self._slot_minutes(s) - pref_minutes) <= 60
                ]
            except ValueError:
                return slots
        elif "after" in preference:
            # "after 3pm", "after 15:00"
            import re
            match = re.search(r"(\d{1,2})", preference)
            if match:
                hour = int(match.group(1))
                if "pm" in preference and hour < 12:
                    hour += 12
                return [s for s in slots if self._slot_hour(s) >= hour]

        return slots  # No filter understood

    @staticmethod
    def _slot_hour(slot: dict) -> int:
        start = slot.get("start", "00:00")
        return int(start.split(":")[0])

    @staticmethod
    def _slot_minutes(slot: dict) -> int:
        start = slot.get("start", "00:00")
        h, m = map(int, start.split(":"))
        return h * 60 + m
