from datetime import datetime, timedelta, timezone

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.exceptions import ConflictException, UnauthorizedException
from app.core.security import create_access_token, hash_password, verify_password
from app.models.user import User
from app.schemas.auth import LoginResponse, RegisterRequest, UserInfo

MAX_FAILED_LOGINS = 5
LOCKOUT_MINUTES = 15


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
    now = datetime.now(timezone.utc)

    if not user or not verify_password(password, user.hashed_password):
        if user:
            user.failed_login_count += 1
            if user.failed_login_count >= MAX_FAILED_LOGINS:
                user.locked_until = now + timedelta(minutes=LOCKOUT_MINUTES)
            await db.commit()
        raise UnauthorizedException("Invalid username or password")

    if not user.is_active:
        raise UnauthorizedException("Account is inactive")

    if user.locked_until and now < user.locked_until:
        remaining = int((user.locked_until - now).total_seconds() / 60) + 1
        raise UnauthorizedException(f"Account locked. Try again in {remaining} minutes")

    # Reset on successful login
    user.failed_login_count = 0
    user.locked_until = None
    await db.commit()

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
