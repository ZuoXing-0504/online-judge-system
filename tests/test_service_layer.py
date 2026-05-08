from types import SimpleNamespace

import pytest
from sqlalchemy import select

from app.core.exceptions import ConflictException, ForbiddenException, NotFoundException, UnauthorizedException
from app.core.security import hash_password, verify_password
from app.models.problem import Problem
from app.models.submission import Submission
from app.models.submission_test_result import SubmissionTestResult
from app.models.test_case import TestCase as TestCaseModel
from app.models.user import User
from app.schemas.auth import RegisterRequest
from app.schemas.problem import ProblemCreate, ProblemUpdate
from app.schemas.test_case import TestCaseCreate as TestCaseCreateSchema, TestCaseUpdate as TestCaseUpdateSchema
from app.schemas.user import UserUpdate
from app.services import auth_service, judge_service, problem_service, submission_service, user_service


async def _create_user(
    db,
    *,
    username: str,
    email: str,
    password: str = "password123",
    role: str = "user",
    is_active: bool = True,
) -> User:
    user = User(
        username=username,
        email=email,
        hashed_password=hash_password(password),
        role=role,
        is_active=is_active,
    )
    db.add(user)
    await db.commit()
    await db.refresh(user)
    return user


async def _create_problem(
    db,
    *,
    author_id,
    title: str = "Sample Problem",
    slug: str = "sample-problem",
    is_public: bool = True,
    difficulty: str = "easy",
) -> Problem:
    problem = Problem(
        title=title,
        slug=slug,
        description="Problem description",
        difficulty=difficulty,
        is_public=is_public,
        created_by=author_id,
    )
    db.add(problem)
    await db.commit()
    await db.refresh(problem)
    return problem


async def _create_test_case(
    db,
    *,
    problem_id,
    input_data: str = "1\n",
    expected_output: str = "1\n",
    is_sample: bool = True,
    order: int = 0,
) -> TestCaseModel:
    test_case = TestCaseModel(
        problem_id=problem_id,
        input=input_data,
        expected_output=expected_output,
        is_sample=is_sample,
        order=order,
    )
    db.add(test_case)
    await db.commit()
    await db.refresh(test_case)
    return test_case


async def _create_submission(
    db,
    *,
    user_id,
    problem_id,
    code: str = "print(1)",
    status: str = "pending",
) -> Submission:
    submission = Submission(
        user_id=user_id,
        problem_id=problem_id,
        code=code,
        language="python",
        status=status,
    )
    db.add(submission)
    await db.commit()
    await db.refresh(submission)
    return submission


@pytest.mark.asyncio
async def test_auth_service_register_and_authenticate(db):
    created = await auth_service.register(
        db,
        RegisterRequest(
            username="service-user",
            email="service@example.com",
            password="password123",
        ),
    )
    assert created.username == "service-user"
    assert verify_password("password123", created.hashed_password)

    login = await auth_service.authenticate(db, "service-user", "password123")
    assert login.user.username == "service-user"
    assert login.access_token


@pytest.mark.asyncio
async def test_auth_service_rejects_duplicate_and_invalid_login(db):
    existing = await _create_user(
        db,
        username="dupe-user",
        email="dupe@example.com",
    )

    with pytest.raises(ConflictException):
        await auth_service.register(
            db,
            RegisterRequest(
                username="dupe-user",
                email="other@example.com",
                password="password123",
            ),
        )

    with pytest.raises(ConflictException):
        await auth_service.register(
            db,
            RegisterRequest(
                username="other-user",
                email="dupe@example.com",
                password="password123",
            ),
        )

    with pytest.raises(UnauthorizedException):
        await auth_service.authenticate(db, existing.username, "wrong-password")

    inactive = await _create_user(
        db,
        username="inactive-user",
        email="inactive@example.com",
        is_active=False,
    )
    with pytest.raises(UnauthorizedException):
        await auth_service.authenticate(db, inactive.username, "password123")


@pytest.mark.asyncio
async def test_user_service_profile_listing_and_role_changes(db):
    primary = await _create_user(
        db,
        username="primary-user",
        email="primary@example.com",
    )
    other = await _create_user(
        db,
        username="other-user",
        email="other@example.com",
    )
    admin = await _create_user(
        db,
        username="admin-user",
        email="admin@example.com",
        role="admin",
    )

    fetched = await user_service.get_by_id(db, str(primary.id))
    assert fetched.id == primary.id

    with pytest.raises(NotFoundException):
        await user_service.get_by_id(db, "00000000-0000-0000-0000-000000000000")

    updated = await user_service.update_profile(
        db,
        primary,
        UserUpdate(username="renamed-user", email="renamed@example.com"),
    )
    assert updated.username == "renamed-user"
    assert updated.email == "renamed@example.com"

    with pytest.raises(ConflictException):
        await user_service.update_profile(db, updated, UserUpdate(username=other.username))

    with pytest.raises(ConflictException):
        await user_service.update_profile(db, updated, UserUpdate(email=other.email))

    admins, total_admins = await user_service.list_users(db, role="admin")
    assert total_admins == 1
    assert [user.username for user in admins] == [admin.username]

    changed = await user_service.change_role(db, str(other.id), "admin", commit=False)
    assert changed.role == "admin"
    await db.rollback()
    await db.refresh(other)
    assert other.role == "user"

    changed = await user_service.change_role(db, str(other.id), "admin")
    assert changed.role == "admin"


@pytest.mark.asyncio
async def test_problem_service_crud_and_test_case_flow(db):
    admin = await _create_user(
        db,
        username="problem-admin",
        email="problem-admin@example.com",
        role="admin",
    )

    payload = ProblemCreate(
        title="Service Problem",
        slug="service-problem",
        description="Service problem description",
        difficulty="medium",
        is_public=True,
    )
    created = await problem_service.create_problem(db, payload, admin.id)
    assert created.slug == "service-problem"

    with pytest.raises(ConflictException):
        await problem_service.create_problem(db, payload, admin.id)

    fetched = await problem_service.get_by_slug(db, "service-problem")
    assert fetched.id == created.id

    public_items, public_total = await problem_service.list_problems(
        db,
        difficulty="medium",
        search="Service",
    )
    assert public_total == 1
    assert public_items[0].slug == "service-problem"

    await problem_service.update_problem(
        db,
        "service-problem",
        ProblemUpdate(title="Updated Service Problem", is_public=False),
    )
    updated = await problem_service.get_by_slug(db, "service-problem")
    assert updated.title == "Updated Service Problem"
    assert updated.is_public is False

    admin_items, admin_total = await problem_service.list_problems(db, is_admin=True)
    assert admin_total == 1
    assert admin_items[0].slug == "service-problem"

    test_case = await problem_service.create_test_case(
        db,
        "service-problem",
        TestCaseCreateSchema(
            input="1 2\n",
            expected_output="3\n",
            is_sample=True,
            order=2,
        ),
    )
    assert test_case.order == 2

    fetched_case = await problem_service.get_test_case(db, test_case.id)
    assert fetched_case.id == test_case.id

    listed_cases, total_cases = await problem_service.list_test_cases(db, "service-problem")
    assert total_cases == 1
    assert listed_cases[0].id == test_case.id

    updated_case = await problem_service.update_test_case(
        db,
        "service-problem",
        test_case.id,
        TestCaseUpdateSchema(expected_output="4\n", order=1, is_sample=False),
    )
    assert updated_case.expected_output == "4\n"
    assert updated_case.order == 1
    assert updated_case.is_sample is False

    wrong_problem = await _create_problem(
        db,
        author_id=admin.id,
        title="Other Problem",
        slug="other-problem",
        is_public=True,
    )
    assert wrong_problem.slug == "other-problem"

    with pytest.raises(NotFoundException):
        await problem_service.get_test_case_for_problem(db, "other-problem", test_case.id)

    await problem_service.delete_test_case(db, "service-problem", test_case.id)
    with pytest.raises(NotFoundException):
        await problem_service.get_test_case(db, test_case.id)

    await problem_service.delete_problem(db, "service-problem")
    with pytest.raises(NotFoundException):
        await problem_service.get_by_slug(db, "service-problem")

    deleted_problem = await problem_service._get_by_slug(db, "service-problem", include_deleted=True)
    assert deleted_problem is not None
    assert deleted_problem.deleted_at is not None
    assert deleted_problem.is_public is False


@pytest.mark.asyncio
async def test_submission_service_queries_and_permissions(db):
    admin = await _create_user(
        db,
        username="submission-admin",
        email="submission-admin@example.com",
        role="admin",
    )
    owner = await _create_user(
        db,
        username="submission-owner",
        email="submission-owner@example.com",
    )
    other = await _create_user(
        db,
        username="submission-other",
        email="submission-other@example.com",
    )
    public_problem = await _create_problem(
        db,
        author_id=admin.id,
        title="Public Problem",
        slug="public-problem-service",
        is_public=True,
    )
    private_problem = await _create_problem(
        db,
        author_id=admin.id,
        title="Private Problem",
        slug="private-problem-service",
        is_public=False,
    )

    created = await submission_service.create_submission(
        db,
        owner,
        public_problem.slug,
        "print(1)",
    )
    assert created.user_id == owner.id

    with pytest.raises(NotFoundException):
        await submission_service.create_submission(db, owner, "missing-problem", "print(1)")

    with pytest.raises(NotFoundException):
        await submission_service.create_submission(db, owner, private_problem.slug, "print(1)")

    admin_submission = await submission_service.create_submission(
        db,
        admin,
        private_problem.slug,
        "print(2)",
    )
    assert admin_submission.problem_id == private_problem.id

    owned = await submission_service.get_submission(db, created.id, owner)
    assert owned.id == created.id

    with pytest.raises(ForbiddenException):
        await submission_service.get_submission(db, created.id, other)

    with pytest.raises(NotFoundException):
        await submission_service.get_submission(
            db,
            admin_submission.id.__class__("00000000-0000-0000-0000-000000000000"),
            admin,
        )

    raw = await submission_service.get_submission_raw(db, created.id)
    assert raw is not None
    assert await submission_service.get_submission_raw(
        db,
        created.id.__class__("00000000-0000-0000-0000-000000000000"),
    ) is None

    created.status = "accepted"
    admin_submission.status = "runtime_error"
    await db.commit()

    owner_items, owner_total = await submission_service.list_submissions(db, owner)
    assert owner_total == 1
    assert owner_items[0].id == created.id

    admin_items, admin_total = await submission_service.list_submissions(
        db,
        admin,
        problem_slug=private_problem.slug,
        status="runtime_error",
        is_admin=True,
    )
    assert admin_total == 1
    assert admin_items[0].id == admin_submission.id


@pytest.mark.asyncio
async def test_judge_service_happy_path_and_error_recovery(db, monkeypatch):
    admin = await _create_user(
        db,
        username="judge-admin",
        email="judge-admin@example.com",
        role="admin",
    )
    owner = await _create_user(
        db,
        username="judge-owner",
        email="judge-owner@example.com",
    )
    problem = await _create_problem(
        db,
        author_id=admin.id,
        title="Judge Problem",
        slug="judge-problem",
        is_public=True,
    )
    submission = await _create_submission(
        db,
        user_id=owner.id,
        problem_id=problem.id,
        code="print(1)",
        status="pending",
    )
    await _create_test_case(
        db,
        problem_id=problem.id,
        input_data="1\n",
        expected_output="1\n",
        is_sample=True,
        order=0,
    )
    await _create_test_case(
        db,
        problem_id=problem.id,
        input_data="2\n",
        expected_output="3\n",
        is_sample=False,
        order=1,
    )

    results = iter(
        [
            SimpleNamespace(
                status="accepted",
                execution_time_ms=12.5,
                memory_used_kb=64.0,
                output="1\n",
                expected_output="1\n",
                error_message="",
            ),
            SimpleNamespace(
                status="wrong_answer",
                execution_time_ms=24.0,
                memory_used_kb=96.0,
                output="2\n",
                expected_output="3\n",
                error_message="mismatch",
            ),
        ]
    )

    async def fake_execute_test_case(**_kwargs):
        return next(results)

    monkeypatch.setattr(judge_service, "execute_test_case", fake_execute_test_case)
    await judge_service._do_judge(db, submission.id)

    judged = await db.get(Submission, submission.id)
    assert judged.status == "wrong_answer"
    assert judged.total_test_cases == 2
    assert judged.passed_test_cases == 1
    assert judged.max_execution_time_ms == 24.0
    assert judged.max_memory_used_kb == 96.0
    assert judged.error_message == "mismatch"

    stored_results = (
        await db.execute(
            select(SubmissionTestResult)
            .where(SubmissionTestResult.submission_id == submission.id)
            .order_by(SubmissionTestResult.execution_time_ms)
        )
    ).scalars().all()
    assert len(stored_results) == 2
    assert stored_results[0].expected_output == "1\n"
    assert stored_results[1].expected_output is None

    no_case_problem = await _create_problem(
        db,
        author_id=admin.id,
        title="No Case Problem",
        slug="no-case-problem",
        is_public=True,
    )
    empty_submission = await _create_submission(
        db,
        user_id=owner.id,
        problem_id=no_case_problem.id,
        code="print(1)",
        status="pending",
    )

    await judge_service._do_judge(db, empty_submission.id)
    empty_judged = await db.get(Submission, empty_submission.id)
    assert empty_judged.status == "accepted"

    running_submission = await _create_submission(
        db,
        user_id=owner.id,
        problem_id=problem.id,
        code="print(1)",
        status="running",
    )

    async def explode(_db, _submission_id):
        raise RuntimeError("judge exploded")

    monkeypatch.setattr(judge_service, "_do_judge", explode)
    await judge_service.judge_submission(db, running_submission.id)

    recovered = await db.get(Submission, running_submission.id)
    assert recovered.status == "error"
    assert "RuntimeError: judge exploded" in recovered.error_message
