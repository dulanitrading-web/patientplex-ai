"""PatientPlex AI FastAPI application entry point."""

import logging
from contextlib import asynccontextmanager

from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from slowapi import Limiter, _rate_limit_exceeded_handler
from slowapi.errors import RateLimitExceeded
from slowapi.util import get_remote_address

from app.api.v1 import (
    analytics, auth, onboarding, whatsapp, appointments, campaigns, chatgpt_ads,
    landing_pages, intelligence, calls, conversions, bookings, billing,
    marketing_brain, ml, webhooks, payments, signals, ehr, compliance,
)
from app.core.config import settings

logger = logging.getLogger(__name__)

limiter = Limiter(key_func=get_remote_address, default_limits=["100/minute"])


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Application lifespan: runs startup and shutdown hooks."""
    if settings.SECRET_KEY == "change-this-to-a-random-secret-key-in-production":
        logger.warning(
            "⚠️  SECRET_KEY is set to the default value. "
            "Generate a secure key: python -c \"import secrets; print(secrets.token_hex(32))\""
        )
    logger.info("PatientPlex AI API started")
    yield
    logger.info("PatientPlex AI API shutting down")


app = FastAPI(
    title=settings.PROJECT_NAME,
    description=(
        "Healthcare Patient Acquisition SaaS — automates Google/Meta/LinkedIn ads "
        "for doctors and books appointments directly into their calendars."
    ),
    version="0.1.0",
    lifespan=lifespan,
)

app.state.limiter = limiter
app.add_exception_handler(RateLimitExceeded, _rate_limit_exceeded_handler)

# CORS — restrict origins in production, allow all in dev
ALLOWED_ORIGINS = [
    "http://localhost:3000",
    "https://patientplex.ai",
    "https://app.patientplex.ai",
    "https://www.patientplex.ai",
    "https://patientplex-ai.vercel.app",
]
app.add_middleware(
    CORSMiddleware,
    allow_origins=ALLOWED_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Routers
app.include_router(auth.router, prefix=settings.API_V1_PREFIX)
app.include_router(onboarding.router, prefix=settings.API_V1_PREFIX)
app.include_router(whatsapp.router, prefix=settings.API_V1_PREFIX)
app.include_router(appointments.router, prefix=settings.API_V1_PREFIX)
app.include_router(campaigns.router, prefix=settings.API_V1_PREFIX)
app.include_router(landing_pages.router, prefix=settings.API_V1_PREFIX)
app.include_router(intelligence.router, prefix=settings.API_V1_PREFIX)
app.include_router(calls.router, prefix=settings.API_V1_PREFIX)
app.include_router(conversions.router, prefix=settings.API_V1_PREFIX)
app.include_router(bookings.router, prefix=settings.API_V1_PREFIX)
app.include_router(billing.router, prefix=settings.API_V1_PREFIX)
app.include_router(chatgpt_ads.router, prefix=settings.API_V1_PREFIX)
app.include_router(marketing_brain.router, prefix=settings.API_V1_PREFIX)
app.include_router(ml.router, prefix=settings.API_V1_PREFIX)
app.include_router(analytics.router, prefix=settings.API_V1_PREFIX)
app.include_router(webhooks.router, prefix=settings.API_V1_PREFIX)
app.include_router(payments.router, prefix=settings.API_V1_PREFIX)
app.include_router(signals.router, prefix=settings.API_V1_PREFIX)
app.include_router(ehr.router, prefix=settings.API_V1_PREFIX)
app.include_router(compliance.router, prefix=settings.API_V1_PREFIX)


@app.get("/", tags=["health"])
async def health_check() -> dict:
    """Basic health-check endpoint."""
    return {"status": "healthy", "service": settings.PROJECT_NAME}
