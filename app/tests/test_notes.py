"""
Тесты для заметок.
"""
import pytest
from httpx import AsyncClient


@pytest.mark.asyncio
async def test_create_note(client: AsyncClient, test_user: dict):
    """Тест создания заметки."""
    note_data = {
        "title": "Test Note",
        "content": "This is a test note content."
    }

    headers = {"Authorization": f"Bearer {test_user['access_token']}"}

    response = await client.post(
        "/api/v1/notes/",
        json=note_data,
        headers=headers
    )

    assert response.status_code == 201
    data = response.json()
    assert data["title"] == note_data["title"]
    assert data["content"] == note_data["content"]
    assert data["owner_id"] == test_user["user_id"]
    assert "id" in data


@pytest.mark.asyncio
async def test_get_notes(client: AsyncClient, test_user: dict):
    """Тест получения списка заметок."""
    # Сначала создаем несколько заметок
    headers = {"Authorization": f"Bearer {test_user['access_token']}"}

    for i in range(3):
        await client.post(
            "/api/v1/notes/",
            json={"title": f"Note {i}", "content": f"Content {i}"},
            headers=headers
        )
    # Получаем список заметок
    response = await client.get("/api/v1/notes/", headers=headers)

    assert response.status_code == 200
    data = response.json()
    assert len(data) == 3
    assert all(note["owner_id"] == test_user["user_id"] for note in data)


@pytest.mark.asyncio
async def test_get_note_unauthorized(client: AsyncClient):
    """Тест получения заметки без авторизации."""
    response = await client.get("/api/v1/notes/")

    assert response.status_code == 401  # Unauthorized


@pytest.mark.asyncio
async def test_update_note(client: AsyncClient, test_user: dict):
    """Тест обновления заметки."""
    # Создаем заметку
    headers = {"Authorization": f"Bearer {test_user['access_token']}"}

    create_response = await client.post(
        "/api/v1/notes/",
        json={"title": "Original", "content": "Original content"},
        headers=headers
    )
    note_id = create_response.json()["id"]
    # Обновляем заметку
    update_data = {"title": "Updated", "content": "Updated content"}

    response = await client.put(
        f"/api/v1/notes/{note_id}",
        json=update_data,
        headers=headers
    )

    assert response.status_code == 200
    data = response.json()
    assert data["title"] == update_data["title"]
    assert data["content"] == update_data["content"]


@pytest.mark.asyncio
async def test_delete_note(client: AsyncClient, test_user: dict):
    """Тест удаления заметки."""
    # Создаем заметку
    headers = {"Authorization": f"Bearer {test_user['access_token']}"}

    create_response = await client.post(
        "/api/v1/notes/",
        json={"title": "To Delete", "content": "Will be deleted"},
        headers=headers
    )
    note_id = create_response.json()["id"]
    # Удаляем заметку
    response = await client.delete(f"/api/v1/notes/{note_id}", headers=headers)

    assert response.status_code == 204
    # Проверяем, что заметка удалена
    get_response = await client.get(f"/api/v1/notes/{note_id}", headers=headers)
    assert get_response.status_code == 404