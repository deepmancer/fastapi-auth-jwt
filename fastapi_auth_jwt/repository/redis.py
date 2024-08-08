from datetime import timedelta
from typing import Any, Optional, Union

from redis.asyncio import Redis

from ..config.storage import RedisConfig
from .base import BaseRepository


class RedisRepository(BaseRepository):
    """Repository implementation using redis-py's async capabilities."""

    def __init__(self, config: RedisConfig):
        self._config = config
        self._redis = Redis.from_url(self._config.get_url(), decode_responses=True)

    @property
    def redis(self) -> Redis:
        return self._redis

    @property
    def config(self) -> RedisConfig:
        return self._config

    async def get(self, key: str) -> Optional[Any]:
        value = await self._redis.get(key)
        if value is not None:
            return value.decode("utf-8")
        return None

    async def set(
        self,
        key: str,
        value: Any,
        expiration: Optional[Union[int, float, timedelta]] = None,
    ) -> None:
        await self._redis.set(key, value, ex=self._cast_expiration(expiration))

    async def delete(self, key: str) -> None:
        await self._redis.delete(key)


__all__ = ["RedisRepository"]
