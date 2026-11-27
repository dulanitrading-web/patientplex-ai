"""Authentication endpoints: signup, login, profile, and password reset."""

import logging
import secrets
import time

from fastapi import APIRouter, Depends, HTTPException, Request, status
from fastapi.responses import JSONResponse
from fastapi.security import OAuth2PasswordBearer
import os
from slowapi import Limiter
from slowapi.util import get_remote_address

limiter = Limiter(key_func=get_remote_address, enabled=os.environ.get("TESTING", "").lower() != "true")
from jwt.exceptions import InvalidTokenError as JWTError
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.audit import log_audit
from app.core.config import settings
from app.core.security import create_access_token, hash_password, verify_password, verify_token
from app.db.session import get_db
from app.models.doctor import Doctor
from app.schemas.doctor import (
    DoctorCreate, DoctorLogin, DoctorResponse, TokenResponse,
    ProfileUpdate, ForgotPasswordRequest, ResetPasswordRequest,
)

logger = logging.getLogger(__name__)

_RESET_TOKEN_TTL = 3600  # 1 hour

router = APIRouter(prefix="/auth", tags=["auth"])

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/api/v1/auth/login")


async def get_current_doctor(
    token: str = Depends(oauth2_scheme),
    db: AsyncSession = Depends(get_db),
) -> Doctor:
    """Decode the JWT and return the authenticated Doctor, or raise 401."""
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )
    try:
        payload = verify_token(token)
        doctor_id: str | None = payload.get("sub")
        if doctor_id is None:
            raise credentials_exception
    except JWTError:
        raise credentials_exception

    result = await db.execute(select(Doctor).where(Doctor.id == doctor_id))
    doctor = result.scalar_one_or_none()
    if doctor is None:
        raise credentials_exception
    return doctor


@router.post("/signup", response_model=TokenResponse, status_code=status.HTTP_201_CREATED)
@limiter.limit("20/minute")
async def signup(request: Request, body: DoctorCreate, db: AsyncSession = Depends(get_db)) -> TokenResponse:
    """Register a new doctor account and return a JWT.

    Raises 409 if the email is already registered.
    """
    existing = await db.execute(select(Doctor).where(Doctor.email == body.email))
    if existing.scalar_one_or_none():
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="A doctor with this email already exists.",
        )

    doctor = Doctor(
        full_name=body.full_name,
        email=body.email,
        phone=body.phone,
        password_hash=hash_password(body.password),
    )
    db.add(doctor)
    await db.commit()
    await db.refresh(doctor)

    access_token = create_access_token(data={"sub": str(doctor.id)})

    log_audit(action="signup", actor_id=str(doctor.id), resource="auth", details={"email": doctor.email})

    response = JSONResponse(
        content={
            "access_token": access_token,
            "token_type": "bearer",
            "user": {
                "full_name": doctor.full_name,
                "email": doctor.email,
                "onboarding_completed": doctor.onboarding_completed,
            },
        },
        status_code=status.HTTP_201_CREATED,
    )
    return response


@router.post("/login", response_model=TokenResponse)
@limiter.limit("5/15minutes")
async def login(request: Request, body: DoctorLogin, db: AsyncSession = Depends(get_db)) -> TokenResponse:
    """Authenticate a doctor by email/password and return a JWT.

    Raises 401 on invalid credentials.
    """
    result = await db.execute(select(Doctor).where(Doctor.email == body.email))
    doctor = result.scalar_one_or_none()
    if not doctor or not verify_password(body.password, doctor.password_hash):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid email or password.",
        )

    access_token = create_access_token(data={"sub": str(doctor.id)})

    log_audit(action="login", actor_id=str(doctor.id), resource="auth", details={"email": doctor.email})

    response = JSONResponse(
        content={
            "access_token": access_token,
            "token_type": "bearer",
            "user": {
                "full_name": doctor.full_name,
                "email": doctor.email,
                "onboarding_completed": doctor.onboarding_completed,
            },
        },
    )
    return response


@router.post("/refresh", response_model=TokenResponse)
async def refresh_token(doctor: Doctor = Depends(get_current_doctor)):
    """Issue a fresh JWT for the currently authenticated doctor.

    Call this before the current token expires to keep the session alive.
    The old token remains valid until its own expiry — no revocation.
    """
    new_token = create_access_token(data={"sub": str(doctor.id)})
    return TokenResponse(access_token=new_token, token_type="bearer")


@router.get("/me", response_model=DoctorResponse)
async def get_me(doctor: Doctor = Depends(get_current_doctor)) -> DoctorResponse:
    """Return the profile of the currently authenticated doctor."""
    return DoctorResponse.model_validate(doctor)


@router.put("/profile", response_model=DoctorResponse)
async def update_profile(
    body: ProfileUpdate,
    doctor: Doctor = Depends(get_current_doctor),
    db: AsyncSession = Depends(get_db),
) -> DoctorResponse:
    """Update the authenticated doctor's profile. Only provided fields are changed."""
    update_data = body.model_dump(exclude_unset=True)
    if not update_data:
        raise HTTPException(status_code=400, detail="No fields to update.")

    for field_name, value in update_data.items():
        setattr(doctor, field_name, value)

    await db.commit()
    await db.refresh(doctor)

    log_audit(
        action="profile_update",
        actor_id=str(doctor.id),
        resource="auth",
        details={"fields": list(update_data.keys())},
    )

    return DoctorResponse.model_validate(doctor)


@router.post("/forgot-password")
async def forgot_password(
    body: ForgotPasswordRequest,
    db: AsyncSession = Depends(get_db),
):
    """Request a password reset link. Always returns success to prevent email enumeration."""
    result = await db.execute(select(Doctor).where(Doctor.email == body.email))
    doctor = result.scalar_one_or_none()

    if doctor:
        # Generate token and store in database (survives deploys and horizontal scaling)
        token = secrets.token_urlsafe(48)
        from datetime import datetime, timezone, timedelta
        doctor.reset_token = token
        doctor.reset_token_expires = datetime.now(timezone.utc) + timedelta(seconds=_RESET_TOKEN_TTL)
        await db.commit()

        reset_url = f"{settings.FRONTEND_BASE_URL}/reset-password?token={token}"

        # Send email if email service is configured
        try:
            from app.services.email_service import send_password_reset_email, email_service_configured
            if email_service_configured():
                await send_password_reset_email(
                    email=doctor.email,
                    name=doctor.clinic_name or doctor.name or "Doctor",
                    reset_token=token,
                )
                logger.info("Password reset email sent to %s", body.email)
            else:
                logger.warning(
                    "Password reset requested for %s but email service not configured. "
                    "Token generated but not delivered — configure EMAIL_PROVIDER.", body.email
                )
        except Exception as e:
            logger.error("Failed to send password reset email: %s", e)

    return {"message": "If an account with that email exists, a reset link has been sent."}


@router.post("/reset-password")
async def reset_password(
    body: ResetPasswordRequest,
    db: AsyncSession = Depends(get_db),
):
    """Reset password using a valid reset token."""
    from datetime import datetime, timezone
    result = await db.execute(
        select(Doctor).where(Doctor.reset_token == body.token)
    )
    doctor = result.scalar_one_or_none()
    if not doctor:
        raise HTTPException(status_code=400, detail="Invalid or expired reset token.")
    if not doctor.reset_token_expires or doctor.reset_token_expires < datetime.now(timezone.utc):
        # Clear expired token
        doctor.reset_token = None
        doctor.reset_token_expires = None
        await db.commit()
        raise HTTPException(status_code=400, detail="Invalid or expired reset token.")

    doctor.password_hash = hash_password(body.new_password)
    doctor.reset_token = None
    doctor.reset_token_expires = None
    await db.commit()

    log_audit(action="password_reset", actor_id=str(doctor.id), resource="auth", details={})

    return {"message": "Password has been reset successfully. You can now log in."}


@router.get("/integrations")
async def get_integration_status(
    doctor: Doctor = Depends(get_current_doctor),
    db: AsyncSession = Depends(get_db),
):
    """Return real-time connection status of all integrations.

    Checks actual API keys/credentials configured on the backend
    and whether campaigns exist for each platform.
    """
    from app.models.campaign import Campaign, AdPlatform

    # Check which platforms have campaigns
    result = await db.execute(
        select(Campaign.platform).where(Campaign.doctor_id == doctor.id).distinct()
    )
    active_platforms = {row[0].value for row in result.all()}

    # Check credentials — per-doctor OAuth takes priority over global keys
    # Use getattr with defaults in case columns don't exist yet in DB
    google_ads_configured = bool(getattr(doctor, 'google_ads_connected', False)) or bool(settings.GOOGLE_ADS_DEVELOPER_TOKEN)
    meta_ads_configured = bool(getattr(doctor, 'meta_ads_connected', False)) or bool(settings.META_APP_ID and settings.META_APP_SECRET)
    chatgpt_ads_configured = bool(settings.CHATGPT_ADS_API_KEY)
    linkedin_configured = bool(settings.LINKEDIN_ACCESS_TOKEN)
    twilio_configured = bool(settings.TWILIO_ACCOUNT_SID and settings.TWILIO_AUTH_TOKEN)
    whatsapp_api_configured = bool(settings.WHATSAPP_API_TOKEN)

    def _status(platform_key: str, credentials_ok: bool, doctor_oauth: bool = False) -> str:
        """Determine integration status: connected, active, pending, not_connected."""
        has_campaigns = platform_key in active_platforms
        if doctor_oauth:
            return "connected"  # Doctor personally connected via OAuth
        if has_campaigns and credentials_ok:
            return "connected"
        if has_campaigns and not credentials_ok:
            return "active_draft"  # Campaigns exist but in draft/demo mode
        if credentials_ok:
            return "ready"  # Global credentials set, no per-doctor OAuth yet
        return "not_connected"

    return {
        "google_calendar": {
            "status": "connected" if doctor.google_calendar_connected else "not_connected",
            "detail": "Syncing appointments" if doctor.google_calendar_connected else "Connect to sync appointments",
        },
        "whatsapp": {
            "status": "connected" if (doctor.whatsapp_number and doctor.whatsapp_verified) else ("pending" if doctor.whatsapp_number else "not_connected"),
            "detail": f"{doctor.whatsapp_number}" if doctor.whatsapp_number else "No number configured",
            "number": doctor.whatsapp_number,
            "verified": doctor.whatsapp_verified if doctor.whatsapp_number else False,
        },
        "google_ads": {
            "status": (
                "connected" if getattr(doctor, 'google_ads_connected', False)
                else ("ready" if google_ads_configured else "not_connected")
            ),
            "detail": (
                f"Connected — Account {getattr(doctor, 'google_ads_customer_id', '')}" if getattr(doctor, 'google_ads_connected', False)
                else ("MCC linked — Click Connect to link your Google Ads account" if settings.GOOGLE_ADS_DEVELOPER_TOKEN else "Click Connect to link your Google Ads account")
            ),
            "has_campaigns": "GOOGLE" in active_platforms,
            "credentials_configured": google_ads_configured,
            "doctor_connected": getattr(doctor, 'google_ads_connected', False),
        },
        "meta_ads": {
            "status": _status("META", meta_ads_configured, getattr(doctor, 'meta_ads_connected', False)),
            "detail": (
                f"Connected — Ad Account {getattr(doctor, 'meta_ads_account_id', '')}" if getattr(doctor, 'meta_ads_connected', False)
                else ("Connected — App configured" if (settings.META_APP_ID and settings.META_APP_SECRET) else "Click Connect to link your Meta Ads account")
            ),
            "has_campaigns": "META" in active_platforms,
            "credentials_configured": meta_ads_configured,
            "doctor_connected": getattr(doctor, 'meta_ads_connected', False),
        },
        "chatgpt_ads": {
            "status": _status("CHATGPT", chatgpt_ads_configured),
            "detail": "Connected" if chatgpt_ads_configured else "Add ChatGPT Ads API key to connect",
            "has_campaigns": "CHATGPT" in active_platforms,
            "credentials_configured": chatgpt_ads_configured,
        },
        "linkedin_ads": {
            "status": _status("LINKEDIN", linkedin_configured),
            "detail": "Connected" if linkedin_configured else "Add LinkedIn access token to connect",
            "has_campaigns": "LINKEDIN" in active_platforms,
            "credentials_configured": linkedin_configured,
        },
        "whatsapp_ads": {
            "status": _status("WHATSAPP", meta_ads_configured),
            "detail": "Click-to-WhatsApp via Meta" if meta_ads_configured else "Requires Meta Ads connection",
            "has_campaigns": "WHATSAPP" in active_platforms,
        },
        "twilio_calls": {
            "status": "connected" if twilio_configured else "not_connected",
            "detail": "Call tracking active" if twilio_configured else "Add Twilio credentials for call tracking",
            "credentials_configured": twilio_configured,
        },
        "exotel_calls": {
            "status": "connected" if (settings.EXOTEL_API_KEY and settings.EXOTEL_API_TOKEN) else "not_connected",
            "detail": (
                f"Call tracking active — SID {settings.EXOTEL_SID}" if (settings.EXOTEL_API_KEY and settings.EXOTEL_API_TOKEN)
                else "Configure Exotel credentials"
            ),
            "credentials_configured": bool(settings.EXOTEL_API_KEY and settings.EXOTEL_API_TOKEN),
        },
    }
