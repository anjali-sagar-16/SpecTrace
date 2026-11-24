"""Pydantic schemas for Repository CRUD operations and responses."""

from datetime import datetime
from typing import Optional
from pydantic import BaseModel, ConfigDict, Field, field_validator


class RepositoryCreate(BaseModel):
    """Payload schema for adding a code repository to a project."""

    name: str = Field(
        ...,
        min_length=1,
        max_length=150,
        description="Short repository name",
        examples=["SpecTrace"],
    )
    full_name: str = Field(
        ...,
        min_length=1,
        max_length=255,
        description="Full repository namespace or slug",
        examples=["anjali-sagar-16/SpecTrace"],
    )
    provider: str = Field(
        default="github",
        min_length=1,
        max_length=50,
        description="Version control provider (e.g. github)",
        examples=["github"],
    )
    external_id: Optional[str] = Field(
        default=None,
        max_length=100,
        description="Provider's unique repository ID",
        examples=["891042145"],
    )
    default_branch: Optional[str] = Field(
        default="main",
        max_length=100,
        description="Default Git branch name",
        examples=["main"],
    )
    html_url: Optional[str] = Field(
        default=None,
        max_length=500,
        description="Public web URL of the repository",
        examples=["https://github.com/anjali-sagar-16/SpecTrace"],
    )

    model_config = ConfigDict(extra="forbid")

    @field_validator("name")
    @classmethod
    def validate_name_not_empty(cls, v: str) -> str:
        stripped = v.strip()
        if not stripped:
            raise ValueError("Repository name cannot be empty or whitespace only")
        return stripped

    @field_validator("full_name")
    @classmethod
    def validate_full_name_not_empty(cls, v: str) -> str:
        stripped = v.strip()
        if not stripped:
            raise ValueError("Repository full_name cannot be empty or whitespace only")
        return stripped

    @field_validator("provider")
    @classmethod
    def validate_provider_not_empty(cls, v: str) -> str:
        stripped = v.strip().lower()
        if not stripped:
            raise ValueError("Provider cannot be empty or whitespace only")
        return stripped


class RepositoryResponse(BaseModel):
    """Response schema for repository entity data."""

    id: int
    project_id: int
    name: str
    full_name: str
    provider: str
    external_id: Optional[str] = None
    default_branch: Optional[str] = None
    html_url: Optional[str] = None
    created_at: datetime
    updated_at: datetime

    model_config = ConfigDict(from_attributes=True)


class RepositoryMessageResponse(BaseModel):
    """Message response schema for repository operations."""

    message: str
