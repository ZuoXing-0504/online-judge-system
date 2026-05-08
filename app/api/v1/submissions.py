import asyncio
import json
import uuid

from fastapi import APIRouter, Depends, Query, Request, WebSocket, WebSocketDisconnect
from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker

from app.core.database import get_db
from app.core.dependencies import get_current_user, resolve_websocket_user
from app.core.exceptions import ForbiddenException, NotFoundException, UnauthorizedException
from app.core.rate_limit import limiter
from app.core.redis import get_redis_pool
from app.models.submission import Submission
from app.models.user import User
from app.schemas.common import PaginatedResponse
from app.schemas.submission import (
    SubmissionCreate,
    SubmissionCreateResponse,
    SubmissionDetail,
    SubmissionList,
    TestResultRead,
)
from app.services import submission_service

router = APIRouter()


def _build_list_item(sub: Submission) -> SubmissionList:
    problem = sub.problem
    return SubmissionList(
        id=sub.id,
        problem_id=sub.problem_id,
        problem_slug=problem.slug if problem else "",
        problem_title=problem.title if problem else "",
        status=sub.status,
        total_test_cases=sub.total_test_cases,
        passed_test_cases=sub.passed_test_cases,
        max_execution_time_ms=sub.max_execution_time_ms,
        max_memory_used_kb=sub.max_memory_used_kb,
        created_at=sub.created_at,
    )


def _build_detail(sub: Submission) -> SubmissionDetail:
    test_results = []
    for tr in sub.test_results:
        test_results.append(TestResultRead(
            id=tr.id,
            test_case_id=tr.test_case_id,
            status=tr.status,
            execution_time_ms=tr.execution_time_ms,
            memory_used_kb=tr.memory_used_kb,
            output=tr.output,
            expected_output=tr.expected_output,
            error_message=tr.error_message,
            created_at=tr.created_at,
        ))
    return SubmissionDetail(
        id=sub.id,
        user_id=sub.user_id,
        username=sub.user.username if sub.user else "",
        problem_id=sub.problem_id,
        problem_title=sub.problem.title if sub.problem else "",
        problem_slug=sub.problem.slug if sub.problem else "",
        language=sub.language,
        code=sub.code,
        status=sub.status,
        total_test_cases=sub.total_test_cases,
        passed_test_cases=sub.passed_test_cases,
        max_execution_time_ms=sub.max_execution_time_ms,
        max_memory_used_kb=sub.max_memory_used_kb,
        error_message=sub.error_message,
        created_at=sub.created_at,
        test_results=test_results,
    )


@router.post("", response_model=SubmissionCreateResponse, status_code=202)
@limiter.limit("30/minute")
async def submit_code(
    request: Request,
    data: SubmissionCreate,
    db: AsyncSession = Depends(get_db),
    user: User = Depends(get_current_user),
):
    submission = await submission_service.create_submission(
        db, user, data.problem_slug, data.code, data.language,
    )
    redis_pool = await get_redis_pool()
    await redis_pool.enqueue_job("judge_job", str(submission.id))
    return submission


@router.get("", response_model=PaginatedResponse)
async def list_submissions(
    page: int = Query(1, ge=1),
    page_size: int = Query(20, ge=1, le=100),
    problem_slug: str | None = None,
    status: str | None = None,
    db: AsyncSession = Depends(get_db),
    user: User = Depends(get_current_user),
):
    is_admin = user.role == "admin"

    subs, total = await submission_service.list_submissions(
        db, user, page=page, page_size=page_size,
        problem_slug=problem_slug, status=status, is_admin=is_admin,
    )
    items = [_build_list_item(s) for s in subs]
    return PaginatedResponse(
        items=items, total=total, page=page, page_size=page_size,
        total_pages=max(1, (total + page_size - 1) // page_size),
    )


@router.get("/{submission_id}", response_model=SubmissionDetail)
async def get_submission(
    submission_id: uuid.UUID,
    db: AsyncSession = Depends(get_db),
    user: User = Depends(get_current_user),
):
    sub = await submission_service.get_submission(db, submission_id, user)
    return _build_detail(sub)


@router.websocket("/{submission_id}/ws")
async def submission_status_ws(
    websocket: WebSocket,
    submission_id: uuid.UUID,
    db: AsyncSession = Depends(get_db),
):
    try:
        user = await resolve_websocket_user(websocket, db)
        await submission_service.get_submission(db, submission_id, user)
    except UnauthorizedException:
        await websocket.close(code=4401, reason="Not authenticated")
        return
    except ForbiddenException:
        await websocket.close(code=4403, reason="Cannot view this submission")
        return
    except NotFoundException:
        await websocket.close(code=4404, reason="Submission not found")
        return

    await websocket.accept()
    poll_session_factory = async_sessionmaker(
        db.bind,
        class_=AsyncSession,
        expire_on_commit=False,
    )

    for _ in range(120):
        try:
            async with poll_session_factory() as poll_db:
                sub = await submission_service.get_submission(
                    poll_db,
                    submission_id,
                    user,
                )

                detail = _build_detail(sub)
                await websocket.send_json(
                    json.loads(detail.model_dump_json())
                )

                if sub.status not in ("pending", "running"):
                    return

            await asyncio.sleep(1)
        except WebSocketDisconnect:
            return
        except ForbiddenException:
            await websocket.close(code=4403, reason="Cannot view this submission")
            return
        except NotFoundException:
            await websocket.send_json({"error": "Submission not found"})
            return
        except Exception:
            await asyncio.sleep(1)
