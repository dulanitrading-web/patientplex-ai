"""Razorpay subscription billing service.

Handles:
- Creating Razorpay customers and subscriptions
- Plan upgrades/downgrades
- Webhook processing for payment events
- Usage limit enforcement
- Invoice generation

Razorpay Subscriptions API: https://razorpay.com/docs/api/subscriptions/
"""

import logging
from datetime import datetime, timedelta, timezone
from uuid import UUID

import httpx
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.config import settings
from app.models.billing import (
    Invoice,
    PLAN_CONFIG,
    PlanTier,
    Subscription,
    SubscriptionStatus,
)
from app.models.doctor import Doctor

logger = logging.getLogger(__name__)

RAZORPAY_BASE = "https://api.razorpay.com/v1"


class BillingService:
    """Manages subscriptions and payments via Razorpay."""

    def __init__(self, db: AsyncSession):
        self.db = db
        self.key_id = settings.RAZORPAY_KEY_ID
        self.key_secret = settings.RAZORPAY_KEY_SECRET

    async def create_trial(self, doctor_id: UUID) -> Subscription:
        """Start a 14-day free trial for a new doctor. Called after onboarding."""
        now = datetime.now(timezone.utc)

        subscription = Subscription(
            doctor_id=doctor_id,
            plan=PlanTier.FREE_TRIAL,
            status=SubscriptionStatus.TRIAL,
            price_inr=0,
            trial_started_at=now,
            trial_ends_at=now + timedelta(days=14),
            current_period_start=now,
            current_period_end=now + timedelta(days=14),
            usage_reset_at=now,
        )
        self.db.add(subscription)
        await self.db.flush()

        logger.info("Free trial started for doctor %s (14 days)", doctor_id)
        return subscription

    async def get_subscription(self, doctor_id: UUID) -> Subscription | None:
        """Get the current subscription for a doctor."""
        result = await self.db.execute(
            select(Subscription).where(Subscription.doctor_id == doctor_id)
        )
        return result.scalar_one_or_none()

    async def create_razorpay_subscription(
        self,
        doctor: Doctor,
        plan: PlanTier,
    ) -> dict:
        """Create a Razorpay subscription for a paid plan.

        Returns a dict with subscription_id and short_url for checkout.
        """
        config = PLAN_CONFIG[plan]

        # In production: create Razorpay plan and subscription
        # Step 1: Create or get Razorpay customer
        # Step 2: Create subscription
        # customer = await self._create_razorpay_customer(doctor)
        # sub = await self._create_razorpay_sub(customer["id"], plan_id)

        # For now, update the local subscription
        subscription = await self.get_subscription(doctor.id)
        if not subscription:
            subscription = await self.create_trial(doctor.id)

        now = datetime.now(timezone.utc)
        subscription.plan = plan
        subscription.status = SubscriptionStatus.ACTIVE
        subscription.price_inr = config["price_inr"]
        subscription.current_period_start = now
        subscription.current_period_end = now + timedelta(days=30)
        subscription.conversations_this_month = 0

        await self.db.commit()

        return {
            "subscription_id": str(subscription.id),
            "plan": plan.value,
            "price_inr": config["price_inr"],
            "status": "active",
            # In production: return Razorpay checkout URL
            # "checkout_url": sub["short_url"],
        }

    async def handle_razorpay_webhook(self, event: str, payload: dict) -> dict:
        """Process Razorpay webhook events.

        Events handled:
        - subscription.activated — payment successful, activate plan
        - subscription.charged — recurring payment successful
        - subscription.cancelled — subscription cancelled
        - payment.failed — payment failed, mark as past_due
        """
        if event == "subscription.activated":
            sub_id = payload.get("subscription", {}).get("id")
            result = await self.db.execute(
                select(Subscription).where(Subscription.razorpay_subscription_id == sub_id)
            )
            subscription = result.scalar_one_or_none()
            if subscription:
                subscription.status = SubscriptionStatus.ACTIVE
                await self.db.commit()
                return {"handled": True, "action": "activated"}

        elif event == "subscription.charged":
            sub_id = payload.get("subscription", {}).get("id")
            payment_id = payload.get("payment", {}).get("entity", {}).get("id")
            amount = payload.get("payment", {}).get("entity", {}).get("amount", 0)

            result = await self.db.execute(
                select(Subscription).where(Subscription.razorpay_subscription_id == sub_id)
            )
            subscription = result.scalar_one_or_none()
            if subscription:
                now = datetime.now(timezone.utc)
                subscription.current_period_start = now
                subscription.current_period_end = now + timedelta(days=30)
                subscription.conversations_this_month = 0

                # Create invoice
                invoice = Invoice(
                    doctor_id=subscription.doctor_id,
                    subscription_id=subscription.id,
                    razorpay_payment_id=payment_id,
                    amount_inr=amount // 100,
                    status="paid",
                    plan=subscription.plan.value,
                    period_start=now,
                    period_end=now + timedelta(days=30),
                )
                self.db.add(invoice)
                await self.db.commit()
                return {"handled": True, "action": "charged", "invoice_id": str(invoice.id)}

        elif event == "payment.failed":
            sub_id = payload.get("subscription", {}).get("id")
            result = await self.db.execute(
                select(Subscription).where(Subscription.razorpay_subscription_id == sub_id)
            )
            subscription = result.scalar_one_or_none()
            if subscription:
                subscription.status = SubscriptionStatus.PAST_DUE
                await self.db.commit()
                return {"handled": True, "action": "past_due"}

        return {"handled": False, "event": event}

    async def check_limit(self, doctor_id: UUID, feature: str) -> dict:
        """Check if a doctor can use a feature based on their plan.

        Returns: {"allowed": bool, "reason": str, "usage": int, "limit": int}
        """
        subscription = await self.get_subscription(doctor_id)
        if not subscription:
            return {"allowed": False, "reason": "No subscription", "upgrade_to": "STARTER"}

        # Check trial expiry
        if subscription.status == SubscriptionStatus.TRIAL:
            if subscription.trial_ends_at and subscription.trial_ends_at < datetime.now(timezone.utc):
                subscription.status = SubscriptionStatus.EXPIRED
                await self.db.commit()
                return {"allowed": False, "reason": "Trial expired", "upgrade_to": "STARTER"}

        if subscription.status not in (SubscriptionStatus.TRIAL, SubscriptionStatus.ACTIVE):
            return {"allowed": False, "reason": f"Subscription {subscription.status.value}", "upgrade_to": "STARTER"}

        config = PLAN_CONFIG.get(subscription.plan, PLAN_CONFIG[PlanTier.FREE_TRIAL])

        # Check conversation limit
        if feature == "conversation":
            limit = config["max_conversations"]
            if limit > 0 and subscription.conversations_this_month >= limit:
                return {
                    "allowed": False,
                    "reason": f"Conversation limit reached ({limit}/month)",
                    "usage": subscription.conversations_this_month,
                    "limit": limit,
                    "upgrade_to": "GROWTH",
                }

        # Check campaign limit
        if feature == "campaign":
            limit = config["max_campaigns"]
            if limit > 0 and subscription.campaigns_count >= limit:
                return {
                    "allowed": False,
                    "reason": f"Campaign limit reached ({limit})",
                    "usage": subscription.campaigns_count,
                    "limit": limit,
                    "upgrade_to": "GROWTH",
                }

        # Check platform access
        if feature in ("META", "LINKEDIN"):
            if feature not in config["platforms"]:
                return {
                    "allowed": False,
                    "reason": f"{feature} ads requires Growth plan",
                    "upgrade_to": "GROWTH",
                }

        # Check specific features
        if feature in ("competitive_intel", "conversion_tracking", "daily_summary"):
            if feature not in config["features"]:
                return {
                    "allowed": False,
                    "reason": f"{feature} requires Growth plan",
                    "upgrade_to": "GROWTH",
                }

        return {"allowed": True, "plan": subscription.plan.value}

    async def increment_usage(self, doctor_id: UUID, feature: str) -> None:
        """Increment usage counter after a feature is used."""
        subscription = await self.get_subscription(doctor_id)
        if not subscription:
            return

        if feature == "conversation":
            subscription.conversations_this_month += 1
        elif feature == "campaign":
            subscription.campaigns_count += 1

        await self.db.flush()
