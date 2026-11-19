"""Call handling webhook endpoints for Twilio/Exotel integration.

These endpoints receive webhooks from the voice provider when:
1. An inbound call arrives → we return TwiML to forward it to the doctor
2. The call ends → we detect missed calls and trigger WhatsApp follow-up
3. A recording is ready → we store the URL
"""

import logging
from datetime import datetime, timezone
from uuid import UUID

from fastapi import APIRouter, Depends, Form, HTTPException, Query, Request, Response
from sqlalchemy import and_, func, select
from sqlalchemy.ext.asyncio import AsyncSession
from twilio.request_validator import RequestValidator

import os
from slowapi import Limiter
from slowapi.util import get_remote_address

from app.api.v1.auth import get_current_doctor
from app.core.config import settings

limiter = Limiter(key_func=get_remote_address, enabled=os.environ.get("TESTING", "").lower() != "true")
from app.db.session import get_db
from app.models.call_log import CallDirection, CallLog, CallStatus
from app.models.doctor import Doctor
from app.services.call_handler import CallHandler, TwilioVoiceHandler
from app.services.call_tracking import call_tracking_service

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/calls", tags=["calls"])


async def verify_twilio_signature(request: Request) -> None:
    """Validate that the request genuinely came from Twilio."""
    auth_token = settings.TWILIO_AUTH_TOKEN
    if not auth_token:
        logger.warning(
            "TWILIO_AUTH_TOKEN is empty — skipping webhook signature verification (dev mode)"
        )
        return

    validator = RequestValidator(auth_token)
    signature = request.headers.get("X-Twilio-Signature", "")
    url = str(request.url)
    form = await request.form()
    params = {k: v for k, v in form.items()}

    if not validator.validate(url, params, signature):
        raise HTTPException(status_code=403, detail="Invalid Twilio signature")


@router.post("/incoming", dependencies=[Depends(verify_twilio_signature)])
@limiter.limit("30/minute")
async def handle_incoming_call(
    request: Request,
    db: AsyncSession = Depends(get_db),
):
    """Twilio voice webhook — called when a patient dials the virtual number.

    Returns TwiML that:
    1. Forwards the call to the doctor's real phone
    2. Records the call
    3. Sets a callback URL for when the call ends
    """
    form = await request.form()
    caller = form.get("From", "")
    called = form.get("To", "")
    call_sid = form.get("CallSid", "")

    logger.info("Incoming call: %s → %s (SID: %s)", caller, called, call_sid)

    handler = CallHandler(db)
    call_log = await handler.handle_inbound_call(
        caller_phone=caller,
        clinic_phone=called,
        call_sid=call_sid,
    )
    await db.commit()

    # Find doctor to forward to
    result = await db.execute(
        select(Doctor).where(
            Doctor.whatsapp_number.contains(called[-10:])
            | Doctor.phone.contains(called[-10:])
        )
    )
    doctor = result.scalar_one_or_none()

    if doctor:
        twiml = TwilioVoiceHandler.generate_call_twiml(doctor)
    else:
        twiml = TwilioVoiceHandler.generate_missed_call_twiml("the clinic")

    return Response(content=twiml, media_type="application/xml")


@router.post("/status", dependencies=[Depends(verify_twilio_signature)])
@limiter.limit("30/minute")
async def handle_call_status(
    request: Request,
    db: AsyncSession = Depends(get_db),
):
    """Twilio status callback — called when a call completes or fails.

    This is where we detect missed calls and trigger the WhatsApp follow-up.
    """
    form = await request.form()
    call_sid = form.get("CallSid", "")
    call_status = form.get("CallStatus", form.get("DialCallStatus", ""))
    duration = int(form.get("CallDuration", form.get("DialCallDuration", "0")))
    recording_url = form.get("RecordingUrl", None)

    logger.info("Call status: SID=%s status=%s duration=%ds", call_sid, call_status, duration)

    handler = CallHandler(db)
    call_log = await handler.handle_call_completed(
        call_sid=call_sid,
        status=call_status,
        duration=duration,
        recording_url=recording_url,
    )

    return {"status": "ok"}


@router.post("/status/recording")
async def handle_recording_ready(
    request: Request,
    db: AsyncSession = Depends(get_db),
):
    """Twilio recording status callback — called when a call recording is ready."""
    form = await request.form()
    call_sid = form.get("CallSid", "")
    recording_url = form.get("RecordingUrl", "")

    if call_sid and recording_url:
        result = await db.execute(
            select(CallLog).where(CallLog.platform_call_sid == call_sid)
        )
        call_log = result.scalar_one_or_none()
        if call_log:
            call_log.recording_url = recording_url
            await db.commit()

    return {"status": "ok"}


@router.post("/sms", dependencies=[Depends(verify_twilio_signature)])
@limiter.limit("30/minute")
async def handle_incoming_sms(
    request: Request,
    db: AsyncSession = Depends(get_db),
):
    """Twilio SMS webhook — processes incoming text messages through AI receptionist.

    When a patient sends an SMS to the Twilio number, this endpoint:
    1. Identifies which doctor the number belongs to
    2. Passes the message to the AI receptionist
    3. Sends back the AI response as an SMS reply
    """
    form = await request.form()
    sender = form.get("From", "")
    to_number = form.get("To", "")
    body = form.get("Body", "").strip()

    if not sender or not body:
        return Response(content="<Response></Response>", media_type="application/xml")

    logger.info("Incoming SMS from %s to %s: %s", sender, to_number, body[:50])

    # Find the doctor this number belongs to
    clean_to = to_number.replace("+", "").replace(" ", "")[-10:]
    result = await db.execute(
        select(Doctor).where(
            Doctor.whatsapp_number.contains(clean_to)
            | Doctor.phone.contains(clean_to)
        )
    )
    doctor = result.scalar_one_or_none()

    if doctor:
        try:
            from app.services.ai_receptionist import AIReceptionist
            receptionist = AIReceptionist(doctor, db)
            response_text = await receptionist.process_message(sender, body)
        except Exception as exc:
            logger.error("AI receptionist error: %s", exc)
            response_text = f"Thank you for reaching out to {doctor.clinic_name or 'our clinic'}. We'll get back to you shortly."
    else:
        response_text = "Thank you for your message. We'll get back to you shortly."

    # Return TwiML response
    twiml = f'<Response><Message>{response_text}</Message></Response>'
    return Response(content=twiml, media_type="application/xml")


# ---- Dashboard endpoints (protected) ----

@router.get("/logs")
async def list_call_logs(
    status: CallStatus | None = None,
    limit: int = Query(50, le=200),
    offset: int = Query(0, ge=0),
    doctor: Doctor = Depends(get_current_doctor),
    db: AsyncSession = Depends(get_db),
):
    """List call logs for the authenticated doctor."""
    query = select(CallLog).where(CallLog.doctor_id == doctor.id)
    if status:
        query = query.where(CallLog.status == status)
    query = query.order_by(CallLog.created_at.desc()).limit(limit).offset(offset)

    result = await db.execute(query)
    logs = result.scalars().all()

    return {
        "call_logs": [
            {
                "id": str(cl.id),
                "caller_phone": cl.caller_phone,
                "direction": cl.direction.value,
                "status": cl.status.value,
                "duration_seconds": cl.duration_seconds,
                "recording_url": cl.recording_url,
                "whatsapp_followup_sent": cl.whatsapp_followup_sent,
                "started_at": cl.started_at.isoformat(),
                "created_at": cl.created_at.isoformat(),
            }
            for cl in logs
        ],
        "count": len(logs),
    }


@router.get("/stats")
async def call_stats(
    days: int = Query(30, ge=7, le=365),
    doctor: Doctor = Depends(get_current_doctor),
    db: AsyncSession = Depends(get_db),
):
    """Call statistics — total, answered, missed, recovered via WhatsApp."""
    from datetime import timedelta
    since = func.now() - timedelta(days=days)

    result = await db.execute(
        select(CallLog).where(
            and_(CallLog.doctor_id == doctor.id, CallLog.created_at >= since)
        )
    )
    logs = result.scalars().all()

    total = len(logs)
    answered = sum(1 for cl in logs if cl.status == CallStatus.ANSWERED)
    missed = sum(1 for cl in logs if cl.status in (CallStatus.MISSED, CallStatus.BUSY))
    recovered = sum(1 for cl in logs if cl.whatsapp_followup_sent)

    return {
        "period_days": days,
        "total_calls": total,
        "answered": answered,
        "missed": missed,
        "recovered_via_whatsapp": recovered,
        "recovery_rate": round(recovered / missed * 100, 1) if missed > 0 else 0,
        "answer_rate": round(answered / total * 100, 1) if total > 0 else 0,
    }


# ---- Call Tracking Number Management ----

@router.post("/tracking/provision")
async def provision_tracking_number(
    doctor: Doctor = Depends(get_current_doctor),
):
    """Provision a Twilio virtual number for call tracking.

    This number is used in Google Ads call extensions so PatientPlex
    captures every caller's real phone number (Google normally blurs it).
    """
    result = await call_tracking_service.provision_number(
        country_code="IN",
        webhook_base_url=None,  # Uses BACKEND_URL env var
    )
    return result


@router.get("/tracking/numbers")
async def list_tracking_numbers(
    doctor: Doctor = Depends(get_current_doctor),
):
    """List all provisioned Twilio tracking numbers."""
    numbers = await call_tracking_service.list_numbers()
    return {"numbers": numbers, "twilio_connected": call_tracking_service.is_connected}


@router.post("/callback")
async def initiate_callback(
    caller_phone: str = Query(..., description="Patient phone number to call back"),
    doctor: Doctor = Depends(get_current_doctor),
    db: AsyncSession = Depends(get_db),
):
    """Initiate a callback to a patient whose number was captured.

    Uses the clinic's Twilio virtual number to call the patient back,
    then connects them to the doctor's real phone.
    """
    clinic_phone = doctor.whatsapp_number or doctor.phone
    clinic_name = doctor.clinic_name or f"Dr. {doctor.full_name}'s clinic"

    result = await call_tracking_service.initiate_callback(
        from_number=clinic_phone,
        to_number=caller_phone,
        clinic_name=clinic_name,
    )

    # Log the outbound call
    if result.get("status") == "calling":
        call_log = CallLog(
            doctor_id=doctor.id,
            caller_phone=caller_phone,
            clinic_phone=clinic_phone,
            direction=CallDirection.OUTBOUND,
            status=CallStatus.RINGING,
            started_at=datetime.now(timezone.utc),
            platform_call_sid=result.get("call_sid"),
            platform_provider="twilio",
        )
        db.add(call_log)
        await db.commit()

    return result
