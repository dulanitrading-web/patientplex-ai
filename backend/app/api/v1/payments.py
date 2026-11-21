"""
Payment API routes — Razorpay integration for PatientPlex subscriptions.

NOTE: Currently configured for Razorpay TEST MODE only.
Set RAZORPAY_KEY_ID (rzp_test_...) and RAZORPAY_KEY_SECRET in env vars.
Complete Razorpay KYC to go live.
"""

import logging
from datetime import datetime, timezone
from typing import Optional
from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, Request
from pydantic import BaseModel
from sqlalchemy import select, update
from sqlalchemy.ext.asyncio import AsyncSession

from app.api.v1.auth import get_current_doctor
from app.core.config import settings
from app.db.session import get_db
from app.models.billing import Subscription, SubscriptionStatus, PlanTier
from app.models.doctor import Doctor
from app.services.razorpay_service import razorpay_service, PLANS, ANNUAL_PLANS

logger = logging.getLogger(__name__)
router = APIRouter(prefix="/payments", tags=["payments"])


class CreateOrderRequest(BaseModel):
    plan_id: str  # "starter", "growth", or "enterprise"
    doctor_id: str
    annual: bool = False


class VerifyPaymentRequest(BaseModel):
    razorpay_order_id: str
    razorpay_payment_id: str
    razorpay_signature: str
    doctor_id: str
    plan_id: str


# === ENDPOINTS ===


@router.get("/plans")
async def list_plans():
    """List all available subscription plans."""
    return {
        "monthly": {k: {"name": v["name"], "amount_inr": v["amount"] / 100, "description": v["description"]}
                     for k, v in PLANS.items()},
        "annual": {k: {"name": v["name"], "amount_inr": v["amount"] / 100, "description": v["description"]}
                   for k, v in ANNUAL_PLANS.items()},
    }


@router.post("/create-order")
async def create_order(req: CreateOrderRequest):
    """Create a Razorpay order for checkout.

    Returns order_id and key_id needed for Razorpay's checkout.js.
    """
    result = razorpay_service.create_order(
        plan_id=req.plan_id,
        doctor_id=req.doctor_id,
        annual=req.annual,
    )
    if result["status"] == "error":
        raise HTTPException(status_code=400, detail=result["message"])
    return result


@router.post("/verify-payment")
async def verify_payment(
    req: VerifyPaymentRequest,
    db: AsyncSession = Depends(get_db),
):
    """Verify payment after Razorpay checkout completes.

    Called from the frontend after successful Razorpay checkout.
    Verifies the signature and activates the subscription.
    """
    result = razorpay_service.verify_payment(
        razorpay_order_id=req.razorpay_order_id,
        razorpay_payment_id=req.razorpay_payment_id,
        razorpay_signature=req.razorpay_signature,
    )

    if result["status"] in ("verified", "demo_mode"):
        # Map plan_id to tier
        tier_map = {"starter": PlanTier.STARTER, "growth": PlanTier.GROWTH, "enterprise": PlanTier.ENTERPRISE}
        tier = tier_map.get(req.plan_id, PlanTier.STARTER)

        # Upsert subscription
        doctor_uuid = UUID(req.doctor_id)
        existing = await db.execute(
            select(Subscription).where(Subscription.doctor_id == doctor_uuid)
        )
        sub = existing.scalar_one_or_none()
        if sub:
            sub.plan_tier = tier
            sub.status = SubscriptionStatus.ACTIVE
            sub.razorpay_payment_id = req.razorpay_payment_id
            sub.current_period_start = datetime.now(timezone.utc)
        else:
            sub = Subscription(
                doctor_id=doctor_uuid,
                plan_tier=tier,
                status=SubscriptionStatus.ACTIVE,
                razorpay_payment_id=req.razorpay_payment_id,
                current_period_start=datetime.now(timezone.utc),
            )
            db.add(sub)
        await db.commit()

        logger.info("Payment verified for doctor %s, plan %s", req.doctor_id, req.plan_id)
        return {
            "status": "success",
            "message": "Payment verified and subscription activated",
            "payment_id": result.get("payment_id", "demo"),
            "plan": req.plan_id,
        }

    raise HTTPException(status_code=400, detail="Payment verification failed")


@router.get("/subscription")
async def get_subscription(
    doctor: Doctor = Depends(get_current_doctor),
    db: AsyncSession = Depends(get_db),
):
    """Get current subscription status for the authenticated doctor."""
    result = await db.execute(
        select(Subscription).where(Subscription.doctor_id == doctor.id)
    )
    sub = result.scalar_one_or_none()

    if not sub:
        return {
            "doctor_id": str(doctor.id),
            "status": "inactive",
            "plan": None,
            "message": "No active subscription. Choose a plan to get started.",
        }

    return {
        "doctor_id": str(doctor.id),
        "status": sub.status.value,
        "plan": sub.plan_tier.value,
        "current_period_start": sub.current_period_start.isoformat() if sub.current_period_start else None,
        "current_period_end": sub.current_period_end.isoformat() if sub.current_period_end else None,
    }


@router.post("/webhook")
async def razorpay_webhook(request: Request, db: AsyncSession = Depends(get_db)):
    """Razorpay webhook receiver with signature verification.

    Handles: payment.captured, payment.failed,
    subscription.activated, subscription.cancelled, subscription.charged.
    Updates subscription status in the database.
    """
    body = await request.body()
    signature = request.headers.get("X-Razorpay-Signature", "")

    if not razorpay_service.verify_webhook_signature(body, signature):
        raise HTTPException(status_code=401, detail="Invalid webhook signature")

    payload = await request.json()
    event_type = payload.get("event", "")
    event_payload = payload.get("payload", {})

    logger.info("Razorpay webhook: %s", event_type)
    result = razorpay_service.process_webhook_event(event_type, event_payload)
    doctor_id = result.get("doctor_id")

    if result["action"] == "activate_subscription" and doctor_id:
        try:
            doctor_uuid = UUID(doctor_id)
            await db.execute(
                update(Subscription)
                .where(Subscription.doctor_id == doctor_uuid)
                .values(status=SubscriptionStatus.ACTIVE)
            )
            await db.commit()
            logger.info("Subscription activated for doctor %s", doctor_id)
        except Exception:
            logger.exception("Failed to activate subscription for %s", doctor_id)

    elif result["action"] == "notify_payment_failure":
        logger.warning("Payment failed for doctor %s: %s", doctor_id, result.get("reason"))
        if doctor_id:
            try:
                doctor_uuid = UUID(doctor_id)
                await db.execute(
                    update(Subscription)
                    .where(Subscription.doctor_id == doctor_uuid)
                    .values(status=SubscriptionStatus.PAST_DUE)
                )
                await db.commit()
            except Exception:
                logger.exception("Failed to mark past_due for %s", doctor_id)

    elif result["action"] == "cancel_subscription":
        sub_id = result.get("subscription_id")
        if sub_id:
            try:
                await db.execute(
                    update(Subscription)
                    .where(Subscription.razorpay_subscription_id == sub_id)
                    .values(status=SubscriptionStatus.CANCELLED)
                )
                await db.commit()
                logger.info("Subscription cancelled: %s", sub_id)
            except Exception:
                logger.exception("Failed to cancel subscription %s", sub_id)

    elif result["action"] == "record_renewal":
        logger.info("Subscription renewed: %s", result.get("subscription_id"))

    return {"status": "ok", "processed": event_type}


@router.get("/status")
async def payment_status():
    """Check if payment integration is active."""
    return {
        "razorpay_connected": razorpay_service.is_connected,
        "plans_available": len(PLANS),
    }
