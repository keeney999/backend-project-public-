"""
CRUD операции для пользователей.
"""

from typing import Optional
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from app.db.models import User
from app.schemas.user import UserCreate, UserUpdate
from app.core.security import get_password_hash


class UserCRUD:
    """CRUD операции для модели User."""

    @staticmethod
    async def get_by_id(db: AsyncSession, user_id: int) -> Optional[User]:
        """
        Получает пользователя по ID.

        Args:
            db: Сессия БД
            user_id: ID пользователя

        Returns:
            Optional[User]: Объект пользователя или None
        """
        result = await db.execute(select(User).where(User.id == user_id))
        return result.scalar_one_or_none()

    @staticmethod
    async def get_by_email(db: AsyncSession, email: str) -> Optional[User]:
        """
        Получает пользователя по email.

        Args:
            db: Сессия БД
            email: Email пользователя

        Returns:
            Optional[User]: Объект пользователя или None
        """
        result = await db.execute(select(User).where(User.email == email))
        return result.scalar_one_or_none()

    @staticmethod
    async def create(db: AsyncSession, user_in: UserCreate) -> User:
        """
        Создает нового пользователя.

        Args:
            db: Сессия БД
            user_in: Данные для создания пользователя

        Returns:
            User: Созданный пользователь
        """
        # Хешируем пароль
        hashed_password = get_password_hash(user_in.password)

        # Создаем объект пользователя
        db_user = User(
            email=user_in.email,
            hashed_password=hashed_password,
            is_active=user_in.is_active,
        )

        # Сохраняем в БД
        db.add(db_user)
        await db.commit()
        await db.refresh(db_user)

        return db_user

    @staticmethod
    async def update(db: AsyncSession, db_user: User, user_in: UserUpdate) -> User:
        """
        Обновляет данные пользователя.

        Args:
            db: Сессия БД
            db_user: Существующий пользователь
            user_in: Новые данные

        Returns:
            User: Обновленный пользователь
        """
        update_data = user_in.model_dump(exclude_unset=True)

        if "password" in update_data:
            hashed_password = get_password_hash(update_data["password"])
            update_data["hashed_password"] = hashed_password
            del update_data["password"]

        for field, value in update_data.items():
            setattr(db_user, field, value)

        db.add(db_user)
        await db.commit()
        await db.refresh(db_user)

        return db_user

    @staticmethod
    async def delete(db: AsyncSession, db_user: User) -> None:
        """
        Удаляет пользователя.

        Args:
            db: Сессия БД
            db_user: Пользователь для удаления
        """
        await db.delete(db_user)
        await db.commit()


user = UserCRUD()
