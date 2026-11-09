"""Background worker for scheduled tasks.

Runs appointment reminders, no-show marking, campaign performance syncing,
and auto-optimization on a schedule using APScheduler.

Usage:
    python -m app.workers
"""

import asyncio
import logging

from apscheduler.schedulers.asyncio import AsyncIOScheduler
from apscheduler.triggers.cron import CronTrigger
from apscheduler.triggers.interval import IntervalTrigger

from app.db.session import async_session_factory
from app.services.reminder_service import ReminderService

logging.basicConfig(level=logging.INFO, format="%(asctime)s [%(name)s] %(levelname)s: %(message)s")
logger = logging.getLogger("patientplex.workers")


async def run_reminders():
    """Check for upcoming appointments and send WhatsApp reminders."""
    logger.info("Running reminder check...")
    async with async_session_factory() as db:
        service = ReminderService()
        summary = await service.check_and_send_reminders(db)
        logger.info("Reminders sent: %s", summary)


async def run_no_show_check():
    """Mark past appointments without attendance as no-shows."""
    logger.info("Running no-show check...")
    async with async_session_factory() as db:
        service = ReminderService()
        count = await service.mark_no_shows(db)
        logger.info("Marked %d appointments as no-show", count)


async def run_campaign_sync():
    """Sync campaign performance metrics from ad platforms."""
    logger.info("Running campaign performance sync...")
    from sqlalchemy import select
    from app.models.campaign import Campaign, CampaignStatus
    from app.services.google_ads_engine import GoogleAdsEngine
    from app.services.meta_ads_engine import MetaAdsEngine

    async with async_session_factory() as db:
        result = await db.execute(
            select(Campaign).where(Campaign.status == CampaignStatus.ACTIVE)
        )
        campaigns = result.scalars().all()

        for campaign in campaigns:
            try:
                if campaign.platform.value == "GOOGLE":
                    engine = GoogleAdsEngine(db)
                    await engine.sync_performance(campaign)
                elif campaign.platform.value == "META":
                    engine = MetaAdsEngine(db)
                    await engine.sync_performance(campaign)
                logger.info("Synced campaign %s", campaign.name)
            except Exception as exc:
                logger.error("Failed to sync campaign %s: %s", campaign.name, exc)

        await db.commit()
    logger.info("Campaign sync complete — %d campaigns", len(campaigns))


async def run_optimization():
    """Run auto-optimization on all doctors' campaigns.

    The optimization engine analyzes performance and makes
    data-driven adjustments: bid changes, budget reallocation,
    keyword pausing, negative keyword additions.
    """
    logger.info("Running campaign optimization cycle...")
    from sqlalchemy import select
    from app.models.doctor import Doctor
    from app.services.optimization_engine import CampaignOptimizer

    async with async_session_factory() as db:
        result = await db.execute(
            select(Doctor.id).where(Doctor.is_active == True, Doctor.onboarding_completed == True)
        )
        doctor_ids = result.scalars().all()

        for doctor_id in doctor_ids:
            try:
                optimizer = CampaignOptimizer(db)
                report = await optimizer.run_optimization_cycle(doctor_id)
                logger.info("Optimization for doctor %s: %s", doctor_id, report.get("status"))
            except Exception as exc:
                logger.error("Optimization failed for doctor %s: %s", doctor_id, exc)

    logger.info("Optimization cycle complete — %d doctors processed", len(doctor_ids))


async def run_cache_warmup():
    """Pre-compute expensive analytics queries and cache them.

    Runs after campaign sync so dashboard data is fresh.
    """
    logger.info("Running cache warmup...")
    from sqlalchemy import select
    from app.models.doctor import Doctor
    from app.services.analytics_service import AnalyticsService
    from app.core.cache import RedisCache, CacheTTL

    async with async_session_factory() as db:
        result = await db.execute(
            select(Doctor.id).where(Doctor.is_active == True)
        )
        doctor_ids = result.scalars().all()

        analytics = AnalyticsService(db)
        for doctor_id in doctor_ids:
            try:
                doctor_str = str(doctor_id)
                # Pre-compute dashboard summary
                dashboard = await analytics.get_dashboard_summary(doctor_id)
                await RedisCache.set(doctor_str, "dashboard:30", dashboard, CacheTTL.DASHBOARD)

                # Pre-compute funnel
                funnel = await analytics.get_funnel_drop_off(doctor_id)
                await RedisCache.set(doctor_str, "funnel:30", funnel, CacheTTL.FUNNEL)

                logger.info("Cache warmed for doctor %s", doctor_id)
            except Exception as exc:
                logger.error("Cache warmup failed for doctor %s: %s", doctor_id, exc)

    logger.info("Cache warmup complete — %d doctors", len(doctor_ids))


def create_scheduler() -> AsyncIOScheduler:
    """Create and configure the APScheduler instance."""
    scheduler = AsyncIOScheduler()

    # ── Appointment management ──

    # Check for reminders every 15 minutes
    scheduler.add_job(
        run_reminders,
        trigger=IntervalTrigger(minutes=15),
        id="reminders",
        name="Appointment Reminders",
        replace_existing=True,
    )

    # Check for no-shows every hour
    scheduler.add_job(
        run_no_show_check,
        trigger=IntervalTrigger(hours=1),
        id="no_show_check",
        name="No-Show Check",
        replace_existing=True,
    )

    # ── Campaign management ──

    # Sync campaign performance every 4 hours
    scheduler.add_job(
        run_campaign_sync,
        trigger=IntervalTrigger(hours=4),
        id="campaign_sync",
        name="Campaign Performance Sync",
        replace_existing=True,
    )

    # Run optimization daily at 6 AM IST (00:30 UTC)
    scheduler.add_job(
        run_optimization,
        trigger=CronTrigger(hour=0, minute=30),
        id="daily_optimization",
        name="Daily Campaign Optimization",
        replace_existing=True,
    )

    # ── Analytics ──

    # Cache warmup every 4 hours (after campaign sync)
    scheduler.add_job(
        run_cache_warmup,
        trigger=IntervalTrigger(hours=4, start_date="2024-01-01 00:15:00"),  # 15 min after sync
        id="cache_warmup",
        name="Analytics Cache Warmup",
        replace_existing=True,
    )

    return scheduler


async def main():
    """Entry point for the background worker process."""
    logger.info("Starting PatientPlex AI background workers...")
    scheduler = create_scheduler()
    scheduler.start()

    logger.info("Workers running. Scheduled jobs:")
    for job in scheduler.get_jobs():
        logger.info("  - %s: %s", job.name, job.trigger)

    # Keep the process alive
    try:
        while True:
            await asyncio.sleep(3600)
    except (KeyboardInterrupt, SystemExit):
        logger.info("Shutting down workers...")
        scheduler.shutdown()


if __name__ == "__main__":
    asyncio.run(main())
