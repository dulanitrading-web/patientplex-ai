# PatientPlex AI Backend — Production Dockerfile
FROM python:3.12-slim

# Security: create non-root user
RUN groupadd -r pplex && useradd -r -g pplex -d /app pplex

WORKDIR /app

# Install system dependencies (asyncpg, cryptography)
RUN apt-get update && \
    apt-get install -y --no-install-recommends gcc libpq-dev curl && \
    rm -rf /var/lib/apt/lists/*

# Install Python dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir --upgrade pip && \
    pip install --no-cache-dir -r requirements.txt && \
    apt-get purge -y --auto-remove gcc

# Copy application code
COPY . .

# Own the app directory
RUN chown -R pplex:pplex /app

# Switch to non-root user
USER pplex

EXPOSE 8000

# Health check
HEALTHCHECK --interval=30s --timeout=10s --start-period=15s --retries=3 \
    CMD curl -f http://localhost:8000/ || exit 1

# Production: 4 workers with uvloop
CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000", "--workers", "4"]
