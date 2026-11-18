"""Clinic staff management — multiple doctors per clinic.

Endpoints:
- GET /staff — list all staff members
- POST /staff — add a new staff member
- PUT /staff/{id} — update a staff member
- DELETE /staff/{id} — deactivate a staff member
- GET /staff/{id}/availability — get available slots for a staff member on a date
- GET /staff/calendar — combined calendar view for all staff
"""

from datetime import date, time as time_type, timedelta
from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, Query
from pydantic import BaseModel
from sqlalchemy import and_, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.api.v1.auth import get_current_doctor
from app.db.session import get_db
from app.models.clinic_staff import ClinicStaff, StaffRole
from app.models.conversation import Appointment, AppointmentStatus
from app.models.doctor import Doctor

router = APIRouter(prefix="/staff", tags=["clinic-staff"])


# ─── Schemas ───

class StaffCreate(BaseModel):
    full_name: str
    title: str = "Dr."
    specialty: str
    role: StaffRole = StaffRole.DOCTOR
    phone: str | None = None
    email: str | None = None
    services: list[str] | None = None
    weekly_schedule: dict | None = None
    slot_duration_minutes: int = 30
    max_patients_per_day: int = 20
    calendar_color: str = "#10b981"


class StaffUpdate(BaseModel):
    full_name: str | None = None
    title: str | None = None
    specialty: str | None = None
    role: StaffRole | None = None
    phone: str | None = None
    email: str | None = None
    services: list[str] | None = None
    weekly_schedule: dict | None = None
    slot_duration_minutes: int | None = None
    max_patients_per_day: int | None = None
    calendar_color: str | None = None
    is_active: bool | None = None
    display_order: int | None = None


# ─── Endpoints ───

@router.get("/")
async def list_staff(
    doctor: Doctor = Depends(get_current_doctor),
    db: AsyncSession = Depends(get_db),
):
    """List all staff members for this clinic."""
    result = await db.execute(
        select(ClinicStaff)
        .where(ClinicStaff.doctor_id == doctor.id)
        .order_by(ClinicStaff.display_order, ClinicStaff.full_name)
    )
    staff = result.scalars().all()

    # If no staff exist yet, auto-create the owner as the first staff member
    if not staff:
        owner_staff = ClinicStaff(
            doctor_id=doctor.id,
            full_name=doctor.full_name,
            title="Dr.",
            specialty=doctor.specialty.value if doctor.specialty else "General",
            role=StaffRole.OWNER,
            phone=doctor.phone,
            email=doctor.email,
            services=doctor.services,
            google_calendar_id=doctor.google_calendar_id,
            google_calendar_connected=doctor.google_calendar_connected,
            calendar_color="#10b981",
        )
        db.add(owner_staff)
        await db.commit()
        staff = [owner_staff]

    return {
        "staff": [_serialize_staff(s) for s in staff],
        "count": len(staff),
    }


@router.post("/")
async def add_staff(
    body: StaffCreate,
    doctor: Doctor = Depends(get_current_doctor),
    db: AsyncSession = Depends(get_db),
):
    """Add a new staff member to this clinic."""
    # Count existing staff
    result = await db.execute(
        select(ClinicStaff).where(ClinicStaff.doctor_id == doctor.id)
    )
    existing = result.scalars().all()
    if len(existing) >= 15:
        raise HTTPException(status_code=400, detail="Maximum 15 staff members per clinic")

    staff = ClinicStaff(
        doctor_id=doctor.id,
        full_name=body.full_name,
        title=body.title,
        specialty=body.specialty,
        role=body.role,
        phone=body.phone,
        email=body.email,
        services=body.services,
        weekly_schedule=body.weekly_schedule,
        slot_duration_minutes=body.slot_duration_minutes,
        max_patients_per_day=body.max_patients_per_day,
        calendar_color=body.calendar_color,
        display_order=len(existing),
    )
    db.add(staff)
    await db.commit()

    return {"message": "Staff member added", "staff": _serialize_staff(staff)}


@router.put("/{staff_id}")
async def update_staff(
    staff_id: UUID,
    body: StaffUpdate,
    doctor: Doctor = Depends(get_current_doctor),
    db: AsyncSession = Depends(get_db),
):
    """Update a staff member's details."""
    result = await db.execute(
        select(ClinicStaff).where(
            and_(ClinicStaff.id == staff_id, ClinicStaff.doctor_id == doctor.id)
        )
    )
    staff = result.scalar_one_or_none()
    if not staff:
        raise HTTPException(status_code=404, detail="Staff member not found")

    for field, value in body.model_dump(exclude_unset=True).items():
        setattr(staff, field, value)

    await db.commit()
    return {"message": "Staff updated", "staff": _serialize_staff(staff)}


@router.delete("/{staff_id}")
async def deactivate_staff(
    staff_id: UUID,
    doctor: Doctor = Depends(get_current_doctor),
    db: AsyncSession = Depends(get_db),
):
    """Deactivate a staff member (doesn't delete — preserves appointment history)."""
    result = await db.execute(
        select(ClinicStaff).where(
            and_(ClinicStaff.id == staff_id, ClinicStaff.doctor_id == doctor.id)
        )
    )
    staff = result.scalar_one_or_none()
    if not staff:
        raise HTTPException(status_code=404, detail="Staff member not found")

    if staff.role == StaffRole.OWNER:
        raise HTTPException(status_code=400, detail="Cannot deactivate the clinic owner")

    staff.is_active = False
    await db.commit()
    return {"message": f"{staff.full_name} deactivated"}


@router.get("/{staff_id}/availability")
async def get_staff_availability(
    staff_id: UUID,
    target_date: date = Query(..., alias="date"),
    doctor: Doctor = Depends(get_current_doctor),
    db: AsyncSession = Depends(get_db),
):
    """Get available time slots for a specific staff member on a date.

    Checks:
    1. Staff's weekly schedule for that day of week
    2. Existing appointments on that date
    3. Returns available slots
    """
    result = await db.execute(
        select(ClinicStaff).where(
            and_(ClinicStaff.id == staff_id, ClinicStaff.doctor_id == doctor.id)
        )
    )
    staff = result.scalar_one_or_none()
    if not staff:
        raise HTTPException(status_code=404, detail="Staff member not found")

    # Check if staff works on this day
    day_name = target_date.strftime("%A").lower()
    schedule = (staff.weekly_schedule or {}).get(day_name)
    if not schedule:
        return {"date": target_date.isoformat(), "staff_id": str(staff_id), "slots": [], "message": f"{staff.full_name} does not work on {day_name.title()}s"}

    # Get existing appointments for this staff member on this date
    appt_result = await db.execute(
        select(Appointment).where(
            and_(
                Appointment.doctor_id == doctor.id,
                Appointment.staff_id == staff_id,
                Appointment.appointment_date == target_date,
                Appointment.status.notin_([AppointmentStatus.CANCELLED]),
            )
        )
    )
    existing_appts = appt_result.scalars().all()
    booked_times = {a.appointment_time.strftime("%H:%M") for a in existing_appts}

    # Generate slots
    start_parts = schedule["start"].split(":")
    end_parts = schedule["end"].split(":")
    start_hour, start_min = int(start_parts[0]), int(start_parts[1])
    end_hour, end_min = int(end_parts[0]), int(end_parts[1])

    slots = []
    current_minutes = start_hour * 60 + start_min
    end_minutes = end_hour * 60 + end_min
    duration = staff.slot_duration_minutes

    while current_minutes + duration <= end_minutes:
        h, m = divmod(current_minutes, 60)
        time_str = f"{h:02d}:{m:02d}"
        slots.append({
            "time": time_str,
            "available": time_str not in booked_times,
        })
        current_minutes += duration

    return {
        "date": target_date.isoformat(),
        "staff_id": str(staff_id),
        "staff_name": staff.full_name,
        "slots": slots,
        "total": len(slots),
        "available": sum(1 for s in slots if s["available"]),
    }


@router.get("/calendar")
async def combined_calendar(
    date_from: date | None = None,
    date_to: date | None = None,
    doctor: Doctor = Depends(get_current_doctor),
    db: AsyncSession = Depends(get_db),
):
    """Combined calendar view — all staff members' appointments for a date range.

    Returns appointments grouped by staff member, used to render the multi-doctor
    calendar view in the dashboard.
    """
    if not date_from:
        # Default to current week (Monday to Sunday)
        today = date.today()
        weekday = today.weekday()
        date_from = today - timedelta(days=weekday)
    if not date_to:
        date_to = date_from + timedelta(days=6)

    # Get all active staff
    staff_result = await db.execute(
        select(ClinicStaff).where(
            and_(ClinicStaff.doctor_id == doctor.id, ClinicStaff.is_active == True)
        ).order_by(ClinicStaff.display_order)
    )
    staff_members = staff_result.scalars().all()

    # Get all appointments in the date range
    appt_result = await db.execute(
        select(Appointment).where(
            and_(
                Appointment.doctor_id == doctor.id,
                Appointment.appointment_date >= date_from,
                Appointment.appointment_date <= date_to,
            )
        ).order_by(Appointment.appointment_date, Appointment.appointment_time)
    )
    appointments = appt_result.scalars().all()

    # Group appointments by staff_id
    appts_by_staff: dict[str, list] = {}
    unassigned = []
    for a in appointments:
        sid = str(a.staff_id) if a.staff_id else None
        if sid:
            if sid not in appts_by_staff:
                appts_by_staff[sid] = []
            appts_by_staff[sid].append(_serialize_appointment_mini(a))
        else:
            unassigned.append(_serialize_appointment_mini(a))

    return {
        "date_from": date_from.isoformat(),
        "date_to": date_to.isoformat(),
        "staff": [
            {
                **_serialize_staff(s),
                "appointments": appts_by_staff.get(str(s.id), []),
            }
            for s in staff_members
        ],
        "unassigned_appointments": unassigned,
    }


@router.get("/route")
async def route_patient(
    treatment: str = Query(...),
    target_date: date = Query(..., alias="date"),
    doctor: Doctor = Depends(get_current_doctor),
    db: AsyncSession = Depends(get_db),
):
    """Smart routing — find the best available staff for a treatment on a date.

    Logic:
    1. Find all active staff whose services list includes this treatment
    2. For each matching staff, check availability on the requested date
    3. Return staff sorted by availability (most open slots first)
    """
    staff_result = await db.execute(
        select(ClinicStaff).where(
            and_(ClinicStaff.doctor_id == doctor.id, ClinicStaff.is_active == True)
        )
    )
    all_staff = staff_result.scalars().all()

    # Filter staff who can handle this treatment
    treatment_lower = treatment.lower()
    matching = []
    for s in all_staff:
        staff_services = [svc.lower() for svc in (s.services or [])]
        if treatment_lower in staff_services or not s.services:
            # Staff with no services set = can handle anything (general)
            matching.append(s)

    if not matching:
        return {
            "treatment": treatment,
            "date": target_date.isoformat(),
            "options": [],
            "message": f"No staff member handles '{treatment}'. Add this service to a staff member's profile.",
        }

    # Check each staff's availability on that date
    day_name = target_date.strftime("%A").lower()
    options = []
    for s in matching:
        schedule = (s.weekly_schedule or {}).get(day_name)
        if not schedule:
            continue  # Doesn't work that day

        # Count booked slots
        appt_result = await db.execute(
            select(Appointment).where(
                and_(
                    Appointment.staff_id == s.id,
                    Appointment.appointment_date == target_date,
                    Appointment.status.notin_([AppointmentStatus.CANCELLED]),
                )
            )
        )
        booked_count = len(appt_result.scalars().all())

        # Calculate total slots
        start_parts = schedule["start"].split(":")
        end_parts = schedule["end"].split(":")
        total_minutes = (int(end_parts[0]) * 60 + int(end_parts[1])) - (int(start_parts[0]) * 60 + int(start_parts[1]))
        total_slots = total_minutes // s.slot_duration_minutes
        available_slots = max(0, total_slots - booked_count)

        if available_slots > 0:
            options.append({
                "staff_id": str(s.id),
                "staff_name": s.full_name,
                "specialty": s.specialty,
                "available_slots": available_slots,
                "total_slots": total_slots,
                "calendar_color": s.calendar_color,
            })

    # Sort by most available first
    options.sort(key=lambda x: x["available_slots"], reverse=True)

    return {
        "treatment": treatment,
        "date": target_date.isoformat(),
        "options": options,
    }


# ─── Helpers ───

def _serialize_staff(s: ClinicStaff) -> dict:
    return {
        "id": str(s.id),
        "full_name": s.full_name,
        "title": s.title,
        "specialty": s.specialty,
        "role": s.role.value,
        "phone": s.phone,
        "email": s.email,
        "services": s.services or [],
        "weekly_schedule": s.weekly_schedule or {},
        "slot_duration_minutes": s.slot_duration_minutes,
        "max_patients_per_day": s.max_patients_per_day,
        "calendar_color": s.calendar_color,
        "is_active": s.is_active,
        "display_order": s.display_order,
        "google_calendar_connected": s.google_calendar_connected,
    }


def _serialize_appointment_mini(a: Appointment) -> dict:
    return {
        "id": str(a.id),
        "patient_name": a.patient_name,
        "treatment": a.treatment,
        "date": a.appointment_date.isoformat(),
        "time": a.appointment_time.strftime("%H:%M"),
        "duration_minutes": a.duration_minutes,
        "status": a.status.value,
        "staff_id": str(a.staff_id) if a.staff_id else None,
    }
