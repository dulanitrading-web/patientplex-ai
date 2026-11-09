"""
Payment API routes — Razorpay integration for PatientPlex subscriptions.
"""

import logging
from typing import Optional

from fastapi import APIRouter, HTTPException, Request
from pydantic import BaseModel

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
async def verify_payment(req: VerifyPaymentRequest):
    """Verify payment after Razorpay checkout completes.

    Called from the frontend after successful Razorpay checkout.
    Verifies the signature and activates the subscription.
    """
    result = razorpay_service.verify_payment(
        razorpay_order_id=req.razorpay_order_id,
        razorpay_payment_id=req.razorpay_payment_id,
        razorpay_signature=req.razorpay_signature,
    )

    if result["status"] == "verified":
        # TODO: Update doctor's subscription status in DB
        # await db.execute(
        #     update(Doctor).where(Doctor.id == req.doctor_id).values(
        #         plan=req.plan_id, subscription_status="active",
        #         razorpay_payment_id=req.razorpay_payment_id,
        #     )
        # )
        logger.info(f"Payment verified for doctor {req.doctor_id}, plan {req.plan_id}")
        return {
            "status": "success",
            "message": "Payment verified and subscription activated",
            "payment_id": result["payment_id"],
        }

    raise HTTPException(status_code=400, detail="Payment verification failed")


@router.get("/subscription/{doctor_id}")
async def get_subscription(doctor_id: str):
    """Get current subscription status for a doctor."""
    # TODO: Fetch from DB
    return {
        "doctor_id": doctor_id,
        "status": "inactive",
        "plan": None,
        "message": "No active subscription. Choose a plan to get started.",
    }


@router.post("/webhook")
async def razorpay_webhook(request: Request):
    """Razorpay webhook receiver.

    Handles: payment.captured, payment.failed,
    subscription.activated, subscription.cancelled, subscription.charged
    """
    body = await request.body()
    signature = request.headers.get("X-Razorpay-Signature", "")

    if not razorpay_service.verify_webhook_signature(body, signature):
        raise HTTPException(status_code=401, detail="Invalid webhook signature")

    payload = await request.json()
    event_type = payload.get("event", "")
    event_payload = payload.get("payload", {})

    logger.info(f"Razorpay webhook: {event_type}")
    result = razorpay_service.process_webhook_event(event_type, event_payload)

    # TODO: Process each action type
    if result["action"] == "activate_subscription":
        logger.info(f"Activating subscription: {result}")
        # Update DB, send confirmation WhatsApp
    elif result["action"] == "notify_payment_failure":
        logger.warning(f"Payment failed: {result}")
        # Notify doctor via WhatsApp/email
    elif result["action"] == "cancel_subscription":
        logger.info(f"Subscription cancelled: {result}")
        # Update DB, send confirmation
    elif result["action"] == "record_renewal":
        logger.info(f"Subscription renewed: {result}")
        # Record in billing table

    return {"status": "ok", "processed": event_type}


@router.get("/status")
async def payment_status():
    """Check if payment integration is active."""
    return {
        "razorpay_connected": razorpay_service.is_connected,
        "plans_available": len(PLANS),
    }
