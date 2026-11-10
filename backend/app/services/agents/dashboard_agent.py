"""Dashboard Agent — Nightly Data Pre-computation"""
import logging
from datetime import datetime
from app.services.agents.base_agent import BaseAgent

logger = logging.getLogger(__name__)


class DashboardAgent(BaseAgent):
    name = "dashboard_agent"
    display_name = "Dashboard Agent"
    schedule = "0 1 * * *"  # 1 AM IST nightly
    description = "Nightly pre-compute per-clinic + aggregate + leaderboard dashboard data."

    async def run(self, **kwargs) -> dict:
        self.log_start()
        if self.demo_mode:
            return await self._demo_run()
        self.log_complete(tasks=3)
        return {"message": "Production mode not yet connected"}

    async def _demo_run(self) -> dict:
        return {
            "agent": self.name, "computed_at": datetime.now().isoformat(),
            "dashboard_data": {
                "aggregate": {
                    "total_clinics": 50, "active_campaigns": 47, "total_spend_mtd": 375000,
                    "total_leads_mtd": 1250, "total_bookings_mtd": 520, "avg_cpl": 300,
                    "avg_roas": 4.1, "mrr": 149700,
                },
                "leaderboard": [
                    {"rank": 1, "clinic": "Smile Dental", "city": "Hyderabad", "roas": 5.8, "bookings": 42, "health": 95},
                    {"rank": 2, "clinic": "ClearVision Eye", "city": "Bangalore", "roas": 5.2, "bookings": 38, "health": 91},
                    {"rank": 3, "clinic": "ENT Care Plus", "city": "Chennai", "roas": 4.9, "bookings": 35, "health": 88},
                ],
                "alerts_summary": {"critical": 2, "high": 5, "medium": 8, "low": 12},
                "cache_stats": {"entries_updated": 50, "aggregate_updated": True, "leaderboard_updated": True},
            },
        }
