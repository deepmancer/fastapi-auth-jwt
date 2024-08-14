from typing import Optional

import pytest
from pydantic import BaseModel, ConfigDict

from fastapi_auth_jwt.backend import JWTAuthBackend
from fastapi_auth_jwt.config.auth_token import AuthConfig
from fastapi_auth_jwt.config.storage import RedisConfig, StorageConfig
from tests.test_doubles.time import TimeProvider

MOCKED_TIMESTAMP = 1704067200  # 2024, January 1


class MockUser(BaseModel):
    model_config = ConfigDict(
        populate_by_name=True,
        extra="allow",
        arbitrary_types_allowed=True,
    )


@pytest.fixture(scope="function")
def auth_config():
    return AuthConfig(secret="mysecret", algorithm="HS256")


@pytest.fixture(scope="function")
def storage_config():
    return StorageConfig()


# fixture for redis storage config
@pytest.fixture(scope="function")
def redis_storage_config():
    return RedisConfig(
        host="localhost",
        port=6379,
        db=0,
        password=None,
        username=None,
    )


@pytest.fixture(scope="function")
def jwt_auth_backend(auth_config, storage_config):
    return JWTAuthBackend(
        authentication_config=auth_config,
        storage_config=storage_config,
        user_schema=MockUser,
    )


@pytest.fixture(scope="function")
def time_machine():
    provider = TimeProvider(timestamp=MOCKED_TIMESTAMP)
    provider.start()
    yield provider
    provider.stop()
