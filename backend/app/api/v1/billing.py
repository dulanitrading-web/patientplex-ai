"""Billing and subscription management endpoints."""

import hashlib
import hmac
import logging

from fastapi import APIRouter, Depends, HTTPException, Request
from pydantic import BaseModel
from sqlalchemy.ext.asyncio import AsyncSession

from app.api.v1.auth import get_current_doctor
from app.core.config import settings
from app.db.session import get_db
from app.models.billing import PLAN_CONFIG, PlanTier
from app.models.doctor import Doctor
from app.services.billing_service import BillingService

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/billing", tags=["billing"])


class SubscribeRequest(BaseModel):
    plan: str  # STARTER, GROWTH, ENTERPRISE


@router.get("/plans")
async def list_plans():
    """List all available subscription plans with pricing and features."""
    plans = []
    for tier, config in PLAN_CONFIG.items():
        if tier == PlanTier.FREE_TRIAL:
            continue
        plans.append({
            "id": tier.value,
            "name": tier.value.replace("_", " ").title(),
            "price_inr": config["price_inr"],
            "max_conversations": config["max_conversations"],
            "max_campaigns": config["max_campaigns"],
            "platforms": config["platforms"],
            "features": config["features"],
        })
    return {"plans": plans}


@router.get("/subscription")
async def get_subscription(
    doctor: Doctor = Depends(get_current_doctor),
    db: AsyncSession = Depends(get_db),
):
    """Get the doctor's current subscription status."""
    billing = BillingService(db)
    sub = await billing.get_subscription(doctor.id)

    if not sub:
        return {"subscription": None, "message": "No subscription. Start a free trial."}

    config = PLAN_CONFIG.get(sub.plan, {})

    return {
        "subscription": {
            "id": str(sub.id),
            "plan": sub.plan.value,
            "status": sub.status.value,
            "price_inr": sub.price_inr,
            "trial_ends_at": sub.trial_ends_at.isoformat() if sub.trial_ends_at else None,
            "current_period_end": sub.current_period_end.isoformat() if sub.current_period_end else None,
            "conversations_used": sub.conversations_this_month,
            "conversations_limit": config.get("max_conversations", 0),
            "campaigns_used": sub.campaigns_count,
            "campaigns_limit": config.get("max_campaigns", 0),
        },
    }


@router.post("/subscribe")
async def subscribe(
    body: SubscribeRequest,
    doctor: Doctor = Depends(get_current_doctor),
    db: AsyncSession = Depends(get_db),
):
    """Subscribe to a paid plan (or upgrade/downgrade)."""
    try:
        plan = PlanTier(body.plan)
    except ValueError:
        raise HTTPException(status_code=400, detail=f"Invalid plan: {body.plan}")

    if plan == PlanTier.FREE_TRIAL:
        raise HTTPException(status_code=400, detail="Cannot subscribe to free trial directly")

    billing = BillingService(db)
    result = await billing.create_razorpay_subscription(doctor, plan)
    return result


@router.post("/start-trial")
async def start_trial(
    doctor: Doctor = Depends(get_current_doctor),
    db: AsyncSession = Depends(get_db),
):
    """Start a 14-day free trial."""
    billing = BillingService(db)
    existing = await billing.get_subscription(doctor.id)
    if existing:
        raise HTTPException(status_code=400, detail="Trial already started")

    sub = await billing.create_trial(doctor.id)
    await db.commit()

    return {
        "message": "14-day free trial started",
        "trial_ends_at": sub.trial_ends_at.isoformat() if sub.trial_ends_at else None,
        "plan": "FREE_TRIAL",
    }


@router.get("/check/{feature}")
async def check_feature_access(
    feature: str,
    doctor: Doctor = Depends(get_current_doctor),
    db: AsyncSession = Depends(get_db),
):
    """Check if the doctor's plan allows a specific feature."""
    billing = BillingService(db)
    return await billing.check_limit(doctor.id, feature)


@router.post("/webhook/razorpay")
async def razorpay_webhook(request: Request, db: AsyncSession = Depends(get_db)):
    """Razorpay webhook handler — processes payment and subscription events.

    Razorpay sends: subscription.activated, subscription.charged,
    subscription.cancelled, payment.failed, etc.
    """
    body = await request.body()
    signature = request.headers.get("X-Razorpay-Signature", "")

    # Verify webhook signature
    # In production, verify: hmac.new(webhook_secret, body, hashlib.sha256).hexdigest() == signature

    try:
        payload = await request.json()
    except Exception:
        raise HTTPException(status_code=400, detail="Invalid JSON")

    event = payload.get("event", "")
    event_payload = payload.get("payload", {})

    billing = BillingService(db)
    result = await billing.handle_razorpay_webhook(event, event_payload)

    logger.info("Razorpay webhook: event=%s result=%s", event, result)
    return {"status": "ok", **result}
