import pytest

from app.core.pagination import PaginatedResponse
from app.core import redis as redis_module


@pytest.mark.asyncio
async def test_redis_pool_reuses_current_loop_and_resets_for_new_loop(monkeypatch):
    calls: list[tuple[str, int]] = []

    class FakePool:
        async def close(self) -> None:
            return None

    async def fake_create_pool(settings):
        calls.append((settings.host, settings.port))
        return FakePool()

    loop_one = object()
    loop_two = object()

    monkeypatch.setattr(redis_module, "_pool", None)
    monkeypatch.setattr(redis_module, "_pool_loop", None)
    monkeypatch.setattr(redis_module, "create_pool", fake_create_pool)
    monkeypatch.setattr(redis_module.asyncio, "get_running_loop", lambda: loop_one)

    first = await redis_module.get_redis_pool()
    second = await redis_module.get_redis_pool()
    assert first is second
    assert len(calls) == 1

    monkeypatch.setattr(redis_module.asyncio, "get_running_loop", lambda: loop_two)
    third = await redis_module.get_redis_pool()
    assert third is not first
    assert len(calls) == 2

    await redis_module.close_redis_pool()


@pytest.mark.asyncio
async def test_close_redis_pool_swallows_runtime_error(monkeypatch):
    class ExplodingPool:
        async def close(self) -> None:
            raise RuntimeError("already closing")

    monkeypatch.setattr(redis_module, "_pool", ExplodingPool())
    monkeypatch.setattr(redis_module, "_pool_loop", object())

    await redis_module.close_redis_pool()

    assert redis_module._pool is None
    assert redis_module._pool_loop is None


def test_paginated_response_total_pages():
    empty_page = PaginatedResponse(items=[], total=0, page=1, page_size=20)
    assert empty_page.total_pages == 1

    multi_page = PaginatedResponse(items=[1, 2], total=21, page=1, page_size=20)
    assert multi_page.total_pages == 2
