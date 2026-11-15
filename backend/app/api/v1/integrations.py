"""Integration endpoints — connect Google Ads, Meta Ads, WhatsApp, Calendar.

Each clinic connects their OWN ad accounts through OAuth.
PatientPlex manages campaigns on their behalf.
"""

import logging
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

# Base URL for OAuth callbacks
BACKEND_BASE = "https://patientplex-ai-g7ce.onrender.com"
FRONTEND_BASE = "https://patientplex-ai.vercel.app"


# ---------------------------------------------------------------------------
# Google Ads OAuth
# ---------------------------------------------------------------------------

@router.get("/google-ads/connect")
async def google_ads_connect(
    doctor: Doctor = Depends(get_current_doctor),
):
    """Start Google Ads OAuth flow. Returns the consent URL."""
    if not settings.GOOGLE_CLIENT_ID:
        raise HTTPException(status_code=400, detail="Google OAuth not configured on server")

    from app.services.google_ads_oauth import get_google_ads_auth_url

    redirect_uri = f"{BACKEND_BASE}/api/v1/integrations/google-ads/callback"
    auth_url = get_google_ads_auth_url(str(doctor.id), redirect_uri)

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

    # Parse state: "google_ads:<doctor_id>"
    parts = state.split(":", 1)
    if len(parts) != 2 or parts[0] != "google_ads":
        raise HTTPException(status_code=400, detail="Invalid OAuth state")

    doctor_id = parts[1]

    redirect_uri = f"{BACKEND_BASE}/api/v1/integrations/google-ads/callback"

    try:
        tokens = await exchange_google_ads_code(code, redirect_uri)
    except Exception as exc:
        logger.error("Google Ads token exchange failed: %s", exc)
        return RedirectResponse(
            url=f"{FRONTEND_BASE}/dashboard/settings?google_ads=error&message={str(exc)}"
        )

    # Store the refresh token
    result = await db.execute(select(Doctor).where(Doctor.id == doctor_id))
    doctor = result.scalar_one_or_none()
    if not doctor:
        raise HTTPException(status_code=404, detail="Doctor not found")

    doctor.google_ads_refresh_token = tokens.get("refresh_token")
    doctor.google_ads_connected = True

    # Try to get their customer ID
    try:
        from app.services.google_ads_oauth import get_google_ads_customer_ids
        customers = await get_google_ads_customer_ids(tokens["access_token"])
        if customers:
            doctor.google_ads_customer_id = customers[0]["customer_id"]
    except Exception as e:
        logger.warning("Could not auto-detect Google Ads customer ID: %s", e)

    await db.commit()

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
    if not settings.META_APP_ID:
        raise HTTPException(status_code=400, detail="Meta App not configured on server")

    redirect_uri = f"{BACKEND_BASE}/api/v1/integrations/meta-ads/callback"
    params = {
        "client_id": settings.META_APP_ID,
        "redirect_uri": redirect_uri,
        "scope": META_SCOPES,
        "response_type": "code",
        "state": f"meta_ads:{doctor.id}",
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

    parts = state.split(":", 1)
    if len(parts) != 2 or parts[0] != "meta_ads":
        raise HTTPException(status_code=400, detail="Invalid OAuth state")

    doctor_id = parts[1]
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

    # Store token
    result = await db.execute(select(Doctor).where(Doctor.id == doctor_id))
    doctor = result.scalar_one_or_none()
    if not doctor:
        raise HTTPException(status_code=404, detail="Doctor not found")

    doctor.meta_ads_access_token = long_token
    doctor.meta_ads_connected = True
    if ad_accounts:
        doctor.meta_ads_account_id = ad_accounts[0]["id"]
    if pages:
        doctor.meta_ads_page_id = pages[0]["id"]

    await db.commit()

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
        phone_number_id = settings.WHATSAPP_API_TOKEN.split(":")[0] if ":" in settings.WHATSAPP_API_TOKEN else ""
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
                return {"status": "verified", "message": "WhatsApp verification message sent"}
            else:
                error_data = resp.json()
                return {"status": "error", "detail": error_data}

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
    import os

    if not getattr(doctor, 'google_ads_connected', False) and not settings.GOOGLE_ADS_DEVELOPER_TOKEN:
        raise HTTPException(status_code=400, detail="Google Ads not connected. Connect first in Settings.")

    engine = GoogleAdsEngine(db)

    # Get the customer ID
    customer_id = getattr(doctor, 'google_ads_customer_id', None) or os.getenv("GOOGLE_ADS_LOGIN_CUSTOMER_ID", "")
    if not customer_id:
        return {
            "status": "no_customer_id",
            "message": "No Google Ads customer ID found. The clinic may not have a Google Ads account yet.",
            "imported": 0,
        }

    # Fetch campaigns from Google Ads API
    metrics_data = await engine.get_campaign_metrics(customer_id, days=90)

    if metrics_data.get("status") == "demo_mode":
        # No real API — create draft campaigns from onboarding data
        campaign = await engine.create_campaign_from_onboarding(doctor)
        await db.commit()
        return {
            "status": "draft_mode",
            "message": "Google Ads API not connected with real credentials. Created draft campaign from clinic data.",
            "imported": 1,
            "campaigns": [{"name": campaign.name, "status": campaign.status.value}],
        }

    if metrics_data.get("status") != "success":
        return {
            "status": "error",
            "message": metrics_data.get("message", "Failed to fetch campaigns from Google Ads"),
            "imported": 0,
        }

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
        campaign = Campaign(
            doctor_id=doctor.id,
            platform=AdPlatform.GOOGLE,
            platform_campaign_id=str(gads_campaign["campaign_id"]),
            name=gads_campaign.get("name", "Imported Campaign"),
            campaign_type="SEARCH",
            status=CampaignStatus.ACTIVE if gads_campaign.get("status") == "ENABLED" else CampaignStatus.PAUSED,
            impressions=gads_campaign.get("impressions", 0),
            clicks=gads_campaign.get("clicks", 0),
            conversions=int(gads_campaign.get("conversions", 0)),
            spend=int(gads_campaign.get("cost_inr", 0) * 100),  # Store in paise
            cpc=gads_campaign.get("avg_cpc_inr", 0),
            ctr=gads_campaign.get("ctr", 0),
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
    else:
        return result


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
