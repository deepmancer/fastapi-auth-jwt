from datetime import timedelta

import pytest

from fastapi_auth_jwt.utils.time_helpers import cast_to_seconds


def test_cast_expiration_none():
    expiration = None
    result = cast_to_seconds(expiration)
    assert result is None


def test_cast_expiration_integer():
    expiration = 60
    result = cast_to_seconds(expiration)
    assert result == expiration


def test_cast_expiration_float():
    expiration = 60.5
    result = cast_to_seconds(expiration)
    assert result == int(expiration)


def test_cast_expiration_timedelta():
    expiration = timedelta(minutes=1)
    result = cast_to_seconds(expiration)
    assert result == expiration.total_seconds()


def test_cast_expiration_invalid():
    expiration = "invalid"

    with pytest.raises(TypeError):
        cast_to_seconds(expiration)

    expiration = [60]

    with pytest.raises(TypeError):
        cast_to_seconds(expiration)
