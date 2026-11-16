"""
Meta Ads Master Brain — Deep expertise in Facebook & Instagram ads for clinics.

Unlike Google (intent-based), Meta is discovery-based:
patients don't know they need treatment until they see your ad.

This brain knows:
1. AUDIENCE STRATEGY: Who to target for each treatment
2. CREATIVE STRATEGY: What visuals and copy convert for healthcare
3. FUNNEL STRATEGY: Awareness → Consideration → Booking
4. LOOKALIKE STRATEGY: Find patients similar to existing ones
5. RETARGETING: Re-engage website visitors who didn't book
"""

import logging

logger = logging.getLogger(__name__)


# Treatment → Audience targeting for Indian clinics
TREATMENT_AUDIENCES = {
    "dental_implants": {
        "age_range": [35, 65],
        "interests": [
            "Dental health", "Dental care", "Cosmetic dentistry",
            "Health & wellness", "Medical tourism",
        ],
        "behaviors": ["Engaged shoppers", "Frequent travelers"],
        "income_targeting": "top_25_percent",
        "creative_angle": "before_after_transformation",
        "cta": "Book Free Consultation",
        "ad_format": "carousel",  # Before/after works best
    },
    "braces_aligners": {
        "age_range": [16, 35],
        "interests": [
            "Beauty", "Fashion", "Self improvement",
            "Fitness", "Social media",
        ],
        "behaviors": ["Engaged shoppers"],
        "income_targeting": "top_50_percent",
        "creative_angle": "confidence_transformation",
        "cta": "Get Free Smile Assessment",
        "ad_format": "video",  # Transformation videos work best
    },
    "teeth_whitening": {
        "age_range": [20, 40],
        "interests": [
            "Beauty", "Skincare", "Wedding planning",
            "Photography", "Fashion",
        ],
        "behaviors": ["Engaged shoppers"],
        "income_targeting": "top_50_percent",
        "creative_angle": "quick_result",
        "cta": "Get Whiter Teeth Today",
        "ad_format": "single_image",
    },
    "skin_treatment": {
        "age_range": [18, 45],
        "interests": [
            "Skincare", "Beauty", "Dermatology",
            "Acne treatment", "Anti-aging",
        ],
        "behaviors": ["Online shoppers"],
        "income_targeting": "top_50_percent",
        "creative_angle": "before_after_skin",
        "cta": "Book Skin Consultation",
        "ad_format": "carousel",
    },
}

# Creative best practices for healthcare Meta ads
CREATIVE_RULES = {
    "do": [
        "Use real patient before/after photos (with consent)",
        "Show the doctor in a clean, modern clinic",
        "Include patient testimonial quotes",
        "Show pricing transparently (EMI options)",
        "Use local language (Hindi/regional + English)",
        "Video: keep under 15 seconds, hook in first 3 seconds",
        "Carousel: before → during → after → testimonial → CTA",
    ],
    "dont": [
        "Never use graphic medical images",
        "Don't make unrealistic claims ('guaranteed results')",
        "Don't use stock photos of foreign clinics",
        "Don't run ads without a clear CTA",
        "Don't target too broadly (waste budget)",
        "Don't ignore Meta's healthcare ad policies",
    ],
    "copy_formula": (
        "Hook (problem) → Solution (treatment) → Proof (result/testimonial) → "
        "CTA (book now) → Urgency (limited slots/offer)"
    ),
}

# Meta campaign funnel structure
CAMPAIGN_FUNNEL = {
    "top_of_funnel": {
        "objective": "REACH",
        "targeting": "broad_interests",
        "budget_pct": 0.20,
        "purpose": "Build awareness in the local area",
        "creative": "Educational content, doctor intro videos",
        "kpi": "CPM, reach, video views",
    },
    "middle_of_funnel": {
        "objective": "TRAFFIC",
        "targeting": "interest_based",
        "budget_pct": 0.30,
        "purpose": "Drive website visits and WhatsApp messages",
        "creative": "Before/after, treatment explainers, offers",
        "kpi": "CPC, CTR, landing page views",
    },
    "bottom_of_funnel": {
        "objective": "CONVERSIONS",
        "targeting": "retargeting + lookalikes",
        "budget_pct": 0.40,
        "purpose": "Convert visitors into booked appointments",
        "creative": "Testimonials, limited-time offers, call-to-action",
        "kpi": "Cost per lead, cost per booking, ROAS",
    },
    "retargeting": {
        "objective": "CONVERSIONS",
        "targeting": "website_visitors_7d + engaged_users",
        "budget_pct": 0.10,
        "purpose": "Re-engage people who showed interest but didn't book",
        "creative": "Reminder ads, special offer, social proof",
        "kpi": "ROAS, cost per conversion",
    },
}


class MetaAdsBrain:
    """Master brain for Meta Ads (Facebook + Instagram).

    Unlike Google where patients search for treatment,
    Meta shows ads to people who MIGHT need treatment.
    Different strategy entirely.
    """

    def recommend_campaign_structure(
        self,
        specialty: str,
        city: str,
        clinic_name: str,
        services: list[str],
        monthly_budget: float,
    ) -> dict:
        """Recommend Meta Ads campaign structure for a clinic."""
        daily_budget = round(monthly_budget / 30.4)

        campaigns = []
        for stage, config in CAMPAIGN_FUNNEL.items():
            stage_budget = round(daily_budget * config["budget_pct"])

            campaigns.append({
                "stage": stage,
                "objective": config["objective"],
                "daily_budget_inr": max(stage_budget, 100),
                "targeting_strategy": config["targeting"],
                "purpose": config["purpose"],
                "creative_type": config["creative"],
                "kpi": config["kpi"],
            })

        return {
            "clinic": clinic_name,
            "city": city,
            "specialty": specialty,
            "total_daily_budget": daily_budget,
            "campaigns": campaigns,
            "creative_guidelines": CREATIVE_RULES,
            "audience_recommendations": self._get_audiences_for_services(services),
        }

    def get_creative_brief(self, treatment: str, city: str) -> dict:
        """Generate a creative brief for a specific treatment ad."""
        treatment_lower = treatment.lower()

        audience = None
        for key, aud in TREATMENT_AUDIENCES.items():
            if any(word in treatment_lower for word in key.split("_")):
                audience = aud
                break

        if not audience:
            audience = TREATMENT_AUDIENCES.get("skin_treatment")  # Default

        return {
            "treatment": treatment,
            "city": city,
            "target_age": audience["age_range"],
            "ad_format": audience["ad_format"],
            "creative_angle": audience["creative_angle"],
            "cta": audience["cta"],
            "copy_formula": CREATIVE_RULES["copy_formula"],
            "do_rules": CREATIVE_RULES["do"],
            "dont_rules": CREATIVE_RULES["dont"],
            "headline_suggestions": [
                f"Transform Your {treatment} — {city}",
                f"Why 1000+ Patients Trust Us for {treatment}",
                f"{treatment} — Results You'll Love",
            ],
        }

    def _get_audiences_for_services(self, services: list[str]) -> list[dict]:
        """Map clinic services to Meta audience recommendations."""
        audiences = []
        for service in services:
            service_lower = service.lower()
            for key, aud in TREATMENT_AUDIENCES.items():
                if any(word in service_lower for word in key.split("_")):
                    audiences.append({
                        "service": service,
                        "template": key,
                        "age_range": aud["age_range"],
                        "interests": aud["interests"],
                        "ad_format": aud["ad_format"],
                    })
                    break
        return audiences
