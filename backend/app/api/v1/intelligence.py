"""Competitive intelligence endpoints."""

from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession

from app.api.v1.auth import get_current_doctor
from app.db.session import get_db
from app.models.doctor import Doctor
from app.services.competitive_intel import CompetitiveIntelService

router = APIRouter(prefix="/intelligence", tags=["intelligence"])


@router.get("/competitors")
async def get_competitor_analysis(
    doctor: Doctor = Depends(get_current_doctor),
    db: AsyncSession = Depends(get_db),
):
    """Get competitive intelligence report for the doctor's market."""
    service = CompetitiveIntelService()
    report = await service.generate_competitive_report(doctor)
    return report


@router.get("/competitors/ads")
async def search_competitor_ads(
    search_term: str | None = None,
    doctor: Doctor = Depends(get_current_doctor),
    db: AsyncSession = Depends(get_db),
):
    """Search competitor ads on Meta Ad Library."""
    service = CompetitiveIntelService()
    terms = [search_term] if search_term else None
    return await service.search_competitor_ads(doctor, terms)
