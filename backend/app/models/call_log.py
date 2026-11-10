"""Call log and conversion tracking models."""

import enum
import uuid
from datetime import datetime, timezone

from sqlalchemy import (
    Boolean, DateTime, Enum, Float, ForeignKey, Integer, JSON, String, Text,
)
from app.db.types import PortableUUID as UUID
from sqlalchemy.orm import Mapped, mapped_column

from app.db.base import Base


class CallDirection(str, enum.Enum):
    INBOUND = "INBOUND"
    OUTBOUND = "OUTBOUND"  # Auto-callback
    MISSED = "MISSED"


class CallStatus(str, enum.Enum):
    RINGING = "RINGING"
    ANSWERED = "ANSWERED"
    MISSED = "MISSED"
    VOICEMAIL = "VOICEMAIL"
    BUSY = "BUSY"
    FAILED = "FAILED"
    WHATSAPP_TRIGGERED = "WHATSAPP_TRIGGERED"  # Missed call → WhatsApp flow started


class ConversionStage(str, enum.Enum):
    """Full patient acquisition funnel stages."""
    AD_IMPRESSION = "AD_IMPRESSION"
    AD_CLICK = "AD_CLICK"
    LANDING_PAGE_VIEW = "LANDING_PAGE_VIEW"
    CALL_ATTEMPTED = "CALL_ATTEMPTED"
    CALL_CONNECTED = "CALL_CONNECTED"
    CALL_MISSED = "CALL_MISSED"
    WHATSAPP_STARTED = "WHATSAPP_STARTED"
    WHATSAPP_ENGAGED = "WHATSAPP_ENGAGED"  # Patient replied
    SLOT_CHECKED = "SLOT_CHECKED"
    SLOT_OFFERED = "SLOT_OFFERED"
    BOOKING_CONFIRMED = "BOOKING_CONFIRMED"
    CONFIRMATION_SENT = "CONFIRMATION_SENT"
    REMINDER_24H = "REMINDER_24H"
    REMINDER_2H = "REMINDER_2H"
    PATIENT_ATTENDED = "PATIENT_ATTENDED"
    PATIENT_NO_SHOW = "PATIENT_NO_SHOW"
    TREATMENT_ACCEPTED = "TREATMENT_ACCEPTED"


class CallLog(Base):
    """Log of every phone call — inbound, outbound, and missed."""

    __tablename__ = "call_logs"

    id: Mapped[uuid.UUID] = mapped_column(UUID(), primary_key=True, default=uuid.uuid4)
    doctor_id: Mapped[uuid.UUID] = mapped_column(UUID(), ForeignKey("doctors.id"), index=True)

    # Call details
    caller_phone: Mapped[str] = mapped_column(String(20), index=True)
    clinic_phone: Mapped[str] = mapped_column(String(20))
    direction: Mapped[CallDirection] = mapped_column(Enum(CallDirection, name="call_direction_enum"))
    status: Mapped[CallStatus] = mapped_column(Enum(CallStatus, name="call_status_enum"))

    # Timing
    started_at: Mapped[datetime] = mapped_column(DateTime(timezone=True))
    answered_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)
    ended_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)
    duration_seconds: Mapped[int] = mapped_column(Integer, default=0)

    # Recording
    recording_url: Mapped[str | None] = mapped_column(Text, nullable=True)
    recording_duration: Mapped[int] = mapped_column(Integer, default=0)

    # Platform IDs
    platform_call_sid: Mapped[str | None] = mapped_column(String(255), nullable=True)  # Twilio CallSid
    platform_provider: Mapped[str] = mapped_column(String(20), default="twilio")  # twilio or exotel

    # What happened after the call
    whatsapp_followup_sent: Mapped[bool] = mapped_column(Boolean, default=False)
    conversation_id: Mapped[uuid.UUID | None] = mapped_column(
        UUID(), ForeignKey("conversations.id"), nullable=True
    )
    appointment_id: Mapped[uuid.UUID | None] = mapped_column(
        UUID(), ForeignKey("appointments.id"), nullable=True
    )

    # Source tracking
    utm_source: Mapped[str | None] = mapped_column(String(100), nullable=True)
    utm_campaign: Mapped[str | None] = mapped_column(String(255), nullable=True)
    utm_medium: Mapped[str | None] = mapped_column(String(100), nullable=True)

    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=lambda: datetime.now(timezone.utc))


class ConversionEvent(Base):
    """Tracks every step of the patient acquisition funnel.

    One row per event — a patient may have many events across their journey.
    This powers the full-funnel analytics dashboard.
    """

    __tablename__ = "conversion_events"

    id: Mapped[uuid.UUID] = mapped_column(UUID(), primary_key=True, default=uuid.uuid4)
    doctor_id: Mapped[uuid.UUID] = mapped_column(UUID(), ForeignKey("doctors.id"), index=True)

    # Patient identifier (phone or session)
    patient_phone: Mapped[str | None] = mapped_column(String(20), index=True, nullable=True)
    session_id: Mapped[str | None] = mapped_column(String(255), nullable=True)  # For anonymous web visits

    # Funnel stage
    stage: Mapped[ConversionStage] = mapped_column(
        Enum(ConversionStage, name="conversion_stage_enum"), index=True
    )

    # Source attribution
    source_channel: Mapped[str] = mapped_column(String(50))  # google_ads, meta_ads, organic, direct, whatsapp, call
    utm_source: Mapped[str | None] = mapped_column(String(100), nullable=True)
    utm_campaign: Mapped[str | None] = mapped_column(String(255), nullable=True)
    utm_medium: Mapped[str | None] = mapped_column(String(100), nullable=True)
    utm_content: Mapped[str | None] = mapped_column(String(255), nullable=True)

    # Linked records
    campaign_id: Mapped[uuid.UUID | None] = mapped_column(UUID(), ForeignKey("campaigns.id"), nullable=True)
    conversation_id: Mapped[uuid.UUID | None] = mapped_column(UUID(), ForeignKey("conversations.id"), nullable=True)
    appointment_id: Mapped[uuid.UUID | None] = mapped_column(UUID(), ForeignKey("appointments.id"), nullable=True)
    call_log_id: Mapped[uuid.UUID | None] = mapped_column(UUID(), ForeignKey("call_logs.id"), nullable=True)

    # Value
    treatment: Mapped[str | None] = mapped_column(String(255), nullable=True)
    revenue_inr: Mapped[float | None] = mapped_column(Float, nullable=True)

    # Extra data
    extra_data: Mapped[dict | None] = mapped_column(JSON, nullable=True)
    timestamp: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), default=lambda: datetime.now(timezone.utc), index=True
    )
