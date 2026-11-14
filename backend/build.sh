#!/usr/bin/env bash
# Render build script — installs deps + runs DB migrations
set -o errexit

pip install -r requirements.txt

# Run database migrations
alembic upgrade head
