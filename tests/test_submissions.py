import pytest
from httpx import AsyncClient


@pytest.mark.asyncio
async def test_submit_code_to_problem(client: AsyncClient, admin_token: str, user_token: str):
    # Admin creates problem with test cases
    resp = await client.post(
        "/api/v1/problems",
        json={
            "title": "Sum",
            "slug": "sum",
            "description": "Add two numbers",
            "difficulty": "easy",
            "is_public": True,
        },
        headers={"Authorization": f"Bearer {admin_token}"},
    )
    assert resp.status_code == 201

    # Add a test case
    resp = await client.post(
        "/api/v1/problems/sum/test-cases",
        json={
            "input": "2\n3\n",
            "expected_output": "5\n",
            "order": 1,
        },
        headers={"Authorization": f"Bearer {admin_token}"},
    )
    assert resp.status_code == 201

    # User submits code
    response = await client.post(
        "/api/v1/submissions",
        json={
            "problem_slug": "sum",
            "code": "a = int(input())\nb = int(input())\nprint(a + b)",
            "language": "python",
        },
        headers={"Authorization": f"Bearer {user_token}"},
    )
    assert response.status_code == 202
    data = response.json()
    assert "id" in data
    assert data["status"] == "pending"


@pytest.mark.asyncio
async def test_submit_to_nonexistent_problem(client: AsyncClient, user_token: str):
    response = await client.post(
        "/api/v1/submissions",
        json={
            "problem_slug": "does-not-exist",
            "code": "print(1)",
        },
        headers={"Authorization": f"Bearer {user_token}"},
    )
    assert response.status_code == 404


@pytest.mark.asyncio
async def test_submit_without_auth(client: AsyncClient):
    response = await client.post(
        "/api/v1/submissions",
        json={
            "problem_slug": "anything",
            "code": "print(1)",
        },
    )
    assert response.status_code in (401, 403)


@pytest.mark.asyncio
async def test_list_submissions(client: AsyncClient, user_token: str):
    response = await client.get(
        "/api/v1/submissions",
        headers={"Authorization": f"Bearer {user_token}"},
    )
    assert response.status_code == 200
    data = response.json()
    assert "items" in data
    assert "total" in data
    assert "page" in data


@pytest.mark.asyncio
async def test_list_submissions_without_auth(client: AsyncClient):
    response = await client.get("/api/v1/submissions")
    assert response.status_code in (401, 403)


@pytest.mark.asyncio
async def test_get_nonexistent_submission(client: AsyncClient, user_token: str):
    response = await client.get(
        "/api/v1/submissions/00000000-0000-0000-0000-000000000000",
        headers={"Authorization": f"Bearer {user_token}"},
    )
    assert response.status_code == 404


@pytest.mark.asyncio
async def test_submit_rejects_unsupported_language(client: AsyncClient, admin_token: str, user_token: str):
    await client.post(
        "/api/v1/problems",
        json={
            "title": "Python Only",
            "slug": "python-only",
            "description": "Language boundary test",
            "difficulty": "easy",
            "is_public": True,
        },
        headers={"Authorization": f"Bearer {admin_token}"},
    )

    response = await client.post(
        "/api/v1/submissions",
        json={
            "problem_slug": "python-only",
            "code": "print(1)",
            "language": "ruby",
        },
        headers={"Authorization": f"Bearer {user_token}"},
    )
    assert response.status_code == 422
