import pytest
import pytest_asyncio
from httpx import ASGITransport
from httpx import AsyncClient

from app.main import app


@pytest_asyncio.fixture
async def frontend_client():
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as client:
        yield client


@pytest.mark.asyncio
@pytest.mark.parametrize(
    ("route", "marker"),
    [
        ("/", 'data-page="home"'),
        ("/auth", 'data-page="auth"'),
        ("/problems", 'data-page="problems"'),
        ("/problem", 'data-page="problem-detail"'),
        ("/submit", 'data-page="submit"'),
        ("/submissions", 'data-page="submissions"'),
        ("/admin", 'data-page="admin"'),
    ],
)
async def test_frontend_pages_served(frontend_client: AsyncClient, route: str, marker: str):
    response = await frontend_client.get(route)
    assert response.status_code == 200
    assert "text/html" in response.headers["content-type"]
    assert 'id="language-select"' in response.text
    assert marker in response.text


@pytest.mark.asyncio
async def test_static_assets_served(frontend_client: AsyncClient):
    response = await frontend_client.get("/static/app.js")
    assert response.status_code == 200
    assert "SUPPORTED_LANGUAGES" in response.text


@pytest.mark.asyncio
async def test_favicon_route_redirects(frontend_client: AsyncClient):
    response = await frontend_client.get("/favicon.ico", follow_redirects=False)
    assert response.status_code in (302, 307)
