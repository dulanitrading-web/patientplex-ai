"""CSM Co-pilot — Client health scoring and retention assistant."""
import logging
from datetime import datetime
from app.services.agents.base_agent import BaseAgent

logger = logging.getLogger(__name__)


class CSMCopilot(BaseAgent):
    name = "csm_copilot"
    display_name = "CSM Co-pilot"
    schedule = "0 8 * * 1-5"  # 8 AM weekdays
    description = "Scores client health 0-100, classifies healthy/watch/at-risk, suggests retention actions."

    async def run(self, clinic_id: str = None) -> dict:
        self.log_start()
        try:
            if self.demo_mode:
                return self._demo_run()
            return {"status": "not_configured", "message": "Needs database with clinic performance data"}
        except Exception as e:
            self.log_error(e)
            raise

    def _demo_run(self) -> dict:
        return {
            "agent": self.name,
            "run_at": datetime.now().isoformat(),
            "mode": "demo",
            "clinics_scored": 1,
            "scores": [
                {
                    "clinic": "Pilot Clinic",
                    "health_score": 72,
                    "category": "watch",
                    "factors": {
                        "bookings_trend": "stable",
                        "ad_spend_roi": "not_measured_yet",
                        "response_rate": "high",
                        "payment_status": "trial",
                    },
                    "recommended_action": "Schedule a check-in call — clinic is on trial, conversion window closing",
                },
            ],
            "note": "Demo data — health scores require real clinic performance metrics.",
        }
