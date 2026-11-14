"""PatientPlex AI FastAPI application entry point."""
import logging
from contextlib import asynccontextmanager
import os

from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from slowapi import Limiter, _rate_limit_exceeded_handler
from slowapi.errors import RateLimitExceeded
from slowapi.util import get_remote_address

from app.api.v1 import (
    analytics, auth, onboarding, whatsapp, appointments, campaigns, chatgpt_ads,
    landing_pages, intelligence, calls, conversions, bookings, billing,
    marketing_brain, ml, webhooks, payments, signals, ehr, compliance,
    knowledge, google_my_business, ga4,
)
from app.api.v1.agents_router import router as agents_router
from app.core.config import settings

logger = logging.getLogger(__name__)

# --- Rate Limiting ---
_testing = os.environ.get("TESTING", "").lower() == "true"
limiter = Limiter(
    key_func=get_remote_address,
    default_limits=["100/minute"],
    enabled=not _testing,
)

# --- Agent Scheduler ---
_scheduler = None


@asynccontextmanager
async def lifespan(app: FastAPI):
    global _scheduler
    # Startup
    if settings.SECRET_KEY == "change-this-to-a-random-secret-key-in-production":
        logger.warning("SECRET_KEY is set to the default value.")
    logger.info(f"{settings.PROJECT_NAME} API starting up")

    # Start agent scheduler
    try:
        from apscheduler.schedulers.asyncio import AsyncIOScheduler
        from app.services.agent_scheduler import setup_agent_scheduler

        _scheduler = AsyncIOScheduler()
        count = setup_agent_scheduler(_scheduler)
        _scheduler.start()
        logger.info(f"Agent scheduler started with {count} scheduled agents")
    except ImportError:
        logger.warning("APScheduler not installed — agent scheduling disabled")
    except Exception as e:
        logger.error(f"Failed to start agent scheduler: {e}")

    yield

    # Shutdown
    if _scheduler:
        _scheduler.shutdown(wait=False)
        logger.info("Agent scheduler stopped")
    logger.info(f"{settings.PROJECT_NAME} API shutting down")


app = FastAPI(
    title=settings.PROJECT_NAME,
    description=(
        "Healthcare Patient Acquisition SaaS — automates Google Ads, Meta Ads, "
        "LinkedIn Ads, ChatGPT Ads, Google My Business, WhatsApp AI receptionist, "
        "and smart appointment booking for healthcare clinics across India."
    ),
    version="0.1.0",
    lifespan=lifespan,
)

app.state.limiter = limiter
app.add_exception_handler(RateLimitExceeded, _rate_limit_exceeded_handler)

# --- CORS ---
app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:3000",
        "http://localhost:5173",
        "https://patientplex.ai",
        "https://www.patientplex.ai",
        "https://app.patientplex.ai",
        "https://patientplex-ai.vercel.app",
        "https://patientplex-mission-control.lovable.app",
    ],
    allow_credentials=True,
    allow_methods=["GET", "POST", "PUT", "DELETE", "OPTIONS"],
    allow_headers=["*"],
)

# --- Routers ---
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
app.include_router(signals.router, prefix=settings.API_V1_PREFIX)
app.include_router(google_my_business.router, prefix=settings.API_V1_PREFIX)
app.include_router(ga4.router, prefix=settings.API_V1_PREFIX)
app.include_router(ml.router, prefix=settings.API_V1_PREFIX)
app.include_router(analytics.router, prefix=settings.API_V1_PREFIX)
app.include_router(webhooks.router, prefix=settings.API_V1_PREFIX)
app.include_router(payments.router, prefix=settings.API_V1_PREFIX)
app.include_router(compliance.router, prefix=settings.API_V1_PREFIX)
app.include_router(knowledge.router, prefix=settings.API_V1_PREFIX)

# AI Agents — list, trigger, monitor
app.include_router(agents_router, prefix=settings.API_V1_PREFIX)

# EHR — enable when integration is wired:
# app.include_router(ehr.router, prefix=settings.API_V1_PREFIX)


@app.get("/", tags=["health"])
async def health_check() -> dict:
    """System health check."""
    jobs = 0
    if _scheduler and _scheduler.running:
        jobs = len(_scheduler.get_jobs())
    return {
        "status": "healthy",
        "service": settings.PROJECT_NAME,
        "agents_scheduled": jobs,
    }
