"""Content Creator Agent — Weekly Multi-Channel Content Generation"""
import logging
from datetime import datetime
from app.services.agents.base_agent import BaseAgent
from app.core.knowledge_base import get_benchmark, NMC_COMPLIANCE, check_nmc_compliance

logger = logging.getLogger(__name__)


class ContentCreator(BaseAgent):
    """Generates weekly content: LinkedIn post, newsletter section,
    GMB post, and WhatsApp broadcast — all NMC compliant."""

    name = "content_creator"
    display_name = "Content Creator"
    schedule = "0 9 * * 1"  # Monday 9 AM
    description = "Weekly content: LinkedIn, newsletter, GMB post, WhatsApp broadcast."

    async def run(self, specialty: str = "dental_general", city: str = "hyderabad") -> dict:
        self.log_start()
        try:
            if self.demo_mode:
                return await self._demo_run(specialty, city)

            benchmark = get_benchmark(specialty)
            content = {}
            for channel in ["linkedin", "newsletter", "gmb", "whatsapp"]:
                prompt = self._build_prompt(channel, benchmark, city)
                result = await self.call_claude(prompt)
                violations = check_nmc_compliance(result.get("response", ""))
                content[channel] = {"content": result, "nmc_violations": violations}
            self.log_complete(tasks=4)
            return content
        except Exception as e:
            self.log_error(e)
            raise

    def _build_prompt(self, channel, benchmark, city):
        return f"Write a {channel} post for a {benchmark['name']} clinic in {city}. NMC compliant."

    async def _demo_run(self, specialty, city) -> dict:
        benchmark = get_benchmark(specialty)
        return {
            "agent": self.name,
            "generated_at": datetime.now().isoformat(),
            "week": datetime.now().strftime("Week %W, %Y"),
            "content": {
                "linkedin": {
                    "post": f"🏥 Did you know? The average Indian searches for a {benchmark['name'].lower()} 3x before booking.\n\nAt PatientPlex, we help clinics capture those searches with AI-powered Google Ads + WhatsApp automation.\n\nResult for our {city.title()} clients:\n📊 {benchmark['avg_roas']}x average ROAS\n📱 10-second WhatsApp response time\n📈 25-35 new patient leads/month\n\nYour clinic's next patient is already searching. Are you visible?\n\n#HealthcareMarketing #DigitalHealth #PatientPlex",
                    "nmc_compliant": True,
                    "scheduled_for": "Tuesday 10:00 AM",
                },
                "newsletter": {
                    "subject": f"How {city.title()} Clinics Are Getting 30+ Patients/Month",
                    "preview_text": "The AI-powered system behind India's fastest-growing clinics",
                    "sections": [
                        {"heading": "This Week's Wins", "content": f"Our {city.title()} clinics collectively generated 450+ leads this week at ₹{benchmark['avg_cpl']['avg']} average CPL."},
                        {"heading": "Tip of the Week", "content": f"Add your clinic's WhatsApp number to your Google Ads — 40% of patients prefer messaging over calling."},
                        {"heading": "Case Study Spotlight", "content": f"A {benchmark['name'].lower()} clinic went from 0 to 22 patients/month in 60 days using our 3-campaign strategy."},
                    ],
                    "nmc_compliant": True,
                    "scheduled_for": "Wednesday 11:00 AM",
                },
                "gmb": {
                    "post": f"Looking for quality {benchmark['name'].lower()} in {city.title()}? We offer a range of treatments with experienced doctors. Book your consultation today!\n\n📞 Call or WhatsApp us\n⏰ Mon-Sat, 9 AM - 8 PM\n\nResults may vary. Please consult your doctor for personalized advice.",
                    "nmc_compliant": True,
                    "type": "update",
                    "scheduled_for": "Thursday 2:00 PM",
                },
                "whatsapp_broadcast": {
                    "message": f"Hi! 👋\n\nThis week at our clinic:\n✅ Special consultation offer\n✅ New treatment options available\n✅ Easy online booking\n\nReply BOOK to schedule your visit!\n\nResults may vary. Please consult your doctor for personalized advice.",
                    "nmc_compliant": True,
                    "target_segment": "Enquired but not booked (last 30 days)",
                    "estimated_reach": 150,
                    "scheduled_for": "Friday 10:00 AM",
                },
            },
        }
