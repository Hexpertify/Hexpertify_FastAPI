import pytest

pytestmark = pytest.mark.asyncio


async def test_create_user(client):
    response = await client.post("/api/v1/users/", json={
        "first_name": "John",
        "last_name": "Doe",
        "email": "john@example.com",
        "phone": "1234567890",
        "password": "securepass123"
    })
    assert response.status_code == 201
    data = response.json()
    assert data["email"] == "john@example.com"
    assert "password" not in data
    assert "password_hash" not in data


async def test_create_duplicate_email_fails(client):
    payload = {
        "first_name": "Jane",
        "last_name": "Doe",
        "email": "dup@example.com",
        "password": "securepass123"
    }
    await client.post("/api/v1/users/", json=payload)
    response = await client.post("/api/v1/users/", json=payload)
    assert response.status_code == 409


async def test_get_user_by_id(client):
    create_resp = await client.post("/api/v1/users/", json={
        "first_name": "Get",
        "last_name": "Test",
        "email": "gettest@example.com",
        "password": "securepass123"
    })
    user_id = create_resp.json()["id"]

    response = await client.get(f"/api/v1/users/{user_id}")
    assert response.status_code == 200
    assert response.json()["email"] == "gettest@example.com"


async def test_get_nonexistent_user_returns_404(client):
    fake_id = "00000000-0000-0000-0000-000000000000"
    response = await client.get(f"/api/v1/users/{fake_id}")
    assert response.status_code == 404


async def test_list_users(client):
    await client.post("/api/v1/users/", json={
        "first_name": "List",
        "last_name": "Test",
        "email": "listtest@example.com",
        "password": "securepass123"
    })
    response = await client.get("/api/v1/users/")
    assert response.status_code == 200
    assert isinstance(response.json(), list)
    assert len(response.json()) >= 1


async def test_update_user(client):
    create_resp = await client.post("/api/v1/users/", json={
        "first_name": "Before",
        "last_name": "Update",
        "email": "updatetest@example.com",
        "password": "securepass123"
    })
    user_id = create_resp.json()["id"]

    response = await client.put(f"/api/v1/users/{user_id}", json={"first_name": "After"})
    assert response.status_code == 200
    assert response.json()["first_name"] == "After"


async def test_delete_user(client):
    create_resp = await client.post("/api/v1/users/", json={
        "first_name": "Delete",
        "last_name": "Test",
        "email": "deletetest@example.com",
        "password": "securepass123"
    })
    user_id = create_resp.json()["id"]

    delete_resp = await client.delete(f"/api/v1/users/{user_id}")
    assert delete_resp.status_code == 204

    get_resp = await client.get(f"/api/v1/users/{user_id}")
    assert get_resp.status_code == 404