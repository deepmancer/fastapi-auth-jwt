from datetime import datetime, timedelta

import jwt
import pytest

from fastapi_auth_jwt.utils.jwt_token import JWTHandler


@pytest.fixture(scope="function")
def jwt_handler():
    secret = "mysecret"
    return JWTHandler(secret)


def test_encode(jwt_handler):
    payload = {"user_id": 1, "username": "john_doe"}
    expiration = 3600
    token = jwt_handler.encode(payload, expiration)
    assert isinstance(token, str)


def test_decode(jwt_handler):
    payload = {"user_id": 1, "username": "john_doe"}
    expiration = 3600
    token = jwt_handler.encode(payload, expiration)
    decoded = jwt_handler.decode(token)
    assert isinstance(decoded, dict)
    assert decoded["user_id"] == payload["user_id"]
    assert decoded["username"] == payload["username"]


def test_decode_with_expired_token(jwt_handler, time_machine):
    payload = {"user_id": 1, "username": "john_doe"}
    expiration = 1
    token = jwt_handler.encode(payload, expiration)

    time_machine.advance_time(2)

    with pytest.raises(jwt.ExpiredSignatureError):
        jwt_handler.decode(token)


def test_decode_with_invalid_signature(jwt_handler):
    payload = {"user_id": 1, "username": "john_doe"}
    expiration = 3600
    token = jwt_handler.encode(payload, expiration)

    modified_token = token + "invalid"
    with pytest.raises(jwt.InvalidSignatureError):
        jwt_handler.decode(modified_token)


def test_encode_with_different_data_types(jwt_handler):
    payload = {
        "string": "Hello, World!",
        "integer": 12345,
        "float": 3.14,
        "boolean": True,
        "list": [1, 2, 3],
        "dictionary": {"key": "value"},
        "null": None,
    }
    expiration = 3600
    token = jwt_handler.encode(payload, expiration)
    assert isinstance(token, str)


def test_decode_with_different_data_types(jwt_handler):
    payload = {
        "string": "Hello, World!",
        "integer": 12345,
        "float": 3.14,
        "boolean": True,
        "list": [1, 2, 3],
        "dictionary": {"key": "value"},
        "null": None,
    }
    expiration = 3600
    token = jwt_handler.encode(payload, expiration)
    decoded = jwt_handler.decode(token)
    assert isinstance(decoded, dict)
    assert decoded["string"] == payload["string"]
    assert decoded["integer"] == payload["integer"]
    assert decoded["float"] == payload["float"]
    assert decoded["boolean"] == payload["boolean"]
    assert decoded["list"] == payload["list"]
    assert decoded["dictionary"] == payload["dictionary"]
    assert decoded["null"] == payload["null"]


def test_encode_without_expiration(jwt_handler):
    payload = {"user_id": 1, "username": "john_doe"}
    token = jwt_handler.encode(payload)
    decoded = jwt_handler.decode(token)
    assert isinstance(decoded, dict)
    assert decoded["user_id"] == payload["user_id"]
    assert decoded["username"] == payload["username"]
    assert "exp" not in decoded


def test_decode_with_missing_claim(jwt_handler):
    payload = {"user_id": 1, "username": "john_doe"}
    expiration = 3600
    token = jwt_handler.encode(payload, expiration)

    with pytest.raises(jwt.MissingRequiredClaimError):
        jwt_handler.decode(token, options={"require": ["email"]})


def test_decode_with_different_algorithm(jwt_handler):
    payload = {"user_id": 1, "username": "john_doe"}
    expiration = 3600
    token = jwt_handler.encode(payload, expiration)

    jwt_handler_different_algo = JWTHandler(secret="mysecret", algorithm="HS384")

    with pytest.raises(jwt.InvalidAlgorithmError):
        jwt_handler_different_algo.decode(token)


def test_decode_with_verification_disabled(jwt_handler):
    payload = {"user_id": 1, "username": "john_doe"}
    expiration = 3600
    token = jwt_handler.encode(payload, expiration)

    decoded = jwt_handler.decode(token, options={"verify_signature": False})
    assert isinstance(decoded, dict)
    assert decoded["user_id"] == payload["user_id"]
    assert decoded["username"] == payload["username"]


def test_encode_decode_empty_payload(jwt_handler):
    payload = {}
    token = jwt_handler.encode(payload)
    decoded = jwt_handler.decode(token)
    assert isinstance(decoded, dict)
    assert decoded == {}


def test_decode_with_future_token(jwt_handler):
    payload = {"user_id": 1, "username": "john_doe"}
    future_time = datetime.utcnow() + timedelta(hours=1)
    expiration = 3600
    token = jwt_handler.encode(payload, expiration, nbf=future_time)

    with pytest.raises(jwt.ImmatureSignatureError):
        jwt_handler.decode(token)


def test_encode_with_invalid_type(jwt_handler):
    payload = {"user_id": set([1, 2, 3])}  # Sets are not JSON serializable
    with pytest.raises(TypeError):
        jwt_handler.encode(payload)


def test_decode_with_invalid_token(jwt_handler):
    invalid_token = "invalid.token.string"
    with pytest.raises(jwt.DecodeError):
        jwt_handler.decode(invalid_token)


def test_decode_with_unexpected_error(jwt_handler, mocker):
    payload = {"user_id": 1, "username": "john_doe"}
    expiration = 3600
    token = jwt_handler.encode(payload, expiration)

    mocker.patch("jwt.decode", side_effect=Exception("Unexpected error"))
    with pytest.raises(
        Exception,
        match="An unexpected error occurred while decoding the token: Unexpected error",
    ):
        jwt_handler.decode(token)


def test_encode_with_unexpected_error(jwt_handler, mocker):
    payload = {"user_id": 1, "username": "john_doe"}

    mocker.patch("jwt.encode", side_effect=Exception("Unexpected error"))
    with pytest.raises(
        Exception,
        match="An unexpected error occurred while encoding the token: Unexpected error",
    ):
        jwt_handler.encode(payload)
