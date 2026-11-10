"""API routes for EHR, Calendar & Revenue Integration."""

from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from typing import Optional, List, Dict
from app.services.ehr_integration import (
    EHRIntegration,
    Appointment,
    AppointmentStatus,
)

router = APIRouter(prefix="/ehr", tags=["EHR & Calendar"])

ehr = EHRIntegration()


class BookAppointmentInput(BaseModel):
    id: str
    clinic_id: str
    patient_id: str
    doctor_id: str
    treatment: str
    scheduled_at: str
    source_platform: str = ""
    source_campaign_id: str = ""
    cost_of_acquisition_inr: float = 0.0
    notes: str = ""


class UpdateStatusInput(BaseModel):
    status: str
    revenue_inr: float = 0.0


class SetScheduleInput(BaseModel):
    doctor_id: str
    date: str
    slots: List[Dict]


@router.post("/appointments/book")
async def book_appointment(data: BookAppointmentInput):
    """Book a new appointment."""
    apt = Appointment(
        id=data.id,
        clinic_id=data.clinic_id,
        patient_id=data.patient_id,
        doctor_id=data.doctor_id,
        treatment=data.treatment,
        scheduled_at=data.scheduled_at,
        status=AppointmentStatus.BOOKED,
        source_platform=data.source_platform,
        source_campaign_id=data.source_campaign_id,
        cost_of_acquisition_inr=data.cost_of_acquisition_inr,
        notes=data.notes,
    )
    return ehr.book_appointment(apt)


@router.put("/appointments/{appointment_id}/status")
async def update_status(appointment_id: str, data: UpdateStatusInput):
    """Update appointment status (completed, no_show, cancelled, etc.)."""
    try:
        status = AppointmentStatus(data.status)
    except ValueError:
        raise HTTPException(
            status_code=400,
            detail=f"Invalid status. Valid: {[s.value for s in AppointmentStatus]}",
        )
    return ehr.update_appointment_status(
        appointment_id, status, data.revenue_inr
    )


@router.get("/appointments/{appointment_id}")
async def get_appointment(appointment_id: str):
    """Get a single appointment."""
    apt = ehr.get_appointment(appointment_id)
    if not apt:
        raise HTTPException(status_code=404, detail="Appointment not found")
    return apt


@router.post("/schedule/{clinic_id}")
async def set_schedule(clinic_id: str, data: SetScheduleInput):
    """Set available slots for a clinic on a given date."""
    return ehr.set_clinic_schedule(
        clinic_id, data.doctor_id, data.date, data.slots
    )


@router.get("/availability/{clinic_id}/{date}")
async def get_availability(clinic_id: str, date: str):
    """Get available appointment slots for a clinic on a date."""
    slots = ehr.get_available_slots(clinic_id, date)
    return {"clinic_id": clinic_id, "date": date, "available_slots": slots}


@router.get("/revenue/{clinic_id}")
async def get_revenue(
    clinic_id: str,
    start_date: Optional[str] = None,
    end_date: Optional[str] = None,
):
    """Get revenue and business metrics for a clinic."""
    return ehr.get_revenue_metrics(clinic_id, start_date, end_date)


@router.get("/cost-per-revenue/{clinic_id}")
async def get_cost_per_revenue(clinic_id: str):
    """Get cost per rupee of revenue for a clinic."""
    return ehr.get_cost_per_dollar_booked(clinic_id)
