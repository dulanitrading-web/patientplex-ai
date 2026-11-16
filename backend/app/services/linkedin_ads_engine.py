"""LinkedIn Ads campaign engine for specialist referral and B2B positioning.

LinkedIn is used differently from Google/Meta in healthcare:
- Target referring doctors (GP → Specialist referral pipeline)
- Thought leadership positioning (specialist builds credibility)
- B2B clinic partnerships
- Recruiting associate doctors
"""

import logging
import uuid
from datetime import datetime, timezone

from sqlalchemy.ext.asyncio import AsyncSession

from app.core.config import settings
from app.models.campaign import AdPlatform, Campaign, CampaignStatus
from app.models.doctor import Doctor

logger = logging.getLogger(__name__)


# LinkedIn targeting for healthcare B2B
HEALTHCARE_TARGETING = {
    "industries": [
        {"id": 14, "name": "Hospital & Health Care"},
        {"id": 15, "name": "Medical Devices"},
        {"id": 16, "name": "Medical Practice"},
        {"id": 17, "name": "Pharmaceuticals"},
    ],
    "job_titles": [
        "General Physician",
        "Family Doctor",
        "Medical Director",
        "Hospital Administrator",
        "Clinic Manager",
        "Healthcare Consultant",
    ],
    "job_functions": [
        {"id": 12, "name": "Healthcare Services"},
        {"id": 1, "name": "Administrative"},
    ],
    "seniority": [
        {"id": 4, "name": "Manager"},
        {"id": 5, "name": "Director"},
        {"id": 6, "name": "VP"},
        {"id": 8, "name": "Owner"},
    ],
}


class LinkedInAdsEngine:
    """Manages LinkedIn Marketing campaigns for healthcare provider positioning.

    Campaign types:
    - REFERRAL: Target GPs and other doctors who might refer patients
    - THOUGHT_LEADERSHIP: Promote the doctor's expertise articles/posts
    - CLINIC_BRANDING: Build awareness of the clinic among healthcare professionals
    """

    def __init__(self, db: AsyncSession):
        self.db = db
        self.api_base = "https://api.linkedin.com/v2"

    async def create_referral_campaign(self, doctor: Doctor) -> Campaign:
        """Create a LinkedIn campaign targeting referring doctors.

        For example, a specialist (orthopedic surgeon) targets GPs in their city
        who might refer patients needing surgery.
        """
        specialty = doctor.specialty.value.replace("_", " ").title() if doctor.specialty else "Specialist"
        city = doctor.city or "India"

        # Allocate 10% of total budget to LinkedIn
        linkedin_monthly = round(doctor.monthly_budget * 0.10)
        daily_budget = max(round(linkedin_monthly / 30.4), 200)  # Min ₹200/day on LinkedIn

        campaign_name = f"CC_LI_Referral_{doctor.clinic_name}_{specialty}"

        # Build ad copy for referring doctors
        ad_content = {
            "intro_text": (
                f"Looking for a trusted {specialty.lower()} for your patients in {city}? "
                f"Dr. {doctor.full_name} at {doctor.clinic_name} accepts referrals and "
                f"provides timely updates on patient progress."
            ),
            "headline": f"{specialty} Referrals — {city}",
            "description": f"{doctor.clinic_name} · Accepting new referrals · Same-week appointments",
            "cta": "LEARN_MORE",
        }

        # Targeting: healthcare professionals in the doctor's city
        targeting = {
            "locations": [{"name": city}],
            "industries": HEALTHCARE_TARGETING["industries"],
            "job_titles": HEALTHCARE_TARGETING["job_titles"],
            "seniority": HEALTHCARE_TARGETING["seniority"],
            "and_conditions": [
                {"field": "industry", "values": ["Hospital & Health Care", "Medical Practice"]},
            ],
        }

        campaign = Campaign(
            doctor_id=doctor.id,
            platform=AdPlatform.LINKEDIN,
            name=campaign_name,
            campaign_type="REFERRAL",
            daily_budget=daily_budget,
            total_budget=linkedin_monthly,
            currency=doctor.currency or "INR",
            target_location=city,
            target_radius_km=doctor.geo_radius_km,
            target_audiences=targeting,
            ad_copy=ad_content,
            landing_page_url=(
                f"https://{doctor.subdomain_slug}.patientplex.ai"
                if doctor.subdomain_slug else None
            ),
            status=CampaignStatus.DRAFT,
        )

        try:
            platform_ids = await self._create_on_linkedin(campaign, doctor)
            campaign.platform_campaign_id = platform_ids.get("campaign_id")
            campaign.status = CampaignStatus.PENDING_REVIEW
        except Exception as exc:
            logger.error("LinkedIn Ads creation failed: %s", exc)
            campaign.error_message = str(exc)

        self.db.add(campaign)
        await self.db.flush()

        logger.info("Created LinkedIn referral campaign for Dr. %s (₹%d/day)", doctor.full_name, daily_budget)
        return campaign

    async def create_thought_leadership_campaign(self, doctor: Doctor, article_url: str) -> Campaign:
        """Promote a doctor's article or post to build credibility.

        Useful for specialists who publish case studies, research,
        or educational content about their specialty.
        """
        specialty = doctor.specialty.value.replace("_", " ").title() if doctor.specialty else "Medicine"
        campaign_name = f"CC_LI_Thought_{doctor.clinic_name}"

        ad_content = {
            "intro_text": (
                f"Dr. {doctor.full_name} shares insights on the latest in {specialty.lower()} practice."
            ),
            "headline": f"Expert Insights: {specialty}",
            "description": f"By Dr. {doctor.full_name}, {doctor.clinic_name}",
            "cta": "LEARN_MORE",
            "article_url": article_url,
        }

        daily_budget = max(round(doctor.monthly_budget * 0.05 / 30.4), 150)

        campaign = Campaign(
            doctor_id=doctor.id,
            platform=AdPlatform.LINKEDIN,
            name=campaign_name,
            campaign_type="THOUGHT_LEADERSHIP",
            daily_budget=daily_budget,
            total_budget=round(daily_budget * 30.4),
            currency=doctor.currency or "INR",
            target_location=doctor.city or "",
            target_audiences={"industries": HEALTHCARE_TARGETING["industries"]},
            ad_copy=ad_content,
            landing_page_url=article_url,
            status=CampaignStatus.DRAFT,
        )

        self.db.add(campaign)
        await self.db.flush()
        return campaign

    async def _create_on_linkedin(self, campaign: Campaign, doctor: Doctor) -> dict:
        """Create campaign on LinkedIn Marketing API.

        LinkedIn API flow:
        1. POST /adAccounts/{id}/campaigns — Create campaign
        2. POST /adAccounts/{id}/creatives — Create creative
        3. Set targeting criteria
        4. Associate creative with campaign

        NOTE: Structured placeholder. Replace with actual LinkedIn Marketing API
        calls when developer access is granted.
        """

        # ---------- Campaign Creation ----------
        # campaign_data = {
        #     "account": f"urn:li:sponsoredAccount:{ad_account_id}",
        #     "name": campaign.name,
        #     "objectiveType": "WEBSITE_VISITS",
        #     "type": "SPONSORED_UPDATES",
        #     "status": "PAUSED",
        #     "costType": "CPC",
        #     "dailyBudget": {"amount": str(campaign.daily_budget), "currencyCode": "INR"},
        #     "locale": {"country": "IN", "language": "en"},
        # }

        # ---------- Targeting ----------
        # targeting_criteria = {
        #     "include": {
        #         "and": [
        #             {"or": {"urn:li:adTargetingFacet:locations": [...]}},
        #             {"or": {"urn:li:adTargetingFacet:industries": [...]}},
        #             {"or": {"urn:li:adTargetingFacet:seniorities": [...]}},
        #         ]
        #     }
        # }

        # ---------- Creative ----------
        # creative_data = {
        #     "campaign": campaign_urn,
        #     "type": "SPONSORED_STATUS_UPDATE",
        #     "reference": share_urn,
        #     "status": "ACTIVE",
        # }

        return {
            "campaign_id": f"li_draft_{uuid.uuid4().hex[:12]}",
        }

    async def sync_performance(self, campaign: Campaign) -> dict:
        """Sync LinkedIn campaign analytics."""
        # GET /adAnalytics?q=analytics&campaigns=urn:li:sponsoredCampaign:{id}
        #     &dateRange.start.year=2026&dateRange.start.month=10&dateRange.start.day=1
        #     &timeGranularity=ALL&fields=impressions,clicks,costInLocalCurrency,...

        campaign.last_synced_at = datetime.now(timezone.utc)
        await self.db.commit()
        return {
            "impressions": campaign.impressions,
            "clicks": campaign.clicks,
            "spend": campaign.spend,
        }

    # ------------------------------------------------------------------
    # WRITE API — Edit/update LinkedIn Ads campaigns
    # ------------------------------------------------------------------

    async def update_campaign_status(self, campaign: Campaign, new_status: str) -> dict:
        """Enable or pause a LinkedIn campaign.

        new_status: "ACTIVE" or "PAUSED"
        LinkedIn API: PATCH /adAccounts/{id}/campaigns/{campaignId}
        """
        campaign.status = CampaignStatus.ACTIVE if new_status == "ACTIVE" else CampaignStatus.PAUSED
        await self.db.commit()

        if campaign.platform_campaign_id:
            # When LinkedIn Marketing API access is granted:
            # PATCH {api_base}/adCampaignsV2/{campaign_urn}
            # body: {"patch": {"$set": {"status": new_status}}}
            logger.info("LinkedIn campaign %s set to %s (local)", campaign.name, new_status)

        return {"status": "success", "new_status": new_status}

    async def update_budget(self, campaign: Campaign, new_daily_inr: float) -> dict:
        """Update LinkedIn campaign daily budget.

        LinkedIn uses micros (1/10000 of currency unit).
        ₹500/day → {"amount": "5000000", "currencyCode": "INR"}
        """
        campaign.daily_budget = round(new_daily_inr)
        campaign.total_budget = round(new_daily_inr * 30.4)
        await self.db.commit()

        if campaign.platform_campaign_id:
            # PATCH /adCampaignsV2/{urn}
            # body: {"patch": {"$set": {"dailyBudget": {"amount": str(int(new_daily_inr*10000)), "currencyCode": "INR"}}}}
            logger.info("LinkedIn budget updated to ₹%s/day (local)", new_daily_inr)

        return {"status": "success", "new_daily_budget_inr": new_daily_inr}

    async def update_targeting(self, campaign: Campaign, targeting_updates: dict) -> dict:
        """Update LinkedIn audience targeting.

        targeting_updates can include: locations, industries, job_titles, seniority, etc.
        """
        current = campaign.target_audiences or {}
        current.update(targeting_updates)
        campaign.target_audiences = current
        await self.db.commit()

        return {"status": "success", "targeting": current}

    async def update_ad_copy(self, campaign: Campaign, intro_text: str, headline: str, description: str) -> dict:
        """Update LinkedIn Sponsored Content ad copy.

        LinkedIn ad components:
        - intro_text: Text above the image/card (max 600 chars)
        - headline: Bold headline on the card (max 200 chars)
        - description: Subtitle on the card (max 300 chars)
        """
        if len(intro_text) > 600:
            return {"status": "error", "message": "Intro text must be ≤600 chars"}
        if len(headline) > 200:
            return {"status": "error", "message": "Headline must be ≤200 chars"}

        campaign.ad_copy = {
            **(campaign.ad_copy or {}),
            "intro_text": intro_text,
            "headline": headline,
            "description": description,
        }
        await self.db.commit()

        return {"status": "success", "ad_copy": campaign.ad_copy}

    async def get_demographics_report(self, campaign: Campaign) -> dict:
        """Get audience demographics breakdown for a LinkedIn campaign.

        Shows which job titles, industries, and seniority levels
        are engaging most — critical for B2B healthcare referral targeting.
        """
        # When API access available:
        # GET /adAnalytics?q=analytics&campaigns=urn:li:sponsoredCampaign:{id}
        #     &pivot=MEMBER_JOB_TITLE&dateRange=...

        return {
            "campaign_id": str(campaign.id),
            "note": "Demographics report available when LinkedIn API access is granted",
            "targeting_active": campaign.target_audiences or {},
        }
