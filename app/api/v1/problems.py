import uuid
from fastapi import APIRouter, Depends, Query, Request
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.database import get_db
from app.core.dependencies import get_current_user, get_current_user_optional, require_admin
from app.models.user import User
from app.schemas.common import PaginatedResponse
from app.schemas.problem import ProblemCreate, ProblemList, ProblemRead, ProblemUpdate
from app.schemas.test_case import TestCaseCreate, TestCaseRead, TestCaseUpdate
from app.services import problem_service
from app.services.audit_service import create_audit_log

router = APIRouter()


@router.get("", response_model=PaginatedResponse)
async def list_problems(
    page: int = Query(1, ge=1),
    page_size: int = Query(20, ge=1, le=100),
    difficulty: str | None = Query(None, pattern=r"^(easy|medium|hard)$"),
    search: str | None = None,
    db: AsyncSession = Depends(get_db),
    user: User | None = Depends(get_current_user_optional),
):
    is_admin = user is not None and user.role == "admin"
    problems, total = await problem_service.list_problems(
        db, page=page, page_size=page_size,
        difficulty=difficulty, search=search, is_admin=is_admin,
    )
    items = [ProblemList.model_validate(p) for p in problems]
    return PaginatedResponse(
        items=items, total=total, page=page, page_size=page_size,
        total_pages=max(1, (total + page_size - 1) // page_size),
    )


@router.get("/{slug}", response_model=ProblemRead)
async def get_problem(
    slug: str,
    db: AsyncSession = Depends(get_db),
    user: User | None = Depends(get_current_user_optional),
):
    problem = await problem_service.get_by_slug(db, slug)
    is_admin = user is not None and user.role == "admin"
    if not problem.is_public and not is_admin:
        from app.core.exceptions import NotFoundException
        raise NotFoundException("Problem not found")
    return problem


@router.post("/{slug}/run")
async def run_sample(
    slug: str,
    data: dict,
    db: AsyncSession = Depends(get_db),
):
    from app.judge.executor import execute_test_case
    from app.models.test_case import TestCase as TestCaseModel  # noqa: F811

    problem = await problem_service.get_by_slug(db, slug)
    result = await db.execute(
        select(TestCaseModel)
        .where(TestCaseModel.problem_id == problem.id, TestCaseModel.is_sample)
        .order_by(TestCaseModel.order)
        .limit(1)
    )
    sample = result.scalar_one_or_none()
    if sample:
        exec_result = await execute_test_case(
            code=data.get("code", ""),
            input_data=sample.input,
            expected_output=sample.expected_output,
            time_limit_ms=problem.time_limit_ms,
            memory_limit_kb=problem.memory_limit_kb,
            language=data.get("language", "python"),
        )
        return {"status": exec_result.status, "output": exec_result.output or "",
                "expected": sample.expected_output or "",
                "error": exec_result.error_message or ""}
    return {"status": "no_sample", "output": "", "expected": "", "error": "No sample test case"}


@router.get("/{slug}/status")
async def get_problem_status(
    slug: str,
    db: AsyncSession = Depends(get_db),
    user: User = Depends(get_current_user),
):
    from sqlalchemy import func
    from app.models.submission import Submission

    problem = await problem_service.get_by_slug(db, slug)
    result = await db.execute(
        select(Submission.status, func.count())
        .where(Submission.user_id == user.id, Submission.problem_id == problem.id)
        .group_by(Submission.status)
    )
    rows = dict(result.all())
    accepted = rows.get("accepted", 0)
    total = sum(rows.values())
    return {"slug": slug, "accepted": accepted > 0, "total_attempts": total, "accepted_count": accepted}


@router.post("", response_model=ProblemRead, status_code=201)
async def create_problem(
    data: ProblemCreate,
    db: AsyncSession = Depends(get_db),
    admin: User = Depends(require_admin),
):
    return await problem_service.create_problem(db, data, admin.id)


@router.put("/{slug}", response_model=ProblemRead)
async def update_problem(
    slug: str,
    data: ProblemUpdate,
    db: AsyncSession = Depends(get_db),
    admin: User = Depends(require_admin),
):
    return await problem_service.update_problem(db, slug, data)


@router.delete("/{slug}", status_code=204)
async def delete_problem(
    slug: str,
    db: AsyncSession = Depends(get_db),
    admin: User = Depends(require_admin),
):
    await problem_service.delete_problem(db, slug)


@router.get("/{slug}/test-cases", response_model=PaginatedResponse)
async def list_test_cases(
    slug: str,
    page: int = Query(1, ge=1),
    page_size: int = Query(50, ge=1, le=100),
    db: AsyncSession = Depends(get_db),
    admin: User = Depends(require_admin),
):
    cases, total = await problem_service.list_test_cases(db, slug, page, page_size)
    items = [TestCaseRead.model_validate(tc) for tc in cases]
    return PaginatedResponse(
        items=items, total=total, page=page, page_size=page_size,
        total_pages=max(1, (total + page_size - 1) // page_size),
    )


@router.post("/{slug}/test-cases", response_model=TestCaseRead, status_code=201)
async def create_test_case(
    slug: str,
    data: TestCaseCreate,
    db: AsyncSession = Depends(get_db),
    admin: User = Depends(require_admin),
):
    return await problem_service.create_test_case(db, slug, data)


@router.put("/{slug}/test-cases/{test_case_id}", response_model=TestCaseRead)
async def update_test_case(
    slug: str,
    test_case_id: uuid.UUID,
    data: TestCaseUpdate,
    db: AsyncSession = Depends(get_db),
    admin: User = Depends(require_admin),
):
    return await problem_service.update_test_case(db, slug, test_case_id, data)


@router.delete("/{slug}/test-cases/{test_case_id}", status_code=204)
async def delete_test_case(
    slug: str,
    test_case_id: uuid.UUID,
    db: AsyncSession = Depends(get_db),
    admin: User = Depends(require_admin),
):
    await problem_service.delete_test_case(db, slug, test_case_id)
