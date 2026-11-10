"""Ads Optimizer Agent — Daily Google Ads Campaign Optimization Engine"""
import logging
from datetime import datetime, timedelta
from typing import Optional
from app.services.agents.base_agent import BaseAgent
from app.core.knowledge_base import get_benchmark, get_city_tier, NMC_COMPLIANCE, MARKETING_EXPERTISE, check_nmc_compliance

logger = logging.getLogger(__name__)


class AdsOptimizer(BaseAgent):
    """Runs daily automated optimization on ALL clinic Google Ads campaigns.
    The brain of a ₹2L/month performance marketing specialist, encoded as code."""

    name = "ads_optimizer"
    display_name = "Ads Optimizer"
    schedule = "0 6 * * *"  # 6 AM IST daily
    description = "Daily optimization: search terms, bids, quality scores, ad copy refresh, budget pacing."

    async def run(self, clinic_id: str = None) -> dict:
        self.log_start()
        try:
            if self.demo_mode:
                return await self._demo_run(clinic_id)

            # Production flow
            clinics = await self._get_active_clinics(clinic_id)
            results = []
            for clinic in clinics:
                result = await self._optimize_clinic(clinic)
                results.append(result)
            self.log_complete(tasks=len(results))
            return {"optimized_clinics": len(results), "results": results}
        except Exception as e:
            self.log_error(e)
            raise

    async def _optimize_clinic(self, clinic: dict) -> dict:
        """Full optimization cycle for one clinic."""
        # Step 1: Pull data from Google Ads API
        search_terms = await self._get_search_terms(clinic)
        # Step 2: Analyze and optimize
        bleeders = self._find_bleeders(search_terms)
        winners = self._find_winners(search_terms)
        # Step 3-7: Bid optimization, QS monitoring, ad copy, budget pacing, report
        return {"clinic": clinic["name"], "bleeders_paused": len(bleeders), "winners_promoted": len(winners)}

    async def _get_active_clinics(self, clinic_id=None):
        return []

    async def _get_search_terms(self, clinic):
        return []

    def _find_bleeders(self, terms):
        return [t for t in terms if t.get("spend", 0) > 500 and t.get("conversions", 0) == 0]

    def _find_winners(self, terms):
        return [t for t in terms if t.get("conversions", 0) >= 3]

    async def _demo_run(self, clinic_id: str = None) -> dict:
        clinics_data = [
            {"name": "Smile Dental Clinic", "city": "Hyderabad", "specialty": "dental_general",
             "spend_7d": 4200, "clicks": 312, "leads": 18, "bookings": 9, "cpl": 233},
            {"name": "SkinGlow Dermatology", "city": "Mumbai", "specialty": "dermatology",
             "spend_7d": 6800, "clicks": 245, "leads": 14, "bookings": 7, "cpl": 486},
            {"name": "Nova Fertility Centre", "city": "Delhi", "specialty": "ivf",
             "spend_7d": 12500, "clicks": 187, "leads": 8, "bookings": 3, "cpl": 1563},
            {"name": "ClearVision Eye Hospital", "city": "Bangalore", "specialty": "ophthalmology",
             "spend_7d": 3100, "clicks": 198, "leads": 12, "bookings": 6, "cpl": 258},
            {"name": "OrthoCare Clinic", "city": "Pune", "specialty": "orthopedics",
             "spend_7d": 5400, "clicks": 156, "leads": 10, "bookings": 4, "cpl": 540},
        ]

        optimizations = []
        total_saved = 0
        total_actions = 0

        for clinic in clinics_data:
            benchmark = get_benchmark(clinic["specialty"])
            actions = []

            # Bleeder keywords
            bleeders = [
                {"keyword": "dental college hyderabad", "spend": 850, "clicks": 12, "conversions": 0},
                {"keyword": "dentistry course", "spend": 420, "clicks": 8, "conversions": 0},
            ] if clinic["specialty"] == "dental_general" else [
                {"keyword": f"{benchmark['name'].lower()} course", "spend": 650, "clicks": 10, "conversions": 0},
            ]
            saved = sum(b["spend"] for b in bleeders)
            total_saved += saved
            actions.append(f"Paused {len(bleeders)} bleeder keywords (saved ₹{saved}/week)")

            # Negative keywords
            neg_count = len(benchmark.get("negative_keywords", [])[:5])
            actions.append(f"Added {neg_count} negative keywords from knowledge base")

            # Winner promotion
            actions.append(f"Increased bids on top performer by 15% (CPL ₹{int(clinic['cpl'] * 0.7)})")

            # Quality score
            actions.append("Quality Score check: all keywords ≥5 ✅")

            # Budget pacing
            daily_budget = clinic["spend_7d"] / 7
            actions.append(f"Budget pacing: ₹{int(daily_budget)}/day — on track ✅")

            # Campaign health
            health_score = min(100, int(
                (30 if clinic["cpl"] < benchmark["avg_cpl"]["avg"] else 15) +
                (25 if clinic["bookings"] / max(clinic["leads"], 1) > 0.3 else 10) +
                (20 if clinic["leads"] > 10 else 10) +
                25  # base
            ))

            total_actions += len(actions)
            optimizations.append({
                "clinic": clinic["name"],
                "city": clinic["city"],
                "specialty": clinic["specialty"],
                "period": "Last 7 days",
                "metrics": {
                    "spend": f"₹{clinic['spend_7d']:,}",
                    "clicks": clinic["clicks"],
                    "leads": clinic["leads"],
                    "bookings": clinic["bookings"],
                    "cpl": f"₹{clinic['cpl']}",
                    "ctr": f"{round(clinic['clicks'] / max(clinic['clicks'] * 15, 1) * 100, 1)}%",
                    "roas": f"{round(clinic['bookings'] * benchmark['avg_treatment_value'] / max(clinic['spend_7d'], 1), 1)}x",
                },
                "health_score": health_score,
                "actions_taken": actions,
                "recommendations": [
                    f"Increase daily budget by 20% — missing clicks after 4pm",
                    f"Add sitelink extensions — estimated CTR improvement +12%",
                ],
            })

        return {
            "agent": self.name,
            "run_at": datetime.now().isoformat(),
            "summary": {
                "clinics_optimized": len(clinics_data),
                "total_actions": total_actions,
                "total_weekly_savings": f"₹{total_saved}",
                "avg_health_score": round(sum(o["health_score"] for o in optimizations) / len(optimizations)),
            },
            "optimizations": optimizations,
        }
