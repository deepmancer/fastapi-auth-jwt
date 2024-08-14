# examples/redis/app/config.py

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


class StorageConfig(BaseModel):
    storage_type: str = "redis"
    host: str = "localhost"
    port: int = 6379
    db: int = 0


__all__ = ["User", "AuthenticationSettings", "StorageConfig"]
