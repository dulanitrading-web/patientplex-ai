"""Analytics API endpoints — powers the PatientPlex AI dashboard."""

import logging
from uuid import UUID

from fastapi import APIRouter, Depends, Query
from sqlalchemy.ext.asyncio import AsyncSession

from app.db.session import get_db
from app.services.analytics_service import AnalyticsService

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/analytics", tags=["analytics"])


# TODO: Replace with actual auth dependency that extracts doctor_id from JWT
async def get_current_doctor_id() -> UUID:
    """Placeholder — in production, extracts doctor_id from the authenticated JWT token."""
    from uuid import uuid4
    return uuid4()


@router.get("/dashboard")
async def dashboard_summary(
    days: int = Query(30, ge=1, le=365, description="Number of days to analyze"),
    db: AsyncSession = Depends(get_db),
    doctor_id: UUID = Depends(get_current_doctor_id),
):
    """Top-level dashboard metrics with period-over-period comparison.

    Returns total spend, impressions, clicks, bookings, attended patients,
    revenue, ROI, and percentage changes vs. the previous period.
    """
    service = AnalyticsService(db)
    return await service.get_dashboard_summary(doctor_id, days)


@router.get("/channels")
async def channel_performance(
    days: int = Query(30, ge=1, le=365),
    db: AsyncSession = Depends(get_db),
    doctor_id: UUID = Depends(get_current_doctor_id),
):
    """Performance breakdown by acquisition channel (Google, Meta, WhatsApp, organic)."""
    service = AnalyticsService(db)
    return await service.get_channel_performance(doctor_id, days)


@router.get("/campaigns")
async def campaign_performance(
    days: int = Query(30, ge=1, le=365),
    db: AsyncSession = Depends(get_db),
    doctor_id: UUID = Depends(get_current_doctor_id),
):
    """Per-campaign metrics with quality scores and recommendations."""
    service = AnalyticsService(db)
    return await service.get_campaign_performance(doctor_id, days)


@router.get("/hourly")
async def hourly_performance(
    days: int = Query(7, ge=1, le=30),
    db: AsyncSession = Depends(get_db),
    doctor_id: UUID = Depends(get_current_doctor_id),
):
    """Hour-by-hour engagement patterns to identify peak times."""
    service = AnalyticsService(db)
    return await service.get_hourly_performance(doctor_id, days)


@router.get("/treatments")
async def treatment_analytics(
    days: int = Query(30, ge=1, le=365),
    db: AsyncSession = Depends(get_db),
    doctor_id: UUID = Depends(get_current_doctor_id),
):
    """Treatment-level revenue and acquisition metrics."""
    service = AnalyticsService(db)
    return await service.get_treatment_analytics(doctor_id, days)


@router.get("/cac")
async def patient_acquisition_cost(
    days: int = Query(30, ge=1, le=365),
    db: AsyncSession = Depends(get_db),
    doctor_id: UUID = Depends(get_current_doctor_id),
):
    """Patient Acquisition Cost — overall, by channel, and weekly trend."""
    service = AnalyticsService(db)
    return await service.get_patient_acquisition_cost(doctor_id, days)


@router.get("/funnel")
async def funnel_drop_off(
    days: int = Query(30, ge=1, le=365),
    db: AsyncSession = Depends(get_db),
    doctor_id: UUID = Depends(get_current_doctor_id),
):
    """Funnel drop-off analysis — where patients are being lost."""
    service = AnalyticsService(db)
    return await service.get_funnel_drop_off(doctor_id, days)
