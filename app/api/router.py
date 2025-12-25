from fastapi import APIRouter

from app.api.routers.auth import router as auth_router
from app.api.routers.projects import router as projects_router
from app.api.routers.tasks import router as tasks_router
from app.api.routers.admin import router as admin_router

api_router = APIRouter()
api_router.include_router(auth_router, prefix="/auth", tags=["auth"])
api_router.include_router(projects_router, prefix="/projects", tags=["projects"])
api_router.include_router(tasks_router, tags=["tasks"])
api_router.include_router(admin_router, prefix="/admin", tags=["admin"])
