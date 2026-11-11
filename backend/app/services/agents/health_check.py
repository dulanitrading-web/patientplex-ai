"""Health Check — Churn early-warning system."""
import logging
from datetime import datetime
from app.services.agents.base_agent import BaseAgent

logger = logging.getLogger(__name__)


class HealthCheck(BaseAgent):
    name = "health_check"
    display_name = "Health Check"
    schedule = "0 7 * * *"  # 7 AM daily
    description = "Detects churn signals: declining bookings, low ROAS, missed payments, dashboard inactivity."

    CHURN_SIGNALS = [
        "bookings_declining",
        "roas_below_2x",
        "no_dashboard_login_7d",
        "payment_overdue",
        "whatsapp_resolution_below_70pct",
        "negative_reviews_increasing",
    ]

    async def run(self, clinic_id: str = None) -> dict:
        self.log_start()
        try:
            if self.demo_mode:
                return self._demo_run()
            return {"status": "not_configured", "message": "Needs database with clinic metrics"}
        except Exception as e:
            self.log_error(e)
            raise

    def _demo_run(self) -> dict:
        return {
            "agent": self.name,
            "run_at": datetime.now().isoformat(),
            "mode": "demo",
            "clinics_checked": 1,
            "alerts": [],
            "summary": "No churn signals detected (only 1 pilot clinic, still on trial).",
            "note": "Demo data — churn detection requires 30+ days of real performance data.",
        }
