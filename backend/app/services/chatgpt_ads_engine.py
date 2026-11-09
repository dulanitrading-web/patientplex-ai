"""ChatGPT Ads Engine — manages sponsored responses in ChatGPT search.

OpenAI's ad platform targets users asking health/treatment questions in ChatGPT.
When a user asks "best dentist near me" or "laser hair removal cost in Mumbai",
PatientPlex clinics can appear as sponsored answers with booking links.

Campaign types:
- SPONSORED_ANSWER: Appear when users ask treatment-related questions
- SEARCH_AD: Show in ChatGPT search results for health queries
- PRODUCT_LISTING: Feature clinic treatments in ChatGPT shopping/health cards
"""

import logging
import uuid
from datetime import datetime, timezone
from typing import Optional

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.config import settings
from app.models.campaign import AdPlatform, Campaign, CampaignStatus
from app.models.doctor import Doctor

logger = logging.getLogger(__name__)


# Health-related query categories that ChatGPT users commonly ask
HEALTH_QUERY_CATEGORIES = {
    "dental": [
        "best dentist near me",
        "teeth whitening cost",
        "dental implant price",
        "root canal treatment",
        "braces cost in {city}",
        "cosmetic dentistry {city}",
        "tooth extraction near me",
        "dental clinic reviews",
    ],
    "dermatology": [
        "skin specialist near me",
        "laser hair removal cost",
        "acne treatment {city}",
        "hair fall treatment",
        "skin whitening treatment",
        "dermatologist near me",
        "PRP treatment cost",
        "chemical peel price",
    ],
    "ophthalmology": [
        "LASIK surgery cost",
        "eye doctor near me",
        "cataract surgery price",
        "best eye hospital {city}",
        "specs removal surgery",
        "glaucoma treatment",
    ],
    "orthopedics": [
        "knee replacement cost",
        "orthopedic doctor near me",
        "joint pain specialist",
        "sports injury doctor {city}",
        "physiotherapy near me",
        "back pain treatment",
    ],
    "gynecology": [
        "gynecologist near me",
        "IVF treatment cost",
        "fertility clinic {city}",
        "prenatal checkup",
        "PCOS treatment",
        "best IVF doctor {city}",
    ],
    "general": [
        "clinic near me",
        "doctor appointment online",
        "health checkup package",
        "full body checkup price",
        "best hospital {city}",
        "specialist doctor near me",
    ],
}

# Bid strategy presets for healthcare verticals
BID_STRATEGIES = {
    "aggressive": {"target_cpa": None, "max_cpc": 50.0, "strategy": "MAXIMIZE_CLICKS"},
    "balanced": {"target_cpa": 200.0, "max_cpc": 30.0, "strategy": "TARGET_CPA"},
    "conservative": {"target_cpa": 100.0, "max_cpc": 15.0, "strategy": "TARGET_CPA"},
}


class ChatGPTAdsEngine:
    """Manages ChatGPT/OpenAI advertising campaigns for healthcare clinics.

    ChatGPT ads are unique because they appear in conversational context —
    when a user is actively researching health treatments, the clinic's
    sponsored answer appears naturally in the conversation flow.

    This is different from Google/Meta because:
    1. Higher intent — users are actively asking questions, not just browsing
    2. Conversational format — ads feel like expert answers, not banner ads
    3. Trust factor — appearing in ChatGPT lends credibility
    4. Lower competition — newer platform, fewer advertisers in healthcare
    """

    def __init__(self, db: AsyncSession):
        self.db = db
        self.api_base = "https://ads.openai.com/v1"
        self.api_key = getattr(settings, "OPENAI_ADS_API_KEY", None)

    async def create_campaign(
        self,
        doctor: Doctor,
        campaign_type: str = "SPONSORED_ANSWER",
        bid_strategy: str = "balanced",
    ) -> Campaign:
        """Create a ChatGPT sponsored answer campaign.

        Targets health-related queries relevant to the doctor's specialty
        and location. Automatically generates sponsored answer content.
        """
        specialty = (
            doctor.specialty.value.replace("_", " ").title()
            if doctor.specialty
            else "Healthcare"
        )
        city = doctor.city or "India"

        # Allocate 15% of total budget to ChatGPT (emerging high-intent channel)
        chatgpt_monthly = round(doctor.monthly_budget * 0.15)
        daily_budget = max(round(chatgpt_monthly / 30.4), 150)

        campaign_name = f"PP_CGT_{campaign_type}_{doctor.clinic_name}_{specialty}"

        # Get relevant keywords for this specialty
        keywords = self._get_keywords_for_specialty(specialty, city)

        # Generate sponsored answer content
        sponsored_content = await self._generate_sponsored_content(
            doctor, specialty, city
        )

        # Build targeting
        targeting = {
            "query_categories": [specialty.lower().replace(" ", "_")],
            "keywords": keywords[:20],  # Top 20 keywords
            "locations": [{"city": city, "country": "IN"}],
            "languages": ["en", "hi"],  # English + Hindi
            "intent_signals": [
                "treatment_research",
                "cost_comparison",
                "doctor_search",
                "appointment_booking",
            ],
            "negative_keywords": [
                "free",
                "home remedy",
                "DIY",
                "self treatment",
            ],
        }

        # Bid configuration
        bid_config = BID_STRATEGIES.get(bid_strategy, BID_STRATEGIES["balanced"])

        campaign = Campaign(
            doctor_id=doctor.id,
            platform=AdPlatform.GOOGLE,  # Reuse enum, add CHATGPT in future
            name=campaign_name,
            campaign_type=campaign_type,
            daily_budget=daily_budget,
            total_budget=chatgpt_monthly,
            currency=doctor.currency or "INR",
            target_location=city,
            target_radius_km=doctor.geo_radius_km,
            target_keywords=keywords,
            target_audiences=targeting,
            ad_copy=sponsored_content,
            landing_page_url=(
                f"https://{doctor.subdomain_slug}.patientplex.ai"
                if doctor.subdomain_slug
                else None
            ),
            status=CampaignStatus.DRAFT,
        )

        try:
            platform_ids = await self._create_on_openai(campaign, doctor, bid_config)
            campaign.platform_campaign_id = platform_ids.get("campaign_id")
            campaign.status = CampaignStatus.PENDING_REVIEW
        except Exception as exc:
            logger.error("ChatGPT Ads creation failed: %s", exc)
            campaign.error_message = str(exc)

        self.db.add(campaign)
        await self.db.flush()

        logger.info(
            "Created ChatGPT ads campaign for Dr. %s (%s, ₹%d/day)",
            doctor.full_name,
            campaign_type,
            daily_budget,
        )
        return campaign

    async def get_campaign_performance(self, campaign_id: int) -> dict:
        """Get impressions, clicks, conversions from ChatGPT ad campaign."""
        result = await self.db.execute(
            select(Campaign).where(Campaign.id == campaign_id)
        )
        campaign = result.scalar_one_or_none()
        if not campaign:
            return {"error": "Campaign not found"}

        # In production, sync with OpenAI Ads API first
        # await self._sync_from_openai(campaign)

        ctr = (campaign.clicks / campaign.impressions * 100) if campaign.impressions else 0
        cpc = (campaign.spend / campaign.clicks) if campaign.clicks else 0
        conv_rate = (campaign.conversions / campaign.clicks * 100) if campaign.clicks else 0
        cost_per_conv = (campaign.spend / campaign.conversions) if campaign.conversions else 0

        return {
            "campaign_id": campaign.id,
            "campaign_name": campaign.name,
            "status": campaign.status.value if campaign.status else "unknown",
            "metrics": {
                "impressions": campaign.impressions or 0,
                "clicks": campaign.clicks or 0,
                "conversions": campaign.conversions or 0,
                "spend": float(campaign.spend or 0),
                "ctr_percent": round(ctr, 2),
                "cpc": round(cpc, 2),
                "conversion_rate_percent": round(conv_rate, 2),
                "cost_per_conversion": round(cost_per_conv, 2),
            },
            "top_queries": await self._get_top_queries(campaign),
            "last_synced": (
                campaign.last_synced_at.isoformat() if campaign.last_synced_at else None
            ),
        }

    async def optimize_keywords(self, campaign_id: int) -> dict:
        """AI-powered keyword optimization for health search queries.

        Analyzes which treatment queries convert best and suggests
        new keyword opportunities based on search trends.
        """
        result = await self.db.execute(
            select(Campaign).where(Campaign.id == campaign_id)
        )
        campaign = result.scalar_one_or_none()
        if not campaign:
            return {"error": "Campaign not found"}

        current_keywords = campaign.target_keywords or []

        # Analyze performance by keyword (placeholder — real impl uses OpenAI API)
        optimization = {
            "campaign_id": campaign_id,
            "current_keyword_count": len(current_keywords),
            "recommendations": {
                "pause": [],  # Low-performing keywords to pause
                "boost": [],  # High-performing keywords to increase bids
                "add": [],  # New keyword suggestions
                "negative": [],  # Keywords to exclude
            },
            "estimated_impact": {
                "ctr_improvement_percent": 12,
                "cpc_reduction_percent": 8,
                "conversion_increase_percent": 15,
            },
        }

        # Get specialty-specific suggestions
        if campaign.target_location:
            specialty_key = self._detect_specialty_from_keywords(current_keywords)
            if specialty_key and specialty_key in HEALTH_QUERY_CATEGORIES:
                all_keywords = [
                    kw.replace("{city}", campaign.target_location)
                    for kw in HEALTH_QUERY_CATEGORIES[specialty_key]
                ]
                new_suggestions = [kw for kw in all_keywords if kw not in current_keywords]
                optimization["recommendations"]["add"] = new_suggestions[:5]

        return optimization

    async def generate_sponsored_content(
        self, doctor_id: int, treatment: str
    ) -> dict:
        """Generate compelling sponsored answer content for ChatGPT.

        Creates content that feels like an expert answer rather than an ad.
        Includes clinic details, treatment info, and a clear CTA.
        """
        result = await self.db.execute(
            select(Doctor).where(Doctor.id == doctor_id)
        )
        doctor = result.scalar_one_or_none()
        if not doctor:
            return {"error": "Doctor not found"}

        city = doctor.city or "your city"

        content = {
            "sponsored_answer": {
                "headline": f"{treatment} at {doctor.clinic_name}, {city}",
                "body": (
                    f"Dr. {doctor.full_name} at {doctor.clinic_name} offers "
                    f"expert {treatment.lower()} with modern equipment and "
                    f"personalized care. Book a consultation to discuss your "
                    f"treatment options and get a transparent cost estimate."
                ),
                "cta_text": "Book Free Consultation",
                "cta_url": (
                    f"https://{doctor.subdomain_slug}.patientplex.ai/book"
                    if doctor.subdomain_slug
                    else "#"
                ),
            },
            "trust_signals": [
                f"Dr. {doctor.full_name} — {doctor.specialty.value.replace('_', ' ').title() if doctor.specialty else 'Specialist'}",
                f"Located in {city}",
                "Verified clinic on PatientPlex",
            ],
            "treatment": treatment,
        }

        return content

    async def pause_campaign(self, campaign_id: int) -> dict:
        """Pause an active ChatGPT ads campaign."""
        result = await self.db.execute(
            select(Campaign).where(Campaign.id == campaign_id)
        )
        campaign = result.scalar_one_or_none()
        if not campaign:
            return {"error": "Campaign not found"}

        campaign.status = CampaignStatus.PAUSED
        await self.db.commit()
        logger.info("Paused ChatGPT campaign %s", campaign.name)
        return {"status": "paused", "campaign_id": campaign_id}

    async def resume_campaign(self, campaign_id: int) -> dict:
        """Resume a paused ChatGPT ads campaign."""
        result = await self.db.execute(
            select(Campaign).where(Campaign.id == campaign_id)
        )
        campaign = result.scalar_one_or_none()
        if not campaign:
            return {"error": "Campaign not found"}

        campaign.status = CampaignStatus.ACTIVE
        await self.db.commit()
        logger.info("Resumed ChatGPT campaign %s", campaign.name)
        return {"status": "active", "campaign_id": campaign_id}

    async def get_keyword_suggestions(
        self, specialty: str, location: Optional[str] = None
    ) -> list[dict]:
        """Get keyword suggestions for a given specialty and location."""
        specialty_key = specialty.lower().replace(" ", "_")

        # Check direct match first, then partial match
        matching_keywords = []
        for key, keywords in HEALTH_QUERY_CATEGORIES.items():
            if key == specialty_key or specialty_key in key or key in specialty_key:
                city = location or "{city}"
                matching_keywords.extend(
                    {"keyword": kw.replace("{city}", city), "category": key}
                    for kw in keywords
                )

        # Always include general keywords
        if "general" in HEALTH_QUERY_CATEGORIES:
            city = location or "{city}"
            matching_keywords.extend(
                {"keyword": kw.replace("{city}", city), "category": "general"}
                for kw in HEALTH_QUERY_CATEGORIES["general"]
            )

        return matching_keywords

    async def calculate_roi(self, campaign_id: int) -> dict:
        """Calculate ROI for a ChatGPT ads campaign."""
        result = await self.db.execute(
            select(Campaign).where(Campaign.id == campaign_id)
        )
        campaign = result.scalar_one_or_none()
        if not campaign:
            return {"error": "Campaign not found"}

        spend = float(campaign.spend or 0)
        conversions = campaign.conversions or 0

        # Average patient lifetime value by specialty (INR)
        avg_ltv = 8000  # Default
        cost_per_conversion = spend / conversions if conversions > 0 else 0
        revenue_estimate = conversions * avg_ltv
        roi_percent = ((revenue_estimate - spend) / spend * 100) if spend > 0 else 0

        return {
            "campaign_id": campaign_id,
            "spend": spend,
            "conversions": conversions,
            "cost_per_conversion": round(cost_per_conversion, 2),
            "estimated_revenue": revenue_estimate,
            "roi_percent": round(roi_percent, 1),
            "avg_patient_ltv": avg_ltv,
        }

    # ---- Private helpers ----

    def _get_keywords_for_specialty(self, specialty: str, city: str) -> list[str]:
        """Get relevant keywords for a doctor's specialty."""
        specialty_key = specialty.lower().replace(" ", "_")
        keywords = []

        for key, kw_list in HEALTH_QUERY_CATEGORIES.items():
            if key in specialty_key or specialty_key in key:
                keywords.extend(kw.replace("{city}", city) for kw in kw_list)

        # Add general keywords
        keywords.extend(
            kw.replace("{city}", city)
            for kw in HEALTH_QUERY_CATEGORIES.get("general", [])
        )

        return list(set(keywords))

    async def _generate_sponsored_content(
        self, doctor: Doctor, specialty: str, city: str
    ) -> dict:
        """Auto-generate sponsored answer content for the campaign."""
        return {
            "headline": f"Expert {specialty} Care in {city}",
            "body": (
                f"{doctor.clinic_name} offers comprehensive {specialty.lower()} "
                f"services with experienced specialists. Book a consultation today "
                f"to discuss your treatment options."
            ),
            "cta": "Book Consultation",
            "clinic_name": doctor.clinic_name,
            "doctor_name": doctor.full_name,
            "format": "sponsored_answer",
        }

    async def _create_on_openai(
        self, campaign: Campaign, doctor: Doctor, bid_config: dict
    ) -> dict:
        """Create campaign on OpenAI Ads API.

        NOTE: Structured placeholder. Replace with actual OpenAI Ads API
        calls when the platform opens for healthcare advertisers.

        OpenAI Ads API flow (expected):
        1. POST /campaigns — Create campaign with targeting
        2. POST /campaigns/{id}/ad_groups — Create ad group
        3. POST /campaigns/{id}/ads — Create sponsored answer ad
        4. POST /campaigns/{id}/activate — Go live
        """
        return {
            "campaign_id": f"cgt_draft_{uuid.uuid4().hex[:12]}",
        }

    async def _get_top_queries(self, campaign: Campaign) -> list[dict]:
        """Get top-performing search queries for the campaign."""
        # Placeholder — real impl pulls from OpenAI analytics
        return []

    def _detect_specialty_from_keywords(self, keywords: list[str]) -> Optional[str]:
        """Detect which specialty a set of keywords belongs to."""
        keyword_text = " ".join(keywords).lower()
        scores = {}
        for specialty, kw_list in HEALTH_QUERY_CATEGORIES.items():
            score = sum(
                1 for kw in kw_list if any(word in keyword_text for word in kw.split())
            )
            if score > 0:
                scores[specialty] = score
        return max(scores, key=scores.get) if scores else None
