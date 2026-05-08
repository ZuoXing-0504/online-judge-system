import uuid
from datetime import datetime, timezone

from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import joinedload

from app.core.exceptions import ConflictException, NotFoundException, BadRequestException
from app.models.contest import Contest, ContestParticipant, ContestProblem, ContestSubmissionAttempt
from app.models.problem import Problem
from app.models.submission import Submission
from app.models.user import User


async def create_contest(db: AsyncSession, data, author_id: uuid.UUID) -> Contest:
    existing = await db.execute(select(Contest).where(Contest.slug == data.slug))
    if existing.scalar_one_or_none():
        raise ConflictException(f"Contest '{data.slug}' already exists")

    contest = Contest(
        title=data.title,
        slug=data.slug,
        description=data.description,
        start_time=data.start_time,
        end_time=data.end_time,
        is_public=data.is_public,
        freeze_minutes=data.freeze_minutes,
        created_by=author_id,
    )
    db.add(contest)
    await db.flush()

    for idx, slug in enumerate(data.problem_slugs):
        result = await db.execute(select(Problem).where(Problem.slug == slug))
        problem = result.scalar_one_or_none()
        if problem:
            db.add(ContestProblem(
                contest_id=contest.id, problem_id=problem.id,
                order=idx, label=chr(65 + idx),
            ))

    await db.commit()
    result = await db.execute(
        select(Contest)
        .options(joinedload(Contest.problems).joinedload(ContestProblem.problem))
        .where(Contest.id == contest.id)
    )
    created = result.unique().scalar_one()
    created.participant_count = 0
    created.problem_count = len(created.problems)
    return created


async def get_contest(db: AsyncSession, slug: str) -> Contest:
    result = await db.execute(
        select(Contest)
        .options(joinedload(Contest.problems).joinedload(ContestProblem.problem))
        .where(Contest.slug == slug)
    )
    contest = result.unique().scalar_one_or_none()
    if not contest:
        raise NotFoundException("Contest not found")
    contest.participant_count = (
        await db.execute(
            select(func.count())
            .select_from(ContestParticipant)
            .where(ContestParticipant.contest_id == contest.id)
        )
    ).scalar() or 0
    contest.problem_count = len(contest.problems)
    return contest


async def list_contests(db: AsyncSession, page: int = 1, page_size: int = 20) -> tuple[list[Contest], int]:
    query = select(Contest).order_by(Contest.start_time.desc())
    count_q = select(func.count()).select_from(Contest)
    total = (await db.execute(count_q)).scalar() or 0
    offset = (page - 1) * page_size
    result = await db.execute(query.offset(offset).limit(page_size))
    contests = list(result.scalars().all())
    for c in contests:
        c.participant_count = (await db.execute(
            select(func.count()).select_from(ContestParticipant).where(ContestParticipant.contest_id == c.id)
        )).scalar() or 0
        c.problem_count = (await db.execute(
            select(func.count()).select_from(ContestProblem).where(ContestProblem.contest_id == c.id)
        )).scalar() or 0
    return contests, total


async def register_participant(db: AsyncSession, contest_slug: str, user: User) -> ContestParticipant:
    contest = await get_contest(db, contest_slug)
    now = datetime.now(timezone.utc)
    if now > contest.end_time:
        raise BadRequestException("Contest has ended")
    if now < contest.start_time:
        raise BadRequestException("Contest has not started yet")

    existing = await db.execute(
        select(ContestParticipant).where(
            ContestParticipant.contest_id == contest.id,
            ContestParticipant.user_id == user.id,
        )
    )
    if existing.scalar_one_or_none():
        raise ConflictException("Already registered")

    cp = ContestParticipant(contest_id=contest.id, user_id=user.id)
    db.add(cp)
    await db.commit()
    return cp


async def get_leaderboard(db: AsyncSession, contest_slug: str) -> list[dict]:
    contest = await get_contest(db, contest_slug)
    result = await db.execute(
        select(ContestParticipant)
        .options(joinedload(ContestParticipant.user))
        .where(ContestParticipant.contest_id == contest.id)
        .order_by(ContestParticipant.solved_count.desc(), ContestParticipant.penalty.asc())
    )
    participants = result.unique().scalars().all()
    board = []
    for rank, p in enumerate(participants, 1):
        board.append({
            "rank": rank,
            "user_id": p.user_id,
            "username": p.user.username,
            "solved_count": p.solved_count,
            "penalty": p.penalty,
            "score": p.score,
        })
    return board


async def update_contest_scores(db: AsyncSession, submission: Submission) -> None:
    if submission.status in ("pending", "running", "error"):
        return

    cps = await db.execute(
        select(ContestProblem).where(ContestProblem.problem_id == submission.problem_id)
    )
    contest_problems = cps.scalars().all()
    if not contest_problems:
        return

    for cp in contest_problems:
        contest = await db.get(Contest, cp.contest_id)
        if not contest:
            continue
        now = datetime.now(timezone.utc)
        if now < contest.start_time or now > contest.end_time:
            continue

        participant = await db.execute(
            select(ContestParticipant).where(
                ContestParticipant.contest_id == contest.id,
                ContestParticipant.user_id == submission.user_id,
            )
        )
        participant = participant.scalar_one_or_none()
        if not participant:
            continue

        # Check if already solved this problem
        already_solved = await db.execute(
            select(ContestSubmissionAttempt).where(
                ContestSubmissionAttempt.contest_id == contest.id,
                ContestSubmissionAttempt.user_id == submission.user_id,
                ContestSubmissionAttempt.problem_id == submission.problem_id,
                ContestSubmissionAttempt.status == "accepted",
            )
        )
        if already_solved.scalar_one_or_none():
            continue

        # Record attempt (skip duplicates from retries)
        existing_attempt = await db.execute(
            select(ContestSubmissionAttempt).where(
                ContestSubmissionAttempt.submission_id == submission.id,
            )
        )
        if existing_attempt.scalar_one_or_none():
            continue

        attempt = ContestSubmissionAttempt(
            contest_id=contest.id,
            user_id=submission.user_id,
            problem_id=submission.problem_id,
            submission_id=submission.id,
            status=submission.status,
        )
        db.add(attempt)

        if submission.status == "accepted":
            elapsed = int((submission.created_at - contest.start_time).total_seconds())
            wrong_count = (
                await db.execute(
                    select(ContestSubmissionAttempt).where(
                        ContestSubmissionAttempt.contest_id == contest.id,
                        ContestSubmissionAttempt.user_id == submission.user_id,
                        ContestSubmissionAttempt.problem_id == submission.problem_id,
                        ContestSubmissionAttempt.status != "accepted",
                    )
                )
            ).scalars().all()
            penalty = elapsed + len(wrong_count) * 1200  # 20 min per wrong attempt
            participant.solved_count += 1
            participant.penalty += penalty
            participant.score += 100
            await db.commit()
            return
