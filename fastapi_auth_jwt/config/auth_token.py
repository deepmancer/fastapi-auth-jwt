import json

from pydantic import BaseModel, Field, computed_field, field_validator


class AuthConfig(BaseModel):
    secret: str = Field(default="default_secret")
    algorithm: str = Field(default="HS256")
    expiration_seconds: int = Field(default=3600)

    @field_validator("expiration_seconds", mode="before")
    def validate_expiration_seconds(cls, v):
        if isinstance(v, (int, float, str)):
            v = int(v)

        if v < 0:
            raise ValueError("expiration_seconds must be greater than 0")

        return v

    @computed_field(return_type=int)
    def expiration_minutes(self) -> int:
        return self.expiration_seconds // 60 if self.expiration_seconds else None

    def __repr__(self):
        dict_repr = json.dumps(self.model_dump(), indent=2)
        return f"<AuthConfig: {dict_repr}>"

    def __str__(self):
        return self.__repr__()


__all__ = ["AuthConfig"]
