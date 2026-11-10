"""Reel Writer Agent — Instagram Reel Script Generator"""
import logging
from datetime import datetime
from app.services.agents.base_agent import BaseAgent
from app.core.knowledge_base import get_benchmark, check_nmc_compliance

logger = logging.getLogger(__name__)


class ReelWriter(BaseAgent):
    name = "reel_writer"
    display_name = "Reel Writer"
    schedule = "0 11 * * 3"  # Wednesday 11 AM IST
    description = "Instagram Reel scripts HOOK→PROBLEM→SOLUTION→CTA format."

    async def run(self, specialty: str = "dental_general", topic: str = None) -> dict:
        self.log_start()
        if self.demo_mode:
            return await self._demo_run(specialty, topic)
        self.log_complete(tasks=1)
        return {"message": "Production mode not yet connected"}

    async def _demo_run(self, specialty, topic) -> dict:
        benchmark = get_benchmark(specialty)
        scripts = [
            {
                "title": f"Stop Scrolling If You Have {benchmark['patient_questions'][0].split('?')[0]}",
                "duration": "30 seconds",
                "format": "HOOK → PROBLEM → SOLUTION → CTA",
                "script": {
                    "hook": f"🛑 Stop scrolling if you've been ignoring this...",
                    "problem": f"Most people delay {benchmark['name'].lower()} treatment thinking it's painful or expensive.",
                    "solution": f"Modern {benchmark['name'].lower()} is virtually painless and starts at just ₹{benchmark['avg_treatment_value']:,}.",
                    "cta": "DM 'BOOK' to get a free consultation this week ↓",
                },
                "visual_notes": "Doctor speaking to camera → pain-free procedure B-roll → price graphic → DM button",
                "hashtags": [f"#{benchmark['name'].replace(' ', '').lower()}", "#healthcare", "#doctortips"],
                "nmc_compliance": "PASSED",
            },
            {
                "title": f"3 Signs You Need to See a {benchmark['name']} Specialist",
                "duration": "45 seconds",
                "format": "HOOK → 3 SIGNS → CTA",
                "script": {
                    "hook": "Your body is trying to tell you something 👆",
                    "sign_1": "Sign 1: [Symptom specific to specialty]",
                    "sign_2": "Sign 2: [Symptom specific to specialty]",
                    "sign_3": "Sign 3: If you've been waiting more than 2 weeks...",
                    "cta": f"Comment 'CHECK' and we'll send you a free symptom guide",
                },
                "visual_notes": "Split screen: symptoms vs healthy → doctor explaining → comment CTA overlay",
                "hashtags": [f"#{benchmark['name'].replace(' ', '').lower()}", "#healthtips", "#awareness"],
                "nmc_compliance": "PASSED",
            },
        ]
        return {
            "agent": self.name, "generated_at": datetime.now().isoformat(),
            "scripts_count": len(scripts), "scripts": scripts,
        }
