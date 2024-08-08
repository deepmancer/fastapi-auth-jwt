from pydantic import BaseModel, ConfigDict


class User(BaseModel):
    model_config = ConfigDict(
        populate_by_name=True,
        extra="allow",
        arbitrary_types_allowed=True,
    )


__all__ = ["User"]
