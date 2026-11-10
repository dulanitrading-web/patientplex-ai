"""Onboarding Agent — New Clinic Setup Automation"""
import logging
from datetime import datetime
from app.services.agents.base_agent import BaseAgent
from app.core.knowledge_base import get_benchmark, get_city_tier, MARKETING_EXPERTISE

logger = logging.getLogger(__name__)


class OnboardingAgent(BaseAgent):
    name = "onboarding_agent"
    display_name = "Onboarding Agent"
    schedule = "on_demand"
    description = "4 campaign structures, 7 WhatsApp templates, calendar config for new clinic setup."

    async def run(self, clinic_name: str = "", specialty: str = "dental_general", city: str = "hyderabad") -> dict:
        self.log_start()
        if self.demo_mode:
            return await self._demo_run(clinic_name, specialty, city)
        self.log_complete(tasks=1)
        return {"message": "Production mode not yet connected"}

    async def _demo_run(self, clinic_name, specialty, city) -> dict:
        benchmark = get_benchmark(specialty)
        tier = get_city_tier(city)
        name = clinic_name or "New Clinic"
        campaigns = {
            "brand": {"name": f"{name} - Brand", "keywords": [f"{name.lower()}", f"{name.lower()} {city}"],
                      "daily_budget": 200, "bid_strategy": "manual_cpc_enhanced"},
            "core_treatments": {"name": f"{name} - Treatments", "keywords": benchmark["top_keywords"][:5],
                                "daily_budget": 500, "bid_strategy": "manual_cpc_enhanced"},
            "near_me": {"name": f"{name} - Near Me", "keywords": [f"{benchmark['name'].lower()} near me",
                        f"{benchmark['name'].lower()} near {city}"], "daily_budget": 300, "bid_strategy": "manual_cpc_enhanced"},
            "competitor": {"name": f"{name} - Competitor", "keywords": ["[competitor names]"],
                           "daily_budget": 200, "bid_strategy": "manual_cpc"},
        }
        whatsapp_templates = [
            {"name": "welcome", "text": f"Hi {{name}}! 👋 Welcome to {name}. How can we help you today?"},
            {"name": "appointment_confirm", "text": "Your appointment is confirmed for {{date}} at {{time}}. See you soon!"},
            {"name": "reminder_24h", "text": "Reminder: Your appointment at {name} is tomorrow at {{time}}. Reply YES to confirm."},
            {"name": "follow_up", "text": "Hi {{name}}, how was your visit? We'd love your feedback! Rate us: {{link}}"},
            {"name": "missed_call", "text": "We missed your call! Our next available slot is {{slot}}. Book now: {{link}}"},
            {"name": "treatment_info", "text": f"Thank you for your interest in {{treatment}}! Here's what you need to know: {{info}}"},
            {"name": "offer", "text": f"Special offer from {name}! {{offer_details}}. Valid till {{date}}. Book: {{link}}"},
        ]
        return {
            "agent": self.name, "generated_at": datetime.now().isoformat(),
            "setup": {
                "clinic": name, "specialty": benchmark["name"], "city": city.title(), "tier": tier["tier"],
                "campaigns": campaigns, "total_daily_budget": sum(c["daily_budget"] for c in campaigns.values()),
                "whatsapp_templates": whatsapp_templates,
                "calendar_config": {
                    "working_hours": "9:00 AM - 8:00 PM",
                    "slot_duration_minutes": 30,
                    "buffer_minutes": 15,
                    "max_daily_appointments": 20,
                    "peak_hours": benchmark["peak_search_hours"],
                },
                "checklist": [
                    "✅ Google Ads account created", "✅ 4 campaigns configured",
                    "✅ WhatsApp Business API connected", "✅ 7 auto-reply templates set",
                    "✅ Calendar & booking system configured", "✅ Dashboard access shared",
                    "⏳ Landing page review pending", "⏳ First optimization in 7 days",
                ],
            },
        }
