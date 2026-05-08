import secrets

from starlette.middleware.base import BaseHTTPMiddleware
from starlette.responses import Response
from fastapi import Request

CSRF_COOKIE = "csrf_token"
CSRF_HEADER = "X-CSRF-Token"
CSRF_SAFE_METHODS = {"GET", "HEAD", "OPTIONS"}
CSRF_EXEMPT_PATHS = {"/api/v1/auth/login", "/api/v1/auth/register", "/api/v1/auth/logout", "/api/v1/health", "/metrics"}

def _is_csrf_exempt(path: str) -> bool:
    if path in CSRF_EXEMPT_PATHS:
        return True
    # Also exempt quick-run endpoints (read-only test)
    if path.startswith("/api/v1/problems/") and path.endswith("/run"):
        return True
    return False


class CSRFMiddleware(BaseHTTPMiddleware):
    async def dispatch(self, request: Request, call_next):
        cookie_token = request.cookies.get(CSRF_COOKIE)

        if request.method not in CSRF_SAFE_METHODS and not _is_csrf_exempt(request.url.path):
            # Skip CSRF check if Authorization header is present (Bearer tokens are CSRF-safe)
            if not request.headers.get("Authorization"):
                header_token = request.headers.get(CSRF_HEADER)
                if not cookie_token or not header_token or not secrets.compare_digest(cookie_token, header_token):
                    return Response("CSRF token mismatch", status_code=403)

        response = await call_next(request)

        if not cookie_token:
            cookie_token = secrets.token_hex(32)
            response.set_cookie(CSRF_COOKIE, cookie_token, httponly=False, samesite="lax", max_age=86400)

        return response
