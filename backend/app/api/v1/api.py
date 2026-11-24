from fastapi import APIRouter
from app.api.v1.endpoints import auth, health, projects, repositories

api_router = APIRouter()
api_router.include_router(health.router, tags=["Health"])
api_router.include_router(auth.router, prefix="/auth", tags=["Authentication"])
api_router.include_router(projects.router, prefix="/projects", tags=["Projects"])
api_router.include_router(
    repositories.router,
    prefix="/projects/{project_id}/repositories",
    tags=["Repositories"],
)
