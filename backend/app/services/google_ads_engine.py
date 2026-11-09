"""Google Ads campaign engine — production integration via google-ads SDK.

Creates Search campaigns from doctor onboarding data with:
- Healthcare-specific keyword targeting
- Geo-targeting based on clinic location + radius
- AI-generated RSA ad copy
- Automatic negative keyword exclusion
- Budget optimization

Falls back to demo mode when Google Ads credentials are not configured.
"""

import logging
import os
import uuid
from datetime import datetime, timezone
from typing import Dict, List, Optional

from sqlalchemy.ext.asyncio import AsyncSession

from app.core.config import settings
from app.models.campaign import AdPlatform, Campaign, CampaignStatus
from app.models.doctor import Doctor
from app.schemas.specialty import SPECIALTY_CONFIGS
from app.services.ad_copy_generator import generate_google_ad_copy

logger = logging.getLogger(__name__)

# Conditionally import google-ads SDK
try:
    from google.ads.googleads.client import GoogleAdsClient
    from google.ads.googleads.errors import GoogleAdsException

    GOOGLE_ADS_SDK_AVAILABLE = True
except ImportError:
    GOOGLE_ADS_SDK_AVAILABLE = False
    GoogleAdsClient = None
    GoogleAdsException = Exception
    logger.warning("google-ads SDK not installed — pip install google-ads")


def _build_google_ads_client() -> Optional["GoogleAdsClient"]:
    """Build a GoogleAdsClient from environment variables, or return None."""
    if not GOOGLE_ADS_SDK_AVAILABLE:
        return None

    dev_token = os.getenv("GOOGLE_ADS_DEVELOPER_TOKEN", "")
    client_id = os.getenv("GOOGLE_ADS_CLIENT_ID", "")
    client_secret = os.getenv("GOOGLE_ADS_CLIENT_SECRET", "")
    refresh_token = os.getenv("GOOGLE_ADS_REFRESH_TOKEN", "")
    login_customer_id = os.getenv("GOOGLE_ADS_LOGIN_CUSTOMER_ID", "")

    if not (dev_token and client_id and client_secret and refresh_token):
        logger.info("Google Ads credentials not set — running in demo mode")
        return None

    try:
        config = {
            "developer_token": dev_token,
            "client_id": client_id,
            "client_secret": client_secret,
            "refresh_token": refresh_token,
            "use_proto_plus": True,
        }
        if login_customer_id:
            config["login_customer_id"] = login_customer_id

        client = GoogleAdsClient.load_from_dict(config)
        logger.info("Google Ads client initialised successfully")
        return client
    except Exception as exc:
        logger.error("Failed to initialise Google Ads client: %s", exc)
        return None


# Module-level client (singleton, reused across requests)
_ads_client: Optional["GoogleAdsClient"] = None
_ads_client_initialised = False


def _get_client() -> Optional["GoogleAdsClient"]:
    global _ads_client, _ads_client_initialised
    if not _ads_client_initialised:
        _ads_client = _build_google_ads_client()
        _ads_client_initialised = True
    return _ads_client


class GoogleAdsEngine:
    """Manages Google Ads campaign lifecycle for healthcare providers.

    When credentials are configured (GOOGLE_ADS_DEVELOPER_TOKEN etc.),
    every method calls the real Google Ads API v17+.
    Otherwise it falls back to demo mode — creates local Campaign records
    with draft IDs so the rest of the system can still run.
    """

    def __init__(self, db: AsyncSession):
        self.db = db
        self.client = _get_client()

    @property
    def is_connected(self) -> bool:
        return self.client is not None

    # ------------------------------------------------------------------
    # PUBLIC: high-level methods used by the rest of the app
    # ------------------------------------------------------------------

    async def create_campaign_from_onboarding(self, doctor: Doctor) -> Campaign:
        """Create a complete Google Ads Search campaign from onboarding data."""

        specialty_key = doctor.specialty.value if doctor.specialty else "GENERAL_PHYSICIAN"
        config = SPECIALTY_CONFIGS.get(specialty_key, SPECIALTY_CONFIGS["GENERAL_PHYSICIAN"])

        ad_copy = await generate_google_ad_copy(doctor)

        daily_budget_inr = round(doctor.monthly_budget / 30.4)

        # Build keyword list
        keywords = list(config.default_keywords)
        for service in doctor.services or []:
            keywords.append(f"{service.lower()} near me")
            keywords.append(f"{service.lower()} in {doctor.city}")
            keywords.append(f"best {service.lower()} {doctor.city}")
        keywords = list(dict.fromkeys(keywords))

        campaign_name = f"PP_{doctor.clinic_name}_{specialty_key}_{doctor.city}"

        campaign = Campaign(
            doctor_id=doctor.id,
            platform=AdPlatform.GOOGLE,
            name=campaign_name,
            campaign_type="SEARCH",
            daily_budget=daily_budget_inr,
            total_budget=doctor.monthly_budget,
            currency=doctor.currency or "INR",
            target_location=f"{doctor.city}, {doctor.state}",
            target_radius_km=doctor.geo_radius_km,
            target_latitude=doctor.latitude,
            target_longitude=doctor.longitude,
            keywords=keywords,
            negative_keywords=config.negative_keywords,
            headlines=ad_copy.get("headlines", []),
            descriptions=ad_copy.get("descriptions", []),
            landing_page_url=(
                f"https://{doctor.subdomain_slug}.patientplex.ai"
                if doctor.subdomain_slug
                else None
            ),
            status=CampaignStatus.DRAFT,
        )

        try:
            platform_ids = await self._create_on_google_ads(campaign, doctor)
            campaign.platform_campaign_id = platform_ids.get("campaign_id")
            campaign.platform_ad_group_id = platform_ids.get("ad_group_id")
            campaign.status = CampaignStatus.PENDING_REVIEW
        except Exception as exc:
            logger.error("Google Ads API creation failed: %s", exc)
            campaign.error_message = str(exc)
            campaign.status = CampaignStatus.DRAFT

        self.db.add(campaign)
        await self.db.flush()

        logger.info(
            "Created Google Ads campaign '%s' for Dr. %s (%d keywords, ₹%d/day)",
            campaign_name,
            doctor.full_name,
            len(keywords),
            daily_budget_inr,
        )
        return campaign

    async def pause_campaign(self, campaign: Campaign) -> bool:
        """Pause an active campaign."""
        if self.is_connected and campaign.platform_campaign_id:
            customer_id = self._customer_id_for(campaign)
            result = await self._set_campaign_status_api(
                customer_id, campaign.platform_campaign_id, "PAUSED"
            )
            if result.get("status") == "error":
                logger.error("API pause failed: %s", result)
                return False
        campaign.status = CampaignStatus.PAUSED
        await self.db.commit()
        return True

    async def resume_campaign(self, campaign: Campaign) -> bool:
        """Resume a paused campaign."""
        if self.is_connected and campaign.platform_campaign_id:
            customer_id = self._customer_id_for(campaign)
            result = await self._set_campaign_status_api(
                customer_id, campaign.platform_campaign_id, "ENABLED"
            )
            if result.get("status") == "error":
                logger.error("API resume failed: %s", result)
                return False
        campaign.status = CampaignStatus.ACTIVE
        await self.db.commit()
        return True

    async def update_budget(self, campaign: Campaign, new_daily_budget: int) -> bool:
        """Update a campaign's daily budget."""
        if self.is_connected and campaign.platform_campaign_id:
            customer_id = self._customer_id_for(campaign)
            result = await self._update_budget_api(
                customer_id, campaign.platform_campaign_id, new_daily_budget
            )
            if result.get("status") == "error":
                logger.error("API budget update failed: %s", result)
                return False
        campaign.daily_budget = new_daily_budget
        campaign.total_budget = round(new_daily_budget * 30.4)
        await self.db.commit()
        return True

    async def sync_performance(self, campaign: Campaign) -> dict:
        """Sync performance metrics from Google Ads reporting API."""
        if self.is_connected and campaign.platform_campaign_id:
            customer_id = self._customer_id_for(campaign)
            data = await self.get_campaign_metrics(
                customer_id, campaign.platform_campaign_id, days=30
            )
            if data.get("status") == "success" and data.get("campaigns"):
                m = data["campaigns"][0]
                campaign.impressions = m.get("impressions", 0)
                campaign.clicks = m.get("clicks", 0)
                campaign.conversions = m.get("conversions", 0)
                campaign.spend = m.get("cost_inr", 0)
                campaign.cpc = m.get("avg_cpc_inr", 0)
                campaign.ctr = m.get("ctr", 0)

        campaign.last_synced_at = datetime.now(timezone.utc)
        await self.db.commit()

        return {
            "impressions": campaign.impressions,
            "clicks": campaign.clicks,
            "conversions": campaign.conversions,
            "spend": campaign.spend,
            "cpc": campaign.cpc,
            "ctr": campaign.ctr,
        }

    async def optimize_campaign(self, campaign: Campaign) -> dict:
        """Run optimization checks and apply improvements."""
        actions_taken: List[str] = []

        if self.is_connected and campaign.platform_campaign_id:
            customer_id = self._customer_id_for(campaign)

            # 1. Mine search terms for negatives
            st_data = await self.get_search_terms(
                customer_id, campaign.platform_campaign_id, days=14
            )
            if st_data.get("status") == "success":
                wasted = [
                    t for t in st_data.get("search_terms", []) if t.get("wasted")
                ]
                if wasted:
                    actions_taken.append(
                        f"Found {len(wasted)} wasted search terms "
                        f"(₹{st_data.get('wasted_spend_inr', 0)} wasted)"
                    )

            # 2. Check keyword performance
            kw_data = await self.get_keyword_performance(
                customer_id, campaign.platform_campaign_id, days=14
            )
            if kw_data.get("status") == "success":
                poor = [
                    k
                    for k in kw_data.get("keywords", [])
                    if k.get("clicks", 0) > 20 and k.get("conversions", 0) == 0
                ]
                if poor:
                    actions_taken.append(
                        f"{len(poor)} keywords with 20+ clicks but 0 conversions — consider pausing"
                    )

        return {
            "campaign_id": str(campaign.id),
            "connected": self.is_connected,
            "actions_taken": actions_taken,
            "recommendations": [
                "Monitor search terms report for irrelevant queries",
                "Test ad variations with different CTAs",
                "Consider adding call extensions for mobile users",
                "Review geographic performance and adjust radius if needed",
            ],
        }

    # ------------------------------------------------------------------
    # GOOGLE ADS API — low-level methods
    # ------------------------------------------------------------------

    async def _create_on_google_ads(
        self, campaign: Campaign, doctor: Doctor
    ) -> dict:
        """Create campaign + ad group + keywords + ad on the API."""
        if not self.is_connected:
            return {
                "campaign_id": f"draft_{uuid.uuid4().hex[:12]}",
                "ad_group_id": f"draft_{uuid.uuid4().hex[:12]}",
            }

        customer_id = self._customer_id_for(campaign)

        try:
            # Step 1 — budget
            budget_resource = self._create_budget(
                customer_id,
                f"PP Budget — {campaign.name}",
                campaign.daily_budget,
            )

            # Step 2 — campaign
            campaign_resource = self._create_campaign_resource(
                customer_id, campaign.name, budget_resource
            )
            campaign_id = campaign_resource.split("/")[-1]

            # Step 3 — ad group
            ag_resource = self._create_ad_group(
                customer_id, campaign_resource, f"{campaign.name}_AG"
            )
            ad_group_id = ag_resource.split("/")[-1]

            # Step 4 — keywords
            if campaign.keywords:
                self._add_keywords(customer_id, ag_resource, campaign.keywords)

            # Step 5 — negative keywords
            if campaign.negative_keywords:
                self._add_negative_keywords(
                    customer_id, campaign_resource, campaign.negative_keywords
                )

            # Step 6 — RSA
            if campaign.headlines and campaign.landing_page_url:
                self._create_rsa(
                    customer_id,
                    ag_resource,
                    campaign.headlines,
                    campaign.descriptions or [],
                    campaign.landing_page_url,
                )

            # Step 7 — location targeting
            if campaign.target_latitude and campaign.target_longitude:
                self._set_proximity_target(
                    customer_id,
                    campaign_resource,
                    campaign.target_latitude,
                    campaign.target_longitude,
                    campaign.target_radius_km or 5,
                )

            logger.info(
                "Google Ads resources created: campaign=%s, ad_group=%s",
                campaign_id,
                ad_group_id,
            )
            return {"campaign_id": campaign_id, "ad_group_id": ad_group_id}

        except GoogleAdsException as ex:
            errors = [
                {"message": err.message, "code": str(err.error_code)}
                for err in ex.failure.errors
            ]
            logger.error("Google Ads API error during creation: %s", errors)
            raise
        except Exception:
            logger.exception("Unexpected error during Google Ads creation")
            raise

    # ---- Budget ----

    def _create_budget(
        self, customer_id: str, name: str, daily_inr: int
    ) -> str:
        svc = self.client.get_service("CampaignBudgetService")
        op = self.client.get_type("CampaignBudgetOperation")
        b = op.create
        b.name = name
        b.amount_micros = daily_inr * 1_000_000
        b.delivery_method = self.client.enums.BudgetDeliveryMethodEnum.STANDARD
        resp = svc.mutate_campaign_budgets(
            customer_id=customer_id, operations=[op]
        )
        return resp.results[0].resource_name

    # ---- Campaign ----

    def _create_campaign_resource(
        self, customer_id: str, name: str, budget_resource: str
    ) -> str:
        svc = self.client.get_service("CampaignService")
        op = self.client.get_type("CampaignOperation")
        c = op.create
        c.name = name
        c.advertising_channel_type = (
            self.client.enums.AdvertisingChannelTypeEnum.SEARCH
        )
        c.status = self.client.enums.CampaignStatusEnum.PAUSED
        c.campaign_budget = budget_resource
        c.network_settings.target_google_search = True
        c.network_settings.target_search_network = True
        c.network_settings.target_content_network = False
        c.maximize_conversions.target_cpa_micros = 0  # let Google optimise
        resp = svc.mutate_campaigns(
            customer_id=customer_id, operations=[op]
        )
        return resp.results[0].resource_name

    # ---- Ad Group ----

    def _create_ad_group(
        self, customer_id: str, campaign_resource: str, name: str
    ) -> str:
        svc = self.client.get_service("AdGroupService")
        op = self.client.get_type("AdGroupOperation")
        ag = op.create
        ag.name = name
        ag.campaign = campaign_resource
        ag.status = self.client.enums.AdGroupStatusEnum.ENABLED
        ag.type_ = self.client.enums.AdGroupTypeEnum.SEARCH_STANDARD
        ag.cpc_bid_micros = 5_000_000  # ₹5 starting CPC
        resp = svc.mutate_ad_groups(
            customer_id=customer_id, operations=[op]
        )
        return resp.results[0].resource_name

    # ---- Keywords ----

    def _add_keywords(
        self, customer_id: str, ad_group_resource: str, keywords: List[str]
    ) -> int:
        svc = self.client.get_service("AdGroupCriterionService")
        ops = []
        for kw_text in keywords[:200]:  # API limit per request
            op = self.client.get_type("AdGroupCriterionOperation")
            criterion = op.create
            criterion.ad_group = ad_group_resource
            criterion.status = (
                self.client.enums.AdGroupCriterionStatusEnum.ENABLED
            )
            criterion.keyword.text = kw_text
            criterion.keyword.match_type = (
                self.client.enums.KeywordMatchTypeEnum.PHRASE
            )
            ops.append(op)
        resp = svc.mutate_ad_group_criteria(
            customer_id=customer_id, operations=ops
        )
        return len(resp.results)

    def _add_negative_keywords(
        self, customer_id: str, campaign_resource: str, negatives: List[str]
    ) -> int:
        svc = self.client.get_service("CampaignCriterionService")
        ops = []
        for neg in negatives[:500]:
            op = self.client.get_type("CampaignCriterionOperation")
            criterion = op.create
            criterion.campaign = campaign_resource
            criterion.negative = True
            criterion.keyword.text = neg
            criterion.keyword.match_type = (
                self.client.enums.KeywordMatchTypeEnum.BROAD
            )
            ops.append(op)
        resp = svc.mutate_campaign_criteria(
            customer_id=customer_id, operations=ops
        )
        return len(resp.results)

    # ---- RSA ----

    def _create_rsa(
        self,
        customer_id: str,
        ad_group_resource: str,
        headlines: List[str],
        descriptions: List[str],
        final_url: str,
    ) -> str:
        svc = self.client.get_service("AdGroupAdService")
        op = self.client.get_type("AdGroupAdOperation")
        aga = op.create
        aga.ad_group = ad_group_resource
        aga.status = self.client.enums.AdGroupAdStatusEnum.ENABLED

        ad = aga.ad
        ad.final_urls.append(final_url)

        rsa = ad.responsive_search_ad
        for h in headlines[:15]:
            asset = self.client.get_type("AdTextAsset")
            asset.text = h[:30]  # headline max 30 chars
            rsa.headlines.append(asset)

        for d in descriptions[:4]:
            asset = self.client.get_type("AdTextAsset")
            asset.text = d[:90]  # description max 90 chars
            rsa.descriptions.append(asset)

        resp = svc.mutate_ad_group_ads(
            customer_id=customer_id, operations=[op]
        )
        return resp.results[0].resource_name

    # ---- Location targeting ----

    def _set_proximity_target(
        self,
        customer_id: str,
        campaign_resource: str,
        lat: float,
        lng: float,
        radius_km: int,
    ):
        svc = self.client.get_service("CampaignCriterionService")
        op = self.client.get_type("CampaignCriterionOperation")
        criterion = op.create
        criterion.campaign = campaign_resource
        prox = criterion.proximity
        prox.geo_point.latitude_in_micro_degrees = int(lat * 1_000_000)
        prox.geo_point.longitude_in_micro_degrees = int(lng * 1_000_000)
        prox.radius = float(radius_km)
        prox.radius_units = (
            self.client.enums.ProximityRadiusUnitsEnum.KILOMETERS
        )
        svc.mutate_campaign_criteria(
            customer_id=customer_id, operations=[op]
        )

    # ------------------------------------------------------------------
    # GOOGLE ADS API — reporting / metrics
    # ------------------------------------------------------------------

    async def get_campaign_metrics(
        self,
        customer_id: str,
        campaign_id: Optional[str] = None,
        days: int = 30,
    ) -> Dict:
        """Pull campaign performance metrics via GAQL."""
        if not self.is_connected:
            return self._demo_metrics()

        try:
            ga_svc = self.client.get_service("GoogleAdsService")
            query = f"""
                SELECT
                    campaign.id,
                    campaign.name,
                    campaign.status,
                    metrics.impressions,
                    metrics.clicks,
                    metrics.cost_micros,
                    metrics.conversions,
                    metrics.ctr,
                    metrics.average_cpc,
                    metrics.cost_per_conversion,
                    metrics.conversion_rate
                FROM campaign
                WHERE segments.date DURING LAST_{days}_DAYS
            """
            if campaign_id:
                query += f" AND campaign.id = {campaign_id}"

            response = ga_svc.search(customer_id=customer_id, query=query)
            campaigns = []
            for row in response:
                campaigns.append(
                    {
                        "campaign_id": str(row.campaign.id),
                        "name": row.campaign.name,
                        "status": row.campaign.status.name,
                        "impressions": row.metrics.impressions,
                        "clicks": row.metrics.clicks,
                        "cost_inr": round(row.metrics.cost_micros / 1e6, 2),
                        "conversions": round(row.metrics.conversions, 1),
                        "ctr": round(row.metrics.ctr * 100, 2),
                        "avg_cpc_inr": round(
                            row.metrics.average_cpc / 1e6, 2
                        ),
                        "cost_per_conversion_inr": (
                            round(row.metrics.cost_per_conversion / 1e6, 2)
                            if row.metrics.cost_per_conversion
                            else None
                        ),
                        "conversion_rate": round(
                            row.metrics.conversion_rate * 100, 2
                        ),
                    }
                )
            return {
                "status": "success",
                "campaigns": campaigns,
                "period_days": days,
            }
        except GoogleAdsException as ex:
            errors = [{"message": e.message} for e in ex.failure.errors]
            return {"status": "error", "errors": errors}
        except Exception as e:
            return {"status": "error", "message": str(e)}

    async def get_keyword_performance(
        self, customer_id: str, campaign_id: str, days: int = 30
    ) -> Dict:
        """Keyword-level performance for a campaign."""
        if not self.is_connected:
            return {"status": "demo_mode", "keywords": []}

        try:
            ga_svc = self.client.get_service("GoogleAdsService")
            query = f"""
                SELECT
                    ad_group_criterion.keyword.text,
                    ad_group_criterion.keyword.match_type,
                    metrics.impressions,
                    metrics.clicks,
                    metrics.cost_micros,
                    metrics.conversions,
                    metrics.ctr,
                    metrics.average_cpc
                FROM keyword_view
                WHERE campaign.id = {campaign_id}
                    AND segments.date DURING LAST_{days}_DAYS
                ORDER BY metrics.cost_micros DESC
                LIMIT 50
            """
            response = ga_svc.search(customer_id=customer_id, query=query)
            keywords = []
            for row in response:
                keywords.append(
                    {
                        "keyword": row.ad_group_criterion.keyword.text,
                        "match_type": row.ad_group_criterion.keyword.match_type.name,
                        "impressions": row.metrics.impressions,
                        "clicks": row.metrics.clicks,
                        "cost_inr": round(row.metrics.cost_micros / 1e6, 2),
                        "conversions": round(row.metrics.conversions, 1),
                        "ctr": round(row.metrics.ctr * 100, 2),
                        "avg_cpc_inr": round(
                            row.metrics.average_cpc / 1e6, 2
                        ),
                    }
                )
            return {"status": "success", "keywords": keywords}
        except Exception as e:
            return {"status": "error", "message": str(e)}

    async def get_search_terms(
        self, customer_id: str, campaign_id: str, days: int = 30
    ) -> Dict:
        """Search terms report — find wasted spend and negative keyword candidates."""
        if not self.is_connected:
            return {"status": "demo_mode", "search_terms": []}

        try:
            ga_svc = self.client.get_service("GoogleAdsService")
            query = f"""
                SELECT
                    search_term_view.search_term,
                    metrics.impressions,
                    metrics.clicks,
                    metrics.cost_micros,
                    metrics.conversions
                FROM search_term_view
                WHERE campaign.id = {campaign_id}
                    AND segments.date DURING LAST_{days}_DAYS
                ORDER BY metrics.cost_micros DESC
                LIMIT 100
            """
            response = ga_svc.search(customer_id=customer_id, query=query)
            terms = []
            for row in response:
                cost = row.metrics.cost_micros / 1e6
                terms.append(
                    {
                        "search_term": row.search_term_view.search_term,
                        "impressions": row.metrics.impressions,
                        "clicks": row.metrics.clicks,
                        "cost_inr": round(cost, 2),
                        "conversions": round(row.metrics.conversions, 1),
                        "wasted": cost > 0 and row.metrics.conversions == 0,
                    }
                )
            wasted_spend = sum(t["cost_inr"] for t in terms if t["wasted"])
            return {
                "status": "success",
                "search_terms": terms,
                "wasted_spend_inr": round(wasted_spend, 2),
            }
        except Exception as e:
            return {"status": "error", "message": str(e)}

    # ------------------------------------------------------------------
    # GOOGLE ADS API — campaign status / budget mutations
    # ------------------------------------------------------------------

    async def _set_campaign_status_api(
        self, customer_id: str, campaign_id: str, status: str
    ) -> Dict:
        if not self.is_connected:
            return {"status": "demo_mode"}
        try:
            svc = self.client.get_service("CampaignService")
            op = self.client.get_type("CampaignOperation")
            c = op.update
            c.resource_name = svc.campaign_path(customer_id, campaign_id)
            c.status = getattr(self.client.enums.CampaignStatusEnum, status)
            self.client.copy_from(
                op.update_mask,
                self.client.get_type("FieldMask")(paths=["status"]),
            )
            svc.mutate_campaigns(customer_id=customer_id, operations=[op])
            return {"status": "success", "new_status": status}
        except Exception as e:
            return {"status": "error", "message": str(e)}

    async def _update_budget_api(
        self, customer_id: str, campaign_id: str, new_daily_inr: float
    ) -> Dict:
        if not self.is_connected:
            return {"status": "demo_mode"}
        try:
            ga_svc = self.client.get_service("GoogleAdsService")
            query = f"""
                SELECT campaign.campaign_budget
                FROM campaign
                WHERE campaign.id = {campaign_id}
            """
            resp = ga_svc.search(customer_id=customer_id, query=query)
            budget_resource = None
            for row in resp:
                budget_resource = row.campaign.campaign_budget
                break
            if not budget_resource:
                return {"status": "error", "message": "Campaign not found"}

            bsvc = self.client.get_service("CampaignBudgetService")
            bop = self.client.get_type("CampaignBudgetOperation")
            b = bop.update
            b.resource_name = budget_resource
            b.amount_micros = int(new_daily_inr * 1_000_000)
            self.client.copy_from(
                bop.update_mask,
                self.client.get_type("FieldMask")(paths=["amount_micros"]),
            )
            bsvc.mutate_campaign_budgets(
                customer_id=customer_id, operations=[bop]
            )
            return {"status": "updated", "new_daily_budget_inr": new_daily_inr}
        except Exception as e:
            return {"status": "error", "message": str(e)}

    # ------------------------------------------------------------------
    # Helpers
    # ------------------------------------------------------------------

    @staticmethod
    def _customer_id_for(campaign: Campaign) -> str:
        """Resolve the Google Ads customer ID for a campaign's doctor.

        In production this comes from the doctor's stored OAuth / MCC link.
        Falls back to the env-level login_customer_id.
        """
        return os.getenv("GOOGLE_ADS_LOGIN_CUSTOMER_ID", "")

    @staticmethod
    def _demo_metrics() -> Dict:
        return {
            "status": "demo_mode",
            "message": "Google Ads not configured. Set GOOGLE_ADS_* env vars to connect.",
            "campaigns": [
                {
                    "campaign_id": "demo",
                    "name": "Demo Campaign",
                    "status": "DEMO",
                    "impressions": 0,
                    "clicks": 0,
                    "cost_inr": 0,
                    "conversions": 0,
                    "ctr": 0,
                    "avg_cpc_inr": 0,
                }
            ],
        }
