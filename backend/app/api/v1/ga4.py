"""Google Analytics 4 endpoints — server-side event tracking and reporting.

Provides:
- Server-side conversion event tracking via GA4 Measurement Protocol
- Analytics reporting via GA4 Data API
- Realtime active user data
- Full conversion funnel: ad_click → whatsapp_start → booking → attended → revenue
"""

from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel
from sqlalchemy.ext.asyncio import AsyncSession

from app.api.v1.auth import get_current_doctor
from app.db.session import get_db
from app.models.doctor import Doctor
from app.services.ga4_service import ga4_service

router = APIRouter(prefix="/ga4", tags=["google-analytics-4"])


# ─── Request Models ───

class TrackEventRequest(BaseModel):
    client_id: str
    event_name: str
    params: dict | None = None
    user_id: str | None = None


class TrackBookingRequest(BaseModel):
    client_id: str
    treatment: str
    value: float = 0


class TrackRevenueRequest(BaseModel):
    client_id: str
    treatment: str
    amount: float


# ─── Event Tracking ───

@router.post("/track")
async def track_event(
    body: TrackEventRequest,
    doctor: Doctor = Depends(get_current_doctor),
):
    """Track a custom GA4 event via Measurement Protocol.

    Server-side tracking ensures events fire even for WhatsApp-only flows.
    """
    result = await ga4_service.track_event(
        client_id=body.client_id,
        event_name=body.event_name,
        params={**(body.params or {}), "doctor_id": str(doctor.id)},
        user_id=body.user_id,
    )
    return result


@router.post("/track/booking")
async def track_booking(
    body: TrackBookingRequest,
    doctor: Doctor = Depends(get_current_doctor),
):
    """Track a confirmed booking as a GA4 conversion event."""
    return await ga4_service.track_booking(
        client_id=body.client_id,
        doctor_id=str(doctor.id),
        treatment=body.treatment,
        value=body.value,
    )


@router.post("/track/revenue")
async def track_revenue(
    body: TrackRevenueRequest,
    doctor: Doctor = Depends(get_current_doctor),
):
    """Track treatment revenue as a GA4 purchase event."""
    return await ga4_service.track_revenue(
        client_id=body.client_id,
        doctor_id=str(doctor.id),
        treatment=body.treatment,
        amount=body.amount,
    )


# ─── Reporting ───

@router.get("/report")
async def get_analytics_report(
    date_range: str = "30daysAgo",
    doctor: Doctor = Depends(get_current_doctor),
):
    """Pull an analytics report from GA4 Data API.

    Returns: active users, sessions, conversions, revenue,
    top sources, top pages, and conversion funnel metrics.
    Falls back to demo data if GA4 is not connected.
    """
    return await ga4_service.get_report(date_range=date_range)


@router.get("/realtime")
async def get_realtime(
    doctor: Doctor = Depends(get_current_doctor),
):
    """Get realtime active users from GA4.

    Returns current active visitors, top pages, and top sources.
    """
    return await ga4_service.get_realtime_report()
