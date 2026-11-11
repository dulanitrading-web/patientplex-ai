"""Reel Writer — Instagram Reel script generator."""
import logging
from datetime import datetime
from app.services.agents.base_agent import BaseAgent

logger = logging.getLogger(__name__)


class ReelWriter(BaseAgent):
    name = "reel_writer"
    display_name = "Reel Writer"
    schedule = "0 11 * * 3"  # Wednesday 11 AM
    description = "Generates Instagram Reel scripts: HOOK → PROBLEM → SOLUTION → CTA structure."

    async def run(self, specialty: str = "dental", topic: str = None) -> dict:
        self.log_start()
        try:
            if self.demo_mode:
                return self._demo_run(specialty)
            return {"status": "not_configured", "message": "Needs Claude API key for script generation"}
        except Exception as e:
            self.log_error(e)
            raise

    def _demo_run(self, specialty: str) -> dict:
        return {
            "agent": self.name,
            "run_at": datetime.now().isoformat(),
            "mode": "demo",
            "script": {
                "format": "30-second Reel",
                "hook": "Stop scrolling if you have tooth pain right now 🦷",
                "problem": "Most people wait until it gets unbearable — by then a simple filling becomes a root canal",
                "solution": "A 15-minute check-up can save you thousands. Book with your dentist today.",
                "cta": "DM us 'CHECK' to book a free consultation",
                "nmc_note": "No 'best doctor' / 'guaranteed' claims — NMC compliant",
            },
            "note": "Demo data — full script generation requires Claude API key.",
        }
