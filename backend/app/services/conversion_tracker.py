"""Conversion tracking service — records every step of the patient funnel.

Tracks the complete journey:
  Ad impression → Click → Landing page → Call/WhatsApp → Conversation →
  Slot check → Booking → Confirmation → Reminder → Attended → Treatment accepted

Every step is an immutable event stored in conversion_events, enabling:
- Full-funnel analytics (where are patients dropping off?)
- Cost-per-stage calculations (what does a seated patient actually cost?)
- Source attribution (which Google keyword brought the patient who got braces?)
- ROI tracking (₹X spent on ads → ₹Y in treatment revenue)
"""

import logging
from datetime import datetime, timezone
from uuid import UUID

from sqlalchemy import and_, func, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.call_log import ConversionEvent, ConversionStage

logger = logging.getLogger(__name__)


class ConversionTracker:
    """Records and queries conversion events across the patient funnel."""

    def __init__(self, db: AsyncSession):
        self.db = db

    async def track(
        self,
        doctor_id: UUID,
        stage: ConversionStage,
        source_channel: str,
        patient_phone: str | None = None,
        session_id: str | None = None,
        utm_source: str | None = None,
        utm_campaign: str | None = None,
        utm_medium: str | None = None,
        utm_content: str | None = None,
        campaign_id: UUID | None = None,
        conversation_id: UUID | None = None,
        appointment_id: UUID | None = None,
        call_log_id: UUID | None = None,
        treatment: str | None = None,
        revenue_inr: float | None = None,
        extra_data: dict | None = None,
    ) -> ConversionEvent:
        """Record a conversion event.

        Call this at every meaningful step of the patient journey.
        """
        event = ConversionEvent(
            doctor_id=doctor_id,
            patient_phone=patient_phone,
            session_id=session_id,
            stage=stage,
            source_channel=source_channel,
            utm_source=utm_source,
            utm_campaign=utm_campaign,
            utm_medium=utm_medium,
            utm_content=utm_content,
            campaign_id=campaign_id,
            conversation_id=conversation_id,
            appointment_id=appointment_id,
            call_log_id=call_log_id,
            treatment=treatment,
            revenue_inr=revenue_inr,
            extra_data=extra_data,
        )
        self.db.add(event)
        await self.db.flush()

        logger.info(
            "Conversion: doctor=%s stage=%s channel=%s phone=%s",
            doctor_id, stage.value, source_channel, patient_phone or "anon",
        )
        return event

    async def get_funnel_stats(
        self,
        doctor_id: UUID,
        days: int = 30,
        source_channel: str | None = None,
    ) -> dict:
        """Get full-funnel conversion stats for a doctor.

        Returns count at each stage, conversion rates between stages,
        and cost-per-stage if spend data is available.
        """
        from datetime import timedelta
        since = datetime.now(timezone.utc) - timedelta(days=days)

        query = select(
            ConversionEvent.stage,
            func.count(ConversionEvent.id).label("count"),
            func.count(func.distinct(ConversionEvent.patient_phone)).label("unique_patients"),
        ).where(
            and_(
                ConversionEvent.doctor_id == doctor_id,
                ConversionEvent.timestamp >= since,
            )
        ).group_by(ConversionEvent.stage)

        if source_channel:
            query = query.where(ConversionEvent.source_channel == source_channel)

        result = await self.db.execute(query)
        rows = result.all()

        stage_data = {row.stage.value: {"count": row.count, "unique": row.unique_patients} for row in rows}

        # Define funnel order and calculate conversion rates
        funnel_order = [
            "AD_CLICK", "LANDING_PAGE_VIEW", "CALL_ATTEMPTED", "CALL_MISSED",
            "WHATSAPP_STARTED", "WHATSAPP_ENGAGED", "SLOT_CHECKED",
            "SLOT_OFFERED", "BOOKING_CONFIRMED", "CONFIRMATION_SENT",
            "REMINDER_24H", "PATIENT_ATTENDED", "TREATMENT_ACCEPTED",
        ]

        funnel = []
        for i, stage_name in enumerate(funnel_order):
            data = stage_data.get(stage_name, {"count": 0, "unique": 0})
            prev_count = funnel[i - 1]["count"] if i > 0 and funnel[i - 1]["count"] > 0 else None
            conversion_rate = round(data["count"] / prev_count * 100, 1) if prev_count else None

            funnel.append({
                "stage": stage_name,
                "count": data["count"],
                "unique_patients": data["unique"],
                "conversion_rate": conversion_rate,
            })

        return {
            "period_days": days,
            "funnel": funnel,
            "total_stages_tracked": sum(d["count"] for d in stage_data.values()),
            "source_channel": source_channel or "all",
        }

    async def get_source_attribution(self, doctor_id: UUID, days: int = 30) -> dict:
        """Break down conversions by source channel.

        Shows which channel (Google Ads, Meta, organic, calls) drives
        the most booked patients.
        """
        from datetime import timedelta
        since = datetime.now(timezone.utc) - timedelta(days=days)

        result = await self.db.execute(
            select(
                ConversionEvent.source_channel,
                ConversionEvent.stage,
                func.count(ConversionEvent.id),
            ).where(
                and_(
                    ConversionEvent.doctor_id == doctor_id,
                    ConversionEvent.timestamp >= since,
                )
            ).group_by(ConversionEvent.source_channel, ConversionEvent.stage)
        )
        rows = result.all()

        # Pivot: {channel: {stage: count}}
        channels: dict[str, dict[str, int]] = {}
        for channel, stage, count in rows:
            if channel not in channels:
                channels[channel] = {}
            channels[channel][stage.value] = count

        return {
            "period_days": days,
            "by_channel": channels,
            "channels_active": list(channels.keys()),
        }

    async def get_patient_journey(self, doctor_id: UUID, patient_phone: str) -> list[dict]:
        """Get the complete journey of a specific patient.

        Shows every touchpoint in chronological order — useful for
        understanding how a patient moved from ad click to seated appointment.
        """
        result = await self.db.execute(
            select(ConversionEvent).where(
                and_(
                    ConversionEvent.doctor_id == doctor_id,
                    ConversionEvent.patient_phone == patient_phone,
                )
            ).order_by(ConversionEvent.timestamp.asc())
        )
        events = result.scalars().all()

        return [
            {
                "stage": e.stage.value,
                "source_channel": e.source_channel,
                "treatment": e.treatment,
                "timestamp": e.timestamp.isoformat(),
                "metadata": e.metadata,
            }
            for e in events
        ]
