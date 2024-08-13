
from fastapi import FastAPI, HTTPException, Request
from typing import Optional
from fastapi.responses import JSONResponse
from pydantic import BaseModel, Field
from starlette.testclient import TestClient
from starlette.responses import Response
from starlette.requests import Request

from fastapi_auth_jwt import JWTAuthBackend
from fastapi_auth_jwt import JWTAuthenticationMiddleware


app = FastAPI()

# The application specific user schema
class User(BaseModel):
    username: str
    password: str
    
    # just add a token field to the user schema if you want to persist the token
    token: Optional[str] = Field(None)

class RegisterSchema(BaseModel):
    username: str
    password: str
    # some other fields
    
class LoginSchema(BaseModel):
    username: str
    password: str

# in production you can use Settings management
# from pydantic to get secret key from .env
class AuthenticationSettings(BaseModel):
    secret: str = "secret" 
    jwt_algorithm: str = "HS256"
    expiration_seconds: int = 60 * 60 # 1 hour

auth_backend = JWTAuthBackend(
    authentication_config=AuthenticationSettings(),
    user_schema=User,
    # if want to use redis, you can pass the storage_config using the fastapi_auth_jwt.RedisConfig 
)

app.add_middleware(
    JWTAuthenticationMiddleware,
    backend=auth_backend,
    exclude_urls=["/sign-up", "/login"],
)


@app.post("/sign-up")
async def sign_up(request_data: RegisterSchema):
    return {"message": "User created"}

@app.post("/login")
async def login(request_data: LoginSchema):
    # Check credentials
    user = User(username=request_data.username, password=request_data.password)
    token = await auth_backend.create_token(user) # creates and persists a token with expirtion of 1 hour
    return {"token": token}

@app.get("/profile-info")
async def get_profile_info(request: Request):
    user: User = request.state.user
    # ptint(user)
    # >>> User(username='some_username', password='some_password', token='some_token)
    return {"username": user.username}

# api for logout which invalidates the token
@app.post("/logout")
async def logout(request: Request):
    user: User = request.state.user
    await auth_backend.invalidate_token(user.token)
    return {"message": "Logged out"}


