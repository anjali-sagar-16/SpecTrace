"""Repository management endpoints for SpecTrace projects."""

import logging
from typing import List
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy import select
from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy.orm import Session

from app.api.deps import get_current_user
from app.db.session import get_db
from app.models.project import Project
from app.models.repository import Repository
from app.models.user import User
from app.schemas.repository import (
    RepositoryCreate,
    RepositoryMessageResponse,
    RepositoryResponse,
)

logger = logging.getLogger(__name__)

router = APIRouter()


def _get_verified_user_project(project_id: int, user_id: int, db: Session) -> Project:
    """Helper to verify project exists and is owned by the authenticated user."""
    project = db.scalar(
        select(Project).where(
            Project.id == project_id,
            Project.owner_id == user_id,
        )
    )
    if not project:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Project not found",
        )
    return project


@router.post(
    "",
    response_model=RepositoryResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Add repository to project",
    description="Registers a new code repository under an owned project.",
)
def create_repository(
    project_id: int,
    payload: RepositoryCreate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
) -> Repository:
    """Add a code repository to a project. Validates project ownership."""
    project = _get_verified_user_project(project_id, current_user.id, db)

    # project_id is strictly derived from the path, never accepted from request input
    repo = Repository(
        project_id=project.id,
        name=payload.name,
        full_name=payload.full_name,
        provider=payload.provider,
        external_id=payload.external_id,
        default_branch=payload.default_branch,
        html_url=payload.html_url,
    )

    try:
        db.add(repo)
        db.commit()
        db.refresh(repo)
        return repo
    except SQLAlchemyError as exc:
        db.rollback()
        logger.error(
            "Database error while creating repository for project %s: %s",
            project_id,
            exc,
        )
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="An error occurred while creating the repository.",
        )


@router.get(
    "",
    response_model=List[RepositoryResponse],
    status_code=status.HTTP_200_OK,
    summary="List project repositories",
    description="Lists all code repositories attached to the specified owned project.",
)
def list_repositories(
    project_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
) -> List[Repository]:
    """Retrieve all repositories attached to the project. Requires ownership."""
    _get_verified_user_project(project_id, current_user.id, db)

    repos = db.scalars(
        select(Repository)
        .where(Repository.project_id == project_id)
        .order_by(Repository.created_at.desc())
    ).all()
    return list(repos)


@router.get(
    "/{repository_id}",
    response_model=RepositoryResponse,
    status_code=status.HTTP_200_OK,
    summary="Get project repository details",
    description="Retrieves a single repository belonging to the specified owned project.",
)
def get_repository(
    project_id: int,
    repository_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
) -> Repository:
    """Fetch repository by ID, ensuring both project ownership and project-repo association."""
    _get_verified_user_project(project_id, current_user.id, db)

    repo = db.scalar(
        select(Repository).where(
            Repository.id == repository_id,
            Repository.project_id == project_id,
        )
    )
    if not repo:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Repository not found",
        )
    return repo


@router.delete(
    "/{repository_id}",
    response_model=RepositoryMessageResponse,
    status_code=status.HTTP_200_OK,
    summary="Remove repository from project",
    description="Deletes a repository record from the specified owned project.",
)
def delete_repository(
    project_id: int,
    repository_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
) -> RepositoryMessageResponse:
    """Delete repository record. Requires project ownership and correct association."""
    _get_verified_user_project(project_id, current_user.id, db)

    repo = db.scalar(
        select(Repository).where(
            Repository.id == repository_id,
            Repository.project_id == project_id,
        )
    )
    if not repo:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Repository not found",
        )

    try:
        db.delete(repo)
        db.commit()
        return RepositoryMessageResponse(message="Repository deleted successfully")
    except SQLAlchemyError as exc:
        db.rollback()
        logger.error(
            "Database error while deleting repository %s from project %s: %s",
            repository_id,
            project_id,
            exc,
        )
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="An error occurred while deleting the repository.",
        )
