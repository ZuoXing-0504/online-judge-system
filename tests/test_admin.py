import pytest
from httpx import AsyncClient
from sqlalchemy import select

from app.models.audit_log import AuditLog


@pytest.mark.asyncio
async def test_change_user_role_creates_audit_log(
    client: AsyncClient,
    db,
    admin_token: str,
    test_user,
):
    response = await client.patch(
        f"/api/v1/admin/users/{test_user.id}/role?role=admin",
        headers={"Authorization": f"Bearer {admin_token}"},
    )

    assert response.status_code == 200
    assert response.json()["role"] == "admin"

    logs = await db.execute(
        select(AuditLog).where(
            AuditLog.action == "change_role",
            AuditLog.target_id == str(test_user.id),
        )
    )
    entries = logs.scalars().all()
    assert len(entries) == 1
    assert entries[0].detail == {"old_role": "user", "new_role": "admin"}


@pytest.mark.asyncio
async def test_admin_cannot_change_own_role(
    client: AsyncClient,
    admin_token: str,
    test_admin,
):
    response = await client.patch(
        f"/api/v1/admin/users/{test_admin.id}/role?role=user",
        headers={"Authorization": f"Bearer {admin_token}"},
    )

    assert response.status_code == 400
