"""API endpoints for the PatientPlex AI Knowledge Base.

Exposes all benchmark data, marketing expertise, and knowledge library
to the frontend dashboard and to internal AI services.
"""

from fastapi import APIRouter, Query
from typing import Optional

from app.services.ai_knowledge_base import knowledge_base, Specialty
from app.services.marketing_expertise import marketing_expertise
from app.services.knowledge_library import knowledge_library

router = APIRouter(prefix="/knowledge", tags=["AI Knowledge Base"])


# ---------------------------------------------------------------------------
# Benchmark Data
# ---------------------------------------------------------------------------

@router.get("/specialties")
async def list_specialties():
    """List all supported specialties with summary metrics."""
    return {"specialties": knowledge_base.get_all_specialties()}


@router.get("/benchmark/{specialty}")
async def get_benchmark(specialty: str):
    """Get full benchmark data for a specialty."""
    try:
        spec = Specialty(specialty)
    except ValueError:
        return {"error": f"Unknown specialty: {specialty}", "available": [s.value for s in Specialty]}
    bm = knowledge_base.get_benchmark(spec)
    return {
        "specialty": bm.specialty.value,
        "google_ads": {
            "cpc_range": f"₹{bm.google_cpc_low}-{bm.google_cpc_high}",
            "cpl_range": f"₹{bm.google_cpl_low}-{bm.google_cpl_high}",
            "cpql_top_quartile": bm.google_cpql_top_quartile,
            "cpql_market_median": bm.google_cpql_market_median,
            "conversion_rate": f"{bm.google_conversion_rate_low}-{bm.google_conversion_rate_high}%",
        },
        "meta_ads": {
            "ctwa_cpl_range": f"₹{bm.meta_ctwa_cpl_low}-{bm.meta_ctwa_cpl_high}",
            "form_cpl_range": f"₹{bm.meta_form_cpl_low}-{bm.meta_form_cpl_high}",
            "cpql_range": f"₹{bm.meta_cpql_low}-{bm.meta_cpql_high}",
            "qualified_rate": f"{bm.meta_qualified_rate_low}-{bm.meta_qualified_rate_high}%",
        },
        "economics": {
            "consultation_fee": f"₹{bm.consultation_fee_low}-{bm.consultation_fee_high}",
            "avg_treatment_value": bm.avg_treatment_value,
            "high_value_treatment": bm.high_value_treatment,
            "high_value_cost": bm.high_value_treatment_cost,
            "patient_consideration_days": bm.patient_consideration_days,
            "repeat_rate": f"{bm.repeat_visit_rate}%",
            "ltv_months": bm.lifetime_value_months,
        },
        "campaign": {
            "recommended_daily_budget": f"₹{bm.recommended_daily_budget_low}-{bm.recommended_daily_budget_high}",
            "geo_radius_km": bm.recommended_geo_radius_km,
            "peak_hours": bm.peak_search_hours,
            "peak_days": bm.peak_search_days,
        },
        "keywords": bm.top_keywords,
        "negative_keywords": bm.negative_keywords,
        "content": {
            "reel_topics": bm.reel_topics,
            "patient_faqs": bm.patient_questions,
        },
        "compliance": {"banned_claims": bm.banned_claims},
    }


@router.get("/estimate-roi")
async def estimate_roi(
    specialty: str = Query(..., description="Specialty key (e.g. dental_general)"),
    city: str = Query(..., description="City name (e.g. mumbai)"),
    monthly_budget: float = Query(..., description="Monthly ad budget in INR"),
):
    """Estimate ROI for a clinic based on specialty, city, and budget."""
    try:
        spec = Specialty(specialty)
    except ValueError:
        return {"error": f"Unknown specialty: {specialty}"}
    return knowledge_base.estimate_roi(spec, city, monthly_budget)


@router.get("/campaign-template")
async def get_campaign_template(
    specialty: str = Query(...),
    city: str = Query(...),
    monthly_budget: float = Query(...),
):
    """Generate a complete campaign template for a new clinic."""
    try:
        spec = Specialty(specialty)
    except ValueError:
        return {"error": f"Unknown specialty: {specialty}"}
    return knowledge_base.get_campaign_template(spec, city, monthly_budget)


@router.get("/receptionist-knowledge/{specialty}")
async def get_receptionist_knowledge(specialty: str):
    """Get AI receptionist knowledge for a specialty."""
    try:
        spec = Specialty(specialty)
    except ValueError:
        return {"error": f"Unknown specialty: {specialty}"}
    return knowledge_base.get_receptionist_knowledge(spec)


@router.get("/content-calendar")
async def get_content_calendar(
    specialty: str = Query(...),
    city: str = Query(...),
):
    """Generate monthly content calendar for a clinic."""
    try:
        spec = Specialty(specialty)
    except ValueError:
        return {"error": f"Unknown specialty: {specialty}"}
    return knowledge_base.get_content_calendar(spec, city)


# ---------------------------------------------------------------------------
# Marketing Expertise
# ---------------------------------------------------------------------------

@router.get("/marketing/campaign-structure")
async def get_campaign_structure(
    specialty: str = Query(...),
    city: str = Query(...),
    monthly_budget: float = Query(...),
):
    """Get recommended Google Ads campaign structure."""
    return marketing_expertise.get_campaign_structure(specialty, city, monthly_budget)


@router.get("/marketing/negative-keywords/{specialty}")
async def get_negative_keywords(specialty: str):
    """Get negative keyword list for a specialty."""
    return {"specialty": specialty, "negative_keywords": marketing_expertise.get_negative_keywords(specialty)}


@router.get("/marketing/bidding-strategy")
async def get_bidding_strategy(
    campaign_age_days: int = Query(...),
    total_conversions: int = Query(...),
):
    """Get recommended bidding strategy based on campaign maturity."""
    return marketing_expertise.get_bidding_strategy(campaign_age_days, total_conversions)


@router.get("/marketing/ad-copy-formulas")
async def get_ad_copy_formulas():
    """Get ad copy generation templates and NMC compliance rules."""
    return marketing_expertise.get_ad_copy_formulas()


@router.get("/marketing/meta-ads")
async def get_meta_ads_expertise():
    """Get Meta/Facebook/Instagram Ads best practices."""
    return marketing_expertise.get_meta_ads_expertise()


@router.get("/marketing/nurture-sequence/{specialty}")
async def get_nurture_sequence(specialty: str):
    """Get WhatsApp nurture message templates for a specialty."""
    return {"specialty": specialty, "sequences": marketing_expertise.get_nurture_sequence(specialty)}


@router.get("/marketing/daily-checklist")
async def get_daily_checklist():
    """Get the performance marketer's daily optimization checklist."""
    return {"checklist": marketing_expertise.get_daily_checklist()}


@router.post("/marketing/evaluate-campaign")
async def evaluate_campaign_health(metrics: dict):
    """Evaluate a campaign's health and suggest optimization actions."""
    return marketing_expertise.evaluate_campaign_health(metrics)


# ---------------------------------------------------------------------------
# Knowledge Library (Books & Frameworks)
# ---------------------------------------------------------------------------

@router.get("/library/books")
async def list_books():
    """List all books and frameworks in the knowledge library."""
    return {"books": knowledge_library.get_all_books()}


@router.get("/library/book/{key}")
async def get_book(key: str):
    """Get a specific book's full data including principles and AI application."""
    book = knowledge_library.get_book(key)
    if not book:
        return {"error": f"Book not found: {key}"}
    return book


@router.get("/library/principles/{task}")
async def get_principles_for_task(task: str):
    """Get relevant principles for a specific task.

    Tasks: ad_copy, bidding, nurture, sales, onboarding, retention, content, landing_page
    """
    principles = knowledge_library.get_principles_for_task(task)
    if not principles:
        return {"error": f"Unknown task: {task}", "available_tasks": ["ad_copy", "bidding", "nurture", "sales", "onboarding", "retention", "content", "landing_page"]}
    return {"task": task, "principles": principles}


@router.get("/library/category/{category}")
async def get_books_by_category(category: str):
    """Get all knowledge in a category.

    Categories: marketing_foundations, psychology, strategy, ai_strategy,
    healthcare_specific, market_intelligence, sales, ux, product
    """
    books = knowledge_library.get_by_category(category)
    return {"category": category, "books": books}
