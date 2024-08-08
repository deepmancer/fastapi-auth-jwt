from ..config import StorageConfig, StorageTypes
from .base import BaseRepository


class RepositoryFactory:
    """Factory class to create repository instances."""

    @staticmethod
    def create(
        config: StorageConfig,
    ) -> BaseRepository:
        storage_type = config.storage_type
        if storage_type == StorageTypes.REDIS:
            return RepositoryFactory._create_redis_repository(config)
        elif storage_type == StorageTypes.MEMORY:
            return RepositoryFactory._create_local_repository(config)
        else:
            raise ValueError(f"Unknown storage type: {storage_type}, available types: {StorageTypes.values()}")

    @staticmethod
    def _create_local_repository(config: StorageConfig) -> BaseRepository:
        from .local import LocalRepository

        return LocalRepository(config)

    @staticmethod
    def _create_redis_repository(config: StorageConfig) -> BaseRepository:
        from .redis import RedisRepository

        return RedisRepository(config)


__all__ = ["RepositoryFactory"]
