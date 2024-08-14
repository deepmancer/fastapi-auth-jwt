import datetime
from unittest.mock import AsyncMock, patch

import pytest
import pytest_asyncio

from fastapi_auth_jwt.config.storage import RedisConfig
from fastapi_auth_jwt.repository.redis import RedisRepository


@pytest.fixture
def redis_config():
    """Fixture for Redis configuration."""
    config = RedisConfig(
        host="localhost",
        port=6379,
        db=0,
        password=None,
    )
    return config


@pytest.fixture
def redis_mock():
    """Fixture to create a mock Redis instance."""
    mock_redis = AsyncMock()
    return mock_redis


@pytest_asyncio.fixture()
async def redis_repository(redis_config, redis_mock):
    """Fixture to create a RedisRepository instance with a mocked Redis client."""
    with patch(
        "fastapi_auth_jwt.repository.redis.Redis.from_url", return_value=redis_mock
    ):
        repo = RedisRepository(config=redis_config)
        repo._redis = redis_mock
        yield repo


@pytest.mark.asyncio
async def test_get_existing_key(redis_repository, redis_mock):
    """Test getting an existing key from Redis."""
    key = "test_key"
    expected_value = "test_value"

    # Mock the get method of the Redis client
    redis_mock.get.return_value = expected_value.encode("utf-8")
    value = await redis_repository.get(key)

    redis_mock.get.assert_awaited_once_with(key)
    assert value == expected_value


@pytest.mark.asyncio
async def test_get_nonexistent_key(redis_repository, redis_mock):
    """Test getting a non-existent key from Redis."""
    key = "nonexistent_key"

    # Mock the get method to return None
    redis_mock.get.return_value = None

    value = await redis_repository.get(key)

    redis_mock.get.assert_awaited_once_with(key)
    assert value is None


@pytest.mark.asyncio
async def test_set_key(redis_repository, redis_mock):
    """Test setting a key in Redis."""
    key = "test_key"
    value = "test_value"
    expiration = 60

    await redis_repository.set(key, value, expiration)

    redis_mock.set.assert_awaited_once_with(key, value, ex=expiration)


@pytest.mark.asyncio
async def test_set_key_with_timedelta_expiration(redis_repository, redis_mock):
    """Test setting a key with a datetime.timedelta expiration in Redis."""
    key = "test_key"
    value = "test_value"
    expiration = datetime.timedelta(seconds=120)

    await redis_repository.set(key, value, expiration)

    redis_mock.set.assert_awaited_once_with(key, value, ex=120)


@pytest.mark.asyncio
async def test_delete_key(redis_repository, redis_mock):
    """Test deleting a key from Redis."""
    key = "test_key"

    await redis_repository.delete(key)

    redis_mock.delete.assert_awaited_once_with(key)


def test_singleton_behavior(redis_repository):
    """Test that the RedisRepository is a singleton."""
    repo1 = redis_repository
    repo2 = redis_repository

    assert repo1 is repo2
    assert repo1._redis is repo2._redis


@pytest.mark.asyncio
async def test_redis_connection_failure(redis_config):
    """Test that a RedisRepository raises an exception when the connection fails."""
    with patch(
        "fastapi_auth_jwt.repository.redis.Redis.from_url",
        side_effect=Exception("Connection error"),
    ):
        with pytest.raises(Exception) as exc_info:
            RedisRepository(config=redis_config)

            assert "Connection error" in str(exc_info.value)


@pytest.mark.asyncio
async def test_get_existing_key_returns_value(redis_repository, redis_mock):
    """Test that get() returns the value for an existing key from Redis."""
    key = "test_key"
    expected_value = "test_value"

    # Mock the get method of the Redis client
    redis_mock.get.return_value = expected_value.encode("utf-8")
    value = await redis_repository.get(key)

    redis_mock.get.assert_awaited_once_with(key)
    assert value == expected_value


@pytest.mark.asyncio
async def test_get_nonexistent_key_returns_none(redis_repository, redis_mock):
    """Test that get() returns None for a non-existent key from Redis."""
    key = "nonexistent_key"

    # Mock the get method to return None
    redis_mock.get.return_value = None

    value = await redis_repository.get(key)

    redis_mock.get.assert_awaited_once_with(key)
    assert value is None


@pytest.mark.asyncio
async def test_set_key_with_expiration(redis_repository, redis_mock):
    """Test setting a key with an expiration in Redis."""
    key = "test_key"
    value = "test_value"
    expiration = 60

    await redis_repository.set(key, value, expiration)

    redis_mock.set.assert_awaited_once_with(key, value, ex=expiration)


@pytest.mark.asyncio
async def test_set_key_without_expiration(redis_repository, redis_mock):
    """Test setting a key without an expiration in Redis."""
    key = "test_key"
    value = "test_value"

    await redis_repository.set(key, value)

    redis_mock.set.assert_awaited_once_with(key, value)


@pytest.mark.asyncio
async def test_delete_existing_key(redis_repository, redis_mock):
    """Test deleting an existing key from Redis."""
    key = "test_key"

    await redis_repository.delete(key)

    redis_mock.delete.assert_awaited_once_with(key)


@pytest.mark.asyncio
async def test_delete_nonexistent_key(redis_repository, redis_mock):
    """Test deleting a non-existent key from Redis."""
    key = "nonexistent_key"

    await redis_repository.delete(key)

    redis_mock.delete.assert_awaited_once_with(key)


def test_redis_singleton_behavior(redis_repository):
    """Test that the RedisRepository is a singleton."""
    repo1 = redis_repository
    repo2 = redis_repository

    assert repo1 is repo2
    assert repo1._redis is repo2._redis
