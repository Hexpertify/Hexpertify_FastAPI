import pytest

pytestmark = pytest.mark.asyncio


async def test_create_root_menu(client, admin_token):
    headers = {"Authorization": f"Bearer {admin_token}"}
    response = await client.post("/api/v1/menus/", json={
        "code": "ROOT_TEST",
        "name": "Root Test",
        "route": "/root-test",
        "sort_order": 1
    }, headers=headers)
    assert response.status_code == 201
    data = response.json()
    assert data["code"] == "ROOT_TEST"
    assert data["parent_id"] is None


async def test_create_child_menu(client, admin_token):
    headers = {"Authorization": f"Bearer {admin_token}"}
    parent_resp = await client.post("/api/v1/menus/", json={
        "code": "PARENT_TEST", "name": "Parent Test"
    }, headers=headers)
    parent_id = parent_resp.json()["id"]

    child_resp = await client.post("/api/v1/menus/", json={
        "parent_id": parent_id,
        "code": "CHILD_TEST",
        "name": "Child Test"
    }, headers=headers)
    assert child_resp.status_code == 201
    assert child_resp.json()["parent_id"] == parent_id


async def test_create_duplicate_menu_code_fails(client, admin_token):
    headers = {"Authorization": f"Bearer {admin_token}"}
    payload = {"code": "DUP_MENU", "name": "Dup Menu"}
    await client.post("/api/v1/menus/", json=payload, headers=headers)
    response = await client.post("/api/v1/menus/", json=payload, headers=headers)
    assert response.status_code == 409


async def test_create_menu_with_invalid_parent_fails(client, admin_token):
    headers = {"Authorization": f"Bearer {admin_token}"}
    fake_parent_id = "00000000-0000-0000-0000-000000000000"
    response = await client.post("/api/v1/menus/", json={
        "parent_id": fake_parent_id,
        "code": "ORPHAN_TEST",
        "name": "Orphan Test"
    }, headers=headers)
    assert response.status_code == 400


async def test_get_menu_by_id(client, admin_token):
    headers = {"Authorization": f"Bearer {admin_token}"}
    create_resp = await client.post("/api/v1/menus/", json={
        "code": "GET_MENU_TEST", "name": "Get Menu Test"
    }, headers=headers)
    menu_id = create_resp.json()["id"]

    response = await client.get(f"/api/v1/menus/{menu_id}")
    assert response.status_code == 200
    assert response.json()["code"] == "GET_MENU_TEST"


async def test_get_nonexistent_menu_returns_404(client):
    fake_id = "00000000-0000-0000-0000-000000000000"
    response = await client.get(f"/api/v1/menus/{fake_id}")
    assert response.status_code == 404


async def test_list_menus(client, admin_token):
    headers = {"Authorization": f"Bearer {admin_token}"}
    await client.post("/api/v1/menus/", json={"code": "LIST_MENU_TEST", "name": "List Menu Test"}, headers=headers)
    response = await client.get("/api/v1/menus/")
    assert response.status_code == 200
    assert isinstance(response.json(), list)


async def test_menu_tree(client, admin_token):
    headers = {"Authorization": f"Bearer {admin_token}"}
    parent_resp = await client.post("/api/v1/menus/", json={
        "code": "TREE_PARENT", "name": "Tree Parent"
    }, headers=headers)
    parent_id = parent_resp.json()["id"]
    await client.post("/api/v1/menus/", json={
        "parent_id": parent_id, "code": "TREE_CHILD", "name": "Tree Child"
    }, headers=headers)

    response = await client.get("/api/v1/menus/tree")
    assert response.status_code == 200
    tree = response.json()
    parent_node = next((m for m in tree if m["code"] == "TREE_PARENT"), None)
    assert parent_node is not None
    assert len(parent_node["children"]) >= 1


async def test_update_menu(client, admin_token):
    headers = {"Authorization": f"Bearer {admin_token}"}
    create_resp = await client.post("/api/v1/menus/", json={
        "code": "UPDATE_MENU_TEST", "name": "Before Update"
    }, headers=headers)
    menu_id = create_resp.json()["id"]

    response = await client.put(f"/api/v1/menus/{menu_id}", json={"name": "After Update"}, headers=headers)
    assert response.status_code == 200
    assert response.json()["name"] == "After Update"


async def test_menu_cannot_be_own_parent(client, admin_token):
    headers = {"Authorization": f"Bearer {admin_token}"}
    create_resp = await client.post("/api/v1/menus/", json={
        "code": "SELF_PARENT_TEST", "name": "Self Parent Test"
    }, headers=headers)
    menu_id = create_resp.json()["id"]

    response = await client.put(f"/api/v1/menus/{menu_id}", json={"parent_id": menu_id}, headers=headers)
    assert response.status_code == 400


async def test_delete_menu(client, admin_token):
    headers = {"Authorization": f"Bearer {admin_token}"}
    create_resp = await client.post("/api/v1/menus/", json={
        "code": "DELETE_MENU_TEST", "name": "Delete Menu Test"
    }, headers=headers)
    menu_id = create_resp.json()["id"]

    delete_resp = await client.delete(f"/api/v1/menus/{menu_id}", headers=headers)
    assert delete_resp.status_code == 204

    get_resp = await client.get(f"/api/v1/menus/{menu_id}")
    assert get_resp.status_code == 404