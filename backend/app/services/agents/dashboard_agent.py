"""Dashboard Agent — Nightly dashboard data pre-computation."""
import logging
from datetime import datetime
from app.services.agents.base_agent import BaseAgent

logger = logging.getLogger(__name__)


class DashboardAgent(BaseAgent):
    name = "dashboard_agent"
    display_name = "Dashboard Agent"
    schedule = "0 1 * * *"  # 1 AM daily
    description = "Pre-computes per-clinic dashboards, aggregate metrics, and leaderboard data."

    async def run(self) -> dict:
        self.log_start()
        try:
            if self.demo_mode:
                return self._demo_run()
            return {"status": "not_configured", "message": "Needs database and Redis for cache"}
        except Exception as e:
            self.log_error(e)
            raise

    def _demo_run(self) -> dict:
        return {
            "agent": self.name,
            "run_at": datetime.now().isoformat(),
            "mode": "demo",
            "dashboards_computed": 0,
            "reason": "No active clinics with campaign data yet",
            "note": "Demo data — dashboard pre-compute requires active clinic campaigns.",
        }
