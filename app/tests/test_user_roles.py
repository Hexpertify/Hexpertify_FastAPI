import pytest

pytestmark = pytest.mark.asyncio


async def _create_user(client, email="urtest@example.com"):
    resp = await client.post("/api/v1/users/", json={
        "first_name": "UR", "last_name": "Test", "email": email, "password": "testpass123"
    })
    return resp.json()["id"]


async def _create_role(client, code="UR_TEST_ROLE"):
    resp = await client.post("/api/v1/roles/", json={"code": code, "name": "UR Test Role"})
    return resp.json()["id"]


async def test_assign_role_to_user(client):
    user_id = await _create_user(client, "assign1@example.com")
    role_id = await _create_role(client, "ASSIGN_ROLE_1")

    response = await client.post(f"/api/v1/users/{user_id}/roles", json={"role_id": role_id})
    assert response.status_code == 201
    roles = response.json()
    assert any(r["id"] == role_id for r in roles)


async def test_assign_duplicate_role_fails(client):
    user_id = await _create_user(client, "assign2@example.com")
    role_id = await _create_role(client, "ASSIGN_ROLE_2")

    await client.post(f"/api/v1/users/{user_id}/roles", json={"role_id": role_id})
    response = await client.post(f"/api/v1/users/{user_id}/roles", json={"role_id": role_id})
    assert response.status_code == 409


async def test_assign_role_to_nonexistent_user_fails(client):
    fake_user_id = "00000000-0000-0000-0000-000000000000"
    role_id = await _create_role(client, "ASSIGN_ROLE_3")

    response = await client.post(f"/api/v1/users/{fake_user_id}/roles", json={"role_id": role_id})
    assert response.status_code == 404


async def test_get_user_roles(client):
    user_id = await _create_user(client, "getroles@example.com")
    role_id = await _create_role(client, "GET_ROLES_TEST")
    await client.post(f"/api/v1/users/{user_id}/roles", json={"role_id": role_id})

    response = await client.get(f"/api/v1/users/{user_id}/roles")
    assert response.status_code == 200
    assert any(r["id"] == role_id for r in response.json())


async def test_replace_user_roles(client):
    user_id = await _create_user(client, "replace@example.com")
    role_id_1 = await _create_role(client, "REPLACE_ROLE_1")
    role_id_2 = await _create_role(client, "REPLACE_ROLE_2")

    await client.post(f"/api/v1/users/{user_id}/roles", json={"role_id": role_id_1})
    response = await client.put(f"/api/v1/users/{user_id}/roles", json={"role_ids": [role_id_2]})
    assert response.status_code == 200
    roles = response.json()
    assert len(roles) == 1
    assert roles[0]["id"] == role_id_2


async def test_remove_user_role(client):
    user_id = await _create_user(client, "remove@example.com")
    role_id = await _create_role(client, "REMOVE_ROLE_TEST")
    await client.post(f"/api/v1/users/{user_id}/roles", json={"role_id": role_id})

    delete_resp = await client.delete(f"/api/v1/users/{user_id}/roles/{role_id}")
    assert delete_resp.status_code == 204

    get_resp = await client.get(f"/api/v1/users/{user_id}/roles")
    assert get_resp.json() == []


async def test_remove_unassigned_role_returns_404(client):
    user_id = await _create_user(client, "removefail@example.com")
    role_id = await _create_role(client, "REMOVE_FAIL_ROLE")

    response = await client.delete(f"/api/v1/users/{user_id}/roles/{role_id}")
    assert response.status_code == 404