import uuid

import pytest

from app.api.v1.submissions import submission_status_ws
from app.core.security import create_access_token, hash_password
from app.models.problem import Problem
from app.models.submission import Submission
from app.models.user import User


class FakeWebSocket:
    def __init__(self, token: str | None = None) -> None:
        self.query_params = {"token": token} if token else {}
        self.headers = {}
        self.cookies = {}
        self.accepted = False
        self.closed = False
        self.close_code: int | None = None
        self.close_reason: str | None = None
        self.sent_payloads: list[dict] = []

    async def accept(self) -> None:
        self.accepted = True

    async def close(self, code: int, reason: str | None = None) -> None:
        self.closed = True
        self.close_code = code
        self.close_reason = reason

    async def send_json(self, payload: dict) -> None:
        self.sent_payloads.append(payload)


@pytest.fixture
async def seeded_submission(db):
    suffix = uuid.uuid4().hex[:8]
    admin = User(
        username=f"ws_admin_{suffix}",
        email=f"ws_admin_{suffix}@example.com",
        hashed_password=hash_password("admin123"),
        role="admin",
    )
    owner = User(
        username=f"ws_owner_{suffix}",
        email=f"ws_owner_{suffix}@example.com",
        hashed_password=hash_password("owner123"),
    )
    other_user = User(
        username=f"ws_other_{suffix}",
        email=f"ws_other_{suffix}@example.com",
        hashed_password=hash_password("other123"),
    )
    db.add_all([admin, owner, other_user])
    await db.flush()

    problem = Problem(
        title="WebSocket Access Control",
        slug=f"ws-problem-{suffix}",
        description="Test submission ownership over WebSocket",
        is_public=True,
        created_by=admin.id,
    )
    db.add(problem)
    await db.flush()

    submission = Submission(
        user_id=owner.id,
        problem_id=problem.id,
        code="print(1)",
        language="python",
        status="accepted",
        total_test_cases=1,
        passed_test_cases=1,
    )
    db.add(submission)
    await db.commit()
    await db.refresh(submission)

    return {
        "submission_id": submission.id,
        "owner_token": create_access_token(data={"sub": str(owner.id)}),
        "other_token": create_access_token(data={"sub": str(other_user.id)}),
    }


@pytest.mark.asyncio
async def test_submission_websocket_requires_auth(db, seeded_submission):
    websocket = FakeWebSocket()

    await submission_status_ws(
        websocket,
        seeded_submission["submission_id"],
        db,
    )

    assert websocket.accepted is False
    assert websocket.close_code == 4401


@pytest.mark.asyncio
async def test_submission_websocket_rejects_other_user(db, seeded_submission):
    websocket = FakeWebSocket(token=seeded_submission["other_token"])

    await submission_status_ws(
        websocket,
        seeded_submission["submission_id"],
        db,
    )

    assert websocket.accepted is False
    assert websocket.close_code == 4403


@pytest.mark.asyncio
async def test_submission_websocket_allows_owner(db, seeded_submission):
    websocket = FakeWebSocket(token=seeded_submission["owner_token"])

    await submission_status_ws(
        websocket,
        seeded_submission["submission_id"],
        db,
    )

    assert websocket.accepted is True
    assert websocket.close_code is None
    assert len(websocket.sent_payloads) == 1
    assert str(websocket.sent_payloads[0]["id"]) == str(seeded_submission["submission_id"])
    assert websocket.sent_payloads[0]["code"] == "print(1)"
