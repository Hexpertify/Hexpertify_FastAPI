import pytest

pytestmark = pytest.mark.asyncio


async def test_create_role(client, admin_token):
    response = await client.post(
        "/api/v1/roles/",
        json={"code": "MANAGER_TEST", "name": "Manager Test", "description": "A test role"},
        headers={"Authorization": f"Bearer {admin_token}"}
    )
    assert response.status_code == 201
    data = response.json()
    assert data["code"] == "MANAGER_TEST"
    assert "id" in data


async def test_create_duplicate_role_fails(client, admin_token):
    payload = {"code": "DUP_ROLE", "name": "Dup Role"}
    headers = {"Authorization": f"Bearer {admin_token}"}
    await client.post("/api/v1/roles/", json=payload, headers=headers)
    response = await client.post("/api/v1/roles/", json=payload, headers=headers)
    assert response.status_code == 409


async def test_get_role_by_id(client, admin_token):
    headers = {"Authorization": f"Bearer {admin_token}"}
    create_resp = await client.post("/api/v1/roles/", json={"code": "GET_TEST", "name": "Get Test"}, headers=headers)
    role_id = create_resp.json()["id"]

    response = await client.get(f"/api/v1/roles/{role_id}")
    assert response.status_code == 200
    assert response.json()["code"] == "GET_TEST"


async def test_get_nonexistent_role_returns_404(client):
    fake_id = "00000000-0000-0000-0000-000000000000"
    response = await client.get(f"/api/v1/roles/{fake_id}")
    assert response.status_code == 404


async def test_list_roles(client, admin_token):
    headers = {"Authorization": f"Bearer {admin_token}"}
    await client.post("/api/v1/roles/", json={"code": "LIST_TEST", "name": "List Test"}, headers=headers)
    response = await client.get("/api/v1/roles/")
    assert response.status_code == 200
    assert isinstance(response.json(), list)
    assert len(response.json()) >= 1


async def test_update_role(client, admin_token):
    headers = {"Authorization": f"Bearer {admin_token}"}
    create_resp = await client.post("/api/v1/roles/", json={"code": "UPDATE_TEST", "name": "Before Update"}, headers=headers)
    role_id = create_resp.json()["id"]

    response = await client.put(f"/api/v1/roles/{role_id}", json={"name": "After Update"}, headers=headers)
    assert response.status_code == 200
    assert response.json()["name"] == "After Update"


async def test_delete_role(client, admin_token):
    headers = {"Authorization": f"Bearer {admin_token}"}
    create_resp = await client.post("/api/v1/roles/", json={"code": "DELETE_TEST", "name": "Delete Test"}, headers=headers)
    role_id = create_resp.json()["id"]

    delete_resp = await client.delete(f"/api/v1/roles/{role_id}", headers=headers)
    assert delete_resp.status_code == 204

    get_resp = await client.get(f"/api/v1/roles/{role_id}")
    assert get_resp.status_code == 404