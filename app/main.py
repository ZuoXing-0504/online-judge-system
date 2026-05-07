from contextlib import asynccontextmanager
from pathlib import Path

from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import FileResponse, JSONResponse, RedirectResponse
from fastapi.staticfiles import StaticFiles
from slowapi import _rate_limit_exceeded_handler
from slowapi.errors import RateLimitExceeded

from app.api.v1.router import api_router
from app.core.config import settings
from app.core.database import engine
from app.core.exceptions import AppException
from app.core.logging import RequestIDMiddleware, setup_logging
from app.core.rate_limit import limiter
from app.core.redis import close_redis_pool
from prometheus_fastapi_instrumentator import Instrumentator

setup_logging()

BASE_DIR = Path(__file__).resolve().parent
STATIC_DIR = BASE_DIR / "static"


def page_response(filename: str) -> FileResponse:
    return FileResponse(STATIC_DIR / filename)


@asynccontextmanager
async def lifespan(app: FastAPI):
    yield
    await close_redis_pool()
    await engine.dispose()


app = FastAPI(
    title=settings.app_name,
    version="1.0.0",
    docs_url="/docs",
    lifespan=lifespan,
)

app.state.limiter = limiter
app.add_exception_handler(RateLimitExceeded, _rate_limit_exceeded_handler)

app.add_middleware(RequestIDMiddleware)

Instrumentator().instrument(app).expose(app, include_in_schema=False)

app.mount("/static", StaticFiles(directory=STATIC_DIR), name="static")

app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.cors_origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.exception_handler(AppException)
async def app_exception_handler(request: Request, exc: AppException):
    return JSONResponse(
        status_code=exc.status_code,
        content={"detail": exc.detail, "error_code": exc.error_code},
    )


@app.get("/", include_in_schema=False)
async def frontend_index():
    return page_response("auth.html")


@app.get("/portal", include_in_schema=False)
async def frontend_portal():
    return page_response("index.html")


@app.get("/auth", include_in_schema=False)
async def frontend_auth():
    return page_response("auth.html")


@app.get("/register", include_in_schema=False)
async def frontend_register():
    return page_response("register.html")


@app.get("/problems", include_in_schema=False)
async def frontend_problems():
    return page_response("problems.html")


@app.get("/problem", include_in_schema=False)
async def frontend_problem_detail():
    return page_response("problem.html")


@app.get("/submit", include_in_schema=False)
async def frontend_submit():
    return page_response("submit.html")


@app.get("/submissions", include_in_schema=False)
async def frontend_submissions():
    return page_response("submissions.html")


@app.get("/admin", include_in_schema=False)
async def frontend_admin():
    return page_response("admin.html")


@app.get("/favicon.ico", include_in_schema=False)
async def favicon():
    return RedirectResponse(url="/static/favicon.svg")


@app.get("/api/v1/health")
async def health_check():
    return {"status": "healthy", "version": "1.0.0"}


app.include_router(api_router, prefix="/api/v1")
