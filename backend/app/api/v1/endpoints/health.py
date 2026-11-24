from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy import text
from sqlalchemy.orm import Session
from app.core.config import settings
from app.db.session import get_db

router = APIRouter()


@router.get("/health", summary="Service Health Check")
def get_health():
    """Returns the operational status and metadata of the SpecTrace API service."""
    return {
        "status": "healthy",
        "service": settings.PROJECT_NAME,
        "version": settings.VERSION,
        "environment": settings.ENVIRONMENT,
    }


@router.get("/health/db", summary="Database Health Check")
def get_database_health(db: Session = Depends(get_db)):
    """Checks whether the PostgreSQL database is reachable and accepting queries."""
    try:
        # Lightweight connection verification query
        result = db.execute(text("SELECT 1")).scalar()
        if result == 1:
            return {
                "status": "healthy",
                "database": "connected",
                "engine": "PostgreSQL",
                "database_name": settings.POSTGRES_DB,
                "host": settings.POSTGRES_SERVER,
                "port": settings.POSTGRES_PORT,
                "pool": {
                    "pool_size": settings.DATABASE_POOL_SIZE,
                    "max_overflow": settings.DATABASE_MAX_OVERFLOW,
                },
            }
        raise ValueError("Unexpected query scalar response from PostgreSQL")
    except Exception as exc:
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail={
                "status": "unhealthy",
                "database": "disconnected",
                "error": str(exc),
            },
        )
