"""Optimization tracking models — records every auto-optimization decision."""

import enum
import uuid
from datetime import datetime, timezone

from sqlalchemy import (
    Boolean, DateTime, Enum, Float, ForeignKey, Integer, JSON, String, Text,
)
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.base import Base


class OptimizationActionType(str, enum.Enum):
    PAUSE_KEYWORD = "PAUSE_KEYWORD"
    ENABLE_KEYWORD = "ENABLE_KEYWORD"
    ADJUST_BID = "ADJUST_BID"
    ADD_NEGATIVE_KEYWORD = "ADD_NEGATIVE_KEYWORD"
    REALLOCATE_BUDGET = "REALLOCATE_BUDGET"
    ADJUST_GEO_RADIUS = "ADJUST_GEO_RADIUS"
    ADJUST_TIME_BID = "ADJUST_TIME_BID"
    ADJUST_DEVICE_BID = "ADJUST_DEVICE_BID"
    ROTATE_AD_COPY = "ROTATE_AD_COPY"
    PAUSE_CAMPAIGN = "PAUSE_CAMPAIGN"
    INCREASE_BUDGET = "INCREASE_BUDGET"
    DECREASE_BUDGET = "DECREASE_BUDGET"


class OptimizationRunStatus(str, enum.Enum):
    RUNNING = "RUNNING"
    COMPLETED = "COMPLETED"
    FAILED = "FAILED"
    PARTIAL = "PARTIAL"  # Some actions applied, some failed


class OptimizationRun(Base):
    """A single optimization cycle for a doctor's campaigns."""

    __tablename__ = "optimization_runs"

    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    doctor_id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), ForeignKey("doctors.id"), index=True)

    started_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=lambda: datetime.now(timezone.utc))
    completed_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)

    status: Mapped[OptimizationRunStatus] = mapped_column(
        Enum(OptimizationRunStatus, name="optimization_run_status_enum"),
        default=OptimizationRunStatus.RUNNING,
    )

    # Summary
    campaigns_analyzed: Mapped[int] = mapped_column(Integer, default=0)
    actions_taken: Mapped[int] = mapped_column(Integer, default=0)
    actions_skipped: Mapped[int] = mapped_column(Integer, default=0)

    # Snapshots for before/after comparison
    performance_before: Mapped[dict | None] = mapped_column(JSON, nullable=True)
    performance_after: Mapped[dict | None] = mapped_column(JSON, nullable=True)

    # AI-generated summary
    summary: Mapped[str | None] = mapped_column(Text, nullable=True)
    recommendations: Mapped[list | None] = mapped_column(JSON, nullable=True)

    error_message: Mapped[str | None] = mapped_column(Text, nullable=True)

    actions = relationship("OptimizationActionRecord", back_populates="run", lazy="selectin")


class OptimizationActionRecord(Base):
    """Individual action taken (or recommended) during an optimization run."""

    __tablename__ = "optimization_actions"

    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    run_id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), ForeignKey("optimization_runs.id"), index=True)
    campaign_id: Mapped[uuid.UUID | None] = mapped_column(UUID(as_uuid=True), ForeignKey("campaigns.id"), nullable=True)

    action_type: Mapped[OptimizationActionType] = mapped_column(
        Enum(OptimizationActionType, name="optimization_action_type_enum"),
    )

    description: Mapped[str] = mapped_column(Text)
    reason: Mapped[str] = mapped_column(Text)

    # What changed
    target: Mapped[str | None] = mapped_column(String(255), nullable=True)  # e.g. keyword text, ad group name
    old_value: Mapped[str | None] = mapped_column(String(255), nullable=True)
    new_value: Mapped[str | None] = mapped_column(String(255), nullable=True)

    # Confidence and impact
    confidence_score: Mapped[float] = mapped_column(Float, default=0.5)  # 0-1
    estimated_impact: Mapped[str | None] = mapped_column(String(100), nullable=True)  # e.g. "Save ₹200/day"

    # Execution
    applied: Mapped[bool] = mapped_column(Boolean, default=False)
    applied_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)
    result: Mapped[str | None] = mapped_column(Text, nullable=True)

    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=lambda: datetime.now(timezone.utc))

    run = relationship("OptimizationRun", back_populates="actions")
