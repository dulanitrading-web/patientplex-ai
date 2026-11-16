"""
Google Ads Master Brain — Deep expertise in Google Search & Display for clinics.

This brain thinks like a Google Ads specialist who has managed 500+ healthcare
accounts. It knows:

1. CAMPAIGN STRUCTURE: How to structure campaigns for clinics
   - Single Keyword Ad Groups (SKAGs) for high-value treatments
   - Treatment-based campaign grouping
   - Brand vs Generic vs Competitor campaigns
   - Call-only campaigns for emergency/urgent searches

2. KEYWORD STRATEGY: What patients actually search
   - Treatment + City keywords (highest intent)
   - "near me" keywords (location intent)
   - Symptom keywords (early funnel)
   - Cost/price keywords (decision stage)
   - Negative keyword lists (prevent waste)

3. BIDDING STRATEGY: When and how much to bid
   - Max Conversions for new accounts (need data first)
   - Target CPA once 30+ conversions
   - Manual CPC for tight budgets
   - Time-of-day adjustments for Indian clinics
   - Device bid adjustments (mobile-first)

4. QUALITY SCORE: How to improve it
   - Ad relevance (keyword in headline)
   - Landing page experience
   - Expected CTR signals

5. BUDGET OPTIMIZATION: Where to put the money
   - High-intent campaigns get priority
   - Treatment value determines budget ceiling
   - Competition level affects strategy
"""

import logging
from dataclasses import dataclass
from typing import Optional
from uuid import UUID

logger = logging.getLogger(__name__)


# ═══════════════════════════════════════════════════════════════
# GOOGLE ADS CAMPAIGN TEMPLATES — What to create for each specialty
# ═══════════════════════════════════════════════════════════════

DENTAL_CAMPAIGN_TEMPLATES = {
    "high_value_implants": {
        "name_template": "{clinic} | Search | Dental Implants | {city}",
        "campaign_type": "SEARCH",
        "keywords": [
            "dental implant {city}", "dental implant cost {city}",
            "best dental implant clinic {city}", "dental implant near me",
            "tooth implant {city}", "implant dentist {city}",
            "full mouth implant {city}", "all on 4 implant {city}",
        ],
        "negative_keywords": [
            "course", "training", "salary", "jobs", "college",
            "DIY", "free", "home remedy",
        ],
        "headlines": [
            "Dental Implants in {city}",
            "Same Day Implant Placement",
            "₹25,000 Onwards — Implants",
            "15+ Years Experience",
            "Free Implant Consultation",
            "Book Your Appointment Now",
        ],
        "descriptions": [
            "Advanced dental implant treatment by experienced specialist. Same-day placement available. Book free consultation today.",
            "Affordable dental implants with latest technology. EMI options available. {clinic} — Trusted by 1000+ patients.",
        ],
        "budget_weight": 0.30,
        "target_cpa_multiplier": 1.5,  # Can afford higher CPA
        "bid_strategy": "MAX_CONVERSIONS",
        "treatment_value_inr": 80000,
    },
    "cosmetic_smile": {
        "name_template": "{clinic} | Search | Smile Design | {city}",
        "campaign_type": "SEARCH",
        "keywords": [
            "smile makeover {city}", "cosmetic dentistry {city}",
            "smile design {city}", "teeth whitening {city}",
            "veneers {city}", "best cosmetic dentist {city}",
        ],
        "negative_keywords": [
            "course", "training", "toothpaste", "DIY",
        ],
        "headlines": [
            "Smile Makeover — {city}",
            "Transform Your Smile Today",
            "Cosmetic Dentistry Expert",
            "Teeth Whitening ₹5,000",
            "Veneers & Smile Design",
            "Free Smile Assessment",
        ],
        "descriptions": [
            "Get the smile you've always wanted. Advanced cosmetic dental treatments. Before-after gallery available. Book consultation.",
            "Hollywood smile at Indian prices. Veneers, whitening & complete smile design. {clinic} — {city}.",
        ],
        "budget_weight": 0.20,
        "target_cpa_multiplier": 1.2,
        "bid_strategy": "MAX_CONVERSIONS",
        "treatment_value_inr": 40000,
    },
    "braces_aligners": {
        "name_template": "{clinic} | Search | Braces & Aligners | {city}",
        "campaign_type": "SEARCH",
        "keywords": [
            "braces {city}", "braces cost {city}",
            "invisible braces {city}", "aligners {city}",
            "invisalign {city}", "teeth straightening {city}",
            "orthodontist {city}", "best braces doctor {city}",
        ],
        "negative_keywords": [
            "remove braces", "braces pain", "DIY braces",
        ],
        "headlines": [
            "Braces Starting ₹25,000",
            "Invisible Aligners — {city}",
            "Straight Teeth in 6 Months",
            "EMI from ₹3,000/month",
            "Orthodontist — {city}",
            "Free Braces Consultation",
        ],
        "descriptions": [
            "Metal braces, ceramic braces & invisible aligners. Affordable EMI plans. Expert orthodontist at {clinic}.",
            "Get straight teeth without metal. Clear aligners from ₹50,000. Free consultation & 3D scan. {clinic} {city}.",
        ],
        "budget_weight": 0.15,
        "target_cpa_multiplier": 1.0,
        "bid_strategy": "MAX_CONVERSIONS",
        "treatment_value_inr": 30000,
    },
    "root_canal_emergency": {
        "name_template": "{clinic} | Search | RCT & Emergency | {city}",
        "campaign_type": "SEARCH",
        "keywords": [
            "root canal treatment {city}", "rct {city}",
            "tooth pain {city}", "emergency dentist {city}",
            "dental emergency {city}", "toothache treatment {city}",
            "root canal cost {city}", "broken tooth {city}",
        ],
        "negative_keywords": [
            "root canal side effects", "root canal pain",
        ],
        "headlines": [
            "Emergency Dentist — {city}",
            "Painless Root Canal — ₹3,000",
            "Same Day Appointment",
            "Open Sundays — Walk-in OK",
            "Tooth Pain? Call Now",
            "24/7 Dental Emergency",
        ],
        "descriptions": [
            "Suffering from tooth pain? Get instant relief. Painless root canal treatment with latest technology. Walk-in welcome.",
            "Emergency dental care available now. {clinic} {city}. Experienced team. Affordable treatment. Call for appointment.",
        ],
        "budget_weight": 0.15,
        "target_cpa_multiplier": 0.8,
        "bid_strategy": "MAX_CLICKS",  # Volume play
        "treatment_value_inr": 5000,
    },
    "local_brand": {
        "name_template": "{clinic} | Search | Local Dentist | {city}",
        "campaign_type": "SEARCH",
        "keywords": [
            "dentist near me", "dental clinic near me",
            "best dentist {city}", "dentist {city}",
            "dental clinic {city}", "dental hospital {city}",
        ],
        "negative_keywords": [
            "dental college", "BDS", "MDS admission",
        ],
        "headlines": [
            "Best Dentist in {city}",
            "{clinic} — {city}",
            "15+ Years Experience",
            "1000+ Happy Patients",
            "All Dental Treatments",
            "Book Online — Free Consult",
        ],
        "descriptions": [
            "Complete dental care under one roof. From routine checkup to advanced treatments. {clinic} — trusted by {city} families.",
            "Looking for a good dentist? Visit {clinic}. Modern equipment, experienced team, affordable prices. Book today.",
        ],
        "budget_weight": 0.10,
        "target_cpa_multiplier": 0.7,
        "bid_strategy": "MAX_CLICKS",
        "treatment_value_inr": 3000,
    },
    "call_only": {
        "name_template": "{clinic} | Call Only | {city}",
        "campaign_type": "CALL_ONLY",
        "keywords": [
            "dentist phone number {city}", "dental clinic contact {city}",
            "dentist near me call", "emergency dentist call",
        ],
        "negative_keywords": [],
        "headlines": [
            "Call {clinic} Now",
            "Dentist — {city}",
            "Book Appointment by Phone",
        ],
        "descriptions": [
            "Call now to book your dental appointment. {clinic} {city}. All treatments available.",
        ],
        "budget_weight": 0.10,
        "target_cpa_multiplier": 0.5,
        "bid_strategy": "MAX_CLICKS",
        "treatment_value_inr": 3000,
    },
}


# ═══════════════════════════════════════════════════════════════
# BID STRATEGY DECISION MATRIX
# ═══════════════════════════════════════════════════════════════

BID_STRATEGY_RULES = {
    "new_account_no_data": {
        "strategy": "MAXIMIZE_CLICKS",
        "reason": "New account needs click data before Google can optimize for conversions",
        "when_to_switch": "After 50+ clicks and 5+ conversions, switch to MAX_CONVERSIONS",
        "max_cpc_cap": True,
    },
    "some_data_few_conversions": {
        "strategy": "MAXIMIZE_CLICKS",
        "reason": "Some data but not enough conversions for smart bidding",
        "when_to_switch": "After 15+ conversions in 30 days, switch to TARGET_CPA",
        "max_cpc_cap": True,
    },
    "enough_conversions": {
        "strategy": "MAXIMIZE_CONVERSIONS",
        "reason": "Enough conversion data for Google's ML to optimize",
        "when_to_switch": "After 30+ conversions, consider TARGET_CPA with specific target",
        "max_cpc_cap": False,
    },
    "mature_account": {
        "strategy": "TARGET_CPA",
        "reason": "Stable conversion history allows precise CPA targeting",
        "when_to_switch": "If CPA drifts >30% above target for 2 weeks, revert to MAX_CONVERSIONS",
        "max_cpc_cap": False,
    },
}


# Time-of-day bid modifiers for Indian clinics (IST)
INDIA_HOURLY_BID_MODIFIERS = {
    0: -70, 1: -70, 2: -70, 3: -70, 4: -70, 5: -50,  # Night: reduce heavily
    6: -30, 7: -10, 8: 0,                               # Early morning: minimal
    9: +20, 10: +30, 11: +25,                           # Morning: patients search before visiting
    12: +35, 13: +30,                                    # Lunch break: peak search time
    14: +15, 15: +10, 16: +10,                          # Afternoon: moderate
    17: +20, 18: +30, 19: +35,                          # Evening: second peak (after work)
    20: +25, 21: +15, 22: 0, 23: -30,                  # Late evening: declining
}


class GoogleAdsBrain:
    """Master brain for Google Ads — thinks like a senior Google Ads specialist.

    Capabilities:
    1. Analyze an existing Google Ads account and find every problem
    2. Recommend optimal campaign structure for any specialty
    3. Generate keywords, ad copy, and negative keywords
    4. Determine the right bid strategy based on account maturity
    5. Set time-of-day and device bid modifiers
    6. Calculate CPA targets from treatment values
    """

    def recommend_campaign_structure(
        self,
        specialty: str,
        city: str,
        clinic_name: str,
        services: list[str],
        monthly_budget: float,
    ) -> list[dict]:
        """Recommend what campaigns to create for a clinic.

        This is what a Google Ads specialist does on day 1:
        1. Look at what the clinic offers
        2. Map services to campaign templates
        3. Prioritize by treatment value and search volume
        4. Allocate budget to maximize patient acquisition
        """
        if specialty == "DENTIST":
            templates = DENTAL_CAMPAIGN_TEMPLATES
        else:
            # For non-dental, adapt the templates
            templates = self._adapt_templates_for_specialty(specialty, city, clinic_name)

        daily_budget = round(monthly_budget / 30.4)
        recommendations = []

        for template_key, template in templates.items():
            # Check if this template matches any of the clinic's services
            relevance = self._check_template_relevance(template_key, services)

            campaign_name = template["name_template"].format(
                clinic=clinic_name or "Clinic",
                city=city or "Local",
            )

            campaign_daily = round(daily_budget * template["budget_weight"])

            recommendations.append({
                "template_key": template_key,
                "campaign_name": campaign_name,
                "campaign_type": template["campaign_type"],
                "keywords": [
                    kw.format(city=city.lower() if city else "")
                    for kw in template["keywords"]
                ],
                "negative_keywords": template["negative_keywords"],
                "headlines": [
                    h.format(clinic=clinic_name or "Clinic", city=city or "")
                    for h in template["headlines"]
                ],
                "descriptions": [
                    d.format(clinic=clinic_name or "Clinic", city=city or "")
                    for d in template["descriptions"]
                ],
                "daily_budget_inr": max(campaign_daily, 100),
                "treatment_value_inr": template["treatment_value_inr"],
                "bid_strategy": template["bid_strategy"],
                "relevance_to_services": relevance,
                "priority": "high" if relevance > 0.5 else "medium" if relevance > 0 else "low",
            })

        # Sort by relevance × treatment value
        recommendations.sort(
            key=lambda r: r["relevance_to_services"] * r["treatment_value_inr"],
            reverse=True,
        )

        return recommendations

    def get_bid_strategy_recommendation(
        self,
        total_clicks_30d: int,
        total_conversions_30d: int,
        account_age_days: int,
    ) -> dict:
        """Recommend the right bid strategy based on account maturity."""
        if total_conversions_30d >= 30:
            rule = BID_STRATEGY_RULES["mature_account"]
        elif total_conversions_30d >= 15:
            rule = BID_STRATEGY_RULES["enough_conversions"]
        elif total_clicks_30d >= 50:
            rule = BID_STRATEGY_RULES["some_data_few_conversions"]
        else:
            rule = BID_STRATEGY_RULES["new_account_no_data"]

        return {
            "recommended_strategy": rule["strategy"],
            "reason": rule["reason"],
            "when_to_switch": rule["when_to_switch"],
            "use_max_cpc_cap": rule["max_cpc_cap"],
            "account_metrics": {
                "clicks_30d": total_clicks_30d,
                "conversions_30d": total_conversions_30d,
                "account_age_days": account_age_days,
            },
        }

    def get_hourly_bid_modifiers(self) -> dict:
        """Return time-of-day bid modifiers for Indian clinic hours."""
        return {
            "timezone": "Asia/Kolkata",
            "modifiers": INDIA_HOURLY_BID_MODIFIERS,
            "peak_hours": [9, 10, 11, 12, 13, 17, 18, 19],
            "explanation": (
                "Indian patients search for doctors during morning (9-11am), "
                "lunch break (12-1pm), and evening (5-7pm). We bid higher during "
                "these hours and reduce bids during night when conversion is unlikely."
            ),
        }

    def calculate_target_cpa(
        self,
        treatment_value_inr: float,
        target_roas: float = 3.0,
    ) -> dict:
        """Calculate target CPA from treatment value and desired ROAS.

        Rule of thumb for healthcare:
        - CPA should be < 10% of treatment value for high-value treatments
        - CPA should be < 20% of treatment value for medium-value
        - CPA can be up to 50% for volume/retention plays (cleanings)
        """
        if treatment_value_inr >= 50000:
            max_cpa_pct = 0.10
        elif treatment_value_inr >= 15000:
            max_cpa_pct = 0.15
        elif treatment_value_inr >= 5000:
            max_cpa_pct = 0.25
        else:
            max_cpa_pct = 0.40

        target_cpa = round(treatment_value_inr * max_cpa_pct)
        roas_at_target = round(treatment_value_inr / target_cpa, 1) if target_cpa > 0 else 0

        return {
            "treatment_value_inr": treatment_value_inr,
            "target_cpa_inr": target_cpa,
            "max_cpa_percent": max_cpa_pct * 100,
            "expected_roas": roas_at_target,
            "explanation": (
                f"For a ₹{treatment_value_inr:,} treatment, max CPA should be "
                f"₹{target_cpa:,} ({max_cpa_pct*100:.0f}% of treatment value). "
                f"This gives {roas_at_target}x ROAS."
            ),
        }

    def _check_template_relevance(self, template_key: str, services: list[str]) -> float:
        """Check how relevant a campaign template is to the clinic's services."""
        services_lower = [s.lower() for s in services]
        template_terms = {
            "high_value_implants": ["implant", "dental implant"],
            "cosmetic_smile": ["cosmetic", "smile", "whitening", "veneer"],
            "braces_aligners": ["braces", "aligner", "orthodontic", "invisalign"],
            "root_canal_emergency": ["root canal", "rct", "emergency", "extraction"],
            "local_brand": ["dentist", "dental"],  # Always relevant
            "call_only": ["dentist"],  # Always relevant
        }

        terms = template_terms.get(template_key, [])
        if not terms:
            return 0.5

        matches = sum(
            1 for term in terms
            if any(term in svc for svc in services_lower)
        )
        return min(matches / max(len(terms), 1), 1.0)

    def _adapt_templates_for_specialty(
        self, specialty: str, city: str, clinic_name: str
    ) -> dict:
        """Create campaign templates for non-dental specialties."""
        # For now, return a generic structure
        # TODO: Add specialty-specific templates like dental
        from app.schemas.specialty import SPECIALTY_CONFIGS
        config = SPECIALTY_CONFIGS.get(specialty)
        if not config:
            return {}

        return {
            "main_search": {
                "name_template": f"{clinic_name or 'Clinic'} | Search | {specialty.title()} | {city or 'Local'}",
                "campaign_type": "SEARCH",
                "keywords": config.default_keywords[:10],
                "negative_keywords": config.negative_keywords,
                "headlines": [
                    f"Best {specialty.title().replace('_', ' ')} in {city or 'your city'}",
                    "Book Appointment Today",
                    "Expert Treatment Available",
                    "Experienced Specialist",
                    "Affordable Prices",
                    "Free Consultation",
                ],
                "descriptions": [
                    f"Expert {specialty.lower().replace('_', ' ')} treatment. Experienced specialist with modern equipment. Book your appointment today.",
                    f"Visit our clinic for the best {specialty.lower().replace('_', ' ')} care in {city or 'your area'}. Affordable prices. Walk-in welcome.",
                ],
                "budget_weight": 0.60,
                "target_cpa_multiplier": 1.0,
                "bid_strategy": "MAX_CONVERSIONS",
                "treatment_value_inr": 10000,
            },
            "near_me": {
                "name_template": f"{clinic_name or 'Clinic'} | Search | Near Me | {city or 'Local'}",
                "campaign_type": "SEARCH",
                "keywords": [
                    f"{specialty.lower().replace('_', ' ')} near me",
                    f"best {specialty.lower().replace('_', ' ')} near me",
                    f"{specialty.lower().replace('_', ' ')} clinic near me",
                ],
                "negative_keywords": config.negative_keywords,
                "headlines": [
                    f"{specialty.title().replace('_', ' ')} Near You",
                    "Open Now — Book Online",
                    f"{clinic_name or 'Our Clinic'}",
                ],
                "descriptions": [
                    f"Looking for a {specialty.lower().replace('_', ' ')} near you? {clinic_name or 'Visit us'}. Modern clinic, experienced doctor.",
                ],
                "budget_weight": 0.40,
                "target_cpa_multiplier": 0.8,
                "bid_strategy": "MAX_CLICKS",
                "treatment_value_inr": 5000,
            },
        }
