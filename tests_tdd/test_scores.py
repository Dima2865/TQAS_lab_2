import pytest
from httpx import AsyncClient


@pytest.mark.asyncio
async def test_create_score(client: AsyncClient):
    # Создаём студента и предмет
    student_resp = await client.post("/api/v1/students/", json={"first_name": "Алиса", "last_name": "Соколова",
                                                                "email": "alice@example.com"})
    student_id = student_resp.json()["id"]
    subject_resp = await client.post("/api/v1/subjects/", json={"name": "Программирование"})
    subject_id = subject_resp.json()["id"]

    payload = {
        "student_id": student_id,
        "subject_id": subject_id,
        "score": 95.5
    }
    response = await client.post("/api/v1/scores/", json=payload)
    assert response.status_code == 201
    data = response.json()
    assert data["student_id"] == student_id
    assert data["subject_id"] == subject_id
    assert data["score"] == 95.5
    assert "id" in data
    assert "created_at" in data


@pytest.mark.asyncio
async def test_create_score_duplicate(client: AsyncClient):
    """Нельзя создать две оценки для одного студента по одному предмету"""
    student_resp = await client.post("/api/v1/students/",
                                     json={"first_name": "Борис", "last_name": "Павлов", "email": "boris@example.com"})
    student_id = student_resp.json()["id"]
    subject_resp = await client.post("/api/v1/subjects/", json={"name": "Алгоритмы"})
    subject_id = subject_resp.json()["id"]

    payload = {"student_id": student_id, "subject_id": subject_id, "score": 88}
    await client.post("/api/v1/scores/", json=payload)

    # Вторая попытка
    response = await client.post("/api/v1/scores/", json=payload)
    assert response.status_code == 400
    assert "Score for this student and subject already exists" in response.text


@pytest.mark.asyncio
async def test_create_score_invalid_student(client: AsyncClient):
    subject_resp = await client.post("/api/v1/subjects/", json={"name": "Базы данных"})
    subject_id = subject_resp.json()["id"]
    payload = {"student_id": 9999, "subject_id": subject_id, "score": 70}
    response = await client.post("/api/v1/scores/", json=payload)
    assert response.status_code == 404
    assert "Student not found" in response.text


@pytest.mark.asyncio
async def test_read_scores(client: AsyncClient):
    # Создаём данные
    s1 = await client.post("/api/v1/students/",
                           json={"first_name": "Виктор", "last_name": "Зайцев", "email": "victor@example.com"})
    s2 = await client.post("/api/v1/students/",
                           json={"first_name": "Галина", "last_name": "Морозова", "email": "galina@example.com"})
    subj = await client.post("/api/v1/subjects/", json={"name": "Математический анализ"})
    await client.post("/api/v1/scores/",
                      json={"student_id": s1.json()["id"], "subject_id": subj.json()["id"], "score": 90})
    await client.post("/api/v1/scores/",
                      json={"student_id": s2.json()["id"], "subject_id": subj.json()["id"], "score": 85})

    response = await client.get("/api/v1/scores/")
    assert response.status_code == 200
    data = response.json()
    assert len(data) >= 2


@pytest.mark.asyncio
async def test_update_score(client: AsyncClient):
    student = await client.post("/api/v1/students/",
                                json={"first_name": "Елена", "last_name": "Сергеева", "email": "elena@example.com"})
    subject = await client.post("/api/v1/subjects/", json={"name": "Философия"})
    score_resp = await client.post("/api/v1/scores/",
                                   json={"student_id": student.json()["id"], "subject_id": subject.json()["id"],
                                         "score": 60})
    score_id = score_resp.json()["id"]

    update_payload = {"score": 75}
    response = await client.patch(f"/api/v1/scores/{score_id}", json=update_payload)
    assert response.status_code == 200
    data = response.json()
    assert data["score"] == 75


@pytest.mark.asyncio
async def test_delete_score(client: AsyncClient):
    student = await client.post("/api/v1/students/",
                                json={"first_name": "Жанна", "last_name": "Фёдорова", "email": "zhanna@example.com"})
    subject = await client.post("/api/v1/subjects/", json={"name": "Иностранный язык"})
    score_resp = await client.post("/api/v1/scores/",
                                   json={"student_id": student.json()["id"], "subject_id": subject.json()["id"],
                                         "score": 92})
    score_id = score_resp.json()["id"]

    del_resp = await client.delete(f"/api/v1/scores/{score_id}")
    assert del_resp.status_code == 200
    get_resp = await client.get(f"/api/v1/scores/{score_id}")
    assert get_resp.status_code == 404