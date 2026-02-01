"""
Эндпоинты для аутентификации.
"""

from datetime import timedelta
from typing import Annotated
from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordRequestForm
from sqlalchemy.ext.asyncio import AsyncSession
from app.db.database import get_db
from app.core.config import settings
from app.core.security import verify_password, create_access_token
from app.schemas.user import Token, UserCreate, UserResponse
from app.crud.user import user as user_crud

router = APIRouter()


@router.post(
    "/signup", response_model=UserResponse, status_code=status.HTTP_201_CREATED
)
async def signup(
    user_in: UserCreate, db: Annotated[AsyncSession, Depends(get_db)]
) -> dict:
    """
    Регистрация нового пользователя.

    Args:
        user_in: Данные пользователя
        db: Сессия БД

    Returns:
        dict: Созданный пользователь

    Raises:
        HTTPException: Если пользователь с таким email уже существует
    """
    # Проверяем, существует ли пользователь
    db_user = await user_crud.get_by_email(db, email=user_in.email)
    if db_user:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST, detail="Email already registered"
        )
    # Создаем пользователя
    user = await user_crud.create(db, user_in=user_in)

    return user


@router.post("/login", response_model=Token)
async def login(
    form_data: Annotated[OAuth2PasswordRequestForm, Depends()],
    db: Annotated[AsyncSession, Depends(get_db)],
) -> dict:
    """
    Аутентификация пользователя.

    Args:
        form_data: Данные формы (username=email, password)
        db: Сессия БД

    Returns:
        dict: JWT токен доступа

    Raises:
        HTTPException: Если неверный email или пароль
    """
    # Ищем пользователя по email
    db_user = await user_crud.get_by_email(db, email=form_data.username)
    if not db_user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect email or password",
            headers={"WWW-Authenticate": "Bearer"},
        )
    # Проверяем пароль
    if not verify_password(form_data.password, db_user.hashed_password):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect email or password",
            headers={"WWW-Authenticate": "Bearer"},
        )
    # Проверяем активность пользователя
    if not db_user.is_active:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST, detail="Inactive user"
        )
    # Создаем токен
    access_token_expires = timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)
    access_token = create_access_token(
        data={"user_id": db_user.id}, expires_delta=access_token_expires
    )

    return {"access_token": access_token, "token_type": "bearer"}
