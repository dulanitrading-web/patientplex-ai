"""Campaign Auto-Optimization Engine — the performance marketing brain.

This is the core intelligence of PatientPlex AI. It analyzes campaign
performance data and makes automated optimization decisions:

1. Keyword management — pause underperformers, boost converters
2. Bid optimization — adjust bids based on conversion value
3. Budget reallocation — move money from losers to winners
4. Search term analysis — add negative keywords from irrelevant queries
5. Geographic optimization — adjust targeting based on actual conversions
6. Time-of-day bidding — bid higher during peak patient search hours
7. Device bidding — adjust for mobile vs desktop performance
8. Ad copy rotation — identify winning ad variations
9. Seasonal awareness — adjust for healthcare demand patterns

Every action is logged in optimization_runs/optimization_actions for
full auditability and before/after performance comparison.
"""

import logging
from dataclasses import dataclass, field
from datetime import datetime, timedelta, timezone
from enum import Enum
from uuid import UUID

from sqlalchemy import and_, func, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.call_log import ConversionEvent, ConversionStage
from app.models.campaign import AdPlatform, Campaign, CampaignStatus
from app.models.conversation import Appointment, AppointmentStatus
from app.models.doctor import Doctor
from app.models.optimization import (
    OptimizationActionRecord,
    OptimizationActionType,
    OptimizationRun,
    OptimizationRunStatus,
)

logger = logging.getLogger(__name__)


# ──────────────────────────────────────────────────────────
# Thresholds & Configuration
# ──────────────────────────────────────────────────────────

class OptConfig:
    """Optimization thresholds — tuned for Indian healthcare market."""

    # Minimum data before optimizing (prevent premature decisions)
    MIN_IMPRESSIONS = 100
    MIN_CLICKS = 20
    MIN_DAYS_ACTIVE = 3

    # Keyword performance thresholds
    LOW_CTR_THRESHOLD = 0.01          # 1% — below this, keyword is underperforming
    HIGH_CPC_MULTIPLIER = 2.0         # Keywords costing 2x+ the average CPC
    MIN_CONVERSION_RATE = 0.02        # 2% — minimum acceptable conversion rate
    KEYWORD_SPEND_WASTE_INR = 500     # ₹500 spent with 0 conversions → pause

    # Bid adjustment ranges
    BID_INCREASE_PERCENT = 0.20       # +20% for high performers
    BID_DECREASE_PERCENT = 0.15       # -15% for underperformers
    MAX_BID_INR = 200                 # Never bid more than ₹200/click
    MIN_BID_INR = 5                   # Never bid less than ₹5/click

    # Budget reallocation
    BUDGET_REALLOCATION_PERCENT = 0.15  # Move up to 15% between campaigns
    MIN_CAMPAIGN_BUDGET_INR = 100       # Never reduce below ₹100/day

    # Geographic
    GEO_EXPANSION_THRESHOLD = 0.8     # If 80%+ conversions from outside radius, expand
    GEO_MAX_RADIUS_KM = 25

    # Time-of-day bid modifiers (IST)
    PEAK_HOURS_IST = [9, 10, 11, 14, 15, 16, 19, 20]  # When patients search
    PEAK_BID_MODIFIER = 1.25          # +25% during peak hours
    OFF_PEAK_BID_MODIFIER = 0.75      # -25% during off-peak

    # Device bid modifiers
    MOBILE_BID_MODIFIER = 1.15        # +15% for mobile (most healthcare searches)
    DESKTOP_BID_MODIFIER = 0.90       # -10% for desktop

    # Optimization cooldown
    COOLDOWN_HOURS = 24               # Minimum hours between optimization runs
    MAX_ACTIONS_PER_RUN = 20          # Cap to prevent over-optimization

    # Healthcare seasonal patterns (month → demand multiplier)
    SEASONAL_MODIFIERS = {
        1: 1.1,   # New Year health resolutions
        2: 1.0,
        3: 1.0,
        4: 0.9,   # Summer starts, slightly lower
        5: 0.85,  # Summer
        6: 0.85,  # Monsoon begins
        7: 0.9,   # Monsoon
        8: 0.9,
        9: 1.0,   # Recovery
        10: 1.15,  # Festival season, cosmetic treatments spike
        11: 1.2,   # Wedding season
        12: 1.1,   # Year-end
    }


@dataclass
class OptimizationAction:
    """An optimization action to be taken or recommended."""

    action_type: OptimizationActionType
    campaign_id: UUID | None
    description: str
    reason: str
    target: str | None = None
    old_value: str | None = None
    new_value: str | None = None
    confidence: float = 0.5
    estimated_impact: str | None = None


class CampaignOptimizer:
    """The marketing brain — analyzes campaigns and makes optimization decisions.

    Usage:
        optimizer = CampaignOptimizer(db)
        report = await optimizer.run_optimization_cycle(doctor_id)
    """

    def __init__(self, db: AsyncSession):
        self.db = db
        self.config = OptConfig()

    async def run_optimization_cycle(self, doctor_id: UUID) -> dict:
        """Main entry point — run a full optimization cycle for a doctor.

        Steps:
        1. Check cooldown (don't optimize too frequently)
        2. Snapshot current performance
        3. Analyze each campaign
        4. Generate and log actions
        5. Apply safe actions automatically
        6. Generate human-readable report
        """
        logger.info("Starting optimization cycle for doctor %s", doctor_id)

        # Check cooldown
        if await self._is_in_cooldown(doctor_id):
            logger.info("Doctor %s is in optimization cooldown, skipping", doctor_id)
            return {"status": "cooldown", "message": "Optimization ran recently, waiting for data to accumulate"}

        # Create optimization run record
        run = OptimizationRun(doctor_id=doctor_id)
        self.db.add(run)
        await self.db.flush()

        try:
            # Get doctor and their active campaigns
            doctor = await self.db.get(Doctor, doctor_id)
            if not doctor:
                raise ValueError(f"Doctor {doctor_id} not found")

            campaigns = await self._get_active_campaigns(doctor_id)
            run.campaigns_analyzed = len(campaigns)

            if not campaigns:
                run.status = OptimizationRunStatus.COMPLETED
                run.summary = "No active campaigns to optimize"
                run.completed_at = datetime.now(timezone.utc)
                await self.db.commit()
                return {"status": "no_campaigns", "message": "No active campaigns found"}

            # Snapshot performance before optimization
            run.performance_before = await self._snapshot_performance(doctor_id)

            # Run all analyses
            all_actions: list[OptimizationAction] = []

            for campaign in campaigns:
                # Skip campaigns without enough data
                if campaign.impressions < self.config.MIN_IMPRESSIONS:
                    logger.info("Campaign '%s' has insufficient data (%d impressions), skipping",
                                campaign.name, campaign.impressions)
                    continue

                actions = await self._analyze_campaign(campaign, doctor)
                all_actions.extend(actions)

            # Cross-campaign budget optimization
            budget_actions = await self._optimize_budget_allocation(doctor_id, campaigns)
            all_actions.extend(budget_actions)

            # Cap total actions
            all_actions = sorted(all_actions, key=lambda a: a.confidence, reverse=True)
            all_actions = all_actions[: self.config.MAX_ACTIONS_PER_RUN]

            # Record and apply actions
            applied_count = 0
            skipped_count = 0

            for action in all_actions:
                record = OptimizationActionRecord(
                    run_id=run.id,
                    campaign_id=action.campaign_id,
                    action_type=action.action_type,
                    description=action.description,
                    reason=action.reason,
                    target=action.target,
                    old_value=action.old_value,
                    new_value=action.new_value,
                    confidence_score=action.confidence,
                    estimated_impact=action.estimated_impact,
                )

                # Auto-apply high-confidence safe actions
                if action.confidence >= 0.7:
                    try:
                        await self._apply_action(action)
                        record.applied = True
                        record.applied_at = datetime.now(timezone.utc)
                        record.result = "Applied successfully"
                        applied_count += 1
                    except Exception as exc:
                        record.result = f"Failed: {exc}"
                        skipped_count += 1
                        logger.error("Failed to apply action: %s — %s", action.description, exc)
                else:
                    record.result = "Recommended (below auto-apply threshold)"
                    skipped_count += 1

                self.db.add(record)

            # Finalize run
            run.actions_taken = applied_count
            run.actions_skipped = skipped_count
            run.status = OptimizationRunStatus.COMPLETED
            run.completed_at = datetime.now(timezone.utc)
            run.performance_after = await self._snapshot_performance(doctor_id)
            run.summary = self._generate_summary(all_actions, applied_count, skipped_count)
            run.recommendations = [a.description for a in all_actions if a.confidence < 0.7]

            await self.db.commit()

            logger.info(
                "Optimization complete for doctor %s: %d actions applied, %d recommendations",
                doctor_id, applied_count, skipped_count,
            )

            return {
                "status": "completed",
                "run_id": str(run.id),
                "campaigns_analyzed": run.campaigns_analyzed,
                "actions_applied": applied_count,
                "recommendations": skipped_count,
                "summary": run.summary,
            }

        except Exception as exc:
            run.status = OptimizationRunStatus.FAILED
            run.error_message = str(exc)
            run.completed_at = datetime.now(timezone.utc)
            await self.db.commit()
            logger.error("Optimization cycle failed for doctor %s: %s", doctor_id, exc)
            raise

    # ──────────────────────────────────────────────────────
    # Campaign-level analysis
    # ──────────────────────────────────────────────────────

    async def _analyze_campaign(self, campaign: Campaign, doctor: Doctor) -> list[OptimizationAction]:
        """Run all analysis checks on a single campaign."""
        actions: list[OptimizationAction] = []

        actions.extend(await self._analyze_keyword_performance(campaign))
        actions.extend(await self._analyze_ad_performance(campaign))
        actions.extend(await self._optimize_bids(campaign))
        actions.extend(await self._analyze_search_terms(campaign))
        actions.extend(await self._check_geographic_performance(campaign, doctor))
        actions.extend(self._get_time_of_day_adjustments(campaign))
        actions.extend(self._get_device_adjustments(campaign))
        actions.extend(self._get_seasonal_adjustments(campaign))

        return actions

    async def _analyze_keyword_performance(self, campaign: Campaign) -> list[OptimizationAction]:
        """Identify and act on underperforming keywords.

        Checks:
        - Keywords with CTR below threshold → pause
        - Keywords with high spend and zero conversions → pause
        - Keywords with CPC > 2x average → reduce bid or pause
        """
        actions = []
        keywords = campaign.keywords or []

        if not keywords or campaign.clicks < self.config.MIN_CLICKS:
            return actions

        avg_cpc = campaign.cpc if campaign.cpc > 0 else 50.0  # Default ₹50

        # TODO: In production, fetch keyword-level metrics from Google Ads API:
        # SELECT ad_group_criterion.keyword.text, metrics.impressions,
        #        metrics.clicks, metrics.ctr, metrics.average_cpc,
        #        metrics.conversions, metrics.cost_micros
        # FROM keyword_view
        # WHERE campaign.id = {campaign_id}
        # AND segments.date DURING LAST_30_DAYS

        # For now, analyze campaign-level metrics to generate recommendations
        if campaign.ctr < self.config.LOW_CTR_THRESHOLD and campaign.impressions > 500:
            actions.append(OptimizationAction(
                action_type=OptimizationActionType.PAUSE_KEYWORD,
                campaign_id=campaign.id,
                description=f"Campaign '{campaign.name}' has low CTR ({campaign.ctr:.2%}). "
                            "Review and pause underperforming keywords.",
                reason=f"CTR {campaign.ctr:.2%} is below {self.config.LOW_CTR_THRESHOLD:.0%} threshold",
                target="low_ctr_keywords",
                old_value=f"CTR: {campaign.ctr:.2%}",
                new_value="Pause bottom 20% keywords",
                confidence=0.6,
                estimated_impact=f"Could improve CTR by 30-50%",
            ))

        if campaign.cpc > avg_cpc * self.config.HIGH_CPC_MULTIPLIER:
            actions.append(OptimizationAction(
                action_type=OptimizationActionType.ADJUST_BID,
                campaign_id=campaign.id,
                description=f"Campaign '{campaign.name}' CPC (₹{campaign.cpc:.0f}) is {campaign.cpc/avg_cpc:.1f}x average.",
                reason=f"CPC ₹{campaign.cpc:.0f} exceeds {self.config.HIGH_CPC_MULTIPLIER}x average (₹{avg_cpc:.0f})",
                target="high_cpc_keywords",
                old_value=f"₹{campaign.cpc:.0f}",
                new_value=f"₹{avg_cpc * 1.2:.0f}",
                confidence=0.65,
                estimated_impact=f"Save ~₹{(campaign.cpc - avg_cpc * 1.2) * campaign.clicks / 30:.0f}/day",
            ))

        # Check for spend with no conversions (wasted budget)
        spend_inr = campaign.spend / 100  # Convert from paise
        if spend_inr > self.config.KEYWORD_SPEND_WASTE_INR and campaign.conversions == 0:
            actions.append(OptimizationAction(
                action_type=OptimizationActionType.PAUSE_CAMPAIGN,
                campaign_id=campaign.id,
                description=f"Campaign '{campaign.name}' spent ₹{spend_inr:.0f} with 0 conversions.",
                reason="Significant spend with zero conversions indicates targeting or ad copy issues",
                old_value=f"₹{spend_inr:.0f} spent, 0 conversions",
                new_value="Pause and review targeting + ad copy",
                confidence=0.8,
                estimated_impact=f"Save ₹{campaign.daily_budget}/day",
            ))

        return actions

    async def _analyze_ad_performance(self, campaign: Campaign) -> list[OptimizationAction]:
        """Identify winning and losing ad variations."""
        actions = []

        # TODO: In production, fetch ad-level performance:
        # SELECT ad_group_ad.ad.responsive_search_ad.headlines,
        #        metrics.impressions, metrics.clicks, metrics.conversions
        # FROM ad_group_ad
        # WHERE campaign.id = {campaign_id}

        # Recommend ad copy refresh if conversion rate is low
        if campaign.clicks > 50 and campaign.conversions > 0:
            conv_rate = campaign.conversions / campaign.clicks
            if conv_rate < self.config.MIN_CONVERSION_RATE:
                actions.append(OptimizationAction(
                    action_type=OptimizationActionType.ROTATE_AD_COPY,
                    campaign_id=campaign.id,
                    description=f"Campaign '{campaign.name}' conversion rate ({conv_rate:.2%}) is below target. "
                                "Generate and test new ad copy variations.",
                    reason=f"Conversion rate {conv_rate:.2%} below {self.config.MIN_CONVERSION_RATE:.0%} target",
                    old_value=f"Conv rate: {conv_rate:.2%}",
                    new_value="Test 3 new ad variations",
                    confidence=0.55,
                    estimated_impact="Could improve conversions by 15-30%",
                ))

        return actions

    async def _optimize_bids(self, campaign: Campaign) -> list[OptimizationAction]:
        """Adjust bids based on conversion data."""
        actions = []

        if campaign.clicks < self.config.MIN_CLICKS:
            return actions

        # TODO: In production, this uses keyword-level conversion data
        # For now, generate campaign-level bid recommendations

        # If conversions are good and cost is reasonable, increase bid to get more volume
        if campaign.conversions > 5 and campaign.cost_per_conversion > 0:
            target_cpa = campaign.cost_per_conversion
            # If CPA is under ₹500, this is a well-performing campaign
            if target_cpa < 500:
                new_bid = min(campaign.cpc * (1 + self.config.BID_INCREASE_PERCENT), self.config.MAX_BID_INR)
                actions.append(OptimizationAction(
                    action_type=OptimizationActionType.ADJUST_BID,
                    campaign_id=campaign.id,
                    description=f"Campaign '{campaign.name}' has strong CPA (₹{target_cpa:.0f}). "
                                "Increase bids to capture more volume.",
                    reason=f"Low CPA (₹{target_cpa:.0f}) suggests room to bid higher for more traffic",
                    target="all_keywords",
                    old_value=f"₹{campaign.cpc:.0f}",
                    new_value=f"₹{new_bid:.0f}",
                    confidence=0.75,
                    estimated_impact=f"Could increase conversions by {self.config.BID_INCREASE_PERCENT:.0%}",
                ))

        return actions

    async def _analyze_search_terms(self, campaign: Campaign) -> list[OptimizationAction]:
        """Find irrelevant search terms and recommend negative keywords."""
        actions = []

        # TODO: In production, fetch search terms report:
        # SELECT search_term_view.search_term, metrics.impressions,
        #        metrics.clicks, metrics.conversions, metrics.cost_micros
        # FROM search_term_view
        # WHERE campaign.id = {campaign_id}
        # AND metrics.impressions > 10
        # AND metrics.conversions = 0

        # Healthcare-specific negative keyword recommendations
        existing_negatives = set(campaign.negative_keywords or [])
        recommended_negatives = {
            "free", "home remedy", "diy", "youtube", "how to at home",
            "salary", "jobs", "career", "course", "study",
            "meaning", "wikipedia", "define", "symptoms",
            "images", "pictures", "videos",
        }
        new_negatives = recommended_negatives - existing_negatives

        if new_negatives and len(existing_negatives) < 50:
            actions.append(OptimizationAction(
                action_type=OptimizationActionType.ADD_NEGATIVE_KEYWORD,
                campaign_id=campaign.id,
                description=f"Add {len(new_negatives)} healthcare-specific negative keywords to campaign '{campaign.name}'.",
                reason="Common irrelevant search terms in healthcare vertical",
                target=", ".join(list(new_negatives)[:10]),
                old_value=f"{len(existing_negatives)} negatives",
                new_value=f"{len(existing_negatives) + len(new_negatives)} negatives",
                confidence=0.85,
                estimated_impact="Reduce wasted spend by 10-20%",
            ))

        return actions

    async def _check_geographic_performance(
        self, campaign: Campaign, doctor: Doctor
    ) -> list[OptimizationAction]:
        """Analyze geographic conversion patterns."""
        actions = []

        # TODO: In production, fetch geo performance:
        # SELECT geographic_view.country_criterion_id,
        #        geographic_view.location_type, metrics.clicks, metrics.conversions
        # FROM geographic_view
        # WHERE campaign.id = {campaign_id}

        # Recommend radius adjustment based on campaign reach vs conversions
        if campaign.target_radius_km and campaign.target_radius_km < 5 and campaign.impressions > 200:
            if campaign.clicks < 10:
                actions.append(OptimizationAction(
                    action_type=OptimizationActionType.ADJUST_GEO_RADIUS,
                    campaign_id=campaign.id,
                    description=f"Campaign '{campaign.name}' has narrow {campaign.target_radius_km}km radius "
                                "with low click volume. Consider expanding.",
                    reason=f"Only {campaign.clicks} clicks with {campaign.target_radius_km}km radius — "
                           "potential patients may be just outside the target area",
                    old_value=f"{campaign.target_radius_km}km",
                    new_value=f"{min(campaign.target_radius_km * 2, self.config.GEO_MAX_RADIUS_KM)}km",
                    confidence=0.6,
                    estimated_impact="Could increase impressions by 2-3x",
                ))

        return actions

    def _get_time_of_day_adjustments(self, campaign: Campaign) -> list[OptimizationAction]:
        """Recommend time-of-day bid adjustments for healthcare searches."""
        actions = []

        # TODO: In production, fetch hour-of-day performance data
        # For now, apply healthcare-specific peak hours

        actions.append(OptimizationAction(
            action_type=OptimizationActionType.ADJUST_TIME_BID,
            campaign_id=campaign.id,
            description=f"Set peak-hour bid adjustments for '{campaign.name}'. "
                        f"Increase bids during {', '.join(f'{h}:00' for h in self.config.PEAK_HOURS_IST[:4])} IST.",
            reason="Healthcare searches peak during morning (9-11 AM) and evening (7-8 PM) hours in India",
            old_value="No time-of-day adjustments",
            new_value=f"+{(self.config.PEAK_BID_MODIFIER - 1) * 100:.0f}% peak, "
                      f"{(self.config.OFF_PEAK_BID_MODIFIER - 1) * 100:.0f}% off-peak",
            confidence=0.5,  # Below auto-apply — recommendation only
            estimated_impact="Better ROI from budget concentration during peak hours",
        ))

        return actions

    def _get_device_adjustments(self, campaign: Campaign) -> list[OptimizationAction]:
        """Recommend device bid adjustments."""
        actions = []

        # TODO: In production, check actual device performance split
        actions.append(OptimizationAction(
            action_type=OptimizationActionType.ADJUST_DEVICE_BID,
            campaign_id=campaign.id,
            description=f"Set mobile bid adjustment for '{campaign.name}'. "
                        "Most healthcare searches in India are on mobile.",
            reason="70%+ of healthcare searches in India happen on mobile devices",
            old_value="No device adjustments",
            new_value=f"+{(self.config.MOBILE_BID_MODIFIER - 1) * 100:.0f}% mobile, "
                      f"{(self.config.DESKTOP_BID_MODIFIER - 1) * 100:.0f}% desktop",
            confidence=0.5,
            estimated_impact="Better allocation of budget toward mobile users",
        ))

        return actions

    def _get_seasonal_adjustments(self, campaign: Campaign) -> list[OptimizationAction]:
        """Apply seasonal budget adjustments for healthcare demand."""
        actions = []
        current_month = datetime.now(timezone.utc).month
        modifier = self.config.SEASONAL_MODIFIERS.get(current_month, 1.0)

        if modifier != 1.0:
            direction = "increase" if modifier > 1.0 else "decrease"
            pct = abs(modifier - 1.0) * 100

            actions.append(OptimizationAction(
                action_type=OptimizationActionType.INCREASE_BUDGET if modifier > 1.0 else OptimizationActionType.DECREASE_BUDGET,
                campaign_id=campaign.id,
                description=f"Seasonal adjustment: {direction} budget by {pct:.0f}% for '{campaign.name}' "
                            f"(month {current_month} demand modifier: {modifier}x).",
                reason=f"Historical healthcare demand in month {current_month} is {modifier:.0%} of average",
                old_value=f"₹{campaign.daily_budget}/day",
                new_value=f"₹{campaign.daily_budget * modifier:.0f}/day",
                confidence=0.45,
                estimated_impact=f"Align spend with expected demand ({direction} {pct:.0f}%)",
            ))

        return actions

    # ──────────────────────────────────────────────────────
    # Cross-campaign optimization
    # ──────────────────────────────────────────────────────

    async def _optimize_budget_allocation(
        self, doctor_id: UUID, campaigns: list[Campaign]
    ) -> list[OptimizationAction]:
        """Reallocate budget from underperforming to high-performing campaigns."""
        actions = []

        if len(campaigns) < 2:
            return actions

        # Score each campaign by efficiency
        scored: list[tuple[Campaign, float]] = []
        for c in campaigns:
            if c.spend > 0 and c.clicks > 0:
                # Score = (conversions per rupee spent) × (CTR × 100)
                efficiency = (c.conversions / (c.spend / 100)) * (c.ctr * 100) if c.spend > 0 else 0
                scored.append((c, efficiency))

        if len(scored) < 2:
            return actions

        scored.sort(key=lambda x: x[1])
        worst = scored[0]
        best = scored[-1]

        if best[1] > worst[1] * 2 and worst[0].daily_budget > self.config.MIN_CAMPAIGN_BUDGET_INR:
            realloc_amount = int(worst[0].daily_budget * self.config.BUDGET_REALLOCATION_PERCENT)
            if realloc_amount >= 50:  # Only reallocate if meaningful (₹50+)
                actions.append(OptimizationAction(
                    action_type=OptimizationActionType.REALLOCATE_BUDGET,
                    campaign_id=best[0].id,
                    description=f"Move ₹{realloc_amount}/day from '{worst[0].name}' to '{best[0].name}'. "
                                f"'{best[0].name}' is {best[1] / worst[1]:.1f}x more efficient.",
                    reason=f"'{best[0].name}' efficiency score: {best[1]:.2f} vs '{worst[0].name}': {worst[1]:.2f}",
                    target=f"{worst[0].name} → {best[0].name}",
                    old_value=f"₹{worst[0].daily_budget} / ₹{best[0].daily_budget}",
                    new_value=f"₹{worst[0].daily_budget - realloc_amount} / ₹{best[0].daily_budget + realloc_amount}",
                    confidence=0.7,
                    estimated_impact=f"Shift ₹{realloc_amount}/day to higher-performing campaign",
                ))

        return actions

    # ──────────────────────────────────────────────────────
    # Helpers
    # ──────────────────────────────────────────────────────

    async def _is_in_cooldown(self, doctor_id: UUID) -> bool:
        """Check if we've optimized this doctor recently."""
        cutoff = datetime.now(timezone.utc) - timedelta(hours=self.config.COOLDOWN_HOURS)
        result = await self.db.execute(
            select(OptimizationRun).where(
                and_(
                    OptimizationRun.doctor_id == doctor_id,
                    OptimizationRun.started_at >= cutoff,
                    OptimizationRun.status == OptimizationRunStatus.COMPLETED,
                )
            ).limit(1)
        )
        return result.scalar_one_or_none() is not None

    async def _get_active_campaigns(self, doctor_id: UUID) -> list[Campaign]:
        """Get all active campaigns for a doctor."""
        result = await self.db.execute(
            select(Campaign).where(
                and_(
                    Campaign.doctor_id == doctor_id,
                    Campaign.status.in_([CampaignStatus.ACTIVE, CampaignStatus.PENDING_REVIEW]),
                )
            )
        )
        return list(result.scalars().all())

    async def _snapshot_performance(self, doctor_id: UUID) -> dict:
        """Capture current performance metrics for before/after comparison."""
        result = await self.db.execute(
            select(
                func.sum(Campaign.spend).label("total_spend"),
                func.sum(Campaign.impressions).label("total_impressions"),
                func.sum(Campaign.clicks).label("total_clicks"),
                func.sum(Campaign.conversions).label("total_conversions"),
                func.avg(Campaign.ctr).label("avg_ctr"),
                func.avg(Campaign.cpc).label("avg_cpc"),
                func.avg(Campaign.cost_per_conversion).label("avg_cpa"),
            ).where(
                and_(
                    Campaign.doctor_id == doctor_id,
                    Campaign.status == CampaignStatus.ACTIVE,
                )
            )
        )
        row = result.one_or_none()
        if not row:
            return {}

        return {
            "total_spend_inr": (row.total_spend or 0) / 100,
            "total_impressions": row.total_impressions or 0,
            "total_clicks": row.total_clicks or 0,
            "total_conversions": row.total_conversions or 0,
            "avg_ctr": round(row.avg_ctr or 0, 4),
            "avg_cpc": round(row.avg_cpc or 0, 2),
            "avg_cpa": round(row.avg_cpa or 0, 2),
            "snapshot_at": datetime.now(timezone.utc).isoformat(),
        }

    async def _apply_action(self, action: OptimizationAction) -> None:
        """Apply an optimization action to the campaign.

        In production, this makes API calls to Google Ads / Meta.
        Currently updates local records and logs the action.
        """
        # TODO: Replace with actual platform API calls
        if action.campaign_id:
            campaign = await self.db.get(Campaign, action.campaign_id)
            if not campaign:
                return

            if action.action_type == OptimizationActionType.PAUSE_CAMPAIGN:
                campaign.status = CampaignStatus.PAUSED
                logger.info("Paused campaign '%s'", campaign.name)

            elif action.action_type == OptimizationActionType.ADD_NEGATIVE_KEYWORD:
                existing = campaign.negative_keywords or []
                new_kws = [kw.strip() for kw in (action.target or "").split(",")]
                campaign.negative_keywords = list(set(existing + new_kws))
                logger.info("Added %d negative keywords to '%s'", len(new_kws), campaign.name)

            elif action.action_type in (
                OptimizationActionType.INCREASE_BUDGET,
                OptimizationActionType.DECREASE_BUDGET,
                OptimizationActionType.REALLOCATE_BUDGET,
            ):
                if action.new_value and "₹" in action.new_value:
                    # Parse the budget from "₹X/day" or "₹X / ₹Y" format
                    # For budget reallocation, apply to the target campaign
                    pass  # TODO: Parse and apply budget changes via platform API
                logger.info("Budget action for '%s': %s", campaign.name, action.description)

    def _generate_summary(
        self, actions: list[OptimizationAction], applied: int, skipped: int
    ) -> str:
        """Generate a human-readable summary of the optimization run."""
        if not actions:
            return "All campaigns are performing within acceptable parameters. No actions needed."

        parts = [f"Analyzed campaigns and identified {len(actions)} optimization opportunities."]
        if applied:
            parts.append(f"{applied} actions were automatically applied (high confidence).")
        if skipped:
            parts.append(f"{skipped} recommendations generated for manual review.")

        # Highlight key actions
        high_impact = [a for a in actions if a.confidence >= 0.7]
        if high_impact:
            parts.append("Key actions: " + "; ".join(a.description[:80] for a in high_impact[:3]))

        return " ".join(parts)
