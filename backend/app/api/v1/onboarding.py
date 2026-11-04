"""Onboarding wizard endpoints.

Guides the doctor through four steps (specialty, address, budget, WhatsApp)
plus Google Calendar OAuth integration.
"""

from fastapi import APIRouter, Depends, HTTPException, Query, status
from fastapi.responses import RedirectResponse
from sqlalchemy.ext.asyncio import AsyncSession

from app.api.v1.auth import get_current_doctor
from app.db.session import get_db
from app.models.doctor import Doctor
from app.schemas.doctor import (
    DoctorOnboardingStep1,
    DoctorOnboardingStep2,
    DoctorOnboardingStep3,
    DoctorOnboardingStep4,
    DoctorResponse,
    OnboardingStatusResponse,
)
from app.schemas.specialty import SPECIALTY_CONFIGS
from app.services.google_calendar import google_calendar_service

router = APIRouter(prefix="/onboarding", tags=["onboarding"])


# ---------------------------------------------------------------------------
# Specialty catalogue
# ---------------------------------------------------------------------------


@router.get("/specialties")
async def list_specialties() -> list[dict]:
    """Return all supported specialties with their default services and keywords.

    This endpoint is public so the frontend can pre-populate the selection UI
    before the doctor reaches that onboarding step.
    """
    return [
        {
            "specialty": cfg.specialty,
            "default_services": cfg.default_services,
            "default_keywords": cfg.default_keywords,
        }
        for cfg in SPECIALTY_CONFIGS.values()
    ]


# ---------------------------------------------------------------------------
# Onboarding steps
# ---------------------------------------------------------------------------


@router.put("/step1", response_model=DoctorResponse)
async def onboarding_step1(
    body: DoctorOnboardingStep1,
    doctor: Doctor = Depends(get_current_doctor),
    db: AsyncSession = Depends(get_db),
) -> DoctorResponse:
    """Step 1: save specialty, services, and clinic name."""
    doctor.specialty = body.specialty
    doctor.services = body.services
    doctor.clinic_name = body.clinic_name
    if doctor.onboarding_step < 2:
        doctor.onboarding_step = 2

    # Auto-generate a subdomain slug from the doctor's name
    if not doctor.subdomain_slug:
        slug = doctor.full_name.lower().replace(" ", "-").replace(".", "")
        doctor.subdomain_slug = slug

    await db.commit()
    await db.refresh(doctor)
    return DoctorResponse.model_validate(doctor)


@router.put("/step2", response_model=DoctorResponse)
async def onboarding_step2(
    body: DoctorOnboardingStep2,
    doctor: Doctor = Depends(get_current_doctor),
    db: AsyncSession = Depends(get_db),
) -> DoctorResponse:
    """Step 2: save clinic address and geo-targeting configuration."""
    doctor.clinic_address = body.clinic_address
    doctor.city = body.city
    doctor.state = body.state
    doctor.pincode = body.pincode
    doctor.geo_radius_km = body.geo_radius_km
    if doctor.onboarding_step < 3:
        doctor.onboarding_step = 3

    await db.commit()
    await db.refresh(doctor)
    return DoctorResponse.model_validate(doctor)


@router.put("/step3", response_model=DoctorResponse)
async def onboarding_step3(
    body: DoctorOnboardingStep3,
    doctor: Doctor = Depends(get_current_doctor),
    db: AsyncSession = Depends(get_db),
) -> DoctorResponse:
    """Step 3: save monthly advertising budget."""
    doctor.monthly_budget = body.monthly_budget
    doctor.currency = body.currency
    if doctor.onboarding_step < 4:
        doctor.onboarding_step = 4

    await db.commit()
    await db.refresh(doctor)
    return DoctorResponse.model_validate(doctor)


@router.put("/step4", response_model=DoctorResponse)
async def onboarding_step4(
    body: DoctorOnboardingStep4,
    doctor: Doctor = Depends(get_current_doctor),
    db: AsyncSession = Depends(get_db),
) -> DoctorResponse:
    """Step 4: save WhatsApp number for patient notifications."""
    doctor.whatsapp_number = body.whatsapp_number
    if doctor.onboarding_step < 5:
        doctor.onboarding_step = 5

    await db.commit()
    await db.refresh(doctor)
    return DoctorResponse.model_validate(doctor)


# ---------------------------------------------------------------------------
# Google Calendar OAuth
# ---------------------------------------------------------------------------


@router.get("/google-calendar/connect")
async def google_calendar_connect(
    doctor: Doctor = Depends(get_current_doctor),
) -> dict:
    """Return the Google OAuth consent URL for calendar access.

    The frontend should redirect the doctor to this URL.
    """
    auth_url = await google_calendar_service.get_auth_url(str(doctor.id))
    return {"auth_url": auth_url}


@router.get("/google-calendar/callback")
async def google_calendar_callback(
    code: str = Query(...),
    state: str = Query(...),
    db: AsyncSession = Depends(get_db),
) -> RedirectResponse:
    """Handle the Google OAuth callback.

    Exchanges the authorization code for tokens, stores them against the
    doctor record, and redirects to the frontend onboarding page.
    """
    try:
        result = await google_calendar_service.handle_callback(
            code=code, doctor_id=state, db=db
        )
    except Exception as exc:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Failed to connect Google Calendar: {exc}",
        )

    # Redirect back to the frontend onboarding page
    return RedirectResponse(url="/onboarding?calendar=connected")


# ---------------------------------------------------------------------------
# Status and completion
# ---------------------------------------------------------------------------


@router.get("/status", response_model=OnboardingStatusResponse)
async def onboarding_status(
    doctor: Doctor = Depends(get_current_doctor),
) -> OnboardingStatusResponse:
    """Return the current onboarding progress for the authenticated doctor."""
    return OnboardingStatusResponse(
        current_step=doctor.onboarding_step,
        onboarding_completed=doctor.onboarding_completed,
        steps={
            "step1_specialty": doctor.specialty is not None,
            "step2_address": doctor.clinic_address is not None,
            "step3_budget": doctor.monthly_budget > 0,
            "step4_whatsapp": doctor.whatsapp_number is not None,
            "google_calendar": doctor.google_calendar_connected,
        },
    )


@router.post("/complete", response_model=DoctorResponse)
async def complete_onboarding(
    doctor: Doctor = Depends(get_current_doctor),
    db: AsyncSession = Depends(get_db),
) -> DoctorResponse:
    """Mark onboarding as complete.

    Validates that all required steps have been filled in. Google Calendar
    connection is recommended but not mandatory.

    Raises 400 if any required step is incomplete.
    """
    missing: list[str] = []
    if doctor.specialty is None:
        missing.append("specialty (step 1)")
    if doctor.clinic_address is None:
        missing.append("clinic address (step 2)")
    if doctor.monthly_budget <= 0:
        missing.append("monthly budget (step 3)")
    if doctor.whatsapp_number is None:
        missing.append("WhatsApp number (step 4)")

    if missing:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Incomplete onboarding. Missing: {', '.join(missing)}",
        )

    doctor.onboarding_completed = True
    await db.commit()
    await db.refresh(doctor)
    return DoctorResponse.model_validate(doctor)
