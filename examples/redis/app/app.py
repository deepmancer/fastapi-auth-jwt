# examples/redis/app/app.py

from fastapi import FastAPI, Request
from fastapi_auth_jwt import JWTAuthBackend, JWTAuthenticationMiddleware

from app.config import User, StorageConfig, AuthenticationSettings
from app.schemas import RegisterSchema, LoginSchema

# Initialize the Authentication Backend
auth_backend = JWTAuthBackend(
    authentication_config=AuthenticationSettings(),
    user_schema=User,
    storage_config=StorageConfig(),
)

# Create FastAPI app and add middleware
app = FastAPI()

app.add_middleware(
    JWTAuthenticationMiddleware,
    backend=auth_backend,
    exclude_urls=["/sign-up", "/login"],
)


# Create Routes
@app.post("/sign-up")
async def sign_up(request_data: RegisterSchema):
    return {"message": "User created"}


@app.post("/login")
async def login(request_data: LoginSchema):
    token = await auth_backend.create_token(
        {
            "username": request_data.username,
            "password": request_data.password,
        }
    )
    return {"token": token}


@app.get("/profile-info")
async def get_profile_info(request: Request):
    user: User = request.state.user
    return {"username": user.username}


@app.post("/logout")
async def logout(request: Request):
    user: User = request.state.user
    await auth_backend.invalidate_token(user.token)
    return {"message": "Logged out"}


__all__ = ["app"]
