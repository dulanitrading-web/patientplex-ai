"""Add call_logs, conversion_events, subscriptions, invoices tables.

Revision ID: 002_add_missing
Revises: 001_initial
Create Date: 2026-11-08
"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects.postgresql import UUID, JSON

revision: str = "002_add_missing"
down_revision: Union[str, None] = "001_initial"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # -- Enums --
    call_direction_enum = sa.Enum(
        "INBOUND", "OUTBOUND", "MISSED",
        name="call_direction_enum",
    )
    call_direction_enum.create(op.get_bind(), checkfirst=True)

    call_status_enum = sa.Enum(
        "RINGING", "ANSWERED", "MISSED", "VOICEMAIL", "BUSY", "FAILED", "WHATSAPP_TRIGGERED",
        name="call_status_enum",
    )
    call_status_enum.create(op.get_bind(), checkfirst=True)

    conversion_stage_enum = sa.Enum(
        "AD_IMPRESSION", "AD_CLICK", "LANDING_PAGE_VIEW",
        "CALL_ATTEMPTED", "CALL_CONNECTED", "CALL_MISSED",
        "WHATSAPP_STARTED", "WHATSAPP_ENGAGED",
        "SLOT_CHECKED", "SLOT_OFFERED",
        "BOOKING_CONFIRMED", "CONFIRMATION_SENT",
        "REMINDER_24H", "REMINDER_2H",
        "PATIENT_ATTENDED", "PATIENT_NO_SHOW",
        "TREATMENT_ACCEPTED",
        name="conversion_stage_enum",
    )
    conversion_stage_enum.create(op.get_bind(), checkfirst=True)

    plan_tier_enum = sa.Enum(
        "FREE_TRIAL", "STARTER", "GROWTH", "ENTERPRISE",
        name="plan_tier_enum",
    )
    plan_tier_enum.create(op.get_bind(), checkfirst=True)

    subscription_status_enum = sa.Enum(
        "TRIAL", "ACTIVE", "PAST_DUE", "CANCELLED", "EXPIRED",
        name="subscription_status_enum",
    )
    subscription_status_enum.create(op.get_bind(), checkfirst=True)

    # -- call_logs --
    op.create_table(
        "call_logs",
        sa.Column("id", UUID(as_uuid=True), primary_key=True),
        sa.Column("doctor_id", UUID(as_uuid=True), sa.ForeignKey("doctors.id"), nullable=False),
        sa.Column("caller_phone", sa.String(20), nullable=False),
        sa.Column("clinic_phone", sa.String(20), nullable=False),
        sa.Column("direction", call_direction_enum, nullable=False),
        sa.Column("status", call_status_enum, nullable=False),
        sa.Column("started_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("answered_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column("ended_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column("duration_seconds", sa.Integer, default=0),
        sa.Column("recording_url", sa.Text, nullable=True),
        sa.Column("recording_duration", sa.Integer, default=0),
        sa.Column("platform_call_sid", sa.String(255), nullable=True),
        sa.Column("platform_provider", sa.String(20), default="twilio"),
        sa.Column("whatsapp_followup_sent", sa.Boolean, default=False),
        sa.Column("conversation_id", UUID(as_uuid=True), sa.ForeignKey("conversations.id"), nullable=True),
        sa.Column("appointment_id", UUID(as_uuid=True), sa.ForeignKey("appointments.id"), nullable=True),
        sa.Column("utm_source", sa.String(100), nullable=True),
        sa.Column("utm_campaign", sa.String(255), nullable=True),
        sa.Column("utm_medium", sa.String(100), nullable=True),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now()),
    )
    op.create_index("ix_call_logs_doctor_id", "call_logs", ["doctor_id"])
    op.create_index("ix_call_logs_caller_phone", "call_logs", ["caller_phone"])
    op.create_index("ix_call_logs_created_at", "call_logs", ["created_at"])

    # -- conversion_events --
    op.create_table(
        "conversion_events",
        sa.Column("id", UUID(as_uuid=True), primary_key=True),
        sa.Column("doctor_id", UUID(as_uuid=True), sa.ForeignKey("doctors.id"), nullable=False),
        sa.Column("patient_phone", sa.String(20), nullable=True),
        sa.Column("session_id", sa.String(255), nullable=True),
        sa.Column("stage", conversion_stage_enum, nullable=False),
        sa.Column("source_channel", sa.String(50), nullable=False),
        sa.Column("utm_source", sa.String(100), nullable=True),
        sa.Column("utm_campaign", sa.String(255), nullable=True),
        sa.Column("utm_medium", sa.String(100), nullable=True),
        sa.Column("utm_content", sa.String(255), nullable=True),
        sa.Column("campaign_id", UUID(as_uuid=True), sa.ForeignKey("campaigns.id"), nullable=True),
        sa.Column("conversation_id", UUID(as_uuid=True), sa.ForeignKey("conversations.id"), nullable=True),
        sa.Column("appointment_id", UUID(as_uuid=True), sa.ForeignKey("appointments.id"), nullable=True),
        sa.Column("call_log_id", UUID(as_uuid=True), sa.ForeignKey("call_logs.id"), nullable=True),
        sa.Column("treatment", sa.String(255), nullable=True),
        sa.Column("revenue_inr", sa.Float, nullable=True),
        sa.Column("extra_data", JSON, nullable=True),
        sa.Column("timestamp", sa.DateTime(timezone=True), server_default=sa.func.now()),
    )
    op.create_index("ix_conversion_events_doctor_id", "conversion_events", ["doctor_id"])
    op.create_index("ix_conversion_events_stage", "conversion_events", ["stage"])
    op.create_index("ix_conversion_events_patient_phone", "conversion_events", ["patient_phone"])
    op.create_index("ix_conversion_events_timestamp", "conversion_events", ["timestamp"])

    # -- subscriptions --
    op.create_table(
        "subscriptions",
        sa.Column("id", UUID(as_uuid=True), primary_key=True),
        sa.Column("doctor_id", UUID(as_uuid=True), sa.ForeignKey("doctors.id"), unique=True, nullable=False),
        sa.Column("plan", plan_tier_enum, default="FREE_TRIAL"),
        sa.Column("status", subscription_status_enum, default="TRIAL"),
        sa.Column("razorpay_subscription_id", sa.String(255), nullable=True),
        sa.Column("razorpay_customer_id", sa.String(255), nullable=True),
        sa.Column("razorpay_plan_id", sa.String(255), nullable=True),
        sa.Column("price_inr", sa.Integer, default=0),
        sa.Column("billing_cycle", sa.String(20), default="monthly"),
        sa.Column("trial_started_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column("trial_ends_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column("conversations_this_month", sa.Integer, default=0),
        sa.Column("campaigns_count", sa.Integer, default=0),
        sa.Column("usage_reset_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column("current_period_start", sa.DateTime(timezone=True), nullable=True),
        sa.Column("current_period_end", sa.DateTime(timezone=True), nullable=True),
        sa.Column("cancelled_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now()),
        sa.Column("updated_at", sa.DateTime(timezone=True), server_default=sa.func.now()),
    )
    op.create_index("ix_subscriptions_doctor_id", "subscriptions", ["doctor_id"])

    # -- invoices --
    op.create_table(
        "invoices",
        sa.Column("id", UUID(as_uuid=True), primary_key=True),
        sa.Column("doctor_id", UUID(as_uuid=True), sa.ForeignKey("doctors.id"), nullable=False),
        sa.Column("subscription_id", UUID(as_uuid=True), sa.ForeignKey("subscriptions.id"), nullable=False),
        sa.Column("razorpay_payment_id", sa.String(255), nullable=True),
        sa.Column("razorpay_invoice_id", sa.String(255), nullable=True),
        sa.Column("amount_inr", sa.Integer, nullable=False),
        sa.Column("status", sa.String(20), default="paid"),
        sa.Column("plan", sa.String(50), nullable=False),
        sa.Column("period_start", sa.DateTime(timezone=True), nullable=False),
        sa.Column("period_end", sa.DateTime(timezone=True), nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now()),
    )
    op.create_index("ix_invoices_doctor_id", "invoices", ["doctor_id"])
    op.create_index("ix_invoices_subscription_id", "invoices", ["subscription_id"])


def downgrade() -> None:
    op.drop_table("invoices")
    op.drop_table("subscriptions")
    op.drop_table("conversion_events")
    op.drop_table("call_logs")

    for enum_name in [
        "subscription_status_enum", "plan_tier_enum",
        "conversion_stage_enum", "call_status_enum", "call_direction_enum",
    ]:
        sa.Enum(name=enum_name).drop(op.get_bind(), checkfirst=True)
