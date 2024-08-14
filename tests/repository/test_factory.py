import pydantic
import pytest

from fastapi_auth_jwt.config.storage import RedisConfig, StorageConfig
from fastapi_auth_jwt.config.storage_type import StorageTypes
from fastapi_auth_jwt.repository.base import BaseRepository
from fastapi_auth_jwt.repository.factory import RepositoryFactory
from fastapi_auth_jwt.repository.local import LocalRepository
from fastapi_auth_jwt.repository.redis import RedisRepository


def test_create_local_repository():
    config = StorageConfig()
    repository = RepositoryFactory._create_local_repository(config)
    assert isinstance(repository, BaseRepository)
    assert isinstance(repository, LocalRepository)


def test_create_redis_repository():
    config = RedisConfig()
    repository = RepositoryFactory._create_redis_repository(config)
    assert isinstance(repository, BaseRepository)
    assert isinstance(repository, RedisRepository)


def test_create_unknown_storage_type():
    with pytest.raises(pydantic.ValidationError):
        config = StorageConfig(storage_type="unknown")
        RepositoryFactory.create(config)


def test_create_local_repository_from_custom_config():
    config = StorageConfig(
        storage_type=StorageTypes.MEMORY,
        pop_up_message="Hello, World!",
    )
    repository = RepositoryFactory._create_local_repository(config)
    assert isinstance(repository, BaseRepository)
    assert isinstance(repository, LocalRepository)


def test_create_repository_with_memory_storage():
    config = StorageConfig(storage_type=StorageTypes.MEMORY)
    repository = RepositoryFactory.create(config)
    assert isinstance(repository, BaseRepository)
    assert isinstance(repository, LocalRepository)


def test_create_repository_with_redis_storage():
    config = RedisConfig(storage_type=StorageTypes.REDIS)
    repository = RepositoryFactory.create(config)
    assert isinstance(repository, BaseRepository)
    assert isinstance(repository, RedisRepository)


def test_create_repository_with_invalid_storage_type():
    class CustomStorageConfig(pydantic.BaseModel):
        storage_type: str = "INVALID_TYPE"

    config = CustomStorageConfig()
    with pytest.raises(ValueError, match="Unknown storage type: INVALID_TYPE"):
        RepositoryFactory.create(config)
