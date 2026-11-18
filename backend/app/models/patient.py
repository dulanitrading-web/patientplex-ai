"""Patient model — first-class entity tracking a patient across their lifecycle.

A patient is identified by phone number (unique per clinic).
Tracks: acquisition source, all appointments, treatments, revenue, lifetime value.
"""

import uuid
from datetime import datetime, timezone

from sqlalchemy import DateTime, Float, ForeignKey, Integer, JSON, String, Text
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.base import Base
from app.db.types import PortableUUID as UUID


class Patient(Base):
    """A patient at a clinic. Identified by phone number per clinic."""

    __tablename__ = "patients"

    id: Mapped[uuid.UUID] = mapped_column(UUID(), primary_key=True, default=uuid.uuid4)
    doctor_id: Mapped[uuid.UUID] = mapped_column(UUID(), ForeignKey("doctors.id"), index=True)

    # Identity
    name: Mapped[str] = mapped_column(String(255), nullable=False)
    phone: Mapped[str] = mapped_column(String(20), nullable=False, index=True)
    email: Mapped[str | None] = mapped_column(String(255), nullable=True)

    # Acquisition
    source: Mapped[str] = mapped_column(String(50), default="Walk-in")  # Google Ads, WhatsApp, Walk-in, Phone, Referral
    first_visit_date: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)
    utm_campaign: Mapped[str | None] = mapped_column(String(255), nullable=True)
    utm_source: Mapped[str | None] = mapped_column(String(255), nullable=True)

    # Aggregated metrics (updated after each appointment)
    total_visits: Mapped[int] = mapped_column(Integer, default=0)
    total_revenue: Mapped[float] = mapped_column(Float, default=0.0)
    total_no_shows: Mapped[int] = mapped_column(Integer, default=0)
    last_visit_date: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)

    # Treatment history (list of treatment names)
    treatments: Mapped[list | None] = mapped_column(JSON, nullable=True, default=list)

    # Notes
    notes: Mapped[str | None] = mapped_column(Text, nullable=True)

    # Tags for segmentation
    tags: Mapped[list | None] = mapped_column(JSON, nullable=True, default=list)

    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=lambda: datetime.now(timezone.utc))
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        default=lambda: datetime.now(timezone.utc),
        onupdate=lambda: datetime.now(timezone.utc),
    )
