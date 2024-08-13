from typing import Union

from pydantic import BaseModel

from ..config.storage import RedisConfig, StorageConfig
from ..config.storage_type import StorageTypes
from .base import BaseRepository


class RepositoryFactory:
    """
    Factory class to create repository instances based on the storage type.

    This factory is responsible for creating instances of different repository
    implementations depending on the storage type specified in the configuration.
    Supported storage types include Redis and in-memory storage.

    Methods:
        create(config: StorageConfig) -> BaseRepository:
            Creates a repository instance based on the provided storage configuration.

        _create_local_repository(config: StorageConfig) -> BaseRepository:
            Creates an instance of LocalRepository for in-memory storage.

        _create_redis_repository(config: StorageConfig) -> BaseRepository:
            Creates an instance of RedisRepository for Redis-based storage.
    """

    @staticmethod
    def create(config: Union[StorageConfig, RedisConfig, BaseModel]) -> BaseRepository:
        """
        Create a repository instance based on the provided storage configuration.

        Args:
            config (Union[StorageConfig, BaseModel]): The configuration object specifying the storage type.

        Returns:
            BaseRepository: An instance of a repository based on the specified storage type.

        Raises:
            ValueError: If the storage type specified in the config is unknown.

        Examples:
            >>> config = StorageConfig(storage_type=StorageTypes.MEMORY)
            >>> repository = RepositoryFactory.create(config)
            >>> isinstance(repository, LocalRepository)
            True

            >>> config = StorageConfig(storage_type=StorageTypes.REDIS)
            >>> repository = RepositoryFactory.create(config)
            >>> isinstance(repository, RedisRepository)
            True

            >>> config = StorageConfig(storage_type="UNKNOWN_TYPE")
            >>> repository = RepositoryFactory.create(config)
            ValueError: Unknown storage type: UNKNOWN_TYPE, available types: ['redis', 'memory']
        """
        storage_type = config.model_dump().get("storage_type", StorageTypes.MEMORY)
        if storage_type == StorageTypes.REDIS:
            redis_config = RedisConfig(**config.model_dump(exclude=storage_type))
            return RepositoryFactory._create_redis_repository(redis_config)
        elif storage_type == StorageTypes.MEMORY:
            in_memory_config = StorageConfig(**config.model_dump(exclude=storage_type))
            return RepositoryFactory._create_local_repository(in_memory_config)
        else:
            raise ValueError(
                f"Unknown storage type: {storage_type}, available types: {StorageTypes.values()}"
            )

    @staticmethod
    def _create_local_repository(config: StorageConfig) -> BaseRepository:
        """
        Create an instance of LocalRepository for in-memory storage.

        Args:
            config (StorageConfig): The configuration object specifying the storage type.

        Returns:
            BaseRepository: An instance of LocalRepository.
        """
        from .local import LocalRepository

        return LocalRepository(config)

    @staticmethod
    def _create_redis_repository(
        config: RedisConfig,
    ) -> BaseRepository:
        """
        Create an instance of RedisRepository for Redis-based storage.

        Args:
            config (RedisConfig): The configuration object specifying the storage type.

        Returns:
            BaseRepository: An instance of RedisRepository.
        """
        from .redis import RedisRepository

        return RedisRepository(config)


__all__ = ["RepositoryFactory"]
