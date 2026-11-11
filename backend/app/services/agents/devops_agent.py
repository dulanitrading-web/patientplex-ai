"""DevOps Agent — System health monitoring."""
import logging
from datetime import datetime
from app.services.agents.base_agent import BaseAgent

logger = logging.getLogger(__name__)


class DevOpsAgent(BaseAgent):
    name = "devops_agent"
    display_name = "DevOps Agent"
    schedule = "*/30 * * * *"  # Every 30 minutes
    description = "Monitors API health, error rates, database connections, deployment status."

    async def run(self) -> dict:
        self.log_start()
        try:
            if self.demo_mode:
                return self._demo_run()
            return {"status": "not_configured", "message": "Needs Sentry DSN and database connection"}
        except Exception as e:
            self.log_error(e)
            raise

    def _demo_run(self) -> dict:
        return {
            "agent": self.name,
            "run_at": datetime.now().isoformat(),
            "mode": "demo",
            "checks": {
                "api_health": "ok (Render free tier — sleeps after 15 min inactivity)",
                "database": "not_connected (no DATABASE_URL configured on Render)",
                "error_rate": "unknown (Sentry not configured)",
                "deployment": "Render free tier — last deploy status unknown",
            },
            "note": "Demo data — real monitoring requires Sentry, database, and paid hosting.",
        }
