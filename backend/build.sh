#!/usr/bin/env bash
# Render build script — installs deps + runs DB migrations
set -o errexit

pip install -r requirements.txt

# Convert async DATABASE_URL to sync for Alembic CLI
# postgresql+asyncpg:// → postgresql://
export ALEMBIC_DATABASE_URL="${DATABASE_URL//postgresql+asyncpg/postgresql}"

# Run database migrations with sync driver
alembic upgrade head
