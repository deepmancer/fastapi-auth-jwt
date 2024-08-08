from fastapi_auth_jwt.config.storage_type import StorageTypes


def test_storage_types_values():
    expected_values = ["redis", "memory"]
    assert StorageTypes.values() == expected_values
