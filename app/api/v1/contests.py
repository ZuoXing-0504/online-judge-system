from fastapi import APIRouter, Depends, Query
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.database import get_db
from app.core.dependencies import get_current_user, require_admin, get_current_user_optional
from app.models.user import User
from app.schemas.common import PaginatedResponse
from app.schemas.contest import ContestCreate, ContestList, ContestRead, LeaderboardEntry
from app.services import contest_service

router = APIRouter()


@router.get("", response_model=PaginatedResponse)
async def list_contests(
    page: int = Query(1, ge=1),
    page_size: int = Query(20, ge=1, le=50),
    db: AsyncSession = Depends(get_db),
):
    contests, total = await contest_service.list_contests(db, page, page_size)
    items = [ContestList.model_validate(c) for c in contests]
    return PaginatedResponse(
        items=items, total=total, page=page, page_size=page_size,
        total_pages=max(1, (total + page_size - 1) // page_size),
    )


@router.post("", response_model=ContestRead, status_code=201)
async def create_contest(
    data: ContestCreate,
    db: AsyncSession = Depends(get_db),
    admin: User = Depends(require_admin),
):
    contest = await contest_service.create_contest(db, data, admin.id)
    return contest


@router.get("/{slug}")
async def get_contest(
    slug: str,
    db: AsyncSession = Depends(get_db),
):
    contest = await contest_service.get_contest(db, slug)
    return {
        "id": str(contest.id),
        "title": contest.title,
        "slug": contest.slug,
        "description": contest.description,
        "start_time": contest.start_time.isoformat(),
        "end_time": contest.end_time.isoformat(),
        "is_public": contest.is_public,
        "freeze_minutes": contest.freeze_minutes,
        "created_by": str(contest.created_by),
        "created_at": contest.created_at.isoformat(),
        "updated_at": contest.updated_at.isoformat(),
        "participant_count": contest.participant_count if hasattr(contest, "participant_count") else 0,
        "problem_count": len(contest.problems),
        "problems": [
            {
                "id": str(cp.id),
                "problem_id": str(cp.problem_id),
                "label": cp.label or "",
                "order": cp.order or 0,
                "title": cp.problem.title if cp.problem else "",
                "slug": cp.problem.slug if cp.problem else "",
            }
            for cp in contest.problems
        ],
    }


@router.post("/{slug}/register", status_code=201)
async def register_for_contest(
    slug: str,
    db: AsyncSession = Depends(get_db),
    user: User = Depends(get_current_user),
):
    await contest_service.register_participant(db, slug, user)
    return {"detail": "Registered"}


@router.get("/{slug}/leaderboard", response_model=list[LeaderboardEntry])
async def contest_leaderboard(
    slug: str,
    db: AsyncSession = Depends(get_db),
):
    return await contest_service.get_leaderboard(db, slug)
