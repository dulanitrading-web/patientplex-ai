"""Text generation through the configured provider."""

import asyncio
import logging

import httpx

from app.core.config import settings

logger = logging.getLogger(__name__)


class AIProviderError(RuntimeError):
    """A provider failure with a safe caller-facing description."""


def configured() -> bool:
    if settings.AI_PROVIDER == "anthropic":
        return bool(settings.ANTHROPIC_API_KEY or settings.CLAUDE_API_KEY)
    if settings.AI_PROVIDER == "openai":
        return bool(settings.OPENAI_API_KEY)
    return False


async def generate_text(system_prompt: str, user_prompt: str, *, max_tokens: int = 1024) -> str:
    provider = settings.AI_PROVIDER
    if not configured():
        raise AIProviderError("AI provider credentials are not configured")
    if provider == "anthropic":
        url = "https://api.anthropic.com/v1/messages"
        headers = {
            "x-api-key": settings.ANTHROPIC_API_KEY or settings.CLAUDE_API_KEY,
            "anthropic-version": "2023-06-01",
            "content-type": "application/json",
        }
        payload = {
            "model": settings.AI_MODEL or "claude-sonnet-5-5",
            "system": system_prompt,
            "messages": [{"role": "user", "content": user_prompt}],
            "max_tokens": max_tokens,
        }
    else:
        url = "https://api.openai.com/v1/responses"
        headers = {"Authorization": f"Bearer {settings.OPENAI_API_KEY}"}
        payload = {
            "model": settings.AI_MODEL or "gpt-5-mini",
            "instructions": system_prompt,
            "input": user_prompt,
            "max_output_tokens": max_tokens,
            "reasoning": {"effort": "minimal"},
            "store": False,
        }

    try:
        async with httpx.AsyncClient(timeout=httpx.Timeout(25, connect=5)) as client:
            for attempt in range(3):
                response = await client.post(url, headers=headers, json=payload)
                if response.status_code != 429 and response.status_code < 500:
                    break
                if attempt < 2:
                    await asyncio.sleep(2 ** attempt)
    except httpx.HTTPError as exc:
        logger.warning("AI provider transport error: provider=%s kind=%s", provider, type(exc).__name__)
        raise AIProviderError("AI provider could not be reached") from None

    if not response.is_success:
        logger.warning("AI provider rejected request: provider=%s status=%s", provider, response.status_code)
        raise AIProviderError(f"AI provider request failed (HTTP {response.status_code})")
    try:
        data = response.json()
        if provider == "anthropic":
            blocks = data["content"]
            text_type = "text"
        else:
            blocks = [
                block
                for item in data["output"] if item["type"] == "message"
                for block in item["content"]
            ]
            text_type = "output_text"
        text = "\n".join(block["text"] for block in blocks if block["type"] == text_type).strip()
    except (KeyError, TypeError, ValueError):
        raise AIProviderError("AI provider returned an invalid response") from None
    if not text:
        raise AIProviderError("AI provider returned no text")
    return text
