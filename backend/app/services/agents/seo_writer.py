"""SEO Writer — Blog and SEO content generator."""
import logging
from datetime import datetime
from app.services.agents.base_agent import BaseAgent

logger = logging.getLogger(__name__)


class SEOWriter(BaseAgent):
    name = "seo_writer"
    display_name = "SEO Writer"
    schedule = "0 10 * * 1"  # Monday 10 AM
    description = "Writes SEO blog articles for clinic specialties with NMC-compliant language."

    async def run(self, specialty: str = "dental", topic: str = None) -> dict:
        self.log_start()
        try:
            if self.demo_mode:
                return self._demo_run(specialty)
            return {"status": "not_configured", "message": "Needs Claude API key for content generation"}
        except Exception as e:
            self.log_error(e)
            raise

    def _demo_run(self, specialty: str) -> dict:
        return {
            "agent": self.name,
            "run_at": datetime.now().isoformat(),
            "mode": "demo",
            "article": {
                "title": f"When Should You Visit a {specialty.title()} Specialist? A Patient's Guide",
                "word_count": "~1500 (would be generated)",
                "target_keywords": [f"{specialty} clinic near me", f"{specialty} cost", f"{specialty} treatment"],
                "nmc_check": "Would verify no banned terms (best, guaranteed, cheapest, etc.)",
            },
            "note": "Demo data — full article generation requires Claude API key.",
        }
