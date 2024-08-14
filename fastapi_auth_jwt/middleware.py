import time
from typing import Awaitable, Callable, List, Optional

import jwt
from fastapi import HTTPException, Request
from fastapi.responses import JSONResponse
from fastapi.security.utils import get_authorization_scheme_param
from starlette.middleware.base import BaseHTTPMiddleware
from starlette.responses import Response
from starlette.types import ASGIApp

from .backend import JWTAuthBackend


class JWTAuthenticationMiddleware(BaseHTTPMiddleware):
    """
    Middleware for handling JWT authentication in FastAPI applications.

    This middleware intercepts incoming requests to apply JWT authentication,
    allowing the authentication process to be customized and token validation to occur before the request reaches the application logic.

    Attributes:
        backend (JWTAuthBackend): The backend used for JWT authentication.
        exclude_urls (List[str]): A list of URL paths that are excluded from authentication.
        _default_excluded_urls (List[str]): A list of default URL paths that are excluded from authentication.

    Methods:
        dispatch(request: Request, call_next: Callable[[Request], Awaitable[Response]]) -> Response: Handle incoming requests and apply JWT authentication
    """

    _default_excluded_urls = [
        "/docs",
        "/redoc",
        "/openapi.json",
        "/swagger.json",
        "/swagger",
        "/favicon.ico",
        "/swagger-ui",
    ]

    def __init__(
        self,
        app: ASGIApp,
        backend: Optional[JWTAuthBackend] = None,
        exclude_urls: Optional[List[str]] = [],
    ):
        """
        Initialize the JWTAuthenticationMiddleware.

        Args:
            app (ASGIApp): The ASGI application instance.
            backend (JWTAuthBackend): The backend to use for authentication.
            exclude_urls (Optional[List[str]]): List of URL paths to exclude from authentication.
        """
        super().__init__(app)
        self._backend = backend or JWTAuthBackend()
        self._exclude_urls = exclude_urls or []

    @property
    def backend(self) -> JWTAuthBackend:
        """
        Get the backend used for JWT authentication.

        Returns:
            JWTAuthBackend: The backend used for JWT authentication.
        """
        return self._backend

    @backend.setter
    def backend(self, value: JWTAuthBackend):
        """
        Set the backend used for JWT authentication.

        Args:
            value (JWTAuthBackend): The backend to use for JWT authentication.
        """
        self._backend = value

    @property
    def exclude_urls(self) -> List[str]:
        """
        Get the list of URL paths that are excluded from authentication.

        Returns:
            List[str]: The list of URL paths that are excluded from authentication.
        """
        return self._exclude_urls

    @exclude_urls.setter
    def exclude_urls(self, value: List[str]):
        """
        Set the list of URL paths that are excluded from authentication.

        Args:
            value (List[str]): The list of URL paths to exclude from authentication.
        """
        self._exclude_urls = value

    @classmethod
    def extract_token_from_request(cls, request: Request) -> str:
        """
        Extract the JWT token from the request's Authorization header or cookies.

        Args:
            request (Request): The FastAPI request object.

        Returns:
            str: The extracted JWT token.

        Raises:
            HTTPException: If the Authorization header is missing or invalid.

        Examples:
            >>> request = Request(...)  # Assume a FastAPI request object with a valid header
            >>> token = JWTAuthenticationMiddleware.extract_token_from_request(request)
            >>> print(token)
            'eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...'
        """
        authorization_header = request.headers.get(
            "Authorization"
        ) or request.cookies.get("Authorization")
        if not authorization_header:
            raise HTTPException(
                status_code=401, detail="Authorization header is missing."
            )

        scheme, token = get_authorization_scheme_param(authorization_header)

        if scheme.lower() != "bearer":
            raise HTTPException(
                status_code=400,
                detail="Invalid authorization header, expected value in format 'Bearer <token>'.",
            )

        return token

    async def dispatch(
        self,
        request: Request,
        call_next: Callable[[Request], Awaitable[Response]],
    ) -> Response:
        """
        Handle incoming requests and apply JWT authentication.

        This method processes each request, extracting and validating the JWT token.
        If authentication fails, an appropriate error response is returned.
        Otherwise, the request proceeds to the next handler.

        Args:
            request (Request): The FastAPI request object.
            call_next (Callable[[Request], Awaitable[Response]]): The next request handler.

        Returns:
            Response: The response object after processing the request.
        """
        request_url_path = request.url.path
        if any(
            url in request_url_path
            for url in self.exclude_urls + self._default_excluded_urls
        ):
            return await call_next(request)

        try:
            token = self.extract_token_from_request(request)
            user = await self.backend.authenticate(token)
            if user is None:
                raise HTTPException(status_code=401, detail="User not found.")
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
        """
        Handle exceptions raised during authentication and return an appropriate JSON response.

        Args:
            request (Request): The FastAPI request object.
            error (Exception): The exception that was raised during authentication.
            default_status_code (int): The default HTTP status code to use in the response.
            default_detail (str): The default error detail message.

        Returns:
            JSONResponse: A JSON response with the error details.

        Examples:
            >>> request = Request(...)  # Assume a FastAPI request object
            >>> error = HTTPException(status_code=401, detail="Invalid token")
            >>> response = JWTAuthenticationMiddleware._handle_authentication_exception(request, error)
            >>> print(response.status_code)
            401
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
