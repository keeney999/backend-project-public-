"""
Эндпоинты для заметок.
"""
from typing import Annotated, List
from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.ext.asyncio import AsyncSession
from app.db.database import get_db
from app.api.deps import get_current_user
from app.db.models import User
from app.schemas.note import NoteCreate, NoteUpdate, NoteResponse
from app.crud.note import note as note_crud


router = APIRouter()


@router.get("/", response_model=List[NoteResponse])
async def read_notes(
    db: Annotated[AsyncSession, Depends(get_db)],
    current_user: Annotated[User, Depends(get_current_user)],
    skip: Annotated[int, Query(ge=0)] = 0,
    limit: Annotated[int, Query(ge=1, le=100)] = 100
) -> List[dict]:
    """
    Получает список заметок текущего пользователя.

    Args:
        db: Сессия БД
        current_user: Текущий пользователь
        skip: Сколько записей пропустить
        limit: Максимальное количество записей

    Returns:
        List[dict]: Список заметок
    """
    notes = await note_crud.get_multi(
        db,
        owner_id=current_user.id,
        skip=skip,
        limit=limit
    )

    return notes


@router.post("/", response_model=NoteResponse, status_code=status.HTTP_201_CREATED)
async def create_note(
    note_in: NoteCreate,
    db: Annotated[AsyncSession, Depends(get_db)],
    current_user: Annotated[User, Depends(get_current_user)]
) -> dict:
    """
    Создает новую заметку.

    Args:
        note_in: Данные для заметки
        db: Сессия БД
        current_user: Текущий пользователь

    Returns:
        dict: Созданная заметка
    """
    note = await note_crud.create(
        db,
        note_in=note_in,
        owner_id=current_user.id
    )

    return note


@router.get("/{note_id}", response_model=NoteResponse)
async def read_note(
    note_id: int,
    db: Annotated[AsyncSession, Depends(get_db)],
    current_user: Annotated[User, Depends(get_current_user)]
) -> dict:
    """
    Получает заметку по ID.

    Args:
        note_id: ID заметки
        db: Сессия БД
        current_user: Текущий пользователь

    Returns:
        dict: Заметка

    Raises:
        HTTPException: Если заметка не найдена или нет прав доступа
    """
    note = await note_crud.get_by_id(
        db,
        note_id=note_id,
        owner_id=current_user.id
    )

    if not note:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Note not found"
        )

    return note


@router.put("/{note_id}", response_model=NoteResponse)
async def update_note(
    note_id: int,
    note_in: NoteUpdate,
    db: Annotated[AsyncSession, Depends(get_db)],
    current_user: Annotated[User, Depends(get_current_user)]
) -> dict:
    """
    Обновляет заметку.

    Args:
        note_id: ID заметки
        note_in: Новые данные
        db: Сессия БД
        current_user: Текущий пользователь

    Returns:
        dict: Обновленная заметка

    Raises:
        HTTPException: Если заметка не найдена или нет прав доступа
    """
    # Получаем заметку
    note = await note_crud.get_by_id(
        db,
        note_id=note_id,
        owner_id=current_user.id
    )

    if not note:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Note not found"
        )
    # Обновляем заметку
    updated_note = await note_crud.update(db, db_note=note, note_in=note_in)

    return updated_note


@router.delete("/{note_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_note(
    note_id: int,
    db: Annotated[AsyncSession, Depends(get_db)],
    current_user: Annotated[User, Depends(get_current_user)]
) -> None:
    """
    Удаляет заметку.

    Args:
        note_id: ID заметки
        db: Сессия БД
        current_user: Текучный пользователь

    Raises:
        HTTPException: Если заметка не найдена или нет прав доступа
    """
    # Получаем заметку
    note = await note_crud.get_by_id(
        db,
        note_id=note_id,
        owner_id=current_user.id
    )

    if not note:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Note not found"
        )
    # Удаляем заметку
    await note_crud.delete(db, db_note=note)