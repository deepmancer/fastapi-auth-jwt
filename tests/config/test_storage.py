from fastapi_auth_jwt.config.storage import RedisConfig


def test_redis_config_get_url_with_password():
    config = RedisConfig(password="password")
    expected_url = "redis://:password@localhost:6379/0"
    assert config.get_url() == expected_url


def test_redis_config_get_url_without_password():
    config = RedisConfig()
    expected_url = "redis://localhost:6379/0"
    assert config.get_url() == expected_url


def test_redis_config_get_url_with_custom_url():
    config = RedisConfig(url="redis://custom-url")
    expected_url = "redis://custom-url"
    assert config.get_url() == expected_url


def test_redis_config_get_url_with_password_and_custom_url():
    config = RedisConfig(password="password", url="redis://custom-url")
    expected_url = "redis://custom-url"
    assert config.get_url() == expected_url


def test_redis_config_get_url_without_password_and_custom_url():
    config = RedisConfig(url="redis://custom-url")
    expected_url = "redis://custom-url"
    assert config.get_url() == expected_url
