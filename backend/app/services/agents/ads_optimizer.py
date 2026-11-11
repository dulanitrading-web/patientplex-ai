"""Ads Optimizer — Daily Google Ads campaign optimization."""
import logging
from datetime import datetime
from app.services.agents.base_agent import BaseAgent

logger = logging.getLogger(__name__)


class AdsOptimizer(BaseAgent):
    name = "ads_optimizer"
    display_name = "Ads Optimizer"
    schedule = "0 6 * * *"  # 6 AM daily
    description = "Daily optimization: pauses bleeding keywords, promotes winners, adjusts bids, checks quality scores."

    async def run(self, clinic_id: str = None) -> dict:
        self.log_start()
        try:
            if self.demo_mode:
                return self._demo_run()
            return {"status": "not_configured", "message": "Needs Google Ads API credentials"}
        except Exception as e:
            self.log_error(e)
            raise

    def _demo_run(self) -> dict:
        return {
            "agent": self.name,
            "run_at": datetime.now().isoformat(),
            "mode": "demo",
            "summary": {"clinics_checked": 1, "actions_taken": 3, "projected_weekly_savings": "TBD"},
            "actions": [
                {"type": "keyword_paused", "detail": "Paused 'dental college' — spent with zero conversions"},
                {"type": "negative_added", "detail": "Added 'course', 'admission', 'salary' as negatives"},
                {"type": "bid_adjusted", "detail": "Increased bid on 'dentist near me' by 10%"},
            ],
            "note": "Demo data — not connected to Google Ads API yet.",
        }
