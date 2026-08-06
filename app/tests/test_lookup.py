import pytest

pytestmark = pytest.mark.asyncio


async def test_lookup_roles(client, admin_token):
    headers = {"Authorization": f"Bearer {admin_token}"}
    await client.post("/api/v1/roles/", json={"code": "LOOKUP_ROLE_TEST", "name": "Lookup Role Test"}, headers=headers)

    response = await client.get("/api/v1/lookup/roles")
    assert response.status_code == 200
    data = response.json()
    assert isinstance(data, list)
    assert any(r["code"] == "LOOKUP_ROLE_TEST" for r in data)
    assert all(set(r.keys()) == {"id", "code", "name"} for r in data)


async def test_lookup_permissions(client, admin_token):
    headers = {"Authorization": f"Bearer {admin_token}"}
    await client.post("/api/v1/permissions/", json={"code": "lookup.perm.test", "name": "Lookup Perm Test"}, headers=headers)

    response = await client.get("/api/v1/lookup/permissions")
    assert response.status_code == 200
    data = response.json()
    assert isinstance(data, list)
    assert any(p["code"] == "lookup.perm.test" for p in data)


async def test_lookup_menus(client, admin_token):
    headers = {"Authorization": f"Bearer {admin_token}"}
    await client.post("/api/v1/menus/", json={"code": "LOOKUP_MENU_TEST", "name": "Lookup Menu Test"}, headers=headers)

    response = await client.get("/api/v1/lookup/menus")
    assert response.status_code == 200
    data = response.json()
    assert isinstance(data, list)
    assert any(m["code"] == "LOOKUP_MENU_TEST" for m in data)


async def test_lookup_endpoints_no_auth_required(client):
    response = await client.get("/api/v1/lookup/roles")
    assert response.status_code == 200