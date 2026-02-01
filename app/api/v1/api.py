"""
Основной роутер API v1.
"""

from fastapi import APIRouter
from app.api.v1.endpoints import auth, notes

api_router = APIRouter()
# Подключаем эндпоинты
api_router.include_router(auth.router, prefix="/auth", tags=["Authentication"])
api_router.include_router(notes.router, prefix="/notes", tags=["Notes"])
