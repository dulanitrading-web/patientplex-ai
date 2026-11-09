"""ChatGPT Ads endpoints — manage sponsored answers in ChatGPT search."""

from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel
from sqlalchemy.ext.asyncio import AsyncSession

from app.api.v1.auth import get_current_doctor
from app.db.session import get_db
from app.models.doctor import Doctor
from app.services.chatgpt_ads_engine import ChatGPTAdsEngine

router = APIRouter(prefix="/chatgpt-ads", tags=["chatgpt-ads"])


class CreateCampaignRequest(BaseModel):
    campaign_type: str = "SPONSORED_ANSWER"
    bid_strategy: str = "balanced"


class GenerateContentRequest(BaseModel):
    treatment: str


@router.post("/campaigns")
async def create_chatgpt_campaign(
    body: CreateCampaignRequest,
    doctor: Doctor = Depends(get_current_doctor),
    db: AsyncSession = Depends(get_db),
):
    """Create a ChatGPT sponsored answer campaign.

    Targets health-related queries relevant to the doctor's specialty.
    """
    if not doctor.onboarding_completed:
        raise HTTPException(
            status_code=400, detail="Complete onboarding before launching campaigns"
        )

    engine = ChatGPTAdsEngine(db)
    campaign = await engine.create_campaign(
        doctor,
        campaign_type=body.campaign_type,
        bid_strategy=body.bid_strategy,
    )
    await db.commit()

    return {
        "message": "ChatGPT ads campaign created",
        "campaign_id": str(campaign.id),
        "name": campaign.name,
        "status": campaign.status.value,
        "daily_budget": campaign.daily_budget,
    }


@router.get("/campaigns/{campaign_id}/performance")
async def get_performance(
    campaign_id: int,
    doctor: Doctor = Depends(get_current_doctor),
    db: AsyncSession = Depends(get_db),
):
    """Get ChatGPT campaign performance metrics."""
    engine = ChatGPTAdsEngine(db)
    return await engine.get_campaign_performance(campaign_id)


@router.post("/campaigns/{campaign_id}/optimize-keywords")
async def optimize_keywords(
    campaign_id: int,
    doctor: Doctor = Depends(get_current_doctor),
    db: AsyncSession = Depends(get_db),
):
    """AI-powered keyword optimization for ChatGPT search queries."""
    engine = ChatGPTAdsEngine(db)
    return await engine.optimize_keywords(campaign_id)


@router.post("/generate-content")
async def generate_content(
    body: GenerateContentRequest,
    doctor: Doctor = Depends(get_current_doctor),
    db: AsyncSession = Depends(get_db),
):
    """Generate sponsored answer content for a treatment."""
    engine = ChatGPTAdsEngine(db)
    return await engine.generate_sponsored_content(doctor.id, body.treatment)


@router.put("/campaigns/{campaign_id}/pause")
async def pause_campaign(
    campaign_id: int,
    doctor: Doctor = Depends(get_current_doctor),
    db: AsyncSession = Depends(get_db),
):
    """Pause a ChatGPT ads campaign."""
    engine = ChatGPTAdsEngine(db)
    return await engine.pause_campaign(campaign_id)


@router.put("/campaigns/{campaign_id}/resume")
async def resume_campaign(
    campaign_id: int,
    doctor: Doctor = Depends(get_current_doctor),
    db: AsyncSession = Depends(get_db),
):
    """Resume a paused ChatGPT ads campaign."""
    engine = ChatGPTAdsEngine(db)
    return await engine.resume_campaign(campaign_id)


@router.get("/keyword-suggestions")
async def keyword_suggestions(
    specialty: str,
    location: str | None = None,
    doctor: Doctor = Depends(get_current_doctor),
    db: AsyncSession = Depends(get_db),
):
    """Get keyword suggestions for ChatGPT ad targeting."""
    engine = ChatGPTAdsEngine(db)
    return await engine.get_keyword_suggestions(specialty, location)


@router.get("/campaigns/{campaign_id}/roi")
async def campaign_roi(
    campaign_id: int,
    doctor: Doctor = Depends(get_current_doctor),
    db: AsyncSession = Depends(get_db),
):
    """Calculate ROI for a ChatGPT ads campaign."""
    engine = ChatGPTAdsEngine(db)
    return await engine.calculate_roi(campaign_id)
