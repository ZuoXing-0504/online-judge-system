from sqlalchemy.ext.asyncio import AsyncSession

from app.models.audit_log import AuditLog


async def create_audit_log(
    db: AsyncSession,
    admin_id: str,
    action: str,
    target_type: str,
    target_id: str | None = None,
    detail: dict | None = None,
    ip_address: str | None = None,
) -> None:
    entry = AuditLog(
        admin_id=admin_id,
        action=action,
        target_type=target_type,
        target_id=target_id,
        detail=detail,
        ip_address=ip_address,
    )
    db.add(entry)
    return entry
