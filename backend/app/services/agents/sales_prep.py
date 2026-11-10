"""Sales Prep Agent — Pre-Call Research Brief Generator"""
import logging
from datetime import datetime
from typing import Optional
from app.services.agents.base_agent import BaseAgent
from app.core.knowledge_base import get_benchmark, get_city_tier, MARKETING_EXPERTISE

logger = logging.getLogger(__name__)


class SalesPrep(BaseAgent):
    """Generates a 1-page research brief before every sales demo call."""

    name = "sales_prep"
    display_name = "Sales Prep"
    schedule = "on_demand"
    description = "Pre-call research: scrapes Google, website, social, generates 1-page brief with SPIN questions and pitch angle."

    async def run(self, clinic_name: str, doctor_name: str = "", city: str = "hyderabad", specialty: str = "dental_general") -> dict:
        self.log_start()
        try:
            if self.demo_mode:
                return await self._demo_run(clinic_name, doctor_name, city, specialty)

            # Production: scrape Google, analyze website, generate brief via Claude
            research = await self._research_clinic(clinic_name, city)
            brief = await self._generate_brief(research, specialty, city)
            self.log_complete(tasks=1)
            return brief
        except Exception as e:
            self.log_error(e)
            raise

    async def _research_clinic(self, clinic_name: str, city: str) -> dict:
        """Research clinic via Google Maps, website, social media."""
        # In production: use SerpAPI, BeautifulSoup, etc.
        return {}

    async def _generate_brief(self, research: dict, specialty: str, city: str) -> dict:
        """Generate the brief via Claude API."""
        benchmark = get_benchmark(specialty)
        tier = get_city_tier(city)

        prompt = f"""Generate a 1-page sales prep brief for a {benchmark['name']} clinic in {city}.
        Use SPIN Selling questions and tactical empathy (Voss).
        Include benchmark CPL: ₹{benchmark['avg_cpl']['avg']}, ATV: ₹{benchmark['avg_treatment_value']}.
        Research data: {research}"""

        return await self.call_claude(prompt)

    async def _demo_run(self, clinic_name: str, doctor_name: str, city: str, specialty: str) -> dict:
        benchmark = get_benchmark(specialty)
        tier = get_city_tier(city)
        doctor = doctor_name or "Dr. Mehta"

        return {
            "agent": self.name,
            "generated_at": datetime.now().isoformat(),
            "brief": {
                "clinic_overview": {
                    "name": clinic_name or "Smile Dental Clinic",
                    "doctor": doctor,
                    "location": f"Banjara Hills, {city.title()} (Tier 1)",
                    "google_rating": 4.3,
                    "review_count": 187,
                    "specialty": benchmark["name"],
                    "services": ["Root Canal", "Implants", "Braces", "Whitening", "Cleaning"],
                    "website": f"{clinic_name.lower().replace(' ', '')}clinic.com" if clinic_name else "smiledentalhyderabad.com",
                    "website_quality": "Modern, mobile-friendly",
                    "instagram": f"@{clinic_name.lower().replace(' ', '_') if clinic_name else 'smiledental_hyd'}",
                    "instagram_followers": 2400,
                    "posts_per_week": 2,
                    "running_google_ads": False,
                },
                "estimated_revenue": f"₹15-20L/month (based on review volume + {tier['tier']} location)",
                "decision_maker": f"{doctor} (owner, 12 years experience)",
                "pain_points_from_reviews": [
                    {"review": "Called 3 times, no one picked up", "insight": "MISSED CALLS = MISSED PATIENTS", "our_solution": "WhatsApp AI answers in 10 seconds, 24/7"},
                    {"review": "Good doctor but had to wait 45 minutes", "insight": "SCHEDULING ISSUE", "our_solution": "AI booking optimization reduces wait times"},
                    {"review": "Hard to reach for appointments", "insight": "ACCESSIBILITY PROBLEM", "our_solution": "WhatsApp AI + instant booking confirmation"},
                ],
                "opportunity": {
                    "cpc_range": f"₹{benchmark['avg_cpc']['min']}-{benchmark['avg_cpc']['max']}",
                    "cpl_range": f"₹{benchmark['avg_cpl']['min']}-{benchmark['avg_cpl']['max']}",
                    "at_15k_budget": "Estimated 25-35 leads, 12-15 bookings",
                    "roi_example": f"Just 1 implant patient (₹{benchmark['high_value_treatments'].get('implants', {}).get('atv', 35000)}) pays for 7 months of PatientPlex",
                },
                "pitch_angle": {
                    "lead_with": f"Your Google reviews mention patients can't reach you for appointments. What if every WhatsApp and call was answered in 10 seconds, 24/7?",
                    "proof_point": f"We helped a similar {benchmark['name'].lower()} clinic get 22 new patients/month at ₹685 each.",
                    "objection_ready": {
                        "i_have_an_agency": "Can your agency tell you which ad brought which patient? Our AI tracks every rupee to every booking.",
                        "too_expensive": f"At ₹2,999/month, you need just ONE extra patient to 3x your investment. Your average treatment is ₹{benchmark['avg_treatment_value']}.",
                        "i_dont_trust_ai": "The AI doesn't replace your receptionist — it answers when they can't. 10pm enquiries, missed calls, holidays.",
                    },
                    "close": "14-day free trial. We set up everything in 48 hours. Zero risk.",
                },
                "spin_questions": {
                    "situation": f"How do you currently get new patients besides walk-ins and referrals?",
                    "problem": "What happens when someone WhatsApps you at 10pm?",
                    "implication": f"If you miss 5 enquiries a week, that's 20 potential patients a month — at ₹{benchmark['avg_treatment_value']} average, that's ₹{benchmark['avg_treatment_value'] * 20:,} in lost revenue.",
                    "need_payoff": "What would it mean for your practice if you had 40 patients instead of 25?",
                },
            },
        }
