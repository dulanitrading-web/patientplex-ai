"""Add clinic_staff table and staff_id to appointments.

Revision ID: 006_add_clinic_staff_table
Revises: 005_add_appointment_tracking_fields
"""

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects.postgresql import UUID

revision = "006_add_clinic_staff_table"
down_revision = "005_add_appointment_tracking_fields"
branch_labels = None
depends_on = None


def upgrade() -> None:
    # Create staff role enum
    staff_role_enum = sa.Enum("OWNER", "DOCTOR", "SPECIALIST", "HYGIENIST", "ASSISTANT", name="staff_role_enum")
    staff_role_enum.create(op.get_bind(), checkfirst=True)

    # Create clinic_staff table
    op.create_table(
        "clinic_staff",
        sa.Column("id", UUID(as_uuid=True), primary_key=True),
        sa.Column("doctor_id", UUID(as_uuid=True), sa.ForeignKey("doctors.id"), nullable=False, index=True),
        sa.Column("full_name", sa.String(255), nullable=False),
        sa.Column("title", sa.String(100), server_default="Dr."),
        sa.Column("specialty", sa.String(100), nullable=False),
        sa.Column("role", staff_role_enum, server_default="DOCTOR"),
        sa.Column("phone", sa.String(20), nullable=True),
        sa.Column("email", sa.String(255), nullable=True),
        sa.Column("photo_url", sa.Text(), nullable=True),
        sa.Column("services", sa.JSON(), nullable=True),
        sa.Column("weekly_schedule", sa.JSON(), nullable=True),
        sa.Column("slot_duration_minutes", sa.Integer(), server_default="30"),
        sa.Column("max_patients_per_day", sa.Integer(), server_default="20"),
        sa.Column("google_calendar_id", sa.String(255), nullable=True),
        sa.Column("google_calendar_connected", sa.Boolean(), server_default="false"),
        sa.Column("is_active", sa.Boolean(), server_default="true"),
        sa.Column("display_order", sa.Integer(), server_default="0"),
        sa.Column("calendar_color", sa.String(7), server_default="#10b981"),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.text("now()")),
        sa.Column("updated_at", sa.DateTime(timezone=True), server_default=sa.text("now()")),
    )

    # Add staff_id to appointments
    op.add_column("appointments", sa.Column("staff_id", UUID(as_uuid=True), sa.ForeignKey("clinic_staff.id"), nullable=True, index=True))


def downgrade() -> None:
    op.drop_column("appointments", "staff_id")
    op.drop_table("clinic_staff")
    sa.Enum(name="staff_role_enum").drop(op.get_bind(), checkfirst=True)
