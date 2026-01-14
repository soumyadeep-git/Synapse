import json
import logging
from typing import Any, Optional
import redis
from app.core.config import settings

logger = logging.getLogger(__name__)

# Initialize Redis Connection
redis_client = redis.Redis.from_url(settings.CELERY_BROKER_URL, decode_responses=True)

def get_cache(key: str) -> Optional[Any]:
    """Retrieve data from Redis"""
    try:
        data = redis_client.get(key)
        if data:
            return json.loads(data)
        return None
    except Exception as e:
        logger.error(f"Redis get error: {e}")
        return None

def set_cache(key: str, value: Any, ttl: Optional[int] = None):
    """Set data in Redis with optional TTL"""
    try:
        redis_client.set(key, json.dumps(value), ex=ttl)
    except Exception as e:
        logger.error(f"Redis set error: {e}")