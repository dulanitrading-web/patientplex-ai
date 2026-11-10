"""Health Check Agent — Churn Signal Detection & Instant Alerts"""
import logging
from datetime import datetime
from app.services.agents.base_agent import BaseAgent

logger = logging.getLogger(__name__)


class HealthCheck(BaseAgent):
    name = "health_check"
    display_name = "Health Check"
    schedule = "0 */4 * * *"  # Every 4 hours
    description = "6 churn signals detection, severity classification, instant alerts."

    CHURN_SIGNALS = [
        {"signal": "bookings_drop_30pct", "severity": "critical", "label": "Bookings dropped >30% week-over-week"},
        {"signal": "no_dashboard_login_7d", "severity": "high", "label": "No dashboard login in 7+ days"},
        {"signal": "payment_overdue_15d", "severity": "critical", "label": "Payment overdue 15+ days"},
        {"signal": "whatsapp_unread_24h", "severity": "high", "label": "WhatsApp messages unread 24h+"},
        {"signal": "roas_below_1", "severity": "critical", "label": "ROAS dropped below 1.0"},
        {"signal": "support_ticket_unresolved", "severity": "medium", "label": "Support ticket open 48h+"},
    ]

    async def run(self, clinic_id: str = None) -> dict:
        self.log_start()
        if self.demo_mode:
            return await self._demo_run(clinic_id)
        self.log_complete(tasks=0)
        return {"message": "Production mode not yet connected"}

    async def _demo_run(self, clinic_id=None) -> dict:
        alerts = [
            {"clinic": "Nova Fertility Centre", "city": "Delhi", "signal": "bookings_drop_30pct",
             "severity": "critical", "details": "Bookings dropped from 12 to 6 (-50%) this week",
             "action": "Immediate CSM call + campaign audit", "detected_at": datetime.now().isoformat()},
            {"clinic": "Nova Fertility Centre", "city": "Delhi", "signal": "roas_below_1",
             "severity": "critical", "details": "ROAS at 0.8 — spending more than earning",
             "action": "Pause underperforming campaigns, reallocate budget", "detected_at": datetime.now().isoformat()},
            {"clinic": "SkinGlow Dermatology", "city": "Mumbai", "signal": "no_dashboard_login_7d",
             "severity": "high", "details": "Last login: 9 days ago",
             "action": "Send re-engagement email with weekly wins summary", "detected_at": datetime.now().isoformat()},
            {"clinic": "OrthoCare Clinic", "city": "Pune", "signal": "whatsapp_unread_24h",
             "severity": "high", "details": "3 patient messages unread for 28 hours",
             "action": "Alert clinic owner via SMS + auto-respond to patients", "detected_at": datetime.now().isoformat()},
        ]
        return {
            "agent": self.name, "run_at": datetime.now().isoformat(),
            "summary": {
                "clinics_scanned": 5,
                "alerts_generated": len(alerts),
                "critical": sum(1 for a in alerts if a["severity"] == "critical"),
                "high": sum(1 for a in alerts if a["severity"] == "high"),
                "medium": sum(1 for a in alerts if a["severity"] == "medium"),
            },
            "alerts": alerts,
        }
