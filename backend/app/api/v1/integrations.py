"""Integration endpoints — connect Google Ads, Meta Ads, WhatsApp, Calendar.

Each clinic connects their OWN ad accounts through OAuth.
PatientPlex manages campaigns on their behalf.
"""

import base64
import hashlib
import hmac
import json
import logging
import time
from urllib.parse import urlencode

from fastapi import APIRouter, Depends, HTTPException, Query, Request
from fastapi.responses import RedirectResponse
from pydantic import BaseModel
from sqlalchemy.ext.asyncio import AsyncSession

from app.api.v1.auth import get_current_doctor
from app.core.config import settings
from app.db.session import get_db
from app.models.doctor import Doctor

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/integrations", tags=["integrations"])

# Base URLs for OAuth callbacks — loaded from config (env vars)
BACKEND_BASE = settings.BACKEND_BASE_URL.rstrip("/")
FRONTEND_BASE = settings.FRONTEND_BASE_URL.rstrip("/")

_OAUTH_STATE_TTL = 600  # 10 minutes


def _create_oauth_state(provider: str, doctor_id: str) -> str:
    """Create a signed OAuth state token (stateless — works across workers)."""
    data = json.dumps({
        "p": provider,
        "d": doctor_id,
        "e": time.time() + _OAUTH_STATE_TTL,
    })
    encoded = base64.urlsafe_b64encode(data.encode()).decode().rstrip("=")
    signature = hmac.new(
        settings.SECRET_KEY.encode(), encoded.encode(), hashlib.sha256
    ).hexdigest()[:16]
    return f"{encoded}.{signature}"


def _verify_oauth_state(state: str, expected_provider: str) -> str:
    """Verify a signed OAuth state token. Returns doctor_id or raises."""
    parts = state.rsplit(".", 1)
    if len(parts) != 2:
        raise HTTPException(status_code=400, detail="Invalid OAuth state")

    encoded, signature = parts
    expected_sig = hmac.new(
        settings.SECRET_KEY.encode(), encoded.encode(), hashlib.sha256
    ).hexdigest()[:16]
    if not hmac.compare_digest(signature, expected_sig):
        raise HTTPException(status_code=400, detail="Invalid OAuth state signature")

    # Restore padding for base64
    padded = encoded + "=" * (4 - len(encoded) % 4)
    try:
        data = json.loads(base64.urlsafe_b64decode(padded))
    except Exception:
        raise HTTPException(status_code=400, detail="Corrupted OAuth state")

    if data.get("e", 0) < time.time():
        raise HTTPException(
            status_code=400,
            detail="OAuth state expired. Please try connecting again.",
        )

    if data.get("p") != expected_provider:
        raise HTTPException(status_code=400, detail="OAuth state mismatch")

    return data["d"]


async def _get_access_token_from_refresh(refresh_token: str) -> str | None:
    """Exchange a Google OAuth refresh_token for a fresh access_token."""
    import httpx
    try:
        async with httpx.AsyncClient() as client:
            resp = await client.post(
                "https://oauth2.googleapis.com/token",
                data={
                    "client_id": settings.GOOGLE_CLIENT_ID,
                    "client_secret": settings.GOOGLE_CLIENT_SECRET,
                    "refresh_token": refresh_token,
                    "grant_type": "refresh_token",
                },
                timeout=15,
            )
            resp.raise_for_status()
            return resp.json().get("access_token")
    except Exception as e:
        logger.error("Failed to refresh Google access token: %s", e)
        return None


# ---------------------------------------------------------------------------
# Google Ads OAuth
# ---------------------------------------------------------------------------

@router.get("/google-ads/connect")
async def google_ads_connect(
    doctor: Doctor = Depends(get_current_doctor),
):
    """Start Google Ads OAuth flow. Returns the consent URL."""
    if not settings.GOOGLE_CLIENT_ID or settings.GOOGLE_CLIENT_ID.startswith("YOUR_"):
        raise HTTPException(
            status_code=400,
            detail="Google OAuth is not configured yet. The server needs GOOGLE_CLIENT_ID and GOOGLE_CLIENT_SECRET set in environment variables. Please add credentials from console.cloud.google.com to Render.",
        )

    from app.services.google_ads_oauth import get_google_ads_auth_url

    redirect_uri = f"{BACKEND_BASE}/api/v1/integrations/google-ads/callback"
    state = _create_oauth_state("google_ads", str(doctor.id))
    auth_url = get_google_ads_auth_url(state, redirect_uri)

    return {"auth_url": auth_url}


@router.get("/google-ads/callback")
async def google_ads_callback(
    code: str = Query(...),
    state: str = Query(...),
    db: AsyncSession = Depends(get_db),
):
    """Google Ads OAuth callback — exchanges code for tokens, stores refresh_token."""
    from sqlalchemy import select
    from app.services.google_ads_oauth import exchange_google_ads_code

    # Verify and consume the OAuth state token (CSRF protection)
    doctor_id = _verify_oauth_state(state, "google_ads")

    redirect_uri = f"{BACKEND_BASE}/api/v1/integrations/google-ads/callback"

    try:
        tokens = await exchange_google_ads_code(code, redirect_uri)
    except Exception as exc:
        logger.error("Google Ads token exchange failed: %s", exc)
        return RedirectResponse(
            url=f"{FRONTEND_BASE}/dashboard/settings?google_ads=error&message={str(exc)}"
        )

    # Store the refresh token (encrypted at rest)
    from app.core.encryption import encrypt_value

    result = await db.execute(select(Doctor).where(Doctor.id == doctor_id))
    doctor = result.scalar_one_or_none()
    if not doctor:
        raise HTTPException(status_code=404, detail="Doctor not found")

    refresh_token = tokens.get("refresh_token")
    if refresh_token:
        doctor.google_ads_refresh_token = encrypt_value(refresh_token)
    doctor.google_ads_connected = False
    doctor.google_ads_customer_id = None

    # Try to get their customer ID
    try:
        from app.services.google_ads_oauth import get_google_ads_customer_ids
        customers = await get_google_ads_customer_ids(tokens["access_token"])
        logger.info("OAuth callback: accessible customers = %s", customers)
        if customers:
            doctor.google_ads_customer_id = customers[0]["customer_id"]
            logger.info("OAuth callback: stored customer_id = %s", doctor.google_ads_customer_id)
        else:
            logger.warning("OAuth callback: no accessible customers found")
    except Exception as e:
        logger.warning("Could not auto-detect Google Ads customer ID: %s", e, exc_info=True)

    doctor.google_ads_connected = bool(doctor.google_ads_refresh_token and doctor.google_ads_customer_id)
    await db.commit()
    if not doctor.google_ads_connected:
        return RedirectResponse(url=f"{FRONTEND_BASE}/dashboard/settings?google_ads=error")

    logger.info("Google Ads connected for doctor %s (customer: %s)",
                doctor.full_name, doctor.google_ads_customer_id)

    return RedirectResponse(
        url=f"{FRONTEND_BASE}/dashboard/settings?google_ads=connected"
    )


@router.post("/google-ads/disconnect")
async def google_ads_disconnect(
    doctor: Doctor = Depends(get_current_doctor),
    db: AsyncSession = Depends(get_db),
):
    """Disconnect Google Ads account."""
    doctor.google_ads_refresh_token = None
    doctor.google_ads_customer_id = None
    doctor.google_ads_connected = False
    await db.commit()
    return {"status": "disconnected"}


# ---------------------------------------------------------------------------
# Meta Ads OAuth
# ---------------------------------------------------------------------------

META_AUTH_URL = "https://www.facebook.com/v18.0/dialog/oauth"
META_TOKEN_URL = "https://graph.facebook.com/v18.0/oauth/access_token"
META_SCOPES = "ads_management,ads_read,pages_read_engagement,pages_show_list,business_management"


@router.get("/meta-ads/connect")
async def meta_ads_connect(
    doctor: Doctor = Depends(get_current_doctor),
):
    """Start Meta (Facebook) Ads OAuth flow."""
    if not settings.META_APP_ID or settings.META_APP_ID.startswith("YOUR_"):
        raise HTTPException(
            status_code=400,
            detail="Meta Ads is not configured yet. The server needs META_APP_ID and META_APP_SECRET set in environment variables. Please create a Meta App at developers.facebook.com and add the credentials to Render.",
        )

    # Validate Meta App ID is numeric (Facebook App IDs are always numbers)
    if not settings.META_APP_ID.strip().isdigit():
        raise HTTPException(
            status_code=400,
            detail=f"META_APP_ID appears invalid (must be a numeric Facebook App ID). Current value starts with: {settings.META_APP_ID[:6]}... — Please check at developers.facebook.com → Your App → Settings → Basic.",
        )

    redirect_uri = f"{BACKEND_BASE}/api/v1/integrations/meta-ads/callback"
    state = _create_oauth_state("meta_ads", str(doctor.id))
    params = {
        "client_id": settings.META_APP_ID,
        "redirect_uri": redirect_uri,
        "scope": META_SCOPES,
        "response_type": "code",
        "state": state,
    }
    auth_url = f"{META_AUTH_URL}?{urlencode(params)}"

    return {"auth_url": auth_url}


@router.get("/meta-ads/callback")
async def meta_ads_callback(
    code: str = Query(...),
    state: str = Query(...),
    db: AsyncSession = Depends(get_db),
):
    """Meta Ads OAuth callback — exchanges code for long-lived access token."""
    import httpx
    from sqlalchemy import select

    # Verify and consume the OAuth state token (CSRF protection)
    doctor_id = _verify_oauth_state(state, "meta_ads")
    redirect_uri = f"{BACKEND_BASE}/api/v1/integrations/meta-ads/callback"

    try:
        # Exchange code for short-lived token
        async with httpx.AsyncClient() as client:
            resp = await client.get(META_TOKEN_URL, params={
                "client_id": settings.META_APP_ID,
                "client_secret": settings.META_APP_SECRET,
                "redirect_uri": redirect_uri,
                "code": code,
            }, timeout=30)
            resp.raise_for_status()
            short_token = resp.json().get("access_token")

            # Exchange for long-lived token (60 days)
            resp2 = await client.get(META_TOKEN_URL, params={
                "grant_type": "fb_exchange_token",
                "client_id": settings.META_APP_ID,
                "client_secret": settings.META_APP_SECRET,
                "fb_exchange_token": short_token,
            }, timeout=30)
            resp2.raise_for_status()
            long_token = resp2.json().get("access_token")

            # Get ad accounts
            resp3 = await client.get(
                "https://graph.facebook.com/v18.0/me/adaccounts",
                params={"access_token": long_token, "fields": "id,name,account_status"},
                timeout=30,
            )
            resp3.raise_for_status()
            ad_accounts = resp3.json().get("data", [])

            # Get pages
            resp4 = await client.get(
                "https://graph.facebook.com/v18.0/me/accounts",
                params={"access_token": long_token, "fields": "id,name"},
                timeout=30,
            )
            pages = resp4.json().get("data", [])

    except Exception as exc:
        logger.error("Meta token exchange failed: %s", exc)
        return RedirectResponse(
            url=f"{FRONTEND_BASE}/dashboard/settings?meta_ads=error"
        )

    # Store token (encrypted at rest)
    from app.core.encryption import encrypt_value

    result = await db.execute(select(Doctor).where(Doctor.id == doctor_id))
    doctor = result.scalar_one_or_none()
    if not doctor:
        raise HTTPException(status_code=404, detail="Doctor not found")

    doctor.meta_ads_access_token = encrypt_value(long_token) if long_token else None
    doctor.meta_ads_connected = bool(long_token and ad_accounts)
    doctor.meta_ads_account_id = None
    doctor.meta_ads_page_id = None
    if ad_accounts:
        doctor.meta_ads_account_id = ad_accounts[0]["id"]
    if pages:
        doctor.meta_ads_page_id = pages[0]["id"]

    await db.commit()
    if not doctor.meta_ads_connected:
        return RedirectResponse(url=f"{FRONTEND_BASE}/dashboard/settings?meta_ads=error")

    logger.info("Meta Ads connected for doctor %s (ad_account: %s, page: %s)",
                doctor.full_name, doctor.meta_ads_account_id, doctor.meta_ads_page_id)

    return RedirectResponse(
        url=f"{FRONTEND_BASE}/dashboard/settings?meta_ads=connected"
    )


@router.post("/meta-ads/disconnect")
async def meta_ads_disconnect(
    doctor: Doctor = Depends(get_current_doctor),
    db: AsyncSession = Depends(get_db),
):
    """Disconnect Meta Ads account."""
    doctor.meta_ads_access_token = None
    doctor.meta_ads_account_id = None
    doctor.meta_ads_page_id = None
    doctor.meta_ads_connected = False
    await db.commit()
    return {"status": "disconnected"}


# ---------------------------------------------------------------------------
# WhatsApp Cloud API
# ---------------------------------------------------------------------------

@router.post("/whatsapp/verify")
async def verify_whatsapp(
    doctor: Doctor = Depends(get_current_doctor),
    db: AsyncSession = Depends(get_db),
):
    """Send a test message to verify WhatsApp number is working.

    Uses the Meta WhatsApp Cloud API to send a template message.
    If the message sends successfully, marks the number as verified.
    """
    if not doctor.whatsapp_number:
        raise HTTPException(status_code=400, detail="No WhatsApp number configured")

    if not settings.WHATSAPP_API_TOKEN:
        # Try Twilio WhatsApp as fallback
        if settings.TWILIO_ACCOUNT_SID:
            return {
                "status": "pending",
                "message": "WhatsApp verification will happen via Twilio when a message is received",
                "provider": "twilio",
            }
        raise HTTPException(status_code=400, detail="WhatsApp API not configured")

    import httpx

    try:
        # Send test message via Meta Cloud API
        phone_number_id = settings.WHATSAPP_PHONE_NUMBER_ID
        if not phone_number_id:
            raise HTTPException(
                status_code=400,
                detail="WHATSAPP_PHONE_NUMBER_ID not configured. Set it in Render environment variables (find it in Meta Business Suite → WhatsApp → API Setup).",
            )
        async with httpx.AsyncClient() as client:
            resp = await client.post(
                f"{settings.WHATSAPP_API_URL}/{phone_number_id}/messages",
                headers={
                    "Authorization": f"Bearer {settings.WHATSAPP_API_TOKEN}",
                    "Content-Type": "application/json",
                },
                json={
                    "messaging_product": "whatsapp",
                    "to": doctor.whatsapp_number.replace("+", ""),
                    "type": "text",
                    "text": {
                        "body": f"✅ PatientPlex AI connected! Your WhatsApp number {doctor.whatsapp_number} is now linked to your clinic dashboard. Patients will receive automated booking confirmations here."
                    },
                },
                timeout=30,
            )

            if resp.status_code == 200:
                doctor.whatsapp_verified = True
                await db.commit()
                return {"status": "verified", "message": "WhatsApp verification message sent successfully! ✅"}
            else:
                error_data = resp.json()
                # Extract human-readable error message from Meta API response
                error_msg = "WhatsApp API error"
                if isinstance(error_data, dict):
                    err_obj = error_data.get("error", error_data)
                    if isinstance(err_obj, dict):
                        error_msg = err_obj.get("message", str(err_obj))
                    else:
                        error_msg = str(err_obj)
                else:
                    error_msg = str(error_data)
                logger.error("WhatsApp verify failed: %s (status %d)", error_msg, resp.status_code)
                return {"status": "error", "message": error_msg}

    except Exception as exc:
        logger.error("WhatsApp verification failed: %s", exc)
        return {"status": "error", "message": str(exc)}


# ---------------------------------------------------------------------------
# Razorpay
# ---------------------------------------------------------------------------

class CreateOrderRequest(BaseModel):
    plan: str  # STARTER, GROWTH, ENTERPRISE


@router.post("/razorpay/create-order")
async def create_razorpay_order(
    body: CreateOrderRequest,
    doctor: Doctor = Depends(get_current_doctor),
):
    """Create a Razorpay order for subscription payment."""
    if not settings.RAZORPAY_KEY_ID or not settings.RAZORPAY_KEY_SECRET:
        raise HTTPException(status_code=400, detail="Razorpay not configured")

    import razorpay

    plan_prices = {
        "STARTER": 999900,      # ₹9,999 in paise
        "GROWTH": 2499900,      # ₹24,999 in paise
        "ENTERPRISE": 4999900,  # ₹49,999 in paise
    }

    amount = plan_prices.get(body.plan.upper())
    if not amount:
        raise HTTPException(status_code=400, detail=f"Invalid plan: {body.plan}")

    try:
        client = razorpay.Client(
            auth=(settings.RAZORPAY_KEY_ID, settings.RAZORPAY_KEY_SECRET)
        )

        order = client.order.create({
            "amount": amount,
            "currency": "INR",
            "receipt": f"pp_{doctor.id}_{body.plan.lower()}",
            "notes": {
                "doctor_id": str(doctor.id),
                "plan": body.plan,
                "email": doctor.email,
            },
        })

        return {
            "order_id": order["id"],
            "amount": amount,
            "currency": "INR",
            "key_id": settings.RAZORPAY_KEY_ID,
            "prefill": {
                "name": doctor.full_name,
                "email": doctor.email,
                "contact": doctor.phone,
            },
        }

    except Exception as exc:
        logger.error("Razorpay order creation failed: %s", exc)
        raise HTTPException(status_code=500, detail=f"Payment error: {str(exc)}")


@router.post("/razorpay/verify")
async def verify_razorpay_payment(
    request: Request,
    doctor: Doctor = Depends(get_current_doctor),
    db: AsyncSession = Depends(get_db),
):
    """Verify Razorpay payment signature and activate subscription."""
    if not settings.RAZORPAY_KEY_ID or not settings.RAZORPAY_KEY_SECRET:
        raise HTTPException(status_code=400, detail="Razorpay not configured")

    import razorpay

    body = await request.json()
    payment_id = body.get("razorpay_payment_id")
    order_id = body.get("razorpay_order_id")
    signature = body.get("razorpay_signature")

    if not all([payment_id, order_id, signature]):
        raise HTTPException(status_code=400, detail="Missing payment details")

    try:
        client = razorpay.Client(
            auth=(settings.RAZORPAY_KEY_ID, settings.RAZORPAY_KEY_SECRET)
        )

        # Verify signature
        client.utility.verify_payment_signature({
            "razorpay_payment_id": payment_id,
            "razorpay_order_id": order_id,
            "razorpay_signature": signature,
        })

        # Payment verified — activate subscription
        # Get order details for plan info
        order = client.order.fetch(order_id)
        plan = order.get("notes", {}).get("plan", "STARTER")

        # Update subscription in DB
        from app.models.billing import Subscription
        from sqlalchemy import select as sa_select
        from datetime import datetime, timedelta, timezone

        result = await db.execute(
            sa_select(Subscription).where(Subscription.doctor_id == doctor.id)
        )
        sub = result.scalar_one_or_none()

        if sub:
            sub.plan = plan
            sub.status = "ACTIVE"
            sub.price_inr = order.get("amount", 0) // 100
            sub.current_period_end = datetime.now(timezone.utc) + timedelta(days=30)
            sub.razorpay_payment_id = payment_id
            sub.razorpay_order_id = order_id
        else:
            # Create new subscription record
            sub = Subscription(
                doctor_id=doctor.id,
                plan=plan,
                status="ACTIVE",
                price_inr=order.get("amount", 0) // 100,
                current_period_end=datetime.now(timezone.utc) + timedelta(days=30),
            )
            db.add(sub)

        await db.commit()

        return {
            "status": "success",
            "plan": plan,
            "message": f"Payment verified. {plan} plan activated!",
        }

    except razorpay.errors.SignatureVerificationError:
        raise HTTPException(status_code=400, detail="Payment signature verification failed")
    except Exception as exc:
        logger.error("Payment verification failed: %s", exc)
        raise HTTPException(status_code=500, detail=str(exc))


# ---------------------------------------------------------------------------
# Google Ads — Import existing campaigns
# ---------------------------------------------------------------------------

@router.post("/google-ads/import-campaigns")
async def import_google_ads_campaigns(
    doctor: Doctor = Depends(get_current_doctor),
    db: AsyncSession = Depends(get_db),
):
    """Import existing Google Ads campaigns into PatientPlex.

    Pulls all campaigns from the doctor's connected Google Ads account
    and creates corresponding Campaign records in our database.
    This lets PatientPlex track and optimize campaigns the clinic already has.
    """
    from app.models.campaign import AdPlatform, Campaign, CampaignStatus
    from app.services.google_ads_engine import GoogleAdsEngine
    from app.core.encryption import decrypt_value
    if not doctor.google_ads_connected or not doctor.google_ads_refresh_token or not doctor.google_ads_customer_id:
        raise HTTPException(status_code=409, detail="Reconnect Google Ads and select an accessible customer account")
    engine = GoogleAdsEngine(db)
    await engine.connect_with_refresh_token(decrypt_value(doctor.google_ads_refresh_token))
    if not engine.is_connected:
        raise HTTPException(status_code=502, detail="Google Ads authorization failed")
    customer_id = doctor.google_ads_customer_id
    # Fetch campaigns from Google Ads API
    # Strip dashes from customer ID (Google Ads API requires plain numbers)
    customer_id = customer_id.replace("-", "").strip()

    # Fetch campaigns from Google Ads API (use LAST_30_DAYS — valid GAQL range)
    metrics_data = await engine.get_campaign_metrics(customer_id, days=30)

    if metrics_data.get("status") != "success":
        raise HTTPException(status_code=502, detail="Google Ads data fetch failed; reconnect or check developer token permissions")

    # Import each campaign
    imported = []
    from sqlalchemy import select
    for gads_campaign in metrics_data.get("campaigns", []):
        # Check if already imported
        existing = await db.execute(
            select(Campaign).where(
                Campaign.doctor_id == doctor.id,
                Campaign.platform == AdPlatform.GOOGLE,
                Campaign.platform_campaign_id == str(gads_campaign["campaign_id"]),
            )
        )
        if existing.scalar_one_or_none():
            continue  # Already imported

        # Create local record
        # NOTE: cost_inr from REST API is already in INR (micros/1e6), store directly
        # ctr from REST API is already in percentage (raw * 100), store directly
        # avg_cpc_inr from REST API is already in INR (micros/1e6), store directly
        gads_status = gads_campaign.get("status", "UNKNOWN")
        if gads_status == "ENABLED":
            local_status = CampaignStatus.ACTIVE
        elif gads_status == "PAUSED":
            local_status = CampaignStatus.PAUSED
        elif gads_status == "REMOVED":
            local_status = CampaignStatus.COMPLETED
        else:
            local_status = CampaignStatus.DRAFT

        # Map Google Ads channel type to our campaign_type
        channel = gads_campaign.get("channel_type", "SEARCH")
        campaign_type_map = {
            "SEARCH": "SEARCH",
            "DISPLAY": "DISPLAY",
            "VIDEO": "VIDEO",
            "SHOPPING": "SHOPPING",
            "MULTI_CHANNEL": "PMAX",
            "PERFORMANCE_MAX": "PMAX",
        }

        campaign = Campaign(
            doctor_id=doctor.id,
            platform=AdPlatform.GOOGLE,
            platform_campaign_id=str(gads_campaign["campaign_id"]),
            name=gads_campaign.get("name", "Imported Campaign"),
            campaign_type=campaign_type_map.get(channel, "SEARCH"),
            status=local_status,
            daily_budget=round(gads_campaign.get("daily_budget_inr", 0)),
            total_budget=round(gads_campaign.get("daily_budget_inr", 0) * 30.4),
            impressions=gads_campaign.get("impressions", 0),
            clicks=gads_campaign.get("clicks", 0),
            conversions=int(gads_campaign.get("conversions", 0)),
            spend=round(gads_campaign.get("cost_inr", 0)),  # Already in INR from REST API
            cpc=round(gads_campaign.get("avg_cpc_inr", 0), 2),
            ctr=round(gads_campaign.get("ctr", 0), 2),
            target_location=f"{doctor.city}, {doctor.state}" if doctor.city else None,
            target_radius_km=doctor.geo_radius_km,
            currency="INR",
        )
        db.add(campaign)
        imported.append({"name": campaign.name, "status": campaign.status.value, "google_id": gads_campaign["campaign_id"]})

    await db.commit()

    return {
        "status": "success",
        "message": f"Imported {len(imported)} campaigns from Google Ads",
        "imported": len(imported),
        "campaigns": imported,
    }


@router.post("/google-ads/resync-all")
async def resync_google_ads_campaigns(
    doctor: Doctor = Depends(get_current_doctor),
    db: AsyncSession = Depends(get_db),
):
    """Re-sync ALL imported Google Ads campaigns with fresh data from the API.

    Fixes: budget amounts, spend values, status, metrics.
    Use this after import to correct any data discrepancies.
    """
    from app.models.campaign import AdPlatform, Campaign, CampaignStatus
    from app.services.google_ads_engine import GoogleAdsEngine
    from sqlalchemy import select
    from app.core.encryption import decrypt_value
    if not doctor.google_ads_connected or not doctor.google_ads_refresh_token or not doctor.google_ads_customer_id:
        raise HTTPException(status_code=409, detail="Reconnect Google Ads before synchronizing")
    engine = GoogleAdsEngine(db)
    await engine.connect_with_refresh_token(decrypt_value(doctor.google_ads_refresh_token))
    if not engine.is_connected:
        raise HTTPException(status_code=502, detail="Google Ads authorization failed")
    customer_id = doctor.google_ads_customer_id
    customer_id = customer_id.replace("-", "").strip()
    metrics_data = await engine.get_campaign_metrics(customer_id, days=30)

    if metrics_data.get("status") != "success":
        raise HTTPException(status_code=502, detail="Google Ads synchronization failed")

    # Build lookup from Google data
    google_data = {str(c["campaign_id"]): c for c in metrics_data.get("campaigns", [])}

    # Update all existing campaigns
    result = await db.execute(
        select(Campaign).where(
            Campaign.doctor_id == doctor.id,
            Campaign.platform == AdPlatform.GOOGLE,
        )
    )
    existing = result.scalars().all()
    updated = 0

    for campaign in existing:
        gads = google_data.get(campaign.platform_campaign_id)
        if not gads:
            continue

        # Fix status
        gads_status = gads.get("status", "UNKNOWN")
        if gads_status == "ENABLED":
            campaign.status = CampaignStatus.ACTIVE
        elif gads_status == "PAUSED":
            campaign.status = CampaignStatus.PAUSED
        elif gads_status == "REMOVED":
            campaign.status = CampaignStatus.COMPLETED

        # Fix budget (now comes as INR from API)
        campaign.daily_budget = round(gads.get("daily_budget_inr", 0))
        campaign.total_budget = round(gads.get("daily_budget_inr", 0) * 30.4)

        # Fix metrics (all already in correct units from API)
        campaign.impressions = gads.get("impressions", 0)
        campaign.clicks = gads.get("clicks", 0)
        campaign.conversions = int(gads.get("conversions", 0))
        campaign.spend = round(gads.get("cost_inr", 0))  # INR, not paise
        campaign.cpc = round(gads.get("avg_cpc_inr", 0), 2)
        campaign.ctr = round(gads.get("ctr", 0), 2)

        # Fix campaign type from channel
        channel = gads.get("channel_type", "SEARCH")
        type_map = {"SEARCH": "SEARCH", "DISPLAY": "DISPLAY", "VIDEO": "VIDEO", "MULTI_CHANNEL": "PMAX"}
        campaign.campaign_type = type_map.get(channel, campaign.campaign_type or "SEARCH")

        from datetime import datetime, timezone
        campaign.last_synced_at = datetime.now(timezone.utc)
        updated += 1

    await db.commit()

    return {
        "status": "success",
        "message": f"Re-synced {updated} campaigns with fresh Google Ads data",
        "updated": updated,
        "total_existing": len(existing),
    }


# ---------------------------------------------------------------------------
# Twilio — Provision tracking number for a clinic
# ---------------------------------------------------------------------------

@router.post("/twilio/provision")
async def provision_twilio_number(
    doctor: Doctor = Depends(get_current_doctor),
    db: AsyncSession = Depends(get_db),
):
    """Provision a Twilio virtual number for this clinic's call tracking.

    The virtual number is used in Google Ads call extensions.
    When patients call it, PatientPlex captures their real phone number
    (which Google would normally blur) and forwards to the doctor.
    """
    from app.services.call_tracking import call_tracking_service

    if not call_tracking_service.is_connected:
        return {
            "status": "not_configured",
            "message": "Twilio credentials not set on server. Add TWILIO_ACCOUNT_SID and TWILIO_AUTH_TOKEN in Render.",
        }

    # Check if doctor already has a number
    existing_number = getattr(doctor, 'twilio_phone_number', None)
    if existing_number:
        return {
            "status": "already_provisioned",
            "phone_number": existing_number,
            "message": f"Clinic already has tracking number: {existing_number}",
        }

    result = await call_tracking_service.provision_number(country_code="IN")

    if result.get("status") == "provisioned":
        doctor.twilio_phone_number = result["phone_number"]
        await db.commit()
        return {
            "status": "provisioned",
            "phone_number": result["phone_number"],
            "message": f"Tracking number {result['phone_number']} provisioned! Use this in Google Ads call extensions.",
            "webhook_url": result.get("webhook_url"),
        }
    # Provide user-friendly error messages for common Twilio issues
    error_msg = result.get("message", "")
    if "Trial" in error_msg or "trial" in error_msg or "verify" in error_msg.lower():
        # On trial, automatically try to verify the clinic's own number as a caller ID
        try:
            from twilio.rest import Client as TwilioClient
            twilio_client = TwilioClient(settings.TWILIO_ACCOUNT_SID, settings.TWILIO_AUTH_TOKEN)

            phone = doctor.phone
            if not phone.startswith("+"):
                phone = f"+91{phone}" if len(phone) == 10 else f"+{phone}"

            # Check if already verified
            existing = twilio_client.outgoing_caller_ids.list(phone_number=phone)
            if existing:
                doctor.twilio_phone_number = phone
                await db.commit()
                return {
                    "status": "success",
                    "phone_number": phone,
                    "message": f"Your number {phone} is already verified with Twilio! Call tracking is active.",
                }

            # Initiate verification call
            validation = twilio_client.validation_requests.create(
                friendly_name=f"PatientPlex - {doctor.clinic_name or doctor.full_name}",
                phone_number=phone,
            )

            return {
                "status": "verification_sent",
                "phone_number": phone,
                "validation_code": validation.validation_code,
                "message": f"Twilio is calling {phone} now! Answer and enter code: {validation.validation_code}. After verification, click Provision Number again.",
            }
        except Exception as verify_exc:
            logger.warning("Auto-verify caller ID failed: %s", verify_exc)
            return {
                "status": "trial_account",
                "message": (
                    "Twilio trial accounts cannot provision numbers or verify caller IDs via API. "
                    "To enable call tracking, upgrade your Twilio account at twilio.com/console \u2192 Upgrade. "
                    "It costs nothing extra \u2014 just add a payment method and Twilio gives you $15.50 free credit. "
                    "After upgrading, click Provision Number again."
                ),
            }

    return result


@router.post("/twilio/verify-caller-id")
async def verify_twilio_caller_id(
    doctor: Doctor = Depends(get_current_doctor),
    db: AsyncSession = Depends(get_db),
):
    """Verify the doctor's phone number as a Twilio Outgoing Caller ID.

    On trial accounts, Twilio can't provision new numbers but CAN verify
    existing numbers as caller IDs. This sends a verification call to the
    doctor's phone with a 6-digit code.
    """
    from twilio.rest import Client as TwilioClient

    if not settings.TWILIO_ACCOUNT_SID or not settings.TWILIO_AUTH_TOKEN:
        raise HTTPException(status_code=400, detail="Twilio credentials not configured")

    # Use doctor's clinic phone or whatsapp number
    phone = doctor.phone or (doctor.whatsapp_number if doctor.whatsapp_number else None)
    if not phone:
        raise HTTPException(status_code=400, detail="No phone number found for this clinic")

    # Ensure proper format
    if not phone.startswith("+"):
        phone = f"+91{phone}" if len(phone) == 10 else f"+{phone}"

    try:
        client = TwilioClient(settings.TWILIO_ACCOUNT_SID, settings.TWILIO_AUTH_TOKEN)

        # Check if already verified
        existing = client.outgoing_caller_ids.list(phone_number=phone)
        if existing:
            # Already verified — store it
            doctor.twilio_phone_number = phone
            await db.commit()
            return {
                "status": "already_verified",
                "phone_number": phone,
                "message": f"Phone number {phone} is already verified as a Twilio Caller ID! Call tracking is now active.",
            }

        # Initiate verification — Twilio will call this number with a code
        validation_request = client.validation_requests.create(
            friendly_name=f"PatientPlex - {doctor.clinic_name or doctor.full_name}",
            phone_number=phone,
        )

        return {
            "status": "verification_sent",
            "phone_number": phone,
            "validation_code": validation_request.validation_code,
            "message": f"Twilio is calling {phone} now! When you answer, enter the code: {validation_request.validation_code}",
        }

    except Exception as exc:
        error_msg = str(exc)
        logger.error("Twilio verify caller ID failed: %s", error_msg)

        if "upgrade" in error_msg.lower() or "trial" in error_msg.lower():
            return {
                "status": "trial_limit",
                "message": "Twilio trial account has reached its limits. Please upgrade at twilio.com/console.",
            }

        return {
            "status": "error",
            "message": f"Verification failed: {error_msg}",
        }


@router.get("/twilio/status")
async def twilio_status(
    doctor: Doctor = Depends(get_current_doctor),
):
    """Get Twilio call tracking status for this clinic."""
    from app.services.call_tracking import call_tracking_service

    return {
        "connected": call_tracking_service.is_connected,
        "clinic_tracking_number": getattr(doctor, 'twilio_phone_number', None),
        "whatsapp_number": doctor.whatsapp_number,
    }


@router.get("/booking-urls")
async def get_booking_urls(
    doctor: Doctor = Depends(get_current_doctor),
):
    """Get all booking-related URLs for this clinic.

    Useful for:
    - Setting Google Ads final URL
    - Sharing booking link with patients
    - QR code generation for clinic display
    """
    slug = doctor.subdomain_slug
    frontend = settings.FRONTEND_BASE_URL.rstrip("/")

    if not slug:
        return {
            "booking_page": None,
            "message": "No booking slug set. Complete onboarding or the system will auto-generate one on next deploy.",
        }

    booking_url = f"{frontend}/book/{slug}"

    return {
        "booking_page": booking_url,
        "booking_page_with_utm": f"{booking_url}?utm_source=google&utm_campaign={{campaign_name}}",
        "google_ads_final_url": booking_url,
        "google_ads_final_url_template": f"{booking_url}?utm_source=google&utm_medium=cpc&utm_campaign={{campaignid}}&utm_term={{keyword}}&gclid={{gclid}}",
        "whatsapp_link": f"https://wa.me/91{doctor.whatsapp_number[-10:]}?text=Hi%2C%20I%27d%20like%20to%20book%20an%20appointment" if doctor.whatsapp_number else None,
        "qr_code_url": f"https://api.qrserver.com/v1/create-qr-code/?size=300x300&data={booking_url}",
        "slug": slug,
    }
