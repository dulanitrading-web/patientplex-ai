"""
Orchestration Brain — The master coordinator that runs all platform brains.

This is the CEO of the marketing department. It:
1. Decides how to split budget between Google and Meta
2. Coordinates campaign launches across platforms
3. Monitors cross-platform performance
4. Shifts budget from underperforming platform to the winner
5. Ensures the whole system works toward one goal: appointments

KEY PRINCIPLE:
Google Ads = captures existing demand (patients searching)
Meta Ads = creates new demand (patients who don't know they need treatment)

For clinics with small budgets: Google first (higher intent, faster ROI)
For clinics with larger budgets: Google + Meta (capture + create demand)
"""

import logging
from uuid import UUID

from sqlalchemy.ext.asyncio import AsyncSession

from app.services.brains.google_ads_brain import GoogleAdsBrain
from app.services.brains.meta_ads_brain import MetaAdsBrain
from app.services.keyword_intelligence import keyword_intelligence

logger = logging.getLogger(__name__)


# Budget split rules based on monthly budget
BUDGET_SPLIT_RULES = {
    "micro": {
        "range_inr": (0, 10000),
        "google_pct": 1.0,
        "meta_pct": 0.0,
        "reason": "Below ₹10K/month — Google only. Higher intent, faster results.",
    },
    "small": {
        "range_inr": (10000, 30000),
        "google_pct": 0.80,
        "meta_pct": 0.20,
        "reason": "₹10-30K/month — 80% Google (high intent), 20% Meta (awareness).",
    },
    "medium": {
        "range_inr": (30000, 75000),
        "google_pct": 0.65,
        "meta_pct": 0.35,
        "reason": "₹30-75K/month — Balanced. Google captures demand, Meta creates it.",
    },
    "large": {
        "range_inr": (75000, 200000),
        "google_pct": 0.55,
        "meta_pct": 0.45,
        "reason": "₹75K-2L/month — Near equal split. Both channels at scale.",
    },
    "enterprise": {
        "range_inr": (200000, float("inf")),
        "google_pct": 0.50,
        "meta_pct": 0.50,
        "reason": "₹2L+/month — Full funnel on both platforms.",
    },
}


class OrchestrationBrain:
    """The master brain that coordinates all platform-specific brains.

    Usage:
        brain = OrchestrationBrain(db)
        plan = await brain.create_full_marketing_plan(doctor_id)
    """

    def __init__(self, db: AsyncSession):
        self.db = db
        self.google_brain = GoogleAdsBrain()
        self.meta_brain = MetaAdsBrain()

    async def create_full_marketing_plan(self, doctor_id: UUID) -> dict:
        """Create a complete marketing plan across all platforms.

        This is what a marketing director presents to the clinic owner:
        1. Here's your budget and how we'll split it
        2. Here's what campaigns we'll run on Google
        3. Here's what campaigns we'll run on Meta
        4. Here's the expected results
        5. Here's the timeline
        """
        from app.models.doctor import Doctor

        doctor = await self.db.get(Doctor, doctor_id)
        if not doctor:
            return {"error": "Doctor not found"}

        monthly_budget = doctor.monthly_budget or 0
        city = doctor.city or ""
        specialty = doctor.specialty or "DENTIST"
        clinic_name = doctor.clinic_name or ""
        services = doctor.services or []

        # 1. Determine platform budget split
        split = self._get_budget_split(monthly_budget)

        google_monthly = round(monthly_budget * split["google_pct"])
        meta_monthly = round(monthly_budget * split["meta_pct"])

        # 2. Get market intelligence
        market_data = keyword_intelligence.get_market_data(city, specialty)

        # 3. Get Google Ads recommendations
        google_plan = self.google_brain.recommend_campaign_structure(
            specialty=specialty,
            city=city,
            clinic_name=clinic_name,
            services=services,
            monthly_budget=google_monthly,
        )

        # 4. Get Meta Ads recommendations
        meta_plan = self.meta_brain.recommend_campaign_structure(
            specialty=specialty,
            city=city,
            clinic_name=clinic_name,
            services=services,
            monthly_budget=meta_monthly,
        )

        # 5. Get bid strategy recommendation
        # For now, assume new account (will check real data later)
        bid_strategy = self.google_brain.get_bid_strategy_recommendation(
            total_clicks_30d=0,
            total_conversions_30d=0,
            account_age_days=0,
        )

        # 6. Estimate results
        estimates = self._estimate_results(
            google_monthly, meta_monthly, market_data, specialty
        )

        return {
            "doctor_id": str(doctor_id),
            "clinic_name": clinic_name,
            "city": city,
            "specialty": specialty,
            "monthly_budget": monthly_budget,
            "budget_split": {
                "google_ads": {
                    "monthly_inr": google_monthly,
                    "daily_inr": round(google_monthly / 30.4),
                    "percentage": split["google_pct"] * 100,
                },
                "meta_ads": {
                    "monthly_inr": meta_monthly,
                    "daily_inr": round(meta_monthly / 30.4),
                    "percentage": split["meta_pct"] * 100,
                },
                "rationale": split["reason"],
            },
            "market_intelligence": market_data,
            "google_ads_plan": {
                "campaigns": google_plan,
                "bid_strategy": bid_strategy,
                "hourly_modifiers": self.google_brain.get_hourly_bid_modifiers(),
            },
            "meta_ads_plan": meta_plan,
            "estimated_results": estimates,
            "execution_timeline": {
                "week_1": "Set up Google Ads campaigns (highest intent, fastest results)",
                "week_2": "Launch Meta awareness + retargeting campaigns",
                "week_3": "Analyze first results, adjust keywords and audiences",
                "week_4": "Optimize bids, expand winning campaigns, pause losers",
                "month_2": "Scale winning campaigns, test new treatments, add lookalikes",
                "month_3": "Switch to tCPA bidding (if enough conversions), full funnel live",
            },
        }

    def _get_budget_split(self, monthly_budget: float) -> dict:
        """Determine Google vs Meta budget split based on total budget."""
        for tier, config in BUDGET_SPLIT_RULES.items():
            low, high = config["range_inr"]
            if low <= monthly_budget < high:
                return {
                    "tier": tier,
                    "google_pct": config["google_pct"],
                    "meta_pct": config["meta_pct"],
                    "reason": config["reason"],
                }
        return BUDGET_SPLIT_RULES["medium"]

    def _estimate_results(
        self,
        google_monthly: float,
        meta_monthly: float,
        market_data: dict,
        specialty: str,
    ) -> dict:
        """Estimate monthly results from the marketing plan.

        Uses real CPC data and industry conversion rates.
        Conservative estimates — better to under-promise and over-deliver.
        """
        # Google estimates (search = high intent)
        google_cpc = market_data.get("avg_cpc_inr", 30) or 30
        google_clicks = round(google_monthly / max(google_cpc, 1))
        google_ctr = 0.05  # 5% average for healthcare
        google_conv_rate = 0.05  # 5% click-to-appointment for search

        # Meta estimates (discovery = lower intent but larger reach)
        meta_cpm = 150  # Average CPM in INR for healthcare
        meta_reach = round((meta_monthly / meta_cpm) * 1000)
        meta_ctr = 0.015  # 1.5% CTR for healthcare Meta ads
        meta_clicks = round(meta_reach * meta_ctr)
        meta_conv_rate = 0.02  # 2% click-to-appointment for Meta

        google_appointments = round(google_clicks * google_conv_rate)
        meta_appointments = round(meta_clicks * meta_conv_rate)
        total_appointments = google_appointments + meta_appointments

        total_spend = google_monthly + meta_monthly
        cost_per_appointment = (
            round(total_spend / total_appointments) if total_appointments > 0 else None
        )

        return {
            "google_ads": {
                "estimated_clicks": google_clicks,
                "estimated_appointments": google_appointments,
                "estimated_cpc": google_cpc,
                "conversion_rate_assumed": f"{google_conv_rate*100}%",
            },
            "meta_ads": {
                "estimated_reach": meta_reach,
                "estimated_clicks": meta_clicks,
                "estimated_appointments": meta_appointments,
                "conversion_rate_assumed": f"{meta_conv_rate*100}%",
            },
            "total": {
                "estimated_appointments": total_appointments,
                "estimated_cost_per_appointment": cost_per_appointment,
                "total_spend": total_spend,
                "note": "Conservative estimates. Actual results depend on landing page quality, ad copy, and conversion tracking setup.",
            },
        }
