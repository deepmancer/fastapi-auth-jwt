# config/storage_type.py

from enum import Enum
from typing import List


class StorageTypes(str, Enum):
    """
    An enumeration of supported storage types for session management.

    Attributes:
        REDIS (str): Utilizes a Redis database to store session data, suitable for distributed systems.
        MEMORY (str): Utilizes an in-memory dictionary to store session data, suitable for single-instance applications.
    """

    REDIS = "redis"
    MEMORY = "memory"

    @classmethod
    def values(cls) -> List[str]:
        """
        Returns a list of storage type values.

        This class method retrieves the string values associated with each
        storage type in the enumeration. This can be useful for validation
        or configuration purposes where a list of available storage types is required.

        Returns:
            List[str]: A list containing the string values of the defined storage types.
        """
        return [storage_type.value for storage_type in cls]


__all__ = ["StorageTypes"]
