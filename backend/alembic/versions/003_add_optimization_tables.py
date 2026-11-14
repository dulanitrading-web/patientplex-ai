"""Add optimization_runs and optimization_actions tables.

Revision ID: 003_add_optimization
Revises: 002_add_missing
Create Date: 2026-11-14
"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects.postgresql import UUID, JSON

revision: str = "003_add_optimization"
down_revision: Union[str, None] = "002_add_missing"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.create_table(
        "optimization_runs",
        sa.Column("id", UUID(as_uuid=True), primary_key=True),
        sa.Column("doctor_id", UUID(as_uuid=True), sa.ForeignKey("doctors.id"), nullable=False),
        sa.Column("run_type", sa.String(50), nullable=False),  # bid, budget, audience, creative
        sa.Column("status", sa.String(20), nullable=False, server_default="pending"),
        sa.Column("input_data", JSON, nullable=True),
        sa.Column("output_data", JSON, nullable=True),
        sa.Column("improvements", JSON, nullable=True),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now()),
        sa.Column("completed_at", sa.DateTime(timezone=True), nullable=True),
    )

    op.create_table(
        "optimization_actions",
        sa.Column("id", UUID(as_uuid=True), primary_key=True),
        sa.Column("run_id", UUID(as_uuid=True), sa.ForeignKey("optimization_runs.id"), nullable=False),
        sa.Column("doctor_id", UUID(as_uuid=True), sa.ForeignKey("doctors.id"), nullable=False),
        sa.Column("action_type", sa.String(50), nullable=False),
        sa.Column("entity_type", sa.String(50), nullable=False),  # campaign, ad_group, keyword
        sa.Column("entity_id", sa.String(200), nullable=True),
        sa.Column("old_value", sa.String(500), nullable=True),
        sa.Column("new_value", sa.String(500), nullable=True),
        sa.Column("status", sa.String(20), nullable=False, server_default="proposed"),
        sa.Column("applied_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now()),
    )

    op.create_index("ix_opt_runs_doctor", "optimization_runs", ["doctor_id"])
    op.create_index("ix_opt_actions_run", "optimization_actions", ["run_id"])


def downgrade() -> None:
    op.drop_index("ix_opt_actions_run", table_name="optimization_actions")
    op.drop_index("ix_opt_runs_doctor", table_name="optimization_runs")
    op.drop_table("optimization_actions")
    op.drop_table("optimization_runs")
