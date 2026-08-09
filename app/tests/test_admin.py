import pytest

pytestmark = pytest.mark.asyncio

BOOTSTRAP_SECRET = "change-this-to-a-long-random-secret"


async def test_seed_defaults_success(client):
    response = await client.post("/api/v1/admin/seed", json={"bootstrap_secret": BOOTSTRAP_SECRET})
    assert response.status_code == 201
    data = response.json()
    assert "roles" in data
    assert "permissions" in data
    assert "menus" in data


async def test_seed_defaults_wrong_secret_fails(client):
    response = await client.post("/api/v1/admin/seed", json={"bootstrap_secret": "wrong_secret"})
    assert response.status_code == 403


async def test_seed_defaults_idempotent(client):
    await client.post("/api/v1/admin/seed", json={"bootstrap_secret": BOOTSTRAP_SECRET})
    response = await client.post("/api/v1/admin/seed", json={"bootstrap_secret": BOOTSTRAP_SECRET})
    assert response.status_code == 201
    data = response.json()
    assert data["roles"] == 0
    assert data["permissions"] == 0


async def test_create_super_admin_success(client):
    response = await client.post("/api/v1/admin/create-super-admin", json={
        "bootstrap_secret": BOOTSTRAP_SECRET,
        "first_name": "Super",
        "last_name": "Admin",
        "email": "superadmin1@example.com",
        "password": "superadminpass123"
    })
    assert response.status_code == 201
    data = response.json()
    assert data["email"] == "superadmin1@example.com"


async def test_create_super_admin_wrong_secret_fails(client):
    response = await client.post("/api/v1/admin/create-super-admin", json={
        "bootstrap_secret": "wrong_secret",
        "first_name": "Super",
        "last_name": "Admin",
        "email": "superadmin2@example.com",
        "password": "superadminpass123"
    })
    assert response.status_code == 403


async def test_super_admin_can_create_role(client):
    await client.post("/api/v1/admin/create-super-admin", json={
        "bootstrap_secret": BOOTSTRAP_SECRET,
        "first_name": "Super",
        "last_name": "Admin",
        "email": "superadmin3@example.com",
        "password": "superadminpass123"
    })
    login_resp = await client.post("/api/v1/auth/login", json={
        "email": "superadmin3@example.com", "password": "superadminpass123"
    })
    access_token = login_resp.json()["access_token"]

    response = await client.post(
        "/api/v1/roles/",
        json={"code": "SUPER_ADMIN_CREATED_ROLE", "name": "Created By Super Admin"},
        headers={"Authorization": f"Bearer {access_token}"}
    )
    assert response.status_code == 201


async def test_reset_permissions_success(client):
    response = await client.post("/api/v1/admin/reset-permissions", json={"bootstrap_secret": BOOTSTRAP_SECRET})
    assert response.status_code == 201
    assert "permissions_created" in response.json()


async def test_sync_menus_success(client):
    response = await client.post("/api/v1/admin/sync-menus", json={"bootstrap_secret": BOOTSTRAP_SECRET})
    assert response.status_code == 201
    assert "menus_created" in response.json()