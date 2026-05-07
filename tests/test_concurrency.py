import asyncio

import pytest
from httpx import AsyncClient


async def _create_public_problem(client: AsyncClient, admin_token: str, slug: str) -> None:
    response = await client.post(
        "/api/v1/problems",
        json={
            "title": f"Problem {slug}",
            "slug": slug,
            "description": "Problem used for integration tests.",
            "is_public": True,
        },
        headers={"Authorization": f"Bearer {admin_token}"},
    )
    assert response.status_code == 201


async def _add_test_case(client: AsyncClient, admin_token: str, slug: str) -> None:
    response = await client.post(
        f"/api/v1/problems/{slug}/test-cases",
        json={
            "input": "1\n",
            "expected_output": "1\n",
            "is_sample": True,
            "order": 0,
        },
        headers={"Authorization": f"Bearer {admin_token}"},
    )
    assert response.status_code == 201


@pytest.mark.asyncio
async def test_concurrent_submissions(client: AsyncClient, admin_token: str, user_token: str):
    await _create_public_problem(client, admin_token, "concurrency-test")
    await _add_test_case(client, admin_token, "concurrency-test")

    async def submit_one():
        return await client.post(
            "/api/v1/submissions",
            json={
                "problem_slug": "concurrency-test",
                "code": "print(int(input()))",
                "language": "python",
            },
            headers={"Authorization": f"Bearer {user_token}"},
        )

    results = await asyncio.gather(*[submit_one() for _ in range(10)])
    for result in results:
        assert result.status_code == 202


@pytest.mark.asyncio
async def test_large_code_rejected(client: AsyncClient, admin_token: str, user_token: str):
    await _create_public_problem(client, admin_token, "boundary-test")

    large_but_valid_code = "print('ok')\n" * 5000
    response = await client.post(
        "/api/v1/submissions",
        json={
            "problem_slug": "boundary-test",
            "code": large_but_valid_code,
            "language": "python",
        },
        headers={"Authorization": f"Bearer {user_token}"},
    )
    assert response.status_code == 202


@pytest.mark.asyncio
async def test_unauthorized_access(client: AsyncClient):
    response = await client.get("/api/v1/admin/users")
    assert response.status_code == 401

    response = await client.patch(
        "/api/v1/admin/users/00000000-0000-0000-0000-000000000000/role?role=admin"
    )
    assert response.status_code == 401


@pytest.mark.asyncio
async def test_user_cannot_access_others_submission(
    client: AsyncClient,
    admin_token: str,
    user_token: str,
):
    await _create_public_problem(client, admin_token, "access-control-test")

    submit_response = await client.post(
        "/api/v1/submissions",
        json={
            "problem_slug": "access-control-test",
            "code": "print('test')",
            "language": "python",
        },
        headers={"Authorization": f"Bearer {user_token}"},
    )
    assert submit_response.status_code == 202
    submission_id = submit_response.json()["id"]

    register_response = await client.post(
        "/api/v1/auth/register",
        json={
            "username": "user_b_submission",
            "email": "userb_sub@test.com",
            "password": "test_password_123",
        },
    )
    assert register_response.status_code == 201

    login_response = await client.post(
        "/api/v1/auth/login",
        json={
            "username": "user_b_submission",
            "password": "test_password_123",
        },
    )
    assert login_response.status_code == 200
    other_token = login_response.json()["access_token"]

    response = await client.get(
        f"/api/v1/submissions/{submission_id}",
        headers={"Authorization": f"Bearer {other_token}"},
    )
    assert response.status_code == 403
