"""Finance Bot Agent — Revenue Reconciliation & SaaS Metrics"""
import logging
from datetime import datetime
from app.services.agents.base_agent import BaseAgent

logger = logging.getLogger(__name__)


class FinanceBot(BaseAgent):
    name = "finance_bot"
    display_name = "Finance Bot"
    schedule = "0 7 1 * *"  # 1st of month, 7 AM IST
    description = "Razorpay reconciliation, SaaS metrics (MRR/churn/LTV/CAC), GST reports."

    async def run(self, **kwargs) -> dict:
        self.log_start()
        if self.demo_mode:
            return await self._demo_run()
        self.log_complete(tasks=1)
        return {"message": "Production mode not yet connected"}

    async def _demo_run(self) -> dict:
        return {
            "agent": self.name, "generated_at": datetime.now().isoformat(),
            "financial_report": {
                "period": "November 2026",
                "saas_metrics": {
                    "mrr": 149700, "new_mrr": 23940, "churned_mrr": 5994, "expansion_mrr": 8991,
                    "net_new_mrr": 26937, "mrr_growth_rate": "21.9%",
                },
                "clinic_metrics": {
                    "total_clinics": 50, "active": 47, "churned_this_month": 2, "new_this_month": 8,
                    "monthly_churn_rate": "4.0%", "annual_churn_rate": "38.3%",
                },
                "unit_economics": {
                    "arpu": 2994, "ltv": 74850, "cac": 8500, "ltv_cac_ratio": 8.8,
                    "payback_months": 2.8, "gross_margin": "82%",
                },
                "revenue_breakdown": {
                    "starter_plan": {"clinics": 25, "revenue": 74975},
                    "growth_plan": {"clinics": 15, "revenue": 44955},
                    "premium_plan": {"clinics": 7, "revenue": 20979},
                    "ad_spend_managed": 750000,
                },
                "razorpay_reconciliation": {
                    "expected": 149700, "received": 143706, "pending": 5994,
                    "overdue_clinics": ["Nova Fertility Centre", "QuickSmile Dental"],
                },
                "gst_summary": {"taxable_amount": 149700, "cgst_9pct": 13473, "sgst_9pct": 13473, "total_gst": 26946},
            },
        }
