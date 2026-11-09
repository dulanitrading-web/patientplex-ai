"""Analytics Aggregation Service — powers the PatientPlex AI dashboard.

Computes real-time and historical metrics from conversion events,
campaign data, and appointment records. Every dashboard widget
gets its data from this service.

Key metrics:
- Patient Acquisition Cost (CAC) by channel, treatment, and time
- Full-funnel conversion rates and drop-off analysis
- Channel performance comparison (Google vs Meta vs WhatsApp vs Organic)
- Treatment-level revenue and ROI
- Hourly engagement patterns for bid optimization
"""

import logging
from datetime import datetime, timedelta, timezone
from uuid import UUID

from sqlalchemy import and_, case, cast, func, Float as SAFloat, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.call_log import ConversionEvent, ConversionStage
from app.models.campaign import Campaign, CampaignStatus, AdPlatform
from app.models.conversation import Appointment, AppointmentStatus, Conversation
from app.models.doctor import Doctor

logger = logging.getLogger(__name__)


class AnalyticsService:
    """Aggregates metrics across campaigns, conversions, and appointments."""

    def __init__(self, db: AsyncSession):
        self.db = db

    # ──────────────────────────────────────────────────────
    # Dashboard summary
    # ──────────────────────────────────────────────────────

    async def get_dashboard_summary(self, doctor_id: UUID, days: int = 30) -> dict:
        """Top-level dashboard metrics with period-over-period comparison."""
        now = datetime.now(timezone.utc)
        current_start = now - timedelta(days=days)
        previous_start = current_start - timedelta(days=days)

        current = await self._period_metrics(doctor_id, current_start, now)
        previous = await self._period_metrics(doctor_id, previous_start, current_start)

        def pct_change(curr: float, prev: float) -> float | None:
            if prev == 0:
                return None
            return round((curr - prev) / prev * 100, 1)

        return {
            "period_days": days,
            "metrics": current,
            "previous_period": previous,
            "changes": {
                "spend": pct_change(current["total_spend"], previous["total_spend"]),
                "impressions": pct_change(current["total_impressions"], previous["total_impressions"]),
                "clicks": pct_change(current["total_clicks"], previous["total_clicks"]),
                "bookings": pct_change(current["total_bookings"], previous["total_bookings"]),
                "attended": pct_change(current["total_attended"], previous["total_attended"]),
                "revenue": pct_change(current["revenue"], previous["revenue"]),
                "cac": pct_change(current["cost_per_attended"], previous["cost_per_attended"]),
            },
        }

    async def _period_metrics(self, doctor_id: UUID, start: datetime, end: datetime) -> dict:
        """Compute core metrics for a time window."""
        # Campaign metrics
        camp_result = await self.db.execute(
            select(
                func.coalesce(func.sum(Campaign.spend), 0).label("spend"),
                func.coalesce(func.sum(Campaign.impressions), 0).label("impressions"),
                func.coalesce(func.sum(Campaign.clicks), 0).label("clicks"),
                func.coalesce(func.sum(Campaign.conversions), 0).label("conversions"),
            ).where(
                and_(
                    Campaign.doctor_id == doctor_id,
                    Campaign.updated_at >= start,
                    Campaign.updated_at < end,
                )
            )
        )
        camp = camp_result.one()

        # Bookings in period
        booking_result = await self.db.execute(
            select(func.count(Appointment.id)).where(
                and_(
                    Appointment.doctor_id == doctor_id,
                    Appointment.created_at >= start,
                    Appointment.created_at < end,
                )
            )
        )
        total_bookings = booking_result.scalar() or 0

        # Attended appointments
        attended_result = await self.db.execute(
            select(func.count(Appointment.id)).where(
                and_(
                    Appointment.doctor_id == doctor_id,
                    Appointment.status == AppointmentStatus.ATTENDED,
                    Appointment.created_at >= start,
                    Appointment.created_at < end,
                )
            )
        )
        total_attended = attended_result.scalar() or 0

        # Revenue from treatment-accepted events
        rev_result = await self.db.execute(
            select(func.coalesce(func.sum(ConversionEvent.revenue_inr), 0)).where(
                and_(
                    ConversionEvent.doctor_id == doctor_id,
                    ConversionEvent.stage == ConversionStage.TREATMENT_ACCEPTED,
                    ConversionEvent.timestamp >= start,
                    ConversionEvent.timestamp < end,
                )
            )
        )
        revenue = rev_result.scalar() or 0

        spend_inr = camp.spend / 100  # paise → rupees
        ctr = camp.clicks / camp.impressions if camp.impressions > 0 else 0
        conv_rate = camp.conversions / camp.clicks if camp.clicks > 0 else 0
        cost_per_booking = spend_inr / total_bookings if total_bookings > 0 else 0
        cost_per_attended = spend_inr / total_attended if total_attended > 0 else 0
        roi = ((revenue - spend_inr) / spend_inr * 100) if spend_inr > 0 else 0

        return {
            "total_spend": round(spend_inr, 2),
            "total_impressions": camp.impressions,
            "total_clicks": camp.clicks,
            "total_conversions": camp.conversions,
            "total_bookings": total_bookings,
            "total_attended": total_attended,
            "ctr": round(ctr, 4),
            "conversion_rate": round(conv_rate, 4),
            "cost_per_booking": round(cost_per_booking, 2),
            "cost_per_attended": round(cost_per_attended, 2),
            "revenue": round(revenue, 2),
            "roi_percent": round(roi, 1),
        }

    # ──────────────────────────────────────────────────────
    # Channel performance
    # ──────────────────────────────────────────────────────

    async def get_channel_performance(self, doctor_id: UUID, days: int = 30) -> dict:
        """Break down performance by acquisition channel."""
        since = datetime.now(timezone.utc) - timedelta(days=days)

        # Conversion events by channel
        result = await self.db.execute(
            select(
                ConversionEvent.source_channel,
                ConversionEvent.stage,
                func.count(ConversionEvent.id).label("count"),
                func.coalesce(func.sum(ConversionEvent.revenue_inr), 0).label("revenue"),
            ).where(
                and_(
                    ConversionEvent.doctor_id == doctor_id,
                    ConversionEvent.timestamp >= since,
                )
            ).group_by(ConversionEvent.source_channel, ConversionEvent.stage)
        )
        rows = result.all()

        # Campaign spend by platform
        spend_result = await self.db.execute(
            select(
                Campaign.platform,
                func.coalesce(func.sum(Campaign.spend), 0).label("spend"),
                func.coalesce(func.sum(Campaign.clicks), 0).label("clicks"),
            ).where(
                and_(
                    Campaign.doctor_id == doctor_id,
                    Campaign.status.in_([CampaignStatus.ACTIVE, CampaignStatus.COMPLETED]),
                )
            ).group_by(Campaign.platform)
        )
        spend_rows = spend_result.all()

        # Build channel summary
        channels: dict[str, dict] = {}
        for row in rows:
            ch = row.source_channel
            if ch not in channels:
                channels[ch] = {"clicks": 0, "bookings": 0, "attended": 0, "revenue": 0, "spend": 0}
            if row.stage == ConversionStage.AD_CLICK:
                channels[ch]["clicks"] += row.count
            elif row.stage == ConversionStage.BOOKING_CONFIRMED:
                channels[ch]["bookings"] += row.count
            elif row.stage == ConversionStage.PATIENT_ATTENDED:
                channels[ch]["attended"] += row.count
            elif row.stage == ConversionStage.TREATMENT_ACCEPTED:
                channels[ch]["revenue"] += row.revenue

        # Map platform spend to channels
        platform_to_channel = {
            AdPlatform.GOOGLE: "google_ads",
            AdPlatform.META: "meta_ads",
            AdPlatform.LINKEDIN: "linkedin_ads",
        }
        for row in spend_rows:
            ch = platform_to_channel.get(row.platform, "other")
            if ch not in channels:
                channels[ch] = {"clicks": 0, "bookings": 0, "attended": 0, "revenue": 0, "spend": 0}
            channels[ch]["spend"] = row.spend / 100

        # Compute derived metrics
        for ch, data in channels.items():
            data["cost_per_booking"] = round(data["spend"] / data["bookings"], 2) if data["bookings"] > 0 else 0
            data["cost_per_attended"] = round(data["spend"] / data["attended"], 2) if data["attended"] > 0 else 0
            data["roi_percent"] = (
                round((data["revenue"] - data["spend"]) / data["spend"] * 100, 1)
                if data["spend"] > 0 else 0
            )

        return {"period_days": days, "channels": channels}

    # ──────────────────────────────────────────────────────
    # Campaign performance
    # ──────────────────────────────────────────────────────

    async def get_campaign_performance(self, doctor_id: UUID, days: int = 30) -> dict:
        """Per-campaign metrics with quality scores and recommendations."""
        result = await self.db.execute(
            select(Campaign).where(Campaign.doctor_id == doctor_id).order_by(Campaign.created_at.desc())
        )
        campaigns = result.scalars().all()

        campaign_data = []
        for c in campaigns:
            spend_inr = c.spend / 100
            ctr = c.clicks / c.impressions if c.impressions > 0 else 0
            conv_rate = c.conversions / c.clicks if c.clicks > 0 else 0

            # Quality score: weighted combination of CTR, conversion rate, CPA efficiency
            quality = self._compute_quality_score(c)
            recommendation = self._get_campaign_recommendation(c, quality)

            # Count bookings from this campaign
            booking_result = await self.db.execute(
                select(func.count(ConversionEvent.id)).where(
                    and_(
                        ConversionEvent.campaign_id == c.id,
                        ConversionEvent.stage == ConversionStage.BOOKING_CONFIRMED,
                    )
                )
            )
            bookings = booking_result.scalar() or 0

            campaign_data.append({
                "id": str(c.id),
                "name": c.name,
                "platform": c.platform.value,
                "status": c.status.value,
                "spend_inr": round(spend_inr, 2),
                "daily_budget_inr": c.daily_budget,
                "impressions": c.impressions,
                "clicks": c.clicks,
                "ctr": round(ctr, 4),
                "conversions": c.conversions,
                "cost_per_conversion": round(c.cost_per_conversion, 2),
                "bookings": bookings,
                "cost_per_booking": round(spend_inr / bookings, 2) if bookings > 0 else 0,
                "quality_score": quality,
                "recommendation": recommendation,
                "last_synced": c.last_synced_at.isoformat() if c.last_synced_at else None,
            })

        return {"period_days": days, "campaigns": campaign_data}

    def _compute_quality_score(self, campaign: Campaign) -> int:
        """Compute a 1-10 quality score for a campaign."""
        if campaign.impressions < 100:
            return 0  # Not enough data

        score = 5  # Start at average

        ctr = campaign.clicks / campaign.impressions if campaign.impressions > 0 else 0
        conv_rate = campaign.conversions / campaign.clicks if campaign.clicks > 0 else 0

        # CTR scoring (healthcare avg is ~3-5%)
        if ctr > 0.05:
            score += 2
        elif ctr > 0.03:
            score += 1
        elif ctr < 0.01:
            score -= 2
        elif ctr < 0.02:
            score -= 1

        # Conversion rate scoring
        if conv_rate > 0.10:
            score += 2
        elif conv_rate > 0.05:
            score += 1
        elif conv_rate < 0.01 and campaign.clicks > 50:
            score -= 2

        # CPA scoring (lower is better for healthcare in India)
        if campaign.cost_per_conversion > 0:
            if campaign.cost_per_conversion < 200:
                score += 1
            elif campaign.cost_per_conversion > 1000:
                score -= 1

        return max(1, min(10, score))

    def _get_campaign_recommendation(self, campaign: Campaign, quality: int) -> str:
        """Generate an actionable recommendation based on campaign quality."""
        if quality == 0:
            return "Needs more data — wait for 100+ impressions before optimizing"
        if quality >= 8:
            return "Performing excellently — consider increasing budget to scale"
        if quality >= 6:
            return "Performing well — test new ad variations to push further"
        if quality >= 4:
            return "Needs optimization — review keywords and ad copy"
        if quality >= 2:
            return "Underperforming — consider pausing, refreshing targeting and creatives"
        return "Critical — pause and rebuild with different approach"

    # ──────────────────────────────────────────────────────
    # Hourly performance
    # ──────────────────────────────────────────────────────

    async def get_hourly_performance(self, doctor_id: UUID, days: int = 7) -> dict:
        """Hour-by-hour engagement patterns."""
        since = datetime.now(timezone.utc) - timedelta(days=days)

        result = await self.db.execute(
            select(
                func.extract("hour", ConversionEvent.timestamp).label("hour"),
                ConversionEvent.stage,
                func.count(ConversionEvent.id).label("count"),
            ).where(
                and_(
                    ConversionEvent.doctor_id == doctor_id,
                    ConversionEvent.timestamp >= since,
                )
            ).group_by("hour", ConversionEvent.stage)
        )
        rows = result.all()

        hourly: dict[int, dict] = {h: {"clicks": 0, "whatsapp_starts": 0, "bookings": 0} for h in range(24)}

        for row in rows:
            h = int(row.hour)
            if row.stage == ConversionStage.AD_CLICK:
                hourly[h]["clicks"] += row.count
            elif row.stage == ConversionStage.WHATSAPP_STARTED:
                hourly[h]["whatsapp_starts"] += row.count
            elif row.stage == ConversionStage.BOOKING_CONFIRMED:
                hourly[h]["bookings"] += row.count

        # Find peak and dead hours
        sorted_by_clicks = sorted(hourly.items(), key=lambda x: x[1]["clicks"], reverse=True)
        peak_hours = [h for h, _ in sorted_by_clicks[:5] if sorted_by_clicks[0][1]["clicks"] > 0]
        dead_hours = [h for h, data in hourly.items() if data["clicks"] == 0 and data["bookings"] == 0]

        return {
            "period_days": days,
            "hourly": hourly,
            "peak_hours": peak_hours,
            "dead_hours": dead_hours,
            "note": "Hours are in UTC — add 5:30 for IST",
        }

    # ──────────────────────────────────────────────────────
    # Treatment analytics
    # ──────────────────────────────────────────────────────

    async def get_treatment_analytics(self, doctor_id: UUID, days: int = 30) -> dict:
        """Which treatments drive the most revenue and which cost the most to acquire."""
        since = datetime.now(timezone.utc) - timedelta(days=days)

        result = await self.db.execute(
            select(
                ConversionEvent.treatment,
                ConversionEvent.stage,
                func.count(ConversionEvent.id).label("count"),
                func.coalesce(func.sum(ConversionEvent.revenue_inr), 0).label("revenue"),
            ).where(
                and_(
                    ConversionEvent.doctor_id == doctor_id,
                    ConversionEvent.treatment.isnot(None),
                    ConversionEvent.timestamp >= since,
                )
            ).group_by(ConversionEvent.treatment, ConversionEvent.stage)
        )
        rows = result.all()

        treatments: dict[str, dict] = {}
        for row in rows:
            t = row.treatment
            if t not in treatments:
                treatments[t] = {"bookings": 0, "attended": 0, "revenue": 0}
            if row.stage == ConversionStage.BOOKING_CONFIRMED:
                treatments[t]["bookings"] += row.count
            elif row.stage == ConversionStage.PATIENT_ATTENDED:
                treatments[t]["attended"] += row.count
            elif row.stage == ConversionStage.TREATMENT_ACCEPTED:
                treatments[t]["revenue"] += row.revenue

        # Compute per-treatment metrics
        treatment_list = []
        for name, data in treatments.items():
            avg_value = data["revenue"] / data["attended"] if data["attended"] > 0 else 0
            treatment_list.append({
                "treatment": name,
                "bookings": data["bookings"],
                "attended": data["attended"],
                "show_rate": round(data["attended"] / data["bookings"] * 100, 1) if data["bookings"] > 0 else 0,
                "revenue_inr": round(data["revenue"], 2),
                "avg_treatment_value": round(avg_value, 2),
            })

        treatment_list.sort(key=lambda x: x["revenue_inr"], reverse=True)
        return {"period_days": days, "treatments": treatment_list}

    # ──────────────────────────────────────────────────────
    # Patient Acquisition Cost (CAC)
    # ──────────────────────────────────────────────────────

    async def get_patient_acquisition_cost(self, doctor_id: UUID, days: int = 30) -> dict:
        """The key metric — how much it costs to get a patient seated in the chair."""
        since = datetime.now(timezone.utc) - timedelta(days=days)

        # Total spend
        spend_result = await self.db.execute(
            select(func.coalesce(func.sum(Campaign.spend), 0)).where(
                and_(Campaign.doctor_id == doctor_id, Campaign.status != CampaignStatus.DRAFT)
            )
        )
        total_spend_paise = spend_result.scalar() or 0
        total_spend = total_spend_paise / 100

        # Total attended patients
        attended_result = await self.db.execute(
            select(func.count(Appointment.id)).where(
                and_(
                    Appointment.doctor_id == doctor_id,
                    Appointment.status == AppointmentStatus.ATTENDED,
                    Appointment.created_at >= since,
                )
            )
        )
        total_attended = attended_result.scalar() or 0

        overall_cac = total_spend / total_attended if total_attended > 0 else 0

        # CAC by channel
        channel_result = await self.db.execute(
            select(
                Campaign.platform,
                func.sum(Campaign.spend).label("spend"),
            ).where(
                and_(Campaign.doctor_id == doctor_id, Campaign.status != CampaignStatus.DRAFT)
            ).group_by(Campaign.platform)
        )

        cac_by_channel = {}
        for row in channel_result.all():
            ch_spend = (row.spend or 0) / 100
            # Get attended count per channel from conversion events
            ch_attended = await self.db.execute(
                select(func.count(ConversionEvent.id)).where(
                    and_(
                        ConversionEvent.doctor_id == doctor_id,
                        ConversionEvent.stage == ConversionStage.PATIENT_ATTENDED,
                        ConversionEvent.source_channel == row.platform.value.lower() + "_ads",
                        ConversionEvent.timestamp >= since,
                    )
                )
            )
            ch_att = ch_attended.scalar() or 0
            cac_by_channel[row.platform.value] = {
                "spend": round(ch_spend, 2),
                "attended": ch_att,
                "cac": round(ch_spend / ch_att, 2) if ch_att > 0 else 0,
            }

        # Weekly CAC trend
        weekly_trend = []
        for week in range(min(days // 7, 8)):
            week_end = since + timedelta(weeks=week + 1)
            week_start = since + timedelta(weeks=week)
            week_attended = await self.db.execute(
                select(func.count(Appointment.id)).where(
                    and_(
                        Appointment.doctor_id == doctor_id,
                        Appointment.status == AppointmentStatus.ATTENDED,
                        Appointment.created_at >= week_start,
                        Appointment.created_at < week_end,
                    )
                )
            )
            wa = week_attended.scalar() or 0
            weekly_trend.append({
                "week_start": week_start.date().isoformat(),
                "attended": wa,
            })

        return {
            "period_days": days,
            "overall_cac": round(overall_cac, 2),
            "total_spend": round(total_spend, 2),
            "total_attended": total_attended,
            "by_channel": cac_by_channel,
            "weekly_trend": weekly_trend,
        }

    # ──────────────────────────────────────────────────────
    # Funnel drop-off analysis
    # ──────────────────────────────────────────────────────

    async def get_funnel_drop_off(self, doctor_id: UUID, days: int = 30) -> dict:
        """Identify where patients are dropping off in the acquisition funnel."""
        since = datetime.now(timezone.utc) - timedelta(days=days)

        result = await self.db.execute(
            select(
                ConversionEvent.stage,
                func.count(ConversionEvent.id).label("count"),
            ).where(
                and_(
                    ConversionEvent.doctor_id == doctor_id,
                    ConversionEvent.timestamp >= since,
                )
            ).group_by(ConversionEvent.stage)
        )
        rows = result.all()
        stage_counts = {row.stage.value: row.count for row in rows}

        funnel_order = [
            ("AD_CLICK", "Ad Click"),
            ("LANDING_PAGE_VIEW", "Landing Page"),
            ("WHATSAPP_STARTED", "WhatsApp Started"),
            ("WHATSAPP_ENGAGED", "Patient Replied"),
            ("SLOT_CHECKED", "Checked Slots"),
            ("BOOKING_CONFIRMED", "Booked"),
            ("PATIENT_ATTENDED", "Attended"),
            ("TREATMENT_ACCEPTED", "Treatment Accepted"),
        ]

        funnel = []
        biggest_leak = {"stage": None, "drop_rate": 0}

        for i, (stage_key, label) in enumerate(funnel_order):
            count = stage_counts.get(stage_key, 0)
            prev_count = funnel[i - 1]["count"] if i > 0 else count
            drop_rate = round((1 - count / prev_count) * 100, 1) if prev_count > 0 and i > 0 else 0

            funnel.append({
                "stage": stage_key,
                "label": label,
                "count": count,
                "drop_rate": drop_rate,
            })

            if drop_rate > biggest_leak["drop_rate"] and i > 0:
                biggest_leak = {"stage": label, "drop_rate": drop_rate}

        # Generate recommendation for biggest leak
        leak_recommendations = {
            "Landing Page": "Improve landing page load speed and messaging clarity. Add stronger CTAs.",
            "WhatsApp Started": "Reduce friction in WhatsApp opt-in. Use clearer CTA buttons on landing page.",
            "Patient Replied": "Improve AI receptionist's opening message. Make it more conversational.",
            "Checked Slots": "Patient may not have found suitable times. Offer more slot options.",
            "Booked": "Slot availability might be limited. Consider extending hours or adding days.",
            "Attended": "Improve appointment reminders. Send 24h + 2h reminders via WhatsApp.",
            "Treatment Accepted": "Treatment presentation may need work. Coach doctors on case acceptance.",
        }

        return {
            "period_days": days,
            "funnel": funnel,
            "biggest_leak": biggest_leak,
            "recommendation": leak_recommendations.get(
                biggest_leak["stage"], "Review funnel for optimization opportunities"
            ),
        }
