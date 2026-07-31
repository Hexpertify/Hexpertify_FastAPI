import pytest

pytestmark = pytest.mark.asyncio


async def test_create_permission(client):
    response = await client.post("/api/v1/permissions/", json={
        "code": "user.create",
        "name": "Create User",
        "resource": "user",
        "action": "create"
    })
    assert response.status_code == 201
    data = response.json()
    assert data["code"] == "user.create"
    assert "id" in data


async def test_create_duplicate_permission_fails(client):
    payload = {"code": "dup.perm", "name": "Dup Permission"}
    await client.post("/api/v1/permissions/", json=payload)
    response = await client.post("/api/v1/permissions/", json=payload)
    assert response.status_code == 409


async def test_get_permission_by_id(client):
    create_resp = await client.post("/api/v1/permissions/", json={
        "code": "get.test", "name": "Get Test"
    })
    permission_id = create_resp.json()["id"]

    response = await client.get(f"/api/v1/permissions/{permission_id}")
    assert response.status_code == 200
    assert response.json()["code"] == "get.test"


async def test_get_nonexistent_permission_returns_404(client):
    fake_id = "00000000-0000-0000-0000-000000000000"
    response = await client.get(f"/api/v1/permissions/{fake_id}")
    assert response.status_code == 404


async def test_list_permissions(client):
    await client.post("/api/v1/permissions/", json={"code": "list.test", "name": "List Test"})
    response = await client.get("/api/v1/permissions/")
    assert response.status_code == 200
    assert isinstance(response.json(), list)
    assert len(response.json()) >= 1


async def test_update_permission(client):
    create_resp = await client.post("/api/v1/permissions/", json={
        "code": "update.test", "name": "Before Update"
    })
    permission_id = create_resp.json()["id"]

    response = await client.put(f"/api/v1/permissions/{permission_id}", json={"name": "After Update"})
    assert response.status_code == 200
    assert response.json()["name"] == "After Update"


async def test_delete_permission(client):
    create_resp = await client.post("/api/v1/permissions/", json={
        "code": "delete.test", "name": "Delete Test"
    })
    permission_id = create_resp.json()["id"]

    delete_resp = await client.delete(f"/api/v1/permissions/{permission_id}")
    assert delete_resp.status_code == 204

    get_resp = await client.get(f"/api/v1/permissions/{permission_id}")
    assert get_resp.status_code == 404