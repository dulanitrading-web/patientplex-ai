"""Landing page generation and serving endpoints."""

from fastapi import APIRouter, Depends, HTTPException, Response
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.api.v1.auth import get_current_doctor
from app.db.session import get_db
from app.models.doctor import Doctor
from app.services.landing_page_generator import (
    generate_landing_page_html,
    generate_slug,
    generate_treatment_page_html,
)

router = APIRouter(prefix="/landing", tags=["landing-pages"])


@router.post("/generate")
async def generate_landing_page(
    doctor: Doctor = Depends(get_current_doctor),
    db: AsyncSession = Depends(get_db),
):
    """Generate and assign a landing page for the doctor.

    Creates a subdomain slug and returns the generated HTML.
    """
    if not doctor.subdomain_slug:
        doctor.subdomain_slug = generate_slug(doctor)
        await db.commit()

    html = generate_landing_page_html(doctor)

    return {
        "slug": doctor.subdomain_slug,
        "url": f"https://{doctor.subdomain_slug}.patientplex.ai",
        "html_length": len(html),
        "preview_url": f"/api/v1/landing/preview/{doctor.subdomain_slug}",
    }


@router.get("/preview/{slug}")
async def preview_landing_page(slug: str, db: AsyncSession = Depends(get_db)):
    """Serve a doctor's landing page by slug (for preview and production serving)."""
    result = await db.execute(
        select(Doctor).where(Doctor.subdomain_slug == slug)
    )
    doctor = result.scalar_one_or_none()
    if not doctor:
        raise HTTPException(status_code=404, detail="Page not found")

    html = generate_landing_page_html(doctor)
    return Response(content=html, media_type="text/html")


@router.get("/preview/{slug}/{treatment_slug}")
async def preview_treatment_page(
    slug: str, treatment_slug: str, db: AsyncSession = Depends(get_db)
):
    """Serve a treatment-specific landing page."""
    result = await db.execute(
        select(Doctor).where(Doctor.subdomain_slug == slug)
    )
    doctor = result.scalar_one_or_none()
    if not doctor:
        raise HTTPException(status_code=404, detail="Page not found")

    # Convert slug back to treatment name
    treatment = treatment_slug.replace("-", " ").title()

    # Verify this treatment is in the doctor's services
    services_lower = [s.lower() for s in (doctor.services or [])]
    if treatment.lower() not in services_lower:
        raise HTTPException(status_code=404, detail="Treatment page not found")

    html = generate_treatment_page_html(doctor, treatment)
    return Response(content=html, media_type="text/html")


@router.get("/pages")
async def list_landing_pages(
    doctor: Doctor = Depends(get_current_doctor),
):
    """List all landing page URLs for the doctor (main page + treatment pages)."""
    if not doctor.subdomain_slug:
        return {"pages": [], "message": "No landing page generated yet. Call POST /landing/generate first."}

    base_url = f"https://{doctor.subdomain_slug}.patientplex.ai"
    pages = [{"url": base_url, "type": "main", "title": f"{doctor.full_name} — Main Page"}]

    for service in (doctor.services or []):
        treatment_slug = service.lower().replace(" ", "-")
        pages.append({
            "url": f"{base_url}/{treatment_slug}",
            "type": "treatment",
            "title": f"{service} — {doctor.city}",
        })

    return {"pages": pages, "count": len(pages)}
