"""Webhook handlers for real-time platform events.

Receives notifications from:
- Google Ads — campaign status changes, budget alerts, ad disapprovals
- Meta Marketing API — ad account and campaign status changes
- WhatsApp Business API — message delivery status callbacks
- Razorpay — payment and subscription events
"""

import hashlib
import hmac
import logging
from datetime import datetime, timezone

from fastapi import APIRouter, Depends, Header, HTTPException, Query, Request
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.config import settings
from app.db.session import get_db

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/webhooks", tags=["webhooks"])


# ──────────────────────────────────────────────────────────
# Google Ads webhooks
# ──────────────────────────────────────────────────────────

@router.post("/google-ads")
async def google_ads_webhook(request: Request, db: AsyncSession = Depends(get_db)):
    """Handle Google Ads push notifications.

    Events:
    - CAMPAIGN_STATUS_CHANGED: campaign enabled/paused/removed
    - BUDGET_EXHAUSTED: daily or total budget reached
    - AD_DISAPPROVED: ad failed policy review
    """
    body = await request.json()
    event_type = body.get("event_type")
    logger.info("Google Ads webhook: %s", event_type)

    try:
        if event_type == "CAMPAIGN_STATUS_CHANGED":
            await _handle_google_campaign_status(body, db)
        elif event_type == "BUDGET_EXHAUSTED":
            await _handle_google_budget_exhausted(body, db)
        elif event_type == "AD_DISAPPROVED":
            await _handle_google_ad_disapproved(body, db)
        else:
            logger.warning("Unknown Google Ads event type: %s", event_type)

    except Exception as exc:
        logger.error("Google Ads webhook processing error: %s", exc)
        # Return 200 to prevent retries for non-transient errors
        return {"status": "error", "message": str(exc)}

    return {"status": "ok"}


async def _handle_google_campaign_status(body: dict, db: AsyncSession):
    """Update local campaign status when it changes on Google Ads."""
    from app.models.campaign import Campaign, CampaignStatus

    platform_id = body.get("campaign_id")
    new_status = body.get("status")

    if not platform_id:
        return

    result = await db.execute(
        select(Campaign).where(Campaign.platform_campaign_id == platform_id)
    )
    campaign = result.scalar_one_or_none()
    if campaign:
        status_map = {
            "ENABLED": CampaignStatus.ACTIVE,
            "PAUSED": CampaignStatus.PAUSED,
            "REMOVED": CampaignStatus.COMPLETED,
        }
        if new_status in status_map:
            campaign.status = status_map[new_status]
            await db.commit()
            logger.info("Campaign '%s' status updated to %s", campaign.name, new_status)


async def _handle_google_budget_exhausted(body: dict, db: AsyncSession):
    """Handle budget exhaustion notification."""
    campaign_id = body.get("campaign_id")
    logger.warning("Budget exhausted for Google campaign %s", campaign_id)
    # TODO: Send notification to doctor via WhatsApp or email
    # TODO: Optionally auto-increase budget if within monthly limit


async def _handle_google_ad_disapproved(body: dict, db: AsyncSession):
    """Handle ad disapproval — update status and notify."""
    from app.models.campaign import Campaign, CampaignStatus

    platform_id = body.get("campaign_id")
    reason = body.get("disapproval_reason", "Unknown")

    result = await db.execute(
        select(Campaign).where(Campaign.platform_campaign_id == platform_id)
    )
    campaign = result.scalar_one_or_none()
    if campaign:
        campaign.status = CampaignStatus.ERROR
        campaign.error_message = f"Ad disapproved: {reason}"
        await db.commit()
        logger.warning("Ad disapproved for campaign '%s': %s", campaign.name, reason)
        # TODO: Notify doctor and auto-generate compliant ad copy


# ──────────────────────────────────────────────────────────
# Meta Marketing API webhooks
# ──────────────────────────────────────────────────────────

@router.get("/meta")
async def meta_webhook_verify(
    hub_mode: str = Query(alias="hub.mode"),
    hub_verify_token: str = Query(alias="hub.verify_token"),
    hub_challenge: str = Query(alias="hub.challenge"),
):
    """Meta webhook subscription verification (GET)."""
    if hub_mode == "subscribe" and hub_verify_token == settings.WHATSAPP_VERIFY_TOKEN:
        logger.info("Meta webhook verified")
        return int(hub_challenge)
    raise HTTPException(status_code=403, detail="Verification failed")


@router.post("/meta")
async def meta_webhook(request: Request, db: AsyncSession = Depends(get_db)):
    """Handle Meta Marketing API events.

    Events:
    - ad_account changes: status, spend limit
    - campaign changes: status, budget, delivery
    """
    body = await request.json()
    entries = body.get("entry", [])

    for entry in entries:
        changes = entry.get("changes", [])
        for change in changes:
            field = change.get("field")
            value = change.get("value", {})
            logger.info("Meta webhook: field=%s", field)

            if field == "campaign_status":
                await _handle_meta_campaign_status(value, db)
            elif field == "ad_account":
                await _handle_meta_account_change(value, db)

    return {"status": "ok"}


async def _handle_meta_campaign_status(value: dict, db: AsyncSession):
    """Update local campaign when Meta campaign status changes."""
    from app.models.campaign import Campaign, CampaignStatus

    platform_id = str(value.get("campaign_id", ""))
    if not platform_id:
        return

    result = await db.execute(
        select(Campaign).where(Campaign.platform_campaign_id == platform_id)
    )
    campaign = result.scalar_one_or_none()
    if campaign:
        status = value.get("effective_status", "").upper()
        status_map = {
            "ACTIVE": CampaignStatus.ACTIVE,
            "PAUSED": CampaignStatus.PAUSED,
            "DELETED": CampaignStatus.COMPLETED,
            "DISAPPROVED": CampaignStatus.ERROR,
        }
        if status in status_map:
            campaign.status = status_map[status]
            await db.commit()


async def _handle_meta_account_change(value: dict, db: AsyncSession):
    """Handle Meta ad account changes."""
    logger.info("Meta account change: %s", value)
    # TODO: Handle account spend limits, status changes


# ──────────────────────────────────────────────────────────
# WhatsApp message status callbacks
# ──────────────────────────────────────────────────────────

@router.post("/whatsapp/status")
async def whatsapp_status_webhook(request: Request, db: AsyncSession = Depends(get_db)):
    """Handle WhatsApp Cloud API message status updates.

    Statuses: sent, delivered, read, failed
    """
    body = await request.json()
    entries = body.get("entry", [])

    for entry in entries:
        changes = entry.get("changes", [])
        for change in changes:
            value = change.get("value", {})
            statuses = value.get("statuses", [])

            for status in statuses:
                msg_id = status.get("id")
                msg_status = status.get("status")  # sent, delivered, read, failed
                recipient = status.get("recipient_id")
                timestamp = status.get("timestamp")

                logger.info(
                    "WhatsApp status: msg=%s status=%s recipient=%s",
                    msg_id, msg_status, recipient,
                )

                if msg_status == "failed":
                    errors = status.get("errors", [])
                    error_msg = errors[0].get("message", "Unknown") if errors else "Unknown"
                    logger.error("WhatsApp message failed: %s — %s", msg_id, error_msg)
                    # TODO: Retry or notify doctor

                # TODO: Update conversation record with delivery status

    return {"status": "ok"}


# ──────────────────────────────────────────────────────────
# Razorpay payment webhooks
# ──────────────────────────────────────────────────────────

@router.post("/razorpay")
async def razorpay_webhook(
    request: Request,
    db: AsyncSession = Depends(get_db),
    x_razorpay_signature: str | None = Header(None),
):
    """Handle Razorpay payment and subscription events.

    Events:
    - payment.captured: payment successful
    - payment.failed: payment failed
    - subscription.activated: new subscription started
    - subscription.charged: recurring payment successful
    - subscription.cancelled: subscription cancelled
    """
    body_bytes = await request.body()

    # Verify webhook signature
    if settings.RAZORPAY_KEY_SECRET and x_razorpay_signature:
        expected = hmac.new(
            settings.RAZORPAY_KEY_SECRET.encode(),
            body_bytes,
            hashlib.sha256,
        ).hexdigest()
        if not hmac.compare_digest(expected, x_razorpay_signature):
            logger.warning("Invalid Razorpay webhook signature")
            raise HTTPException(status_code=400, detail="Invalid signature")

    body = await request.json()
    event = body.get("event")
    payload = body.get("payload", {})

    logger.info("Razorpay webhook: %s", event)

    try:
        if event == "payment.captured":
            await _handle_payment_captured(payload, db)
        elif event == "payment.failed":
            await _handle_payment_failed(payload, db)
        elif event == "subscription.activated":
            await _handle_subscription_activated(payload, db)
        elif event == "subscription.charged":
            await _handle_subscription_charged(payload, db)
        elif event == "subscription.cancelled":
            await _handle_subscription_cancelled(payload, db)
        else:
            logger.info("Unhandled Razorpay event: %s", event)

    except Exception as exc:
        logger.error("Razorpay webhook processing error: %s", exc)

    return {"status": "ok"}


async def _handle_payment_captured(payload: dict, db: AsyncSession):
    """Process successful payment."""
    payment = payload.get("payment", {}).get("entity", {})
    amount_inr = payment.get("amount", 0) / 100  # paise → rupees
    notes = payment.get("notes", {})
    doctor_id = notes.get("doctor_id")

    logger.info("Payment captured: ₹%.2f for doctor %s", amount_inr, doctor_id)

    # TODO: Update subscription record, activate features
    # TODO: Send payment confirmation via WhatsApp


async def _handle_payment_failed(payload: dict, db: AsyncSession):
    """Handle failed payment — notify and potentially pause campaigns."""
    payment = payload.get("payment", {}).get("entity", {})
    error = payment.get("error_description", "Unknown")
    notes = payment.get("notes", {})
    doctor_id = notes.get("doctor_id")

    logger.warning("Payment failed for doctor %s: %s", doctor_id, error)
    # TODO: Notify doctor, pause campaigns after grace period


async def _handle_subscription_activated(payload: dict, db: AsyncSession):
    """New subscription activated."""
    sub = payload.get("subscription", {}).get("entity", {})
    logger.info("Subscription activated: %s", sub.get("id"))
    # TODO: Update billing record, enable features


async def _handle_subscription_charged(payload: dict, db: AsyncSession):
    """Recurring subscription payment successful."""
    sub = payload.get("subscription", {}).get("entity", {})
    logger.info("Subscription charged: %s", sub.get("id"))
    # TODO: Record payment, extend subscription period


async def _handle_subscription_cancelled(payload: dict, db: AsyncSession):
    """Subscription cancelled."""
    sub = payload.get("subscription", {}).get("entity", {})
    logger.info("Subscription cancelled: %s", sub.get("id"))
    # TODO: Mark subscription as cancelled, schedule campaign pause
