import uuid

from fastapi import APIRouter, Depends, Query, Request
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.database import get_db
from app.core.dependencies import require_admin
from app.core.exceptions import BadRequestException
from app.models.user import User
from app.schemas.common import PaginatedResponse
from app.schemas.user import AdminUserRead
from app.services import user_service
from app.services.audit_service import create_audit_log

router = APIRouter()


def _client_ip(request: Request) -> str:
    forwarded = request.headers.get("X-Forwarded-For")
    if forwarded:
        return forwarded.split(",")[0].strip()
    return request.client.host if request.client else ""


@router.get("/users", response_model=PaginatedResponse)
async def list_users(
    page: int = Query(1, ge=1),
    page_size: int = Query(20, ge=1, le=100),
    role: str | None = Query(None, pattern=r"^(user|admin)$"),
    db: AsyncSession = Depends(get_db),
    admin: User = Depends(require_admin),
):
    users, total = await user_service.list_users(db, page=page, page_size=page_size, role=role)
    items = [AdminUserRead.model_validate(u) for u in users]
    return PaginatedResponse(
        items=items, total=total, page=page, page_size=page_size,
        total_pages=max(1, (total + page_size - 1) // page_size),
    )


@router.patch("/users/{user_id}/role", response_model=AdminUserRead,
    summary="Change user role",
    description="Promote a user to admin or demote an admin to user. Cannot change your own role.",
    responses={400: {"description": "Cannot change your own role"}, 403: {"description": "Admin access required"}, 404: {"description": "User not found"}},
    tags=["Admin"],
)
async def change_user_role(
    request: Request,
    user_id: uuid.UUID,
    role: str = Query(..., pattern=r"^(user|admin)$"),
    db: AsyncSession = Depends(get_db),
    admin: User = Depends(require_admin),
):
    if user_id == admin.id:
        raise BadRequestException("Cannot change your own role")
    try:
        target = await user_service.get_by_id(db, str(user_id))
        old_role = target.role
        updated = await user_service.change_role(db, str(user_id), role, commit=False)
        await create_audit_log(
            db, str(admin.id), "change_role", "user",
            target_id=str(user_id),
            detail={"old_role": old_role, "new_role": role},
            ip_address=_client_ip(request),
        )
        await db.commit()
        await db.refresh(updated)
        return updated
    except Exception:
        await db.rollback()
        raise
