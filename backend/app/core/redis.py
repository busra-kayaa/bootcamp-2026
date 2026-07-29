"""Redis client configuration and connection provider."""

import os
import redis.asyncio as aioredis
from redis import Redis

REDIS_URL = os.getenv("REDIS_URL", "redis://localhost:6379/0")

# Senkron Redis istemcisi (RESP2 zorlaması ile)
redis_client: Redis = Redis.from_url(REDIS_URL, decode_responses=True, protocol=2)


async def get_async_redis_client() -> aioredis.Redis:
    """Asenkron FastAPI servisleri için Redis bağlantı istemcisi döner."""
    return aioredis.from_url(REDIS_URL, decode_responses=True, protocol=2)


def check_redis_connection() -> bool:
    """Redis sunucusuna erişilebilirlik kontrolü yapar."""
    try:
        return redis_client.ping()
    except Exception:
        return False