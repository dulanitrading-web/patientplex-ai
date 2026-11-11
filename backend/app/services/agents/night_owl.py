"""Night Owl — WhatsApp conversation monitor.

Checks for unresponded WhatsApp messages after clinic hours.
Generates a morning digest for each clinic's doctor.

This is one of the TWO agents that should run first. The other is Lead Hunter.
"""
import logging
from datetime import datetime
from app.services.agents.base_agent import BaseAgent

logger = logging.getLogger(__name__)


class NightOwl(BaseAgent):
    name = "night_owl"
    display_name = "Night Owl"
    schedule = "0 20 * * *"  # 8 PM IST daily
    description = "Monitors WhatsApp conversations after hours, flags urgent messages, generates morning digest."

    async def run(self, clinic_id: str = None) -> dict:
        self.log_start()
        try:
            if self.demo_mode:
                return self._demo_run()

            # Production: query real WhatsApp conversations from database
            # This requires: database connection, WhatsApp API credentials
            # TODO: wire to real app.services.whatsapp_ai service
            return {"status": "no_credentials", "message": "WhatsApp API not configured yet"}
        except Exception as e:
            self.log_error(e)
            raise

    def _demo_run(self) -> dict:
        """Return realistic sample data for demo/testing."""
        return {
            "agent": self.name,
            "run_at": datetime.now().isoformat(),
            "mode": "demo",
            "summary": {
                "clinics_monitored": 1,
                "total_conversations": 8,
                "unresponded": 2,
                "urgent": 1,
                "auto_replied": 5,
            },
            "clinics": [
                {
                    "name": "Pilot Clinic",
                    "conversations_after_hours": 8,
                    "ai_auto_replied": 5,
                    "needs_human_follow_up": 2,
                    "urgent_flags": [
                        {
                            "patient": "Patient A",
                            "message": "I have severe pain, can I come now?",
                            "time": "22:45",
                            "reason": "Pain/emergency keyword detected",
                        }
                    ],
                }
            ],
            "note": "Demo data — not connected to real WhatsApp API yet.",
        }
