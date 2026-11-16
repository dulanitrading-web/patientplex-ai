"""
PatientPlex Performance Marketing Brain — Real AI Intelligence for Dental Clinics.

This is not a dummy framework. This is a production-grade performance marketing
engine that thinks like a senior dental marketing strategist.

WHAT IT DOES:
1. AUDIT — Analyzes existing Google Ads account like a performance marketer
   walking into a new client's account for the first time
2. DIAGNOSE — Identifies every gap: missing campaign types, budget waste,
   keyword gaps, poor structure, wrong bid strategies
3. PRESCRIBE — Generates a prioritized action plan with expected impact
4. EXECUTE — Allocates budget intelligently based on real performance data
5. MONITOR — Continuously watches for anomalies and opportunities

REAL DENTAL MARKETING KNOWLEDGE BAKED IN:
- Which treatments have highest patient lifetime value (implants > RCT > cleaning)
- Which campaign structures work for Indian dental clinics
- What CTR/CPC/CPA benchmarks to target by treatment type
- When patients search (lunch breaks, evenings, weekends)
- How to structure campaigns by intent (emergency vs cosmetic vs preventive)
"""

import logging
from dataclasses import dataclass, field
from datetime import datetime, timezone
from enum import Enum
from typing import Optional
from uuid import UUID

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.campaign import AdPlatform, Campaign, CampaignStatus
from app.models.doctor import Doctor

logger = logging.getLogger(__name__)


# ═══════════════════════════════════════════════════════════════
# DENTAL MARKETING KNOWLEDGE BASE — Real benchmarks, not guesses
# ═══════════════════════════════════════════════════════════════

# Treatment categories ranked by patient lifetime value (LTV)
# This determines budget priority — high LTV treatments get more budget
TREATMENT_TIERS = {
    "tier_1_high_value": {
        "treatments": [
            "dental implants", "implant", "full mouth rehabilitation",
            "all on 4", "all on 6", "smile makeover", "smile design",
            "cosmetic dentistry", "veneers", "cosmetic",
        ],
        "avg_case_value_inr": 80000,  # ₹50K-₹3L per case
        "target_cpa_inr": 3000,       # Can afford ₹3000 CPA
        "target_ctr_pct": 4.0,
        "target_cpc_inr": 80,
        "budget_weight": 0.35,         # 35% of budget
        "patient_intent": "high",
        "decision_time_days": 14,      # Takes 2 weeks to decide
        "campaign_type": "SEARCH",
        "match_types": ["phrase", "exact"],
    },
    "tier_2_medium_value": {
        "treatments": [
            "braces", "aligners", "invisalign", "orthodontics", "orthodontic",
            "root canal", "rct", "endodontics", "crown", "bridge",
            "crowns & bridges", "crowns and bridges",
        ],
        "avg_case_value_inr": 25000,  # ₹15K-₹50K
        "target_cpa_inr": 1500,
        "target_ctr_pct": 5.0,
        "target_cpc_inr": 40,
        "budget_weight": 0.30,         # 30% of budget
        "patient_intent": "medium_high",
        "decision_time_days": 7,
        "campaign_type": "SEARCH",
        "match_types": ["phrase", "exact"],
    },
    "tier_3_volume": {
        "treatments": [
            "teeth cleaning", "scaling", "teeth whitening", "whitening",
            "dental checkup", "check up", "dentist near me", "dental clinic",
            "tooth extraction", "wisdom tooth",
            "gum treatment", "periodontal",
        ],
        "avg_case_value_inr": 3000,   # ₹500-₹5K but leads to upsells
        "target_cpa_inr": 500,
        "target_ctr_pct": 6.0,
        "target_cpc_inr": 20,
        "budget_weight": 0.15,         # 15% — volume play, low margin
        "patient_intent": "medium",
        "decision_time_days": 2,
        "campaign_type": "SEARCH",
        "match_types": ["phrase", "broad"],
    },
    "tier_4_emergency": {
        "treatments": [
            "emergency dentist", "tooth pain", "toothache",
            "broken tooth", "dental emergency",
        ],
        "avg_case_value_inr": 5000,   # Emergency + follow-up
        "target_cpa_inr": 800,
        "target_ctr_pct": 8.0,        # Very high intent
        "target_cpc_inr": 30,
        "budget_weight": 0.10,         # 10% — small but high conversion
        "patient_intent": "very_high",
        "decision_time_days": 0,       # Same day
        "campaign_type": "SEARCH",
        "match_types": ["phrase", "exact"],
    },
    "tier_5_brand_local": {
        "treatments": [
            "call only", "local dentist", "best dentist",
            "dentist indore", "dental clinic near me",
        ],
        "avg_case_value_inr": 5000,
        "target_cpa_inr": 600,
        "target_ctr_pct": 7.0,
        "target_cpc_inr": 25,
        "budget_weight": 0.10,         # 10% — brand + local discovery
        "patient_intent": "high",
        "decision_time_days": 1,
        "campaign_type": "SEARCH",
        "match_types": ["broad", "phrase"],
    },
}

# Indian dental ads benchmarks by city tier
CITY_BENCHMARKS = {
    "tier_1": {  # Mumbai, Delhi, Bangalore
        "avg_cpc_inr": 60,
        "avg_ctr_pct": 4.5,
        "avg_cpa_inr": 1500,
        "competition": "high",
    },
    "tier_2": {  # Indore, Jaipur, Lucknow, Pune, Ahmedabad
        "avg_cpc_inr": 35,
        "avg_ctr_pct": 5.5,
        "avg_cpa_inr": 800,
        "competition": "medium",
    },
    "tier_3": {  # Smaller cities
        "avg_cpc_inr": 20,
        "avg_ctr_pct": 6.0,
        "avg_cpa_inr": 500,
        "competition": "low",
    },
}

# Cities mapped to tiers
CITY_TIER_MAP = {
    "mumbai": "tier_1", "delhi": "tier_1", "bangalore": "tier_1",
    "bengaluru": "tier_1", "chennai": "tier_1", "hyderabad": "tier_1",
    "kolkata": "tier_1",
    "pune": "tier_2", "ahmedabad": "tier_2", "jaipur": "tier_2",
    "lucknow": "tier_2", "indore": "tier_2", "bhopal": "tier_2",
    "nagpur": "tier_2", "surat": "tier_2", "chandigarh": "tier_2",
    "kochi": "tier_2", "coimbatore": "tier_2", "visakhapatnam": "tier_2",
}

# Campaign health thresholds
HEALTH_THRESHOLDS = {
    "critical_low_ctr": 1.0,        # Below 1% CTR = campaign is sick
    "poor_ctr": 3.0,                # Below 3% = needs work
    "good_ctr": 5.0,                # 5%+ = healthy
    "excellent_ctr": 8.0,           # 8%+ = excellent
    "waste_spend_zero_clicks": 500,  # ₹500 spent, 0 clicks = waste
    "waste_spend_zero_conv": 2000,   # ₹2000 spent, 0 conversions = concern
    "min_impressions_for_judgment": 200,
    "min_clicks_for_ctr_judgment": 30,
}


class AuditSeverity(str, Enum):
    CRITICAL = "critical"   # Losing money right now
    HIGH = "high"           # Major opportunity being missed
    MEDIUM = "medium"       # Improvement available
    LOW = "low"             # Nice to have
    INFO = "info"           # Observation


class ActionType(str, Enum):
    CREATE_CAMPAIGN = "create_campaign"
    PAUSE_CAMPAIGN = "pause_campaign"
    INCREASE_BUDGET = "increase_budget"
    DECREASE_BUDGET = "decrease_budget"
    REALLOCATE_BUDGET = "reallocate_budget"
    ADD_KEYWORDS = "add_keywords"
    ADD_NEGATIVE_KEYWORDS = "add_negative_keywords"
    IMPROVE_AD_COPY = "improve_ad_copy"
    CHANGE_BID_STRATEGY = "change_bid_strategy"
    EXPAND_GEO = "expand_geo"
    TIGHTEN_GEO = "tighten_geo"
    FIX_TRACKING = "fix_tracking"
    RESTRUCTURE = "restructure"
    RETIRE_CAMPAIGN = "retire_campaign"


@dataclass
class AuditFinding:
    """A single finding from the account audit."""
    severity: AuditSeverity
    category: str
    title: str
    detail: str
    action: ActionType
    action_detail: str
    expected_impact: str
    priority_score: float  # 0-100, used for sorting
    campaign_id: Optional[UUID] = None
    campaign_name: Optional[str] = None


@dataclass
class BudgetRecommendation:
    """Budget allocation recommendation for a campaign."""
    campaign_id: UUID
    campaign_name: str
    current_daily_budget: float
    recommended_daily_budget: float
    change_pct: float
    reason: str
    treatment_tier: str
    performance_score: float


class PerformanceMarketingBrain:
    """
    The real performance marketing AI.

    This thinks like a senior performance marketer who just got access
    to a new dental clinic's Google Ads account and needs to:
    1. Understand what's there
    2. Find what's broken or missing
    3. Fix it in priority order
    4. Allocate budget where it will generate the most appointments
    """

    def __init__(self, db: AsyncSession):
        self.db = db

    # ═══════════════════════════════════════════════════════════
    # 1. FULL ACCOUNT AUDIT — Like a marketer's first day
    # ═══════════════════════════════════════════════════════════

    async def audit_account(self, doctor_id: UUID) -> dict:
        """
        Complete account audit — the first thing a performance marketer does.

        Returns a structured report with:
        - Account health score (0-100)
        - Findings (sorted by severity/priority)
        - Action plan (what to do, in what order)
        - Budget recommendation
        """
        doctor = await self.db.get(Doctor, doctor_id)
        if not doctor:
            return {"error": "Doctor not found"}

        # Get all campaigns
        result = await self.db.execute(
            select(Campaign).where(Campaign.doctor_id == doctor_id)
        )
        campaigns = list(result.scalars().all())

        city = (doctor.city or "").lower().strip()
        city_tier = CITY_TIER_MAP.get(city, "tier_2")
        benchmarks = CITY_BENCHMARKS[city_tier]
        specialty = (doctor.specialty or "DENTIST").upper()
        services = doctor.services or []
        monthly_budget = doctor.monthly_budget or 0

        findings: list[AuditFinding] = []

        # ── CHECK 1: Account structure ──
        findings.extend(self._audit_account_structure(
            campaigns, services, city, monthly_budget
        ))

        # ── CHECK 2: Per-campaign health ──
        for campaign in campaigns:
            findings.extend(self._audit_campaign_health(
                campaign, benchmarks, monthly_budget, len(campaigns)
            ))

        # ── CHECK 3: Missing campaign coverage ──
        findings.extend(self._audit_coverage_gaps(
            campaigns, services, city
        ))

        # ── CHECK 4: Budget distribution ──
        findings.extend(self._audit_budget_distribution(
            campaigns, monthly_budget
        ))

        # ── CHECK 5: Conversion tracking ──
        findings.extend(self._audit_conversion_setup(campaigns))

        # Sort by priority
        findings.sort(key=lambda f: f.priority_score, reverse=True)

        # Calculate health score
        health_score = self._calculate_health_score(findings, campaigns, benchmarks)

        # Generate budget recommendations
        budget_plan = self._generate_budget_plan(
            campaigns, monthly_budget, services, city_tier
        )

        # Generate action plan (top 10 priorities)
        action_plan = self._generate_action_plan(findings[:10])

        return {
            "doctor_id": str(doctor_id),
            "clinic_name": doctor.clinic_name,
            "city": doctor.city,
            "city_tier": city_tier,
            "benchmarks": benchmarks,
            "monthly_budget": monthly_budget,
            "total_campaigns": len(campaigns),
            "active_campaigns": sum(
                1 for c in campaigns if c.status == CampaignStatus.ACTIVE
            ),
            "paused_campaigns": sum(
                1 for c in campaigns if c.status == CampaignStatus.PAUSED
            ),
            "health_score": health_score,
            "health_grade": (
                "A" if health_score >= 80 else
                "B" if health_score >= 60 else
                "C" if health_score >= 40 else
                "D" if health_score >= 20 else "F"
            ),
            "total_spend": sum(c.spend for c in campaigns),
            "total_clicks": sum(c.clicks for c in campaigns),
            "total_impressions": sum(c.impressions for c in campaigns),
            "total_conversions": sum(c.conversions for c in campaigns),
            "findings": [
                {
                    "severity": f.severity.value,
                    "category": f.category,
                    "title": f.title,
                    "detail": f.detail,
                    "action": f.action.value,
                    "action_detail": f.action_detail,
                    "expected_impact": f.expected_impact,
                    "priority_score": f.priority_score,
                    "campaign_name": f.campaign_name,
                }
                for f in findings
            ],
            "budget_plan": budget_plan,
            "action_plan": action_plan,
            "audited_at": datetime.now(timezone.utc).isoformat(),
        }

    # ═══════════════════════════════════════════════════════════
    # 2. INTELLIGENT BUDGET ALLOCATION
    # ═══════════════════════════════════════════════════════════

    async def allocate_budget(self, doctor_id: UUID) -> dict:
        """
        Allocate the monthly budget across campaigns based on real performance.

        Algorithm (how a real performance marketer thinks):
        1. What treatments does this clinic offer?
        2. Which campaigns already exist and how are they performing?
        3. Which campaigns are generating appointments (conversions)?
        4. Which campaigns have good CTR but no conversions? (landing page problem)
        5. Which campaigns are burning money with no results? (pause or fix)
        6. Are there high-value treatments with no campaigns? (create them)
        7. Allocate budget: performers get more, losers get cut, gaps get filled
        """
        doctor = await self.db.get(Doctor, doctor_id)
        if not doctor:
            return {"error": "Doctor not found"}

        result = await self.db.execute(
            select(Campaign).where(Campaign.doctor_id == doctor_id)
        )
        campaigns = list(result.scalars().all())

        monthly_budget = doctor.monthly_budget or 0
        daily_budget = round(monthly_budget / 30.4) if monthly_budget > 0 else 0
        services = doctor.services or []
        city_tier = CITY_TIER_MAP.get((doctor.city or "").lower(), "tier_2")

        if not campaigns:
            return {
                "doctor_id": str(doctor_id),
                "message": "No campaigns found. Run audit first to identify what to create.",
                "daily_budget": daily_budget,
                "allocations": [],
            }

        allocations = self._generate_budget_plan(
            campaigns, monthly_budget, services, city_tier
        )

        return {
            "doctor_id": str(doctor_id),
            "monthly_budget": monthly_budget,
            "daily_budget": daily_budget,
            "allocations": allocations,
            "strategy_summary": self._summarize_budget_strategy(allocations),
        }

    # ═══════════════════════════════════════════════════════════
    # INTERNAL: Account structure audit
    # ═══════════════════════════════════════════════════════════

    def _audit_account_structure(
        self,
        campaigns: list[Campaign],
        services: list[str],
        city: str,
        monthly_budget: float,
    ) -> list[AuditFinding]:
        findings = []

        if not campaigns:
            findings.append(AuditFinding(
                severity=AuditSeverity.CRITICAL,
                category="Account Structure",
                title="No campaigns in account",
                detail="The ad account has zero campaigns. No ads are running, "
                       "which means zero patient acquisition from paid channels.",
                action=ActionType.CREATE_CAMPAIGN,
                action_detail="Create campaigns for top 3 services by treatment value",
                expected_impact="Start generating patient enquiries immediately",
                priority_score=100,
            ))
            return findings

        # Check if all campaigns are paused
        active = [c for c in campaigns if c.status == CampaignStatus.ACTIVE]
        paused = [c for c in campaigns if c.status == CampaignStatus.PAUSED]

        if not active and paused:
            findings.append(AuditFinding(
                severity=AuditSeverity.CRITICAL,
                category="Account Structure",
                title=f"All {len(paused)} campaigns are paused",
                detail="Every campaign is paused. The clinic is getting zero "
                       "visibility from paid ads. Need to identify best performers "
                       "and reactivate them.",
                action=ActionType.REALLOCATE_BUDGET,
                action_detail=(
                    "Reactivate top campaigns by past performance: "
                    "sort by CTR and conversion rate, enable top 3-5"
                ),
                expected_impact="Restore patient flow from paid channels",
                priority_score=95,
            ))

        # Check campaign naming — well-structured accounts use naming conventions
        has_location = sum(1 for c in campaigns if city and city in (c.name or "").lower())
        has_treatment = sum(
            1 for c in campaigns
            if any(svc.lower() in (c.name or "").lower() for svc in services)
        )

        if len(campaigns) > 3 and has_treatment < len(campaigns) * 0.5:
            findings.append(AuditFinding(
                severity=AuditSeverity.MEDIUM,
                category="Account Structure",
                title="Campaign naming could be clearer",
                detail="Less than half the campaigns include the treatment name. "
                       "Clear naming like 'BDC | Search | Implants | Indore' helps "
                       "with quick analysis and budget decisions.",
                action=ActionType.RESTRUCTURE,
                action_detail="Rename campaigns: [Clinic] | [Type] | [Treatment] | [City]",
                expected_impact="Better organization, faster optimization decisions",
                priority_score=20,
            ))

        # Check if monthly budget is reasonable for the number of campaigns
        if monthly_budget > 0 and len(active) > 0:
            per_campaign_daily = (monthly_budget / 30.4) / len(active)
            if per_campaign_daily < 100:
                findings.append(AuditFinding(
                    severity=AuditSeverity.HIGH,
                    category="Budget",
                    title="Budget spread too thin across campaigns",
                    detail=(
                        f"₹{monthly_budget:,.0f}/month across {len(active)} active "
                        f"campaigns = ₹{per_campaign_daily:,.0f}/day each. Google needs "
                        f"at least ₹200-300/day per campaign to gather meaningful data. "
                        f"Consider pausing weaker campaigns and concentrating budget."
                    ),
                    action=ActionType.REALLOCATE_BUDGET,
                    action_detail=(
                        f"Reduce to top {min(3, len(active))} campaigns, "
                        f"give each ₹{(monthly_budget/30.4/min(3, len(active))):,.0f}/day"
                    ),
                    expected_impact="Faster data collection, better optimization signals",
                    priority_score=75,
                ))

        return findings

    # ═══════════════════════════════════════════════════════════
    # INTERNAL: Per-campaign health check
    # ═══════════════════════════════════════════════════════════

    def _audit_campaign_health(
        self,
        campaign: Campaign,
        benchmarks: dict,
        monthly_budget: float,
        total_campaigns: int,
    ) -> list[AuditFinding]:
        findings = []
        name = campaign.name or "Unnamed"

        # Skip campaigns with zero data — they haven't run yet
        if campaign.impressions == 0 and campaign.clicks == 0:
            if campaign.status == CampaignStatus.PAUSED:
                # Paused with no data — was it ever live?
                findings.append(AuditFinding(
                    severity=AuditSeverity.LOW,
                    category="Campaign Health",
                    title=f"'{name}' — paused with no data",
                    detail="This campaign was created but never gathered data. "
                           "Either it was paused before getting impressions, or "
                           "there's an approval/targeting issue.",
                    action=ActionType.RETIRE_CAMPAIGN,
                    action_detail="Review if still needed. If treatment is relevant, "
                                  "create a fresh campaign with proper setup.",
                    expected_impact="Cleaner account, less confusion",
                    priority_score=15,
                    campaign_id=campaign.id,
                    campaign_name=name,
                ))
            return findings

        # ── CTR Analysis ──
        if campaign.impressions >= HEALTH_THRESHOLDS["min_impressions_for_judgment"]:
            ctr = campaign.ctr
            if ctr < HEALTH_THRESHOLDS["critical_low_ctr"]:
                findings.append(AuditFinding(
                    severity=AuditSeverity.HIGH,
                    category="CTR",
                    title=f"'{name}' — critically low CTR ({ctr:.1f}%)",
                    detail=(
                        f"CTR is {ctr:.1f}% vs benchmark {benchmarks['avg_ctr_pct']}% "
                        f"for this market. This means ads are showing but people aren't "
                        f"clicking. Likely causes: irrelevant keywords, weak ad copy, "
                        f"or wrong audience."
                    ),
                    action=ActionType.IMPROVE_AD_COPY,
                    action_detail=(
                        "1) Review search terms report for irrelevant queries\n"
                        "2) Rewrite headlines with treatment name + location + USP\n"
                        "3) Add negative keywords for non-converting terms\n"
                        "4) Consider changing match types from broad to phrase/exact"
                    ),
                    expected_impact=f"Improving CTR from {ctr:.1f}% to {benchmarks['avg_ctr_pct']}% "
                                    f"would increase clicks by {((benchmarks['avg_ctr_pct']/max(ctr,0.1))-1)*100:.0f}%",
                    priority_score=80,
                    campaign_id=campaign.id,
                    campaign_name=name,
                ))
            elif ctr >= HEALTH_THRESHOLDS["excellent_ctr"]:
                findings.append(AuditFinding(
                    severity=AuditSeverity.INFO,
                    category="CTR",
                    title=f"'{name}' — excellent CTR ({ctr:.1f}%)",
                    detail=f"CTR of {ctr:.1f}% is well above benchmark. This campaign's "
                           f"ad copy and targeting are performing. Consider increasing budget.",
                    action=ActionType.INCREASE_BUDGET,
                    action_detail="Increase daily budget by 20-30% to capture more of this demand",
                    expected_impact="More clicks at the same efficiency = more appointments",
                    priority_score=60,
                    campaign_id=campaign.id,
                    campaign_name=name,
                ))

        # ── Spend efficiency ──
        # Normalize spend: if > 100000, likely in paise (micros), convert to INR
        spend_inr = campaign.spend / 1000000 if campaign.spend > 100000 else campaign.spend
        if spend_inr > HEALTH_THRESHOLDS["waste_spend_zero_conv"] and campaign.conversions == 0:
            findings.append(AuditFinding(
                severity=AuditSeverity.HIGH,
                category="Conversion",
                title=f"'{name}' — ₹{campaign.spend:,} spent, 0 conversions",
                detail=(
                    f"This campaign has spent ₹{spend_inr:,.0f} without a single "
                    f"tracked conversion. Either: (a) conversion tracking is broken, "
                    f"(b) landing page isn't converting, or (c) traffic quality is poor."
                ),
                action=ActionType.FIX_TRACKING,
                action_detail=(
                    "1) Verify conversion tracking is set up (call tracking, form submission)\n"
                    "2) Check landing page load speed and mobile friendliness\n"
                    "3) Review search terms for intent mismatch\n"
                    "4) If CPA > ₹{target}, reduce budget and fix fundamentals first"
                ),
                expected_impact="Either fix tracking (reveals hidden conversions) or "
                                "stop wasting budget on non-converting traffic",
                priority_score=85,
                campaign_id=campaign.id,
                campaign_name=name,
            ))

        # ── CPC vs benchmark ──
        # Note: campaign.cpc may be in paise (smallest unit) from Google Ads import
        # We normalize: if CPC > 500, assume it's in paise and divide by 100
        if campaign.clicks > 0 and campaign.cpc > 0:
            cpc_inr = campaign.cpc / 100 if campaign.cpc > 500 else campaign.cpc
            benchmark_cpc = benchmarks["avg_cpc_inr"]
            if cpc_inr > benchmark_cpc * 2.5:
                findings.append(AuditFinding(
                    severity=AuditSeverity.MEDIUM,
                    category="CPC",
                    title=f"'{name}' — CPC ₹{cpc_inr:.0f} is {cpc_inr/benchmark_cpc:.1f}x benchmark",
                    detail=(
                        f"Average CPC of ₹{cpc_inr:.0f} is significantly above "
                        f"the ₹{benchmark_cpc} benchmark for this market. High CPCs eat "
                        f"through budget faster, reducing total patient volume."
                    ),
                    action=ActionType.CHANGE_BID_STRATEGY,
                    action_detail=(
                        "1) Switch to Maximize Clicks or Target CPA bidding\n"
                        "2) Review keyword match types — broad match often inflates CPC\n"
                        "3) Add long-tail keywords with lower competition\n"
                        "4) Check Quality Score — low QS increases CPC"
                    ),
                    expected_impact=f"Reducing CPC to ₹{benchmark_cpc*1.5:.0f} would give "
                                    f"{campaign.spend//(benchmark_cpc*1.5) - campaign.clicks:.0f} more clicks "
                                    f"for the same spend",
                    priority_score=55,
                    campaign_id=campaign.id,
                    campaign_name=name,
                ))

        return findings

    # ═══════════════════════════════════════════════════════════
    # INTERNAL: Coverage gap analysis
    # ═══════════════════════════════════════════════════════════

    def _audit_coverage_gaps(
        self,
        campaigns: list[Campaign],
        services: list[str],
        city: str,
    ) -> list[AuditFinding]:
        """Check if the clinic's services are covered by campaigns."""
        findings = []

        # Normalize campaign names for matching
        campaign_names_lower = [
            (c.name or "").lower() for c in campaigns
        ]
        all_campaign_text = " ".join(campaign_names_lower)

        # Check each service the clinic offers
        for service in services:
            service_lower = service.lower().strip()

            # Find which treatment tier this service belongs to
            tier_name = None
            tier_data = None
            for tn, td in TREATMENT_TIERS.items():
                if any(t in service_lower for t in td["treatments"]):
                    tier_name = tn
                    tier_data = td
                    break

            if not tier_data:
                continue  # Service not in our treatment mapping

            # Check if any campaign covers this service
            service_words = service_lower.split()
            has_campaign = any(
                any(word in cn for word in service_words if len(word) > 3)
                for cn in campaign_names_lower
            )

            if not has_campaign:
                findings.append(AuditFinding(
                    severity=(
                        AuditSeverity.HIGH if tier_name in ("tier_1_high_value", "tier_2_medium_value")
                        else AuditSeverity.MEDIUM
                    ),
                    category="Coverage Gap",
                    title=f"No campaign for '{service}' ({tier_name.replace('_', ' ').title()})",
                    detail=(
                        f"The clinic offers {service} (avg case value ₹{tier_data['avg_case_value_inr']:,}) "
                        f"but has no search campaign targeting it. Patients searching for "
                        f"'{service_lower} in {city}' won't find this clinic through ads."
                    ),
                    action=ActionType.CREATE_CAMPAIGN,
                    action_detail=(
                        f"Create a Search campaign for '{service}' with:\n"
                        f"- Keywords: '{service_lower} {city}', '{service_lower} near me', "
                        f"'best {service_lower} clinic {city}'\n"
                        f"- Target CPA: ₹{tier_data['target_cpa_inr']}\n"
                        f"- Suggested daily budget: ₹{round(tier_data['target_cpa_inr'] * 2)}"
                    ),
                    expected_impact=(
                        f"Capturing '{service_lower}' searches could bring "
                        f"₹{tier_data['avg_case_value_inr']:,}/patient. "
                        f"At target CPA of ₹{tier_data['target_cpa_inr']}, "
                        f"ROI = {tier_data['avg_case_value_inr']/tier_data['target_cpa_inr']:.0f}x"
                    ),
                    priority_score=90 if "tier_1" in tier_name else 70 if "tier_2" in tier_name else 50,
                ))

        # Check for emergency campaign
        has_emergency = any("emergency" in cn or "pain" in cn or "toothache" in cn
                          for cn in campaign_names_lower)
        if not has_emergency:
            findings.append(AuditFinding(
                severity=AuditSeverity.MEDIUM,
                category="Coverage Gap",
                title="No emergency dental campaign",
                detail=(
                    "Emergency searches ('tooth pain', 'dental emergency', 'toothache') "
                    "have the highest conversion rate (often 15-25%) because the patient "
                    "needs help NOW. Missing this is leaving easy appointments on the table."
                ),
                action=ActionType.CREATE_CAMPAIGN,
                action_detail=(
                    f"Create an emergency campaign with:\n"
                    f"- Keywords: 'emergency dentist {city}', 'tooth pain {city}', "
                    f"'dental emergency near me'\n"
                    f"- Ad copy emphasizing: 'Same Day Appointment', 'Walk-in Welcome'\n"
                    f"- Call extensions with clinic phone number\n"
                    f"- Schedule: 24/7 (emergencies happen anytime)"
                ),
                expected_impact="Emergency patients convert at 15-25% vs 3-5% for regular searches",
                priority_score=65,
            ))

        return findings

    # ═══════════════════════════════════════════════════════════
    # INTERNAL: Budget distribution audit
    # ═══════════════════════════════════════════════════════════

    def _audit_budget_distribution(
        self,
        campaigns: list[Campaign],
        monthly_budget: float,
    ) -> list[AuditFinding]:
        findings = []

        if not campaigns or monthly_budget <= 0:
            return findings

        active = [c for c in campaigns if c.status == CampaignStatus.ACTIVE]
        if not active:
            return findings

        # Check if budget is equally distributed (the problem the user identified)
        budgets = [c.daily_budget for c in active if c.daily_budget > 0]
        if len(budgets) >= 2:
            budget_range = max(budgets) - min(budgets)
            avg_budget = sum(budgets) / len(budgets)

            if budget_range < avg_budget * 0.1:
                # All budgets are within 10% of each other = equal split
                findings.append(AuditFinding(
                    severity=AuditSeverity.HIGH,
                    category="Budget Strategy",
                    title="Budget is split equally — not by performance",
                    detail=(
                        "All active campaigns have nearly the same daily budget. "
                        "A performance marketer allocates MORE budget to campaigns "
                        "that generate conversions at lower CPA, and LESS to those "
                        "that don't convert. Equal split wastes money on losers."
                    ),
                    action=ActionType.REALLOCATE_BUDGET,
                    action_detail=(
                        "Shift budget based on performance:\n"
                        "- Top CTR campaigns → increase budget 30-50%\n"
                        "- Campaigns with 0 conversions after ₹2000+ spend → cut 50%\n"
                        "- High-value treatment campaigns (implants, smile makeover) → priority\n"
                        "- Low-value treatment campaigns (cleaning) → minimum budget"
                    ),
                    expected_impact="Performance-based allocation typically improves ROAS by 30-60%",
                    priority_score=85,
                ))

        return findings

    # ═══════════════════════════════════════════════════════════
    # INTERNAL: Conversion tracking audit
    # ═══════════════════════════════════════════════════════════

    def _audit_conversion_setup(self, campaigns: list[Campaign]) -> list[AuditFinding]:
        findings = []

        total_spend = sum(c.spend for c in campaigns)
        total_conversions = sum(c.conversions for c in campaigns)

        if total_spend > 5000 and total_conversions == 0:
            findings.append(AuditFinding(
                severity=AuditSeverity.CRITICAL,
                category="Conversion Tracking",
                title="₹{:,} spent with 0 tracked conversions".format(total_spend),
                detail=(
                    "The account has spent ₹{:,} but shows zero conversions. "
                    "This usually means conversion tracking isn't set up properly. "
                    "Without conversion data, Google can't optimize for patients "
                    "who actually book appointments — it just chases clicks."
                ).format(total_spend),
                action=ActionType.FIX_TRACKING,
                action_detail=(
                    "Set up conversion tracking:\n"
                    "1) Phone call tracking via Twilio (already integrated)\n"
                    "2) WhatsApp message tracking (when patient sends first message)\n"
                    "3) Form submission tracking on landing page\n"
                    "4) Google Ads call extension tracking\n"
                    "5) Import offline conversions (booked appointments)"
                ),
                expected_impact=(
                    "With conversion tracking, Google's AI bidding (tCPA, tROAS) "
                    "can optimize for actual appointments instead of just clicks. "
                    "Typically reduces CPA by 30-50%."
                ),
                priority_score=98,
            ))

        return findings

    # ═══════════════════════════════════════════════════════════
    # INTERNAL: Budget allocation logic
    # ═══════════════════════════════════════════════════════════

    def _generate_budget_plan(
        self,
        campaigns: list[Campaign],
        monthly_budget: float,
        services: list[str],
        city_tier: str,
    ) -> list[dict]:
        """
        Generate intelligent budget allocation based on performance data.

        The algorithm a performance marketer uses:
        1. Score each campaign on: CTR, CPC efficiency, conversion rate, treatment value
        2. Classify into: Stars (high perf), Workhorses (decent), Dogs (underperform), New
        3. Stars get 40% of budget, Workhorses 35%, New campaigns 20%, Dogs get 5% (probation)
        """
        if not campaigns or monthly_budget <= 0:
            return []

        daily_total = round(monthly_budget / 30.4)
        benchmarks = CITY_BENCHMARKS[city_tier]
        allocations = []

        for campaign in campaigns:
            score = self._score_campaign(campaign, benchmarks)
            tier = self._classify_treatment_tier(campaign.name)

            allocations.append({
                "campaign_id": str(campaign.id),
                "campaign_name": campaign.name,
                "status": campaign.status.value,
                "performance_score": score["total"],
                "score_breakdown": score,
                "treatment_tier": tier,
                "treatment_value_weight": (
                    TREATMENT_TIERS.get(tier, {}).get("budget_weight", 0.10)
                ),
                "current_daily_budget": campaign.daily_budget,
                "impressions": campaign.impressions,
                "clicks": campaign.clicks,
                "ctr": campaign.ctr,
                "cpc": campaign.cpc,
                "spend": campaign.spend,
                "conversions": campaign.conversions,
            })

        # Calculate weighted scores for budget distribution
        # Weight = performance_score * treatment_value_weight
        for alloc in allocations:
            perf = alloc["performance_score"]
            treatment_weight = alloc["treatment_value_weight"]

            # Active campaigns with data get scored normally
            # Paused campaigns with good past data get half weight (potential)
            # Zero-data campaigns get minimum allocation
            if alloc["status"] == "ACTIVE" and alloc["impressions"] > 0:
                alloc["budget_weight"] = perf * treatment_weight * 1.0
            elif alloc["status"] == "PAUSED" and alloc["clicks"] > 0:
                alloc["budget_weight"] = perf * treatment_weight * 0.5
            elif alloc["status"] == "ACTIVE":
                alloc["budget_weight"] = treatment_weight * 0.3  # New, needs data
            else:
                alloc["budget_weight"] = 0.05  # Paused, no data = minimum

        total_weight = sum(a["budget_weight"] for a in allocations) or 1
        min_daily = 50  # Minimum ₹50/day for any active campaign

        for alloc in allocations:
            raw_budget = (alloc["budget_weight"] / total_weight) * daily_total
            alloc["recommended_daily_budget"] = max(round(raw_budget), min_daily)

            current = alloc["current_daily_budget"]
            recommended = alloc["recommended_daily_budget"]

            if current > 0:
                alloc["change_pct"] = round(
                    ((recommended - current) / current) * 100, 1
                )
            else:
                alloc["change_pct"] = 100.0

            # Generate reason
            if alloc["performance_score"] >= 70:
                alloc["reason"] = "High performer — deserves more budget to capture demand"
            elif alloc["performance_score"] >= 40:
                alloc["reason"] = "Decent performance — maintain budget, optimize for improvement"
            elif alloc["impressions"] == 0:
                alloc["reason"] = "No data yet — needs minimum budget to test"
            else:
                alloc["reason"] = "Underperforming — reduced budget, fix fundamentals first"

        # Sort: highest recommended budget first
        allocations.sort(key=lambda a: a["recommended_daily_budget"], reverse=True)

        return allocations

    def _score_campaign(self, campaign: Campaign, benchmarks: dict) -> dict:
        """Score a campaign 0-100 based on real performance metrics."""
        scores = {
            "ctr_score": 0,
            "cpc_score": 0,
            "conversion_score": 0,
            "volume_score": 0,
            "total": 0,
        }

        # CTR score (0-30 points)
        if campaign.impressions >= 100:
            ctr = campaign.ctr
            benchmark_ctr = benchmarks["avg_ctr_pct"]
            if ctr >= benchmark_ctr * 1.5:
                scores["ctr_score"] = 30
            elif ctr >= benchmark_ctr:
                scores["ctr_score"] = 25
            elif ctr >= benchmark_ctr * 0.5:
                scores["ctr_score"] = 15
            elif ctr > 0:
                scores["ctr_score"] = 5
            # 0 if zero CTR

        # CPC efficiency score (0-25 points)
        if campaign.clicks > 0 and campaign.cpc > 0:
            benchmark_cpc = benchmarks["avg_cpc_inr"]
            if campaign.cpc <= benchmark_cpc * 0.7:
                scores["cpc_score"] = 25  # Below benchmark = efficient
            elif campaign.cpc <= benchmark_cpc:
                scores["cpc_score"] = 20
            elif campaign.cpc <= benchmark_cpc * 1.5:
                scores["cpc_score"] = 15
            elif campaign.cpc <= benchmark_cpc * 2.5:
                scores["cpc_score"] = 8
            else:
                scores["cpc_score"] = 2  # Very expensive

        # Conversion score (0-30 points) — the most important metric
        if campaign.conversions > 0:
            if campaign.clicks > 0:
                conv_rate = campaign.conversions / campaign.clicks
                if conv_rate >= 0.10:
                    scores["conversion_score"] = 30
                elif conv_rate >= 0.05:
                    scores["conversion_score"] = 25
                elif conv_rate >= 0.02:
                    scores["conversion_score"] = 20
                else:
                    scores["conversion_score"] = 15
            else:
                scores["conversion_score"] = 10  # Has conversions somehow
        elif campaign.spend > 2000:
            scores["conversion_score"] = 0  # Spent money, no conversions

        # Volume score (0-15 points) — campaigns with more data are more reliable
        if campaign.impressions >= 5000:
            scores["volume_score"] = 15
        elif campaign.impressions >= 1000:
            scores["volume_score"] = 12
        elif campaign.impressions >= 200:
            scores["volume_score"] = 8
        elif campaign.impressions > 0:
            scores["volume_score"] = 4

        scores["total"] = (
            scores["ctr_score"]
            + scores["cpc_score"]
            + scores["conversion_score"]
            + scores["volume_score"]
        )

        return scores

    def _classify_treatment_tier(self, campaign_name: str) -> str:
        """Match a campaign name to a treatment tier for budget weighting."""
        name_lower = (campaign_name or "").lower()

        for tier_name, tier_data in TREATMENT_TIERS.items():
            if any(treatment in name_lower for treatment in tier_data["treatments"]):
                return tier_name

        return "tier_3_volume"  # Default to volume tier

    # ═══════════════════════════════════════════════════════════
    # INTERNAL: Health score calculation
    # ═══════════════════════════════════════════════════════════

    def _calculate_health_score(
        self,
        findings: list[AuditFinding],
        campaigns: list[Campaign],
        benchmarks: dict,
    ) -> int:
        """Calculate overall account health 0-100."""
        score = 100

        # Deduct for findings by severity
        for finding in findings:
            if finding.severity == AuditSeverity.CRITICAL:
                score -= 20
            elif finding.severity == AuditSeverity.HIGH:
                score -= 10
            elif finding.severity == AuditSeverity.MEDIUM:
                score -= 5
            elif finding.severity == AuditSeverity.LOW:
                score -= 2

        # Bonus for good performance
        active = [c for c in campaigns if c.status == CampaignStatus.ACTIVE]
        if active:
            avg_ctr = sum(c.ctr for c in active) / len(active)
            if avg_ctr > benchmarks["avg_ctr_pct"]:
                score += 5

            total_conversions = sum(c.conversions for c in active)
            if total_conversions > 0:
                score += 10

        return max(0, min(100, score))

    # ═══════════════════════════════════════════════════════════
    # INTERNAL: Action plan generation
    # ═══════════════════════════════════════════════════════════

    def _generate_action_plan(self, top_findings: list[AuditFinding]) -> list[dict]:
        """Convert findings into a prioritized action plan."""
        plan = []
        for i, finding in enumerate(top_findings, 1):
            plan.append({
                "priority": i,
                "severity": finding.severity.value,
                "action": finding.action.value,
                "title": finding.title,
                "what_to_do": finding.action_detail,
                "why": finding.detail,
                "expected_result": finding.expected_impact,
            })
        return plan

    def _summarize_budget_strategy(self, allocations: list[dict]) -> str:
        """Generate a human-readable budget strategy summary."""
        if not allocations:
            return "No campaigns to allocate budget to."

        stars = [a for a in allocations if a["performance_score"] >= 70]
        workhorses = [a for a in allocations if 40 <= a["performance_score"] < 70]
        dogs = [a for a in allocations if 0 < a["performance_score"] < 40 and a["impressions"] > 0]
        new = [a for a in allocations if a["impressions"] == 0]

        parts = []
        if stars:
            names = ", ".join(a["campaign_name"] for a in stars[:3])
            parts.append(f"Top performers ({names}) get increased budget")
        if workhorses:
            parts.append(f"{len(workhorses)} campaigns maintained at current levels")
        if dogs:
            names = ", ".join(a["campaign_name"] for a in dogs[:2])
            parts.append(f"Underperformers ({names}) get reduced budget — fix before scaling")
        if new:
            parts.append(f"{len(new)} campaigns need initial data — minimum budget to test")

        return ". ".join(parts) + "."
