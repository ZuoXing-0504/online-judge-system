import pytest
from httpx import AsyncClient

from app.models.user import User


@pytest.mark.asyncio
async def test_create_problem_as_admin(client: AsyncClient, admin_token: str):
    response = await client.post(
        "/api/v1/problems",
        json={
            "title": "Two Sum",
            "slug": "two-sum",
            "description": "# Two Sum\nGiven an array...",
            "difficulty": "easy",
            "is_public": True,
        },
        headers={"Authorization": f"Bearer {admin_token}"},
    )
    assert response.status_code == 201
    data = response.json()
    assert data["title"] == "Two Sum"
    assert data["slug"] == "two-sum"
    assert data["difficulty"] == "easy"


@pytest.mark.asyncio
async def test_create_problem_as_user(client: AsyncClient, user_token: str):
    response = await client.post(
        "/api/v1/problems",
        json={
            "title": "Test Problem",
            "slug": "test-problem",
            "description": "Description",
        },
        headers={"Authorization": f"Bearer {user_token}"},
    )
    assert response.status_code == 403


@pytest.mark.asyncio
async def test_list_problems(client: AsyncClient, admin_token: str):
    # Create a public problem
    await client.post(
        "/api/v1/problems",
        json={
            "title": "Public Problem",
            "slug": "public-problem",
            "description": "A public problem",
            "is_public": True,
        },
        headers={"Authorization": f"Bearer {admin_token}"},
    )
    # Create a non-public problem
    await client.post(
        "/api/v1/problems",
        json={
            "title": "Private Problem",
            "slug": "private-problem",
            "description": "A private problem",
            "is_public": False,
        },
        headers={"Authorization": f"Bearer {admin_token}"},
    )

    response = await client.get("/api/v1/problems")
    assert response.status_code == 200
    data = response.json()
    assert data["total"] >= 1
    slugs = [p["slug"] for p in data["items"]]
    assert "public-problem" in slugs
    assert "private-problem" not in slugs


@pytest.mark.asyncio
async def test_get_problem_by_slug(client: AsyncClient, admin_token: str):
    await client.post(
        "/api/v1/problems",
        json={
            "title": "Get Problem",
            "slug": "get-problem",
            "description": "Description...",
            "is_public": True,
        },
        headers={"Authorization": f"Bearer {admin_token}"},
    )

    response = await client.get("/api/v1/problems/get-problem")
    assert response.status_code == 200
    data = response.json()
    assert data["slug"] == "get-problem"
    assert data["description"] == "Description..."


@pytest.mark.asyncio
async def test_get_nonexistent_problem(client: AsyncClient):
    response = await client.get("/api/v1/problems/nonexistent")
    assert response.status_code == 404


@pytest.mark.asyncio
async def test_problem_has_correct_response_fields(client: AsyncClient, admin_token: str):
    await client.post(
        "/api/v1/problems",
        json={
            "title": "Field Test",
            "slug": "field-test",
            "description": "Testing fields",
            "difficulty": "medium",
            "is_public": True,
            "sample_input": "1 2 3",
            "sample_output": "6",
        },
        headers={"Authorization": f"Bearer {admin_token}"},
    )

    response = await client.get("/api/v1/problems/field-test")
    assert response.status_code == 200
    data = response.json()
    assert "id" in data
    assert "created_by" in data
    assert "created_at" in data
    assert "updated_at" in data
    assert data["sample_input"] == "1 2 3"


@pytest.mark.asyncio
async def test_delete_problem(client: AsyncClient, admin_token: str):
    await client.post(
        "/api/v1/problems",
        json={
            "title": "To Delete",
            "slug": "to-delete",
            "description": "Will be deleted",
            "is_public": True,
        },
        headers={"Authorization": f"Bearer {admin_token}"},
    )

    response = await client.delete(
        "/api/v1/problems/to-delete",
        headers={"Authorization": f"Bearer {admin_token}"},
    )
    assert response.status_code == 204

    response = await client.get("/api/v1/problems/to-delete")
    assert response.status_code == 404


@pytest.mark.asyncio
async def test_cannot_update_test_case_through_wrong_problem_slug(client: AsyncClient, admin_token: str):
    await client.post(
        "/api/v1/problems",
        json={
            "title": "Primary Problem",
            "slug": "primary-problem",
            "description": "Owns the test case",
            "is_public": True,
        },
        headers={"Authorization": f"Bearer {admin_token}"},
    )
    await client.post(
        "/api/v1/problems",
        json={
            "title": "Secondary Problem",
            "slug": "secondary-problem",
            "description": "Should not reach the other test case",
            "is_public": True,
        },
        headers={"Authorization": f"Bearer {admin_token}"},
    )
    create_response = await client.post(
        "/api/v1/problems/primary-problem/test-cases",
        json={
            "input": "1 2",
            "expected_output": "3",
            "is_sample": True,
            "order": 0,
        },
        headers={"Authorization": f"Bearer {admin_token}"},
    )
    test_case_id = create_response.json()["id"]

    response = await client.put(
        f"/api/v1/problems/secondary-problem/test-cases/{test_case_id}",
        json={"expected_output": "999"},
        headers={"Authorization": f"Bearer {admin_token}"},
    )
    assert response.status_code == 404


@pytest.mark.asyncio
async def test_cannot_delete_test_case_through_wrong_problem_slug(client: AsyncClient, admin_token: str):
    await client.post(
        "/api/v1/problems",
        json={
            "title": "Delete Owner",
            "slug": "delete-owner",
            "description": "Owns the test case",
            "is_public": True,
        },
        headers={"Authorization": f"Bearer {admin_token}"},
    )
    await client.post(
        "/api/v1/problems",
        json={
            "title": "Delete Other",
            "slug": "delete-other",
            "description": "Wrong route target",
            "is_public": True,
        },
        headers={"Authorization": f"Bearer {admin_token}"},
    )
    create_response = await client.post(
        "/api/v1/problems/delete-owner/test-cases",
        json={
            "input": "5",
            "expected_output": "5",
            "is_sample": False,
            "order": 1,
        },
        headers={"Authorization": f"Bearer {admin_token}"},
    )
    test_case_id = create_response.json()["id"]

    response = await client.delete(
        f"/api/v1/problems/delete-other/test-cases/{test_case_id}",
        headers={"Authorization": f"Bearer {admin_token}"},
    )
    assert response.status_code == 404

    verify_response = await client.get(
        "/api/v1/problems/delete-owner/test-cases",
        headers={"Authorization": f"Bearer {admin_token}"},
    )
    assert verify_response.status_code == 200
    assert verify_response.json()["total"] == 1
