# FastAPI Auth JWT

<p align="center">
  <img src="https://raw.githubusercontent.com/deepmancer/fastapi-auth-jwt/main/fastapi_auth_jwt_logo.png" alt="FastAPI Auth JWT">
</p>

<p align="center">
    <em>Highly-customizable and ready-to-use session authentication for FastAPI applications </em>
</p>

<p align="center">
    <a href="https://github.com/deepmancer/fastapi-auth-jwt/actions/" target="_blank">
        <img src="https://github.com/deepmancer/fastapi-auth-jwt/workflows/Build/badge.svg" alt="Build Status">
    </a>
    <a href="https://pypi.org/project/fastapi-auth-jwt/" target="_blank">
        <img src="https://img.shields.io/pypi/v/fastapi-auth-jwt.svg" alt="Package version">
    </a>
    <a href="https://codecov.io/gh/deepmancer/fastapi-auth-jwt" target="_blank">
        <img src="https://codecov.io/gh/deepmancer/fastapi-auth-jwt/branch/main/graph/badge.svg" alt="Coverage">
    </a>
    <a href="https://github.com/deepmancer/fastapi-auth-jwt/blob/main/LICENSE" target="_blank">
        <img src="https://img.shields.io/github/license/deepmancer/fastapi-auth-jwt.svg" alt="License">
    </a>
</p>

## **✨ Features**

- 🚀 **Effortless Integration**: Seamlessly add JWT authentication to your FastAPI application with just a few lines of code.
- 🛠️ **Highly Customizable**: Tailor the authentication process to fit your specific needs, including custom user models and storage options.
- 🔄 **Sync and Async Support**: Works out of the box with both synchronous and asynchronous FastAPI applications.
- 💾 **Flexible Token Storage**: Supports in-memory token storage for simple applications and Redis for real-world, distributed backends.

## **📦 Installation**

To install the basic package:

```bash
pip install fastapi-auth-jwt
```

If you want to use Redis for token storage, install the package with Redis support:

```bash
pip install fastapi-auth-jwt[redis]
```

## **🚀 Quick Start**

### **🛠️ Basic Setup**

1. **🧑‍💻 Define Your User Schema**: Create a Pydantic model representing the user.

```python
from pydantic import BaseModel, Field

class User(BaseModel):
    username: str
    password: str
    token: Optional[str] = Field(None)
```

2. **⚙️ Configure Authentication Settings**: Set up your authentication configuration.

```python
from pydantic import BaseModel

class AuthenticationSettings(BaseModel):
    secret: str = "your-secret-key"
    jwt_algorithm: str = "HS256"
    expiration_seconds: int = 3600  # 1 hour
```

3. **🔧 Initialize the Authentication Backend**: Create an instance of the `JWTAuthBackend`.

```python
from fastapi_auth_jwt import JWTAuthBackend

auth_backend = JWTAuthBackend(
    authentication_config=AuthenticationSettings(),
    user_schema=User
)
```

4. **🔌 Add Middleware to Your FastAPI Application**:

```python
from fastapi import FastAPI
from fastapi_auth_jwt import JWTAuthenticationMiddleware

app = FastAPI()

app.add_middleware(
    JWTAuthenticationMiddleware,
    backend=auth_backend,
    exclude_urls=["/sign-up", "/login"],
)
```

5. **📚 Create Routes**:

```python
@app.post("/sign-up")
async def sign_up(request_data: RegisterSchema):
    return {"message": "User created"}

@app.post("/login")
async def login(request_data: LoginSchema):
    token = await auth_backend.create_token(
        username=request_data.username,
        password=request_data.password,
    )
    return {"token": token}

@app.get("/profile-info")
async def get_profile_info(request: Request):
    user: User = request.state.user
    return {"username": user.username}

@app.post("/logout")
async def logout(request: Request):
    user: User = request.state.user
    await auth_backend.invalidate_token(user.token)
    return {"message": "Logged out"}
```

### **🧰 Redis Extension**

To enable Redis as the storage backend:

```python
from fastapi_auth_jwt import RedisConfig, JWTAuthBackend

redis_config = RedisConfig(
    host="localhost",
    port=6379,
    db=0,
)

auth_backend_redis = JWTAuthBackend(
    authentication_config=AuthenticationSettings(),
    user_schema=User,
    storage_config=redis_config,
)

app.add_middleware(
    JWTAuthenticationMiddleware,
    backend=auth_backend_redis,
    exclude_urls=["/sign-up", "/login"],
)
```

## **⚙️ Configuration Options**

### `AuthConfig`

- 🛡️ `secret` (str): Secret key for signing JWT tokens.
- 🧮 `jwt_algorithm` (str): Algorithm used for token encoding (default: `HS256`).
- ⏲️ `expiration_seconds` (int): Token expiration time in seconds (default: `3600`).

### `StorageConfig`

- 🗄️ `storage_type` (StorageTypes): Type of storage backend (`MEMORY` or `REDIS`).

### `RedisConfig`

- 🌐 `host` (str): Redis server hostname (default: `localhost`).
- 🛠️ `port` (int): Redis server port (default: `6379`).
- 🗃️ `db` (int): Redis database index (default: `0`).
- 🔑 `password` (Optional[str]): Redis server password (default: `None`).

## **📂 Example Projects**

For fully working examples, refer to the [examples directory](https://github.com/deepmancer/fastapi-auth-jwt/tree/main/examples) in the repository.

## **📚 Documentation**

Complete documentation is available in the [docs directory](https://github.com/deepmancer/fastapi-auth-jwt/blob/main/docs/README.md).

## **📝 License**

This project is licensed under the MIT License. See the [LICENSE](LICENSE) file for details.

## **📬 Contact**

For any questions, suggestions, or issues, please feel free to open an issue or reach out via [GitHub Issues](https://github.com/deepmancer/fastapi-auth-jwt/issues).

---

With `fastapi-auth-jwt`, adding secure, flexible JWT-based authentication to your FastAPI applications is easier than ever. Get started today and enjoy a streamlined authentication experience!
