"""
Conversion Bridge — Feeds PatientPlex conversion events back to ad platforms.

This is the CRITICAL missing piece. Without this, Google Ads and Meta Ads
have zero visibility into which clicks actually became patients. They can't
optimize, and the clinic owner can't see ROI.

WHAT THIS DOES:
1. When a patient books an appointment → pushes offline conversion to Google Ads
2. When a patient attends → pushes higher-value conversion to Google Ads
3. When a WhatsApp conversation starts from an ad → tracks as lead
4. When a call from Twilio tracking number comes in → tracks as call conversion

HOW GOOGLE ADS OFFLINE CONVERSIONS WORK:
- Google Ads matches the conversion to the click using the gclid (Google Click ID)
- The gclid comes from the URL when the patient clicks the ad
- We store the gclid when the patient lands on our page
- When they convert (book/attend), we upload it with the gclid
- Google then knows which keyword/ad/audience drove the appointment
- Google's AI bidding (tCPA, tROAS) uses this to optimize future ads
"""

import logging
from datetime import datetime, timezone
from uuid import UUID

from sqlalchemy import select, and_
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.call_log import ConversionEvent, ConversionStage
from app.models.campaign import Campaign, AdPlatform
from app.models.conversation import Appointment, AppointmentStatus
from app.models.doctor import Doctor

logger = logging.getLogger(__name__)


# Google Ads conversion action names
CONVERSION_ACTIONS = {
    "appointment_booked": "PatientPlex — Appointment Booked",
    "appointment_attended": "PatientPlex — Patient Attended",
    "whatsapp_lead": "PatientPlex — WhatsApp Lead",
    "phone_call": "PatientPlex — Phone Call",
}

# Conversion values by treatment type (INR)
TREATMENT_VALUES = {
    "dental implants": 80000,
    "implant": 80000,
    "smile makeover": 60000,
    "cosmetic": 40000,
    "braces": 30000,
    "aligners": 35000,
    "invisalign": 40000,
    "orthodontics": 30000,
    "root canal": 8000,
    "rct": 8000,
    "crown": 10000,
    "bridge": 15000,
    "teeth cleaning": 2000,
    "scaling": 1500,
    "whitening": 5000,
    "extraction": 3000,
    "wisdom tooth": 5000,
    "gum treatment": 4000,
    "consultation": 500,
    "checkup": 500,
}


class ConversionBridge:
    """Bridges PatientPlex conversion events to ad platforms.

    Usage:
        bridge = ConversionBridge(db)

        # When appointment is booked
        await bridge.track_appointment_booked(appointment)

        # When patient attends
        await bridge.track_appointment_attended(appointment)

        # When WhatsApp conversation starts from ad
        await bridge.track_whatsapp_lead(doctor_id, patient_phone, source_campaign)

        # When call comes in from tracking number
        await bridge.track_phone_call(doctor_id, caller_phone, duration_seconds)
    """

    def __init__(self, db: AsyncSession):
        self.db = db

    async def track_appointment_booked(
        self,
        doctor_id: UUID,
        patient_phone: str,
        treatment: str,
        source_campaign_id: UUID | None = None,
        gclid: str | None = None,
    ) -> dict:
        """Track an appointment booking as a conversion.

        This is the primary conversion event. It tells Google Ads
        'this click resulted in a patient booking.'
        """
        conversion_value = self._estimate_treatment_value(treatment)

        # Record the conversion event
        event = ConversionEvent(
            doctor_id=doctor_id,
            patient_phone=patient_phone,
            stage=ConversionStage.BOOKING_CONFIRMED,
            source_channel=self._detect_source_channel(source_campaign_id),
            source_campaign_id=source_campaign_id,
            treatment=treatment,
            conversion_value=conversion_value,
            gclid=gclid,
        )
        self.db.add(event)

        # Update campaign conversion count
        if source_campaign_id:
            result = await self.db.execute(
                select(Campaign).where(Campaign.id == source_campaign_id)
            )
            campaign = result.scalar_one_or_none()
            if campaign:
                campaign.conversions += 1
                logger.info(
                    "Conversion tracked: campaign '%s' now has %d conversions",
                    campaign.name, campaign.conversions,
                )

        # Upload to Google Ads as offline conversion (if gclid available)
        google_upload_status = "no_gclid"
        if gclid:
            google_upload_status = await self._upload_to_google_ads(
                doctor_id, gclid, CONVERSION_ACTIONS["appointment_booked"],
                conversion_value, datetime.now(timezone.utc),
            )

        await self.db.flush()

        logger.info(
            "Appointment booked conversion tracked: doctor=%s, treatment=%s, value=₹%s, gclid=%s",
            doctor_id, treatment, conversion_value, gclid or "none",
        )

        return {
            "event": "appointment_booked",
            "treatment": treatment,
            "conversion_value": conversion_value,
            "google_ads_upload": google_upload_status,
            "source_channel": event.source_channel,
        }

    async def track_appointment_attended(
        self,
        doctor_id: UUID,
        patient_phone: str,
        treatment: str,
        gclid: str | None = None,
    ) -> dict:
        """Track that a patient actually showed up — the highest-value conversion.

        This is worth more than a booking because it's confirmed revenue.
        Google Ads should bid more for keywords that lead to attended appointments.
        """
        conversion_value = self._estimate_treatment_value(treatment)

        event = ConversionEvent(
            doctor_id=doctor_id,
            patient_phone=patient_phone,
            stage=ConversionStage.PATIENT_ATTENDED,
            treatment=treatment,
            conversion_value=conversion_value,
            gclid=gclid,
        )
        self.db.add(event)

        if gclid:
            await self._upload_to_google_ads(
                doctor_id, gclid, CONVERSION_ACTIONS["appointment_attended"],
                conversion_value, datetime.now(timezone.utc),
            )

        await self.db.flush()

        return {
            "event": "patient_attended",
            "treatment": treatment,
            "conversion_value": conversion_value,
        }

    async def track_whatsapp_lead(
        self,
        doctor_id: UUID,
        patient_phone: str,
        source_campaign_id: UUID | None = None,
        gclid: str | None = None,
    ) -> dict:
        """Track a WhatsApp conversation as a lead conversion.

        This is a lighter conversion — the patient engaged but hasn't booked yet.
        Still valuable for Google Ads optimization (shows interest).
        """
        event = ConversionEvent(
            doctor_id=doctor_id,
            patient_phone=patient_phone,
            stage=ConversionStage.WHATSAPP_STARTED,
            source_channel="whatsapp",
            source_campaign_id=source_campaign_id,
            conversion_value=500,  # ₹500 lead value
            gclid=gclid,
        )
        self.db.add(event)
        await self.db.flush()

        if gclid:
            await self._upload_to_google_ads(
                doctor_id, gclid, CONVERSION_ACTIONS["whatsapp_lead"],
                500, datetime.now(timezone.utc),
            )

        return {"event": "whatsapp_lead", "conversion_value": 500}

    async def track_phone_call(
        self,
        doctor_id: UUID,
        caller_phone: str,
        duration_seconds: int,
        source_campaign_id: UUID | None = None,
        gclid: str | None = None,
    ) -> dict:
        """Track a phone call as a conversion.

        Only calls > 30 seconds are considered meaningful conversions.
        Short calls are likely wrong numbers or IVR abandons.
        """
        if duration_seconds < 30:
            return {"event": "phone_call", "tracked": False, "reason": "Too short (<30s)"}

        # Longer calls are worth more (more likely to result in a booking)
        if duration_seconds >= 180:
            value = 2000  # 3+ min call = serious enquiry
        elif duration_seconds >= 60:
            value = 1000  # 1-3 min call = interested
        else:
            value = 500   # 30-60s = basic enquiry

        event = ConversionEvent(
            doctor_id=doctor_id,
            patient_phone=caller_phone,
            stage=ConversionStage.CALL_CONNECTED,
            source_channel="phone",
            source_campaign_id=source_campaign_id,
            conversion_value=value,
            gclid=gclid,
        )
        self.db.add(event)
        await self.db.flush()

        if gclid:
            await self._upload_to_google_ads(
                doctor_id, gclid, CONVERSION_ACTIONS["phone_call"],
                value, datetime.now(timezone.utc),
            )

        return {
            "event": "phone_call",
            "tracked": True,
            "duration_seconds": duration_seconds,
            "conversion_value": value,
        }

    async def get_conversion_summary(self, doctor_id: UUID, days: int = 30) -> dict:
        """Get a summary of all conversions for the dashboard.

        Returns doctor-friendly metrics: total patients, cost per patient, ROI.
        """
        from datetime import timedelta

        cutoff = datetime.now(timezone.utc) - timedelta(days=days)

        result = await self.db.execute(
            select(ConversionEvent).where(
                and_(
                    ConversionEvent.doctor_id == doctor_id,
                    ConversionEvent.created_at >= cutoff,
                )
            )
        )
        events = list(result.scalars().all())

        bookings = [e for e in events if e.stage == ConversionStage.BOOKING_CONFIRMED]
        attended = [e for e in events if e.stage == ConversionStage.PATIENT_ATTENDED]
        leads = [e for e in events if e.stage in (
            ConversionStage.WHATSAPP_STARTED,
            ConversionStage.CALL_CONNECTED,
        )]

        total_revenue = sum(e.conversion_value or 0 for e in attended)

        # Get total ad spend for the period
        campaign_result = await self.db.execute(
            select(Campaign).where(Campaign.doctor_id == doctor_id)
        )
        campaigns = list(campaign_result.scalars().all())
        total_spend = sum(c.spend for c in campaigns)

        return {
            "period_days": days,
            "total_leads": len(leads),
            "total_bookings": len(bookings),
            "total_attended": len(attended),
            "no_show_rate": round(
                (len(bookings) - len(attended)) / len(bookings) * 100, 1
            ) if bookings else 0,
            "total_revenue_estimate": total_revenue,
            "total_ad_spend": total_spend,
            "cost_per_lead": round(total_spend / len(leads)) if leads else None,
            "cost_per_booking": round(total_spend / len(bookings)) if bookings else None,
            "cost_per_patient": round(total_spend / len(attended)) if attended else None,
            "roi_percent": round(
                (total_revenue - total_spend) / total_spend * 100, 1
            ) if total_spend > 0 else None,
        }

    # ─── Internal helpers ───

    def _estimate_treatment_value(self, treatment: str) -> int:
        """Estimate the INR value of a treatment for conversion tracking."""
        if not treatment:
            return 2000  # Default appointment value

        treatment_lower = treatment.lower()
        for keyword, value in TREATMENT_VALUES.items():
            if keyword in treatment_lower:
                return value

        return 5000  # Default for unrecognized treatments

    def _detect_source_channel(self, campaign_id: UUID | None) -> str:
        """Detect which channel a conversion came from."""
        if not campaign_id:
            return "direct"
        # Would query the campaign's platform in production
        return "google_ads"

    async def _upload_to_google_ads(
        self,
        doctor_id: UUID,
        gclid: str,
        conversion_action_name: str,
        conversion_value: int,
        conversion_time: datetime,
    ) -> str:
        """Upload an offline conversion to Google Ads.

        This is where the magic happens — Google Ads learns which clicks
        become real patients and optimizes future bidding accordingly.

        Uses Google Ads API ConversionUploadService:
        POST /v26/customers/{customer_id}:uploadClickConversions

        Returns: "uploaded", "failed", or "not_configured"
        """
        doctor = await self.db.get(Doctor, doctor_id)
        if not doctor or not getattr(doctor, "google_ads_connected", False):
            return "not_configured"

        customer_id = getattr(doctor, "google_ads_customer_id", None)
        if not customer_id:
            return "not_configured"

        # TODO: Implement actual Google Ads API upload
        # The upload requires:
        # 1. Creating a ConversionAction in the Google Ads account (one-time setup)
        # 2. Uploading each conversion with: gclid, conversion_action, conversion_time, value
        #
        # API: POST https://googleads.googleapis.com/v26/customers/{customer_id}:uploadClickConversions
        # Body: {
        #   "conversions": [{
        #     "gclid": "...",
        #     "conversion_action": "customers/{id}/conversionActions/{action_id}",
        #     "conversion_date_time": "2026-11-16 10:30:00+05:30",
        #     "conversion_value": 8000,
        #     "currency_code": "INR"
        #   }],
        #   "partial_failure": true
        # }
        #
        # For now, log and return pending
        logger.info(
            "OFFLINE CONVERSION UPLOAD: customer=%s, gclid=%s, action=%s, value=₹%d",
            customer_id, gclid, conversion_action_name, conversion_value,
        )
        return "pending_implementation"
