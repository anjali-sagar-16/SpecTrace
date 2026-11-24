"""Pydantic schemas for User authentication, login, and profile responses."""

import email_validator
from datetime import datetime
from pydantic import BaseModel, ConfigDict, EmailStr, Field, field_validator

# Disable network DNS deliverability checks to ensure fast, reliable syntax validation
email_validator.CHECK_DELIVERABILITY = False


class UserRegisterRequest(BaseModel):
    """Payload schema for user registration requests."""

    name: str = Field(
        ...,
        min_length=1,
        max_length=100,
        description="Full name of the user",
        examples=["Jane Doe"],
    )
    email: EmailStr = Field(
        ...,
        max_length=255,
        description="Valid email address for the user account",
        examples=["jane.doe@example.com"],
    )
    password: str = Field(
        ...,
        min_length=8,
        max_length=128,
        description="Plain-text password (must be at least 8 characters long)",
        examples=["SecurePassw0rd!2026"],
    )

    @field_validator("name")
    @classmethod
    def validate_name_not_empty(cls, v: str) -> str:
        stripped = v.strip()
        if not stripped:
            raise ValueError("Name cannot be empty or whitespace only")
        return stripped

    @field_validator("password")
    @classmethod
    def validate_password_min_length(cls, v: str) -> str:
        if len(v) < 8:
            raise ValueError("Password must be at least 8 characters long")
        return v


class UserLoginRequest(BaseModel):
    """Payload schema for user authentication / login requests."""

    email: EmailStr = Field(
        ...,
        max_length=255,
        description="User account email address",
        examples=["developer@spectrace.dev"],
    )
    password: str = Field(
        ...,
        min_length=1,
        description="User account password",
        examples=["SecurePassw0rd!2026"],
    )


class UserResponse(BaseModel):
    """Safe user profile response schema excluding sensitive credentials."""

    id: int
    name: str
    email: str
    created_at: datetime

    model_config = ConfigDict(from_attributes=True)


class TokenResponse(BaseModel):
    """Authentication response payload containing JWT access token and user metadata."""

    access_token: str
    token_type: str = "bearer"
    expires_in: int
    user: UserResponse
