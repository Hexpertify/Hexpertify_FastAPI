import pytest

pytestmark = pytest.mark.asyncio


async def _create_user(client, email="authtest@example.com", password="testpass123"):
    await client.post("/api/v1/users/", json={
        "first_name": "Auth", "last_name": "Test", "email": email, "password": password
    })
    return email, password


async def test_login_success(client):
    email, password = await _create_user(client, "login1@example.com")
    response = await client.post("/api/v1/auth/login", json={"email": email, "password": password})
    assert response.status_code == 200
    data = response.json()
    assert "access_token" in data
    assert "refresh_token" in data


async def test_login_wrong_password_fails(client):
    email, _ = await _create_user(client, "login2@example.com")
    response = await client.post("/api/v1/auth/login", json={"email": email, "password": "wrongpass"})
    assert response.status_code == 401


async def test_login_nonexistent_user_fails(client):
    response = await client.post("/api/v1/auth/login", json={
        "email": "doesnotexist@example.com", "password": "whatever"
    })
    assert response.status_code == 401


async def test_get_me_with_valid_token(client):
    email, password = await _create_user(client, "me1@example.com")
    login_resp = await client.post("/api/v1/auth/login", json={"email": email, "password": password})
    access_token = login_resp.json()["access_token"]

    response = await client.get("/api/v1/auth/me", headers={"Authorization": f"Bearer {access_token}"})
    assert response.status_code == 200
    assert response.json()["email"] == email


async def test_get_me_without_token_fails(client):
    response = await client.get("/api/v1/auth/me")
    assert response.status_code in (401, 403)


async def test_get_me_with_invalid_token_fails(client):
    response = await client.get("/api/v1/auth/me", headers={"Authorization": "Bearer invalidtoken"})
    assert response.status_code == 401


async def test_refresh_token_success(client):
    email, password = await _create_user(client, "refresh1@example.com")
    login_resp = await client.post("/api/v1/auth/login", json={"email": email, "password": password})
    refresh_token = login_resp.json()["refresh_token"]

    response = await client.post("/api/v1/auth/refresh-token", json={"refresh_token": refresh_token})
    assert response.status_code == 200
    data = response.json()
    assert "access_token" in data
    assert data["refresh_token"] != refresh_token


async def test_refresh_token_reuse_fails(client):
    email, password = await _create_user(client, "refresh2@example.com")
    login_resp = await client.post("/api/v1/auth/login", json={"email": email, "password": password})
    refresh_token = login_resp.json()["refresh_token"]

    await client.post("/api/v1/auth/refresh-token", json={"refresh_token": refresh_token})
    response = await client.post("/api/v1/auth/refresh-token", json={"refresh_token": refresh_token})
    assert response.status_code == 401


async def test_logout_revokes_token(client):
    email, password = await _create_user(client, "logout1@example.com")
    login_resp = await client.post("/api/v1/auth/login", json={"email": email, "password": password})
    refresh_token = login_resp.json()["refresh_token"]

    logout_resp = await client.post("/api/v1/auth/logout", json={"refresh_token": refresh_token})
    assert logout_resp.status_code == 204

    response = await client.post("/api/v1/auth/refresh-token", json={"refresh_token": refresh_token})
    assert response.status_code == 401


async def test_change_password_success(client):
    email, password = await _create_user(client, "changepass1@example.com", "oldpass123")
    login_resp = await client.post("/api/v1/auth/login", json={"email": email, "password": password})
    access_token = login_resp.json()["access_token"]

    response = await client.post(
        "/api/v1/auth/change-password",
        json={"old_password": "oldpass123", "new_password": "newpass456"},
        headers={"Authorization": f"Bearer {access_token}"}
    )
    assert response.status_code == 204

    login_with_new = await client.post("/api/v1/auth/login", json={"email": email, "password": "newpass456"})
    assert login_with_new.status_code == 200


async def test_change_password_wrong_old_password_fails(client):
    email, password = await _create_user(client, "changepass2@example.com")
    login_resp = await client.post("/api/v1/auth/login", json={"email": email, "password": password})
    access_token = login_resp.json()["access_token"]

    response = await client.post(
        "/api/v1/auth/change-password",
        json={"old_password": "wrongoldpass", "new_password": "newpass456"},
        headers={"Authorization": f"Bearer {access_token}"}
    )
    assert response.status_code == 400

async def test_forgot_password_existing_user(client):
    email, password = await _create_user(client, "forgot1@example.com")
    response = await client.post("/api/v1/auth/forgot-password", json={"email": email})
    assert response.status_code == 200
    assert "debug_token" in response.json()


async def test_forgot_password_nonexistent_user_still_200(client):
    response = await client.post("/api/v1/auth/forgot-password", json={"email": "doesnotexist999@example.com"})
    assert response.status_code == 200


async def test_reset_password_success(client):
    email, password = await _create_user(client, "reset1@example.com", "oldpass123")
    forgot_resp = await client.post("/api/v1/auth/forgot-password", json={"email": email})
    token = forgot_resp.json()["debug_token"]

    reset_resp = await client.post("/api/v1/auth/reset-password", json={
        "token": token, "new_password": "brandnewpass456"
    })
    assert reset_resp.status_code == 204

    login_resp = await client.post("/api/v1/auth/login", json={"email": email, "password": "brandnewpass456"})
    assert login_resp.status_code == 200


async def test_reset_password_reuse_fails(client):
    email, password = await _create_user(client, "reset2@example.com")
    forgot_resp = await client.post("/api/v1/auth/forgot-password", json={"email": email})
    token = forgot_resp.json()["debug_token"]

    await client.post("/api/v1/auth/reset-password", json={"token": token, "new_password": "newpass1"})
    response = await client.post("/api/v1/auth/reset-password", json={"token": token, "new_password": "newpass2"})
    assert response.status_code == 400


async def test_reset_password_invalid_token_fails(client):
    response = await client.post("/api/v1/auth/reset-password", json={
        "token": "totally-invalid-token", "new_password": "newpass123"
    })
    assert response.status_code == 400