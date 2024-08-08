import json
from datetime import timedelta

import pytest

from fastapi_auth_jwt.repository.base import BaseRepository


@pytest.fixture
def base_repository():
    return BaseRepository()


def test_cast_expiration_none():
    expiration = None
    result = BaseRepository._cast_expiration(expiration)
    assert result is None


def test_cast_expiration_integer():
    expiration = 60
    result = BaseRepository._cast_expiration(expiration)
    assert result == expiration


def test_cast_expiration_float():
    expiration = 60.5
    result = BaseRepository._cast_expiration(expiration)
    assert result == int(expiration)


def test_cast_expiration_timedelta():
    expiration = timedelta(minutes=1)
    result = BaseRepository._cast_expiration(expiration)
    assert result == expiration.total_seconds()


def test_cast_expiration_invalid():
    expiration = "invalid"

    with pytest.raises(TypeError):
        BaseRepository._cast_expiration(expiration)

    expiration = [60]

    with pytest.raises(TypeError):
        BaseRepository._cast_expiration(expiration)


def test_base_error_on_instantiation():
    with pytest.raises(TypeError):
        BaseRepository()

        def test_serialize_string():
            value = "test"
            result = BaseRepository._serialize(value)
            assert result == value


def test_serialize_dict():
    value = {"key": "value"}
    result = BaseRepository._serialize(value)
    assert result == json.dumps(value)


def test_serialize_invalid():
    value = 123

    with pytest.raises(TypeError):
        BaseRepository._serialize(value)


def test_deserialize_string():
    value = "test"
    result = BaseRepository._deserialize(value)
    assert result == value


def test_deserialize_dict():
    value = '{"key": "value"}'
    result = BaseRepository._deserialize(value)
    assert result == json.loads(value)
