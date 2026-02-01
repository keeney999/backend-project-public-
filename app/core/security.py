"""
Утилиты для безопасности: JWT и хеширование паролей.
"""
from datetime import datetime, timedelta
from typing import Optional
from jose import JWTError, jwt
from passlib.context import CryptContext
from app.core.config import settings
# Контекст для хеширования паролей
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")


def verify_password(plain_password: str, hashed_password: str) -> bool:
    """
    Проверяет соответствие пароля его хешу.

    Args:
        plain_password: Обычный пароль
        hashed_password: Хешированный пароль

    Returns:
        bool: True если пароль верный
    """
    return pwd_context.verify(plain_password, hashed_password)


def get_password_hash(password: str) -> str:
    """
    Создает bcrypt хеш пароля.

    Args:
        password: Пароль для хеширования

    Returns:
        str: Хешированный пароль
    """
    return pwd_context.hash(password)


def create_access_token(data: dict, expires_delta: Optional[timedelta] = None) -> str:
    """
    Создает JWT токен доступа.

    Args:
        data: Данные для кодирования в токен
        expires_delta: Время жизни токена

    Returns:
        str: Закодированный JWT токен
    """
    to_encode = data.copy()

    if expires_delta:
        expire = datetime.now() + expires_delta
    else:
        expire = datetime.now() + timedelta(
            minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES
        )

    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(
        to_encode,
        settings.SECRET_KEY,
        algorithm=settings.ALGORITHM
    )

    return encoded_jwt


def decode_access_token(token: str) -> Optional[dict]:
    """
    Декодирует и проверяет JWT токен.

    Args:
        token: JWT токен для проверки

    Returns:
        Optional[dict]: Данные из токена или None если токен невалидный
    """
    try:
        payload = jwt.decode(
            token,
            settings.SECRET_KEY,
            algorithms=[settings.ALGORITHM]
        )
        return payload
    except JWTError:
        return None