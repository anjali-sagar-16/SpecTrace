"""Project management CRUD endpoints for SpecTrace."""

import logging
from typing import List
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy import select
from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy.orm import Session

from app.api.deps import get_current_user
from app.db.session import get_db
from app.models.project import Project
from app.models.user import User
from app.schemas.project import (
    ProjectCreate,
    ProjectMessageResponse,
    ProjectResponse,
    ProjectUpdate,
)

logger = logging.getLogger(__name__)

router = APIRouter()


@router.post(
    "",
    response_model=ProjectResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Create a new project",
    description="Creates a new project owned exclusively by the authenticated user.",
)
def create_project(
    payload: ProjectCreate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
) -> Project:
    """Create a new project entity with ownership bound to the active session user."""
    # owner_id is strictly derived from the authenticated session, never from client input
    project = Project(
        name=payload.name,
        description=payload.description,
        owner_id=current_user.id,
    )

    try:
        db.add(project)
        db.commit()
        db.refresh(project)
        return project
    except SQLAlchemyError as exc:
        db.rollback()
        logger.error("Database error while creating project for user %s: %s", current_user.id, exc)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="An error occurred while creating the project.",
        )


@router.get(
    "",
    response_model=List[ProjectResponse],
    status_code=status.HTTP_200_OK,
    summary="List user projects",
    description="Returns all projects owned by the currently authenticated user.",
)
def list_projects(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
) -> List[Project]:
    """Retrieve all projects belonging exclusively to the authenticated user."""
    projects = db.scalars(
        select(Project)
        .where(Project.owner_id == current_user.id)
        .order_by(Project.created_at.desc())
    ).all()
    return list(projects)


@router.get(
    "/{project_id}",
    response_model=ProjectResponse,
    status_code=status.HTTP_200_OK,
    summary="Get project details",
    description="Retrieves a specific project owned by the authenticated user.",
)
def get_project(
    project_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
) -> Project:
    """Retrieve an individual project if owned by the authenticated user, or 404."""
    project = db.scalar(
        select(Project).where(
            Project.id == project_id,
            Project.owner_id == current_user.id,
        )
    )
    if not project:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Project not found",
        )
    return project


@router.patch(
    "/{project_id}",
    response_model=ProjectResponse,
    status_code=status.HTTP_200_OK,
    summary="Update project",
    description="Updates name or description of a project owned by the authenticated user.",
)
def update_project(
    project_id: int,
    payload: ProjectUpdate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
) -> Project:
    """Update name or description of an owned project. Rejects owner_id mutation."""
    project = db.scalar(
        select(Project).where(
            Project.id == project_id,
            Project.owner_id == current_user.id,
        )
    )
    if not project:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Project not found",
        )

    # Apply partial updates
    if payload.name is not None:
        project.name = payload.name
    if payload.description is not None:
        project.description = payload.description

    try:
        db.commit()
        db.refresh(project)
        return project
    except SQLAlchemyError as exc:
        db.rollback()
        logger.error("Database error while updating project %s: %s", project_id, exc)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="An error occurred while updating the project.",
        )


@router.delete(
    "/{project_id}",
    response_model=ProjectMessageResponse,
    status_code=status.HTTP_200_OK,
    summary="Delete project",
    description="Deletes an owned project and cascades to attached repositories.",
)
def delete_project(
    project_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
) -> ProjectMessageResponse:
    """Delete an individual project if owned by the active user, or 404."""
    project = db.scalar(
        select(Project).where(
            Project.id == project_id,
            Project.owner_id == current_user.id,
        )
    )
    if not project:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Project not found",
        )

    try:
        db.delete(project)
        db.commit()
        return ProjectMessageResponse(message="Project deleted successfully")
    except SQLAlchemyError as exc:
        db.rollback()
        logger.error("Database error while deleting project %s: %s", project_id, exc)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="An error occurred while deleting the project.",
        )
