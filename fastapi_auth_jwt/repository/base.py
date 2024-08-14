from abc import ABCMeta, abstractmethod
from typing import Any, Dict, Optional

from ..config.types import EXPIRATION_DTYPE


class SingletonABCMeta(ABCMeta):
    """
    A Singleton metaclass that also supports Abstract Base Classes (ABC).

    This metaclass ensures that a class following this pattern will have only
    one instance (Singleton) while also being able to define abstract methods
    (as an ABC).
    """

    _instances: Dict[Any, Any] = {}

    def __call__(cls, *args, **kwargs):
        if cls not in cls._instances:
            instance = super().__call__(*args, **kwargs)
            cls._instances[cls] = instance
        return cls._instances[cls]


class BaseRepository(metaclass=SingletonABCMeta):
    """
    Abstract base class for a repository interface, implementing a Singleton pattern.

    This class provides an interface for data storage operations such as get, set,
    and delete. It ensures that derived classes are singletons and can only have one instance.

    Methods:
        get(key: str) -> Optional[Any]:
            Abstract method to retrieve a value by key.

        set(key: str, value: Any, expiration: Optional[Union[int, float, datetime.timedelta]] = None) -> None:
            Abstract method to store a value with an optional expiration.

        delete(key: str) -> None:
            Abstract method to delete a value by key.
    """

    @abstractmethod
    async def get(self, key: str) -> Optional[Any]:
        """
        Retrieve a value from the storage by its key.

        Args:
            key (str): The key for the value to retrieve.

        Returns:
            Optional[Any]: The value associated with the key, or None if not found.
        """
        pass

    @abstractmethod
    async def set(
        self, key: str, value: Any, expiration: Optional[EXPIRATION_DTYPE] = None
    ) -> None:
        """
        Store a value in the storage with an optional expiration time.

        Args:
            key (str): The key to associate with the value.
            value (Any): The value to store.
            expiration (Optional[Union[int, float, datetime.timedelta]]): Time in seconds before the value expires. Defaults to None.

        Returns:
            None
        """
        pass

    @abstractmethod
    async def delete(self, key: str) -> None:
        """
        Delete a value from the storage by its key.

        Args:
            key (str): The key for the value to delete.

        Returns:
            None
        """
        pass


__all__ = ["BaseRepository"]
