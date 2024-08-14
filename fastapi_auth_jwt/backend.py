import json
from datetime import timedelta
from typing import Any, Dict, Optional, Type, Union

import jwt
from pydantic import BaseModel

from .config.auth_token import AuthConfig
from .config.storage import StorageConfig
from .config.user_schema import User
from .repository.base import BaseRepository
from .repository.factory import RepositoryFactory
from .utils.jwt_token import JWTHandler
from .utils.time_helpers import cast_to_seconds


class JWTAuthBackend:
    """
    A backend class for handling JWT-based authentication.

    This class provides methods for creating, validating, and invalidating JWT tokens.
    It supports configurable authentication settings, user schemas, and storage backends.

    Attributes:
        _config (AuthConfig): Configuration for authentication (e.g., secret key, jwt_algorithm).
        _user_schema (Type[BaseModel]): Schema for validating user data.
        _storage_config (StorageConfig): Configuration for the storage backend.
        _cache (BaseRepository): The cache repository for storing and retrieving token data.
        _jwt_handler (JWTHandler): Handler for encoding and decoding JWT tokens.

    Methods:
        authenticate(token: str) -> Optional[BaseModel]: Authenticate a user based on a provided JWT token.
        create_token(user_data: Union[Dict[str, Any], pydantic.BaseModel], expiration: Optional[Union[int, float, timedelta]]) -> str: Create a JWT token with an optional expiration time.
        invalidate_token(token: str) -> None: Invalidate a JWT token by removing it from the cache.
        get_current_user(token: str) -> Optional[BaseModel]: Retrieve the current user based on a JWT token.
        get_instance() -> Optional["JWTAuthBackend"]: Get the singleton instance of the JWTAuthBackend class.
    """

    _instance: Optional["JWTAuthBackend"] = None

    def __new__(cls, *args, **kwargs) -> "JWTAuthBackend":
        if cls._instance is None:
            cls._instance = super().__new__(cls)
        return cls._instance

    def __init__(
        self,
        authentication_config: Optional[AuthConfig] = None,
        storage_config: Optional[StorageConfig] = None,
        user_schema: Optional[Type[BaseModel]] = None,
    ):
        if not hasattr(self, "_initialized"):
            self._config = authentication_config or AuthConfig()
            self._user_schema = user_schema or User
            self._storage_config = storage_config or StorageConfig()
            self._cache = RepositoryFactory.create(self._storage_config)
            self._jwt_handler = JWTHandler(
                secret=self.config.secret,
                algorithm=self.config.jwt_algorithm,
            )
            self._initialized = True

    async def authenticate(self, token: str) -> Optional[BaseModel]:
        """
        Authenticate a user based on a provided JWT token.

        Args:
            token (str): The JWT token to authenticate.

        Returns:
            Optional[BaseModel]: The authenticated user model, or None if authentication fails.

        Raises:
            jwt.PyJWTError: If there is an issue with decoding the JWT token.
            Exception: For any other unexpected errors.

        Examples:
            >>> backend = JWTAuthBackend()
            >>> user = await backend.authenticate("some_jwt_token")
            >>> if user:
            >>>     print(f"Authenticated user: {user}")
        """
        try:
            user = await self.get_current_user(token)
            return user
        except jwt.PyJWTError as e:
            raise e
        except Exception as e:
            raise Exception(f"An unexpected error occurred during authentication: {e}")

    async def create_token(
        self,
        user_data: Union[Dict[str, Any], BaseModel],
        expiration: Optional[Union[int, float, timedelta]] = None,
    ) -> str:
        """
        Create a JWT token with an optional expiration time.

        Args:
            user_data (Union[Dict[str, Any], BaseModel]): The payload data to encode into the JWT.
            expiration (Optional[Union[int, float, datetime.timedelta]]): Expiration time in seconds or timedelta.

        Returns:
            str: The generated JWT token.

        Raises:
            Exception: If there is an issue storing the token in the cache.

        Examples:
            >>> backend = JWTAuthBackend()
            >>> token = await backend.create_token({"user_id": 123}, expiration=3600)
            >>> print(f"Generated token: {token}")
        """
        if isinstance(user_data, BaseModel):
            user = user_data
        else:
            user = self.user_schema.model_construct(**user_data)

        if expiration is None:
            expiration_candidates = ["expire", "expiration", "exp"]
            for field in self.config.model_fields.keys():
                if any(candidate in field for candidate in expiration_candidates):
                    expiration = cast_to_seconds(getattr(self.config, field))
                    break
        else:
            expiration = (
                int(expiration.total_seconds())
                if isinstance(expiration, timedelta)
                else int(expiration)
            )

        if expiration is not None and expiration <= 0:
            raise ValueError("Expiration time must be greater than zero.")

        token = self.jwt_handler.encode(
            payload=user.model_dump(exclude_none=True), expiration=expiration
        )

        try:
            await self.cache.set(
                key=token,
                value=user.model_dump_json(exclude_none=True),
                expiration=expiration,
            )
        except Exception as e:
            raise Exception(f"Failed to store token in cache: {e}")

        return token

    async def invalidate_token(self, token: str) -> None:
        """
        Invalidate a JWT token by removing it from the cache.

        Args:
            token (str): The JWT token to invalidate.

        Returns:
            None

        Examples:
            >>> backend = JWTAuthBackend()
            >>> await backend.invalidate_token("some_jwt_token")
        """
        try:
            self.jwt_handler.decode(token, verify=True)
        finally:
            await self.cache.delete(token)

    async def get_current_user(self, token: str) -> Optional[BaseModel]:
        """
        Retrieve the current user based on a JWT token.

        Args:
            token (str): The JWT token to decode and validate.

        Returns:
            Optional[BaseModel]: The validated user model, or None if validation fails.

        Raises:
            jwt.InvalidTokenError: If the token payload does not match the cached payload.
            Exception: For any other unexpected errors.

        Examples:
            >>> backend = JWTAuthBackend()
            >>> user = await backend.get_current_user("some_jwt_token")
            >>> if user:
            >>>     print(f"Current user: {user}")
        """
        token_payload = self.jwt_handler.decode(token)
        try:
            cached_payload = await self.cache.get(token)
            cached_payload = json.loads(cached_payload) if cached_payload else None
        except Exception as e:
            raise Exception(f"Failed to retrieve token from cache: {e}")

        if not cached_payload:
            return None

        for key, value in token_payload.items():
            if value is None:
                continue
            if key not in cached_payload or cached_payload[key] != value:
                raise jwt.InvalidTokenError(f"Token payload mismatch for key: {key}")

        return self.user_schema.model_construct(
            token=token,
            **cached_payload,
        )

    @classmethod
    def get_instance(cls) -> Optional["JWTAuthBackend"]:
        """
        Get the singleton instance of the JWTAuthBackend class.

        Returns:
            Optional[JWTAuthBackend]: The singleton instance.

        Examples:
            >>> backend = JWTAuthBackend.get_instance()
            >>> if backend:
            >>>     print("JWTAuthBackend instance exists.")
        """
        return cls._instance

    @property
    def config(self) -> AuthConfig:
        """Get the current authentication configuration."""
        return self._config

    @config.setter
    def config(self, value: AuthConfig) -> None:
        """Set a new authentication configuration."""
        self._config = value

    @property
    def user_schema(self) -> Type[BaseModel]:
        """Get the current user schema."""
        return self._user_schema

    @user_schema.setter
    def user_schema(self, value: Type[BaseModel]) -> None:
        """Set a new user schema."""
        self._user_schema = value

    @property
    def storage_config(self) -> StorageConfig:
        """Get the current storage configuration."""
        return self._storage_config

    @storage_config.setter
    def storage_config(self, value: StorageConfig) -> None:
        """Set a new storage configuration."""
        self._storage_config = value

    @property
    def cache(self) -> BaseRepository:
        """Get the current cache repository."""
        return self._cache

    @cache.setter
    def cache(self, value: BaseRepository) -> None:
        """Set a new cache repository."""
        self._cache = value

    @property
    def jwt_handler(self) -> JWTHandler:
        """Get the current JWT handler."""
        return self._jwt_handler

    @jwt_handler.setter
    def jwt_handler(self, value: JWTHandler) -> None:
        """Set a new JWT handler."""
        self._jwt_handler = value


__all__ = ["JWTAuthBackend"]
