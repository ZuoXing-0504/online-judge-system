import asyncio

from arq import create_pool
from arq.connections import ArqRedis, RedisSettings

from app.core.config import settings

_pool: ArqRedis | None = None
_pool_loop: asyncio.AbstractEventLoop | None = None


async def get_redis_pool() -> ArqRedis:
    global _pool, _pool_loop
    current_loop = asyncio.get_running_loop()
    if _pool is not None and _pool_loop is not current_loop:
        _pool = None
        _pool_loop = None
    if _pool is None:
        _pool = await create_pool(
            RedisSettings(host=settings.redis_host, port=settings.redis_port)
        )
        _pool_loop = current_loop
    return _pool


async def close_redis_pool() -> None:
    global _pool, _pool_loop
    if _pool is not None:
        try:
            await _pool.close()
        except RuntimeError:
            pass
        finally:
            _pool = None
            _pool_loop = None
