from datetime import timedelta
from typing import Any, Dict, Optional, Type, Union

import jwt
from pydantic import BaseModel

from .config import AuthConfig, StorageConfig, User
from .repository.base import BaseRepository
from .repository.factory import RepositoryFactory
from .utils import JWTHandler


class JWTAuthBackend:
    _instance = None

    def __new__(cls, *args, **kwargs):
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
                algorithm=self.config.algorithm,
            )
            self._initialized = True

    async def authenticate(self, token: str) -> Optional[BaseModel]:
        try:
            user = await self.get_current_user(token)
            return user
        except jwt.PyJWTError as e:
            raise e
        except Exception as e:
            raise Exception(f"An unexpected error occurred during authentication: {e}")

    async def create_token(
        self,
        payload: Dict[str, Any],
        expiration_seconds: Optional[Union[int, float, timedelta]] = None,
    ) -> str:
        if expiration_seconds is None:
            expiration_candidates = ["expire", "expiration", "exp"]
            for field in self.config.model_fields.keys():
                if any(candidate in field for candidate in expiration_candidates):
                    expiration_seconds = getattr(self.config, field)
                    break

        token = self.jwt_handler.encode(payload=payload, expiration=expiration_seconds)

        try:
            await self.cache.set(
                key=token,
                value=payload,
                expiration=expiration_seconds,
            )
        except Exception as e:
            raise Exception(f"Failed to store token in cache: {e}")

        return token

    async def invalidate_token(self, token: str) -> None:
        await self.cache.delete(token)

    async def get_current_user(self, token: str) -> Optional[BaseModel]:
        token_payload = self.jwt_handler.decode(token)
        try:
            cached_payload = await self.cache.get(token)
        except Exception as e:
            raise Exception(f"Failed to retrieve token from cache: {e}")

        if not cached_payload:
            return None

        for key, value in token_payload.items():
            if value is None:
                continue
            if key not in cached_payload or cached_payload[key] != value:
                raise jwt.InvalidTokenError(f"Token payload mismatch for key: {key}")

        return self.user_schema.model_validate(
            {
                "token": token,
                **cached_payload,
            }
        )

    @classmethod
    def get_instance(cls) -> Optional["JWTAuthBackend"]:
        return cls._instance

    @property
    def config(self) -> AuthConfig:
        return self._config

    @config.setter
    def config(self, value: AuthConfig):
        self._config = value

    @property
    def user_schema(self) -> Type[BaseModel]:
        return self._user_schema

    @user_schema.setter
    def user_schema(self, value: Type[BaseModel]):
        self._user_schema = value

    @property
    def storage_config(self) -> StorageConfig:
        return self._storage_config

    @storage_config.setter
    def storage_config(self, value: StorageConfig):
        self._storage_config = value

    @property
    def cache(self) -> BaseRepository:
        return self._cache

    @cache.setter
    def cache(self, value: BaseRepository):
        self._cache = value

    @property
    def jwt_handler(self) -> JWTHandler:
        return self._jwt_handler

    @jwt_handler.setter
    def jwt_handler(self, value: JWTHandler):
        self._jwt_handler = value


__all__ = ["JWTAuthBackend"]
