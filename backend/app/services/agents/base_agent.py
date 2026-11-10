"""Base Agent — Foundation class for all PatientPlex AI agents."""
import logging
import time
from abc import abstractmethod
from datetime import datetime
from typing import Any, Optional

from app.core.config import settings

logger = logging.getLogger(__name__)


class BaseAgent:
    """Base class that every PatientPlex agent extends."""

    name: str = "base_agent"
    display_name: str = "Base Agent"
    schedule: str = "on_demand"
    description: str = "Base agent class"

    def __init__(self):
        self.demo_mode: bool = settings.DEMO_MODE
        self._start_time: Optional[float] = None

    # ── Logging helpers ──

    def log_start(self):
        self._start_time = time.time()
        logger.info(f"[{self.name}] Starting run (demo_mode={self.demo_mode})")

    def log_complete(self, tasks: int = 0):
        elapsed = round(time.time() - (self._start_time or time.time()), 2)
        logger.info(f"[{self.name}] Completed — {tasks} tasks in {elapsed}s")

    def log_error(self, error: Exception):
        logger.error(f"[{self.name}] Error: {error}", exc_info=True)

    # ── Claude API helper ──

    async def call_claude(self, prompt: str, max_tokens: int = 4096) -> dict:
        """Call Anthropic Claude API for AI-powered analysis."""
        if self.demo_mode:
            return {"response": f"[DEMO] Claude response for: {prompt[:80]}..."}

        try:
            import anthropic

            client = anthropic.AsyncAnthropic(api_key=settings.ANTHROPIC_API_KEY)
            message = await client.messages.create(
                model="claude-sonnet-4-20250514",
                max_tokens=max_tokens,
                messages=[{"role": "user", "content": prompt}],
            )
            return {"response": message.content[0].text}
        except Exception as e:
            logger.error(f"[{self.name}] Claude API error: {e}")
            return {"error": str(e)}

    # ── Execution wrapper ──

    async def execute(self, triggered_by: str = "manual", **kwargs) -> dict:
        """Wrapper that tracks timing and creates an AgentRun record."""
        start = datetime.now()
        status = "completed"
        result_data: Any = None
        error_count = 0
        task_count = 0

        try:
            result_data = await self.run(**kwargs)
            if isinstance(result_data, dict):
                task_count = result_data.get("tasks_completed", 1)
        except Exception as exc:
            status = "failed"
            error_count = 1
            result_data = {"error": str(exc)}
            raise
        finally:
            elapsed = (datetime.now() - start).total_seconds()
            run_record = {
                "agent_name": self.name,
                "status": status,
                "started_at": start.isoformat(),
                "completed_at": datetime.now().isoformat(),
                "duration_seconds": round(elapsed, 2),
                "tasks_completed": task_count,
                "errors": error_count,
                "result_summary": str(result_data)[:500] if result_data else None,
                "result_data": result_data,
                "triggered_by": triggered_by,
            }
            logger.info(f"[{self.name}] Run record: {status} in {elapsed:.1f}s")
            # In production, persist run_record to AgentRun table
        return result_data

    # ── Abstract run method ──

    @abstractmethod
    async def run(self, **kwargs) -> dict:
        """Override in each agent with the actual logic."""
        raise NotImplementedError
