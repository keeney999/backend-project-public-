"""
Конфигурация тестов.
"""

import asyncio
from typing import AsyncGenerator, Generator
import pytest
from httpx import AsyncClient
from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine
from sqlalchemy.orm import sessionmaker
from app.main import app
from app.db.database import get_db
from app.db.models import Base

# Тестовая БД (SQLite в памяти)
TEST_DATABASE_URL = "sqlite+aiosqlite:///:memory:"
# Создаем тестовый движок
test_engine = create_async_engine(
    TEST_DATABASE_URL, echo=False, connect_args={"check_same_thread": False}
)
# Создаем фабрику сессий для тестов
TestingSessionLocal = sessionmaker(
    test_engine, class_=AsyncSession, expire_on_commit=False
)


@pytest.fixture(scope="session")
def event_loop() -> Generator[asyncio.AbstractEventLoop, None, None]:
    """Создает event loop для тестов."""
    loop = asyncio.get_event_loop_policy().new_event_loop()
    yield loop
    loop.close()


@pytest.fixture(scope="function", autouse=True)
async def setup_database() -> AsyncGenerator[None, None]:
    """
    Создает и удаляет тестовые таблицы для каждого теста.
    """
    # Создаем таблицы
    async with test_engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)

    yield
    # Удаляем таблицы
    async with test_engine.begin() as conn:
        await conn.run_sync(Base.metadata.drop_all)


@pytest.fixture(scope="function")
async def db_session() -> AsyncGenerator[AsyncSession, None]:
    """
    Создает тестовую сессию БД.
    """
    async with TestingSessionLocal() as session:
        yield session


@pytest.fixture(scope="function")
async def client(db_session: AsyncSession) -> AsyncGenerator[AsyncClient, None]:
    """
    Создает тестовый клиент с подменой зависимости БД.
    """

    # Переопределяем зависимость get_db
    async def override_get_db():
        try:
            yield db_session
        finally:
            await db_session.close()

    app.dependency_overrides[get_db] = override_get_db

    async with AsyncClient(app=app, base_url="http://test") as ac:
        yield ac
    # Очищаем переопределения
    app.dependency_overrides.clear()


@pytest.fixture
async def test_user(client: AsyncClient) -> dict:
    """
    Создает тестового пользователя и возвращает его данные.
    """
    user_data = {"email": "test@example.com", "password": "testpassword123"}
    # Регистрируем пользователя
    response = await client.post("/api/v1/auth/signup", json=user_data)
    assert response.status_code == 201
    # Логинимся для получения токена
    login_response = await client.post(
        "/api/v1/auth/login",
        data={"username": user_data["email"], "password": user_data["password"]},
    )
    assert login_response.status_code == 200

    token_data = login_response.json()

    return {
        **user_data,
        "access_token": token_data["access_token"],
        "user_id": response.json()["id"],
    }
