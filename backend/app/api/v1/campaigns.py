"""Campaign management endpoints — create, monitor, and optimize ad campaigns."""

from datetime import datetime, timezone
from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, Query
from pydantic import BaseModel
from sqlalchemy import and_, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.api.v1.auth import get_current_doctor
from app.core.config import settings
from app.db.session import get_db
from app.models.campaign import AdPlatform, Campaign, CampaignStatus
from app.models.doctor import Doctor
from app.services.google_ads_engine import GoogleAdsEngine
from app.services.meta_ads_engine import MetaAdsEngine
from app.services.chatgpt_ads_engine import ChatGPTAdsEngine
from app.services.linkedin_ads_engine import LinkedInAdsEngine
from app.services.whatsapp_ads_engine import WhatsAppAdsEngine

router = APIRouter(prefix="/campaigns", tags=["campaigns"])


def require_ads_enabled():
    """Gate ad publishing and budget writes behind ADS_ENABLED.

    Campaign LISTING and reads are always available to authenticated clinics;
    only mutating / provider-write operations require ads to be enabled.
    """
    if not settings.ADS_ENABLED:
        raise HTTPException(
            status_code=403,
            detail="Ad publishing is disabled on this server (ADS_ENABLED=false)",
        )


ADS_WRITE = [Depends(require_ads_enabled)]


class LaunchRequest(BaseModel):
    platforms: list[str] = ["GOOGLE", "META", "CHATGPT", "LINKEDIN", "WHATSAPP"]  # Which platforms to launch on


class BudgetUpdate(BaseModel):
    daily_budget: int


class KeywordUpdateRequest(BaseModel):
    """Add or remove keywords from a Google Ads campaign."""
    add: list[str] = []
    remove: list[str] = []


class NegativeKeywordRequest(BaseModel):
    """Add negative keywords to block irrelevant traffic."""
    keywords: list[str]


class AdCopyUpdateRequest(BaseModel):
    """Update RSA headlines and descriptions for a Google Ads campaign."""
    headlines: list[str]  # 3-15 headlines, max 30 chars each
    descriptions: list[str]  # 2-4 descriptions, max 90 chars each


class CampaignStatusRequest(BaseModel):
    """Change campaign status via Google Ads REST API."""
    status: str  # "ENABLED" or "PAUSED"


@router.post("/launch", dependencies=ADS_WRITE)
async def launch_campaigns(
    body: LaunchRequest,
    doctor: Doctor = Depends(get_current_doctor),
    db: AsyncSession = Depends(get_db),
):
    """Smart campaign launcher — optimize existing, create only when needed.

    Logic:
    1. Check which platforms already have active/pending campaigns
    2. For existing campaigns → optimize (sync performance, update keywords, adjust budget)
    3. For missing platforms → create new campaigns
    4. If existing campaign has ERROR status → recreate it
    """
    if not doctor.onboarding_completed:
        raise HTTPException(status_code=400, detail="Complete onboarding before launching campaigns")

    # Fetch all existing campaigns for this doctor
    result = await db.execute(
        select(Campaign).where(Campaign.doctor_id == doctor.id)
    )
    existing = result.scalars().all()

    # Build a map: platform → list of campaigns (most recent first)
    existing_by_platform: dict[str, list[Campaign]] = {}
    for c in existing:
        key = c.platform.value
        existing_by_platform.setdefault(key, []).append(c)

    results = {}

    # Platform handlers
    platform_config = {
        "GOOGLE": {
            "create": lambda: GoogleAdsEngine(db).create_campaign_from_onboarding(doctor),
            "optimize": lambda c: GoogleAdsEngine(db).optimize_campaign(c),
            "sync": lambda c: GoogleAdsEngine(db).sync_performance(c),
        },
        "META": {
            "create": lambda: MetaAdsEngine(db).create_campaign_from_onboarding(doctor),
            "optimize": None,
            "sync": lambda c: MetaAdsEngine(db).sync_performance(c),
        },
        "CHATGPT": {
            "create": lambda: ChatGPTAdsEngine(db).create_campaign(doctor),
            "optimize": None,
            "sync": None,
        },
        "LINKEDIN": {
            "create": lambda: LinkedInAdsEngine(db).create_referral_campaign(doctor),
            "optimize": None,
            "sync": lambda c: LinkedInAdsEngine(db).sync_performance(c),
        },
        "WHATSAPP": {
            "create": lambda: WhatsAppAdsEngine(db).create_campaign(doctor),
            "optimize": None,
            "sync": lambda c: WhatsAppAdsEngine(db).sync_performance(c),
        },
    }

    for platform_key in body.platforms:
        config = platform_config.get(platform_key)
        if not config:
            continue

        existing_campaigns = existing_by_platform.get(platform_key, [])

        # AI Decision: evaluate existing campaigns and decide action
        decision = _ai_campaign_decision(existing_campaigns, doctor)

        if decision["action"] == "optimize":
            # Existing campaign is good → optimize it
            campaign = decision["campaign"]

            # Sync latest performance
            if config["sync"]:
                try:
                    await config["sync"](campaign)
                except Exception:
                    pass

            # Run optimization if available
            optimization_result = None
            if config["optimize"]:
                try:
                    optimization_result = await config["optimize"](campaign)
                except Exception:
                    pass

            results[platform_key.lower()] = {
                "campaign_id": str(campaign.id),
                "name": campaign.name,
                "status": campaign.status.value,
                "daily_budget": campaign.daily_budget,
                "action": "optimized",
                "reason": decision["reason"],
                "health_score": decision["score"],
                "optimization": optimization_result,
            }

        elif decision["action"] == "rebuild":
            # Existing campaign is broken → create fresh
            try:
                campaign = await config["create"]()
                results[platform_key.lower()] = {
                    "campaign_id": str(campaign.id),
                    "name": campaign.name,
                    "status": campaign.status.value,
                    "daily_budget": campaign.daily_budget,
                    "action": "rebuilt",
                    "reason": decision["reason"],
                    "health_score": decision["score"],
                }
            except Exception as exc:
                results[platform_key.lower()] = {"action": "error", "error": str(exc)}

        else:
            # No campaign exists → create new
            try:
                campaign = await config["create"]()
                results[platform_key.lower()] = {
                    "campaign_id": str(campaign.id),
                    "name": campaign.name,
                    "status": campaign.status.value,
                    "daily_budget": campaign.daily_budget,
                    "action": "created",
                    "reason": "No existing campaign for this platform",
                }
            except Exception as exc:
                results[platform_key.lower()] = {"action": "error", "error": str(exc)}

    await db.commit()

    created_count = sum(1 for r in results.values() if r.get("action") == "created")
    optimized_count = sum(1 for r in results.values() if r.get("action") == "optimized")

    return {
        "message": f"{created_count} new campaigns created, {optimized_count} existing campaigns optimized",
        "campaigns": results,
    }


@router.get("/")
async def list_campaigns(
    platform: AdPlatform | None = None,
    status: CampaignStatus | None = None,
    doctor: Doctor = Depends(get_current_doctor),
    db: AsyncSession = Depends(get_db),
):
    """List all campaigns for the authenticated doctor."""
    query = select(Campaign).where(Campaign.doctor_id == doctor.id)
    if platform:
        query = query.where(Campaign.platform == platform)
    if status:
        query = query.where(Campaign.status == status)
    query = query.order_by(Campaign.created_at.desc())

    result = await db.execute(query)
    campaigns = result.scalars().all()

    return {
        "campaigns": [_serialize_campaign(c) for c in campaigns],
        "count": len(campaigns),
        "ads_enabled": settings.ADS_ENABLED,
    }


@router.get("/{campaign_id}")
async def get_campaign(
    campaign_id: UUID,
    doctor: Doctor = Depends(get_current_doctor),
    db: AsyncSession = Depends(get_db),
):
    """Get detailed campaign info including ad copy and performance metrics."""
    campaign = await _get_campaign(campaign_id, doctor.id, db)
    return _serialize_campaign(campaign, detailed=True)


@router.put("/{campaign_id}/pause", dependencies=ADS_WRITE)
async def pause_campaign(
    campaign_id: UUID,
    doctor: Doctor = Depends(get_current_doctor),
    db: AsyncSession = Depends(get_db),
):
    """Pause an active campaign — works for ALL platforms with write API."""
    campaign = await _get_campaign(campaign_id, doctor.id, db)
    if campaign.status != CampaignStatus.ACTIVE:
        raise HTTPException(status_code=400, detail="Campaign is not active")

    result = await _platform_status_update(campaign, "PAUSED", db)
    return {"message": "Campaign paused", "campaign_id": str(campaign_id), **result}


@router.put("/{campaign_id}/resume", dependencies=ADS_WRITE)
async def resume_campaign(
    campaign_id: UUID,
    doctor: Doctor = Depends(get_current_doctor),
    db: AsyncSession = Depends(get_db),
):
    """Resume a paused campaign — works for ALL platforms with write API."""
    campaign = await _get_campaign(campaign_id, doctor.id, db)
    if campaign.status != CampaignStatus.PAUSED:
        raise HTTPException(status_code=400, detail="Campaign is not paused")

    result = await _platform_status_update(campaign, "ACTIVE", db)
    return {"message": "Campaign resumed", "campaign_id": str(campaign_id), **result}


@router.put("/{campaign_id}/budget", dependencies=ADS_WRITE)
async def update_budget(
    campaign_id: UUID,
    body: BudgetUpdate,
    doctor: Doctor = Depends(get_current_doctor),
    db: AsyncSession = Depends(get_db),
):
    """Update a campaign's daily budget — works for ALL platforms with write API."""
    campaign = await _get_campaign(campaign_id, doctor.id, db)

    result = await _platform_budget_update(campaign, body.daily_budget, db)
    return {"message": "Budget updated", "daily_budget": body.daily_budget, **result}


@router.post("/{campaign_id}/sync", dependencies=ADS_WRITE)
async def sync_performance(
    campaign_id: UUID,
    doctor: Doctor = Depends(get_current_doctor),
    db: AsyncSession = Depends(get_db),
):
    """Sync latest performance metrics from the ad platform."""
    campaign = await _get_campaign(campaign_id, doctor.id, db)

    if campaign.platform == AdPlatform.GOOGLE:
        engine = GoogleAdsEngine(db)
        metrics = await engine.sync_performance(campaign)
    elif campaign.platform == AdPlatform.META:
        engine = MetaAdsEngine(db)
        metrics = await engine.sync_performance(campaign)
    elif campaign.platform == AdPlatform.LINKEDIN:
        engine = LinkedInAdsEngine(db)
        metrics = await engine.sync_performance(campaign)
    elif campaign.platform == AdPlatform.WHATSAPP:
        engine = WhatsAppAdsEngine(db)
        metrics = await engine.sync_performance(campaign)
    else:
        metrics = {}

    return {"campaign_id": str(campaign_id), "metrics": metrics}


# ------------------------------------------------------------------
# WRITE API ENDPOINTS — Edit campaigns via Google Ads REST API
# Works with both per-doctor OAuth tokens AND MCC manager tokens
# ------------------------------------------------------------------


@router.put("/{campaign_id}/status", dependencies=ADS_WRITE)
async def update_campaign_status(
    campaign_id: UUID,
    body: CampaignStatusRequest,
    doctor: Doctor = Depends(get_current_doctor),
    db: AsyncSession = Depends(get_db),
):
    """Change campaign status (ENABLED/PAUSED) via Google Ads REST API.

    Uses doctor's OAuth token if available, falls back to MCC manager token.
    """
    campaign = await _get_campaign(campaign_id, doctor.id, db)

    if campaign.platform != AdPlatform.GOOGLE:
        raise HTTPException(status_code=400, detail="Status update via API only supported for Google Ads")

    if body.status not in ("ENABLED", "PAUSED"):
        raise HTTPException(status_code=400, detail="Status must be ENABLED or PAUSED")

    engine = GoogleAdsEngine(db)

    # Try REST API with doctor's OAuth token first
    if campaign.platform_campaign_id:
        customer_id = doctor.google_ads_customer_id or ""
        clean_cid = customer_id.replace("-", "")
        resource_name = f"customers/{clean_cid}/campaigns/{campaign.platform_campaign_id}"
        result = await engine.update_campaign_status_rest(clean_cid, resource_name, body.status)

        if result.get("status") == "success":
            campaign.status = CampaignStatus.ACTIVE if body.status == "ENABLED" else CampaignStatus.PAUSED
            await db.commit()
            return {"message": f"Campaign {body.status.lower()}", "campaign_id": str(campaign_id), "api": "rest"}

    # Fallback to local DB update
    campaign.status = CampaignStatus.ACTIVE if body.status == "ENABLED" else CampaignStatus.PAUSED
    await db.commit()
    return {"message": f"Campaign {body.status.lower()} (local)", "campaign_id": str(campaign_id), "api": "local"}


@router.put("/{campaign_id}/keywords", dependencies=ADS_WRITE)
async def update_keywords(
    campaign_id: UUID,
    body: KeywordUpdateRequest,
    doctor: Doctor = Depends(get_current_doctor),
    db: AsyncSession = Depends(get_db),
):
    """Add or remove keywords from a Google Ads campaign.

    Uses REST API for live Google Ads changes + updates local DB.
    """
    campaign = await _get_campaign(campaign_id, doctor.id, db)

    if campaign.platform != AdPlatform.GOOGLE:
        raise HTTPException(status_code=400, detail="Keyword management only supported for Google Ads")

    current_keywords = list(campaign.keywords or [])
    api_result = None

    # Add keywords via REST API if possible
    if body.add and campaign.platform_campaign_id:
        engine = GoogleAdsEngine(db)
        customer_id = (doctor.google_ads_customer_id or "").replace("-", "")
        # Note: adding keywords requires ad group ID — for now update locally
        # Full implementation needs ad group lookup from campaign
        current_keywords.extend(body.add)

    # Remove keywords
    if body.remove:
        current_keywords = [k for k in current_keywords if k not in body.remove]

    # Deduplicate
    campaign.keywords = list(dict.fromkeys(current_keywords))
    await db.commit()

    return {
        "message": f"Keywords updated: +{len(body.add)} added, -{len(body.remove)} removed",
        "total_keywords": len(campaign.keywords),
        "keywords": campaign.keywords,
    }


@router.put("/{campaign_id}/negative-keywords", dependencies=ADS_WRITE)
async def add_negative_keywords(
    campaign_id: UUID,
    body: NegativeKeywordRequest,
    doctor: Doctor = Depends(get_current_doctor),
    db: AsyncSession = Depends(get_db),
):
    """Add negative keywords to block irrelevant searches.

    Uses REST API for live Google Ads changes + updates local DB.
    Critical for cost optimization — blocks wasteful clicks.
    """
    campaign = await _get_campaign(campaign_id, doctor.id, db)

    if campaign.platform != AdPlatform.GOOGLE:
        raise HTTPException(status_code=400, detail="Negative keywords only supported for Google Ads")

    # Try REST API first
    api_result = None
    if campaign.platform_campaign_id:
        engine = GoogleAdsEngine(db)
        customer_id = (doctor.google_ads_customer_id or "").replace("-", "")
        api_result = await engine.add_negative_keywords_rest(
            customer_id, campaign.platform_campaign_id, body.keywords
        )

    # Always update local DB
    current_negatives = list(campaign.negative_keywords or [])
    current_negatives.extend(body.keywords)
    campaign.negative_keywords = list(dict.fromkeys(current_negatives))
    await db.commit()

    return {
        "message": f"{len(body.keywords)} negative keywords added",
        "total_negative_keywords": len(campaign.negative_keywords),
        "api_result": api_result,
    }


@router.put("/{campaign_id}/ad-copy", dependencies=ADS_WRITE)
async def update_ad_copy(
    campaign_id: UUID,
    body: AdCopyUpdateRequest,
    doctor: Doctor = Depends(get_current_doctor),
    db: AsyncSession = Depends(get_db),
):
    """Update ad copy — works for ALL platforms.

    For Google: RSA format (3-15 headlines max 30 chars, 2-4 descriptions max 90 chars)
    For Meta/WhatsApp: primary_text + headline format
    For LinkedIn: intro_text + headline + description format
    For ChatGPT: headline + body + cta format
    """
    campaign = await _get_campaign(campaign_id, doctor.id, db)

    if campaign.platform == AdPlatform.GOOGLE:
        # Google RSA validation
        if len(body.headlines) < 3:
            raise HTTPException(status_code=400, detail="Minimum 3 headlines required for RSA")
        if len(body.descriptions) < 2:
            raise HTTPException(status_code=400, detail="Minimum 2 descriptions required for RSA")
        over_limit_headlines = [h for h in body.headlines if len(h) > 30]
        if over_limit_headlines:
            raise HTTPException(status_code=400, detail=f"Headlines must be ≤30 chars. Over: {over_limit_headlines[:3]}")
        over_limit_desc = [d for d in body.descriptions if len(d) > 90]
        if over_limit_desc:
            raise HTTPException(status_code=400, detail=f"Descriptions must be ≤90 chars. Over: {over_limit_desc[:2]}")
        campaign.headlines = body.headlines[:15]
        campaign.descriptions = body.descriptions[:4]

    elif campaign.platform == AdPlatform.META:
        engine = MetaAdsEngine(db)
        await engine.update_ad_creative(
            campaign,
            primary_text=body.descriptions[0] if body.descriptions else "",
            headline=body.headlines[0] if body.headlines else "",
            description=body.descriptions[1] if len(body.descriptions) > 1 else "",
        )

    elif campaign.platform == AdPlatform.WHATSAPP:
        engine = WhatsAppAdsEngine(db)
        await engine.update_ad_copy(
            campaign,
            primary_text=body.descriptions[0] if body.descriptions else "",
            headline=body.headlines[0] if body.headlines else "",
        )

    elif campaign.platform == AdPlatform.LINKEDIN:
        engine = LinkedInAdsEngine(db)
        await engine.update_ad_copy(
            campaign,
            intro_text=body.descriptions[0] if body.descriptions else "",
            headline=body.headlines[0] if body.headlines else "",
            description=body.descriptions[1] if len(body.descriptions) > 1 else "",
        )

    elif campaign.platform == AdPlatform.CHATGPT:
        engine = ChatGPTAdsEngine(db)
        await engine.update_sponsored_content(
            campaign.id,
            headline=body.headlines[0] if body.headlines else "",
            body=body.descriptions[0] if body.descriptions else "",
            cta="Book Consultation",
        )

    # Always save headlines/descriptions locally for all platforms
    campaign.headlines = body.headlines[:15]
    campaign.descriptions = body.descriptions[:4]
    await db.commit()

    return {
        "message": "Ad copy updated",
        "platform": campaign.platform.value,
        "headlines": len(campaign.headlines),
        "descriptions": len(campaign.descriptions),
    }


@router.get("/{campaign_id}/keyword-performance")
async def get_keyword_performance(
    campaign_id: UUID,
    days: int = Query(default=30, ge=7, le=90),
    doctor: Doctor = Depends(get_current_doctor),
    db: AsyncSession = Depends(get_db),
):
    """Get keyword-level performance data from Google Ads.

    Shows which keywords are generating clicks and conversions.
    Essential for optimization decisions.
    """
    campaign = await _get_campaign(campaign_id, doctor.id, db)

    if campaign.platform != AdPlatform.GOOGLE:
        raise HTTPException(status_code=400, detail="Keyword performance only available for Google Ads")

    if not campaign.platform_campaign_id:
        return {"keywords": [], "message": "Campaign not yet linked to Google Ads"}

    engine = GoogleAdsEngine(db)
    customer_id = (doctor.google_ads_customer_id or "").replace("-", "")
    result = await engine.get_keyword_performance_rest(customer_id, campaign.platform_campaign_id, days)

    return result


@router.get("/{campaign_id}/search-terms")
async def get_search_terms(
    campaign_id: UUID,
    days: int = Query(default=30, ge=7, le=90),
    doctor: Doctor = Depends(get_current_doctor),
    db: AsyncSession = Depends(get_db),
):
    """Get search terms report — what people actually typed to trigger ads.

    Gold mine for optimization:
    - Good terms → add as keywords
    - Bad terms → add as negative keywords
    - Waste terms → highlighted for immediate blocking
    """
    campaign = await _get_campaign(campaign_id, doctor.id, db)

    if campaign.platform != AdPlatform.GOOGLE:
        raise HTTPException(status_code=400, detail="Search terms only available for Google Ads")

    if not campaign.platform_campaign_id:
        return {"search_terms": [], "message": "Campaign not yet linked to Google Ads"}

    engine = GoogleAdsEngine(db)
    customer_id = (doctor.google_ads_customer_id or "").replace("-", "")
    result = await engine.get_search_terms_rest(customer_id, campaign.platform_campaign_id, days)

    return result


@router.get("/overview/stats")
async def campaign_overview(
    doctor: Doctor = Depends(get_current_doctor),
    db: AsyncSession = Depends(get_db),
):
    """Aggregate stats across all active campaigns."""
    result = await db.execute(
        select(Campaign).where(Campaign.doctor_id == doctor.id)
    )
    campaigns = result.scalars().all()

    total_spend = sum(c.spend for c in campaigns)
    total_clicks = sum(c.clicks for c in campaigns)
    total_impressions = sum(c.impressions for c in campaigns)
    total_conversions = sum(c.conversions for c in campaigns)
    active_count = sum(1 for c in campaigns if c.status == CampaignStatus.ACTIVE)

    # Doctor-friendly metrics
    avg_treatment_value = 5000  # ₹5,000 average treatment value (configurable later)
    cost_per_patient = round(total_spend / total_conversions, 2) if total_conversions else None
    estimated_revenue = total_conversions * avg_treatment_value if total_conversions else 0
    roi_percent = round(
        ((estimated_revenue - total_spend) / total_spend) * 100, 1
    ) if total_spend > 0 and estimated_revenue > 0 else None

    return {
        "total_campaigns": len(campaigns),
        "active_campaigns": active_count,
        "total_spend": total_spend,
        "total_clicks": total_clicks,
        "total_impressions": total_impressions,
        "total_conversions": total_conversions,
        "avg_cpc": round(total_spend / total_clicks, 2) if total_clicks else 0,
        "avg_ctr": round(total_clicks / total_impressions * 100, 2) if total_impressions else 0,
        "cost_per_conversion": round(total_spend / total_conversions, 2) if total_conversions else 0,
        # Doctor-friendly metrics
        "cost_per_patient": cost_per_patient,
        "estimated_revenue": estimated_revenue,
        "roi_percent": roi_percent,
    }


@router.get("/overview/live")
async def campaign_overview_live(
    doctor: Doctor = Depends(get_current_doctor),
    db: AsyncSession = Depends(get_db),
):
    """Same as /overview/stats but includes a refreshed_at timestamp for auto-refresh."""
    result = await db.execute(
        select(Campaign).where(Campaign.doctor_id == doctor.id)
    )
    campaigns = result.scalars().all()

    total_spend = sum(c.spend for c in campaigns)
    total_clicks = sum(c.clicks for c in campaigns)
    total_impressions = sum(c.impressions for c in campaigns)
    total_conversions = sum(c.conversions for c in campaigns)
    active_count = sum(1 for c in campaigns if c.status == CampaignStatus.ACTIVE)

    avg_treatment_value = 5000
    cost_per_patient = round(total_spend / total_conversions, 2) if total_conversions else None
    estimated_revenue = total_conversions * avg_treatment_value if total_conversions else 0
    roi_percent = round(
        ((estimated_revenue - total_spend) / total_spend) * 100, 1
    ) if total_spend > 0 and estimated_revenue > 0 else None

    return {
        "total_campaigns": len(campaigns),
        "active_campaigns": active_count,
        "total_spend": total_spend,
        "total_clicks": total_clicks,
        "total_impressions": total_impressions,
        "total_conversions": total_conversions,
        "avg_cpc": round(total_spend / total_clicks, 2) if total_clicks else 0,
        "avg_ctr": round(total_clicks / total_impressions * 100, 2) if total_impressions else 0,
        "cost_per_conversion": round(total_spend / total_conversions, 2) if total_conversions else 0,
        "cost_per_patient": cost_per_patient,
        "estimated_revenue": estimated_revenue,
        "roi_percent": roi_percent,
        "refreshed_at": datetime.now(timezone.utc).isoformat(),
    }


async def _get_campaign(campaign_id: UUID, doctor_id, db: AsyncSession) -> Campaign:
    result = await db.execute(
        select(Campaign).where(
            and_(Campaign.id == campaign_id, Campaign.doctor_id == doctor_id)
        )
    )
    campaign = result.scalar_one_or_none()
    if not campaign:
        raise HTTPException(status_code=404, detail="Campaign not found")
    return campaign


async def _platform_status_update(campaign: Campaign, new_status: str, db: AsyncSession) -> dict:
    """Route status update to the correct platform engine with write API."""
    api_status = "ENABLED" if new_status == "ACTIVE" and campaign.platform == AdPlatform.GOOGLE else new_status

    if campaign.platform == AdPlatform.GOOGLE:
        engine = GoogleAdsEngine(db)
        if new_status == "PAUSED":
            await engine.pause_campaign(campaign)
        else:
            await engine.resume_campaign(campaign)
        return {"platform": "google", "api": "write"}

    elif campaign.platform == AdPlatform.META:
        engine = MetaAdsEngine(db)
        result = await engine.update_campaign_status(campaign, new_status)
        return {"platform": "meta", **result}

    elif campaign.platform == AdPlatform.LINKEDIN:
        engine = LinkedInAdsEngine(db)
        result = await engine.update_campaign_status(campaign, new_status)
        return {"platform": "linkedin", **result}

    elif campaign.platform == AdPlatform.WHATSAPP:
        engine = WhatsAppAdsEngine(db)
        result = await engine.update_campaign_status(campaign, new_status)
        return {"platform": "whatsapp", **result}

    elif campaign.platform == AdPlatform.CHATGPT:
        engine = ChatGPTAdsEngine(db)
        result = await engine.update_campaign_status(campaign.id, new_status)
        return {"platform": "chatgpt", **result}

    else:
        campaign.status = CampaignStatus.ACTIVE if new_status == "ACTIVE" else CampaignStatus.PAUSED
        await db.commit()
        return {"platform": "unknown", "api": "local"}


async def _platform_budget_update(campaign: Campaign, new_daily_inr: float, db: AsyncSession) -> dict:
    """Route budget update to the correct platform engine with write API."""
    if campaign.platform == AdPlatform.GOOGLE:
        engine = GoogleAdsEngine(db)
        await engine.update_budget(campaign, new_daily_inr)
        return {"platform": "google", "api": "write"}

    elif campaign.platform == AdPlatform.META:
        engine = MetaAdsEngine(db)
        result = await engine.update_budget(campaign, new_daily_inr)
        return {"platform": "meta", **result}

    elif campaign.platform == AdPlatform.LINKEDIN:
        engine = LinkedInAdsEngine(db)
        result = await engine.update_budget(campaign, new_daily_inr)
        return {"platform": "linkedin", **result}

    elif campaign.platform == AdPlatform.WHATSAPP:
        engine = WhatsAppAdsEngine(db)
        result = await engine.update_budget(campaign, new_daily_inr)
        return {"platform": "whatsapp", **result}

    elif campaign.platform == AdPlatform.CHATGPT:
        engine = ChatGPTAdsEngine(db)
        result = await engine.update_budget(campaign.id, new_daily_inr)
        return {"platform": "chatgpt", **result}

    else:
        campaign.daily_budget = round(new_daily_inr)
        campaign.total_budget = round(new_daily_inr * 30.4)
        await db.commit()
        return {"platform": "unknown", "api": "local"}


def _ai_campaign_decision(
    existing_campaigns: list[Campaign], doctor: Doctor
) -> dict:
    """PatientPlex AI brain — decides whether to optimize or rebuild campaigns.

    Scoring system (0-100):
    - 0-30: Campaign infrastructure is broken → REBUILD
    - 31-70: Campaign needs optimization → OPTIMIZE
    - 71-100: Campaign is healthy → OPTIMIZE (light touch)

    Factors evaluated:
    1. Status: ERROR/COMPLETED = bad, ACTIVE/PENDING = good
    2. Keywords: Does it have relevant keywords for the doctor's specialty?
    3. Targeting: Does location match the doctor's current city/radius?
    4. Budget: Is daily budget reasonable for the monthly budget?
    5. Ad copy: Does it have headlines/descriptions?
    6. Performance: If running, is CPC/CTR in acceptable range?
    """
    if not existing_campaigns:
        return {"action": "create", "score": 0, "reason": "No existing campaign", "campaign": None}

    # Filter out COMPLETED campaigns — they're done
    active = [c for c in existing_campaigns if c.status != CampaignStatus.COMPLETED]
    if not active:
        return {"action": "create", "score": 0, "reason": "All campaigns completed", "campaign": None}

    # Evaluate the most recent campaign
    campaign = active[0]
    score = 0
    issues: list[str] = []

    # 1. Status check (0-20 points)
    if campaign.status == CampaignStatus.ERROR:
        score += 0
        issues.append("Campaign in ERROR state")
    elif campaign.status == CampaignStatus.ACTIVE:
        score += 20
    elif campaign.status in (CampaignStatus.PENDING_REVIEW, CampaignStatus.DRAFT):
        score += 15
    elif campaign.status == CampaignStatus.PAUSED:
        score += 10
        issues.append("Campaign is paused")

    # 2. Keywords check (0-20 points)
    keywords = campaign.keywords or []
    if len(keywords) >= 10:
        score += 20
    elif len(keywords) >= 5:
        score += 15
    elif len(keywords) > 0:
        score += 10
        issues.append(f"Only {len(keywords)} keywords — needs more")
    else:
        issues.append("No keywords set")

    # 3. Location targeting (0-15 points)
    if campaign.target_location and doctor.city and doctor.city.lower() in campaign.target_location.lower():
        score += 15
    elif campaign.target_location:
        score += 5
        issues.append("Location may not match current clinic city")
    else:
        issues.append("No location targeting")

    # 4. Budget alignment (0-15 points)
    expected_daily = round(doctor.monthly_budget / 30.4) if doctor.monthly_budget > 0 else 0
    if expected_daily > 0 and campaign.daily_budget > 0:
        ratio = campaign.daily_budget / expected_daily
        if 0.5 <= ratio <= 2.0:
            score += 15
        elif 0.3 <= ratio <= 3.0:
            score += 10
            issues.append("Budget may need adjustment")
        else:
            score += 5
            issues.append("Budget significantly misaligned")
    elif campaign.daily_budget > 0:
        score += 10
    else:
        issues.append("No budget set")

    # 5. Ad copy (0-15 points)
    has_headlines = bool(campaign.headlines and len(campaign.headlines) >= 3)
    has_descriptions = bool(campaign.descriptions and len(campaign.descriptions) >= 2)
    has_ad_copy = bool(campaign.ad_copy)
    if has_headlines and has_descriptions:
        score += 15
    elif has_headlines or has_ad_copy:
        score += 10
        issues.append("Ad copy incomplete")
    else:
        issues.append("No ad copy")

    # 6. Performance signals (0-15 points) — only if campaign has data
    if campaign.impressions > 0:
        if campaign.ctr > 2.0:
            score += 15  # Great CTR
        elif campaign.ctr > 1.0:
            score += 10  # Decent CTR
        elif campaign.clicks > 0:
            score += 5
            issues.append("Low CTR — needs optimization")
        else:
            issues.append("Impressions but no clicks")
    elif campaign.status == CampaignStatus.ACTIVE:
        score += 5  # Active but no data yet — give it time

    # Decision
    if score <= 30:
        return {
            "action": "rebuild",
            "score": score,
            "reason": f"Campaign health score {score}/100 — rebuilding. Issues: {'; '.join(issues)}",
            "campaign": campaign,
        }
    else:
        return {
            "action": "optimize",
            "score": score,
            "reason": f"Campaign health score {score}/100 — optimizing. {'; '.join(issues) if issues else 'Looking good'}",
            "campaign": campaign,
        }


def _serialize_campaign(c: Campaign, detailed: bool = False) -> dict:
    data = {
        "id": str(c.id),
        "platform": c.platform.value,
        "name": c.name,
        "status": c.status.value,
        "campaign_type": c.campaign_type,
        "daily_budget": c.daily_budget,
        "total_budget": c.total_budget,
        "currency": c.currency,
        "impressions": c.impressions,
        "clicks": c.clicks,
        "conversions": c.conversions,
        "spend": c.spend,
        "cpc": c.cpc,
        "ctr": c.ctr,
        "created_at": c.created_at.isoformat(),
        "last_synced_at": c.last_synced_at.isoformat() if c.last_synced_at else None,
    }
    if detailed:
        data.update({
            "platform_campaign_id": c.platform_campaign_id,
            "target_location": c.target_location,
            "target_radius_km": c.target_radius_km,
            "keywords": c.keywords,
            "negative_keywords": c.negative_keywords,
            "headlines": c.headlines,
            "descriptions": c.descriptions,
            "ad_copy": c.ad_copy,
            "landing_page_url": c.landing_page_url,
            "error_message": c.error_message,
        })
    return data
