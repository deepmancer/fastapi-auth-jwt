from pydantic import BaseModel, ConfigDict


class User(BaseModel):
    """
    General Pydantic model for user metadata.

    This model is designed to store and retrieve user metadata, such as `user_id`, `user_name`, and other
    related fields, from a cache or other storage mechanisms. The schema is customizable, allowing users
    to define and set any serializable field according to their needs.
    """

    model_config = ConfigDict(
        populate_by_name=True,
        extra="allow",
        arbitrary_types_allowed=True,
    )


__all__ = ["User"]
