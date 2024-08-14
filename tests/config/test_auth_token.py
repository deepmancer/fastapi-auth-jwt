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


def test_auth_token_config_repr():
    # Test __repr__ method
    config = AuthConfig(
        secret="my_secret", jwt_algorithm="HS512", expiration_seconds=7200
    )
    assert (
        repr(config)
        == "AuthConfig(secret=my_secret, jwt_algorithm=HS512, expiration_seconds=7200, expiration_minutes=120)"
    )


def test_auth_token_config_str():
    # Test __str__ method
    config = AuthConfig(
        secret="my_secret", jwt_algorithm="HS512", expiration_seconds=7200
    )
    assert (
        str(config)
        == "AuthConfig(secret=my_secret, jwt_algorithm=HS512, expiration_seconds=7200, expiration_minutes=120)"
    )
