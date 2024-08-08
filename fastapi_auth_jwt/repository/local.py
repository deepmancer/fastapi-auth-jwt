from datetime import datetime, timedelta
from typing import Any, Optional, Union

from ..config import StorageConfig
from .base import BaseRepository


class LocalRepository(BaseRepository):
    """Repository implementation using a local dictionary."""

    def __init__(self, config: StorageConfig):
        self._store = {}
        self._expirations = {}
        self._config = config

    @property
    def config(self) -> StorageConfig:
        return self._config

    @config.setter
    def config(self, config: StorageConfig):
        self._config = config

    async def get(self, key: str) -> Optional[Any]:
        if key in self._expirations and datetime.now() > self._expirations[key]:
            await self.delete(key)
            return None
        return self._store.get(key)

    async def set(
        self,
        key: str,
        value: Any,
        expiration: Optional[Union[int, float, timedelta]] = None,
    ) -> None:
        self._store[key] = value
        if expiration:
            self._expirations[key] = datetime.now() + timedelta(seconds=self._cast_expiration(expiration))

    async def delete(self, key: str) -> None:
        self._store.pop(key, None)
        self._expirations.pop(key, None)


__all__ = ["LocalRepository"]
