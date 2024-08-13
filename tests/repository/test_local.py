from datetime import datetime, timedelta

import pytest

from fastapi_auth_jwt.config.storage import StorageConfig
from fastapi_auth_jwt.repository.local import LocalRepository


@pytest.fixture
def local_repository_config() -> StorageConfig:
    return StorageConfig()


@pytest.fixture
def local_repository(local_repository_config):
    return LocalRepository(config=local_repository_config)


@pytest.mark.asyncio
async def test_get_existing_key(local_repository):
    key = "existing_key"
    value = "existing_value"
    local_repository._store[key] = value
    assert await local_repository.get(key) == value


@pytest.mark.asyncio
async def test_get_non_existing_key(local_repository):
    key = "non_existing_key"
    assert await local_repository.get(key) is None


@pytest.mark.asyncio
async def test_get_expired_key(local_repository):
    key = "expired_key"
    value = "expired_value"
    expiration = 1  # 1 second expiration
    local_repository._store[key] = value
    local_repository._expirations[key] = datetime.now() - timedelta(seconds=expiration)
    assert await local_repository.get(key) is None


@pytest.mark.asyncio
async def test_set_without_expiration(local_repository):
    key = "key"
    value = "value"
    await local_repository.set(key, value)
    assert local_repository._store[key] == value
    assert key not in local_repository._expirations


@pytest.mark.asyncio
async def test_set_with_expiration(local_repository):
    key = "key"
    value = "value"
    expiration = 10  # 10 seconds expiration
    await local_repository.set(key, value, expiration)
    assert local_repository._store[key] == value
    assert key in local_repository._expirations
    assert local_repository._expirations[key] > datetime.now()


@pytest.mark.asyncio
async def test_delete_existing_key(local_repository):
    key = "existing_key"
    value = "existing_value"
    local_repository._store[key] = value
    local_repository._expirations[key] = datetime.now() + timedelta(seconds=10)
    await local_repository.delete(key)
    assert key not in local_repository._store
    assert key not in local_repository._expirations


@pytest.mark.asyncio
async def test_delete_non_existing_key(local_repository):
    key = "non_existing_key"
    await local_repository.delete(key)  # Should not raise any exception


@pytest.mark.asyncio
async def test_delete_expired_key(local_repository):
    key = "expired_key"
    value = "expired_value"
    expiration = 1  # 1 second expiration
    local_repository._store[key] = value
    local_repository._expirations[key] = datetime.now() - timedelta(seconds=expiration)
    await local_repository.delete(key)
    assert key not in local_repository._store
    assert key not in local_repository._expirations


@pytest.mark.asyncio
async def test_expiration_with_time_traveling(local_repository, time_machine):
    key = "key"
    value = "value"
    expiration = 10
    await local_repository.set(key, value, expiration)

    # Move the time forward by 5 seconds
    time_machine.advance_time(5)

    assert await local_repository.get(key) == value

    # Move the time forward by 6 seconds
    time_machine.advance_time(6)

    assert await local_repository.get(key) is None
    assert key not in local_repository._store
    assert key not in local_repository._expirations


def test_singleton_behavior(local_repository_config):
    repo1 = LocalRepository(config=local_repository_config)
    repo2 = LocalRepository(config=local_repository_config)
    assert repo1 is repo2
    assert repo1._store is repo2._store
    assert repo1._expirations is repo2._expirations
