"""PatientPlex AI — Base Agent class.

Shared execution and text generation for scheduled agents.
"""
import logging
import time
from abc import abstractmethod
from datetime import datetime
from typing import Any, Optional

from app.core.config import settings
from app.services.ai import AIProviderError, generate_text

logger = logging.getLogger(__name__)


class BaseAgent:
    """Base class for all PatientPlex AI agents."""

    name: str = "base"
    display_name: str = "Base Agent"
    schedule: str = "on_demand"
    description: str = ""

    def __init__(self):
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
        """Generate text through the configured provider, or return the demo response."""
        if self.demo_mode:
            return {"response": f"[DEMO] Prompt received ({len(prompt)} chars)"}
        try:
            response = await generate_text(
                "Follow the task instructions.", prompt, max_tokens=max_tokens
            )
            return {"response": response}
        except AIProviderError as error:
            return {"error": str(error)}

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
