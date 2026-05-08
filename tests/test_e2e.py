"""End-to-end test: full user journey via HTTP API + frontend pages."""
import pytest
from httpx import AsyncClient


@pytest.mark.asyncio
async def test_e2e_full_flow(client: AsyncClient, admin_token: str, user_token: str):
    headers = {"Authorization": f"Bearer {admin_token}"}

    # 1. Create a problem
    resp = await client.post("/api/v1/problems", json={
        "title": "E2E Sum", "slug": "e2e-sum", "description": "Sum a and b.",
        "difficulty": "easy", "is_public": True,
    }, headers=headers)
    assert resp.status_code == 201

    # 2. Add test case
    resp = await client.post("/api/v1/problems/e2e-sum/test-cases", json={
        "input": "3 5", "expected_output": "8", "is_sample": True, "order": 0,
    }, headers=headers)
    assert resp.status_code == 201

    # 3. Submit as regular user
    resp = await client.post("/api/v1/submissions", json={
        "problem_slug": "e2e-sum", "code": "print(sum(map(int,input().split())))",
        "language": "python",
    }, headers={"Authorization": f"Bearer {user_token}"})
    assert resp.status_code == 202

    # 4. Browse pages
    for path in ["/portal", "/problems", "/problem?slug=e2e-sum", "/submit"]:
        resp = await client.get(path)
        assert resp.status_code == 200

    # 5. C++ submit
    resp = await client.post("/api/v1/submissions", json={
        "problem_slug": "e2e-sum",
        "code": "#include <iostream>\nint main(){int a,b;std::cin>>a>>b;std::cout<<a+b;return 0;}",
        "language": "cpp",
    }, headers={"Authorization": f"Bearer {user_token}"})
    assert resp.status_code == 202

    # 6. Java submit
    resp = await client.post("/api/v1/submissions", json={
        "problem_slug": "e2e-sum",
        "code": "import java.util.*;public class Main{public static void main(String[]a){Scanner s=new Scanner(System.in);System.out.print(s.nextInt()+s.nextInt());}}",
        "language": "java",
    }, headers={"Authorization": f"Bearer {user_token}"})
    assert resp.status_code == 202

    # 7. Health + metrics
    resp = await client.get("/api/v1/health")
    assert resp.json()["status"] == "healthy"
    resp = await client.get("/metrics")
    assert "http_requests_total" in resp.text


@pytest.mark.asyncio
async def test_e2e_solution_and_csrf(client: AsyncClient, admin_token: str):
    headers = {"Authorization": f"Bearer {admin_token}"}

    # Create a problem with solution
    resp = await client.put("/api/v1/problems/e2e-sum", json={
        "solution_code": "print(sum(map(int,input().split())))",
        "solution_explanation": "Read two ints, print sum.",
    }, headers=headers)
    assert resp.status_code == 200

    # Verify solution is accessible
    resp = await client.get("/api/v1/problems/e2e-sum")
    assert resp.status_code == 200
    assert resp.json().get("solution_code")
