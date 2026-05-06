from fastapi import APIRouter

from app.api.v1 import auth, users, problems, submissions, admin

api_router = APIRouter()
api_router.include_router(auth.router, prefix="/auth", tags=["Auth"])
api_router.include_router(users.router, prefix="/users", tags=["Users"])
api_router.include_router(problems.router, prefix="/problems", tags=["Problems"])
api_router.include_router(submissions.router, prefix="/submissions", tags=["Submissions"])
api_router.include_router(admin.router, prefix="/admin", tags=["Admin"])
