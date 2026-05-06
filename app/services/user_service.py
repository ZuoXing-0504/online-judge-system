from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.exceptions import ConflictException, NotFoundException
from app.models.user import User
from app.schemas.user import UserUpdate


async def get_by_id(db: AsyncSession, user_id: str) -> User:
    result = await db.execute(select(User).where(User.id == user_id))
    user = result.scalar_one_or_none()
    if not user:
        raise NotFoundException("User not found")
    return user


async def update_profile(db: AsyncSession, user: User, data: UserUpdate) -> User:
    if data.username is not None and data.username != user.username:
        existing = await db.execute(select(User).where(User.username == data.username))
        if existing.scalar_one_or_none():
            raise ConflictException("Username already taken")
        user.username = data.username
    if data.email is not None and data.email != user.email:
        existing = await db.execute(select(User).where(User.email == data.email))
        if existing.scalar_one_or_none():
            raise ConflictException("Email already taken")
        user.email = data.email
    await db.commit()
    await db.refresh(user)
    return user


async def list_users(
    db: AsyncSession, page: int = 1, page_size: int = 20, role: str | None = None
) -> tuple[list[User], int]:
    query = select(User)
    count_query = select(User)
    if role:
        query = query.where(User.role == role)
        count_query = count_query.where(User.role == role)
    total_result = await db.execute(select(func.count()).select_from(count_query.subquery()))
    total = total_result.scalar() or 0
    offset = (page - 1) * page_size
    result = await db.execute(query.order_by(User.created_at.desc()).offset(offset).limit(page_size))
    return list(result.scalars().all()), total


async def change_role(db: AsyncSession, user_id: str, new_role: str) -> User:
    user = await get_by_id(db, user_id)
    user.role = new_role
    await db.commit()
    await db.refresh(user)
    return user
