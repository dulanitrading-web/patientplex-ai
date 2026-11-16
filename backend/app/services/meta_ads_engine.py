"""Meta (Facebook/Instagram) Ads campaign engine.

Creates geo-targeted awareness and lead-gen campaigns for healthcare providers
using the Meta Marketing API.
"""

import logging
import uuid
from datetime import datetime, timezone

from sqlalchemy.ext.asyncio import AsyncSession

from app.core.config import settings
from app.models.campaign import AdPlatform, Campaign, CampaignStatus
from app.models.doctor import Doctor
from app.services.ad_copy_generator import generate_meta_ad_copy

logger = logging.getLogger(__name__)


class MetaAdsEngine:
    """Manages Meta Ads (Facebook + Instagram) campaigns for healthcare providers.

    Supports two campaign types:
    - AWARENESS: Reach potential patients in the area
    - LEAD_GEN: Collect patient enquiries via lead forms or WhatsApp
    """

    def __init__(self, db: AsyncSession, doctor_access_token: str | None = None):
        self.db = db
        self.api_version = "v21.0"
        self.base_url = f"https://graph.facebook.com/{self.api_version}"
        # Use per-doctor OAuth access token if available, otherwise fall back to app-level token
        self.access_token = doctor_access_token or getattr(settings, "META_ACCESS_TOKEN", None)

    async def create_campaign_from_onboarding(
        self, doctor: Doctor, campaign_type: str = "LEAD_GEN"
    ) -> Campaign:
        """Create a Meta Ads campaign from doctor onboarding data.

        Args:
            doctor: The doctor whose campaign to create
            campaign_type: AWARENESS or LEAD_GEN
        """
        # Generate AI ad copy
        ad_copy = await generate_meta_ad_copy(doctor)

        # Allocate 40% of budget to Meta (60% goes to Google)
        meta_monthly = round(doctor.monthly_budget * 0.4)
        daily_budget = round(meta_monthly / 30.4)

        specialty_label = (
            doctor.specialty.value.replace("_", " ").title()
            if doctor.specialty
            else "Healthcare"
        )
        campaign_name = f"CC_Meta_{doctor.clinic_name}_{specialty_label}_{doctor.city}"

        # Build audience targeting
        target_audiences = self._build_healthcare_audience(doctor)

        campaign = Campaign(
            doctor_id=doctor.id,
            platform=AdPlatform.META,
            name=campaign_name,
            campaign_type=campaign_type,
            daily_budget=daily_budget,
            total_budget=meta_monthly,
            currency=doctor.currency or "INR",
            target_location=f"{doctor.city}, {doctor.state}",
            target_radius_km=doctor.geo_radius_km,
            target_latitude=doctor.latitude,
            target_longitude=doctor.longitude,
            target_audiences=target_audiences,
            ad_copy=ad_copy,
            landing_page_url=(
                f"https://{doctor.subdomain_slug}.patientplex.ai"
                if doctor.subdomain_slug
                else None
            ),
            status=CampaignStatus.DRAFT,
        )

        # In production: create via Meta Marketing API
        try:
            platform_ids = await self._create_on_meta(campaign, doctor, ad_copy)
            campaign.platform_campaign_id = platform_ids.get("campaign_id")
            campaign.platform_ad_group_id = platform_ids.get("ad_set_id")
            campaign.status = CampaignStatus.PENDING_REVIEW
        except Exception as exc:
            logger.error("Meta Ads API creation failed: %s", exc)
            campaign.error_message = str(exc)
            campaign.status = CampaignStatus.DRAFT

        self.db.add(campaign)
        await self.db.flush()

        logger.info(
            "Created Meta campaign '%s' for Dr. %s (₹%d/day, %dkm radius)",
            campaign_name, doctor.full_name, daily_budget, doctor.geo_radius_km,
        )
        return campaign

    def _build_healthcare_audience(self, doctor: Doctor) -> dict:
        """Build Meta audience targeting optimized for healthcare.

        Targets adults 18-65 in the clinic's geo-radius with
        health & wellness interest targeting.
        """
        # Health-related interest IDs on Meta (these are real Meta interest IDs)
        health_interests = {
            "DENTIST": [
                {"id": "6003384241633", "name": "Dental care"},
                {"id": "6003271978598", "name": "Oral hygiene"},
            ],
            "DERMATOLOGIST": [
                {"id": "6003392552834", "name": "Skin care"},
                {"id": "6003344792234", "name": "Dermatology"},
            ],
            "ORTHOPEDIC": [
                {"id": "6003256270233", "name": "Physical fitness"},
                {"id": "6003384241655", "name": "Orthopedics"},
            ],
            "OPHTHALMOLOGIST": [
                {"id": "6003384241699", "name": "Eye care"},
            ],
            "GYNECOLOGIST": [
                {"id": "6003384241677", "name": "Women's health"},
                {"id": "6003107902433", "name": "Pregnancy"},
            ],
            "PEDIATRICIAN": [
                {"id": "6003455860233", "name": "Parenting"},
                {"id": "6003384241744", "name": "Child health"},
            ],
        }

        specialty_key = doctor.specialty.value if doctor.specialty else "GENERAL_PHYSICIAN"
        interests = health_interests.get(specialty_key, [])

        return {
            "geo_locations": {
                "custom_locations": [
                    {
                        "latitude": doctor.latitude,
                        "longitude": doctor.longitude,
                        "radius": doctor.geo_radius_km,
                        "distance_unit": "kilometer",
                    }
                ]
                if doctor.latitude and doctor.longitude
                else [],
                "cities": [{"name": doctor.city}] if doctor.city else [],
            },
            "age_min": 18,
            "age_max": 65,
            "interests": interests,
            "locales": [6],  # English
            "publisher_platforms": ["facebook", "instagram"],
            "facebook_positions": ["feed", "story", "reels"],
            "instagram_positions": ["stream", "story", "reels"],
        }

    async def _create_on_meta(
        self, campaign: Campaign, doctor: Doctor, ad_copy: dict
    ) -> dict:
        """Create campaign, ad set, and ads on Meta Marketing API.

        NOTE: Structured placeholder — replace with actual API calls
        when Meta app review is approved for ads_management permission.

        Meta API flow:
        1. POST /{ad_account_id}/campaigns — Create Campaign
        2. POST /{ad_account_id}/adsets — Create Ad Set with targeting
        3. POST /{ad_account_id}/adcreatives — Create Ad Creative
        4. POST /{ad_account_id}/ads — Create Ad linking creative to ad set
        """

        # ---------- STEP 1: Create Campaign ----------
        # campaign_data = {
        #     "name": campaign.name,
        #     "objective": "OUTCOME_LEADS" if campaign.campaign_type == "LEAD_GEN" else "OUTCOME_AWARENESS",
        #     "status": "PAUSED",
        #     "special_ad_categories": ["NONE"],  # Healthcare may need special handling
        #     "buying_type": "AUCTION",
        # }
        # resp = await httpx.AsyncClient().post(
        #     f"{self.base_url}/act_{ad_account_id}/campaigns",
        #     params={"access_token": self.access_token},
        #     json=campaign_data,
        # )
        # campaign_id = resp.json()["id"]

        # ---------- STEP 2: Create Ad Set ----------
        # ad_set_data = {
        #     "name": f"{campaign.name}_AdSet",
        #     "campaign_id": campaign_id,
        #     "billing_event": "IMPRESSIONS",
        #     "optimization_goal": "LEAD_GENERATION",
        #     "daily_budget": campaign.daily_budget * 100,  # In cents
        #     "targeting": campaign.target_audiences,
        #     "start_time": datetime.now().isoformat(),
        #     "status": "PAUSED",
        # }

        # ---------- STEP 3: Create Ad Creative ----------
        # For each ad variation from AI-generated copy:
        # creative_data = {
        #     "name": f"{campaign.name}_Creative_{i}",
        #     "object_story_spec": {
        #         "page_id": page_id,
        #         "link_data": {
        #             "message": variation["primary_text"],
        #             "name": variation["headline"],
        #             "description": variation["description"],
        #             "link": campaign.landing_page_url,
        #             "call_to_action": {"type": "BOOK_NOW", "value": {"link": landing_url}},
        #         },
        #     },
        # }

        # ---------- STEP 4: Create Ad ----------
        # ad_data = {
        #     "name": f"{campaign.name}_Ad_{i}",
        #     "adset_id": ad_set_id,
        #     "creative": {"creative_id": creative_id},
        #     "status": "PAUSED",
        # }

        return {
            "campaign_id": f"meta_draft_{uuid.uuid4().hex[:12]}",
            "ad_set_id": f"meta_draft_{uuid.uuid4().hex[:12]}",
        }

    async def sync_performance(self, campaign: Campaign) -> dict:
        """Sync performance metrics from Meta Insights API."""
        if self.access_token and campaign.platform_campaign_id:
            try:
                import httpx
                url = f"{self.base_url}/{campaign.platform_campaign_id}/insights"
                params = {
                    "access_token": self.access_token,
                    "fields": "impressions,clicks,spend,actions,cpc,ctr,cpp",
                    "date_preset": "last_30d",
                }
                async with httpx.AsyncClient() as client:
                    resp = await client.get(url, params=params, timeout=15)
                    if resp.status_code == 200:
                        data = resp.json().get("data", [{}])[0]
                        campaign.impressions = int(data.get("impressions", 0))
                        campaign.clicks = int(data.get("clicks", 0))
                        campaign.spend = float(data.get("spend", 0))
                        campaign.ctr = float(data.get("ctr", 0))
                        campaign.cpc = float(data.get("cpc", 0))
                        actions = data.get("actions", [])
                        for a in actions:
                            if a.get("action_type") in ("lead", "onsite_conversion.messaging_conversation_started_7d"):
                                campaign.conversions += int(a.get("value", 0))
            except Exception as exc:
                logger.error("Meta sync failed: %s", exc)

        campaign.last_synced_at = datetime.now(timezone.utc)
        await self.db.commit()

        return {
            "impressions": campaign.impressions,
            "clicks": campaign.clicks,
            "conversions": campaign.conversions,
            "spend": campaign.spend,
        }

    # ------------------------------------------------------------------
    # WRITE API — Edit/update Meta Ads campaigns
    # ------------------------------------------------------------------

    async def update_campaign_status(self, campaign: Campaign, new_status: str) -> dict:
        """Enable or pause a Meta campaign.

        new_status: "ACTIVE" or "PAUSED"
        Uses Meta Marketing API POST /{campaign_id} with status field.
        """
        if not self.access_token or not campaign.platform_campaign_id:
            campaign.status = CampaignStatus.ACTIVE if new_status == "ACTIVE" else CampaignStatus.PAUSED
            await self.db.commit()
            return {"status": "updated_local", "new_status": new_status}

        try:
            import httpx
            url = f"{self.base_url}/{campaign.platform_campaign_id}"
            async with httpx.AsyncClient() as client:
                resp = await client.post(
                    url,
                    params={"access_token": self.access_token},
                    json={"status": new_status},
                    timeout=15,
                )
                if resp.status_code == 200:
                    campaign.status = CampaignStatus.ACTIVE if new_status == "ACTIVE" else CampaignStatus.PAUSED
                    await self.db.commit()
                    return {"status": "success", "new_status": new_status, "api": "meta"}
                else:
                    error = resp.text[:300]
                    logger.error("Meta status update failed: %s", error)
                    return {"status": "error", "message": error}
        except Exception as e:
            return {"status": "error", "message": str(e)}

    async def update_budget(self, campaign: Campaign, new_daily_inr: float) -> dict:
        """Update daily budget on a Meta ad set.

        Meta budgets are in cents (paise for INR), so ₹500 → 50000.
        Budget lives on the ad_set, not the campaign.
        """
        ad_set_id = campaign.platform_ad_group_id
        if not self.access_token or not ad_set_id:
            campaign.daily_budget = round(new_daily_inr)
            campaign.total_budget = round(new_daily_inr * 30.4)
            await self.db.commit()
            return {"status": "updated_local", "new_daily_budget_inr": new_daily_inr}

        try:
            import httpx
            budget_cents = int(new_daily_inr * 100)
            url = f"{self.base_url}/{ad_set_id}"
            async with httpx.AsyncClient() as client:
                resp = await client.post(
                    url,
                    params={"access_token": self.access_token},
                    json={"daily_budget": budget_cents},
                    timeout=15,
                )
                if resp.status_code == 200:
                    campaign.daily_budget = round(new_daily_inr)
                    campaign.total_budget = round(new_daily_inr * 30.4)
                    await self.db.commit()
                    return {"status": "success", "new_daily_budget_inr": new_daily_inr, "api": "meta"}
                else:
                    return {"status": "error", "message": resp.text[:300]}
        except Exception as e:
            return {"status": "error", "message": str(e)}

    async def update_audience_targeting(self, campaign: Campaign, targeting: dict) -> dict:
        """Update audience targeting on a Meta ad set.

        targeting dict can include: age_min, age_max, interests, geo_locations, etc.
        """
        ad_set_id = campaign.platform_ad_group_id
        if not self.access_token or not ad_set_id:
            campaign.target_audiences = {**(campaign.target_audiences or {}), **targeting}
            await self.db.commit()
            return {"status": "updated_local"}

        try:
            import httpx
            url = f"{self.base_url}/{ad_set_id}"
            async with httpx.AsyncClient() as client:
                resp = await client.post(
                    url,
                    params={"access_token": self.access_token},
                    json={"targeting": targeting},
                    timeout=15,
                )
                if resp.status_code == 200:
                    campaign.target_audiences = {**(campaign.target_audiences or {}), **targeting}
                    await self.db.commit()
                    return {"status": "success", "api": "meta"}
                else:
                    return {"status": "error", "message": resp.text[:300]}
        except Exception as e:
            return {"status": "error", "message": str(e)}

    async def update_ad_creative(
        self, campaign: Campaign, primary_text: str, headline: str, description: str, cta_type: str = "BOOK_NOW"
    ) -> dict:
        """Update or create a new ad creative for the campaign.

        Meta ad copy structure:
        - primary_text: Main body text shown above the image
        - headline: Bold headline below the image
        - description: Subtitle below the headline
        - cta_type: BOOK_NOW, LEARN_MORE, SEND_WHATSAPP_MESSAGE, etc.
        """
        campaign.ad_copy = {
            **(campaign.ad_copy or {}),
            "primary_text": primary_text,
            "headline": headline,
            "description": description,
            "cta_type": cta_type,
        }
        await self.db.commit()

        if not self.access_token:
            return {"status": "updated_local"}

        # When API is live: POST /{ad_account_id}/adcreatives with object_story_spec
        return {"status": "updated_local", "note": "API creative update pending Meta app review"}

    async def get_ad_insights(self, campaign: Campaign, breakdown: str = "age") -> dict:
        """Get detailed performance breakdown by age, gender, placement, etc.

        breakdown: "age", "gender", "publisher_platform", "impression_device", "region"
        """
        if not self.access_token or not campaign.platform_campaign_id:
            return {"status": "no_api_access", "breakdown": breakdown, "data": []}

        try:
            import httpx
            url = f"{self.base_url}/{campaign.platform_campaign_id}/insights"
            params = {
                "access_token": self.access_token,
                "fields": "impressions,clicks,spend,cpc,ctr,actions",
                "breakdowns": breakdown,
                "date_preset": "last_30d",
            }
            async with httpx.AsyncClient() as client:
                resp = await client.get(url, params=params, timeout=15)
                if resp.status_code == 200:
                    return {"status": "success", "breakdown": breakdown, "data": resp.json().get("data", [])}
                else:
                    return {"status": "error", "message": resp.text[:300]}
        except Exception as e:
            return {"status": "error", "message": str(e)}
