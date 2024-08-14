from typing import Any, Optional

from redis.asyncio import Redis

from ..config.storage import RedisConfig
from ..config.types import EXPIRATION_DTYPE
from ..utils.time_helpers import cast_to_seconds
from .base import BaseRepository


class RedisRepository(BaseRepository):
    """
    Repository implementation using Redis with asynchronous capabilities.

    This class provides an interface to interact with Redis as a key-value store.
    It allows storing, retrieving, and deleting values asynchronously, with support
    for optional expiration times.

    Attributes:
        _config (RedisConfig): Configuration object for connecting to Redis.
        _redis (Redis): Redis client instance used for interacting with the Redis database.
    """

    def __init__(self, config: RedisConfig):
        """
        Initialize the RedisRepository with a given configuration.

        Args:
            config (RedisConfig): The configuration object containing Redis connection details.
        """
        self._config: RedisConfig = config
        self._redis: Redis = Redis.from_url(
            self._config.get_url(), decode_responses=True
        )

    @property
    def redis(self) -> Redis:
        """
        Get the Redis client instance.

        Returns:
            Redis: The Redis client instance used for interacting with the Redis database.
        """
        return self._redis

    @property
    def config(self) -> RedisConfig:
        """
        Get the current configuration of the repository.

        Returns:
            RedisConfig: The configuration object for the repository.
        """
        return self._config

    async def get(self, key: str) -> Optional[Any]:
        """
        Retrieve a value from the Redis store by its key.

        Args:
            key (str): The key for the value to retrieve.

        Returns:
            Optional[Any]: The value associated with the key, or None if the key is not found.

        Examples:
            >>> config = RedisConfig(host="localhost", port=6379, db=0)
            >>> repo = RedisRepository(config)
            >>> await repo.set("sample_key", "sample_value")
            >>> value = await repo.get("sample_key")
            >>> print(value)
            'sample_value'
        """
        value = await self._redis.get(key)
        if value is not None:
            return value.decode("utf-8")
        return value

    async def set(
        self,
        key: str,
        value: str,
        expiration: Optional[EXPIRATION_DTYPE] = None,
    ) -> None:
        """
        Store a value in the Redis store with an optional expiration time.

        Args:
            key (str): The key to associate with the value.
            value (str): The value to store.
            expiration (Optional[Union[int, float, datetime.timedelta]]): Optional expiration time
                for the key in seconds or as a timedelta. If not provided, the key will not expire.

        Returns:
            None

        Examples:
            >>> config = RedisConfig(host="localhost", port=6379, db=0)
            >>> repo = RedisRepository(config)
            >>> await repo.set("temp_key", "temp_value", expiration=60)
            # The value will expire after 60 seconds.
        """
        casted_expiration = cast_to_seconds(expiration)
        if casted_expiration:
            await self._redis.set(key, value, ex=casted_expiration)
        else:
            await self._redis.set(key, value)

    async def delete(self, key: str) -> None:
        """
        Delete a value from the Redis store by its key.

        Args:
            key (str): The key for the value to delete.

        Returns:
            None

        Examples:
            >>> config = RedisConfig(host="localhost", port=6379, db=0)
            >>> repo = RedisRepository(config)
            >>> await repo.set("delete_key", "delete_value")
            >>> await repo.delete("delete_key")
            >>> value = await repo.get("delete_key")
            >>> print(value)
            None  # The value has been deleted.
        """
        await self._redis.delete(key)


__all__ = ["RedisRepository"]
