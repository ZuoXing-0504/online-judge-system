import uuid

from fastapi import APIRouter, Depends, Query
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.database import get_db
from app.core.dependencies import require_admin
from app.models.user import User
from app.schemas.common import MessageResponse, PaginatedResponse
from app.schemas.user import AdminUserRead
from app.services import user_service

router = APIRouter()


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


@router.patch("/users/{user_id}/role", response_model=AdminUserRead)
async def change_user_role(
    user_id: uuid.UUID,
    role: str = Query(..., pattern=r"^(user|admin)$"),
    db: AsyncSession = Depends(get_db),
    admin: User = Depends(require_admin),
):
    if user_id == admin.id:
        from app.core.exceptions import BadRequestException
        raise BadRequestException("Cannot change your own role")
    updated = await user_service.change_role(db, str(user_id), role)
    return updated
