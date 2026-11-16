"""Pydantic schemas for doctor signup, onboarding, and API responses."""

import re
from datetime import datetime
from typing import Optional
from uuid import UUID

from pydantic import BaseModel, EmailStr, Field, field_validator

from app.models.doctor import Specialty

# Indian mobile: 10 digits starting with 6-9, optionally prefixed with +91 or 91
_INDIAN_PHONE_RE = re.compile(r"^(?:\+?91)?([6-9]\d{9})$")


def _normalize_indian_phone(v: str) -> str:
    """Validate and normalize an Indian phone number to +91XXXXXXXXXX."""
    digits = re.sub(r"[\s\-()]+", "", v.strip())
    m = _INDIAN_PHONE_RE.match(digits)
    if not m:
        raise ValueError(
            "Enter a valid Indian mobile number (10 digits starting with 6-9)"
        )
    return f"+91{m.group(1)}"


# ---------------------------------------------------------------------------
# Auth
# ---------------------------------------------------------------------------


class DoctorCreate(BaseModel):
    """Payload for new doctor registration."""

    full_name: str = Field(..., min_length=2, max_length=255)
    email: EmailStr
    phone: str = Field(..., min_length=10, max_length=20)
    password: str = Field(..., min_length=8, max_length=128)

    @field_validator("phone")
    @classmethod
    def validate_phone(cls, v: str) -> str:
        return _normalize_indian_phone(v)


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
    clinic_name: str | None = Field(default=None, max_length=255)


class DoctorOnboardingStep2(BaseModel):
    """Step 2: clinic address and geo-targeting radius."""

    clinic_name: str | None = Field(default=None, max_length=255)
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

    @field_validator("whatsapp_number")
    @classmethod
    def validate_whatsapp_phone(cls, v: str) -> str:
        return _normalize_indian_phone(v)


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
    google_ads_connected: bool = False
    google_ads_customer_id: str | None = None
    meta_ads_connected: bool = False
    meta_ads_account_id: str | None = None
    twilio_phone_number: str | None = None
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


# ---------------------------------------------------------------------------
# Profile editing & password reset
# ---------------------------------------------------------------------------


class ProfileUpdate(BaseModel):
    """Partial update to doctor profile. All fields optional."""

    full_name: Optional[str] = Field(default=None, min_length=2, max_length=255)
    phone: Optional[str] = Field(default=None, min_length=10, max_length=20)
    clinic_name: Optional[str] = Field(default=None, max_length=255)
    clinic_address: Optional[str] = Field(default=None, min_length=5)
    city: Optional[str] = Field(default=None, min_length=2, max_length=100)
    state: Optional[str] = Field(default=None, min_length=2, max_length=100)
    pincode: Optional[str] = Field(default=None, min_length=6, max_length=10)
    services: Optional[list[str]] = None
    monthly_budget: Optional[int] = Field(default=None, ge=1000)

    @field_validator("phone")
    @classmethod
    def validate_phone(cls, v: str | None) -> str | None:
        if v is None:
            return v
        return _normalize_indian_phone(v)


class ForgotPasswordRequest(BaseModel):
    email: EmailStr


class ResetPasswordRequest(BaseModel):
    token: str
    new_password: str = Field(..., min_length=8, max_length=128)
