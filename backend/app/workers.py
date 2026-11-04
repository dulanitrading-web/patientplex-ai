"""Background worker for scheduled tasks.

Runs appointment reminders, no-show marking, and campaign performance syncing
on a schedule using APScheduler.

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
logger = logging.getLogger("cliniccare.workers")


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


def create_scheduler() -> AsyncIOScheduler:
    """Create and configure the APScheduler instance."""
    scheduler = AsyncIOScheduler()

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

    # Sync campaign performance every 4 hours
    scheduler.add_job(
        run_campaign_sync,
        trigger=IntervalTrigger(hours=4),
        id="campaign_sync",
        name="Campaign Performance Sync",
        replace_existing=True,
    )

    # Daily optimization check at 6 AM IST (00:30 UTC)
    scheduler.add_job(
        run_campaign_sync,
        trigger=CronTrigger(hour=0, minute=30),
        id="daily_optimization",
        name="Daily Campaign Optimization",
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
