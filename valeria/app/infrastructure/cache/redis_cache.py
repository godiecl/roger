"""
Redis cache implementation for ROGER - Valeria API
"""

import json
from typing import Optional, Any
import redis.asyncio as redis

from app.infrastructure.cache.base_cache import BaseCache
from app.config.settings import settings


class RedisCache(BaseCache):
    """Redis cache implementation."""
    
    def __init__(self):
        self.redis: Optional[redis.Redis] = None
        self.default_ttl = settings.redis_cache_ttl
    
    async def connect(self):
        """Connect to Redis."""
        self.redis = await redis.from_url(
            settings.redis_url,
            encoding="utf-8",
            decode_responses=True
        )
    
    async def disconnect(self):
        """Disconnect from Redis."""
        if self.redis:
            await self.redis.close()
    
    async def get(self, key: str) -> Optional[Any]:
        """Get value from Redis cache."""
        if not self.redis:
            await self.connect()
        
        value = await self.redis.get(key)
        if value:
            try:
                return json.loads(value)
            except json.JSONDecodeError:
                return value
        return None
    
    async def set(self, key: str, value: Any, ttl: Optional[int] = None) -> bool:
        """Set value in Redis cache."""
        if not self.redis:
            await self.connect()
        
        # Serialize value to JSON
        serialized = json.dumps(value) if not isinstance(value, str) else value
        
        # Use default TTL if not provided
        expire_time = ttl if ttl is not None else self.default_ttl
        
        await self.redis.set(key, serialized, ex=expire_time)
        return True
    
    async def delete(self, key: str) -> bool:
        """Delete key from Redis cache."""
        if not self.redis:
            await self.connect()
        
        result = await self.redis.delete(key)
        return result > 0
    
    async def exists(self, key: str) -> bool:
        """Check if key exists in Redis cache."""
        if not self.redis:
            await self.connect()
        
        return await self.redis.exists(key) > 0
    
    async def clear(self) -> bool:
        """Clear all Redis cache entries."""
        if not self.redis:
            await self.connect()
        
        await self.redis.flushdb()
        return True


# Global cache instance
cache = RedisCache()
