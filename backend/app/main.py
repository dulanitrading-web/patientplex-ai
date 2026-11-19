"""PatientPlex AI FastAPI application entry point."""
import logging
from contextlib import asynccontextmanager
import os
import sqlalchemy as sa

from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from slowapi import Limiter, _rate_limit_exceeded_handler
from slowapi.errors import RateLimitExceeded
from slowapi.util import get_remote_address

from app.api.v1 import (
    analytics, auth, onboarding, whatsapp, appointments, campaigns, chatgpt_ads,
    landing_pages, intelligence, calls, conversions, bookings, billing,
    marketing_brain, ml, webhooks, payments, signals, ehr, compliance,
    knowledge, google_my_business, ga4, seo, integrations, clinic_staff, ai_chat, patients,
    notifications, public_booking,
)
from app.api.v1.agents_router import router as agents_router
from app.core.config import settings

logger = logging.getLogger(__name__)

# --- Rate Limiting ---
_testing = os.environ.get("TESTING", "").lower() == "true"


def _get_real_client_ip(request: Request) -> str:
    """Extract the real client IP from X-Forwarded-For (behind Render proxy)."""
    forwarded = request.headers.get("X-Forwarded-For", "")
    if forwarded:
        return forwarded.split(",")[0].strip()
    return get_remote_address(request)


limiter = Limiter(
    key_func=_get_real_client_ip,
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

    # Create database tables if they don't exist
    try:
        from app.db.session import engine
        from app.db.base import Base
        # Import all models so they register with Base
        from app.models.doctor import Doctor  # noqa: F401
        from app.models.conversation import Conversation, Appointment  # noqa: F401
        from app.models.campaign import Campaign  # noqa: F401
        from app.models.call_log import CallLog, ConversionEvent  # noqa: F401
        from app.models.billing import Subscription, Invoice  # noqa: F401
        from app.models.clinic_staff import ClinicStaff  # noqa: F401
        from app.models.patient import Patient  # noqa: F401

        async with engine.begin() as conn:
            await conn.run_sync(Base.metadata.create_all)
            # Safety net: ensure columns exist even if Alembic migration 004
            # hasn't been run yet.  The canonical source of truth is the
            # migration file; this block is a fallback for existing deployments.
            _safety_columns = [
                ("doctors", "clinic_logo", "TEXT"),
                ("doctors", "google_ads_customer_id", "VARCHAR(20)"),
                ("doctors", "google_ads_refresh_token", "TEXT"),
                ("doctors", "google_ads_connected", "BOOLEAN DEFAULT FALSE"),
                ("doctors", "meta_ads_access_token", "TEXT"),
                ("doctors", "meta_ads_account_id", "VARCHAR(100)"),
                ("doctors", "meta_ads_page_id", "VARCHAR(100)"),
                ("doctors", "meta_ads_connected", "BOOLEAN DEFAULT FALSE"),
                ("doctors", "twilio_phone_number", "VARCHAR(20)"),
                ("subscriptions", "razorpay_order_id", "VARCHAR(255)"),
                ("subscriptions", "razorpay_payment_id", "VARCHAR(255)"),
            ]
            for table, col, col_type in _safety_columns:
                try:
                    await conn.execute(
                        sa.text(f"ALTER TABLE {table} ADD COLUMN IF NOT EXISTS {col} {col_type}")
                    )
                except Exception:
                    pass

            # Enum expansion safety net
            for new_val in ("CHATGPT", "INSTAGRAM", "GMB", "WHATSAPP", "PHYSIOTHERAPIST"):
                try:
                    await conn.execute(
                        sa.text(f"ALTER TYPE ad_platform_enum ADD VALUE IF NOT EXISTS '{new_val}'")
                    )
                except Exception:
                    pass

        logger.info("Database tables verified/created")
    except Exception as e:
        logger.error(f"Failed to create database tables: {e}")

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
    ],
    allow_credentials=True,
    allow_methods=["GET", "POST", "PUT", "DELETE", "OPTIONS"],
    allow_headers=["Authorization", "Content-Type", "Accept", "Origin", "X-Requested-With"],
)


# --- Cache headers for read-only endpoints ---
@app.middleware("http")
async def add_cache_headers(request: Request, call_next):
    """Add Cache-Control headers on read-only GET endpoints to reduce DB load."""
    response = await call_next(request)
    if request.method == "GET" and "/api/v1/" in request.url.path:
        path = request.url.path
        # Cache campaign overview and stats for 5 minutes
        if any(p in path for p in ["/campaigns/overview", "/appointments/stats", "/patients/stats", "/ga4/", "/gmb/"]):
            response.headers["Cache-Control"] = "private, max-age=300"
        # Cache notifications for 1 minute
        elif "/notifications" in path:
            response.headers["Cache-Control"] = "private, max-age=60"
    return response


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
app.include_router(seo.router, prefix=settings.API_V1_PREFIX)
app.include_router(ml.router, prefix=settings.API_V1_PREFIX)
app.include_router(analytics.router, prefix=settings.API_V1_PREFIX)
app.include_router(webhooks.router, prefix=settings.API_V1_PREFIX)
app.include_router(payments.router, prefix=settings.API_V1_PREFIX)
app.include_router(compliance.router, prefix=settings.API_V1_PREFIX)
app.include_router(knowledge.router, prefix=settings.API_V1_PREFIX)
app.include_router(integrations.router, prefix=settings.API_V1_PREFIX)
app.include_router(clinic_staff.router, prefix=settings.API_V1_PREFIX)
app.include_router(ai_chat.router, prefix=settings.API_V1_PREFIX)
app.include_router(patients.router, prefix=settings.API_V1_PREFIX)
app.include_router(notifications.router, prefix=settings.API_V1_PREFIX)
app.include_router(public_booking.router, prefix=settings.API_V1_PREFIX)

# AI Agents — list, trigger, monitor
app.include_router(agents_router, prefix=settings.API_V1_PREFIX)

# EHR — enable when integration is wired:
# app.include_router(ehr.router, prefix=settings.API_V1_PREFIX)


@app.get("/", tags=["health"])
async def health_check() -> dict:
    """System health check — verifies DB connectivity."""
    jobs = 0
    if _scheduler and _scheduler.running:
        jobs = len(_scheduler.get_jobs())

    db_ok = False
    try:
        from app.db.session import async_session_factory
        async with async_session_factory() as session:
            await session.execute(sa.text("SELECT 1"))
            db_ok = True
    except Exception:
        pass

    return {
        "status": "healthy" if db_ok else "degraded",
        "service": settings.PROJECT_NAME,
        "database": "connected" if db_ok else "unreachable",
        "agents_scheduled": jobs,
    }


@app.get("/health", tags=["health"])
async def health_probe() -> dict:
    """Lightweight health probe for uptime monitors."""
    try:
        from app.db.session import async_session_factory
        async with async_session_factory() as session:
            await session.execute(sa.text("SELECT 1"))
        return {"ok": True}
    except Exception:
        from fastapi.responses import JSONResponse
        return JSONResponse(status_code=503, content={"ok": False, "error": "database unreachable"})


@app.post("/api/v1/cron/reminders", tags=["cron"])
async def trigger_reminders():
    """Trigger appointment reminders — call this from an external cron service.

    Sends WhatsApp reminders for appointments 24h and 2h away,
    and marks past appointments without attendance as no-shows.

    Set up a free cron job at cron-job.org to call this every 30 minutes:
    POST https://patientplex-ai-g7ce.onrender.com/api/v1/cron/reminders
    """
    from app.db.session import async_session_factory
    from app.services.reminder_service import ReminderService

    async with async_session_factory() as db:
        service = ReminderService()
        reminder_summary = await service.check_and_send_reminders(db)
        no_show_count = await service.mark_no_shows(db)
        await db.commit()

    return {
        "reminders": reminder_summary,
        "no_shows_marked": no_show_count,
    }


@app.get("/api/v1/cron/keep-alive", tags=["cron"])
async def keep_alive():
    """Keep-alive endpoint to prevent Render free tier from sleeping.

    Set up a free cron job to ping this every 10 minutes:
    GET https://patientplex-ai-g7ce.onrender.com/api/v1/cron/keep-alive
    """
    return {"alive": True}
