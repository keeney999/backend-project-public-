"""
Pydantic схемы для заметок.
"""

from datetime import datetime
from typing import Optional
from pydantic import BaseModel, Field, ConfigDict


class NoteBase(BaseModel):
    """Базовая схема заметки."""

    title: str = Field(..., min_length=1, max_length=255)
    content: Optional[str] = None


class NoteCreate(NoteBase):
    """Схема для создания заметки."""

    pass


class NoteUpdate(BaseModel):
    """Схема для обновления заметки."""

    title: Optional[str] = Field(None, min_length=1, max_length=255)
    content: Optional[str] = None


class NoteInDB(NoteBase):
    """Схема заметки в БД."""

    id: int
    owner_id: int
    created_at: datetime
    updated_at: datetime

    model_config = ConfigDict(from_attributes=True)


class NoteResponse(NoteInDB):
    """Схема ответа с заметкой."""

    pass
