"""Sales Prep — Pre-call research brief generator."""
import logging
from datetime import datetime
from app.services.agents.base_agent import BaseAgent

logger = logging.getLogger(__name__)


class SalesPrep(BaseAgent):
    name = "sales_prep"
    display_name = "Sales Prep"
    schedule = "on_demand"
    description = "Generates a research brief before sales calls: clinic overview, pain points, pitch angle."

    async def run(self, clinic_name: str = "", city: str = "hyderabad", specialty: str = "dental") -> dict:
        self.log_start()
        try:
            if self.demo_mode:
                return self._demo_run(clinic_name, city, specialty)
            return {"status": "not_configured", "message": "Needs SerpAPI key and Claude API to research clinics"}
        except Exception as e:
            self.log_error(e)
            raise

    def _demo_run(self, clinic_name: str, city: str, specialty: str) -> dict:
        name = clinic_name or "Sample Dental Clinic"
        return {
            "agent": self.name,
            "run_at": datetime.now().isoformat(),
            "mode": "demo",
            "brief": {
                "clinic": name,
                "city": city.title(),
                "specialty": specialty,
                "google_rating": 4.1,
                "review_count": 65,
                "pain_points": [
                    "Reviews mention long wait times",
                    "No online booking option visible",
                    "After-hours enquiries go unanswered",
                ],
                "pitch_angle": "WhatsApp AI answers patient enquiries 24/7, books appointments automatically",
                "opening_question": "How do you currently handle enquiries that come in after clinic hours?",
            },
            "note": "Demo data — not connected to real APIs yet.",
        }
