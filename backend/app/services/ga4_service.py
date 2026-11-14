"""Google Analytics 4 integration — track events and pull reporting data.

Uses the GA4 Measurement Protocol for server-side event tracking
and the GA4 Data API for pulling analytics reports.

Server-side tracking ensures:
- Ad click → WhatsApp → Booking → Attended conversion chain is tracked
- Events fire even when patient doesn't visit the website (WhatsApp-only flow)
- Revenue attribution works end-to-end
"""

import logging
from datetime import datetime, timezone
from uuid import UUID

import httpx

from app.core.config import settings

logger = logging.getLogger(__name__)

GA4_MEASUREMENT_URL = "https://www.google-analytics.com/mp/collect"
GA4_DATA_API_BASE = "https://analyticsdata.googleapis.com/v1beta"


class GA4Service:
    """Manages Google Analytics 4 event tracking and reporting for clinics."""

    def __init__(self):
        self.measurement_id = settings.GA4_MEASUREMENT_ID
        self.api_secret = settings.GA4_API_SECRET
        self.property_id = settings.GA4_PROPERTY_ID

    # ─── Server-Side Event Tracking (Measurement Protocol) ───

    async def track_event(
        self,
        client_id: str,
        event_name: str,
        params: dict | None = None,
        user_id: str | None = None,
    ) -> dict:
        """Send a server-side event to GA4 via Measurement Protocol.

        Events tracked:
        - ad_click: Patient clicked a Google/Meta ad
        - whatsapp_start: Patient started WhatsApp conversation
        - slot_checked: AI checked calendar availability
        - booking_confirmed: Appointment booked
        - reminder_sent: WhatsApp reminder sent
        - patient_attended: Patient showed up
        - revenue_recorded: Treatment revenue attributed

        Args:
            client_id: GA4 client ID (from cookie or generated)
            event_name: GA4 event name
            params: Event parameters (treatment, revenue, source, etc.)
            user_id: Optional doctor/patient identifier
        """
        if not self.measurement_id or not self.api_secret:
            logger.debug("GA4 not configured — event %s skipped", event_name)
            return {"tracked": False, "reason": "GA4 not configured"}

        payload = {
            "client_id": client_id,
            "events": [
                {
                    "name": event_name,
                    "params": {
                        **(params or {}),
                        "engagement_time_msec": "1",
                    },
                }
            ],
        }
        if user_id:
            payload["user_id"] = user_id

        try:
            async with httpx.AsyncClient() as client:
                resp = await client.post(
                    GA4_MEASUREMENT_URL,
                    params={
                        "measurement_id": self.measurement_id,
                        "api_secret": self.api_secret,
                    },
                    json=payload,
                    timeout=10,
                )
                # GA4 Measurement Protocol returns 204 on success
                if resp.status_code in (200, 204):
                    logger.info("GA4 event tracked: %s", event_name)
                    return {"tracked": True, "event": event_name}
                else:
                    logger.warning("GA4 event failed: %s %s", resp.status_code, resp.text)
                    return {"tracked": False, "status": resp.status_code}
        except Exception as exc:
            logger.error("GA4 tracking error: %s", exc)
            return {"tracked": False, "error": str(exc)}

    # ─── Conversion Events ───

    async def track_ad_click(self, client_id: str, doctor_id: str, source: str, keyword: str = "") -> dict:
        return await self.track_event(client_id, "ad_click", {
            "source": source, "keyword": keyword, "doctor_id": doctor_id,
        })

    async def track_whatsapp_start(self, client_id: str, doctor_id: str, patient_phone: str) -> dict:
        return await self.track_event(client_id, "whatsapp_conversation_start", {
            "doctor_id": doctor_id, "patient_phone_hash": hash(patient_phone) % 10**8,
        })

    async def track_booking(self, client_id: str, doctor_id: str, treatment: str, value: float = 0) -> dict:
        return await self.track_event(client_id, "booking_confirmed", {
            "doctor_id": doctor_id, "treatment": treatment, "value": value, "currency": "INR",
        })

    async def track_patient_attended(self, client_id: str, doctor_id: str, treatment: str, revenue: float = 0) -> dict:
        return await self.track_event(client_id, "patient_attended", {
            "doctor_id": doctor_id, "treatment": treatment, "value": revenue, "currency": "INR",
        })

    async def track_revenue(self, client_id: str, doctor_id: str, treatment: str, amount: float) -> dict:
        """Track actual treatment revenue — the final conversion event."""
        return await self.track_event(client_id, "purchase", {
            "doctor_id": doctor_id, "transaction_id": f"rev_{doctor_id}_{int(datetime.now(timezone.utc).timestamp())}",
            "value": amount, "currency": "INR", "items": [{"item_name": treatment}],
        })

    # ─── GA4 Data API (Reporting) ───

    async def get_report(
        self,
        date_range: str = "30daysAgo",
        metrics: list[str] | None = None,
        dimensions: list[str] | None = None,
    ) -> dict:
        """Pull a report from GA4 Data API.

        Requires OAuth credentials or service account with GA4 access.
        """
        if not self.property_id:
            return self._demo_report()

        default_metrics = metrics or ["activeUsers", "sessions", "conversions", "totalRevenue"]
        default_dims = dimensions or ["date", "source", "medium"]

        body = {
            "dateRanges": [{"startDate": date_range, "endDate": "today"}],
            "metrics": [{"name": m} for m in default_metrics],
            "dimensions": [{"name": d} for d in default_dims],
        }

        try:
            async with httpx.AsyncClient() as client:
                resp = await client.post(
                    f"{GA4_DATA_API_BASE}/properties/{self.property_id}:runReport",
                    json=body,
                    headers={"Authorization": f"Bearer {settings.GA4_API_SECRET}"},
                    timeout=15,
                )
                resp.raise_for_status()
                return resp.json()
        except Exception as exc:
            logger.warning("GA4 report failed: %s", exc)
            return self._demo_report()

    async def get_realtime_report(self) -> dict:
        """Pull realtime data from GA4."""
        if not self.property_id:
            return {
                "demo_mode": True,
                "active_users": 3,
                "top_pages": ["/", "/signup", "/about"],
                "top_sources": ["google_ads", "whatsapp", "direct"],
            }

        try:
            async with httpx.AsyncClient() as client:
                resp = await client.post(
                    f"{GA4_DATA_API_BASE}/properties/{self.property_id}:runRealtimeReport",
                    json={"metrics": [{"name": "activeUsers"}]},
                    headers={"Authorization": f"Bearer {settings.GA4_API_SECRET}"},
                    timeout=10,
                )
                resp.raise_for_status()
                return resp.json()
        except Exception as exc:
            logger.warning("GA4 realtime failed: %s", exc)
            return {"demo_mode": True, "active_users": 0}

    def _demo_report(self) -> dict:
        return {
            "demo_mode": True,
            "period": "Last 30 days",
            "metrics": {
                "active_users": 342,
                "sessions": 1247,
                "conversions": 89,
                "total_revenue": 267000,
                "avg_session_duration": "2m 34s",
                "bounce_rate": "42.3%",
            },
            "top_sources": [
                {"source": "google_ads", "users": 187, "conversions": 52},
                {"source": "meta_ads", "users": 89, "conversions": 24},
                {"source": "direct", "users": 34, "conversions": 8},
                {"source": "organic", "users": 22, "conversions": 3},
                {"source": "whatsapp", "users": 10, "conversions": 2},
            ],
            "top_pages": [
                {"page": "/", "views": 892},
                {"page": "/signup", "views": 234},
                {"page": "/about", "views": 121},
            ],
            "conversion_funnel": {
                "ad_clicks": 1247,
                "whatsapp_starts": 342,
                "bookings": 89,
                "attended": 74,
                "conversion_rate": "7.1%",
            },
            "message": "Connect GA4 for real analytics data",
        }


ga4_service = GA4Service()
