"""Analytics API endpoints — powers the PatientPlex AI dashboard."""

import logging
from datetime import datetime, timedelta, timezone
from uuid import UUID

from fastapi import APIRouter, Depends, Query
from sqlalchemy import func, select, and_
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
    period: str = Query("30d", description="Preset period: 7d, 14d, 30d, 90d, 365d, today, this_week, this_month"),
    db: AsyncSession = Depends(get_db),
    doctor_id: UUID = Depends(get_current_doctor_id),
):
    """Top-level dashboard metrics with period-over-period comparison.

    Returns total spend, impressions, clicks, bookings, attended patients,
    revenue, ROI, and percentage changes vs. the previous period.

    Supports period presets: today, this_week, this_month, 7d, 14d, 30d, 90d, 365d.
    """
    # Map period presets to days
    period_map = {
        "today": 1, "7d": 7, "14d": 14, "30d": 30,
        "90d": 90, "365d": 365, "this_week": 7, "this_month": 30,
    }
    effective_days = period_map.get(period, days)

    service = AnalyticsService(db)
    return await service.get_dashboard_summary(doctor_id, effective_days)


@router.get("/lead-stats")
async def lead_stats(
    period: str = Query("30d", description="Period: today, 7d, 14d, 30d, 90d"),
    db: AsyncSession = Depends(get_db),
    doctor_id: UUID = Depends(get_current_doctor_id),
):
    """Lead statistics with daily trend for sparkline charts.

    Returns total leads, leads by source, and a daily breakdown
    for rendering sparkline/trend charts on the dashboard.
    Auto-synced — no manual fetch needed.
    """
    from app.models.patient import Patient

    now = datetime.now(timezone.utc)
    period_days = {"today": 1, "7d": 7, "14d": 14, "30d": 30, "90d": 90}.get(period, 30)
    since = now - timedelta(days=period_days)
    prev_since = since - timedelta(days=period_days)

    # Current period leads
    current_q = select(func.count(Patient.id)).where(
        and_(Patient.doctor_id == doctor_id, Patient.created_at >= since)
    )
    current_result = await db.execute(current_q)
    current_total = current_result.scalar() or 0

    # Previous period leads
    prev_q = select(func.count(Patient.id)).where(
        and_(
            Patient.doctor_id == doctor_id,
            Patient.created_at >= prev_since,
            Patient.created_at < since,
        )
    )
    prev_result = await db.execute(prev_q)
    prev_total = prev_result.scalar() or 0

    # Daily breakdown for sparkline
    daily_q = select(
        func.date(Patient.created_at).label("day"),
        func.count(Patient.id).label("count"),
    ).where(
        and_(Patient.doctor_id == doctor_id, Patient.created_at >= since)
    ).group_by(func.date(Patient.created_at)).order_by(func.date(Patient.created_at))
    daily_result = await db.execute(daily_q)
    daily_rows = daily_result.all()

    # By source
    source_q = select(
        Patient.source,
        func.count(Patient.id).label("count"),
    ).where(
        and_(Patient.doctor_id == doctor_id, Patient.created_at >= since)
    ).group_by(Patient.source)
    source_result = await db.execute(source_q)
    by_source = {row.source or "unknown": row.count for row in source_result.all()}

    pct_change = None
    if prev_total > 0:
        pct_change = round((current_total - prev_total) / prev_total * 100, 1)

    return {
        "period": period,
        "total_leads": current_total,
        "previous_period_leads": prev_total,
        "change_pct": pct_change,
        "by_source": by_source,
        "daily_trend": [{"date": str(r.day), "count": r.count} for r in daily_rows],
        "auto_synced": True,
        "last_updated": now.isoformat(),
    }


@router.get("/trend")
async def metric_trend(
    metric: str = Query("leads", description="Metric: leads, spend, clicks, impressions, bookings, revenue"),
    period: str = Query("30d", description="Period: 7d, 14d, 30d, 90d"),
    db: AsyncSession = Depends(get_db),
    doctor_id: UUID = Depends(get_current_doctor_id),
):
    """Daily trend data for any metric — powers sparkline charts.

    Returns an array of {date, value} pairs for the requested metric
    over the given period. Used for dashboard sparklines and charts.
    """
    from app.models.patient import Patient
    from app.models.campaign import Campaign
    from app.models.conversation import Appointment

    now = datetime.now(timezone.utc)
    period_days = {"7d": 7, "14d": 14, "30d": 30, "90d": 90}.get(period, 30)
    since = now - timedelta(days=period_days)

    if metric == "leads":
        q = select(
            func.date(Patient.created_at).label("day"),
            func.count(Patient.id).label("value"),
        ).where(
            and_(Patient.doctor_id == doctor_id, Patient.created_at >= since)
        ).group_by(func.date(Patient.created_at)).order_by(func.date(Patient.created_at))
    elif metric == "bookings":
        q = select(
            func.date(Appointment.created_at).label("day"),
            func.count(Appointment.id).label("value"),
        ).where(
            and_(Appointment.doctor_id == doctor_id, Appointment.created_at >= since)
        ).group_by(func.date(Appointment.created_at)).order_by(func.date(Appointment.created_at))
    elif metric in ("spend", "clicks", "impressions"):
        col = getattr(Campaign, metric)
        q = select(
            func.date(Campaign.updated_at).label("day"),
            func.coalesce(func.sum(col), 0).label("value"),
        ).where(
            and_(Campaign.doctor_id == doctor_id, Campaign.updated_at >= since)
        ).group_by(func.date(Campaign.updated_at)).order_by(func.date(Campaign.updated_at))
    else:
        return {"error": f"Unknown metric: {metric}", "valid": ["leads", "spend", "clicks", "impressions", "bookings"]}

    result = await db.execute(q)
    rows = result.all()

    return {
        "metric": metric,
        "period": period,
        "data": [{"date": str(r.day), "value": float(r.value)} for r in rows],
        "auto_synced": True,
    }


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
