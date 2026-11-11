"""Finance Bot — Revenue tracking and billing reconciliation."""
import logging
from datetime import datetime
from app.services.agents.base_agent import BaseAgent

logger = logging.getLogger(__name__)


class FinanceBot(BaseAgent):
    name = "finance_bot"
    display_name = "Finance Bot"
    schedule = "0 6 * * *"  # 6 AM daily
    description = "Tracks MRR, reconciles Razorpay payments, flags overdue invoices, generates SaaS metrics."

    async def run(self) -> dict:
        self.log_start()
        try:
            if self.demo_mode:
                return self._demo_run()
            return {"status": "not_configured", "message": "Needs Razorpay credentials and active subscriptions"}
        except Exception as e:
            self.log_error(e)
            raise

    def _demo_run(self) -> dict:
        return {
            "agent": self.name,
            "run_at": datetime.now().isoformat(),
            "mode": "demo",
            "metrics": {
                "mrr": 0,
                "paying_clinics": 0,
                "trial_clinics": 1,
                "overdue_invoices": 0,
                "note": "Pre-revenue stage — metrics will populate when clinics start paying",
            },
            "note": "Demo data — real metrics require Razorpay integration and paying customers.",
        }
