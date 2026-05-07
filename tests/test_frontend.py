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
        ("/", 'data-page="auth"'),
        ("/portal", 'data-page="home"'),
        ("/auth", 'data-page="auth"'),
        ("/register", 'data-page="register"'),
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
    assert 'src="/static/js/app.js"' in response.text


@pytest.mark.asyncio
async def test_static_assets_served(frontend_client: AsyncClient):
    app_response = await frontend_client.get("/static/js/app.js")
    api_response = await frontend_client.get("/static/js/api.js")
    state_response = await frontend_client.get("/static/js/state.js")

    assert app_response.status_code == 200
    assert "PROTECTED_PAGES" in app_response.text
    assert "redirectToAuth" in app_response.text
    assert 'import { initHomePage' in app_response.text

    assert api_response.status_code == 200
    assert 'credentials: "include"' in api_response.text

    assert state_response.status_code == 200
    assert "authMode" in state_response.text
    assert "hasBearerToken" in state_response.text


@pytest.mark.asyncio
async def test_legacy_frontend_entry_removed(frontend_client: AsyncClient):
    response = await frontend_client.get("/static/app.js")
    assert response.status_code == 404


@pytest.mark.asyncio
async def test_auth_entry_is_standalone(frontend_client: AsyncClient):
    response = await frontend_client.get("/")
    assert response.status_code == 200
    assert 'data-page="auth"' in response.text
    assert 'id="login-form"' in response.text
    assert 'id="open-register"' in response.text
    assert 'id="register-form"' not in response.text
    assert 'class="site-nav"' not in response.text


@pytest.mark.asyncio
async def test_register_page_is_separate(frontend_client: AsyncClient):
    response = await frontend_client.get("/register")
    assert response.status_code == 200
    assert 'data-page="register"' in response.text
    assert 'id="register-form"' in response.text
    assert 'id="close-register-window"' in response.text
    assert 'class="site-nav"' not in response.text


@pytest.mark.asyncio
async def test_user_portal_excludes_admin_nav(frontend_client: AsyncClient):
    response = await frontend_client.get("/portal")
    assert response.status_code == 200
    assert 'data-page="home"' in response.text
    assert 'data-nav="admin"' not in response.text
    assert 'id="admin-entry"' in response.text


@pytest.mark.asyncio
async def test_admin_console_has_separate_navigation(frontend_client: AsyncClient):
    response = await frontend_client.get("/admin")
    assert response.status_code == 200
    assert 'data-page="admin"' in response.text
    assert 'href="#problem-management"' in response.text
    assert 'href="#user-management"' in response.text
    assert 'href="/portal"' in response.text


@pytest.mark.asyncio
async def test_favicon_route_redirects(frontend_client: AsyncClient):
    response = await frontend_client.get("/favicon.ico", follow_redirects=False)
    assert response.status_code in (302, 307)
