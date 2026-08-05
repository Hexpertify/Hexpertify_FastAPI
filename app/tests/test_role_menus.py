import pytest

pytestmark = pytest.mark.asyncio


async def _create_role(client, admin_token, code="RM_TEST_ROLE"):
    resp = await client.post(
        "/api/v1/roles/", json={"code": code, "name": "RM Test Role"},
        headers={"Authorization": f"Bearer {admin_token}"}
    )
    return resp.json()["id"]


async def _create_menu(client, code="RM_TEST_MENU"):
    resp = await client.post("/api/v1/menus/", json={"code": code, "name": "RM Test Menu"})
    return resp.json()["id"]


async def test_assign_menu_to_role(client, admin_token):
    role_id = await _create_role(client, admin_token, "ASSIGN_MENU_ROLE_1")
    menu_id = await _create_menu(client, "ASSIGN_MENU_1")

    response = await client.post(f"/api/v1/roles/{role_id}/menus", json={"menu_id": menu_id})
    assert response.status_code == 201
    menus = response.json()
    assert any(m["id"] == menu_id for m in menus)


async def test_assign_duplicate_menu_fails(client, admin_token):
    role_id = await _create_role(client, admin_token, "ASSIGN_MENU_ROLE_2")
    menu_id = await _create_menu(client, "ASSIGN_MENU_2")

    await client.post(f"/api/v1/roles/{role_id}/menus", json={"menu_id": menu_id})
    response = await client.post(f"/api/v1/roles/{role_id}/menus", json={"menu_id": menu_id})
    assert response.status_code == 409


async def test_assign_menu_to_nonexistent_role_fails(client):
    fake_role_id = "00000000-0000-0000-0000-000000000000"
    menu_id = await _create_menu(client, "ASSIGN_MENU_3")

    response = await client.post(f"/api/v1/roles/{fake_role_id}/menus", json={"menu_id": menu_id})
    assert response.status_code == 404


async def test_get_role_menus(client, admin_token):
    role_id = await _create_role(client, admin_token, "GET_MENU_ROLE")
    menu_id = await _create_menu(client, "GET_MENU_TEST")
    await client.post(f"/api/v1/roles/{role_id}/menus", json={"menu_id": menu_id})

    response = await client.get(f"/api/v1/roles/{role_id}/menus")
    assert response.status_code == 200
    assert any(m["id"] == menu_id for m in response.json())


async def test_replace_role_menus(client, admin_token):
    role_id = await _create_role(client, admin_token, "REPLACE_MENU_ROLE")
    menu_id_1 = await _create_menu(client, "REPLACE_MENU_1")
    menu_id_2 = await _create_menu(client, "REPLACE_MENU_2")

    await client.post(f"/api/v1/roles/{role_id}/menus", json={"menu_id": menu_id_1})
    response = await client.put(f"/api/v1/roles/{role_id}/menus", json={"menu_ids": [menu_id_2]})
    assert response.status_code == 200
    menus = response.json()
    assert len(menus) == 1
    assert menus[0]["id"] == menu_id_2


async def test_remove_role_menu(client, admin_token):
    role_id = await _create_role(client, admin_token, "REMOVE_MENU_ROLE")
    menu_id = await _create_menu(client, "REMOVE_MENU_TEST")
    await client.post(f"/api/v1/roles/{role_id}/menus", json={"menu_id": menu_id})

    delete_resp = await client.delete(f"/api/v1/roles/{role_id}/menus/{menu_id}")
    assert delete_resp.status_code == 204

    get_resp = await client.get(f"/api/v1/roles/{role_id}/menus")
    assert get_resp.json() == []


async def test_remove_unassigned_menu_returns_404(client, admin_token):
    role_id = await _create_role(client, admin_token, "REMOVE_FAIL_MENU_ROLE")
    menu_id = await _create_menu(client, "REMOVE_FAIL_MENU")

    response = await client.delete(f"/api/v1/roles/{role_id}/menus/{menu_id}")
    assert response.status_code == 404