import time
from typing import Any, Callable, Coroutine, List

import jwt
from fastapi import HTTPException, Request
from fastapi.responses import JSONResponse
from fastapi.security.utils import get_authorization_scheme_param
from starlette.middleware.base import BaseHTTPMiddleware
from starlette.responses import Response
from starlette.types import ASGIApp

from .backend import JWTAuthBackend


class JWTAuthenticationMiddleware(BaseHTTPMiddleware):
    """Middleware for handling JWT authentication."""

    def __init__(
        self,
        app: ASGIApp,
        backend: JWTAuthBackend = JWTAuthBackend(),
        exclude_urls: List[str] = None,
    ):
        """Initializes the JWTAuthenticationMiddleware.

        Args:
            app: The ASGI application.
            backend: The backend to use for authentication.
            exclude_urls: List of URLs to exclude from authentication.
        """
        super().__init__(app)
        self.backend = backend
        self.exclude_urls = exclude_urls or []

    @classmethod
    def extract_token_from_request(cls, request: Request) -> str:
        """Extracts the JWT token from the request headers or cookies.

        Args:
            request: The FastAPI request object.

        Returns:
            The JWT token.

        Raises:
            HTTPException: If the authorization header is missing or invalid.
        """
        authorization_header = request.headers.get("Authorization") or request.cookies.get("Authorization")
        if not authorization_header:
            raise HTTPException(status_code=401, detail="Authorization header is missing.")

        try:
            scheme, token = get_authorization_scheme_param(authorization_header)
        except ValueError:
            raise HTTPException(status_code=400, detail="Could not parse authorization header.")

        if scheme.lower() != "bearer":
            raise HTTPException(
                status_code=400, detail="Invalid authorization header, expected value in format 'Bearer <token>'."
            )

        return token

    async def dispatch(
        self,
        request: Request,
        call_next: Callable[[Request], Coroutine[Any, Any, Response]],
    ) -> Response:
        """Handles incoming requests and applies JWT authentication.

        Args:
            request: The FastAPI request object.
            call_next: The next request handler.

        Returns:
            The response object.
        """
        request_url_path = request.url.path
        if any(url in request_url_path for url in self.exclude_urls):
            return await call_next(request)

        try:
            token = self.extract_token_from_request(request)
            user = await self.backend.authenticate(token)
        except jwt.MissingRequiredClaimError as exc:
            return self._handle_authentication_exception(
                request,
                exc,
                default_status_code=400,
                default_detail="Missing required claim.",
            )
        except jwt.PyJWTError as exc:
            return self._handle_authentication_exception(
                request,
                exc,
                default_status_code=401,
                default_detail="Could not validate credentials.",
            )
        except Exception as exc:
            return self._handle_authentication_exception(request, exc)

        request.state.user = user
        return await call_next(request)

    @classmethod
    def _handle_authentication_exception(
        cls,
        request: Request,
        error: Exception,
        default_status_code: int = 500,
        default_detail: str = "Internal Server Error",
    ) -> JSONResponse:
        """Handles exceptions raised during authentication.

        Args:
            request: The FastAPI request object.
            error: The exception that was raised.
            default_status_code: The default HTTP status code to use.
            default_detail: The default error detail message.

        Returns:
            A JSONResponse with the error details.
        """
        if isinstance(error, HTTPException):
            detail = error.detail
            status_code = error.status_code
        else:
            detail = default_detail
            status_code = default_status_code

        error_details = {
            "path": request.url.path,
            "method": request.method,
            "detail": detail,
            "timestamp": int(time.time()),
        }

        return JSONResponse(
            status_code=status_code,
            content=error_details,
        )


__all__ = ["JWTAuthenticationMiddleware"]
