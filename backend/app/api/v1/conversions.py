"""Conversion tracking and funnel analytics endpoints."""

from uuid import UUID

from fastapi import APIRouter, Depends, Query
from sqlalchemy.ext.asyncio import AsyncSession

from app.api.v1.auth import get_current_doctor
from app.db.session import get_db
from app.models.doctor import Doctor
from app.services.conversion_tracker import ConversionTracker

router = APIRouter(prefix="/conversions", tags=["conversions"])


@router.get("/funnel")
async def get_funnel(
    days: int = Query(30, ge=7, le=365),
    source_channel: str | None = None,
    doctor: Doctor = Depends(get_current_doctor),
    db: AsyncSession = Depends(get_db),
):
    """Full-funnel conversion analytics.

    Shows count at each stage from ad click to treatment accepted,
    with conversion rates between stages.
    """
    tracker = ConversionTracker(db)
    return await tracker.get_funnel_stats(doctor.id, days, source_channel)


@router.get("/attribution")
async def get_attribution(
    days: int = Query(30, ge=7, le=365),
    doctor: Doctor = Depends(get_current_doctor),
    db: AsyncSession = Depends(get_db),
):
    """Source attribution — which channels drive the most patients.

    Breaks down conversions by Google Ads, Meta, organic, calls, etc.
    """
    tracker = ConversionTracker(db)
    return await tracker.get_source_attribution(doctor.id, days)


@router.get("/patient/{phone}")
async def get_patient_journey(
    phone: str,
    doctor: Doctor = Depends(get_current_doctor),
    db: AsyncSession = Depends(get_db),
):
    """Complete journey of a specific patient.

    Shows every touchpoint from first ad click to last visit.
    """
    tracker = ConversionTracker(db)
    journey = await tracker.get_patient_journey(doctor.id, phone)
    return {"patient_phone": phone, "events": journey, "total_steps": len(journey)}


@router.post("/track")
async def track_event(
    stage: str,
    source_channel: str,
    patient_phone: str | None = None,
    session_id: str | None = None,
    treatment: str | None = None,
    utm_source: str | None = None,
    utm_campaign: str | None = None,
    doctor: Doctor = Depends(get_current_doctor),
    db: AsyncSession = Depends(get_db),
):
    """Manually track a conversion event (e.g. from landing page JavaScript).

    Typically called by the landing page tracking pixel or the dashboard.
    """
    from app.models.call_log import ConversionStage

    try:
        stage_enum = ConversionStage(stage)
    except ValueError:
        return {"error": f"Invalid stage: {stage}. Valid: {[s.value for s in ConversionStage]}"}

    tracker = ConversionTracker(db)
    event = await tracker.track(
        doctor_id=doctor.id,
        patient_phone=patient_phone,
        session_id=session_id,
        stage=stage_enum,
        source_channel=source_channel,
        treatment=treatment,
        utm_source=utm_source,
        utm_campaign=utm_campaign,
    )
    await db.commit()

    return {"tracked": True, "event_id": str(event.id), "stage": stage}
