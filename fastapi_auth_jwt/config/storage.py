import json
from typing import Optional

from decouple import config
from pydantic import BaseModel, ConfigDict, Field

from .storage_type import StorageTypes


class StorageConfig(BaseModel):
    storage_type: StorageTypes = Field(default=StorageTypes.MEMORY)

    model_config = ConfigDict(
        from_attributes=True,
        validate_assignment=True,
        populate_by_name=True,
        extra="allow",
        arbitrary_types_allowed=True,
    )


class RedisConfig(StorageConfig):
    storage_type: StorageTypes = Field(default=StorageTypes.REDIS)
    host: str = Field(default_factory=lambda: config("REDIS_HOST", "localhost"))
    port: int = Field(default_factory=lambda: int(config("REDIS_PORT", 6379)))
    db: int = Field(default_factory=lambda: int(config("REDIS_DB", 0)))
    password: Optional[str] = Field(default_factory=lambda: config("REDIS_PASSWORD", None))
    url: Optional[str] = Field(default=None)

    def __repr__(self) -> str:
        attributes = self.dict(exclude={"url"})
        attributes["url"] = self.get_url()
        attributes_str = json.dumps(attributes, indent=2)
        return f"< RedisConfig: {attributes_str} >"

    def __str__(self) -> str:
        return self.__repr__()

    def get_url(self) -> str:
        if self.url:
            return self.url
        if self.password:
            return f"redis://:{self.password}@{self.host}:{self.port}/{self.db}"
        return f"redis://{self.host}:{self.port}/{self.db}"


__all__ = ["StorageConfig", "RedisConfig"]
