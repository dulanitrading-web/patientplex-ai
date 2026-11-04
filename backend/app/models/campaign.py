"""Campaign and Ad models for tracking ads across Google, Meta, and LinkedIn."""

import enum
import uuid
from datetime import datetime, timezone

from sqlalchemy import (
    Boolean, DateTime, Enum, Float, ForeignKey, Integer, JSON, String, Text,
)
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column

from app.db.base import Base


class AdPlatform(str, enum.Enum):
    GOOGLE = "GOOGLE"
    META = "META"
    LINKEDIN = "LINKEDIN"


class CampaignStatus(str, enum.Enum):
    DRAFT = "DRAFT"
    PENDING_REVIEW = "PENDING_REVIEW"
    ACTIVE = "ACTIVE"
    PAUSED = "PAUSED"
    COMPLETED = "COMPLETED"
    ERROR = "ERROR"


class Campaign(Base):
    """An advertising campaign on a specific platform."""

    __tablename__ = "campaigns"

    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    doctor_id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), ForeignKey("doctors.id"), index=True)

    # Platform info
    platform: Mapped[AdPlatform] = mapped_column(Enum(AdPlatform, name="ad_platform_enum"))
    platform_campaign_id: Mapped[str | None] = mapped_column(String(255), nullable=True)
    platform_ad_group_id: Mapped[str | None] = mapped_column(String(255), nullable=True)

    # Campaign details
    name: Mapped[str] = mapped_column(String(255))
    status: Mapped[CampaignStatus] = mapped_column(
        Enum(CampaignStatus, name="campaign_status_enum"), default=CampaignStatus.DRAFT
    )
    campaign_type: Mapped[str] = mapped_column(String(50), default="SEARCH")  # SEARCH, DISPLAY, LEAD_GEN, AWARENESS

    # Budget
    daily_budget: Mapped[int] = mapped_column(Integer, default=0)  # In smallest currency unit (paise for INR)
    total_budget: Mapped[int] = mapped_column(Integer, default=0)
    currency: Mapped[str] = mapped_column(String(3), default="INR")

    # Targeting
    target_location: Mapped[str | None] = mapped_column(String(255), nullable=True)
    target_radius_km: Mapped[int] = mapped_column(Integer, default=5)
    target_latitude: Mapped[float | None] = mapped_column(Float, nullable=True)
    target_longitude: Mapped[float | None] = mapped_column(Float, nullable=True)
    keywords: Mapped[list | None] = mapped_column(JSON, nullable=True)
    negative_keywords: Mapped[list | None] = mapped_column(JSON, nullable=True)
    target_audiences: Mapped[dict | None] = mapped_column(JSON, nullable=True)

    # Ad content
    headlines: Mapped[list | None] = mapped_column(JSON, nullable=True)
    descriptions: Mapped[list | None] = mapped_column(JSON, nullable=True)
    ad_copy: Mapped[dict | None] = mapped_column(JSON, nullable=True)  # Meta-specific: primary_text, headline, etc.
    landing_page_url: Mapped[str | None] = mapped_column(Text, nullable=True)

    # Performance (synced from platform)
    impressions: Mapped[int] = mapped_column(Integer, default=0)
    clicks: Mapped[int] = mapped_column(Integer, default=0)
    conversions: Mapped[int] = mapped_column(Integer, default=0)
    spend: Mapped[int] = mapped_column(Integer, default=0)  # In smallest currency unit
    cpc: Mapped[float] = mapped_column(Float, default=0.0)
    ctr: Mapped[float] = mapped_column(Float, default=0.0)
    cost_per_conversion: Mapped[float] = mapped_column(Float, default=0.0)

    # Metadata
    last_synced_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)
    platform_response: Mapped[dict | None] = mapped_column(JSON, nullable=True)  # Raw API response
    error_message: Mapped[str | None] = mapped_column(Text, nullable=True)

    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=lambda: datetime.now(timezone.utc))
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        default=lambda: datetime.now(timezone.utc),
        onupdate=lambda: datetime.now(timezone.utc),
    )
