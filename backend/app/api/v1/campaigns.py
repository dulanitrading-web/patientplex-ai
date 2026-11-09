"""Campaign management endpoints — create, monitor, and optimize ad campaigns."""

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

router = APIRouter(prefix="/campaigns", tags=["campaigns"])


class LaunchRequest(BaseModel):
    platforms: list[str] = ["GOOGLE", "META", "CHATGPT", "LINKEDIN"]  # Which platforms to launch on


class BudgetUpdate(BaseModel):
    daily_budget: int


@router.post("/launch")
async def launch_campaigns(
    body: LaunchRequest,
    doctor: Doctor = Depends(get_current_doctor),
    db: AsyncSession = Depends(get_db),
):
    """Launch ad campaigns on selected platforms from doctor's onboarding data.

    This is the main 'go live' endpoint called after onboarding is complete.
    Creates campaigns on Google Ads and/or Meta based on the doctor's
    specialty, location, budget, and AI-generated ad copy.
    """
    if not doctor.onboarding_completed:
        raise HTTPException(status_code=400, detail="Complete onboarding before launching campaigns")

    results = {}

    if "GOOGLE" in body.platforms:
        engine = GoogleAdsEngine(db)
        campaign = await engine.create_campaign_from_onboarding(doctor)
        results["google"] = {
            "campaign_id": str(campaign.id),
            "name": campaign.name,
            "status": campaign.status.value,
            "daily_budget": campaign.daily_budget,
            "keywords_count": len(campaign.keywords or []),
        }

    if "META" in body.platforms:
        engine = MetaAdsEngine(db)
        campaign = await engine.create_campaign_from_onboarding(doctor)
        results["meta"] = {
            "campaign_id": str(campaign.id),
            "name": campaign.name,
            "status": campaign.status.value,
            "daily_budget": campaign.daily_budget,
        }

    if "CHATGPT" in body.platforms:
        engine = ChatGPTAdsEngine(db)
        campaign = await engine.create_campaign(doctor)
        results["chatgpt"] = {
            "campaign_id": str(campaign.id),
            "name": campaign.name,
            "status": campaign.status.value,
            "daily_budget": campaign.daily_budget,
        }

    if "LINKEDIN" in body.platforms:
        engine = LinkedInAdsEngine(db)
        campaign = await engine.create_referral_campaign(doctor)
        results["linkedin"] = {
            "campaign_id": str(campaign.id),
            "name": campaign.name,
            "status": campaign.status.value,
            "daily_budget": campaign.daily_budget,
        }

    await db.commit()
    return {"message": "Campaigns created", "campaigns": results}


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
