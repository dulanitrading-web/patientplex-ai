"""Appointment management endpoints for the doctor dashboard."""

from datetime import date, datetime, timedelta, timezone
from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, Query
from pydantic import BaseModel
from sqlalchemy import and_, func, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.api.v1.auth import get_current_doctor
from app.db.session import get_db
from app.models.conversation import Appointment, AppointmentStatus
from app.models.doctor import Doctor

router = APIRouter(prefix="/appointments", tags=["appointments"])


class StatusUpdate(BaseModel):
    status: AppointmentStatus
    notes: str | None = None
    revenue_amount: float | None = None
    treatment_done: str | None = None


class BookAppointmentRequest(BaseModel):
    """Manual appointment booking from the dashboard."""
    patient_name: str
    patient_phone: str
    treatment: str
    date: date
    time: str  # "HH:MM" format
    source: str = "Walk-in"  # Google Ads, WhatsApp, Walk-in, Phone Call, Referral
    notes: str | None = None
    patient_email: str | None = None


@router.post("/book")
async def book_appointment(
    body: BookAppointmentRequest,
    doctor: Doctor = Depends(get_current_doctor),
    db: AsyncSession = Depends(get_db),
):
    """Manually book a new appointment from the dashboard.

    Creates the appointment and tracks it as a conversion in the funnel.
    """
    from datetime import time as time_type

    # Parse time string
    try:
        parts = body.time.split(":")
        appt_time = time_type(int(parts[0]), int(parts[1]))
    except (ValueError, IndexError):
        raise HTTPException(status_code=400, detail="Time must be in HH:MM format")

    appointment = Appointment(
        doctor_id=doctor.id,
        patient_name=body.patient_name,
        patient_phone=body.patient_phone,
        treatment=body.treatment,
        appointment_date=body.date,
        appointment_time=appt_time,
        duration_minutes=30,
        status=AppointmentStatus.CONFIRMED,
        notes=body.notes,
        source=body.source,
        patient_email=body.patient_email,
    )
    db.add(appointment)
    await db.flush()

    # Track as a conversion in the funnel
    try:
        from app.services.conversion_bridge import ConversionBridge
        bridge = ConversionBridge(db)
        await bridge.track_appointment_booked(appointment)
    except Exception:
        pass  # Don't fail the booking if tracking fails

    await db.commit()

    # Send email confirmation (non-blocking — don't fail the booking)
    if body.patient_email:
        try:
            from app.services.email_service import send_appointment_confirmation
            await send_appointment_confirmation(
                patient_email=body.patient_email,
                patient_name=body.patient_name,
                doctor_name=doctor.full_name,
                clinic_name=doctor.clinic_name or "",
                treatment=body.treatment,
                date_str=body.date.strftime("%A, %d %B %Y"),
                time_str=body.time,
                clinic_address=doctor.address or "",
                clinic_phone=doctor.phone_number or "",
            )
        except Exception:
            pass  # Don't fail the booking if email fails

    return {
        "message": "Appointment booked",
        "appointment": _serialize_appointment(appointment),
    }


@router.get("/")
async def list_appointments(
    date_from: date | None = None,
    date_to: date | None = None,
    status: AppointmentStatus | None = None,
    limit: int = Query(50, le=200),
    offset: int = Query(0, ge=0),
    doctor: Doctor = Depends(get_current_doctor),
    db: AsyncSession = Depends(get_db),
):
    """List the doctor's appointments with optional date and status filters."""
    query = select(Appointment).where(Appointment.doctor_id == doctor.id)

    if date_from:
        query = query.where(Appointment.appointment_date >= date_from)
    if date_to:
        query = query.where(Appointment.appointment_date <= date_to)
    if status:
        query = query.where(Appointment.status == status)

    query = query.order_by(Appointment.appointment_date.desc(), Appointment.appointment_time.desc())
    query = query.limit(limit).offset(offset)

    result = await db.execute(query)
    appointments = result.scalars().all()

    return {
        "appointments": [_serialize_appointment(a) for a in appointments],
        "count": len(appointments),
    }


@router.get("/today")
async def today_appointments(
    doctor: Doctor = Depends(get_current_doctor),
    db: AsyncSession = Depends(get_db),
):
    """Get all of today's appointments."""
    today = date.today()
    result = await db.execute(
        select(Appointment).where(
            and_(
                Appointment.doctor_id == doctor.id,
                Appointment.appointment_date == today,
            )
        ).order_by(Appointment.appointment_time.asc())
    )
    appointments = result.scalars().all()
    return {
        "date": today.isoformat(),
        "appointments": [_serialize_appointment(a) for a in appointments],
        "count": len(appointments),
    }


@router.get("/stats")
async def appointment_stats(
    days: int = Query(30, ge=7, le=365),
    doctor: Doctor = Depends(get_current_doctor),
    db: AsyncSession = Depends(get_db),
):
    """Summary statistics for appointments over a period.

    Returns: total booked, attended, no-show, cancelled, attendance rate,
    breakdown by treatment, and daily trend.
    """
    since = date.today() - timedelta(days=days)

    result = await db.execute(
        select(Appointment).where(
            and_(
                Appointment.doctor_id == doctor.id,
                Appointment.appointment_date >= since,
            )
        )
    )
    appointments = result.scalars().all()

    total = len(appointments)
    by_status = {}
    by_treatment = {}
    total_revenue = 0.0

    for a in appointments:
        status_key = a.status.value
        by_status[status_key] = by_status.get(status_key, 0) + 1
        by_treatment[a.treatment] = by_treatment.get(a.treatment, 0) + 1
        if getattr(a, "revenue_amount", None):
            total_revenue += a.revenue_amount

    attended = by_status.get("ATTENDED", 0)
    no_show = by_status.get("NO_SHOW", 0)
    cancelled = by_status.get("CANCELLED", 0)
    confirmed = by_status.get("CONFIRMED", 0) + by_status.get("REMINDED", 0)

    completed = attended + no_show  # Appointments past their time
    attendance_rate = round((attended / completed * 100), 1) if completed > 0 else 0
    cancellation_rate = round((cancelled / total * 100), 1) if total > 0 else 0

    return {
        "period_days": days,
        "total_booked": total,
        "attended": attended,
        "no_show": no_show,
        "cancelled": cancelled,
        "upcoming": confirmed,
        "attendance_rate": attendance_rate,
        "cancellation_rate": cancellation_rate,
        "by_treatment": by_treatment,
        "by_status": by_status,
        "total_revenue": total_revenue,
    }


@router.get("/{appointment_id}")
async def get_appointment(
    appointment_id: UUID,
    doctor: Doctor = Depends(get_current_doctor),
    db: AsyncSession = Depends(get_db),
):
    """Get a single appointment's details."""
    result = await db.execute(
        select(Appointment).where(
            and_(Appointment.id == appointment_id, Appointment.doctor_id == doctor.id)
        )
    )
    appointment = result.scalar_one_or_none()
    if not appointment:
        raise HTTPException(status_code=404, detail="Appointment not found")
    return _serialize_appointment(appointment)


@router.put("/{appointment_id}/status")
async def update_appointment_status(
    appointment_id: UUID,
    body: StatusUpdate,
    doctor: Doctor = Depends(get_current_doctor),
    db: AsyncSession = Depends(get_db),
):
    """Update an appointment's status (ATTENDED, NO_SHOW, CANCELLED)."""
    result = await db.execute(
        select(Appointment).where(
            and_(Appointment.id == appointment_id, Appointment.doctor_id == doctor.id)
        )
    )
    appointment = result.scalar_one_or_none()
    if not appointment:
        raise HTTPException(status_code=404, detail="Appointment not found")

    appointment.status = body.status
    if body.notes:
        appointment.notes = body.notes
    if body.revenue_amount is not None:
        appointment.revenue_amount = body.revenue_amount
    if body.treatment_done:
        appointment.treatment_done = body.treatment_done
    await db.commit()

    return {"message": f"Appointment marked as {body.status.value}", "appointment": _serialize_appointment(appointment)}


def _serialize_appointment(a: Appointment) -> dict:
    return {
        "id": str(a.id),
        "patient_name": a.patient_name,
        "patient_phone": a.patient_phone,
        "treatment": a.treatment,
        "date": a.appointment_date.isoformat(),
        "time": a.appointment_time.strftime("%H:%M"),
        "duration_minutes": a.duration_minutes,
        "status": a.status.value,
        "google_event_id": a.google_event_id,
        "reminder_24h_sent": a.reminder_24h_sent,
        "reminder_2h_sent": a.reminder_2h_sent,
        "confirmation_sent": a.confirmation_sent,
        "notes": a.notes,
        "source": getattr(a, "source", "Walk-in"),
        "revenue_amount": getattr(a, "revenue_amount", None),
        "treatment_done": getattr(a, "treatment_done", None),
        "patient_email": getattr(a, "patient_email", None),
        "created_at": a.created_at.isoformat(),
    }
