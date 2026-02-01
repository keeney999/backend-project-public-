"""
Pydantic схемы для пользователей.
"""

from datetime import datetime
from typing import Optional
from pydantic import BaseModel, EmailStr, Field, ConfigDict


class UserBase(BaseModel):
    """Базовая схема пользователя."""

    email: EmailStr
    is_active: Optional[bool] = True


class UserCreate(UserBase):
    """Схема для создания пользователя."""

    password: str = Field(..., min_length=8, max_length=50)


class UserUpdate(BaseModel):
    """Схема для обновления пользователя."""

    email: Optional[EmailStr] = None
    password: Optional[str] = Field(None, min_length=8, max_length=50)
    is_active: Optional[bool] = None


class UserInDB(UserBase):
    """Схема пользователя в БД."""

    id: int
    created_at: datetime

    model_config = ConfigDict(from_attributes=True)


class UserResponse(UserInDB):
    """Схема ответа с пользователем."""

    pass


class Token(BaseModel):
    """Схема JWT токена."""

    access_token: str
    token_type: str = "bearer"


class TokenData(BaseModel):
    """Данные внутри JWT токена."""

    user_id: Optional[int] = None
