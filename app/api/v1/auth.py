from fastapi import APIRouter, Depends, Request, Response
from fastapi.responses import JSONResponse
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.config import settings
from app.core.database import get_db
from app.core.dependencies import get_current_user_optional
from app.core.rate_limit import limiter
from app.core.security import create_access_token
from app.models.user import User
from app.schemas.auth import LoginRequest, LoginResponse, RegisterRequest
from app.schemas.user import UserRead
from app.services import auth_service

router = APIRouter()

COOKIE_KEY = "oj_access_token"
COOKIE_MAX_AGE = 30 * 60  # 30 minutes


@router.post("/register", response_model=UserRead, status_code=201,
    summary="Register a new account",
    description="Create a new user account. Username and email must be unique. Password must be 8-128 characters.",
    responses={409: {"description": "Username or email already taken"}},
    tags=["Auth"],
)
@limiter.limit("10/hour")
async def register(request: Request, data: RegisterRequest, db: AsyncSession = Depends(get_db)):
    user = await auth_service.register(db, data)
    return user


@router.post("/login",
    summary="Login and receive access token",
    description="Authenticate with username and password. Sets httpOnly cookie and returns JWT token with user info.",
    responses={401: {"description": "Invalid credentials"}},
    tags=["Auth"],
)
@limiter.limit("5/minute")
async def login(request: Request, data: LoginRequest, db: AsyncSession = Depends(get_db)):
    result = await auth_service.authenticate(db, data.username, data.password)
    response = JSONResponse({
        "access_token": result.access_token,
        "token_type": "bearer",
        "user": {
            "id": str(result.user.id),
            "username": result.user.username,
            "email": result.user.email,
            "role": result.user.role,
        },
    })
    response.set_cookie(
        COOKIE_KEY,
        result.access_token,
        max_age=COOKIE_MAX_AGE,
        httponly=True,
        secure=settings.cookie_secure,
        samesite=settings.cookie_samesite,
    )
    return response


@router.post("/logout")
async def logout(response: Response):
    response.delete_cookie(
        COOKIE_KEY,
        httponly=True,
        secure=settings.cookie_secure,
        samesite=settings.cookie_samesite,
    )
    return {"detail": "Logged out"}


@router.get("/me", response_model=UserRead | None)
async def me(user: User | None = Depends(get_current_user_optional)):
    return user
