import pytest

pytestmark = pytest.mark.asyncio


async def _create_role(client, admin_token, code="RP_TEST_ROLE"):
    resp = await client.post(
        "/api/v1/roles/", json={"code": code, "name": "RP Test Role"},
        headers={"Authorization": f"Bearer {admin_token}"}
    )
    return resp.json()["id"]


async def _create_permission(client, admin_token, code="rp.test.permission"):
    resp = await client.post(
        "/api/v1/permissions/", json={"code": code, "name": "RP Test Permission"},
        headers={"Authorization": f"Bearer {admin_token}"}
    )
    return resp.json()["id"]


async def test_assign_permission_to_role(client, admin_token):
    headers = {"Authorization": f"Bearer {admin_token}"}
    role_id = await _create_role(client, admin_token, "ASSIGN_PERM_ROLE_1")
    permission_id = await _create_permission(client, admin_token, "assign.perm.1")

    response = await client.post(f"/api/v1/roles/{role_id}/permissions", json={"permission_id": permission_id}, headers=headers)
    assert response.status_code == 201
    permissions = response.json()
    assert any(p["id"] == permission_id for p in permissions)


async def test_assign_duplicate_permission_fails(client, admin_token):
    headers = {"Authorization": f"Bearer {admin_token}"}
    role_id = await _create_role(client, admin_token, "ASSIGN_PERM_ROLE_2")
    permission_id = await _create_permission(client, admin_token, "assign.perm.2")

    await client.post(f"/api/v1/roles/{role_id}/permissions", json={"permission_id": permission_id}, headers=headers)
    response = await client.post(f"/api/v1/roles/{role_id}/permissions", json={"permission_id": permission_id}, headers=headers)
    assert response.status_code == 409


async def test_assign_permission_to_nonexistent_role_fails(client, admin_token):
    headers = {"Authorization": f"Bearer {admin_token}"}
    fake_role_id = "00000000-0000-0000-0000-000000000000"
    permission_id = await _create_permission(client, admin_token, "assign.perm.3")

    response = await client.post(f"/api/v1/roles/{fake_role_id}/permissions", json={"permission_id": permission_id}, headers=headers)
    assert response.status_code == 404


async def test_get_role_permissions(client, admin_token):
    headers = {"Authorization": f"Bearer {admin_token}"}
    role_id = await _create_role(client, admin_token, "GET_PERM_ROLE")
    permission_id = await _create_permission(client, admin_token, "get.perm.test")
    await client.post(f"/api/v1/roles/{role_id}/permissions", json={"permission_id": permission_id}, headers=headers)

    response = await client.get(f"/api/v1/roles/{role_id}/permissions")
    assert response.status_code == 200
    assert any(p["id"] == permission_id for p in response.json())


async def test_replace_role_permissions(client, admin_token):
    headers = {"Authorization": f"Bearer {admin_token}"}
    role_id = await _create_role(client, admin_token, "REPLACE_PERM_ROLE")
    permission_id_1 = await _create_permission(client, admin_token, "replace.perm.1")
    permission_id_2 = await _create_permission(client, admin_token, "replace.perm.2")

    await client.post(f"/api/v1/roles/{role_id}/permissions", json={"permission_id": permission_id_1}, headers=headers)
    response = await client.put(f"/api/v1/roles/{role_id}/permissions", json={"permission_ids": [permission_id_2]}, headers=headers)
    assert response.status_code == 200
    permissions = response.json()
    assert len(permissions) == 1
    assert permissions[0]["id"] == permission_id_2


async def test_remove_role_permission(client, admin_token):
    headers = {"Authorization": f"Bearer {admin_token}"}
    role_id = await _create_role(client, admin_token, "REMOVE_PERM_ROLE")
    permission_id = await _create_permission(client, admin_token, "remove.perm.test")
    await client.post(f"/api/v1/roles/{role_id}/permissions", json={"permission_id": permission_id}, headers=headers)

    delete_resp = await client.delete(f"/api/v1/roles/{role_id}/permissions/{permission_id}", headers=headers)
    assert delete_resp.status_code == 204

    get_resp = await client.get(f"/api/v1/roles/{role_id}/permissions")
    assert get_resp.json() == []


async def test_remove_unassigned_permission_returns_404(client, admin_token):
    headers = {"Authorization": f"Bearer {admin_token}"}
    role_id = await _create_role(client, admin_token, "REMOVE_FAIL_PERM_ROLE")
    permission_id = await _create_permission(client, admin_token, "remove.fail.perm")

    response = await client.delete(f"/api/v1/roles/{role_id}/permissions/{permission_id}", headers=headers)
    assert response.status_code == 404