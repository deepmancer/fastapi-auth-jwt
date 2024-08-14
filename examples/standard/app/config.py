# examples/standard/app/config.py

from pydantic import BaseModel, Field
from typing import Optional


class User(BaseModel):
    username: str
    password: str
    token: Optional[str] = Field(None)


class AuthenticationSettings(BaseModel):
    secret: str = "secret-key"
    jwt_algorithm: str = "HS256"
    expiration_seconds: int = 3600  # 1 hour


__all__ = ["User", "AuthenticationSettings"]
