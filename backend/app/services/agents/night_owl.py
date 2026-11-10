"""Night Owl Agent — WhatsApp Conversation Monitor (8 PM – 8 AM)"""
import logging
from datetime import datetime, timedelta
from app.services.agents.base_agent import BaseAgent

logger = logging.getLogger(__name__)


class NightOwl(BaseAgent):
    """Monitors WhatsApp conversations after hours, flags urgent ones,
    and generates a morning digest at 7:30 AM."""

    name = "night_owl"
    display_name = "Night Owl"
    schedule = "0 20 * * *"  # 8 PM IST daily
    description = "WhatsApp monitor: flags unanswered messages, generates morning digest."

    async def run(self, clinic_id: str = None) -> dict:
        self.log_start()
        try:
            if self.demo_mode:
                return await self._demo_run(clinic_id)

            # Production: query WhatsApp Business API for unresponded messages
            conversations = await self._fetch_unresponded(clinic_id)
            flagged = [c for c in conversations if self._is_urgent(c)]
            digest = await self._generate_digest(conversations, flagged)
            self.log_complete(tasks=len(conversations))
            return digest
        except Exception as e:
            self.log_error(e)
            raise

    async def _fetch_unresponded(self, clinic_id=None):
        """Fetch unresponded WhatsApp messages from Meta Cloud API."""
        return []

    def _is_urgent(self, conversation: dict) -> bool:
        urgent_keywords = ["emergency", "pain", "urgent", "bleeding", "swelling",
                           "accident", "broken", "fever", "infection"]
        msg = conversation.get("message_text", "").lower()
        return any(kw in msg for kw in urgent_keywords)

    async def _generate_digest(self, conversations, flagged):
        return {"total": len(conversations), "flagged": len(flagged)}

    async def _demo_run(self, clinic_id=None) -> dict:
        now = datetime.now()
        return {
            "agent": self.name,
            "run_at": now.isoformat(),
            "period": "8 PM – 8 AM overnight",
            "clinics_monitored": 3,
            "summary": {
                "total_messages": 47,
                "unanswered": 12,
                "ai_auto_replied": 31,
                "flagged_urgent": 4,
                "avg_response_time": "18 seconds",
            },
            "clinics": [
                {
                    "name": "Smile Dental Clinic",
                    "city": "Hyderabad",
                    "messages": 18,
                    "unanswered": 3,
                    "ai_replied": 14,
                    "flagged": [
                        {
                            "patient": "Rahul M.",
                            "time": "11:42 PM",
                            "message": "My child fell and broke a tooth, is this an emergency?",
                            "urgency": "HIGH",
                            "ai_response": "I understand your concern. A broken tooth needs attention. Please visit our emergency hours tomorrow 8 AM, or call 108 if bleeding is severe.",
                            "status": "AI responded + flagged for morning follow-up",
                        }
                    ],
                },
                {
                    "name": "SkinGlow Dermatology",
                    "city": "Mumbai",
                    "messages": 15,
                    "unanswered": 5,
                    "ai_replied": 9,
                    "flagged": [
                        {
                            "patient": "Priya S.",
                            "time": "10:15 PM",
                            "message": "Severe allergic reaction after treatment today, face is swelling",
                            "urgency": "CRITICAL",
                            "ai_response": "This sounds serious. Please go to your nearest hospital emergency immediately. If breathing is difficult, call 108 right away.",
                            "status": "CRITICAL — SMS alert sent to Dr. Sharma",
                        }
                    ],
                },
                {
                    "name": "Nova Fertility Centre",
                    "city": "Delhi",
                    "messages": 14,
                    "unanswered": 4,
                    "ai_replied": 8,
                    "flagged": [
                        {
                            "patient": "Anita K.",
                            "time": "9:30 PM",
                            "message": "When is my next IVF appointment? I forgot the date",
                            "urgency": "LOW",
                            "ai_response": "Your next appointment is on Thursday, Nov 14 at 10:30 AM with Dr. Gupta. Would you like me to send a reminder?",
                            "status": "AI resolved — no follow-up needed",
                        },
                        {
                            "patient": "Meera R.",
                            "time": "1:15 AM",
                            "message": "I'm having cramping after the embryo transfer, is this normal?",
                            "urgency": "HIGH",
                            "ai_response": "Mild cramping is common after embryo transfer. However, if pain is severe or you notice bleeding, please call our emergency line. Dr. Gupta will review your case first thing in the morning.",
                            "status": "AI responded + flagged for morning follow-up",
                        },
                    ],
                },
            ],
            "morning_digest": {
                "generated_at": (now + timedelta(hours=11, minutes=30)).strftime("%Y-%m-%d 07:30 AM"),
                "action_items": [
                    "🔴 CRITICAL: SkinGlow — Priya S. allergic reaction, Dr. Sharma notified",
                    "🟡 HIGH: Smile Dental — Rahul M. child's broken tooth, schedule emergency visit",
                    "🟡 HIGH: Nova Fertility — Meera R. post-transfer cramping, Dr. Gupta to call",
                    "🟢 12 routine messages auto-handled by AI, no follow-up needed",
                ],
            },
        }
