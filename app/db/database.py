"""
Настройка подключения к базе данных.
"""
from typing import AsyncGenerator

from sqlalchemy.ext.asyncio import (
    AsyncSession,
    async_sessionmaker,
    create_async_engine
)

from app.core.config import settings
# Асинхронный движок SQLAlchemy
engine = create_async_engine(
    str(settings.DATABASE_URL),
    echo=settings.DEBUG,
    pool_pre_ping=True,  # Проверяет соединение перед использованием
    pool_size=20,
    max_overflow=0
)
# Фабрика асинхронных сессий
AsyncSessionLocal = async_sessionmaker(
    engine,
    class_=AsyncSession,
    expire_on_commit=False
)


async def get_db() -> AsyncGenerator[AsyncSession, None]:
    """
    Dependency для получения асинхронной сессии БД.

    Yields:
        AsyncSession: Асинхронная сессия SQLAlchemy
    """
    async with AsyncSessionLocal() as session:
        try:
            yield session
            await session.commit()
        except Exception:
            await session.rollback()
            raise
        finally:
            await session.close()


async def init_db() -> None:
    """
    Инициализирует базу данных (создает таблицы).
    """
    async with engine.begin() as conn:
        # Создаем все таблицы
        from app.db.models import Base
        await conn.run_sync(Base.metadata.create_all)