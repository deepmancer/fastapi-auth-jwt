# examples/standard/app/schemas.py

from pydantic import BaseModel


# Define request schemas
class RegisterSchema(BaseModel):
    username: str
    password: str


class LoginSchema(BaseModel):
    username: str
    password: str


__all__ = ["RegisterSchema", "LoginSchema"]
