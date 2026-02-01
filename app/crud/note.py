"""
CRUD операции для заметок.
"""
from typing import Optional, List
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from app.db.models import Note, User
from app.schemas.note import NoteCreate, NoteUpdate


class NoteCRUD:
    """CRUD операции для модели Note."""

    @staticmethod
    async def get_by_id(
            db: AsyncSession,
            note_id: int,
            owner_id: Optional[int] = None
    ) -> Optional[Note]:
        """
        Получает заметку по ID.

        Args:
            db: Сессия БД
            note_id: ID заметки
            owner_id: ID владельца (опционально, для проверки прав)

        Returns:
            Optional[Note]: Объект заметки или None
        """
        query = select(Note).where(Note.id == note_id)

        if owner_id:
            query = query.where(Note.owner_id == owner_id)

        result = await db.execute(query)
        return result.scalar_one_or_none()

    @staticmethod
    async def get_multi(
            db: AsyncSession,
            owner_id: int,
            skip: int = 0,
            limit: int = 100
    ) -> List[Note]:
        """
        Получает список заметок пользователя.

        Args:
            db: Сессия БД
            owner_id: ID владельца
            skip: Сколько записей пропустить
            limit: Максимальное количество записей

        Returns:
            List[Note]: Список заметок
        """
        result = await db.execute(
            select(Note)
            .where(Note.owner_id == owner_id)
            .order_by(Note.created_at.desc())
            .offset(skip)
            .limit(limit)
        )

        return result.scalars().all()

    @staticmethod
    async def create(
            db: AsyncSession,
            note_in: NoteCreate,
            owner_id: int
    ) -> Note:
        """
        Создает новую заметку.

        Args:
            db: Сессия БД
            note_in: Данные для создания заметки
            owner_id: ID владельца

        Returns:
            Note: Созданная заметка
        """
        db_note = Note(**note_in.model_dump(), owner_id=owner_id)

        db.add(db_note)
        await db.commit()
        await db.refresh(db_note)

        return db_note

    @staticmethod
    async def update(
            db: AsyncSession,
            db_note: Note,
            note_in: NoteUpdate
    ) -> Note:
        """
        Обновляет заметку.

        Args:
            db: Сессия БД
            db_note: Существующая заметка
            note_in: Новые данные

        Returns:
            Note: Обновленная заметка
        """
        update_data = note_in.model_dump(exclude_unset=True)

        for field, value in update_data.items():
            setattr(db_note, field, value)

        db.add(db_note)
        await db.commit()
        await db.refresh(db_note)

        return db_note

    @staticmethod
    async def delete(db: AsyncSession, db_note: Note) -> None:
        """
        Удаляет заметку.

        Args:
            db: Сессия БД
            db_note: Заметка для удаления
        """
        await db.delete(db_note)
        await db.commit()


note = NoteCRUD()