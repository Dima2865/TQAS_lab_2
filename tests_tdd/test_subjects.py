import pytest
from httpx import AsyncClient

@pytest.mark.asyncio
async def test_create_subject(client: AsyncClient):
    payload = {"name": "Математика", "description": "Высшая математика"}
    response = await client.post("/api/v1/subjects/", json=payload)
    assert response.status_code == 201
    data = response.json()
    assert data["name"] == payload["name"]
    assert data["description"] == payload["description"]
    assert "id" in data

@pytest.mark.asyncio
async def test_create_subject_duplicate_name(client: AsyncClient):
    payload = {"name": "Физика"}
    await client.post("/api/v1/subjects/", json=payload)
    response = await client.post("/api/v1/subjects/", json={"name": "Физика", "description": "Общая физика"})
    assert response.status_code == 400
    assert "Subject with this name already exists" in response.text

@pytest.mark.asyncio
async def test_read_subjects(client: AsyncClient):
    await client.post("/api/v1/subjects/", json={"name": "Химия"})
    response = await client.get("/api/v1/subjects/")
    assert response.status_code == 200
    data = response.json()
    assert isinstance(data, list)
    assert len(data) > 0

@pytest.mark.asyncio
async def test_read_subject_by_id(client: AsyncClient):
    create_resp = await client.post("/api/v1/subjects/", json={"name": "История"})
    subj_id = create_resp.json()["id"]
    response = await client.get(f"/api/v1/subjects/{subj_id}")
    assert response.status_code == 200
    assert response.json()["id"] == subj_id

@pytest.mark.asyncio
async def test_update_subject(client: AsyncClient):
    create_resp = await client.post("/api/v1/subjects/", json={"name": "Биология", "description": "Наука о жизни"})
    subj_id = create_resp.json()["id"]
    update_payload = {"description": "Изучение живых организмов"}
    response = await client.patch(f"/api/v1/subjects/{subj_id}", json=update_payload)
    assert response.status_code == 200
    data = response.json()
    assert data["description"] == "Изучение живых организмов"
    assert data["name"] == "Биология"

@pytest.mark.asyncio
async def test_delete_subject(client: AsyncClient):
    create_resp = await client.post("/api/v1/subjects/", json={"name": "Информатика"})
    subj_id = create_resp.json()["id"]
    del_resp = await client.delete(f"/api/v1/subjects/{subj_id}")
    assert del_resp.status_code == 200
    get_resp = await client.get(f"/api/v1/subjects/{subj_id}")
    assert get_resp.status_code == 404
