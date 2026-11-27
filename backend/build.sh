#!/usr/bin/env bash
# Render build script
set -o errexit

pip install -r requirements.txt

# Run database migrations — add new columns to existing tables
# This runs BEFORE the app starts so all columns exist when SQLAlchemy queries them
python - <<'PYTHON'
import os, sys
db_url = os.environ.get('DATABASE_URL', '')
if not db_url:
    sys.exit('DATABASE_URL is required for deployment migrations')

# Convert asyncpg URL to psycopg2 for sync operations
sync_url = db_url.replace('postgresql+asyncpg://', 'postgresql://').replace('asyncpg://', 'postgresql://')

import psycopg2
conn = psycopg2.connect(sync_url)
conn.autocommit = True
cur = conn.cursor()

# Add new columns to doctors table
columns = [
    ('google_ads_customer_id', 'VARCHAR(20)'),
    ('google_ads_refresh_token', 'TEXT'),
    ('google_ads_connected', 'BOOLEAN DEFAULT FALSE'),
    ('meta_ads_access_token', 'TEXT'),
    ('meta_ads_account_id', 'VARCHAR(100)'),
    ('meta_ads_page_id', 'VARCHAR(100)'),
    ('meta_ads_connected', 'BOOLEAN DEFAULT FALSE'),
    ('twilio_phone_number', 'VARCHAR(20)'),
    ('reset_token', 'VARCHAR(100)'),
    ('reset_token_expires', 'TIMESTAMPTZ'),
]

for col_name, col_type in columns:
    cur.execute(f'ALTER TABLE doctors ADD COLUMN IF NOT EXISTS {col_name} {col_type}')
    print(f'  ✓ doctors.{col_name} — OK')

# Add new enum values
for val in ('CHATGPT', 'INSTAGRAM', 'GMB', 'WHATSAPP'):
    cur.execute(f"ALTER TYPE ad_platform_enum ADD VALUE IF NOT EXISTS '{val}'")
    print(f'  ✓ enum {val} — OK')

# Migration 005: Add appointment tracking fields
for col_name, col_type in [
    ('source', "VARCHAR(50) DEFAULT 'Walk-in' NOT NULL"),
    ('revenue_amount', 'FLOAT'),
    ('treatment_done', 'VARCHAR(255)'),
    ('patient_email', 'VARCHAR(255)'),
]:
    cur.execute(f'ALTER TABLE appointments ADD COLUMN IF NOT EXISTS {col_name} {col_type}')
    print(f'  ✓ appointments.{col_name} — OK')

# Migration 006: Create staff_role_enum and clinic_staff table
cur.execute("""
    DO $$
    BEGIN
        CREATE TYPE staff_role_enum AS ENUM (
            'OWNER', 'DOCTOR', 'SPECIALIST', 'HYGIENIST', 'ASSISTANT'
        );
    EXCEPTION WHEN duplicate_object THEN NULL;
    END
    $$;
""")
print('  ✓ staff_role_enum — OK')

cur.execute("""
    CREATE TABLE IF NOT EXISTS clinic_staff (
        id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
        doctor_id UUID NOT NULL REFERENCES doctors(id),
        full_name VARCHAR(255) NOT NULL,
        title VARCHAR(100) DEFAULT 'Dr.',
        specialty VARCHAR(100) NOT NULL,
        role staff_role_enum DEFAULT 'DOCTOR',
        phone VARCHAR(20),
        email VARCHAR(255),
        photo_url TEXT,
        services JSONB,
        weekly_schedule JSONB,
        slot_duration_minutes INTEGER DEFAULT 30,
        max_patients_per_day INTEGER DEFAULT 20,
        google_calendar_id VARCHAR(255),
        google_calendar_connected BOOLEAN DEFAULT FALSE,
        is_active BOOLEAN DEFAULT TRUE,
        display_order INTEGER DEFAULT 0,
        calendar_color VARCHAR(7) DEFAULT '#10b981',
        created_at TIMESTAMPTZ DEFAULT NOW(),
        updated_at TIMESTAMPTZ DEFAULT NOW()
    );
""")
print('  ✓ clinic_staff table — OK')

# Add staff_id to appointments
cur.execute('ALTER TABLE appointments ADD COLUMN IF NOT EXISTS staff_id UUID REFERENCES clinic_staff(id)')
print('  ✓ appointments.staff_id — OK')

# Migration 007: Create patients table
cur.execute("""
    CREATE TABLE IF NOT EXISTS patients (
        id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
        doctor_id UUID NOT NULL REFERENCES doctors(id),
        name VARCHAR(255) NOT NULL,
        phone VARCHAR(20) NOT NULL,
        email VARCHAR(255),
        source VARCHAR(50) DEFAULT 'Walk-in',
        first_visit_date TIMESTAMPTZ,
        utm_campaign VARCHAR(255),
        utm_source VARCHAR(255),
        total_visits INTEGER DEFAULT 0,
        total_revenue FLOAT DEFAULT 0,
        total_no_shows INTEGER DEFAULT 0,
        last_visit_date TIMESTAMPTZ,
        treatments JSONB,
        notes TEXT,
        tags JSONB,
        created_at TIMESTAMPTZ DEFAULT NOW(),
        updated_at TIMESTAMPTZ DEFAULT NOW(),
        CONSTRAINT uq_patient_phone_clinic UNIQUE (doctor_id, phone)
    );
""")
print('  ✓ patients table — OK')

# Migration 008: Performance indexes
indexes = [
    ('ix_appointments_doctor_date', 'appointments', 'doctor_id, appointment_date'),
    ('ix_appointments_doctor_status', 'appointments', 'doctor_id, status'),
    ('ix_patients_doctor_phone', 'patients', 'doctor_id, phone'),
    ('ix_clinic_staff_doctor', 'clinic_staff', 'doctor_id, is_active'),
    ('ix_appointments_staff', 'appointments', 'staff_id'),
    ('ix_clinic_staff_doctor_id', 'clinic_staff', 'doctor_id'),
]
for idx_name, table, cols in indexes:
    cur.execute(f'CREATE INDEX IF NOT EXISTS {idx_name} ON {table} ({cols})')
    print(f'  ✓ index {idx_name} — OK')

# Set subdomain_slug for doctors that don't have one yet
# This enables the public booking page at /book/{slug}
cur.execute("""
    UPDATE doctors
    SET subdomain_slug = TRIM(BOTH '-' FROM LOWER(REPLACE(REPLACE(full_name, ' ', '-'), '.', '')))
    WHERE subdomain_slug IS NULL OR subdomain_slug = ''
""")
updated = cur.statusmessage
print(f'  ✓ Set subdomain slugs — {updated}')

# Fix trailing dashes in existing slugs
cur.execute("""
    UPDATE doctors
    SET subdomain_slug = TRIM(BOTH '-' FROM subdomain_slug)
    WHERE subdomain_slug LIKE '%-' OR subdomain_slug LIKE '-%'
""")
fixed = cur.statusmessage
print(f'  ✓ Fixed slug formatting — {fixed}')

cur.execute("""
    SELECT a.atttypid = 'staff_role_enum'::regtype
    FROM pg_attribute a
    WHERE a.attrelid = 'clinic_staff'::regclass
      AND a.attname = 'role' AND NOT a.attisdropped
""")
if cur.fetchone() != (True,):
    sys.exit('clinic_staff.role must use staff_role_enum')
print('  ✓ clinic_staff.role schema verified')

cur.close()
conn.close()
print('Database migrations complete!')
PYTHON
