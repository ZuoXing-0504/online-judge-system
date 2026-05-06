from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.exceptions import ConflictException, UnauthorizedException
from app.core.security import create_access_token, hash_password, verify_password
from app.models.user import User
from app.schemas.auth import LoginResponse, RegisterRequest, UserInfo


async def register(db: AsyncSession, request: RegisterRequest) -> User:
    existing = await db.execute(
        select(User).where((User.username == request.username) | (User.email == request.email))
    )
    existing_user = existing.scalar_one_or_none()
    if existing_user:
        if existing_user.username == request.username:
            raise ConflictException("Username already taken")
        raise ConflictException("Email already taken")

    user = User(
        username=request.username,
        email=request.email,
        hashed_password=hash_password(request.password),
    )
    db.add(user)
    await db.commit()
    await db.refresh(user)
    return user


async def authenticate(db: AsyncSession, username: str, password: str) -> LoginResponse:
    result = await db.execute(select(User).where(User.username == username))
    user = result.scalar_one_or_none()
    if not user or not verify_password(password, user.hashed_password):
        raise UnauthorizedException("Invalid username or password")
    if not user.is_active:
        raise UnauthorizedException("Account is inactive")

    token = create_access_token(data={"sub": str(user.id)})
    return LoginResponse(
        access_token=token,
        user=UserInfo(
            id=user.id,
            username=user.username,
            email=user.email,
            role=user.role,
        ),
    )
