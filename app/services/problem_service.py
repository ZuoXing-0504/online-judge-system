import uuid

from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.exceptions import ConflictException, NotFoundException
from app.models.problem import Problem
from app.models.test_case import TestCase
from app.schemas.problem import ProblemCreate, ProblemUpdate
from app.schemas.test_case import TestCaseCreate, TestCaseUpdate


async def _get_by_slug(db: AsyncSession, slug: str) -> Problem | None:
    result = await db.execute(select(Problem).where(Problem.slug == slug))
    return result.scalar_one_or_none()


async def get_by_slug(db: AsyncSession, slug: str) -> Problem:
    problem = await _get_by_slug(db, slug)
    if not problem:
        raise NotFoundException("Problem not found")
    return problem


async def list_problems(
    db: AsyncSession,
    page: int = 1,
    page_size: int = 20,
    difficulty: str | None = None,
    search: str | None = None,
    is_admin: bool = False,
) -> tuple[list[Problem], int]:
    query = select(Problem)
    if not is_admin:
        query = query.where(Problem.is_public == True)
    if difficulty:
        query = query.where(Problem.difficulty == difficulty)
    if search:
        query = query.where(Problem.title.ilike(f"%{search}%"))
    query = query.order_by(Problem.created_at.desc())

    count_query = select(func.count()).select_from(query.subquery())
    total_result = await db.execute(count_query)
    total = total_result.scalar() or 0

    offset = (page - 1) * page_size
    result = await db.execute(query.offset(offset).limit(page_size))
    return list(result.scalars().all()), total


async def create_problem(db: AsyncSession, data: ProblemCreate, author_id: uuid.UUID) -> Problem:
    existing = await _get_by_slug(db, data.slug)
    if existing:
        raise ConflictException(f"Problem slug '{data.slug}' already exists")
    problem = Problem(**data.model_dump(), created_by=author_id)
    db.add(problem)
    await db.commit()
    await db.refresh(problem)
    return problem


async def update_problem(db: AsyncSession, slug: str, data: ProblemUpdate) -> Problem:
    problem = await get_by_slug(db, slug)
    update_data = data.model_dump(exclude_unset=True)
    for key, value in update_data.items():
        setattr(problem, key, value)
    await db.commit()
    await db.refresh(problem)
    return problem


async def delete_problem(db: AsyncSession, slug: str) -> None:
    problem = await get_by_slug(db, slug)
    await db.delete(problem)
    await db.commit()


async def get_test_case(db: AsyncSession, test_case_id: uuid.UUID) -> TestCase:
    result = await db.execute(select(TestCase).where(TestCase.id == test_case_id))
    tc = result.scalar_one_or_none()
    if not tc:
        raise NotFoundException("Test case not found")
    return tc


async def list_test_cases(
    db: AsyncSession, problem_slug: str, page: int = 1, page_size: int = 50
) -> tuple[list[TestCase], int]:
    problem = await get_by_slug(db, problem_slug)
    query = select(TestCase).where(TestCase.problem_id == problem.id).order_by(TestCase.order)
    count_query = select(func.count()).select_from(query.subquery())
    total_result = await db.execute(count_query)
    total = total_result.scalar() or 0
    offset = (page - 1) * page_size
    result = await db.execute(query.offset(offset).limit(page_size))
    return list(result.scalars().all()), total


async def create_test_case(
    db: AsyncSession, problem_slug: str, data: TestCaseCreate
) -> TestCase:
    problem = await get_by_slug(db, problem_slug)
    tc = TestCase(**data.model_dump(), problem_id=problem.id)
    db.add(tc)
    await db.commit()
    await db.refresh(tc)
    return tc


async def update_test_case(
    db: AsyncSession, problem_slug: str, test_case_id: uuid.UUID, data: TestCaseUpdate
) -> TestCase:
    await get_by_slug(db, problem_slug)
    tc = await get_test_case(db, test_case_id)
    update_data = data.model_dump(exclude_unset=True)
    for key, value in update_data.items():
        setattr(tc, key, value)
    await db.commit()
    await db.refresh(tc)
    return tc


async def delete_test_case(
    db: AsyncSession, problem_slug: str, test_case_id: uuid.UUID
) -> None:
    await get_by_slug(db, problem_slug)
    tc = await get_test_case(db, test_case_id)
    await db.delete(tc)
    await db.commit()
