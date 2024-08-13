from unittest.mock import patch

import jwt
import pytest
from pydantic import BaseModel

from fastapi_auth_jwt.backend import JWTAuthBackend
from fastapi_auth_jwt.config.auth_token import AuthConfig
from fastapi_auth_jwt.config.storage import StorageConfig


class MockUser(BaseModel):
    user_id: int
    username: str


@pytest.fixture(scope="function")
def auth_config():
    return AuthConfig(secret="mysecret", algorithm="HS256")


@pytest.fixture(scope="function")
def storage_config():
    return StorageConfig()


@pytest.fixture(scope="function")
def jwt_auth_backend(auth_config, storage_config):
    return JWTAuthBackend(
        authentication_config=auth_config,
        storage_config=storage_config,
        user_schema=MockUser,
    )


@pytest.mark.asyncio
async def test_singleton_instance(jwt_auth_backend):
    # Ensure singleton behavior
    instance_1 = JWTAuthBackend.get_instance()
    instance_2 = JWTAuthBackend.get_instance()
    assert instance_1 is instance_2
    assert instance_1 is not None


@pytest.mark.asyncio
async def test_create_token(jwt_auth_backend):
    payload = {"user_id": 1, "username": "john_doe"}
    token = await jwt_auth_backend.create_token(payload, expiration=3600)
    assert isinstance(token, str)


@pytest.mark.asyncio
async def test_authenticate_with_valid_token(jwt_auth_backend):
    payload = {"user_id": 1, "username": "john_doe"}
    token = await jwt_auth_backend.create_token(payload, expiration=3600)

    with patch.object(
        JWTAuthBackend,
        "get_current_user",
        return_value=MockUser(user_id=1, username="john_doe"),
    ) as mock_get_current_user:
        user = await jwt_auth_backend.authenticate(token)
        assert user.user_id == 1
        assert user.username == "john_doe"
        mock_get_current_user.assert_called_once_with(token)


@pytest.mark.asyncio
async def test_authenticate_with_invalid_token(jwt_auth_backend):
    with pytest.raises(jwt.InvalidTokenError):
        await jwt_auth_backend.authenticate("invalid_token")


@pytest.mark.asyncio
async def test_authenticate_with_expired_token(jwt_auth_backend, time_machine):
    payload = {"user_id": 1, "username": "john_doe"}
    token = await jwt_auth_backend.create_token(payload, expiration=1)

    time_machine.advance_time(2)

    with pytest.raises(jwt.ExpiredSignatureError):
        await jwt_auth_backend.authenticate(token)


@pytest.mark.asyncio
async def test_invalidate_token(jwt_auth_backend):
    payload = {"user_id": 1, "username": "john_doe"}
    token = await jwt_auth_backend.create_token(payload, expiration=3600)

    await jwt_auth_backend.invalidate_token(token)

    # Try to get the user with the invalidated token, should return None
    with patch.object(jwt_auth_backend.cache, "get", return_value=None):
        user = await jwt_auth_backend.get_current_user(token)
        assert user is None


@pytest.mark.asyncio
async def test_get_current_user_with_valid_token(jwt_auth_backend):
    payload = {"user_id": 1, "username": "john_doe"}
    token = await jwt_auth_backend.create_token(payload, expiration=3600)

    with patch.object(jwt_auth_backend.cache, "get", return_value=payload):
        user = await jwt_auth_backend.get_current_user(token)
        assert user.user_id == 1
        assert user.username == "john_doe"


@pytest.mark.asyncio
async def test_get_current_user_with_invalid_token(jwt_auth_backend):
    with pytest.raises(jwt.InvalidTokenError):
        await jwt_auth_backend.get_current_user("invalid_token")


@pytest.mark.asyncio
async def test_create_token_with_expiration_candidates(jwt_auth_backend):
    payload = {"user_id": 1, "username": "john_doe"}
    token = await jwt_auth_backend.create_token(payload)
    assert isinstance(token, str)


@pytest.mark.asyncio
async def test_handle_cache_failure_during_token_creation(jwt_auth_backend):
    payload = {"user_id": 1, "username": "john_doe"}

    with patch.object(
        jwt_auth_backend.cache, "set", side_effect=Exception("Cache error")
    ):
        with pytest.raises(Exception) as exc_info:
            await jwt_auth_backend.create_token(payload, expiration=3600)
        assert "Failed to store token in cache" in str(exc_info.value)


@pytest.mark.asyncio
async def test_handle_cache_failure_during_token_invalidation(jwt_auth_backend):
    payload = {"user_id": 1, "username": "john_doe"}
    token = await jwt_auth_backend.create_token(payload, expiration=3600)

    with patch.object(
        jwt_auth_backend.cache, "delete", side_effect=Exception("Cache error")
    ):
        with pytest.raises(Exception) as exc_info:
            await jwt_auth_backend.invalidate_token(token)
            assert "Cache error" in str(exc_info.value)


@pytest.mark.asyncio
async def test_handle_cache_failure_during_get_current_user(jwt_auth_backend):
    payload = {"user_id": 1, "username": "john_doe"}
    token = await jwt_auth_backend.create_token(payload, expiration=3600)

    with patch.object(
        jwt_auth_backend.cache, "get", side_effect=Exception("Cache error")
    ):
        with pytest.raises(Exception) as exc_info:
            await jwt_auth_backend.get_current_user(token)
            assert "Failed to retrieve token from cache" in str(exc_info.value)


@pytest.mark.asyncio
async def test_handle_token_payload_mismatch(jwt_auth_backend):
    payload = {"user_id": 1, "username": "john_doe"}
    token = await jwt_auth_backend.create_token(payload, expiration=3600)

    with patch.object(
        jwt_auth_backend.cache,
        "get",
        return_value={"user_id": 1, "username": "jane_doe"},
    ):
        with pytest.raises(jwt.InvalidTokenError):
            await jwt_auth_backend.get_current_user(token)
