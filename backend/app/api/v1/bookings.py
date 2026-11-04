"""Direct booking API — for dashboard manual bookings and external integrations."""

from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.api.v1.auth import get_current_doctor
from app.db.session import get_db
from app.models.doctor import Doctor
from app.services.booking_engine import BookingEngine

router = APIRouter(prefix="/bookings", tags=["bookings"])


class BookingRequest(BaseModel):
    patient_name: str
    patient_phone: str
    treatment: str
    date: str  # YYYY-MM-DD
    time: str  # HH:MM
    source: str = "dashboard"


class AvailabilityRequest(BaseModel):
    date: str  # YYYY-MM-DD
    preferred_time: str | None = None  # "morning", "afternoon", "evening", or "HH:MM"


class RescheduleRequest(BaseModel):
    new_date: str
    new_time: str


@router.post("/check-availability")
async def check_availability(
    body: AvailabilityRequest,
    doctor: Doctor = Depends(get_current_doctor),
    db: AsyncSession = Depends(get_db),
):
    """Check available slots for a given date.

    Used by the dashboard and landing page to show time slots.
    """
    engine = BookingEngine(db)
    return await engine.check_availability(doctor, body.date, body.preferred_time)


@router.post("/book")
async def book_appointment(
    body: BookingRequest,
    doctor: Doctor = Depends(get_current_doctor),
    db: AsyncSession = Depends(get_db),
):
    """Book an appointment manually from the dashboard.

    Triggers the full flow: calendar event, patient WhatsApp confirmation,
    doctor notification, conversion tracking.
    """
    engine = BookingEngine(db)
    result = await engine.book_appointment(
        doctor=doctor,
        patient_name=body.patient_name,
        patient_phone=body.patient_phone,
        treatment=body.treatment,
        appointment_date=body.date,
        appointment_time=body.time,
        source=body.source,
    )
    if not result.get("success"):
        raise HTTPException(status_code=400, detail=result.get("error", "Booking failed"))
    return result


@router.post("/{appointment_id}/cancel")
async def cancel_booking(
    appointment_id: str,
    doctor: Doctor = Depends(get_current_doctor),
    db: AsyncSession = Depends(get_db),
):
    """Cancel an appointment — notifies both patient and doctor."""
    from uuid import UUID
    engine = BookingEngine(db)
    return await engine.cancel_appointment(UUID(appointment_id), doctor, cancelled_by="doctor")


@router.post("/{appointment_id}/reschedule")
async def reschedule_booking(
    appointment_id: str,
    body: RescheduleRequest,
    doctor: Doctor = Depends(get_current_doctor),
    db: AsyncSession = Depends(get_db),
):
    """Reschedule an appointment — cancels old, books new, notifies both."""
    from uuid import UUID
    engine = BookingEngine(db)
    return await engine.reschedule_appointment(
        UUID(appointment_id), doctor, body.new_date, body.new_time
    )
