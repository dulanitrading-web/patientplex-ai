"""Redis caching layer for PatientPlex AI.

Provides async caching with automatic TTL management,
namespaced by doctor_id for multi-tenant isolation.

Falls back gracefully if Redis is unavailable — the app
works without cache, just slower.
"""

import json
import logging
from typing import Any

from app.core.config import settings

logger = logging.getLogger(__name__)

# Global Redis connection — initialized lazily
_redis = None


async def get_redis():
    """Get or create the Redis connection."""
    global _redis
    if _redis is not None:
        return _redis

    try:
        import redis.asyncio as aioredis
        _redis = aioredis.from_url(
            settings.REDIS_URL,
            encoding="utf-8",
            decode_responses=True,
            socket_connect_timeout=5,
            socket_timeout=5,
            retry_on_timeout=True,
        )
        # Test connection
        await _redis.ping()
        logger.info("Redis connected: %s", settings.REDIS_URL)
        return _redis
    except Exception as exc:
        logger.warning("Redis not available (%s) — running without cache", exc)
        _redis = None
        return None


class CacheTTL:
    """Default TTL values in seconds."""
    DASHBOARD = 300       # 5 minutes — dashboard metrics
    CAMPAIGNS = 60        # 1 minute — campaign data (changes frequently)
    ANALYTICS = 600       # 10 minutes — analytics aggregations
    CHANNEL_PERF = 600    # 10 minutes
    FUNNEL = 600          # 10 minutes
    HOURLY = 300          # 5 minutes
    TREATMENTS = 600      # 10 minutes
    DOCTOR_PROFILE = 3600 # 1 hour — rarely changes
    OPTIMIZATION = 1800   # 30 minutes — optimization results


class RedisCache:
    """Async Redis cache with doctor-scoped keys and graceful fallback."""

    PREFIX = "pp"  # PatientPlex namespace

    @classmethod
    def _key(cls, doctor_id: str, key: str) -> str:
        """Build a namespaced cache key."""
        return f"{cls.PREFIX}:{doctor_id}:{key}"

    @classmethod
    async def get(cls, doctor_id: str, key: str) -> Any | None:
        """Get a cached value. Returns None on miss or if Redis is unavailable."""
        redis = await get_redis()
        if not redis:
            return None

        try:
            raw = await redis.get(cls._key(doctor_id, key))
            if raw is None:
                return None
            return json.loads(raw)
        except Exception as exc:
            logger.warning("Cache get failed for %s: %s", key, exc)
            return None

    @classmethod
    async def set(cls, doctor_id: str, key: str, value: Any, ttl: int = 300) -> bool:
        """Set a cached value with TTL. Returns False if Redis is unavailable."""
        redis = await get_redis()
        if not redis:
            return False

        try:
            serialized = json.dumps(value, default=str)
            await redis.setex(cls._key(doctor_id, key), ttl, serialized)
            return True
        except Exception as exc:
            logger.warning("Cache set failed for %s: %s", key, exc)
            return False

    @classmethod
    async def delete(cls, doctor_id: str, key: str) -> bool:
        """Delete a cached value."""
        redis = await get_redis()
        if not redis:
            return False

        try:
            await redis.delete(cls._key(doctor_id, key))
            return True
        except Exception as exc:
            logger.warning("Cache delete failed for %s: %s", key, exc)
            return False

    @classmethod
    async def get_or_set(cls, doctor_id: str, key: str, factory, ttl: int = 300) -> Any:
        """Get from cache, or call factory() and cache the result.

        The factory should be an async callable that produces the value.
        """
        cached = await cls.get(doctor_id, key)
        if cached is not None:
            return cached

        value = await factory()
        await cls.set(doctor_id, key, value, ttl)
        return value

    @classmethod
    async def invalidate_doctor(cls, doctor_id: str) -> int:
        """Invalidate all cached data for a doctor (after optimization, data change, etc)."""
        redis = await get_redis()
        if not redis:
            return 0

        try:
            pattern = f"{cls.PREFIX}:{doctor_id}:*"
            keys = []
            async for key in redis.scan_iter(match=pattern, count=100):
                keys.append(key)
            if keys:
                await redis.delete(*keys)
            logger.info("Invalidated %d cache keys for doctor %s", len(keys), doctor_id)
            return len(keys)
        except Exception as exc:
            logger.warning("Cache invalidation failed for doctor %s: %s", doctor_id, exc)
            return 0
