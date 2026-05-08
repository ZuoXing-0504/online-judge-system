# Online Judge System

[![Test](https://github.com/ZuoXing-0504/online-judge-system/actions/workflows/test.yml/badge.svg)](https://github.com/ZuoXing-0504/online-judge-system/actions/workflows/test.yml)
[![Python](https://img.shields.io/badge/python-3.12-blue.svg)](https://www.python.org/)
[![FastAPI](https://img.shields.io/badge/FastAPI-0.115-green.svg)](https://fastapi.tiangolo.com/)
[![License](https://img.shields.io/badge/license-MIT-blue.svg)](LICENSE)

A production-grade online code judge supporting Python, C++, and Java. Built for internship portfolio demonstration.

---

## Features

- **Multi-language judging** — Python, C++, Java execution in Docker sandboxes
- **101 classic problems** — categorized by topic with official solutions
- **Async judging** — arq worker pool with real-time WebSocket status push
- **Separated frontend** — 8-page SPA, CodeMirror editor, zh/en i18n
- **Rate limiting** — per-endpoint limits on auth and submissions
- **Audit logging** — admin actions tracked with IP and detail
- **Soft delete** — problems and users preserved with deleted_at
- **Structured logging** — JSON log format with request IDs
- **Prometheus metrics** — QPS, latency, error rate at /metrics
- **Docker Compose** — one-command startup with health checks
- **CI/CD** — GitHub Actions: pytest + coverage + ruff lint

---

## Quick Start

```bash
# Clone
git clone https://github.com/ZuoXing-0504/online-judge-system.git
cd online-judge-system

# Build sandbox + start all services
docker compose up --build -d

# Seed problems and solutions (optional)
docker compose exec app python scripts/seed_problems.py
docker compose exec app python scripts/seed_all_solutions.py

# Open in browser
# Frontend:       http://localhost:8000/portal
# API Docs:       http://localhost:8000/docs
# Metrics:        http://localhost:8000/metrics
```

Default admin account (after seeding):
- Username: `admin` / Password: `admin123456`

---

## Architecture

```
Client (SPA)
  │
  ▼
FastAPI (App) ──────► PostgreSQL (persistence)
  │                        ▲
  ▼                        │
Redis (arq queue) ───► Worker (Docker sandbox)
```

| Component | Tech | Role |
|-----------|------|------|
| Web Framework | FastAPI 0.115 | REST API + Swagger + WebSocket |
| ORM | SQLAlchemy 2.0 (async) | Async DB with asyncpg driver |
| Database | PostgreSQL 16 | User, problem, submission storage |
| Queue | Redis 7 + arq 0.26 | Async task dispatch |
| Judge | Docker SDK + subprocess | Sandboxed code execution |
| Frontend | Vanilla JS (ES modules) | 8-page SPA, zero framework |
| Editor | CodeMirror 6 | Syntax highlighting (Python/C++/Java) |
| Metrics | Prometheus | /metrics endpoint |

---

## Database Schema

```
users ──┬── problems (created_by)
        │       └── test_cases (problem_id)
        │
        ├── submissions (user_id, problem_id)
        │       └── submission_test_results (submission_id)
        │
        └── audit_logs (admin_id)
```

5 tables, UUID primary keys, soft-delete on users + problems.

---

## API Endpoints

| Method | Path | Auth | Description |
|--------|------|------|-------------|
| POST | /api/v1/auth/register | Public | Register |
| POST | /api/v1/auth/login | Public | Login (httpOnly cookie + JWT) |
| GET | /api/v1/auth/me | Optional | Current user |
| POST | /api/v1/auth/logout | Public | Clear cookie |
| GET | /api/v1/problems | Optional | List problems (paginated, filterable) |
| GET | /api/v1/problems/{slug} | Optional | Problem detail + solution |
| POST | /api/v1/problems | Admin | Create problem |
| PUT | /api/v1/problems/{slug} | Admin | Update problem |
| DELETE | /api/v1/problems/{slug} | Admin | Soft-delete problem |
| POST | /api/v1/problems/{slug}/test-cases | Admin | Add test case |
| GET | /api/v1/submissions | User | List submissions |
| POST | /api/v1/submissions | User | Submit code |
| GET | /api/v1/submissions/{id} | User | Submission detail + results |
| WS | /api/v1/submissions/{id}/ws | Public | Real-time status |
| GET | /api/v1/admin/users | Admin | List users |
| PATCH | /api/v1/admin/users/{id}/role | Admin | Change user role |
| GET | /api/v1/health | Public | Health check |
| GET | /metrics | Public | Prometheus metrics |

---

## Judge Status Flow

```
User submits code
  │
  ▼
status: pending ──► Redis enqueue
  │
  ▼
Worker picks up
  │
  ▼
status: running ──► Docker sandbox per test case
  │                  (network=none, memory limit, read-only)
  ▼
Final status:
  accepted          — all test cases passed
  wrong_answer      — output mismatch
  time_limit_exceeded — exceeded time limit
  runtime_error     — exception or non-zero exit
  error             — internal judge failure
```

---

## Project Structure

```
online-judge/
├── app/
│   ├── main.py                  # FastAPI entry
│   ├── api/v1/                  # Route layer
│   ├── core/                    # Config, DB, security, rate-limit, logging, redis
│   ├── models/                  # SQLAlchemy models (6 tables)
│   ├── schemas/                 # Pydantic validation
│   ├── services/                # Business logic layer
│   ├── judge/                   # Executor, sandbox, comparator, worker
│   └── static/                  # Frontend SPA + CodeMirror
├── tests/                       # pytest (unit + integration + concurrency)
├── alembic/                     # DB migrations
├── sandbox/                     # Docker sandbox image
├── scripts/                     # Seed data scripts
├── .github/workflows/           # CI/CD
├── docker-compose.yml
├── Dockerfile
└── requirements.txt
```

---

## Development

```bash
# Install deps
pip install -r requirements.txt

# Run API (with PostgreSQL + Redis running)
uvicorn app.main:app --reload

# Run worker (separate terminal)
arq app.judge.worker.WorkerSettings

# Run tests
TEST_DATABASE_URL="postgresql+asyncpg://judge:judge_pass@localhost:5432/online_judge_test" pytest -v
```

---

## License

MIT License
