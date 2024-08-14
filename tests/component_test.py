import asyncio

import pytest
from fastapi import FastAPI, Request
from fastapi.testclient import TestClient
from pydantic import BaseModel

from fastapi_auth_jwt.backend import JWTAuthBackend
from fastapi_auth_jwt.middleware import JWTAuthenticationMiddleware
from tests.conftest import MockUser


# Mock register schema
class RegisterSchema(BaseModel):
    username: str
    password: str


# Mock login schema
class LoginSchema(BaseModel):
    username: str
    password: str


# Mock authentication settings
class AuthenticationSettings(BaseModel):
    secret: str = "your-secret-key"
    jwt_algorithm: str = "HS256"
    expiration_seconds: int = 3600  # 1 hour


users_db = {}


@pytest.fixture
def mock_app():
    auth_backend = JWTAuthBackend(
        authentication_config=AuthenticationSettings(), user_schema=MockUser
    )
    app = FastAPI()

    @app.post("/sign-up")
    async def sign_up(request_data: RegisterSchema):
        users_db[request_data.username] = request_data.password
        return {"message": "MockUser created"}

    @app.post("/login")
    async def login(request_data: LoginSchema):
        if users_db.get(request_data.username) == request_data.password:
            user = MockUser(
                username=request_data.username, password=request_data.password
            )
            token = await auth_backend.create_token(user)
            return {"token": token}
        return {"message": "Invalid credentials"}, 401

    @app.get("/profile-info")
    async def get_profile_info(request: Request):
        user: MockUser = request.state.user
        return {"username": user.username}

    @app.post("/logout")
    async def logout(request: Request):
        user: MockUser = request.state.user
        token = user.token
        await auth_backend.invalidate_token(token)
        return {"message": "Logged out"}

    app.add_middleware(
        JWTAuthenticationMiddleware,
        backend=auth_backend,
        exclude_urls=["/sign-up", "/login"],
    )

    return app


@pytest.fixture
def client(mock_app):
    return TestClient(mock_app)


@pytest.mark.asyncio
async def test_authentication_flow(client):
    # Sign up
    response = client.post(
        "/sign-up", json={"username": "testuser", "password": "testpass"}
    )
    assert response.status_code == 200
    assert response.json() == {"message": "MockUser created"}

    # Login
    response = client.post(
        "/login", json={"username": "testuser", "password": "testpass"}
    )
    assert response.status_code == 200
    token = response.json()["token"]

    assert token is not None
    # Get profile info
    response = client.get("/profile-info", headers={"Authorization": f"Bearer {token}"})
    assert response.status_code == 200
    assert response.json() == {"username": "testuser"}


@pytest.mark.asyncio
async def test_invalidated_token(client):
    client.post("/sign-up", json={"username": "testuser", "password": "testpass"})

    response = client.post(
        "/login", json={"username": "testuser", "password": "testpass"}
    )
    assert response.status_code == 200

    token = response.json()["token"]

    assert token is not None
    # Logout
    response = client.post("/logout", headers={"Authorization": f"Bearer {token}"})
    assert response.status_code == 200
    assert response.json() == {"message": "Logged out"}

    await asyncio.sleep(0.01)

    # Try to get profile info with the invalidated token
    response = client.get("/profile-info", headers={"Authorization": f"Bearer {token}"})
    assert response.status_code == 401
    assert response.json()["detail"] == "User not found."
