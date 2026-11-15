#!/usr/bin/env bash
# Render build script
set -o errexit

pip install -r requirements.txt

# Run database migrations — add new columns to existing tables
# This runs BEFORE the app starts so all columns exist when SQLAlchemy queries them
python -c "
import os, sys
db_url = os.environ.get('DATABASE_URL', '')
if not db_url:
    print('No DATABASE_URL set, skipping migrations')
    sys.exit(0)

# Convert asyncpg URL to psycopg2 for sync operations
sync_url = db_url.replace('postgresql+asyncpg://', 'postgresql://').replace('asyncpg://', 'postgresql://')

import psycopg2
try:
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
    ]

    for col_name, col_type in columns:
        try:
            cur.execute(f'ALTER TABLE doctors ADD COLUMN IF NOT EXISTS {col_name} {col_type}')
            print(f'  ✓ doctors.{col_name} — OK')
        except Exception as e:
            print(f'  ⚠ doctors.{col_name} — {e}')

    # Add new enum values
    for val in ('CHATGPT', 'INSTAGRAM', 'GMB', 'WHATSAPP'):
        try:
            cur.execute(f\"ALTER TYPE ad_platform_enum ADD VALUE IF NOT EXISTS '{val}'\")
            print(f'  ✓ enum {val} — OK')
        except Exception as e:
            print(f'  ⚠ enum {val} — {e}')

    cur.close()
    conn.close()
    print('Database migrations complete!')
except Exception as e:
    print(f'Migration warning (non-fatal): {e}')
    # Don't fail the build — the app can still start
"
