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

    for a in appointments:
        status_key = a.status.value
        by_status[status_key] = by_status.get(status_key, 0) + 1
        by_treatment[a.treatment] = by_treatment.get(a.treatment, 0) + 1

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
        "created_at": a.created_at.isoformat(),
    }
