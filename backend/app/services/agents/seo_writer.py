"""SEO Writer Agent — 2000-word NMC-Compliant Blog Generator"""
import logging
from datetime import datetime
from app.services.agents.base_agent import BaseAgent
from app.core.knowledge_base import get_benchmark, check_nmc_compliance

logger = logging.getLogger(__name__)


class SEOWriter(BaseAgent):
    name = "seo_writer"
    display_name = "SEO Writer"
    schedule = "0 10 * * 1"  # Monday 10 AM IST
    description = "2000-word SEO articles with NMC compliance, FAQ schema JSON-LD."

    async def run(self, specialty: str = "dental_general", city: str = "hyderabad", topic: str = None) -> dict:
        self.log_start()
        if self.demo_mode:
            return await self._demo_run(specialty, city, topic)

        benchmark = get_benchmark(specialty)
        prompt = f"""Write a 2000-word SEO blog post for a {benchmark['name']} clinic in {city}.
        Topic: {topic or benchmark['patient_questions'][0]}
        Include FAQ schema markup. Follow NMC compliance — no banned terms."""
        result = await self.call_claude(prompt)
        self.log_complete(tasks=1)
        return result

    async def _demo_run(self, specialty, city, topic) -> dict:
        benchmark = get_benchmark(specialty)
        title = topic or f"Complete Guide to {benchmark['name']} Treatment in {city.title()} — Cost, Procedure & Recovery"
        return {
            "agent": self.name, "generated_at": datetime.now().isoformat(),
            "article": {
                "title": title,
                "meta_description": f"Looking for {benchmark['name'].lower()} treatment in {city.title()}? Learn about costs (₹{benchmark['avg_treatment_value']:,}+), procedures, recovery time, and how to choose the right clinic.",
                "word_count": 2150,
                "headings": [
                    f"What is {benchmark['name']} Treatment?",
                    f"{benchmark['name']} Treatment Cost in {city.title()} (2026)",
                    "Types of Procedures Available",
                    "How to Choose the Right Clinic",
                    "What to Expect During Your Visit",
                    "Recovery Timeline",
                    "Frequently Asked Questions",
                ],
                "target_keywords": benchmark["top_keywords"][:5],
                "faq_schema": {
                    "@context": "https://schema.org",
                    "@type": "FAQPage",
                    "mainEntity": [
                        {"@type": "Question", "name": q,
                         "acceptedAnswer": {"@type": "Answer", "text": f"[AI-generated answer for: {q}]"}}
                        for q in benchmark["patient_questions"][:3]
                    ],
                },
                "nmc_compliance": {"status": "PASSED", "violations": []},
                "internal_links": [f"/{city.lower()}/{benchmark['name'].lower().replace(' ', '-')}/",
                                   f"/{city.lower()}/book-appointment/"],
            },
        }
