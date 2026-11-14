"""PatientPlex AI — Agent Scheduler.

Runs AI agents on their cron schedules using APScheduler.
Import and call setup_agent_scheduler(scheduler) from workers.py or main.py lifespan.
"""
import logging
from apscheduler.triggers.cron import CronTrigger
from app.services.agents import AGENT_REGISTRY, get_agent

logger = logging.getLogger(__name__)

# IST timezone
TIMEZONE = "Asia/Kolkata"


async def _run_scheduled_agent(agent_name: str):
    """Execute a scheduled agent run."""
    logger.info(f"[Scheduler] Firing agent: {agent_name}")
    try:
        agent = get_agent(agent_name)
        result = await agent.execute(triggered_by="scheduler")
        mode = result.get("result", {}).get("mode", "unknown")
        logger.info(f"[Scheduler] {agent_name} completed (mode={mode})")
        return result
    except Exception as e:
        logger.error(f"[Scheduler] {agent_name} failed: {e}")


def setup_agent_scheduler(scheduler):
    """Register all agents with cron schedules on the given APScheduler instance.

    Call this during app startup. Agents with schedule="on_demand" are skipped.
    """
    registered = 0
    for name, cls in AGENT_REGISTRY.items():
        instance = cls()
        schedule = instance.schedule

        # Skip on-demand agents — they run via API only
        if not schedule or schedule == "on_demand" or schedule.startswith("on_"):
            logger.info(f"[Scheduler] {name}: on-demand only, skipping cron")
            continue

        try:
            parts = schedule.split()
            if len(parts) == 5:
                trigger = CronTrigger(
                    minute=parts[0],
                    hour=parts[1],
                    day=parts[2],
                    month=parts[3],
                    day_of_week=parts[4],
                    timezone=TIMEZONE,
                )
                scheduler.add_job(
                    _run_scheduled_agent,
                    trigger=trigger,
                    args=[name],
                    id=f"agent_{name}",
                    name=f"Agent: {instance.display_name}",
                    replace_existing=True,
                )
                registered += 1
                logger.info(
                    f"[Scheduler] {name} registered: {schedule} ({TIMEZONE})"
                )
            else:
                logger.warning(f"[Scheduler] {name}: invalid cron '{schedule}'")
        except Exception as e:
            logger.error(f"[Scheduler] Failed to register {name}: {e}")

    logger.info(f"[Scheduler] {registered} agents scheduled, {len(AGENT_REGISTRY) - registered} on-demand")
    return registered
