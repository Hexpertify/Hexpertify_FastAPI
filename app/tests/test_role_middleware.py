import pytest

pytestmark = pytest.mark.asyncio


async def _create_user_and_login(client, email, password="testpass123"):
    await client.post("/api/v1/users/", json={
        "first_name": "MW", "last_name": "Test", "email": email, "password": password
    })
    login_resp = await client.post("/api/v1/auth/login", json={"email": email, "password": password})
    return login_resp.json()["access_token"]


async def test_create_role_without_admin_role_fails(client):
    access_token = await _create_user_and_login(client, "noadmin@example.com")

    response = await client.post(
        "/api/v1/roles/",
        json={"code": "NO_ADMIN_TEST", "name": "No Admin Test"},
        headers={"Authorization": f"Bearer {access_token}"}
    )
    assert response.status_code == 403


async def test_create_role_without_token_fails(client):
    response = await client.post(
        "/api/v1/roles/",
        json={"code": "NO_TOKEN_TEST", "name": "No Token Test"}
    )
    assert response.status_code in (401, 403)