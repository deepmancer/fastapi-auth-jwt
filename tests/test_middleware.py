import jwt
import pytest
from fastapi import FastAPI, HTTPException, Request
from fastapi.responses import JSONResponse
from starlette.testclient import TestClient

from fastapi_auth_jwt.backend import JWTAuthBackend
from fastapi_auth_jwt.middleware import JWTAuthenticationMiddleware


@pytest.fixture
def app(jwt_auth_backend):
    app = FastAPI()

    @app.get("/unprotected")
    async def unprotected():
        return {"message": "Unprotected"}

    @app.get("/protected")
    async def protected(request: Request):
        return {"message": f"Protected for {request.state.user['username']}"}

    @app.get("/sync-protected")
    def sync_protected(request: Request):
        return {"message": f"Protected for {request.state.user['username']}"}

    @app.get("/sync-unprotected")
    def sync_unprotected():
        return {"message": "Unprotected"}

    app.add_middleware(
        JWTAuthenticationMiddleware,
        backend=jwt_auth_backend,
        exclude_urls=["/unprotected", "/sync-unprotected"],
    )

    return app


@pytest.fixture
def client(app):
    return TestClient(app)


@pytest.mark.asyncio
async def test_unprotected_route(client):
    response = client.get("/unprotected")
    assert response.status_code == 200
    assert response.json() == {"message": "Unprotected"}


@pytest.mark.asyncio
async def test_protected_route_without_token(client):
    response = client.get("/protected")
    assert response.status_code == 401
    assert response.json()["detail"] == "Authorization header is missing."


@pytest.mark.asyncio
async def test_protected_route_with_invalid_scheme(client):
    headers = {"Authorization": "Basic invalidtoken"}
    response = client.get("/protected", headers=headers)
    assert response.status_code == 400
    assert (
        response.json()["detail"]
        == "Invalid authorization header, expected value in format 'Bearer <token>'."
    )


@pytest.mark.asyncio
async def test_protected_route_with_invalid_token(client, monkeypatch):
    async def mock_authenticate(self, token):
        raise jwt.PyJWTError("Invalid token")

    monkeypatch.setattr(JWTAuthBackend, "authenticate", mock_authenticate)

    headers = {"Authorization": "Bearer invalidtoken"}
    response = client.get("/protected", headers=headers)
    assert response.status_code == 401
    assert response.json()["detail"] == "Could not validate credentials."


@pytest.mark.asyncio
async def test_protected_route_with_missing_claim(client, monkeypatch):
    async def mock_authenticate(self, token):
        raise jwt.MissingRequiredClaimError("exp")

    monkeypatch.setattr(JWTAuthBackend, "authenticate", mock_authenticate)

    headers = {"Authorization": "Bearer validtoken"}
    response = client.get("/protected", headers=headers)
    assert response.status_code == 400
    assert response.json()["detail"] == "Missing required claim."


@pytest.mark.asyncio
async def test_protected_route_with_valid_token(client, monkeypatch):
    async def mock_authenticate(self, token):
        return {"username": "testuser"}

    monkeypatch.setattr(JWTAuthBackend, "authenticate", mock_authenticate)

    headers = {"Authorization": "Bearer validtoken"}
    response = client.get("/protected", headers=headers)
    assert response.status_code == 200
    assert response.json() == {"message": "Protected for testuser"}


@pytest.mark.asyncio
async def test_unhandled_exception_during_authentication(client, monkeypatch):
    async def mock_authenticate(self, token):
        raise Exception("Unhandled exception")

    monkeypatch.setattr(JWTAuthBackend, "authenticate", mock_authenticate)

    headers = {"Authorization": "Bearer validtoken"}
    response = client.get("/protected", headers=headers)
    assert response.status_code == 500
    assert response.json()["detail"] == "Internal Server Error"


@pytest.mark.asyncio
async def test_extract_token_from_request_no_authorization(client, monkeypatch):
    async def mock_call_next(request):
        return JSONResponse({"message": "next called"})

    request = Request(scope={"type": "http", "headers": {}})

    with pytest.raises(HTTPException) as exc_info:
        JWTAuthenticationMiddleware.extract_token_from_request(request)
    assert exc_info.value.status_code == 401
    assert exc_info.value.detail == "Authorization header is missing."


@pytest.mark.asyncio
async def test_extract_token_from_request_invalid_header_format(client, monkeypatch):
    request = Request(
        scope={"type": "http", "headers": [(b"authorization", b"InvalidFormat")]}
    )

    with pytest.raises(HTTPException) as exc_info:
        JWTAuthenticationMiddleware.extract_token_from_request(request)
        assert exc_info.value.status_code == 400
        assert "Invalid authorization headere" in exc_info.value.detail


@pytest.mark.asyncio
async def test_extract_token_from_request_invalid_scheme(client, monkeypatch):
    request = Request(
        scope={"type": "http", "headers": [(b"authorization", b"Basic sometoken")]}
    )

    with pytest.raises(HTTPException) as exc_info:
        JWTAuthenticationMiddleware.extract_token_from_request(request)
    assert exc_info.value.status_code == 400
    assert (
        exc_info.value.detail
        == "Invalid authorization header, expected value in format 'Bearer <token>'."
    )


@pytest.mark.asyncio
async def test_extract_token_from_request_valid_header(client, monkeypatch):
    token = "validtoken"
    request = Request(
        scope={
            "type": "http",
            "headers": [(b"authorization", f"Bearer {token}".encode())],
        }
    )

    extracted_token = JWTAuthenticationMiddleware.extract_token_from_request(request)
    assert extracted_token == token


@pytest.mark.asyncio
async def test_extract_token_from_request_token_in_cookie(client, monkeypatch):
    token = "validtoken"
    request = Request(
        scope={
            "type": "http",
            "headers": [(b"cookie", f"Authorization=Bearer {token}".encode())],
        }
    )

    extracted_token = JWTAuthenticationMiddleware.extract_token_from_request(request)
    assert extracted_token == token


@pytest.mark.asyncio
async def test_sync_unprotected_route(client):
    response = client.get("/sync-unprotected")
    assert response.status_code == 200
    assert response.json() == {"message": "Unprotected"}


@pytest.mark.asyncio
async def test_sync_protected_route_without_token(client):
    response = client.get("/sync-protected")
    assert response.status_code == 401
    assert response.json()["detail"] == "Authorization header is missing."


@pytest.mark.asyncio
async def test_sync_protected_route_with_invalid_token(client, monkeypatch):
    async def mock_authenticate(self, token):
        raise jwt.PyJWTError("Invalid token")

    monkeypatch.setattr(JWTAuthBackend, "authenticate", mock_authenticate)

    headers = {"Authorization": "Bearer invalidtoken"}
    response = client.get("/sync-protected", headers=headers)
    assert response.status_code == 401
    assert response.json()["detail"] == "Could not validate credentials."


@pytest.mark.asyncio
async def test_sync_protected_route_with_valid_token(client, monkeypatch):
    async def mock_authenticate(self, token):
        return {"username": "testuser"}

    monkeypatch.setattr(JWTAuthBackend, "authenticate", mock_authenticate)

    headers = {"Authorization": "Bearer validtoken"}
    response = client.get("/sync-protected", headers=headers)
    assert response.status_code == 200
    assert response.json() == {"message": "Protected for testuser"}


def test_default_exluded_routes():
    expected_excluded_urls = [
        "/docs",
        "/openapi.json",
        "/redoc",
        "/swagger-ui",
        "/swagger",
        "/swagger.json",
        "/favicon.ico",
    ]
    assert sorted(JWTAuthenticationMiddleware._default_excluded_urls) == sorted(
        expected_excluded_urls
    )
