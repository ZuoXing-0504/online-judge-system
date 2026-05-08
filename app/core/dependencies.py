from fastapi import Depends, Request, WebSocket
from fastapi.security import OAuth2PasswordBearer
from jose import JWTError
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.database import get_db
from app.core.exceptions import ForbiddenException, UnauthorizedException
from app.core.security import decode_access_token
from app.models.user import User

COOKIE_KEY = "oj_access_token"
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/api/v1/auth/login", auto_error=False)


def _resolve_token(request: Request, header_token: str | None = None) -> str | None:
    cookie_token = request.cookies.get(COOKIE_KEY)
    return header_token or cookie_token


def _resolve_websocket_token(websocket: WebSocket) -> str | None:
    query_token = websocket.query_params.get("token")
    auth_header = websocket.headers.get("authorization")
    header_token = None
    if auth_header and auth_header.lower().startswith("bearer "):
        header_token = auth_header[7:]
    cookie_token = websocket.cookies.get(COOKIE_KEY)
    return query_token or header_token or cookie_token


async def _resolve_user_from_token(token: str, db: AsyncSession) -> User:
    try:
        payload = decode_access_token(token)
        user_id: str | None = payload.get("sub")
        if user_id is None:
            raise UnauthorizedException("Invalid token")
    except JWTError:
        raise UnauthorizedException("Invalid token")

    result = await db.execute(select(User).where(User.id == user_id))
    user = result.scalar_one_or_none()
    if user is None or not user.is_active:
        raise UnauthorizedException("User not found or inactive")
    return user


async def resolve_websocket_user(
    websocket: WebSocket,
    db: AsyncSession,
) -> User:
    resolved = _resolve_websocket_token(websocket)
    if resolved is None:
        raise UnauthorizedException("Not authenticated")
    return await _resolve_user_from_token(resolved, db)


async def get_current_user_optional(
    request: Request,
    token: str | None = Depends(oauth2_scheme),
    db: AsyncSession = Depends(get_db),
) -> User | None:
    resolved = _resolve_token(request, token)
    if resolved is None:
        return None
    return await _resolve_user_from_token(resolved, db)


async def get_current_user(
    request: Request,
    token: str | None = Depends(oauth2_scheme),
    db: AsyncSession = Depends(get_db),
) -> User:
    resolved = _resolve_token(request, token)
    if resolved is None:
        raise UnauthorizedException("Not authenticated")
    return await _resolve_user_from_token(resolved, db)


async def require_admin(user: User = Depends(get_current_user)) -> User:
    if user.role != "admin":
        raise ForbiddenException("Admin access required")
    return user
