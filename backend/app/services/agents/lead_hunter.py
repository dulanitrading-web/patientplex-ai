"""Lead Hunter — Prospect research and ICP scoring.

Finds clinics on Google Maps, scores them against the Ideal Customer Profile,
and drafts outreach messages. All claims in outreach must be from real data.
"""
import logging
from datetime import datetime
from app.services.agents.base_agent import BaseAgent

logger = logging.getLogger(__name__)


class LeadHunter(BaseAgent):
    name = "lead_hunter"
    display_name = "Lead Hunter"
    schedule = "0 9 * * 1-5"  # 9 AM weekdays
    description = "Finds clinics on Google Maps, scores ICP fit, drafts personalised outreach."

    async def run(self, city: str = "hyderabad", specialty: str = "dental", limit: int = 5) -> dict:
        self.log_start()
        try:
            if self.demo_mode:
                return self._demo_run(city, specialty, limit)

            # Production: use SerpAPI / Google Maps to find clinics
            # TODO: wire to real search + scoring pipeline
            return {"status": "no_credentials", "message": "SerpAPI key not configured yet"}
        except Exception as e:
            self.log_error(e)
            raise

    @staticmethod
    def score_icp(clinic: dict) -> int:
        """Score 0-100 based on observable signals."""
        score = 0
        rating = clinic.get("google_rating", 0)
        reviews = clinic.get("review_count", 0)

        # Google presence
        if rating >= 4.0:
            score += 20
        elif rating >= 3.5:
            score += 10
        if reviews >= 50:
            score += 15
        elif reviews >= 20:
            score += 10

        # Digital presence
        if clinic.get("has_website"):
            score += 15
        if clinic.get("has_social_media"):
            score += 10

        # NOT running ads = bigger opportunity
        if not clinic.get("running_google_ads"):
            score += 20

        # Location tier
        tier = clinic.get("city_tier", "tier_2")
        if tier == "tier_1":
            score += 20
        elif tier == "tier_2":
            score += 15
        else:
            score += 10

        return min(score, 100)

    def _demo_run(self, city: str, specialty: str, limit: int) -> dict:
        return {
            "agent": self.name,
            "run_at": datetime.now().isoformat(),
            "mode": "demo",
            "search": {"city": city, "specialty": specialty},
            "prospects_found": 3,
            "prospects": [
                {
                    "name": f"Sample {specialty.title()} Clinic 1",
                    "city": city.title(),
                    "rating": 4.2,
                    "reviews": 87,
                    "has_website": True,
                    "running_google_ads": False,
                    "icp_score": 75,
                    "outreach_angle": "Good reviews but no online ads — missing patients searching Google",
                },
                {
                    "name": f"Sample {specialty.title()} Clinic 2",
                    "city": city.title(),
                    "rating": 3.8,
                    "reviews": 42,
                    "has_website": False,
                    "running_google_ads": False,
                    "icp_score": 60,
                    "outreach_angle": "No website, no ads — likely relying on walk-ins and referrals only",
                },
                {
                    "name": f"Sample {specialty.title()} Clinic 3",
                    "city": city.title(),
                    "rating": 4.5,
                    "reviews": 210,
                    "has_website": True,
                    "running_google_ads": True,
                    "icp_score": 45,
                    "outreach_angle": "Already running ads — pitch better ROI and AI receptionist",
                },
            ],
            "note": "Demo data — not connected to Google Maps API yet.",
        }
