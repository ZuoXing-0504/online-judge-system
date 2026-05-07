import uuid

from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import joinedload, selectinload

from app.core.config import settings
from app.core.exceptions import ForbiddenException, NotFoundException
from app.models.problem import Problem
from app.models.submission import Submission
from app.models.submission_test_result import SubmissionTestResult
from app.models.test_case import TestCase
from app.models.user import User


async def create_submission(
    db: AsyncSession, user: User, problem_slug: str, code: str, language: str = "python"
) -> Submission:
    result = await db.execute(select(Problem).where(Problem.slug == problem_slug))
    problem = result.scalar_one_or_none()
    if not problem:
        raise NotFoundException("Problem not found")
    if not problem.is_public and user.role != "admin":
        raise NotFoundException("Problem not found")

    submission = Submission(
        user_id=user.id,
        problem_id=problem.id,
        code=code,
        language=language,
        status="pending",
    )
    db.add(submission)
    await db.commit()
    await db.refresh(submission)
    return submission


async def get_submission(db: AsyncSession, submission_id: uuid.UUID, user: User) -> Submission:
    result = await db.execute(
        select(Submission)
        .options(
            selectinload(Submission.test_results),
            joinedload(Submission.problem),
            joinedload(Submission.user),
        )
        .where(Submission.id == submission_id)
    )
    submission = result.unique().scalar_one_or_none()
    if not submission:
        raise NotFoundException("Submission not found")
    if submission.user_id != user.id and user.role != "admin":
        raise ForbiddenException("Cannot view this submission")
    return submission


async def get_submission_raw(db: AsyncSession, submission_id: uuid.UUID) -> Submission | None:
    result = await db.execute(
        select(Submission)
        .options(
            selectinload(Submission.test_results),
            joinedload(Submission.problem),
            joinedload(Submission.user),
        )
        .where(Submission.id == submission_id)
    )
    return result.unique().scalar_one_or_none()


async def list_submissions(
    db: AsyncSession,
    user: User,
    page: int = 1,
    page_size: int = 20,
    problem_slug: str | None = None,
    status: str | None = None,
    is_admin: bool = False,
) -> tuple[list[Submission], int]:
    query = select(Submission).options(joinedload(Submission.problem))
    if not is_admin:
        query = query.where(Submission.user_id == user.id)
    if problem_slug:
        query = query.join(Submission.problem).where(Problem.slug == problem_slug)
    if status:
        query = query.where(Submission.status == status)
    query = query.order_by(Submission.created_at.desc())

    count_query = select(func.count()).select_from(query.subquery())
    total_result = await db.execute(count_query)
    total = total_result.scalar() or 0

    offset = (page - 1) * page_size
    result = await db.execute(query.offset(offset).limit(page_size))
    return list(result.unique().scalars().all()), total
