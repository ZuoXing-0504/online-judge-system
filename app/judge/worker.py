from arq import create_pool
from arq.connections import RedisSettings
from sqlalchemy.ext.asyncio import async_sessionmaker, create_async_engine

from app.core.config import settings
from app.core.database import ensure_database_schema
from app.services.judge_service import judge_submission


async def judge_job(ctx, submission_id: str) -> None:
    session_factory: async_sessionmaker = ctx["session_factory"]
    async with session_factory() as db:
        await judge_submission(db, submission_id)


async def startup(ctx):
    engine = create_async_engine(settings.database_url)
    await ensure_database_schema(engine)
    ctx["session_factory"] = async_sessionmaker(engine, expire_on_commit=False)
    ctx["engine"] = engine


async def shutdown(ctx):
    await ctx["engine"].dispose()


class WorkerSettings:
    functions = [judge_job]
    on_startup = startup
    on_shutdown = shutdown
    redis_settings = RedisSettings(host=settings.redis_host, port=settings.redis_port)
    max_jobs = settings.concurrent_judge_jobs
    job_timeout = 300
    poll_delay = 0.5
