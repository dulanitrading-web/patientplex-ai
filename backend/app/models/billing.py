"""Billing and subscription models."""

import enum
import uuid
from datetime import datetime, timezone

from sqlalchemy import (
    Boolean, DateTime, Enum, Float, ForeignKey, Integer, JSON, String, Text,
)
from app.db.types import PortableUUID as UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.base import Base


class PlanTier(str, enum.Enum):
    FREE_TRIAL = "FREE_TRIAL"
    STARTER = "STARTER"
    GROWTH = "GROWTH"
    ENTERPRISE = "ENTERPRISE"


class SubscriptionStatus(str, enum.Enum):
    TRIAL = "TRIAL"
    ACTIVE = "ACTIVE"
    PAST_DUE = "PAST_DUE"
    CANCELLED = "CANCELLED"
    EXPIRED = "EXPIRED"


# Plan definitions with limits
PLAN_CONFIG = {
    PlanTier.FREE_TRIAL: {
        "price_inr": 0,
        "trial_days": 14,
        "max_conversations": 50,
        "max_campaigns": 1,
        "platforms": ["GOOGLE"],
        "features": ["whatsapp_receptionist", "calendar_booking", "reminders", "1_landing_page"],
    },
    PlanTier.STARTER: {
        "price_inr": 9999,
        "trial_days": 0,
        "max_conversations": 1000,
        "max_campaigns": 3,
        "platforms": ["GOOGLE"],
        "features": [
            "whatsapp_receptionist", "phone_receptionist", "calendar_booking",
            "reminders", "5_landing_pages", "call_recovery", "gmb_management",
            "conversion_dashboard",
        ],
    },
    PlanTier.GROWTH: {
        "price_inr": 24999,
        "trial_days": 0,
        "max_conversations": -1,  # Unlimited
        "max_campaigns": 15,
        "platforms": ["GOOGLE", "META", "CHATGPT", "LINKEDIN"],
        "features": [
            "whatsapp_receptionist", "phone_receptionist", "calendar_booking",
            "reminders", "unlimited_landing_pages", "call_recovery",
            "conversion_tracking", "ga4_analytics", "gmb_review_automation",
            "ml_bid_optimization", "noshow_prediction", "competitive_intel",
            "daily_summary", "doctor_notifications",
        ],
    },
    PlanTier.ENTERPRISE: {
        "price_inr": 49999,
        "trial_days": 0,
        "max_conversations": -1,
        "max_campaigns": -1,
        "max_locations": 10,
        "platforms": ["GOOGLE", "META", "CHATGPT", "LINKEDIN", "INSTAGRAM", "GMB"],
        "features": [
            "whatsapp_receptionist", "phone_receptionist", "calendar_booking",
            "reminders", "unlimited_landing_pages", "call_recovery",
            "conversion_tracking", "ga4_analytics", "gmb_review_automation",
            "ml_bid_optimization", "noshow_prediction", "competitive_intel",
            "daily_summary", "doctor_notifications",
            "multi_location", "multi_doctor", "custom_ai_training",
            "api_access", "ehr_integration", "dedicated_manager",
            "priority_support", "revenue_attribution", "whitelabel_reports",
            "dpdp_audit_logs", "quarterly_strategy_review",
        ],
    },
}


class Subscription(Base):
    """Doctor's subscription to a PatientPlex AI plan."""

    __tablename__ = "subscriptions"

    id: Mapped[uuid.UUID] = mapped_column(UUID(), primary_key=True, default=uuid.uuid4)
    doctor_id: Mapped[uuid.UUID] = mapped_column(UUID(), ForeignKey("doctors.id"), unique=True, index=True)

    # Plan
    plan: Mapped[PlanTier] = mapped_column(Enum(PlanTier, name="plan_tier_enum"), default=PlanTier.FREE_TRIAL)
    status: Mapped[SubscriptionStatus] = mapped_column(
        Enum(SubscriptionStatus, name="subscription_status_enum"), default=SubscriptionStatus.TRIAL
    )

    # Razorpay
    razorpay_subscription_id: Mapped[str | None] = mapped_column(String(255), nullable=True)
    razorpay_customer_id: Mapped[str | None] = mapped_column(String(255), nullable=True)
    razorpay_plan_id: Mapped[str | None] = mapped_column(String(255), nullable=True)

    # Billing
    price_inr: Mapped[int] = mapped_column(Integer, default=0)
    billing_cycle: Mapped[str] = mapped_column(String(20), default="monthly")

    # Trial
    trial_started_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)
    trial_ends_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)

    # Usage tracking
    conversations_this_month: Mapped[int] = mapped_column(Integer, default=0)
    campaigns_count: Mapped[int] = mapped_column(Integer, default=0)
    usage_reset_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)

    # Dates
    current_period_start: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)
    current_period_end: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)
    cancelled_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)

    # Relationships
    doctor = relationship("Doctor", back_populates="subscriptions")
    invoices = relationship("Invoice", back_populates="subscription", lazy="selectin")

    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=lambda: datetime.now(timezone.utc))
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        default=lambda: datetime.now(timezone.utc),
        onupdate=lambda: datetime.now(timezone.utc),
    )


class Invoice(Base):
    """Payment invoice/receipt."""

    __tablename__ = "invoices"

    id: Mapped[uuid.UUID] = mapped_column(UUID(), primary_key=True, default=uuid.uuid4)
    doctor_id: Mapped[uuid.UUID] = mapped_column(UUID(), ForeignKey("doctors.id"), index=True)
    subscription_id: Mapped[uuid.UUID] = mapped_column(UUID(), ForeignKey("subscriptions.id"))

    razorpay_payment_id: Mapped[str | None] = mapped_column(String(255), nullable=True)
    razorpay_invoice_id: Mapped[str | None] = mapped_column(String(255), nullable=True)

    amount_inr: Mapped[int] = mapped_column(Integer)
    status: Mapped[str] = mapped_column(String(20), default="paid")  # paid, failed, refunded
    plan: Mapped[str] = mapped_column(String(50))
    period_start: Mapped[datetime] = mapped_column(DateTime(timezone=True))
    period_end: Mapped[datetime] = mapped_column(DateTime(timezone=True))

    # Relationships
    subscription = relationship("Subscription", back_populates="invoices")

    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=lambda: datetime.now(timezone.utc))
