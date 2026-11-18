"""Add patients table for patient CRM.

Revision ID: 007_add_patients_table
Revises: 006_add_clinic_staff_table
"""

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects.postgresql import UUID

revision = "007_add_patients_table"
down_revision = "006_add_clinic_staff_table"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.create_table(
        "patients",
        sa.Column("id", UUID(as_uuid=True), primary_key=True),
        sa.Column("doctor_id", UUID(as_uuid=True), sa.ForeignKey("doctors.id"), nullable=False, index=True),
        sa.Column("name", sa.String(255), nullable=False),
        sa.Column("phone", sa.String(20), nullable=False, index=True),
        sa.Column("email", sa.String(255), nullable=True),
        sa.Column("source", sa.String(50), server_default="Walk-in"),
        sa.Column("first_visit_date", sa.DateTime(timezone=True), nullable=True),
        sa.Column("utm_campaign", sa.String(255), nullable=True),
        sa.Column("utm_source", sa.String(255), nullable=True),
        sa.Column("total_visits", sa.Integer(), server_default="0"),
        sa.Column("total_revenue", sa.Float(), server_default="0"),
        sa.Column("total_no_shows", sa.Integer(), server_default="0"),
        sa.Column("last_visit_date", sa.DateTime(timezone=True), nullable=True),
        sa.Column("treatments", sa.JSON(), nullable=True),
        sa.Column("notes", sa.Text(), nullable=True),
        sa.Column("tags", sa.JSON(), nullable=True),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.text("now()")),
        sa.Column("updated_at", sa.DateTime(timezone=True), server_default=sa.text("now()")),
    )
    # Unique constraint: one patient per phone per clinic
    op.create_unique_constraint("uq_patient_phone_clinic", "patients", ["doctor_id", "phone"])


def downgrade() -> None:
    op.drop_constraint("uq_patient_phone_clinic", "patients")
    op.drop_table("patients")
