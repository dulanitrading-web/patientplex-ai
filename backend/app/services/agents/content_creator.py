"""Content Creator — Weekly marketing content generator."""
import logging
from datetime import datetime
from app.services.agents.base_agent import BaseAgent

logger = logging.getLogger(__name__)


class ContentCreator(BaseAgent):
    name = "content_creator"
    display_name = "Content Creator"
    schedule = "0 9 * * 1"  # Monday 9 AM
    description = "Generates weekly content: LinkedIn post, newsletter section, GMB post, WhatsApp broadcast."

    async def run(self, specialty: str = "dental") -> dict:
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
            "content_pieces": {
                "linkedin_post": "Draft: How one dental clinic reduced missed appointments by 40% using WhatsApp reminders [would be generated]",
                "gmb_post": "Draft: Now accepting same-day appointments. Message us on WhatsApp! [would be generated]",
                "whatsapp_broadcast": "Draft: Quick health tip for your patients [would be generated]",
            },
            "note": "Demo data — real content requires Claude API key and clinic context.",
        }
