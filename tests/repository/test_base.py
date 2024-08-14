import pytest

from fastapi_auth_jwt.repository.base import BaseRepository


def test_base_instantiation_raises_error():
    with pytest.raises(TypeError):
        BaseRepository()
