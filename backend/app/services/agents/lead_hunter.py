"""Lead Hunter Agent — Google Maps Scraping + ICP Scoring + SPIN Outreach"""
import logging
from datetime import datetime
from app.services.agents.base_agent import BaseAgent
from app.core.knowledge_base import get_benchmark, get_city_tier

logger = logging.getLogger(__name__)


class LeadHunter(BaseAgent):
    """Scrapes Google Maps for clinics, scores them against ICP,
    drafts SPIN Selling outreach messages."""

    name = "lead_hunter"
    display_name = "Lead Hunter"
    schedule = "0 9 * * 1-5"  # 9 AM weekdays
    description = "Scrape Google Maps, ICP score 0-100, draft SPIN outreach."

    async def run(self, city: str = "hyderabad", specialty: str = "dental_general", limit: int = 20) -> dict:
        self.log_start()
        try:
            if self.demo_mode:
                return await self._demo_run(city, specialty)

            # Production: SerpAPI Google Maps search
            raw_results = await self._scrape_google_maps(city, specialty, limit)
            scored = [self._score_icp(r) for r in raw_results]
            scored.sort(key=lambda x: x["icp_score"], reverse=True)

            for prospect in scored[:10]:
                prospect["outreach"] = await self._draft_outreach(prospect, specialty)

            self.log_complete(tasks=len(scored))
            return {"prospects_found": len(scored), "prospects": scored[:10]}
        except Exception as e:
            self.log_error(e)
            raise

    async def _scrape_google_maps(self, city, specialty, limit):
        return []

    def _score_icp(self, clinic: dict) -> dict:
        """Score a clinic 0-100 based on ICP fit."""
        score = 0
        rating = clinic.get("google_rating", 0)
        reviews = clinic.get("review_count", 0)

        # Google rating (0-20): 3.5-4.5 is ideal (room to grow)
        if 3.5 <= rating <= 4.5:
            score += 20
        elif rating > 4.5:
            score += 12
        elif rating > 3.0:
            score += 8

        # Review count (0-20): 50-500 is ideal (established but not massive)
        if 50 <= reviews <= 500:
            score += 20
        elif reviews > 500:
            score += 10
        elif reviews > 20:
            score += 12

        # Website quality (0-20)
        if clinic.get("has_website"):
            score += 15
            if not clinic.get("website_mobile_friendly"):
                score += 5  # more room for us to help
        else:
            score += 10  # no website = needs digital help

        # Social media (0-15)
        if clinic.get("has_social_media"):
            score += 10
        else:
            score += 15  # no social = bigger opportunity

        # Not running Google Ads (0-25) — biggest opportunity signal
        if not clinic.get("running_google_ads"):
            score += 25
        else:
            score += 5

        clinic["icp_score"] = min(100, score)
        return clinic

    async def _draft_outreach(self, prospect, specialty):
        benchmark = get_benchmark(specialty)
        return {
            "subject": f"Getting {prospect.get('name', 'your clinic')} 20+ new patients/month",
            "message": f"Hi Dr. {prospect.get('doctor_name', 'Doctor')}, "
                       f"I noticed {prospect.get('name')} has great reviews but isn't running Google Ads. "
                       f"Clinics like yours in {prospect.get('city', 'your city')} typically get "
                       f"patients at ₹{benchmark['avg_cpl']['avg']}/lead with our system.",
        }

    async def _demo_run(self, city, specialty) -> dict:
        benchmark = get_benchmark(specialty)
        tier = get_city_tier(city)
        return {
            "agent": self.name,
            "run_at": datetime.now().isoformat(),
            "search": {"city": city, "specialty": specialty, "tier": tier["tier"]},
            "summary": {
                "total_scraped": 45,
                "icp_qualified": 18,
                "outreach_drafted": 5,
                "avg_icp_score": 72,
            },
            "top_prospects": [
                {
                    "name": "Bright Smile Dental",
                    "doctor": "Dr. Rajesh Kumar",
                    "city": city.title(),
                    "area": "Banjara Hills",
                    "google_rating": 4.2,
                    "review_count": 156,
                    "has_website": True,
                    "has_social_media": True,
                    "running_google_ads": False,
                    "icp_score": 85,
                    "outreach": {
                        "subject": "Getting Bright Smile Dental 20+ new patients/month",
                        "message": f"Hi Dr. Rajesh, I noticed Bright Smile has 156 great reviews (4.2★) but isn't running Google Ads. Similar {benchmark['name'].lower()} clinics in {city.title()} get patients at ₹{benchmark['avg_cpl']['avg']}/lead. One implant patient (₹35,000) pays for 7 months of our service. Can I show you in 15 minutes?",
                    },
                },
                {
                    "name": "Pearl Dental Care",
                    "doctor": "Dr. Sneha Reddy",
                    "city": city.title(),
                    "area": "Jubilee Hills",
                    "google_rating": 3.8,
                    "review_count": 89,
                    "has_website": True,
                    "has_social_media": False,
                    "running_google_ads": False,
                    "icp_score": 82,
                    "outreach": {
                        "subject": "Pearl Dental Care — patients are searching but can't find you",
                        "message": f"Hi Dr. Sneha, 'dentist near Jubilee Hills' gets 2,400 searches/month. Your clinic has 89 positive reviews but no Google Ads presence. I can get you in front of those patients at ₹{benchmark['avg_cpl']['avg']}/lead. 14-day free trial — zero risk.",
                    },
                },
                {
                    "name": "Dento Care Clinic",
                    "doctor": "Dr. Anil Sharma",
                    "city": city.title(),
                    "area": "Madhapur",
                    "google_rating": 4.5,
                    "review_count": 312,
                    "has_website": True,
                    "has_social_media": True,
                    "running_google_ads": True,
                    "icp_score": 52,
                    "outreach": {
                        "subject": "Dento Care — your Google Ads could perform 3x better",
                        "message": f"Hi Dr. Anil, I see you're already running Google Ads — smart move. But most agencies can't tell you which ad brought which patient. Our AI tracks every rupee to every booking. Current benchmark: ₹{benchmark['avg_cpl']['avg']} CPL, {benchmark['avg_roas']}x ROAS.",
                    },
                },
                {
                    "name": "Healthy Teeth Clinic",
                    "doctor": "Dr. Priya Nair",
                    "city": city.title(),
                    "area": "Kondapur",
                    "google_rating": 4.0,
                    "review_count": 67,
                    "has_website": False,
                    "has_social_media": False,
                    "running_google_ads": False,
                    "icp_score": 78,
                    "outreach": {
                        "subject": "Dr. Priya — your patients can't find you online",
                        "message": f"Hi Dr. Priya, Healthy Teeth has 67 reviews (4.0★) but no website or social media. You're invisible to the 3,000+ people searching for dentists in Kondapur every month. We'll set up everything in 48 hours. 14-day free trial.",
                    },
                },
                {
                    "name": "SmileZone Dental Studio",
                    "doctor": "Dr. Vikram Rao",
                    "city": city.title(),
                    "area": "Gachibowli",
                    "google_rating": 3.6,
                    "review_count": 43,
                    "has_website": True,
                    "has_social_media": True,
                    "running_google_ads": False,
                    "icp_score": 74,
                    "outreach": {
                        "subject": "SmileZone — from 43 reviews to 200+ in 6 months",
                        "message": f"Hi Dr. Vikram, SmileZone has a great setup but needs more patient flow. Our AI-powered Google Ads + WhatsApp system brings 25-35 leads/month at ₹{benchmark['avg_cpl']['avg']} each. Your first implant patient covers 7 months of our service.",
                    },
                },
            ],
        }
