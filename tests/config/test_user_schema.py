from fastapi_auth_jwt.config.user_schema import User


def test_user_model():
    user_data = {
        "username": "john_doe",
        "password": "password123",
        "user_id": "123456",
        "role": "admin",
        "phone_number": "1234567890",
        "email": "john@example.com",
        "token": "abc123",
    }
    user = User(**user_data)

    assert user.username == user_data["username"]
    assert user.password == user_data["password"]
    assert user.user_id == user_data["user_id"]
    assert user.role == user_data["role"]
    assert user.phone_number == user_data["phone_number"]
    assert user.email == user_data["email"]
    assert user.token == user_data["token"]


def test_user_model_dynamic_fields():
    user_data = {
        "username": "john_doe",
        "password": "password123",
        "user_id": "123456",
        "role": "admin",
        "phone_number": "1234567890",
        "email": "john@example.com",
        "token": "abc123",
        "dynamic_field": "value",
    }
    user = User(**user_data)

    assert user.dynamic_field == user_data["dynamic_field"]
    assert "dynamic_field" in user.model_dump().keys()
