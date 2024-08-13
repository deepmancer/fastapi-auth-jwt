import json

import pytest

from fastapi_auth_jwt.repository.base import BaseRepository


@pytest.fixture
def base_repository():
    return BaseRepository()


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
