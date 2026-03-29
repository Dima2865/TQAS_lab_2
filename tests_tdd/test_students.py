import pytest
from httpx import AsyncClient


@pytest.mark.asyncio
async def test_create_student(client: AsyncClient):
    """Создание студента"""
    payload = {
        "first_name": "Иван",
        "last_name": "Петров",
        "email": "ivan@example.com",
        "group_name": "ИТ-11"
    }
    response = await client.post("/api/v1/students/", json=payload)
    assert response.status_code == 201
    data = response.json()
    assert data["first_name"] == payload["first_name"]
    assert data["last_name"] == payload["last_name"]
    assert data["email"] == payload["email"]
    assert data["group_name"] == payload["group_name"]
    assert "id" in data


@pytest.mark.asyncio
async def test_create_student_duplicate_email(client: AsyncClient):
    """Создание студента с уже существующим email"""
    payload = {
        "first_name": "Петр",
        "last_name": "Сидоров",
        "email": "petr@example.com",
        "group_name": "ИТ-12"
    }
    # Создаём первого
    await client.post("/api/v1/students/", json=payload)
    # Пытаемся создать второго с тем же email
    payload2 = {
        "first_name": "Анна",
        "last_name": "Иванова",
        "email": "petr@example.com",
        "group_name": "ИТ-13"
    }
    response = await client.post("/api/v1/students/", json=payload2)
    assert response.status_code == 400
    assert "Email already registered" in response.text


@pytest.mark.asyncio
async def test_read_students(client: AsyncClient):
    """Получение списка студентов"""
    # Создадим пару студентов
    await client.post("/api/v1/students/",
                      json={"first_name": "Анна", "last_name": "Смирнова", "email": "anna@example.com"})
    await client.post("/api/v1/students/",
                      json={"first_name": "Борис", "last_name": "Кузнецов", "email": "boris@example.com"})

    response = await client.get("/api/v1/students/")
    assert response.status_code == 200
    data = response.json()
    assert isinstance(data, list)
    assert len(data) >= 2


@pytest.mark.asyncio
async def test_read_student_by_id(client: AsyncClient):
    """Получение студента по ID"""
    # Создаём студента
    create_resp = await client.post("/api/v1/students/",
                                    json={"first_name": "Ольга", "last_name": "Новикова", "email": "olga@example.com"})
    student_id = create_resp.json()["id"]

    response = await client.get(f"/api/v1/students/{student_id}")
    assert response.status_code == 200
    data = response.json()
    assert data["id"] == student_id
    assert data["email"] == "olga@example.com"


@pytest.mark.asyncio
async def test_read_student_not_found(client: AsyncClient):
    """Получение несуществующего студента"""
    response = await client.get("/api/v1/students/9999")
    assert response.status_code == 404
    assert "Student not found" in response.text


@pytest.mark.asyncio
async def test_update_student(client: AsyncClient):
    """Обновление данных студента"""
    # Создаём
    create_resp = await client.post("/api/v1/students/", json={"first_name": "Дмитрий", "last_name": "Волков",
                                                               "email": "dmitry@example.com"})
    student_id = create_resp.json()["id"]

    # Обновляем
    update_payload = {"last_name": "Орлов", "group_name": "ФИ-21"}
    response = await client.patch(f"/api/v1/students/{student_id}", json=update_payload)
    assert response.status_code == 200
    data = response.json()
    assert data["last_name"] == "Орлов"
    assert data["group_name"] == "ФИ-21"
    # Остальные поля не должны измениться
    assert data["first_name"] == "Дмитрий"
    assert data["email"] == "dmitry@example.com"


@pytest.mark.asyncio
async def test_delete_student(client: AsyncClient):
    """Удаление студента"""
    # Создаём
    create_resp = await client.post("/api/v1/students/",
                                    json={"first_name": "Максим", "last_name": "Лебедев", "email": "max@example.com"})
    student_id = create_resp.json()["id"]

    # Удаляем
    response = await client.delete(f"/api/v1/students/{student_id}")
    assert response.status_code == 200
    # Проверяем, что больше не существует
    get_resp = await client.get(f"/api/v1/students/{student_id}")
    assert get_resp.status_code == 404