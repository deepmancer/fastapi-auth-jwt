# 🚀 FastAPI Auth JWT Documentation

Welcome to the documentation for **FastAPI-Auth-JWT**, an easy-to-use and customizable authentication middleware for FastAPI. This guide provides detailed information about the various components of the library, including middleware, backend, configuration options, and JWT handling.

## 📚 Table of Contents

- [🚀 FastAPI Auth JWT Documentation](#-fastapi-auth-jwt-documentation)
  - [📚 Table of Contents](#-table-of-contents)
  - [🌟 Introduction](#-introduction)
  - [🛡️ Middleware](#️-middleware)
    - [JWTAuthenticationMiddleware](#jwtauthenticationmiddleware)
      - [🔗 Backend](#-backend)
      - [🚫 Exclude URLs](#-exclude-urls)
      - [🛠️ Methods](#️-methods)
      - [🧩 Examples](#-examples)
  - [⚙️ Backend](#️-backend)
    - [JWTAuthBackend](#jwtauthbackend)
      - [📑 Properties](#-properties)
      - [🛠️ Methods](#️-methods-1)
      - [🧩 Examples](#-examples-1)
  - [⚙️ Configuration](#️-configuration)
  - [🔐 JWT Handler](#-jwt-handler)
    - [JWTHandler](#jwthandler)
      - [📑 Properties](#-properties-1)
      - [🛠️ Methods](#️-methods-2)
      - [🧩 Examples](#-examples-2)

## 🌟 Introduction

**FastAPI-Auth-JWT** is an authentication middleware designed to integrate seamlessly with FastAPI applications. It provides JSON Web Token (JWT) authentication with easy configuration and customization options. The following sections guide you through the different modules and their usage.

## 🛡️ Middleware

### JWTAuthenticationMiddleware

`JWTAuthenticationMiddleware` is a middleware class that handles JWT authentication in FastAPI applications. This middleware intercepts incoming requests to apply JWT authentication, allowing for customized authentication processes and token validation before the request reaches the application logic.

#### 🔗 Backend

The backend used for JWT authentication.

- **Type:** [JWTAuthBackend](#jwtauthbackend)

#### 🚫 Exclude URLs

A list of URL paths that are excluded from authentication.

- **Type:** `List[str]`

#### 🛠️ Methods

- **`dispatch(request, call_next)`**  
  Handle incoming requests and apply JWT authentication. Processes each request, extracting and validating the JWT token. If authentication fails, an appropriate error response is returned; otherwise, the request proceeds to the next handler.
  - **Parameters:**
    - `request (Request)`: The FastAPI request object.
    - `call_next (Callable[[Request], Awaitable[Response]])`: The next request handler.
  - **Returns:** `Response` object after processing the request.
  - **Return type:** `Response`

- **`extract_token_from_request(request)`**  
  Extract the JWT token from the request’s Authorization header or cookies.
  - **Parameters:**
    - `request (Request)`: The FastAPI request object.
  - **Returns:** The extracted JWT token.
  - **Return type:** `str`
  - **Raises:** `HTTPException` if the Authorization header is missing or invalid.

#### 🧩 Examples

```python
request = Request(...)  # Assume a FastAPI request object with a valid header
token = JWTAuthenticationMiddleware.extract_token_from_request(request)
print(token)  # Output: 'eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...'
```

## ⚙️ Backend

### JWTAuthBackend

`JWTAuthBackend` is a backend class for handling JWT-based authentication. It provides methods for creating, validating, and invalidating JWT tokens, supporting configurable authentication settings, user schemas, and storage backends.

#### 📑 Properties

- **`config` (AuthConfig):** Configuration for authentication (e.g., secret key, algorithm).
- **`user_schema` (Type[BaseModel]):** Schema for validating user data.
- **`storage_config` (StorageConfig):** Configuration for the storage backend.
- **`cache` (BaseRepository):** Cache repository for storing and retrieving token data.
- **`jwt_handler` ([JWTHandler](#jwthandler)):** Handler for encoding and decoding JWT tokens.

#### 🛠️ Methods

- **`authenticate(token)`**  
  Authenticate a user based on a provided JWT token.
  - **Parameters:**
    - `token (str)`: The JWT token to authenticate.
  - **Returns:** The authenticated user model, or `None` if authentication fails.
  - **Return type:** `Optional[BaseModel]`
  - **Raises:**
    - `jwt.PyJWTError` if there is an issue with decoding the JWT token.
    - `Exception` for any other unexpected errors.

- **`create_token(payload, expiration=None)`**  
  Create a JWT token with an optional expiration time.
  - **Parameters:**
    - `payload (Dict[str, Any])`: The payload data to encode into the JWT.
    - `expiration (Optional[Union[int, float, datetime.timedelta]])`: Expiration time in seconds or timedelta.
  - **Returns:** The generated JWT token.
  - **Return type:** `str`
  - **Raises:** `Exception` if there is an issue storing the token in the cache.

- **`get_current_user(token)`**  
  Retrieve the current user based on a JWT token.
  - **Parameters:**
    - `token (str)`: The JWT token to decode and validate.
  - **Returns:** The validated user model, or `None` if validation fails.
  - **Return type:** `Optional[BaseModel]`
  - **Raises:**
    - `jwt.InvalidTokenError` if the token payload does not match the cached payload.
    - `Exception` for any other unexpected errors.

- **`invalidate_token(token)`**  
  Invalidate a JWT token by removing it from the cache.
  - **Parameters:**
    - `token (str)`: The JWT token to invalidate.
  - **Return type:** `None`

- **`get_instance()`**  
  Get the singleton instance of the JWTAuthBackend class.
  - **Returns:** The singleton instance.
  - **Return type:** `Optional[JWTAuthBackend]`

#### 🧩 Examples

```python
backend = JWTAuthBackend()

# Authenticate a user
user = await backend.authenticate("some_jwt_token")
if user:
    print(f"Authenticated user: {user}")

# Create a JWT token
token = await backend.create_token({"user_id": 123}, expiration=3600)
print(f"Generated token: {token}")

# Get the current user
user = await backend.get_current_user("some_jwt_token")
if user:
    print(f"Current user: {user}")

# Invalidate a token
await backend.invalidate_token("some_jwt_token")

# Get singleton instance
backend_instance = JWTAuthBackend.get_instance()
if backend_instance:
    print("JWTAuthBackend instance exists.")
```

## ⚙️ Configuration

Configuration options for **FastAPI-Auth-JWT** include settings for JWT encoding/decoding, authentication backends, and storage backends. Refer to specific class and method documentation for detailed configuration options.

## 🔐 JWT Handler

### JWTHandler

`JWTHandler` is a handler class for encoding and decoding JWT tokens. It provides methods to encode a payload into a JWT token and decode a JWT token back into a payload. The handler supports setting an expiration time and handles various exceptions during the encoding and decoding process.

#### 📑 Properties

- **`secret (str):`** The secret key used for encoding and decoding the JWT.
- **`algorithm (str):`** The algorithm used for encoding and decoding the JWT. Defaults to `'HS256'`.

#### 🛠️ Methods

- **`decode(token, **kwargs)`**  
  Decode a JWT token into a payload. This method decodes a given JWT token back into its payload, removing the expiration field (`'exp'`) if it exists.
  - **Parameters:**
    - `token (str)`: The JWT token to decode.
  - **Returns:** The decoded payload.
  - **Return type:** `Dict[str, Any]`
  - **Raises:**
    - `jwt.PyJWTError` if an error occurs during decoding.
    - `Exception` if any other unexpected error occurs.

- **`encode(payload, expiration=None, **kwargs)`**  
  Encode a payload into a JWT token, optionally setting an expiration time. Additional key-value pairs can be passed as `kwargs` to be included in the payload.
  - **Parameters:**
    - `payload (Dict[str, Any])`: The payload data to encode into the JWT.
    - `expiration (Optional[Union[float, int]])`: Optional expiration time in seconds. Defaults to `None`.
  - **Returns:** The encoded JWT token.
  - **Return type:** `str`
  - **Raises:**
    - `TypeError` if the payload contains an invalid type.
    - `jwt.PyJWTError` if an error occurs during encoding.
    - `Exception` if any other unexpected error occurs.

#### 🧩 Examples

```python
handler = JWTHandler(secret="mysecret")

# Encode a payload
token = handler.encode({"user_id": 123}, expiration=3600)
print(token)  # Output: 'eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9...'

# Decode a token
payload = handler.decode(token)
print(payload)  # Output: {'user_id': 123}

# Encode with additional fields in the payload
token = handler.encode({"user_id": 123, "role": "admin"}, expiration=3600

)
print(token)
```
