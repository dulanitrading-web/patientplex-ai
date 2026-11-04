"""Pydantic schemas for doctor signup, onboarding, and API responses."""

from datetime import datetime
from uuid import UUID

from pydantic import BaseModel, EmailStr, Field

from app.models.doctor import Specialty


# ---------------------------------------------------------------------------
# Auth
# ---------------------------------------------------------------------------


class DoctorCreate(BaseModel):
    """Payload for new doctor registration."""

    full_name: str = Field(..., min_length=2, max_length=255)
    email: EmailStr
    phone: str = Field(..., min_length=10, max_length=20)
    password: str = Field(..., min_length=8, max_length=128)


class DoctorLogin(BaseModel):
    """Payload for doctor login."""

    email: EmailStr
    password: str


class TokenResponse(BaseModel):
    """JWT token returned after successful authentication."""

    access_token: str
    token_type: str = "bearer"


# ---------------------------------------------------------------------------
# Onboarding steps
# ---------------------------------------------------------------------------


class DoctorOnboardingStep1(BaseModel):
    """Step 1: specialty and services selection."""

    specialty: Specialty
    services: list[str] = Field(..., min_length=1)
    clinic_name: str = Field(..., min_length=2, max_length=255)


class DoctorOnboardingStep2(BaseModel):
    """Step 2: clinic address and geo-targeting radius."""

    clinic_address: str = Field(..., min_length=5)
    city: str = Field(..., min_length=2, max_length=100)
    state: str = Field(..., min_length=2, max_length=100)
    pincode: str = Field(..., min_length=6, max_length=10)
    geo_radius_km: int = Field(default=5, ge=1, le=50)


class DoctorOnboardingStep3(BaseModel):
    """Step 3: monthly advertising budget."""

    monthly_budget: int = Field(default=10000, ge=1000)
    currency: str = Field(default="INR", max_length=3)


class DoctorOnboardingStep4(BaseModel):
    """Step 4: WhatsApp number for patient notifications."""

    whatsapp_number: str = Field(..., min_length=10, max_length=20)


# ---------------------------------------------------------------------------
# Response
# ---------------------------------------------------------------------------


class DoctorResponse(BaseModel):
    """Full doctor profile returned by the API (excludes secrets)."""

    id: UUID
    full_name: str
    email: str
    phone: str
    clinic_name: str | None = None
    specialty: Specialty | None = None
    services: list[str] | None = None
    clinic_address: str | None = None
    city: str | None = None
    state: str | None = None
    pincode: str | None = None
    latitude: float | None = None
    longitude: float | None = None
    geo_radius_km: int
    monthly_budget: int
    currency: str
    google_calendar_connected: bool
    google_calendar_id: str | None = None
    whatsapp_number: str | None = None
    whatsapp_verified: bool
    subdomain_slug: str | None = None
    is_active: bool
    onboarding_step: int
    onboarding_completed: bool
    created_at: datetime
    updated_at: datetime

    model_config = {"from_attributes": True}


class OnboardingStatusResponse(BaseModel):
    """Current onboarding progress summary."""

    current_step: int
    onboarding_completed: bool
    steps: dict[str, bool] = Field(
        ...,
        description="Completion status of each step: step1_specialty, step2_address, step3_budget, step4_whatsapp, google_calendar",
    )
