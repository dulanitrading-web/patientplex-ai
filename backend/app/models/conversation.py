"""Conversation and Appointment models for WhatsApp AI Receptionist."""

import enum
import uuid
from datetime import date, datetime, time, timezone

from sqlalchemy import (
    Boolean, Date, DateTime, Enum, ForeignKey, Integer, JSON, String, Text, Time,
)
from app.db.types import PortableUUID as UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.base import Base


class ConversationStatus(str, enum.Enum):
    ACTIVE = "ACTIVE"
    BOOKING_IN_PROGRESS = "BOOKING_IN_PROGRESS"
    BOOKED = "BOOKED"
    COMPLETED = "COMPLETED"
    ABANDONED = "ABANDONED"
    ESCALATED = "ESCALATED"


class AppointmentStatus(str, enum.Enum):
    CONFIRMED = "CONFIRMED"
    REMINDED = "REMINDED"
    ATTENDED = "ATTENDED"
    NO_SHOW = "NO_SHOW"
    CANCELLED = "CANCELLED"
    RESCHEDULED = "RESCHEDULED"


class Conversation(Base):
    """A WhatsApp conversation between a patient and a doctor's AI receptionist."""

    __tablename__ = "conversations"

    id: Mapped[uuid.UUID] = mapped_column(UUID(), primary_key=True, default=uuid.uuid4)
    doctor_id: Mapped[uuid.UUID] = mapped_column(UUID(), ForeignKey("doctors.id"), index=True)
    patient_phone: Mapped[str] = mapped_column(String(20), index=True)
    patient_name: Mapped[str | None] = mapped_column(String(255), nullable=True)
    treatment_interest: Mapped[str | None] = mapped_column(String(255), nullable=True)
    status: Mapped[ConversationStatus] = mapped_column(
        Enum(ConversationStatus, name="conversation_status_enum"),
        default=ConversationStatus.ACTIVE,
    )
    messages: Mapped[list] = mapped_column(JSON, default=list)
    appointment_id: Mapped[str | None] = mapped_column(String(255), nullable=True)
    appointment_datetime: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)
    source: Mapped[str] = mapped_column(String(50), default="whatsapp")
    utm_campaign: Mapped[str | None] = mapped_column(String(255), nullable=True)
    utm_source: Mapped[str | None] = mapped_column(String(255), nullable=True)

    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=lambda: datetime.now(timezone.utc))
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        default=lambda: datetime.now(timezone.utc),
        onupdate=lambda: datetime.now(timezone.utc),
    )

    doctor = relationship("Doctor", back_populates="conversations")
    appointments = relationship("Appointment", back_populates="conversation")


class Appointment(Base):
    """A booked appointment between a patient and a doctor."""

    __tablename__ = "appointments"

    id: Mapped[uuid.UUID] = mapped_column(UUID(), primary_key=True, default=uuid.uuid4)
    doctor_id: Mapped[uuid.UUID] = mapped_column(UUID(), ForeignKey("doctors.id"), index=True)
    conversation_id: Mapped[uuid.UUID] = mapped_column(UUID(), ForeignKey("conversations.id"), nullable=True)
    patient_name: Mapped[str] = mapped_column(String(255))
    patient_phone: Mapped[str] = mapped_column(String(20))
    treatment: Mapped[str] = mapped_column(String(255))
    appointment_date: Mapped[date] = mapped_column(Date, index=True)
    appointment_time: Mapped[time] = mapped_column(Time)
    duration_minutes: Mapped[int] = mapped_column(Integer, default=30)
    status: Mapped[AppointmentStatus] = mapped_column(
        Enum(AppointmentStatus, name="appointment_status_enum"),
        default=AppointmentStatus.CONFIRMED,
    )
    google_event_id: Mapped[str | None] = mapped_column(String(255), nullable=True)
    reminder_24h_sent: Mapped[bool] = mapped_column(Boolean, default=False)
    reminder_2h_sent: Mapped[bool] = mapped_column(Boolean, default=False)
    confirmation_sent: Mapped[bool] = mapped_column(Boolean, default=False)
    notes: Mapped[str | None] = mapped_column(Text, nullable=True)

    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=lambda: datetime.now(timezone.utc))
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        default=lambda: datetime.now(timezone.utc),
        onupdate=lambda: datetime.now(timezone.utc),
    )

    conversation = relationship("Conversation", back_populates="appointments")
