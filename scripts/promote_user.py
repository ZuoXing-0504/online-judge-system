import argparse
import asyncio
from pathlib import Path
import sys

ROOT_DIR = Path(__file__).resolve().parents[1]
if str(ROOT_DIR) not in sys.path:
    sys.path.insert(0, str(ROOT_DIR))

from sqlalchemy import or_, select

from app.core.database import async_session_factory
from app.models.user import User


async def promote_user(identity: str) -> None:
    async with async_session_factory() as session:
        result = await session.execute(
            select(User).where(or_(User.username == identity, User.email == identity))
        )
        user = result.scalar_one_or_none()
        if user is None:
            raise SystemExit(f"User not found: {identity}")

        if user.role != "admin":
            user.role = "admin"
            await session.commit()
            await session.refresh(user)

        print(f"Promoted to admin: {user.username} <{user.email}>")


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Promote a user to admin by username or email.")
    parser.add_argument("identity", help="Username or email to promote.")
    return parser.parse_args()


if __name__ == "__main__":
    args = parse_args()
    asyncio.run(promote_user(args.identity))
