"""Initial schema — doctors, conversations, appointments, campaigns.

Revision ID: 001_initial
Revises: None
Create Date: 2026-10-31
"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects.postgresql import UUID, JSON

revision: str = "001_initial"
down_revision: Union[str, None] = None
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # -- Enums --
    specialty_enum = sa.Enum(
        "DENTIST", "DERMATOLOGIST", "ORTHOPEDIC", "GENERAL_PHYSICIAN",
        "ENT", "OPHTHALMOLOGIST", "GYNECOLOGIST", "PEDIATRICIAN",
        "SURGEON", "OTHER",
        name="specialty_enum",
    )
    specialty_enum.create(op.get_bind(), checkfirst=True)

    conversation_status_enum = sa.Enum(
        "ACTIVE", "BOOKING_IN_PROGRESS", "BOOKED", "COMPLETED", "ABANDONED",
        name="conversation_status_enum",
    )
    conversation_status_enum.create(op.get_bind(), checkfirst=True)

    appointment_status_enum = sa.Enum(
        "CONFIRMED", "REMINDED", "ATTENDED", "NO_SHOW", "CANCELLED", "RESCHEDULED",
        name="appointment_status_enum",
    )
    appointment_status_enum.create(op.get_bind(), checkfirst=True)

    ad_platform_enum = sa.Enum("GOOGLE", "META", "LINKEDIN", name="ad_platform_enum")
    ad_platform_enum.create(op.get_bind(), checkfirst=True)

    campaign_status_enum = sa.Enum(
        "DRAFT", "PENDING_REVIEW", "ACTIVE", "PAUSED", "COMPLETED", "ERROR",
        name="campaign_status_enum",
    )
    campaign_status_enum.create(op.get_bind(), checkfirst=True)

    # -- Doctors --
    op.create_table(
        "doctors",
        sa.Column("id", UUID(as_uuid=True), primary_key=True),
        sa.Column("full_name", sa.String(255), nullable=False),
        sa.Column("email", sa.String(255), unique=True, nullable=False, index=True),
        sa.Column("phone", sa.String(20), nullable=False),
        sa.Column("password_hash", sa.Text, nullable=False),
        sa.Column("clinic_name", sa.String(255), nullable=True),
        sa.Column("specialty", specialty_enum, nullable=True),
        sa.Column("services", JSON, nullable=True),
        sa.Column("clinic_address", sa.Text, nullable=True),
        sa.Column("city", sa.String(100), nullable=True),
        sa.Column("state", sa.String(100), nullable=True),
        sa.Column("pincode", sa.String(10), nullable=True),
        sa.Column("latitude", sa.Float, nullable=True),
        sa.Column("longitude", sa.Float, nullable=True),
        sa.Column("geo_radius_km", sa.Integer, default=5),
        sa.Column("monthly_budget", sa.Integer, default=10000),
        sa.Column("currency", sa.String(3), default="INR"),
        sa.Column("google_calendar_connected", sa.Boolean, default=False),
        sa.Column("google_calendar_token", JSON, nullable=True),
        sa.Column("google_calendar_id", sa.String(255), nullable=True),
        sa.Column("whatsapp_number", sa.String(20), nullable=True),
        sa.Column("whatsapp_verified", sa.Boolean, default=False),
        sa.Column("subdomain_slug", sa.String(100), unique=True, nullable=True, index=True),
        sa.Column("is_active", sa.Boolean, default=True),
        sa.Column("onboarding_step", sa.Integer, default=1),
        sa.Column("onboarding_completed", sa.Boolean, default=False),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now()),
        sa.Column("updated_at", sa.DateTime(timezone=True), server_default=sa.func.now(), onupdate=sa.func.now()),
    )

    # -- Conversations --
    op.create_table(
        "conversations",
        sa.Column("id", UUID(as_uuid=True), primary_key=True),
        sa.Column("doctor_id", UUID(as_uuid=True), sa.ForeignKey("doctors.id"), index=True),
        sa.Column("patient_phone", sa.String(20), index=True),
        sa.Column("patient_name", sa.String(255), nullable=True),
        sa.Column("treatment_interest", sa.String(255), nullable=True),
        sa.Column("status", conversation_status_enum, default="ACTIVE"),
        sa.Column("messages", JSON, default=[]),
        sa.Column("appointment_id", sa.String(255), nullable=True),
        sa.Column("appointment_datetime", sa.DateTime(timezone=True), nullable=True),
        sa.Column("source", sa.String(50), default="whatsapp"),
        sa.Column("utm_campaign", sa.String(255), nullable=True),
        sa.Column("utm_source", sa.String(255), nullable=True),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now()),
        sa.Column("updated_at", sa.DateTime(timezone=True), server_default=sa.func.now(), onupdate=sa.func.now()),
    )

    # -- Appointments --
    op.create_table(
        "appointments",
        sa.Column("id", UUID(as_uuid=True), primary_key=True),
        sa.Column("doctor_id", UUID(as_uuid=True), sa.ForeignKey("doctors.id"), index=True),
        sa.Column("conversation_id", UUID(as_uuid=True), sa.ForeignKey("conversations.id"), nullable=True),
        sa.Column("patient_name", sa.String(255)),
        sa.Column("patient_phone", sa.String(20)),
        sa.Column("treatment", sa.String(255)),
        sa.Column("appointment_date", sa.Date, index=True),
        sa.Column("appointment_time", sa.Time),
        sa.Column("duration_minutes", sa.Integer, default=30),
        sa.Column("status", appointment_status_enum, default="CONFIRMED"),
        sa.Column("google_event_id", sa.String(255), nullable=True),
        sa.Column("reminder_24h_sent", sa.Boolean, default=False),
        sa.Column("reminder_2h_sent", sa.Boolean, default=False),
        sa.Column("confirmation_sent", sa.Boolean, default=False),
        sa.Column("notes", sa.Text, nullable=True),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now()),
        sa.Column("updated_at", sa.DateTime(timezone=True), server_default=sa.func.now(), onupdate=sa.func.now()),
    )

    # -- Campaigns --
    op.create_table(
        "campaigns",
        sa.Column("id", UUID(as_uuid=True), primary_key=True),
        sa.Column("doctor_id", UUID(as_uuid=True), sa.ForeignKey("doctors.id"), index=True),
        sa.Column("platform", ad_platform_enum),
        sa.Column("platform_campaign_id", sa.String(255), nullable=True),
        sa.Column("platform_ad_group_id", sa.String(255), nullable=True),
        sa.Column("name", sa.String(255)),
        sa.Column("status", campaign_status_enum, default="DRAFT"),
        sa.Column("campaign_type", sa.String(50), default="SEARCH"),
        sa.Column("daily_budget", sa.Integer, default=0),
        sa.Column("total_budget", sa.Integer, default=0),
        sa.Column("currency", sa.String(3), default="INR"),
        sa.Column("target_location", sa.String(255), nullable=True),
        sa.Column("target_radius_km", sa.Integer, default=5),
        sa.Column("target_latitude", sa.Float, nullable=True),
        sa.Column("target_longitude", sa.Float, nullable=True),
        sa.Column("keywords", JSON, nullable=True),
        sa.Column("negative_keywords", JSON, nullable=True),
        sa.Column("target_audiences", JSON, nullable=True),
        sa.Column("headlines", JSON, nullable=True),
        sa.Column("descriptions", JSON, nullable=True),
        sa.Column("ad_copy", JSON, nullable=True),
        sa.Column("landing_page_url", sa.Text, nullable=True),
        sa.Column("impressions", sa.Integer, default=0),
        sa.Column("clicks", sa.Integer, default=0),
        sa.Column("conversions", sa.Integer, default=0),
        sa.Column("spend", sa.Integer, default=0),
        sa.Column("cpc", sa.Float, default=0.0),
        sa.Column("ctr", sa.Float, default=0.0),
        sa.Column("cost_per_conversion", sa.Float, default=0.0),
        sa.Column("last_synced_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column("platform_response", JSON, nullable=True),
        sa.Column("error_message", sa.Text, nullable=True),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now()),
        sa.Column("updated_at", sa.DateTime(timezone=True), server_default=sa.func.now(), onupdate=sa.func.now()),
    )


def downgrade() -> None:
    op.drop_table("campaigns")
    op.drop_table("appointments")
    op.drop_table("conversations")
    op.drop_table("doctors")

    for enum_name in [
        "campaign_status_enum", "ad_platform_enum",
        "appointment_status_enum", "conversation_status_enum", "specialty_enum",
    ]:
        sa.Enum(name=enum_name).drop(op.get_bind(), checkfirst=True)
