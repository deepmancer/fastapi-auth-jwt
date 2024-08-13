from datetime import datetime, timedelta
from typing import Any, Dict, Optional

from ..config.storage import StorageConfig
from ..config.types import EXPIRATION_DTYPE
from ..utils.time_helpers import cast_to_seconds
from .base import BaseRepository


class LocalRepository(BaseRepository):
    """
    Repository implementation using a local in-memory dictionary.

    This class provides a simple key-value store backed by a dictionary for local
    data storage. It supports storing values with optional expiration times and
    allows retrieving and deleting stored values.

    Attributes:
        _store (Dict[str, Any]): The dictionary that stores key-value pairs.
        _expirations (Dict[str, datetime]): A dictionary that keeps track of expiration times for keys.
        _config (StorageConfig): Configuration object for the repository.
    """

    def __init__(self, config: StorageConfig):
        """
        Initialize the LocalRepository with a given configuration.

        Args:
            config (StorageConfig): The configuration object for the repository.
        """
        self._store: Dict[str, Any] = {}
        self._expirations: Dict[str, datetime] = {}
        self._config: StorageConfig = config

    @property
    def config(self) -> StorageConfig:
        """
        Get the current configuration of the repository.

        Returns:
            StorageConfig: The configuration object for the repository.
        """
        return self._config

    @config.setter
    def config(self, config: StorageConfig) -> None:
        """
        Set a new configuration for the repository.

        Args:
            config (StorageConfig): The new configuration object to set.
        """
        self._config = config

    async def get(self, key: str) -> Optional[Any]:
        """
        Retrieve a value from the repository by its key.

        If the key has an associated expiration and it has expired, the key will be deleted
        and None will be returned.

        Args:
            key (str): The key for the value to retrieve.

        Returns:
            Optional[Any]: The value associated with the key, or None if the key is not found
            or has expired.

        Examples:
            >>> config = StorageConfig()
            >>> repo = LocalRepository(config)
            >>> await repo.set("key1", "value1")
            >>> value = await repo.get("key1")
            >>> print(value)
            'value1'

            >>> # Simulating an expired key
            >>> await repo.set("key2", "value2", expiration=1)
            >>> await asyncio.sleep(2)  # Wait for the key to expire
            >>> expired_value = await repo.get("key2")
            >>> print(expired_value)
            None  # The key has expired and is deleted.
        """
        if key in self._expirations and datetime.now() > self._expirations[key]:
            await self.delete(key)
            return None
        return self._store.get(key)

    async def set(
        self,
        key: str,
        value: Any,
        expiration: Optional[EXPIRATION_DTYPE] = None,
    ) -> None:
        """
        Store a value in the repository with an optional expiration time.

        Args:
            key (str): The key to associate with the value.
            value (Any): The value to store.
            expiration (Optional[Union[int, float, datetime.timedelta]]): Optional expiration time
                for the key in seconds or as a timedelta. If not provided, the key will not expire.

        Returns:
            None

        Examples:
            >>> config = StorageConfig()
            >>> repo = LocalRepository(config)
            >>> await repo.set("temp_key", "temp_value", expiration=60)
            >>> # The value will expire after 60 seconds.
        """
        self._store[key] = value
        casted_expiration = cast_to_seconds(expiration)
        if casted_expiration:
            self._expirations[key] = datetime.now() + timedelta(
                seconds=casted_expiration
            )

    async def delete(self, key: str) -> None:
        """
        Delete a value from the repository by its key.

        Args:
            key (str): The key for the value to delete.

        Returns:
            None

        Examples:
            >>> config = StorageConfig()
            >>> repo = LocalRepository(config)
            >>> await repo.set("delete_key", "delete_value")
            >>> await repo.delete("delete_key")
            >>> value = await repo.get("delete_key")
            >>> print(value)
            None  # The value has been deleted.
        """
        self._store.pop(key, None)
        self._expirations.pop(key, None)


__all__ = ["LocalRepository"]
