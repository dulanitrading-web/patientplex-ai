"""Campaign management endpoints — create, monitor, and optimize ad campaigns."""

from datetime import datetime, timezone
from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, Query
from pydantic import BaseModel
from sqlalchemy import and_, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.api.v1.auth import get_current_doctor
from app.db.session import get_db
from app.models.campaign import AdPlatform, Campaign, CampaignStatus
from app.models.doctor import Doctor
from app.services.google_ads_engine import GoogleAdsEngine
from app.services.meta_ads_engine import MetaAdsEngine
from app.services.chatgpt_ads_engine import ChatGPTAdsEngine
from app.services.linkedin_ads_engine import LinkedInAdsEngine
from app.services.whatsapp_ads_engine import WhatsAppAdsEngine

router = APIRouter(prefix="/campaigns", tags=["campaigns"])


class LaunchRequest(BaseModel):
    platforms: list[str] = ["GOOGLE", "META", "CHATGPT", "LINKEDIN", "WHATSAPP"]  # Which platforms to launch on


class BudgetUpdate(BaseModel):
    daily_budget: int


@router.post("/launch")
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


@router.put("/{campaign_id}/pause")
async def pause_campaign(
    campaign_id: UUID,
    doctor: Doctor = Depends(get_current_doctor),
    db: AsyncSession = Depends(get_db),
):
    """Pause an active campaign."""
    campaign = await _get_campaign(campaign_id, doctor.id, db)
    if campaign.status != CampaignStatus.ACTIVE:
        raise HTTPException(status_code=400, detail="Campaign is not active")

    if campaign.platform == AdPlatform.GOOGLE:
        engine = GoogleAdsEngine(db)
        await engine.pause_campaign(campaign)
    else:
        campaign.status = CampaignStatus.PAUSED
        await db.commit()

    return {"message": "Campaign paused", "campaign_id": str(campaign_id)}


@router.put("/{campaign_id}/resume")
async def resume_campaign(
    campaign_id: UUID,
    doctor: Doctor = Depends(get_current_doctor),
    db: AsyncSession = Depends(get_db),
):
    """Resume a paused campaign."""
    campaign = await _get_campaign(campaign_id, doctor.id, db)
    if campaign.status != CampaignStatus.PAUSED:
        raise HTTPException(status_code=400, detail="Campaign is not paused")

    if campaign.platform == AdPlatform.GOOGLE:
        engine = GoogleAdsEngine(db)
        await engine.resume_campaign(campaign)
    else:
        campaign.status = CampaignStatus.ACTIVE
        await db.commit()

    return {"message": "Campaign resumed", "campaign_id": str(campaign_id)}


@router.put("/{campaign_id}/budget")
async def update_budget(
    campaign_id: UUID,
    body: BudgetUpdate,
    doctor: Doctor = Depends(get_current_doctor),
    db: AsyncSession = Depends(get_db),
):
    """Update a campaign's daily budget."""
    campaign = await _get_campaign(campaign_id, doctor.id, db)

    if campaign.platform == AdPlatform.GOOGLE:
        engine = GoogleAdsEngine(db)
        await engine.update_budget(campaign, body.daily_budget)
    else:
        campaign.daily_budget = body.daily_budget
        campaign.total_budget = round(body.daily_budget * 30.4)
        await db.commit()

    return {"message": "Budget updated", "daily_budget": body.daily_budget}


@router.post("/{campaign_id}/sync")
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
            "last_synced_at": c.last_synced_at.isoformat() if c.last_synced_at else None,
            "error_message": c.error_message,
        })
    return data
