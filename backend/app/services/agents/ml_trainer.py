"""ML Trainer — Lead scoring model training."""
import logging
from datetime import datetime
from app.services.agents.base_agent import BaseAgent

logger = logging.getLogger(__name__)


class MLTrainer(BaseAgent):
    name = "ml_trainer"
    display_name = "ML Trainer"
    schedule = "0 2 * * 0"  # Sunday 2 AM
    description = "Trains lead scoring model when enough conversion data exists. Needs 100+ labelled leads."

    async def run(self) -> dict:
        self.log_start()
        try:
            if self.demo_mode:
                return self._demo_run()
            return {"status": "not_configured", "message": "Needs 100+ labelled leads before training is useful"}
        except Exception as e:
            self.log_error(e)
            raise

    def _demo_run(self) -> dict:
        return {
            "agent": self.name,
            "run_at": datetime.now().isoformat(),
            "mode": "demo",
            "status": "waiting_for_data",
            "data_needed": "100+ leads with known outcomes (booked / not booked)",
            "current_leads_with_outcomes": 0,
            "model": "Will use XGBoost when data is available",
            "note": "Demo data — ML training requires real conversion data from active clinics.",
        }
