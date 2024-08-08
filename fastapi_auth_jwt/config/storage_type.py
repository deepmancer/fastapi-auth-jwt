from enum import Enum


class StorageTypes(str, Enum):
    REDIS = "redis"
    MEMORY = "memory"  # Using dictionary to store the data

    @classmethod
    def values(cls):
        return [storage_type.value for storage_type in cls]


__all__ = ["StorageTypes"]
