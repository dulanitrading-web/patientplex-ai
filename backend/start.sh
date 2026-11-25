#!/bin/bash
set -e

echo "=== PatientPlex AI Backend Starting ==="

# Run database migrations before starting
echo "Running database migrations..."
cd /app
python -m alembic upgrade head || echo "WARNING: Migration failed — continuing with existing schema"

echo "Starting Uvicorn server..."
exec uvicorn app.main:app --host 0.0.0.0 --port "${PORT:-8000}" --workers "${WEB_CONCURRENCY:-4}"
