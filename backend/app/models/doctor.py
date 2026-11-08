"""Doctor ORM model — the core entity representing a healthcare provider."""

import enum
import uuid
from datetime import datetime, timezone

from sqlalchemy import Boolean, DateTime, Enum, Float, Integer, JSON, String, Text
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.base import Base


class Specialty(str, enum.Enum):
    """Medical specialties supported by the platform."""

    DENTIST = "DENTIST"
    DERMATOLOGIST = "DERMATOLOGIST"
    ORTHOPEDIC = "ORTHOPEDIC"
    GENERAL_PHYSICIAN = "GENERAL_PHYSICIAN"
    ENT = "ENT"
    OPHTHALMOLOGIST = "OPHTHALMOLOGIST"
    GYNECOLOGIST = "GYNECOLOGIST"
    PEDIATRICIAN = "PEDIATRICIAN"
    SURGEON = "SURGEON"
    OTHER = "OTHER"


class Doctor(Base):
    """Represents a doctor/clinic registered on the PatientPlex AI platform.

    Tracks profile information, clinic details, geo-targeting preferences,
    advertising budget, integration tokens, and onboarding progress.
    """

    __tablename__ = "doctors"

    # Primary key
    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), primary_key=True, default=uuid.uuid4
    )

    # Profile
    full_name: Mapped[str] = mapped_column(String(255), nullable=False)
    email: Mapped[str] = mapped_column(String(255), unique=True, nullable=False, index=True)
    phone: Mapped[str] = mapped_column(String(20), nullable=False)
    password_hash: Mapped[str] = mapped_column(Text, nullable=False)

    # Clinic details
    clinic_name: Mapped[str | None] = mapped_column(String(255), nullable=True)
    specialty: Mapped[Specialty | None] = mapped_column(
        Enum(Specialty, name="specialty_enum"), nullable=True
    )
    services: Mapped[list | None] = mapped_column(JSON, nullable=True)

    # Address and geo-targeting
    clinic_address: Mapped[str | None] = mapped_column(Text, nullable=True)
    city: Mapped[str | None] = mapped_column(String(100), nullable=True)
    state: Mapped[str | None] = mapped_column(String(100), nullable=True)
    pincode: Mapped[str | None] = mapped_column(String(10), nullable=True)
    latitude: Mapped[float | None] = mapped_column(Float, nullable=True)
    longitude: Mapped[float | None] = mapped_column(Float, nullable=True)
    geo_radius_km: Mapped[int] = mapped_column(Integer, default=5)

    # Budget
    monthly_budget: Mapped[int] = mapped_column(Integer, default=10000)
    currency: Mapped[str] = mapped_column(String(3), default="INR")

    # Google Calendar integration
    google_calendar_connected: Mapped[bool] = mapped_column(Boolean, default=False)
    google_calendar_token: Mapped[dict | None] = mapped_column(JSON, nullable=True)
    google_calendar_id: Mapped[str | None] = mapped_column(String(255), nullable=True)

    # WhatsApp integration
    whatsapp_number: Mapped[str | None] = mapped_column(String(20), nullable=True)
    whatsapp_verified: Mapped[bool] = mapped_column(Boolean, default=False)

    # Public profile
    subdomain_slug: Mapped[str | None] = mapped_column(
        String(100), unique=True, nullable=True, index=True
    )

    # Account state
    is_active: Mapped[bool] = mapped_column(Boolean, default=True)
    onboarding_step: Mapped[int] = mapped_column(Integer, default=1)
    onboarding_completed: Mapped[bool] = mapped_column(Boolean, default=False)

    # Timestamps
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), default=lambda: datetime.now(timezone.utc)
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        default=lambda: datetime.now(timezone.utc),
        onupdate=lambda: datetime.now(timezone.utc),
    )

    # Relationships
    campaigns = relationship("Campaign", back_populates="doctor", lazy="selectin")
    conversations = relationship("Conversation", back_populates="doctor", lazy="selectin")
    subscriptions = relationship("Subscription", back_populates="doctor", lazy="selectin")

    def __repr__(self) -> str:
        return f"<Doctor {self.full_name} ({self.email})>"
