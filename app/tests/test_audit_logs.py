import pytest

pytestmark = pytest.mark.asyncio


async def test_list_audit_logs_requires_admin(client, admin_token):
    headers = {"Authorization": f"Bearer {admin_token}"}
    response = await client.get("/api/v1/audit-logs/", headers=headers)
    assert response.status_code == 200
    assert isinstance(response.json(), list)


async def test_list_audit_logs_requires_auth(client):
    response = await client.get("/api/v1/audit-logs/")
    assert response.status_code in (401, 403)


async def test_get_nonexistent_audit_log_returns_404(client, admin_token):
    headers = {"Authorization": f"Bearer {admin_token}"}
    fake_id = "00000000-0000-0000-0000-000000000000"
    response = await client.get(f"/api/v1/audit-logs/{fake_id}", headers=headers)
    assert response.status_code == 404