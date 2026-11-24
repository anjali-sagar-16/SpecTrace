"""Pydantic schemas for Project CRUD operations and responses."""

from datetime import datetime
from typing import Optional
from pydantic import BaseModel, ConfigDict, Field, field_validator


class ProjectCreate(BaseModel):
    """Payload schema for creating a new project."""

    name: str = Field(
        ...,
        min_length=1,
        max_length=150,
        description="Project name (1 to 150 characters)",
        examples=["SpecTrace Core Engine"],
    )
    description: Optional[str] = Field(
        default=None,
        max_length=2000,
        description="Optional project description or notes",
        examples=["Main backend services and analyzer pipeline."],
    )

    model_config = ConfigDict(extra="forbid")

    @field_validator("name")
    @classmethod
    def validate_name_not_empty(cls, v: str) -> str:
        stripped = v.strip()
        if not stripped:
            raise ValueError("Project name cannot be empty or whitespace only")
        return stripped


class ProjectUpdate(BaseModel):
    """Payload schema for updating an existing project (partial update)."""

    name: Optional[str] = Field(
        default=None,
        min_length=1,
        max_length=150,
        description="Updated project name",
        examples=["SpecTrace Unified Engine"],
    )
    description: Optional[str] = Field(
        default=None,
        max_length=2000,
        description="Updated project description",
    )

    model_config = ConfigDict(extra="forbid")

    @field_validator("name")
    @classmethod
    def validate_name_if_provided(cls, v: Optional[str]) -> Optional[str]:
        if v is not None:
            stripped = v.strip()
            if not stripped:
                raise ValueError("Project name cannot be empty or whitespace only")
            return stripped
        return v


class ProjectResponse(BaseModel):
    """Response schema for project metadata and ownership."""

    id: int
    name: str
    description: Optional[str] = None
    owner_id: int
    created_at: datetime
    updated_at: datetime

    model_config = ConfigDict(from_attributes=True)


class ProjectMessageResponse(BaseModel):
    """Standard message response for operations like project deletion."""

    message: str
