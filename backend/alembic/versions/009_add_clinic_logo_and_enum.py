"""Add clinic_logo column and PHYSIOTHERAPIST enum value.

These were previously added via runtime ALTER TABLE in main.py startup.
This migration formalizes them in version-controlled schema.

Revision ID: 009
Revises: 008
"""

from alembic import op
import sqlalchemy as sa

revision = "009_add_clinic_logo_and_enum"
down_revision = "008_add_performance_indexes"
branch_labels = None
depends_on = None


def upgrade() -> None:
    # clinic_logo column on doctors
    op.add_column(
        "doctors",
        sa.Column("clinic_logo", sa.Text(), nullable=True),
    )

    # PHYSIOTHERAPIST was added at runtime but never in a migration
    op.execute(
        sa.text("ALTER TYPE specialty_enum ADD VALUE IF NOT EXISTS 'PHYSIOTHERAPIST'")
    )


def downgrade() -> None:
    op.drop_column("doctors", "clinic_logo")
    # Note: Cannot remove enum values in PostgreSQL without drop/recreate
