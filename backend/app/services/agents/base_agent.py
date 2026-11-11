"""PatientPlex AI — Base Agent class.

All 14 agents extend this. Uses the real repo's config (CLAUDE_API_KEY, not
ANTHROPIC_API_KEY) and defaults DEMO_MODE to True until real API credentials
are configured.
"""
import logging
import time
from abc import abstractmethod
from datetime import datetime
from typing import Any, Optional

from app.core.config import settings

logger = logging.getLogger(__name__)


class BaseAgent:
    """Base class for all PatientPlex AI agents."""

    name: str = "base"
    display_name: str = "Base Agent"
    schedule: str = "on_demand"
    description: str = ""

    def __init__(self):
        # Real config uses CLAUDE_API_KEY.  DEMO_MODE may not be in settings;
        # default to True so agents return sample data until real credentials
        # and database are connected.
        self.demo_mode: bool = getattr(settings, "DEMO_MODE", True)
        self._start_time: float = 0.0

    # ── Logging helpers ──────────────────────────────────────────────

    def log_start(self):
        self._start_time = time.time()
        logger.info(f"[{self.display_name}] Run started")

    def log_complete(self, tasks: int = 0):
        elapsed = round(time.time() - self._start_time, 2)
        logger.info(
            f"[{self.display_name}] Completed — {tasks} tasks in {elapsed}s"
        )

    def log_error(self, error: Exception):
        logger.error(f"[{self.display_name}] Error: {error}", exc_info=True)

    # ── Claude API helper ────────────────────────────────────────────

    async def call_claude(
        self, prompt: str, max_tokens: int = 4096
    ) -> dict:
        """Call Claude API.  Returns canned response in demo mode."""
        if self.demo_mode:
            return {"response": f"[DEMO] Prompt received ({len(prompt)} chars)"}
        try:
            import anthropic

            client = anthropic.AsyncAnthropic(
                api_key=settings.CLAUDE_API_KEY  # matches real config
            )
            message = await client.messages.create(
                model="claude-sonnet-4-20250514",
                max_tokens=max_tokens,
                messages=[{"role": "user", "content": prompt}],
            )
            return {"response": message.content[0].text}
        except Exception as e:
            logger.error(f"Claude API error: {e}")
            return {"error": str(e)}

    # ── Execution wrapper ────────────────────────────────────────────

    async def execute(self, triggered_by: str = "manual", **kwargs) -> dict:
        """Run the agent, time it, return a structured result."""
        self.log_start()
        start = time.time()
        try:
            result = await self.run(**kwargs)
            elapsed = round(time.time() - start, 2)
            return {
                "agent": self.name,
                "status": "completed",
                "triggered_by": triggered_by,
                "duration_seconds": elapsed,
                "result": result,
            }
        except Exception as e:
            self.log_error(e)
            raise

    def get_info(self) -> dict:
        return {
            "name": self.name,
            "display_name": self.display_name,
            "schedule": self.schedule,
            "description": self.description,
            "demo_mode": self.demo_mode,
        }

    @abstractmethod
    async def run(self, **kwargs) -> dict:
        """Subclasses implement the actual work here."""
        ...
