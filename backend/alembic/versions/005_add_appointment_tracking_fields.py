"""Add source, revenue, treatment_done, patient_email to appointments.

Revision ID: 005_add_appointment_tracking_fields
Revises: 004_add_integration_columns
"""

from alembic import op
import sqlalchemy as sa

revision = "005_add_appointment_tracking_fields"
down_revision = "004_add_integration_columns"
branch_labels = None
depends_on = None


def upgrade() -> None:
    # Add new columns to appointments table
    op.add_column("appointments", sa.Column("source", sa.String(50), server_default="Walk-in", nullable=False))
    op.add_column("appointments", sa.Column("revenue_amount", sa.Float(), nullable=True))
    op.add_column("appointments", sa.Column("treatment_done", sa.String(255), nullable=True))
    op.add_column("appointments", sa.Column("patient_email", sa.String(255), nullable=True))


def downgrade() -> None:
    op.drop_column("appointments", "patient_email")
    op.drop_column("appointments", "treatment_done")
    op.drop_column("appointments", "revenue_amount")
    op.drop_column("appointments", "source")
