"""
Razorpay Payment Integration for PatientPlex AI.

Handles subscription creation, order management, payment verification,
and webhook processing for the SaaS billing model.
"""

import hashlib
import hmac
import logging
import os
from typing import Dict, Optional

logger = logging.getLogger(__name__)

# Plan definitions matching the pricing page
PLANS = {
    "starter": {
        "name": "Starter",
        "amount": 499900,  # ₹4,999 in paise
        "currency": "INR",
        "period": "monthly",
        "description": "PatientPlex Starter — 1 location, Google + WhatsApp",
    },
    "growth": {
        "name": "Growth",
        "amount": 1499900,  # ₹14,999 in paise
        "currency": "INR",
        "period": "monthly",
        "description": "PatientPlex Growth — 3 locations, all platforms, AI receptionist",
    },
    "enterprise": {
        "name": "Enterprise",
        "amount": 2499900,  # ₹24,999 in paise
        "currency": "INR",
        "period": "monthly",
        "description": "PatientPlex Enterprise — unlimited locations, dedicated manager",
    },
}

ANNUAL_PLANS = {
    "starter_annual": {
        "name": "Starter Annual",
        "amount": 399900,  # ₹3,999/mo billed annually
        "currency": "INR",
        "period": "yearly",
        "description": "PatientPlex Starter Annual — save 20%",
    },
    "growth_annual": {
        "name": "Growth Annual",
        "amount": 1199900,  # ₹11,999/mo billed annually
        "currency": "INR",
        "period": "yearly",
        "description": "PatientPlex Growth Annual — save 20%",
    },
    "enterprise_annual": {
        "name": "Enterprise Annual",
        "amount": 1999900,  # ₹19,999/mo billed annually
        "currency": "INR",
        "period": "yearly",
        "description": "PatientPlex Enterprise Annual — save 20%",
    },
}


class RazorpayService:
    """Production Razorpay payment integration."""

    def __init__(self):
        self.key_id = os.getenv("RAZORPAY_KEY_ID", "")
        self.key_secret = os.getenv("RAZORPAY_KEY_SECRET", "")
        self.webhook_secret = os.getenv("RAZORPAY_WEBHOOK_SECRET", "")
        self.client = None
        self._initialize()

    def _initialize(self):
        if self.key_id and self.key_secret:
            try:
                import razorpay
                self.client = razorpay.Client(auth=(self.key_id, self.key_secret))
                logger.info("Razorpay client initialized")
            except ImportError:
                logger.error("razorpay package not installed")
            except Exception as e:
                logger.error(f"Razorpay init failed: {e}")
        else:
            logger.warning("Razorpay credentials not set — running in demo mode")

    @property
    def is_connected(self) -> bool:
        return self.client is not None

    # === ORDER MANAGEMENT ===

    def create_order(self, plan_id: str, doctor_id: str, annual: bool = False) -> Dict:
        """Create a Razorpay order for a subscription plan."""
        plans = ANNUAL_PLANS if annual else PLANS
        plan = plans.get(plan_id if not annual else f"{plan_id}_annual")
        if not plan:
            return {"status": "error", "message": f"Invalid plan: {plan_id}"}

        if not self.is_connected:
            return {
                "status": "demo_mode",
                "message": "Razorpay not configured. Set RAZORPAY_KEY_ID and RAZORPAY_KEY_SECRET.",
                "demo_order": {
                    "id": "order_demo_123",
                    "amount": plan["amount"],
                    "currency": plan["currency"],
                },
            }

        try:
            order_data = {
                "amount": plan["amount"],
                "currency": plan["currency"],
                "receipt": f"pp_{doctor_id}_{plan_id}",
                "notes": {
                    "doctor_id": doctor_id,
                    "plan_id": plan_id,
                    "plan_name": plan["name"],
                    "annual": str(annual),
                },
            }
            order = self.client.order.create(data=order_data)
            logger.info(f"Order created: {order['id']} for doctor {doctor_id}, plan {plan_id}")
            return {
                "status": "created",
                "order_id": order["id"],
                "amount": order["amount"],
                "currency": order["currency"],
                "key_id": self.key_id,
                "plan_name": plan["name"],
                "description": plan["description"],
            }
        except Exception as e:
            logger.error(f"Order creation failed: {e}")
            return {"status": "error", "message": str(e)}

    def verify_payment(self, razorpay_order_id: str, razorpay_payment_id: str,
                       razorpay_signature: str) -> Dict:
        """Verify payment signature after Razorpay checkout."""
        if not self.is_connected:
            return {"status": "demo_mode", "verified": True}

        try:
            self.client.utility.verify_payment_signature({
                "razorpay_order_id": razorpay_order_id,
                "razorpay_payment_id": razorpay_payment_id,
                "razorpay_signature": razorpay_signature,
            })
            logger.info(f"Payment verified: {razorpay_payment_id}")
            return {
                "status": "verified",
                "payment_id": razorpay_payment_id,
                "order_id": razorpay_order_id,
            }
        except Exception as e:
            logger.error(f"Payment verification failed: {e}")
            return {"status": "failed", "message": "Payment verification failed"}

    def get_payment_details(self, payment_id: str) -> Dict:
        """Fetch payment details from Razorpay."""
        if not self.is_connected:
            return {"status": "demo_mode"}

        try:
            payment = self.client.payment.fetch(payment_id)
            return {
                "status": "success",
                "payment": {
                    "id": payment["id"],
                    "amount": payment["amount"],
                    "currency": payment["currency"],
                    "status": payment["status"],
                    "method": payment.get("method", ""),
                    "email": payment.get("email", ""),
                    "contact": payment.get("contact", ""),
                    "created_at": payment.get("created_at"),
                },
            }
        except Exception as e:
            return {"status": "error", "message": str(e)}

    # === SUBSCRIPTION MANAGEMENT ===

    def create_razorpay_plan(self, plan_id: str) -> Dict:
        """Create a Razorpay subscription plan (one-time setup)."""
        if not self.is_connected:
            return {"status": "demo_mode"}

        plan = PLANS.get(plan_id)
        if not plan:
            return {"status": "error", "message": f"Invalid plan: {plan_id}"}

        try:
            rz_plan = self.client.plan.create({
                "period": plan["period"],
                "interval": 1,
                "item": {
                    "name": plan["name"],
                    "amount": plan["amount"],
                    "currency": plan["currency"],
                    "description": plan["description"],
                },
            })
            logger.info(f"Razorpay plan created: {rz_plan['id']} for {plan_id}")
            return {"status": "created", "plan_id": rz_plan["id"]}
        except Exception as e:
            return {"status": "error", "message": str(e)}

    def create_subscription(self, razorpay_plan_id: str, doctor_id: str,
                            total_count: int = 12) -> Dict:
        """Create a subscription for a doctor."""
        if not self.is_connected:
            return {"status": "demo_mode"}

        try:
            sub = self.client.subscription.create({
                "plan_id": razorpay_plan_id,
                "total_count": total_count,
                "notes": {"doctor_id": doctor_id},
            })
            return {
                "status": "created",
                "subscription_id": sub["id"],
                "short_url": sub.get("short_url", ""),
            }
        except Exception as e:
            return {"status": "error", "message": str(e)}

    def cancel_subscription(self, subscription_id: str, cancel_at_cycle_end: bool = True) -> Dict:
        """Cancel a subscription."""
        if not self.is_connected:
            return {"status": "demo_mode"}

        try:
            self.client.subscription.cancel(
                subscription_id,
                {"cancel_at_cycle_end": 1 if cancel_at_cycle_end else 0},
            )
            return {"status": "cancelled", "subscription_id": subscription_id}
        except Exception as e:
            return {"status": "error", "message": str(e)}

    # === WEBHOOK ===

    def verify_webhook_signature(self, body: bytes, signature: str) -> bool:
        """Verify Razorpay webhook signature."""
        if not self.webhook_secret:
            logger.warning("RAZORPAY_WEBHOOK_SECRET not set — skipping verification")
            return True

        expected = hmac.new(
            self.webhook_secret.encode("utf-8"),
            body,
            hashlib.sha256,
        ).hexdigest()
        return hmac.compare_digest(expected, signature)

    def process_webhook_event(self, event_type: str, payload: Dict) -> Dict:
        """Process a Razorpay webhook event."""
        entity = payload.get("payment", {}).get("entity", {}) or payload.get("subscription", {}).get("entity", {})

        if event_type == "payment.captured":
            return {
                "action": "activate_subscription",
                "payment_id": entity.get("id"),
                "amount": entity.get("amount"),
                "doctor_id": entity.get("notes", {}).get("doctor_id"),
            }
        elif event_type == "payment.failed":
            return {
                "action": "notify_payment_failure",
                "payment_id": entity.get("id"),
                "doctor_id": entity.get("notes", {}).get("doctor_id"),
                "reason": entity.get("error_description", "Unknown"),
            }
        elif event_type == "subscription.activated":
            return {
                "action": "activate_subscription",
                "subscription_id": entity.get("id"),
                "plan_id": entity.get("plan_id"),
            }
        elif event_type == "subscription.cancelled":
            return {
                "action": "cancel_subscription",
                "subscription_id": entity.get("id"),
            }
        elif event_type == "subscription.charged":
            return {
                "action": "record_renewal",
                "subscription_id": entity.get("id"),
                "amount": entity.get("amount"),
            }
        else:
            return {"action": "unhandled", "event": event_type}


razorpay_service = RazorpayService()
