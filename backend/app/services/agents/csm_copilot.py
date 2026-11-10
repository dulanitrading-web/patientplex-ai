"""CSM Co-Pilot Agent — Client Health Scoring & Retention Engine"""
import logging
from datetime import datetime
from app.services.agents.base_agent import BaseAgent
from app.core.knowledge_base import get_benchmark

logger = logging.getLogger(__name__)


class CSMCopilot(BaseAgent):
    name = "csm_copilot"
    display_name = "CSM Co-Pilot"
    schedule = "0 9 * * 1"  # Monday 9 AM IST
    description = "Health score 0-100, classify healthy/watch/at_risk, upsell/save scripts using Voss+Cialdini."

    WEIGHTS = {
        "bookings_trend": 25, "roas": 20, "whatsapp_resolution": 15,
        "dashboard_login": 15, "payment_status": 15, "nps": 10,
    }

    async def run(self, clinic_id: str = None) -> dict:
        self.log_start()
        if self.demo_mode:
            return await self._demo_run(clinic_id)
        self.log_complete(tasks=0)
        return {"message": "Production mode not yet connected"}

    def _calculate_health(self, clinic: dict) -> dict:
        score = 0
        if clinic.get("bookings_trend") == "up": score += 25
        elif clinic.get("bookings_trend") == "stable": score += 15
        else: score += 5
        if clinic.get("roas", 0) >= 3: score += 20
        elif clinic.get("roas", 0) >= 1.5: score += 10
        if clinic.get("whatsapp_resolution", 0) >= 0.8: score += 15
        elif clinic.get("whatsapp_resolution", 0) >= 0.5: score += 8
        if clinic.get("dashboard_login_days", 99) <= 3: score += 15
        elif clinic.get("dashboard_login_days", 99) <= 7: score += 8
        if clinic.get("payment_status") == "current": score += 15
        elif clinic.get("payment_status") == "overdue_7": score += 5
        if clinic.get("nps", 0) >= 8: score += 10
        elif clinic.get("nps", 0) >= 6: score += 5

        category = "healthy" if score >= 70 else ("watch" if score >= 40 else "at_risk")
        return {"score": score, "category": category}

    async def _demo_run(self, clinic_id=None) -> dict:
        clinics = [
            {"name": "Smile Dental", "city": "Hyderabad", "bookings_trend": "up", "roas": 4.2,
             "whatsapp_resolution": 0.92, "dashboard_login_days": 1, "payment_status": "current", "nps": 9},
            {"name": "SkinGlow Derma", "city": "Mumbai", "bookings_trend": "stable", "roas": 2.8,
             "whatsapp_resolution": 0.75, "dashboard_login_days": 5, "payment_status": "current", "nps": 7},
            {"name": "Nova Fertility", "city": "Delhi", "bookings_trend": "down", "roas": 1.2,
             "whatsapp_resolution": 0.45, "dashboard_login_days": 14, "payment_status": "overdue_15", "nps": 4},
        ]
        results = []
        for c in clinics:
            health = self._calculate_health(c)
            action = []
            if health["category"] == "at_risk":
                action = [
                    "URGENT: Schedule save call within 24h",
                    f"Use tactical empathy: 'It seems like the campaign hasn't been meeting your expectations...'",
                    "Offer: Free campaign audit + 1 month discount",
                ]
            elif health["category"] == "watch":
                action = [
                    "Schedule check-in call this week",
                    "Share wins report with ROI highlight",
                    f"Upsell angle: 'Your {c['bookings_trend']} bookings trend could accelerate with our Growth plan'",
                ]
            else:
                action = [
                    "Send congratulations + case study request",
                    "Upsell to Premium: multi-location support",
                    "Ask for referral (reciprocity principle)",
                ]
            results.append({**c, **health, "action_items": action})

        return {
            "agent": self.name, "run_at": datetime.now().isoformat(),
            "summary": {
                "total_clinics": len(results),
                "healthy": sum(1 for r in results if r["category"] == "healthy"),
                "watch": sum(1 for r in results if r["category"] == "watch"),
                "at_risk": sum(1 for r in results if r["category"] == "at_risk"),
            },
            "clinics": results,
        }
