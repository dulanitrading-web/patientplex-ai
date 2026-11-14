"""SEO endpoints — website audit, keywords, schema markup, blog content, reports.

Provides:
- On-page SEO audit for clinic websites
- Keyword research and suggestions by specialty
- JSON-LD schema markup generation (MedicalBusiness, Physician)
- AI-generated NMC-compliant blog outlines
- Monthly SEO performance reports
"""

from fastapi import APIRouter, Depends
from pydantic import BaseModel
from sqlalchemy.ext.asyncio import AsyncSession

from app.api.v1.auth import get_current_doctor
from app.db.session import get_db
from app.models.doctor import Doctor
from app.services.seo_service import seo_service

router = APIRouter(prefix="/seo", tags=["seo"])


# ─── Request Models ───

class AuditRequest(BaseModel):
    url: str = ""


class KeywordRequest(BaseModel):
    treatment: str = ""


class BlogOutlineRequest(BaseModel):
    topic: str


# ─── Endpoints ───

@router.post("/audit")
async def run_seo_audit(
    body: AuditRequest,
    doctor: Doctor = Depends(get_current_doctor),
):
    """Run an on-page SEO audit on the clinic's website.

    Returns a score, individual check results, and actionable recommendations.
    """
    return await seo_service.audit_website(doctor, body.url)


@router.get("/keywords")
async def get_keywords(
    treatment: str = "",
    doctor: Doctor = Depends(get_current_doctor),
):
    """Get keyword suggestions for the clinic's specialty and location.

    Returns keywords with estimated search volume, competition, and CPC.
    """
    return await seo_service.get_keyword_suggestions(doctor, treatment)


@router.get("/schema")
async def generate_schema_markup(
    doctor: Doctor = Depends(get_current_doctor),
):
    """Generate JSON-LD schema markup for the clinic website.

    Returns MedicalBusiness schema that improves Google rich snippets.
    """
    return await seo_service.generate_schema(doctor)


@router.post("/blog/outline")
async def generate_blog_outline(
    body: BlogOutlineRequest,
    doctor: Doctor = Depends(get_current_doctor),
):
    """Generate an NMC-compliant blog post outline for organic SEO.

    Returns a keyword-optimized outline with H2 sections and SEO tips.
    """
    return await seo_service.generate_blog_outline(doctor, body.topic)


@router.get("/report")
async def get_seo_report(
    days: int = 30,
    doctor: Doctor = Depends(get_current_doctor),
):
    """Get the monthly SEO performance report.

    Returns: organic traffic, keyword rankings, top pages,
    local SEO metrics, and recommendations.
    """
    return await seo_service.get_seo_report(doctor, days)
