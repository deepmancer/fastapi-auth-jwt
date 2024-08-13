import pytest

from fastapi_auth_jwt.config.auth_token import AuthConfig


def test_auth_token_config():
    # Test default values
    config = AuthConfig()
    assert config.secret == "default_secret"
    assert config.jwt_algorithm == "HS256"
    assert config.expiration_seconds == 3600
    assert config.expiration_minutes == 60

    # Test custom values
    config = AuthConfig(
        secret="mysecret", jwt_algorithm="HS512", expiration_seconds=1800
    )
    assert config.secret == "mysecret"
    assert config.jwt_algorithm == "HS512"
    assert config.expiration_seconds == 1800
    assert config.expiration_minutes == 30

    # Test validation
    with pytest.raises(ValueError):
        AuthConfig(expiration_seconds=-1)
