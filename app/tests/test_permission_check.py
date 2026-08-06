import pytest

pytestmark = pytest.mark.asyncio


async def _setup_user_with_permission(client, admin_token, email, permission_code):
    headers = {"Authorization": f"Bearer {admin_token}"}

    user_resp = await client.post("/api/v1/users/", json={
        "first_name": "PC", "last_name": "Test", "email": email, "password": "testpass123"
    })
    user_id = user_resp.json()["id"]

    role_resp = await client.post("/api/v1/roles/", json={
        "code": f"PC_ROLE_{email}", "name": "PC Role"
    }, headers=headers)
    role_id = role_resp.json()["id"]

    perm_resp = await client.post("/api/v1/permissions/", json={
        "code": permission_code, "name": "PC Permission"
    }, headers=headers)
    permission_id = perm_resp.json()["id"]

    await client.post(f"/api/v1/roles/{role_id}/permissions", json={"permission_id": permission_id}, headers=headers)
    await client.post(f"/api/v1/users/{user_id}/roles", json={"role_id": role_id}, headers=headers)

    return user_id


async def test_check_permission_user_has_it(client, admin_token):
    user_id = await _setup_user_with_permission(client, admin_token, "pc1@example.com", "pc.test.permission1")
    headers = {"Authorization": f"Bearer {admin_token}"}

    response = await client.post("/api/v1/permissions/check", json={
        "user_id": user_id, "permission_code": "pc.test.permission1"
    }, headers=headers)
    assert response.status_code == 200
    assert response.json()["has_permission"] is True


async def test_check_permission_user_lacks_it(client, admin_token):
    user_id = await _setup_user_with_permission(client, admin_token, "pc2@example.com", "pc.test.permission2")
    headers = {"Authorization": f"Bearer {admin_token}"}

    response = await client.post("/api/v1/permissions/check", json={
        "user_id": user_id, "permission_code": "some.other.permission"
    }, headers=headers)
    assert response.status_code == 200
    assert response.json()["has_permission"] is False


async def test_check_permission_requires_auth(client):
    response = await client.post("/api/v1/permissions/check", json={
        "user_id": "00000000-0000-0000-0000-000000000000",
        "permission_code": "user.create"
    })
    assert response.status_code in (401, 403)


async def test_check_many_permissions(client, admin_token):
    user_id = await _setup_user_with_permission(client, admin_token, "pc3@example.com", "pc.test.permission3")
    headers = {"Authorization": f"Bearer {admin_token}"}

    response = await client.post("/api/v1/permissions/check-many", json={
        "user_id": user_id,
        "permission_codes": ["pc.test.permission3", "nonexistent.permission"]
    }, headers=headers)
    assert response.status_code == 200
    results = response.json()["results"]
    assert results["pc.test.permission3"] is True
    assert results["nonexistent.permission"] is False