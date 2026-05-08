from fastapi import APIRouter, Depends
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import joinedload

from app.core.database import get_db
from app.core.dependencies import get_current_user, get_current_user_optional
from app.models.comment import Comment
from app.models.user import User
from app.schemas.comment import CommentCreate, CommentRead

router = APIRouter()


@router.get("/problems/{slug}/comments", response_model=list[CommentRead])
async def list_comments(
    slug: str,
    db: AsyncSession = Depends(get_db),
):
    from app.services.problem_service import get_by_slug

    problem = await get_by_slug(db, slug)
    result = await db.execute(
        select(Comment)
        .options(joinedload(Comment.user))
        .where(Comment.problem_id == problem.id)
        .order_by(Comment.created_at.asc())
    )
    comments = result.unique().scalars().all()
    return [
        CommentRead(
            id=c.id, problem_id=c.problem_id, user_id=c.user_id,
            username=c.user.username, content=c.content, created_at=c.created_at,
        )
        for c in comments
    ]


@router.post("/problems/{slug}/comments", response_model=CommentRead, status_code=201)
async def create_comment(
    slug: str,
    data: CommentCreate,
    db: AsyncSession = Depends(get_db),
    user: User = Depends(get_current_user),
):
    from app.services.problem_service import get_by_slug

    problem = await get_by_slug(db, slug)
    comment = Comment(problem_id=problem.id, user_id=user.id, content=data.content)
    db.add(comment)
    await db.commit()
    await db.refresh(comment)
    return CommentRead(
        id=comment.id, problem_id=comment.problem_id, user_id=comment.user_id,
        username=user.username, content=comment.content, created_at=comment.created_at,
    )
