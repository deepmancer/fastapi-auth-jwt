import json
from abc import ABCMeta, abstractmethod
from datetime import timedelta
from typing import Any, Optional, Union


class SingletonABCMeta(ABCMeta):
    """A Singleton metaclass that also supports Abstract Base Classes (ABC)."""

    _instances = {}

    def __call__(cls, *args, **kwargs):
        if cls not in cls._instances:
            instance = super().__call__(*args, **kwargs)
            cls._instances[cls] = instance
        return cls._instances[cls]


class BaseRepository(metaclass=SingletonABCMeta):
    """Abstract base class for a repository, now a Singleton and an ABC."""

    @abstractmethod
    async def get(self, key: str) -> Optional[Any]:
        pass

    @abstractmethod
    async def set(self, key: str, value: Any, expiration: Optional[int] = None) -> None:
        pass

    @abstractmethod
    async def delete(self, key: str) -> None:
        pass

    @classmethod
    def _cast_expiration(cls, expiration: Optional[Union[int, float, timedelta]]) -> Optional[int]:
        if expiration is None:
            return None
        if isinstance(expiration, timedelta):
            return expiration.total_seconds()
        elif isinstance(expiration, (int, float)):
            return int(expiration)
        raise TypeError(f"Invalid expiration type: {type(expiration)}")

    @classmethod
    def _serialize(cls, value: Union[str, dict]) -> str:
        if isinstance(value, str):
            return value
        elif isinstance(value, dict):
            return json.dumps(value)
        raise TypeError(f"Invalid value type: {type(value)}")

    @classmethod
    def _deserialize(cls, value: str) -> Union[str, dict]:
        try:
            return json.loads(value)
        except (json.JSONDecodeError, TypeError):
            return value


__all__ = ["BaseRepository"]
