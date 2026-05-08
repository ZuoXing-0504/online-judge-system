import os
import re

import pytest
import pytest_asyncio
from sqlalchemy import text
from sqlalchemy.engine import make_url
from sqlalchemy.exc import SQLAlchemyError
from httpx import ASGITransport, AsyncClient
from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker, create_async_engine
from sqlalchemy.pool import NullPool

from app.api.v1 import submissions as submissions_api
from app.core.redis import close_redis_pool
from app.core.security import create_access_token, hash_password
from app.main import app
from app.models.base import Base
from app.models.user import User

TEST_DATABASE_URL = os.getenv(
    "TEST_DATABASE_URL",
    "postgresql+asyncpg://judge:judge_pass@localhost:5432/online_judge_test",
)


class FakeRedisPool:
    def __init__(self) -> None:
        self.jobs: list[tuple[str, str]] = []

    async def enqueue_job(self, job_name: str, submission_id: str):
        self.jobs.append((job_name, submission_id))


async def ensure_test_database(database_url: str) -> None:
    url = make_url(database_url)
    database_name = url.database
    if not database_name:
        raise RuntimeError("Test database URL is missing a database name")

    admin_database = "postgres" if database_name != "postgres" else "template1"
    admin_url = url.set(database=admin_database)
    admin_engine = create_async_engine(
        admin_url.render_as_string(hide_password=False),
        echo=False,
        poolclass=NullPool,
        isolation_level="AUTOCOMMIT",
    )

    try:
        async with admin_engine.connect() as conn:
            result = await conn.execute(
                text("SELECT 1 FROM pg_database WHERE datname = :database_name"),
                {"database_name": database_name},
            )
            if result.scalar() is not None:
                return

            if not re.fullmatch(r"[A-Za-z0-9_]+", database_name):
                raise RuntimeError(f"Unsafe test database name: {database_name}")

            await conn.execute(text(f'CREATE DATABASE "{database_name}"'))
    finally:
        await admin_engine.dispose()


@pytest_asyncio.fixture
async def engine():
    try:
        await ensure_test_database(TEST_DATABASE_URL)
    except (ConnectionRefusedError, OSError, SQLAlchemyError) as exc:
        pytest.skip(f"PostgreSQL test database unavailable: {exc}")

    engine = create_async_engine(TEST_DATABASE_URL, echo=False)
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.drop_all)
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
    try:
        yield engine
    finally:
        async with engine.begin() as conn:
            await conn.run_sync(Base.metadata.drop_all)
        await engine.dispose()


@pytest_asyncio.fixture
async def db(engine):
    session_factory = async_sessionmaker(engine, class_=AsyncSession, expire_on_commit=False)
    async with session_factory() as session:
        yield session
        await session.close()


@pytest_asyncio.fixture
async def client(engine):
    from app.core.database import get_db

    session_factory = async_sessionmaker(
        engine, class_=AsyncSession, expire_on_commit=False
    )
    fake_redis_pool = FakeRedisPool()

    async def override_get_db():
        async with session_factory() as session:
            yield session

    async def override_get_redis_pool():
        return fake_redis_pool

    app.dependency_overrides[get_db] = override_get_db
    original_get_redis_pool = submissions_api.get_redis_pool
    submissions_api.get_redis_pool = override_get_redis_pool
    transport = ASGITransport(app=app)
    try:
        async with AsyncClient(transport=transport, base_url="http://test") as ac:
            yield ac
    finally:
        app.dependency_overrides.clear()
        submissions_api.get_redis_pool = original_get_redis_pool
        await close_redis_pool()


@pytest_asyncio.fixture
async def test_user(db) -> User:
    user = User(
        username="testuser",
        email="test@example.com",
        hashed_password=hash_password("password123"),
    )
    db.add(user)
    await db.commit()
    await db.refresh(user)
    return user


@pytest_asyncio.fixture
async def test_admin(db) -> User:
    admin = User(
        username="admin",
        email="admin@example.com",
        hashed_password=hash_password("admin123"),
        role="admin",
    )
    db.add(admin)
    await db.commit()
    await db.refresh(admin)
    return admin


@pytest.fixture
def user_token(test_user) -> str:
    return create_access_token(data={"sub": str(test_user.id)})


@pytest.fixture
def admin_token(test_admin) -> str:
    return create_access_token(data={"sub": str(test_admin.id)})
