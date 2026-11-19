"""Patient management endpoints — patient CRM for clinics.

Every patient interaction (booking, WhatsApp, call, walk-in) creates or updates
a patient record. Doctors can see full patient history, lifetime value, and source.
"""

import csv
import io
from datetime import datetime, timezone
from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, Query
from fastapi.responses import StreamingResponse
from pydantic import BaseModel
from sqlalchemy import and_, func, or_, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.api.v1.auth import get_current_doctor
from app.db.session import get_db
from app.models.conversation import Appointment
from app.models.doctor import Doctor
from app.models.patient import Patient

router = APIRouter(prefix="/patients", tags=["patients"])


class PatientCreate(BaseModel):
    name: str
    phone: str
    email: str | None = None
    source: str = "Walk-in"
    notes: str | None = None
    tags: list[str] | None = None


class PatientUpdate(BaseModel):
    name: str | None = None
    email: str | None = None
    notes: str | None = None
    tags: list[str] | None = None


@router.get("/")
async def list_patients(
    search: str | None = None,
    source: str | None = None,
    sort_by: str = "last_visit",  # last_visit, revenue, name, visits
    limit: int = Query(50, le=200),
    offset: int = Query(0, ge=0),
    doctor: Doctor = Depends(get_current_doctor),
    db: AsyncSession = Depends(get_db),
):
    """List patients with search, filter, and sort."""
    query = select(Patient).where(Patient.doctor_id == doctor.id)

    if search:
        query = query.where(
            or_(
                Patient.name.ilike(f"%{search}%"),
                Patient.phone.ilike(f"%{search}%"),
                Patient.email.ilike(f"%{search}%"),
            )
        )
    if source:
        query = query.where(Patient.source == source)

    # Sorting
    if sort_by == "revenue":
        query = query.order_by(Patient.total_revenue.desc())
    elif sort_by == "visits":
        query = query.order_by(Patient.total_visits.desc())
    elif sort_by == "name":
        query = query.order_by(Patient.name.asc())
    else:
        query = query.order_by(Patient.last_visit_date.desc().nullslast())

    total_result = await db.execute(
        select(func.count()).select_from(Patient).where(Patient.doctor_id == doctor.id)
    )
    total = total_result.scalar() or 0

    query = query.limit(limit).offset(offset)
    result = await db.execute(query)
    patients = result.scalars().all()

    return {
        "patients": [_serialize_patient(p) for p in patients],
        "total": total,
        "count": len(patients),
    }


@router.get("/stats")
async def patient_stats(
    doctor: Doctor = Depends(get_current_doctor),
    db: AsyncSession = Depends(get_db),
):
    """Summary patient statistics."""
    result = await db.execute(
        select(Patient).where(Patient.doctor_id == doctor.id)
    )
    patients = result.scalars().all()

    total = len(patients)
    total_revenue = sum(p.total_revenue for p in patients)
    avg_visits = sum(p.total_visits for p in patients) / max(total, 1)
    avg_revenue = total_revenue / max(total, 1)

    # Source breakdown
    by_source: dict[str, int] = {}
    for p in patients:
        by_source[p.source] = by_source.get(p.source, 0) + 1

    # Top patients by revenue
    top_by_revenue = sorted(patients, key=lambda p: p.total_revenue, reverse=True)[:5]

    return {
        "total_patients": total,
        "total_revenue": total_revenue,
        "avg_visits_per_patient": round(avg_visits, 1),
        "avg_revenue_per_patient": round(avg_revenue),
        "by_source": by_source,
        "top_patients": [
            {"name": p.name, "revenue": p.total_revenue, "visits": p.total_visits}
            for p in top_by_revenue
        ],
    }


@router.get("/export")
async def export_patients(
    format: str = Query("csv", pattern="^(csv|json)$"),
    doctor: Doctor = Depends(get_current_doctor),
    db: AsyncSession = Depends(get_db),
):
    """Export all patients as CSV or JSON."""
    result = await db.execute(
        select(Patient).where(Patient.doctor_id == doctor.id).order_by(Patient.name)
    )
    patients = result.scalars().all()

    if format == "json":
        return {"patients": [_serialize_patient(p) for p in patients]}

    # CSV export
    output = io.StringIO()
    writer = csv.writer(output)
    writer.writerow(["Name", "Phone", "Email", "Source", "Total Visits", "Total Revenue (₹)",
                      "Last Visit", "Treatments", "Tags", "Notes"])
    for p in patients:
        writer.writerow([
            p.name, p.phone, p.email or "", p.source, p.total_visits,
            p.total_revenue, p.last_visit_date.strftime("%Y-%m-%d") if p.last_visit_date else "",
            ", ".join(p.treatments or []), ", ".join(p.tags or []), p.notes or "",
        ])

    output.seek(0)
    return StreamingResponse(
        iter([output.getvalue()]),
        media_type="text/csv",
        headers={"Content-Disposition": f"attachment; filename=patients_{datetime.now().strftime('%Y%m%d')}.csv"},
    )


@router.post("/")
async def create_patient(
    body: PatientCreate,
    doctor: Doctor = Depends(get_current_doctor),
    db: AsyncSession = Depends(get_db),
):
    """Create a new patient record."""
    # Check if patient with this phone already exists
    existing = await db.execute(
        select(Patient).where(
            and_(Patient.doctor_id == doctor.id, Patient.phone == body.phone)
        )
    )
    if existing.scalar_one_or_none():
        raise HTTPException(status_code=400, detail="Patient with this phone number already exists")

    patient = Patient(
        doctor_id=doctor.id,
        name=body.name,
        phone=body.phone,
        email=body.email,
        source=body.source,
        notes=body.notes,
        tags=body.tags or [],
    )
    db.add(patient)
    await db.commit()
    return {"message": "Patient created", "patient": _serialize_patient(patient)}


@router.get("/{patient_id}")
async def get_patient(
    patient_id: UUID,
    doctor: Doctor = Depends(get_current_doctor),
    db: AsyncSession = Depends(get_db),
):
    """Get a patient's full profile with appointment history."""
    result = await db.execute(
        select(Patient).where(
            and_(Patient.id == patient_id, Patient.doctor_id == doctor.id)
        )
    )
    patient = result.scalar_one_or_none()
    if not patient:
        raise HTTPException(status_code=404, detail="Patient not found")

    # Get appointment history
    appt_result = await db.execute(
        select(Appointment).where(
            and_(
                Appointment.doctor_id == doctor.id,
                Appointment.patient_phone == patient.phone,
            )
        ).order_by(Appointment.appointment_date.desc())
    )
    appointments = appt_result.scalars().all()

    return {
        **_serialize_patient(patient),
        "appointments": [
            {
                "id": str(a.id),
                "date": a.appointment_date.isoformat(),
                "time": a.appointment_time.strftime("%H:%M"),
                "treatment": a.treatment,
                "status": a.status.value,
                "revenue": getattr(a, "revenue_amount", None),
                "notes": a.notes,
            }
            for a in appointments
        ],
    }


@router.put("/{patient_id}")
async def update_patient(
    patient_id: UUID,
    body: PatientUpdate,
    doctor: Doctor = Depends(get_current_doctor),
    db: AsyncSession = Depends(get_db),
):
    """Update patient details."""
    result = await db.execute(
        select(Patient).where(
            and_(Patient.id == patient_id, Patient.doctor_id == doctor.id)
        )
    )
    patient = result.scalar_one_or_none()
    if not patient:
        raise HTTPException(status_code=404, detail="Patient not found")

    for field, value in body.model_dump(exclude_unset=True).items():
        setattr(patient, field, value)

    await db.commit()
    return {"message": "Patient updated", "patient": _serialize_patient(patient)}


@router.get("/{patient_id}/appointments/export")
async def export_patient_appointments(
    patient_id: UUID,
    doctor: Doctor = Depends(get_current_doctor),
    db: AsyncSession = Depends(get_db),
):
    """Export a single patient's appointment history as CSV."""
    result = await db.execute(
        select(Patient).where(
            and_(Patient.id == patient_id, Patient.doctor_id == doctor.id)
        )
    )
    patient = result.scalar_one_or_none()
    if not patient:
        raise HTTPException(status_code=404, detail="Patient not found")

    appt_result = await db.execute(
        select(Appointment).where(
            and_(Appointment.doctor_id == doctor.id, Appointment.patient_phone == patient.phone)
        ).order_by(Appointment.appointment_date.desc())
    )
    appointments = appt_result.scalars().all()

    output = io.StringIO()
    writer = csv.writer(output)
    writer.writerow(["Date", "Time", "Treatment", "Status", "Revenue (₹)", "Notes"])
    for a in appointments:
        writer.writerow([
            a.appointment_date.isoformat(), a.appointment_time.strftime("%H:%M"),
            a.treatment, a.status.value, getattr(a, "revenue_amount", "") or "",
            a.notes or "",
        ])

    output.seek(0)
    return StreamingResponse(
        iter([output.getvalue()]),
        media_type="text/csv",
        headers={"Content-Disposition": f"attachment; filename={patient.name.replace(' ', '_')}_appointments.csv"},
    )


def _serialize_patient(p: Patient) -> dict:
    return {
        "id": str(p.id),
        "name": p.name,
        "phone": p.phone,
        "email": p.email,
        "source": p.source,
        "total_visits": p.total_visits,
        "total_revenue": p.total_revenue,
        "total_no_shows": p.total_no_shows,
        "first_visit_date": p.first_visit_date.isoformat() if p.first_visit_date else None,
        "last_visit_date": p.last_visit_date.isoformat() if p.last_visit_date else None,
        "treatments": p.treatments or [],
        "tags": p.tags or [],
        "notes": p.notes,
        "created_at": p.created_at.isoformat(),
    }
