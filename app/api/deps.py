"""
Dependencies для API эндпоинтов.
"""

from typing import Optional, Annotated
from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from sqlalchemy.ext.asyncio import AsyncSession
from app.db.database import get_db
from app.core.security import decode_access_token
from app.crud.user import user as user_crud

security = HTTPBearer()


async def get_current_user(
    credentials: Annotated[HTTPAuthorizationCredentials, Depends(security)],
    db: Annotated[AsyncSession, Depends(get_db)],
) -> Optional[dict]:
    """
    Получает текущего аутентифицированного пользователя из JWT токена.

    Args:
        credentials: HTTP Bearer токен
        db: Сессия БД

    Returns:
        Optional[dict]: Данные пользователя

    Raises:
        HTTPException: Если токен невалидный или пользователь не найден
    """
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )
    # Декодируем токен
    payload = decode_access_token(credentials.credentials)
    if payload is None:
        raise credentials_exception
    # Получаем ID пользователя из токена
    user_id: Optional[int] = payload.get("user_id")
    if user_id is None:
        raise credentials_exception
    # Ищем пользователя в БД
    db_user = await user_crud.get_by_id(db, user_id=user_id)
    if db_user is None:
        raise credentials_exception

    return db_user
