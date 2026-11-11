"""Onboarding Agent — New clinic setup automation."""
import logging
from datetime import datetime
from app.services.agents.base_agent import BaseAgent

logger = logging.getLogger(__name__)


class OnboardingAgent(BaseAgent):
    name = "onboarding_agent"
    display_name = "Onboarding Agent"
    schedule = "on_demand"
    description = "Sets up new clinics: campaign structure, WhatsApp templates, calendar config."

    async def run(self, clinic_name: str = "", specialty: str = "dental", city: str = "hyderabad") -> dict:
        self.log_start()
        try:
            if self.demo_mode:
                return self._demo_run(clinic_name, specialty, city)
            return {"status": "not_configured", "message": "Needs Google Ads + WhatsApp API credentials"}
        except Exception as e:
            self.log_error(e)
            raise

    def _demo_run(self, clinic_name: str, specialty: str, city: str) -> dict:
        name = clinic_name or "New Clinic"
        return {
            "agent": self.name,
            "run_at": datetime.now().isoformat(),
            "mode": "demo",
            "clinic": name,
            "steps_completed": [
                "Campaign structure created (brand + core treatments + near-me)",
                "WhatsApp auto-reply templates configured",
                "Booking calendar linked",
                "Negative keywords added from specialty list",
            ],
            "estimated_setup_time": "48 hours for full activation",
            "note": "Demo data — real onboarding requires API credentials and clinic details.",
        }
