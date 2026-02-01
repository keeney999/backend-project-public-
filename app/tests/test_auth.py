"""
Тесты для аутентификации.
"""

import pytest
from httpx import AsyncClient


@pytest.mark.asyncio
async def test_signup_success(client: AsyncClient):
    """Тест успешной регистрации."""
    user_data = {"email": "newuser@example.com", "password": "strongpassword123"}

    response = await client.post("/api/v1/auth/signup", json=user_data)

    assert response.status_code == 201
    data = response.json()
    assert data["email"] == user_data["email"]
    assert "id" in data
    assert "hashed_password" not in data  # Пароль не должен возвращаться


@pytest.mark.asyncio
async def test_signup_duplicate_email(client: AsyncClient, test_user: dict):
    """Тест регистрации с существующим email."""
    user_data = {
        "email": test_user["email"],  # Используем email существующего пользователя
        "password": "anotherpassword123",
    }

    response = await client.post("/api/v1/auth/signup", json=user_data)

    assert response.status_code == 400
    assert "already registered" in response.json()["detail"].lower()


@pytest.mark.asyncio
async def test_login_success(client: AsyncClient, test_user: dict):
    """Тест успешного входа."""
    login_data = {"username": test_user["email"], "password": test_user["password"]}

    response = await client.post("/api/v1/auth/login", data=login_data)

    assert response.status_code == 200
    data = response.json()
    assert "access_token" in data
    assert data["token_type"] == "bearer"


@pytest.mark.asyncio
async def test_login_wrong_password(client: AsyncClient, test_user: dict):
    """Тест входа с неверным паролем."""
    login_data = {"username": test_user["email"], "password": "wrongpassword"}

    response = await client.post("/api/v1/auth/login", data=login_data)

    assert response.status_code == 401
    assert "incorrect" in response.json()["detail"].lower()
