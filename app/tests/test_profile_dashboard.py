import pytest

pytestmark = pytest.mark.asyncio


async def _create_and_login(client, email, password="testpass123"):
    await client.post("/api/v1/users/", json={
        "first_name": "PD", "last_name": "Test", "email": email, "password": password
    })
    login_resp = await client.post("/api/v1/auth/login", json={"email": email, "password": password})
    return login_resp.json()["access_token"]


async def test_get_profile(client):
    token = await _create_and_login(client, "profile1@example.com")
    response = await client.get("/api/v1/profile/", headers={"Authorization": f"Bearer {token}"})
    assert response.status_code == 200
    assert response.json()["email"] == "profile1@example.com"


async def test_update_profile(client):
    token = await _create_and_login(client, "profile2@example.com")
    response = await client.put(
        "/api/v1/profile/", json={"first_name": "Changed"},
        headers={"Authorization": f"Bearer {token}"}
    )
    assert response.status_code == 200
    assert response.json()["first_name"] == "Changed"


async def test_profile_requires_auth(client):
    response = await client.get("/api/v1/profile/")
    assert response.status_code in (401, 403)


async def test_get_dashboard(client):
    token = await _create_and_login(client, "dash1@example.com")
    response = await client.get("/api/v1/dashboard/", headers={"Authorization": f"Bearer {token}"})
    assert response.status_code == 200


async def test_get_dashboard_stats(client):
    token = await _create_and_login(client, "dash2@example.com")
    response = await client.get("/api/v1/dashboard/stats", headers={"Authorization": f"Bearer {token}"})
    assert response.status_code == 200
    data = response.json()
    assert "total_users" in data