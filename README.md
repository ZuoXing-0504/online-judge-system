# Online Judge System

An online judge prototype built with FastAPI, async SQLAlchemy, PostgreSQL, Redis, and `arq`.

The project includes:

- account registration and login
- public problem browsing
- protected submission history
- separate user and admin frontends
- asynchronous judging with a worker queue
- Docker-based Python sandbox execution
- audit logging for admin role changes
- rate limiting and Prometheus metrics

## Current scope

- The submission runtime currently supports `python` only.
- Database schema changes are managed with Alembic migrations.
- The frontend is served by the FastAPI app as static multi-page assets.

## Stack

- FastAPI
- SQLAlchemy 2.x asyncio
- PostgreSQL
- Redis + arq
- Alembic
- Docker Compose

## Local development

1. Copy environment variables:

```bash
cp .env.example .env
```

2. Start the stack:

```bash
docker compose up --build
```

3. Open the app:

- Frontend: [http://localhost:8000/](http://localhost:8000/)
- API docs: [http://localhost:8000/docs](http://localhost:8000/docs)
- Health: [http://localhost:8000/api/v1/health](http://localhost:8000/api/v1/health)

## Manual run

Install dependencies:

```bash
pip install -r requirements.txt
```

Apply migrations:

```bash
alembic upgrade head
```

Start the API:

```bash
uvicorn app.main:app --reload
```

Start the worker in another terminal:

```bash
arq app.judge.worker.WorkerSettings
```

## Testing

The test suite expects a PostgreSQL database named `online_judge_test` and a Redis instance.

```bash
pytest --cov=app --cov-report=term-missing
```

## Security notes

- Cookies are `HttpOnly`.
- `Secure` cookie mode is controlled by `COOKIE_SECURE`.
- Allowed browser origins are controlled by `CORS_ORIGINS_RAW`.
- For production, set a strong `SECRET_KEY`, enable HTTPS, and tighten CORS to your real domains.

## License

MIT
