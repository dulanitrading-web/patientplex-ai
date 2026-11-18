"""Public booking API — no authentication required.

These endpoints power the patient-facing booking page at:
  /book/<doctor-slug>

A patient clicking a Google Ad lands here and can:
1. See the doctor's profile, services, and availability
2. Pick a date and time slot
3. Enter their name and phone
4. Book the appointment

No login, no WhatsApp, no app download required.
"""

from datetime import date, time as time_type, timedelta
from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, Query
from pydantic import BaseModel
from sqlalchemy import and_, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.db.session import get_db
from app.models.conversation import Appointment, AppointmentStatus
from app.models.doctor import Doctor

router = APIRouter(prefix="/public/book", tags=["public-booking"])


class PublicBookingRequest(BaseModel):
    patient_name: str
    patient_phone: str
    patient_email: str | None = None
    treatment: str
    date: date
    time: str  # HH:MM
    source: str = "Online Booking"
    utm_source: str | None = None
    utm_campaign: str | None = None


@router.get("/{slug}")
async def get_doctor_profile(
    slug: str,
    db: AsyncSession = Depends(get_db),
):
    """Get a doctor's public profile for the booking page.

    Returns: clinic name, doctor name, specialty, services, address, hours.
    No sensitive data exposed.
    """
    result = await db.execute(
        select(Doctor).where(Doctor.subdomain_slug == slug)
    )
    doctor = result.scalar_one_or_none()
    if not doctor:
        raise HTTPException(status_code=404, detail="Doctor not found")

    return {
        "slug": slug,
        "doctor_name": doctor.full_name,
        "clinic_name": doctor.clinic_name or "",
        "specialty": doctor.specialty.value if doctor.specialty else "General",
        "city": doctor.city or "",
        "address": doctor.clinic_address or "",
        "services": doctor.services or [],
        "logo": doctor.clinic_logo,
        "phone": doctor.phone,
    }


@router.get("/{slug}/availability")
async def get_public_availability(
    slug: str,
    target_date: date = Query(..., alias="date"),
    db: AsyncSession = Depends(get_db),
):
    """Get available time slots for a doctor on a specific date.

    Public endpoint — no auth required.
    Uses the doctor's configured hours and existing appointments to calculate open slots.
    """
    result = await db.execute(
        select(Doctor).where(Doctor.subdomain_slug == slug)
    )
    doctor = result.scalar_one_or_none()
    if not doctor:
        raise HTTPException(status_code=404, detail="Doctor not found")

    # Don't allow booking in the past
    if target_date < date.today():
        return {"date": target_date.isoformat(), "slots": [], "message": "Cannot book in the past"}

    # Don't allow booking more than 30 days ahead
    if target_date > date.today() + timedelta(days=30):
        return {"date": target_date.isoformat(), "slots": [], "message": "Cannot book more than 30 days ahead"}

    # Check if it's a Sunday (most Indian clinics closed)
    if target_date.weekday() == 6:
        return {"date": target_date.isoformat(), "slots": [], "message": "Clinic is closed on Sundays"}

    # Get existing appointments for this date
    appt_result = await db.execute(
        select(Appointment).where(
            and_(
                Appointment.doctor_id == doctor.id,
                Appointment.appointment_date == target_date,
                Appointment.status.notin_([AppointmentStatus.CANCELLED]),
            )
        )
    )
    existing = appt_result.scalars().all()
    booked_times = {a.appointment_time.strftime("%H:%M") for a in existing}

    # Generate slots (default: 9 AM to 8 PM, 30-min slots)
    # Saturday: 9 AM to 2 PM
    start_hour = 9
    end_hour = 20 if target_date.weekday() < 5 else 14
    slot_minutes = 30

    slots = []
    current = start_hour * 60
    end = end_hour * 60

    while current + slot_minutes <= end:
        h, m = divmod(current, 60)
        time_str = f"{h:02d}:{m:02d}"

        # Check if already booked
        available = time_str not in booked_times

        # Don't show past slots for today
        if target_date == date.today():
            from datetime import datetime, timezone
            now = datetime.now(timezone.utc).astimezone()
            if h < now.hour or (h == now.hour and m <= now.minute):
                current += slot_minutes
                continue

        # Format for display
        display = f"{h % 12 or 12}:{m:02d} {'AM' if h < 12 else 'PM'}"

        slots.append({
            "time": time_str,
            "display": display,
            "available": available,
        })
        current += slot_minutes

    return {
        "date": target_date.isoformat(),
        "doctor_name": doctor.full_name,
        "clinic_name": doctor.clinic_name or "",
        "slots": slots,
        "total_slots": len(slots),
        "available_slots": sum(1 for s in slots if s["available"]),
    }


@router.post("/{slug}/book")
async def public_book_appointment(
    slug: str,
    body: PublicBookingRequest,
    db: AsyncSession = Depends(get_db),
):
    """Book an appointment from the public booking page.

    No auth required. Creates the appointment and optionally sends
    email confirmation if patient email is provided.
    """
    # Find doctor
    result = await db.execute(
        select(Doctor).where(Doctor.subdomain_slug == slug)
    )
    doctor = result.scalar_one_or_none()
    if not doctor:
        raise HTTPException(status_code=404, detail="Doctor not found")

    # Validate date
    if body.date < date.today():
        raise HTTPException(status_code=400, detail="Cannot book in the past")

    # Parse time
    try:
        parts = body.time.split(":")
        appt_time = time_type(int(parts[0]), int(parts[1]))
    except (ValueError, IndexError):
        raise HTTPException(status_code=400, detail="Invalid time format. Use HH:MM")

    # Check if slot is still available
    existing = await db.execute(
        select(Appointment).where(
            and_(
                Appointment.doctor_id == doctor.id,
                Appointment.appointment_date == body.date,
                Appointment.appointment_time == appt_time,
                Appointment.status.notin_([AppointmentStatus.CANCELLED]),
            )
        )
    )
    if existing.scalar_one_or_none():
        raise HTTPException(status_code=409, detail="This time slot is no longer available. Please choose another.")

    # Create appointment
    appointment = Appointment(
        doctor_id=doctor.id,
        patient_name=body.patient_name,
        patient_phone=body.patient_phone,
        treatment=body.treatment,
        appointment_date=body.date,
        appointment_time=appt_time,
        duration_minutes=30,
        status=AppointmentStatus.CONFIRMED,
        source=body.source,
        patient_email=body.patient_email,
        notes=f"Booked online | UTM: {body.utm_source or 'direct'} / {body.utm_campaign or 'none'}",
    )
    db.add(appointment)
    await db.commit()

    # Send email confirmation (non-blocking)
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
                clinic_address=doctor.clinic_address or "",
                clinic_phone=doctor.phone or "",
            )
        except Exception:
            pass

    # Track conversion
    try:
        from app.services.conversion_bridge import ConversionBridge
        bridge = ConversionBridge(db)
        await bridge.track_appointment_booked(appointment)
    except Exception:
        pass

    return {
        "success": True,
        "message": "Appointment booked successfully!",
        "appointment": {
            "id": str(appointment.id),
            "doctor_name": doctor.full_name,
            "clinic_name": doctor.clinic_name or "",
            "treatment": body.treatment,
            "date": body.date.isoformat(),
            "time": body.time,
            "address": doctor.clinic_address or "",
            "phone": doctor.phone or "",
        },
    }
