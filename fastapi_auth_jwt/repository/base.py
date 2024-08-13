import json
from abc import ABCMeta, abstractmethod
from typing import Any, Dict, Optional, Union

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

        _serialize(value: Union[str, dict]) -> str:
            Serializes a string or dictionary value to a JSON string.

        _deserialize(value: str) -> Union[str, dict]:
            Deserializes a JSON string back to a Python object.
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

    @classmethod
    def _serialize(cls, value: Union[str, dict]) -> str:
        """
        Serialize a string or dictionary value into a JSON string.

        Args:
            value (Union[str, dict]): The value to serialize.

        Returns:
            str: The serialized JSON string.

        Raises:
            TypeError: If the value is not a string or dictionary.

        Examples:
            >>> BaseRepository._serialize({"key": "value"})
            '{"key": "value"}'

            >>> BaseRepository._serialize("simple string")
            'simple string'

            >>> BaseRepository._serialize(123)  # Raises TypeError
        """
        if isinstance(value, str):
            return value
        if isinstance(value, dict):
            return json.dumps(value)
        raise TypeError(f"Invalid value type: {type(value)}")

    @classmethod
    def _deserialize(cls, value: str) -> Union[str, dict]:
        """
        Deserialize a JSON string back into a Python object.

        Args:
            value (str): The JSON string to deserialize.

        Returns:
            Union[str, dict]: The deserialized object, either a string or dictionary.

        Raises:
            json.JSONDecodeError: If the string cannot be decoded as JSON.
            TypeError: If the value is not a valid string.

        Examples:
            >>> BaseRepository._deserialize('{"key": "value"}')
            {'key': 'value'}

            >>> BaseRepository._deserialize("simple string")
            'simple string'

            >>> BaseRepository._deserialize("invalid json")  # Returns the original string
            'invalid json'
        """
        try:
            return json.loads(value)
        except (json.JSONDecodeError, TypeError):
            return value


__all__ = ["BaseRepository"]
