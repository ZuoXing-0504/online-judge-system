import uuid

from fastapi import APIRouter, Depends, Query
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.database import get_db
from app.core.dependencies import get_current_user_optional, require_admin
from app.models.user import User
from app.schemas.common import PaginatedResponse
from app.schemas.problem import ProblemCreate, ProblemList, ProblemRead, ProblemUpdate
from app.schemas.test_case import TestCaseCreate, TestCaseRead, TestCaseUpdate
from app.services import problem_service

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
