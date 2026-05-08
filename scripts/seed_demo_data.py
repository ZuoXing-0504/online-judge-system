import asyncio
from collections.abc import Sequence
from pathlib import Path
import sys

ROOT_DIR = Path(__file__).resolve().parents[1]
if str(ROOT_DIR) not in sys.path:
    sys.path.insert(0, str(ROOT_DIR))

from sqlalchemy import select

from app.core.database import async_session_factory
from app.core.security import hash_password
from app.models.problem import Problem
from app.models.test_case import TestCase
from app.models.user import User

ADMIN_USERNAME = "admin"
ADMIN_EMAIL = "admin@local.dev"
ADMIN_PASSWORD = "Admin123456"

PROBLEMS: Sequence[dict] = [
    {
        "title": "Sum Two Numbers",
        "slug": "sum-two-numbers",
        "description": (
            "Read two integers a and b from standard input and print their sum.\n"
            "The two numbers fit in a signed 64-bit integer."
        ),
        "difficulty": "easy",
        "time_limit_ms": 1000,
        "memory_limit_kb": 65536,
        "input_description": "One line with two integers a and b separated by spaces.",
        "output_description": "Print a single integer: a + b.",
        "sample_input": "3 5\n",
        "sample_output": "8\n",
        "test_cases": [
            {"input": "3 5\n", "expected_output": "8\n", "is_sample": True, "order": 0},
            {"input": "-7 4\n", "expected_output": "-3\n", "is_sample": False, "order": 1},
            {"input": "100000 234567\n", "expected_output": "334567\n", "is_sample": False, "order": 2},
        ],
    },
    {
        "title": "Word Counter",
        "slug": "word-counter",
        "description": (
            "Read all input as text and count how many words it contains.\n"
            "A word is any maximal sequence of non-whitespace characters."
        ),
        "difficulty": "easy",
        "time_limit_ms": 1000,
        "memory_limit_kb": 65536,
        "input_description": "One or more lines of text.",
        "output_description": "Print the total number of words.",
        "sample_input": "hello online judge\n",
        "sample_output": "3\n",
        "test_cases": [
            {"input": "hello online judge\n", "expected_output": "3\n", "is_sample": True, "order": 0},
            {"input": "single\n", "expected_output": "1\n", "is_sample": False, "order": 1},
            {"input": "many   spaces\nand\t tabs\n", "expected_output": "4\n", "is_sample": False, "order": 2},
        ],
    },
    {
        "title": "Distinct Sort",
        "slug": "distinct-sort",
        "description": (
            "Given n integers, remove duplicates, sort the remaining values in ascending order, "
            "and print them on one line separated by spaces."
        ),
        "difficulty": "medium",
        "time_limit_ms": 1500,
        "memory_limit_kb": 131072,
        "input_description": (
            "The first line contains n.\n"
            "The second line contains n integers."
        ),
        "output_description": "Print the distinct values in ascending order separated by spaces.",
        "sample_input": "6\n3 1 3 2 2 5\n",
        "sample_output": "1 2 3 5\n",
        "test_cases": [
            {"input": "6\n3 1 3 2 2 5\n", "expected_output": "1 2 3 5\n", "is_sample": True, "order": 0},
            {"input": "5\n10 9 8 7 6\n", "expected_output": "6 7 8 9 10\n", "is_sample": False, "order": 1},
            {"input": "7\n4 4 4 4 4 4 4\n", "expected_output": "4\n", "is_sample": False, "order": 2},
        ],
    },
    {
        "title": "Balanced Brackets",
        "slug": "balanced-brackets",
        "description": (
            "Given a string containing only (), [], and {} characters, determine whether the "
            "brackets are balanced. Print YES if balanced, otherwise print NO."
        ),
        "difficulty": "medium",
        "time_limit_ms": 1500,
        "memory_limit_kb": 65536,
        "input_description": "A single line containing a bracket string.",
        "output_description": "Print YES or NO.",
        "sample_input": "{[()]}\n",
        "sample_output": "YES\n",
        "test_cases": [
            {"input": "{[()]}\n", "expected_output": "YES\n", "is_sample": True, "order": 0},
            {"input": "([)]\n", "expected_output": "NO\n", "is_sample": False, "order": 1},
            {"input": "(((())))[]{}\n", "expected_output": "YES\n", "is_sample": False, "order": 2},
        ],
    },
    {
        "title": "Climbing Stairs Mod",
        "slug": "climbing-stairs-mod",
        "description": (
            "You are standing at step 0 and want to reach step n. Each move can advance by 1 or 2 steps. "
            "Compute the number of different ways modulo 1000000007."
        ),
        "difficulty": "hard",
        "time_limit_ms": 2000,
        "memory_limit_kb": 131072,
        "input_description": "A single integer n.",
        "output_description": "Print the number of ways modulo 1000000007.",
        "sample_input": "5\n",
        "sample_output": "8\n",
        "test_cases": [
            {"input": "5\n", "expected_output": "8\n", "is_sample": True, "order": 0},
            {"input": "1\n", "expected_output": "1\n", "is_sample": False, "order": 1},
            {"input": "10\n", "expected_output": "89\n", "is_sample": False, "order": 2},
        ],
    },
]


async def ensure_admin_user() -> User:
    async with async_session_factory() as session:
        result = await session.execute(
            select(User).where((User.username == ADMIN_USERNAME) | (User.email == ADMIN_EMAIL))
        )
        admin = result.scalar_one_or_none()
        if admin is not None:
            if admin.role != "admin":
                admin.role = "admin"
                await session.commit()
                await session.refresh(admin)
            return admin

        admin = User(
            username=ADMIN_USERNAME,
            email=ADMIN_EMAIL,
            hashed_password=hash_password(ADMIN_PASSWORD),
            role="admin",
            is_active=True,
        )
        session.add(admin)
        await session.commit()
        await session.refresh(admin)
        return admin


async def seed_problem(admin_id, payload: dict) -> tuple[str, str]:
    async with async_session_factory() as session:
        existing_result = await session.execute(select(Problem).where(Problem.slug == payload["slug"]))
        problem = existing_result.scalar_one_or_none()
        if problem is not None:
            return payload["slug"], "skipped"

        problem_data = {key: value for key, value in payload.items() if key != "test_cases"}
        problem = Problem(**problem_data, created_by=admin_id, is_public=True)
        session.add(problem)
        await session.flush()

        for test_case in payload["test_cases"]:
            session.add(TestCase(problem_id=problem.id, **test_case))

        await session.commit()
        return payload["slug"], "created"


async def main() -> None:
    admin = await ensure_admin_user()

    created = 0
    skipped = 0
    for payload in PROBLEMS:
        slug, status = await seed_problem(admin.id, payload)
        print(f"{slug}: {status}")
        if status == "created":
            created += 1
        else:
            skipped += 1

    print("")
    print(f"Admin username: {ADMIN_USERNAME}")
    print(f"Admin email: {ADMIN_EMAIL}")
    print(f"Admin password: {ADMIN_PASSWORD}")
    print(f"Problems created: {created}")
    print(f"Problems skipped: {skipped}")


if __name__ == "__main__":
    asyncio.run(main())
