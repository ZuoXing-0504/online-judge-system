"""End-to-end test: full user journey via HTTP API + frontend pages."""
import pytest
from httpx import AsyncClient


@pytest.mark.asyncio
async def test_e2e_full_flow(client: AsyncClient):
    # 1. Register
    resp = await client.post("/api/v1/auth/register", json={
        "username": "e2e_user", "email": "e2e@test.com", "password": "password123",
    })
    assert resp.status_code in (201, 409)

    # 2. Login
    resp = await client.post("/api/v1/auth/login", json={
        "username": "e2e_user", "password": "password123",
    })
    assert resp.status_code == 200
    token = resp.json()["access_token"]
    headers = {"Authorization": f"Bearer {token}"}

    # 3. Home page
    resp = await client.get("/portal")
    assert resp.status_code == 200
    assert "Online Judge" in resp.text

    # 4. Problems list
    resp = await client.get("/problems")
    assert resp.status_code == 200
    assert "problem-list" in resp.text

    # 5. Problem detail (use a-plus-b which always exists)
    resp = await client.get("/problem?slug=a-plus-b")
    assert resp.status_code == 200
    assert "problem-title" in resp.text

    # 6. Submit page
    resp = await client.get("/submit")
    assert resp.status_code == 200
    assert "code-editor" in resp.text

    # 7. Submit Python code
    resp = await client.post("/api/v1/submissions", json={
        "problem_slug": "a-plus-b", "code": "print(sum(map(int,input().split())))",
        "language": "python",
    }, headers=headers)
    assert resp.status_code == 202
    sub_id = resp.json()["id"]
    assert sub_id

    # 8. Submissions list
    resp = await client.get("/submissions")
    assert resp.status_code == 200
    assert "submission-list" in resp.text

    # 9. Submissions page served
    resp = await client.get("/api/v1/submissions?page_size=5", headers=headers)
    assert resp.status_code == 200
    items = resp.json()["items"]
    assert len(items) >= 1
    assert items[0]["language"] in ("python", "cpp", "java")

    # 10. Contest list
    resp = await client.get("/contests-page")
    assert resp.status_code == 200
    assert "contest-list" in resp.text

    # 11. Contest detail
    resp = await client.get("/api/v1/contests")
    assert resp.status_code == 200
    contests = resp.json()["items"]
    if contests:
        slug = contests[0]["slug"]
        resp = await client.get(f"/api/v1/contests/{slug}")
        assert resp.status_code == 200
        data = resp.json()
        assert "title" in data
        assert "problems" in data

    # 12. Leaderboard
    if contests:
        slug = contests[0]["slug"]
        resp = await client.get(f"/api/v1/contests/{slug}/leaderboard")
        assert resp.status_code == 200

    # 13. Admin page (should redirect to auth for non-admin)
    resp = await client.get("/admin")
    assert resp.status_code == 200

    # 14. C++ submit
    resp = await client.post("/api/v1/submissions", json={
        "problem_slug": "a-plus-b",
        "code": "#include <iostream>\nint main(){int a,b;std::cin>>a>>b;std::cout<<a+b;return 0;}",
        "language": "cpp",
    }, headers=headers)
    assert resp.status_code == 202

    # 15. Java submit
    resp = await client.post("/api/v1/submissions", json={
        "problem_slug": "a-plus-b",
        "code": "import java.util.*;public class Main{public static void main(String[]a){Scanner s=new Scanner(System.in);System.out.print(s.nextInt()+s.nextInt());}}",
        "language": "java",
    }, headers=headers)
    assert resp.status_code == 202

    # 16. Health + metrics
    resp = await client.get("/api/v1/health")
    assert resp.json()["status"] == "healthy"

    resp = await client.get("/metrics")
    assert resp.status_code == 200
    assert "http_requests_total" in resp.text


@pytest.mark.asyncio
async def test_e2e_solution_and_csrf(client: AsyncClient):
    # Solution is accessible
    resp = await client.get("/api/v1/problems/a-plus-b")
    assert resp.status_code == 200
    assert resp.json().get("solution_code")

    # Unauthorized access returns 401
    resp = await client.get("/api/v1/admin/users")
    assert resp.status_code == 401

    # Invalid token rejected
    resp = await client.post("/api/v1/submissions", json={
        "problem_slug": "a-plus-b", "code": "print(1)", "language": "python",
    }, headers={"Authorization": "Bearer invalid_token"})
    assert resp.status_code == 401
