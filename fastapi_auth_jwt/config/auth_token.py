import json
from typing import Optional

from pydantic import BaseModel, Field, computed_field, field_validator


class AuthConfig(BaseModel):
    """
    Configuration class for authentication settings.

    This class is used to configure authentication-related settings, such as the secret key,
    algorithm used for token encoding (jwt), and token expiration time in seconds. It also provides
    validation for these settings and computed fields for convenience.

    Attributes:
        secret (str): The secret key used for signing tokens. Defaults to "default_secret".
        jwt_algorithm (str): The algorithm used for encoding tokens. Defaults to "HS256".
        expiration_seconds (int): The token expiration time in seconds. Defaults to 3600.
    """

    secret: str = Field(default="default_secret")
    jwt_algorithm: str = Field(default="HS256")
    expiration_seconds: int = Field(default=3600)

    @field_validator("expiration_seconds", mode="before")
    def validate_expiration_seconds(cls, v) -> int:
        """
        Validate and convert the `expiration_seconds` field to an integer.

        This method ensures that the `expiration_seconds` field is a positive integer.
        If a float or string is provided, it is converted to an integer. If the value
        is less than 0, a `ValueError` is raised.

        Args:
            v (Union[int, float, str]): The value to validate and convert.

        Returns:
            int: The validated and converted value.

        Raises:
            ValueError: If `v` is less than 0.

        Examples:
            >>> AuthConfig.validate_expiration_seconds(3600)
            3600

            >>> AuthConfig.validate_expiration_seconds("7200")
            7200

            >>> AuthConfig.validate_expiration_seconds(-100)
            ValueError: expiration_seconds must be greater than 0
        """
        if isinstance(v, (int, float, str)):
            v = int(v)

        if v < 0:
            raise ValueError("expiration_seconds must be greater than 0")

        return v

    @computed_field(return_type=int)
    def expiration_minutes(self) -> Optional[int]:
        """
        Compute the token expiration time in minutes.

        This method calculates the token expiration time in minutes based on the
        `expiration_seconds` attribute.

        Returns:
            Optional[int]: The token expiration time in minutes.

        Examples:
            >>> config = AuthConfig(expiration_seconds=3600)
            >>> config.expiration_minutes
            60

            >>> config = AuthConfig(expiration_seconds=4500)
            >>> config.expiration_minutes
            75
        """
        return self.expiration_seconds // 60 if self.expiration_seconds else None

    def __repr__(self) -> str:
        """
        Return a string representation of the authentication configuration object.

        The representation includes all configuration attributes formatted as a JSON string.

        Returns:
            str: The representation of the authentication configuration.

        Examples:
            >>> config = AuthConfig(secret="my_secret", algorithm="HS512", expiration_seconds=7200)
            >>> repr(config)
            'AuthConfig(secret=my_secret, algorithm=HS512, expiration_seconds=7200, expiration_minutes=120)'
        """
        attributes = self.model_dump(exclude_none=True)
        attributes_str = ", ".join([f"{k}={v}" for k, v in attributes.items()])
        return f"AuthConfig({attributes_str})"

    def __str__(self) -> str:
        """
        Return a string representation of the authentication configuration object.

        This method calls `__repr__` to provide a consistent string representation.

        Returns:
            str: The representation of the authentication configuration.

        Examples:
            >>> config = AuthConfig(secret="my_secret", algorithm="HS512", expiration_seconds=7200)
            >>> str(config)
            'AuthConfig(secret=my_secret, algorithm=HS512, expiration_seconds=7200, expiration_minutes=120)'
        """
        return self.__repr__()


__all__ = ["AuthConfig"]
