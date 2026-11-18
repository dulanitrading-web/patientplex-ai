"""Add composite indexes for performance-critical queries.

Revision ID: 008_add_performance_indexes
Revises: 007_add_patients_table
"""

from alembic import op

revision = "008_add_performance_indexes"
down_revision = "007_add_patients_table"
branch_labels = None
depends_on = None


def upgrade() -> None:
    # Appointments: queried by doctor + date on every dashboard/calendar load
    op.create_index("ix_appointments_doctor_date", "appointments", ["doctor_id", "appointment_date"])
    # Appointments: queried by doctor + status for filtering
    op.create_index("ix_appointments_doctor_status", "appointments", ["doctor_id", "status"])
    # Patients: queried by doctor + phone for dedup
    op.create_index("ix_patients_doctor_phone", "patients", ["doctor_id", "phone"])
    # Clinic staff: queried by doctor for listing
    op.create_index("ix_clinic_staff_doctor", "clinic_staff", ["doctor_id", "is_active"])


def downgrade() -> None:
    op.drop_index("ix_clinic_staff_doctor")
    op.drop_index("ix_patients_doctor_phone")
    op.drop_index("ix_appointments_doctor_status")
    op.drop_index("ix_appointments_doctor_date")
