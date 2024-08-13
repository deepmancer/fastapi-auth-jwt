# FastAPI Auth JWT Documentation

Welcome to the documentation for **FastAPI-Auth-JWT**, a ready-to-use and easy-to-customize authentication middleware for FastAPI. This documentation provides detailed information on the various components of the library, including middleware, backend, configuration options, and JWT handling.

## Introduction

**FastAPI-Auth-JWT** is an authentication middleware that integrates with FastAPI applications. It provides JSON Web Token (JWT) authentication with easy configuration and customization options. The following sections will guide you through the different modules and their usage.

## Modules

### Middleware

### *class* fastapi_auth_jwt.middleware.JWTAuthenticationMiddleware(app, backend=None, exclude_urls=[])

Bases: `BaseHTTPMiddleware`

Middleware for handling JWT authentication in FastAPI applications.

This middleware intercepts incoming requests to apply JWT authentication,
allowing the authentication process to be customized and token validation to occur before the request reaches the application logic.

#### backend

The backend used for JWT authentication.

* **Type:**
  [JWTAuthBackend](#fastapi_auth_jwt.backend.JWTAuthBackend)

#### exclude_urls

A list of URL paths that are excluded from authentication.

* **Type:**
  List[str]

#### *async* dispatch(request, call_next)

Handle incoming requests and apply JWT authentication.

This method processes each request, extracting and validating the JWT token.
If authentication fails, an appropriate error response is returned.
Otherwise, the request proceeds to the next handler.

* **Parameters:**
  * **request** (*Request*) – The FastAPI request object.
  * **call_next** (*Callable* *[* *[**Request* *]* *,* *Awaitable* *[**Response* *]* *]*) – The next request handler.
* **Returns:**
  The response object after processing the request.
* **Return type:**
  Response

#### *classmethod* extract_token_from_request(request)

Extract the JWT token from the request’s Authorization header or cookies.

* **Parameters:**
  **request** (*Request*) – The FastAPI request object.
* **Returns:**
  The extracted JWT token.
* **Return type:**
  str
* **Raises:**
  **HTTPException** – If the Authorization header is missing or invalid.

### Examples

```pycon
>>> request = Request(...)  # Assume a FastAPI request object with a valid header
>>> token = JWTAuthenticationMiddleware.extract_token_from_request(request)
>>> print(token)
'eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...'
```

### Backend

### *class* fastapi_auth_jwt.backend.JWTAuthBackend(authentication_config=None, storage_config=None, user_schema=None)

Bases: `object`

A backend class for handling JWT-based authentication.

This class provides methods for creating, validating, and invalidating JWT tokens.
It supports configurable authentication settings, user schemas, and storage backends.

#### \_config

Configuration for authentication (e.g., secret key, algorithm).

* **Type:**
  AuthConfig

#### \_user_schema

Schema for validating user data.

* **Type:**
  Type[BaseModel]

#### \_storage_config

Configuration for the storage backend.

* **Type:**
  StorageConfig

#### \_cache

The cache repository for storing and retrieving token data.

* **Type:**
  BaseRepository

#### \_jwt_handler

Handler for encoding and decoding JWT tokens.

* **Type:**
  [JWTHandler](#fastapi_auth_jwt.utils.jwt_token.JWTHandler)

#### *async* authenticate(token)

Authenticate a user based on a provided JWT token.

* **Parameters:**
  **token** (*str*) – The JWT token to authenticate.
* **Returns:**
  The authenticated user model, or None if authentication fails.
* **Return type:**
  Optional[BaseModel]
* **Raises:**
  * **jwt.PyJWTError** – If there is an issue with decoding the JWT token.
  * **Exception** – For any other unexpected errors.

### Examples

```pycon
>>> backend = JWTAuthBackend()
>>> user = await backend.authenticate("some_jwt_token")
>>> if user:
>>>     print(f"Authenticated user: {user}")
```

#### *property* cache *: BaseRepository*

Get the current cache repository.

#### *property* config *: AuthConfig*

Get the current authentication configuration.

#### *async* create_token(payload, expiration=None)

Create a JWT token with an optional expiration time.

* **Parameters:**
  * **payload** (*Dict* *[**str* *,* *Any* *]*) – The payload data to encode into the JWT.
  * **expiration** (*Optional* *[**Union* *[**int* *,* *float* *,* *datetime.timedelta* *]* *]*) – Expiration time in seconds or timedelta.
* **Returns:**
  The generated JWT token.
* **Return type:**
  str
* **Raises:**
  **Exception** – If there is an issue storing the token in the cache.

### Examples

```pycon
>>> backend = JWTAuthBackend()
>>> token = await backend.create_token({"user_id": 123}, expiration=3600)
>>> print(f"Generated token: {token}")
```

#### *async* get_current_user(token)

Retrieve the current user based on a JWT token.

* **Parameters:**
  **token** (*str*) – The JWT token to decode and validate.
* **Returns:**
  The validated user model, or None if validation fails.
* **Return type:**
  Optional[BaseModel]
* **Raises:**
  * **jwt.InvalidTokenError** – If the token payload does not match the cached payload.
  * **Exception** – For any other unexpected errors.

### Examples

```pycon
>>> backend = JWTAuthBackend()
>>> user = await backend.get_current_user("some_jwt_token")
>>> if user:
>>>     print(f"Current user: {user}")
```

#### *classmethod* get_instance()

Get the singleton instance of the JWTAuthBackend class.

* **Returns:**
  The singleton instance.
* **Return type:**
  Optional[[JWTAuthBackend](#fastapi_auth_jwt.backend.JWTAuthBackend)]

### Examples

```pycon
>>> backend = JWTAuthBackend.get_instance()
>>> if backend:
>>>     print("JWTAuthBackend instance exists.")
```

#### *async* invalidate_token(token)

Invalidate a JWT token by removing it from the cache.

* **Parameters:**
  **token** (*str*) – The JWT token to invalidate.
* **Return type:**
  `None`
* **Returns:**
  None

### Examples

```pycon
>>> backend = JWTAuthBackend()
>>> await backend.invalidate_token("some_jwt_token")
```

#### *property* jwt_handler *: [JWTHandler](#fastapi_auth_jwt.utils.jwt_token.JWTHandler)*

Get the current JWT handler.

#### *property* storage_config *: StorageConfig*

Get the current storage configuration.

#### *property* user_schema *: Type[BaseModel]*

Get the current user schema.

### Configuration

### JWT Handler

### *class* fastapi_auth_jwt.utils.jwt_token.JWTHandler(secret, algorithm='HS256')

Bases: `object`

A handler class for encoding and decoding JWT tokens.

This class provides methods to encode a payload into a JWT token and decode a JWT token back into a payload.
It supports setting an expiration time and handles various exceptions during the encoding and decoding process.

#### secret

The secret key used for encoding and decoding the JWT.

* **Type:**
  str

#### algorithm

The algorithm used for encoding and decoding the JWT. Defaults to ‘HS256’.

* **Type:**
  str

#### decode(token, \*\*kwargs)

Decode a JWT token into a payload.

This method decodes a given JWT token back into its payload. The expiration field (‘exp’)
is removed from the decoded payload if it exists.

* **Parameters:**
  **token** (*str*) – The JWT token to decode.
* **Returns:**
  The decoded payload.
* **Return type:**
  Dict[str, Any]
* **Raises:**
  * **jwt.PyJWTError** – If an error occurs during decoding.
  * **Exception** – If any other unexpected error occurs.

### Examples

```pycon
>>> handler = JWTHandler(secret="mysecret")
>>> token = handler.encode({"user_id": 123}, expiration=3600)
>>> payload = handler.decode(token)
>>> print(payload)
{'user_id': 123}
```

```pycon
>>> # Decoding a token with additional fields
>>> token = handler.encode({"user_id": 123, "role": "admin"}, expiration=3600)
>>> payload = handler.decode(token)
>>> print(payload)
{'user_id': 123, 'role': 'admin'}
```

#### encode(payload, expiration=None, \*\*kwargs)

Encode a payload into a JWT token.

This method encodes a given payload into a JWT token, optionally setting an expiration time.
Additional key-value pairs can be passed as kwargs to be included in the payload.

* **Parameters:**
  * **payload** (*Dict* *[**str* *,* *Any* *]*) – The payload data to encode into the JWT.
  * **expiration** (*Optional* *[**Union* *[**float* *,* *int* *]* *]*) – Optional expiration time in seconds. Defaults to None.
* **Returns:**
  The encoded JWT token.
* **Return type:**
  str
* **Raises:**
  * **TypeError** – If the payload contains an invalid type.
  * **jwt.PyJWTError** – If an error occurs during encoding.
  * **Exception** – If any other unexpected error occurs.

### Examples

```pycon
>>> handler = JWTHandler(secret="mysecret")
>>> token = handler.encode({"user_id": 123}, expiration=3600)
>>> print(token)
'eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9...'
```

```pycon
>>> # Encoding with additional fields in the payload
>>> token = handler.encode({"user_id": 123}, role="admin", expiration=3600)
>>> print(token)
'eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9...'
```

## Indices and tables

* [Index](genindex.md)
* [Module Index](py-modindex.md)
* [Search Page](search.md)
