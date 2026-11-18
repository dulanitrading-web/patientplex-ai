"""Clinic staff model — multiple doctors/practitioners under one clinic account.

The Doctor model represents the clinic owner/admin account.
ClinicStaff represents individual practitioners who see patients.
A single-doctor clinic has one staff entry (the owner themselves).
A multi-doctor clinic has 2-10+ staff entries.

Each staff member has:
- Their own specialty and services
- Their own availability schedule
- Their own Google Calendar (optional)
- Appointments are assigned to a specific staff member
"""

import enum
import uuid
from datetime import datetime, timezone

from sqlalchemy import Boolean, DateTime, Enum, ForeignKey, Integer, JSON, String, Text
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.base import Base
from app.db.types import PortableUUID as UUID


class StaffRole(str, enum.Enum):
    OWNER = "OWNER"           # Clinic owner — has admin access
    DOCTOR = "DOCTOR"          # Practicing doctor
    SPECIALIST = "SPECIALIST"  # Visiting specialist
    HYGIENIST = "HYGIENIST"    # Dental hygienist, physiotherapist, etc.
    ASSISTANT = "ASSISTANT"    # Medical assistant


class ClinicStaff(Base):
    """A practitioner who sees patients at a clinic.

    The 'doctor_id' links to the Doctor (clinic account) they belong to.
    When a patient books an appointment, they're assigned to a specific staff member
    based on the treatment type → staff specialty/services mapping.
    """

    __tablename__ = "clinic_staff"

    id: Mapped[uuid.UUID] = mapped_column(UUID(), primary_key=True, default=uuid.uuid4)
    doctor_id: Mapped[uuid.UUID] = mapped_column(UUID(), ForeignKey("doctors.id"), index=True)

    # Profile
    full_name: Mapped[str] = mapped_column(String(255), nullable=False)
    title: Mapped[str] = mapped_column(String(100), default="Dr.")  # Dr., Dt., etc.
    specialty: Mapped[str] = mapped_column(String(100), nullable=False)  # e.g. "Orthodontist", "Endodontist"
    role: Mapped[StaffRole] = mapped_column(
        Enum(StaffRole, name="staff_role_enum"),
        default=StaffRole.DOCTOR,
    )
    phone: Mapped[str | None] = mapped_column(String(20), nullable=True)
    email: Mapped[str | None] = mapped_column(String(255), nullable=True)
    photo_url: Mapped[str | None] = mapped_column(Text, nullable=True)

    # What they treat — list of service names
    # e.g. ["Root Canal", "Dental Implants", "Wisdom Tooth Extraction"]
    services: Mapped[list | None] = mapped_column(JSON, nullable=True)

    # Availability — weekly schedule
    # Format: {"monday": {"start": "09:00", "end": "17:00"}, "tuesday": {...}, ...}
    # Empty/null day = not available that day
    weekly_schedule: Mapped[dict | None] = mapped_column(JSON, nullable=True, default=lambda: {
        "monday": {"start": "09:00", "end": "18:00"},
        "tuesday": {"start": "09:00", "end": "18:00"},
        "wednesday": {"start": "09:00", "end": "18:00"},
        "thursday": {"start": "09:00", "end": "18:00"},
        "friday": {"start": "09:00", "end": "18:00"},
        "saturday": {"start": "09:00", "end": "14:00"},
    })

    # Slot duration in minutes (may differ by staff)
    slot_duration_minutes: Mapped[int] = mapped_column(Integer, default=30)

    # Max patients per day (capacity limit)
    max_patients_per_day: Mapped[int] = mapped_column(Integer, default=20)

    # Google Calendar (each staff can have their own)
    google_calendar_id: Mapped[str | None] = mapped_column(String(255), nullable=True)
    google_calendar_connected: Mapped[bool] = mapped_column(Boolean, default=False)

    # Active / on leave
    is_active: Mapped[bool] = mapped_column(Boolean, default=True)

    # Display order in the calendar/list
    display_order: Mapped[int] = mapped_column(Integer, default=0)

    # Color for calendar display (hex)
    calendar_color: Mapped[str] = mapped_column(String(7), default="#10b981")

    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=lambda: datetime.now(timezone.utc))
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        default=lambda: datetime.now(timezone.utc),
        onupdate=lambda: datetime.now(timezone.utc),
    )

    # Relationships
    doctor = relationship("Doctor", backref="staff_members")
