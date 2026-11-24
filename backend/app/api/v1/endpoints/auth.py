"""Authentication and user account endpoints for SpecTrace."""

import logging
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy import select
from sqlalchemy.exc import IntegrityError, SQLAlchemyError
from sqlalchemy.orm import Session

from app.api.deps import get_current_user
from app.core.config import settings
from app.core.security import create_access_token, hash_password, verify_password
from app.db.session import get_db
from app.models.user import User
from app.schemas.user import (
    TokenResponse,
    UserLoginRequest,
    UserRegisterRequest,
    UserResponse,
)

logger = logging.getLogger(__name__)

router = APIRouter()

GENERIC_AUTH_ERROR_DETAIL = "Invalid email or password"


@router.post(
    "/register",
    response_model=UserResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Register a new user",
    description="Registers a new user in SpecTrace with securely hashed credentials.",
)
def register_user(
    payload: UserRegisterRequest,
    db: Session = Depends(get_db),
) -> User:
    """Create a new user account with validated input and Argon2 hashed password."""
    normalized_email = payload.email.strip().lower()

    # Check whether the email already exists
    existing_user = db.scalar(select(User).where(User.email == normalized_email))
    if existing_user:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="A user with this email address already exists.",
        )

    # Securely hash the plain-text password using Argon2
    hashed_password = hash_password(payload.password)

    # Instantiate the new user entity
    new_user = User(
        name=payload.name.strip(),
        email=normalized_email,
        hashed_password=hashed_password,
    )

    try:
        db.add(new_user)
        db.commit()
        db.refresh(new_user)
        return new_user
    except IntegrityError as exc:
        db.rollback()
        logger.warning("Integrity error during user registration for %s: %s", normalized_email, exc)
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="A user with this email address already exists.",
        )
    except SQLAlchemyError as exc:
        db.rollback()
        logger.error("Database error occurred during user registration: %s", exc)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="An unexpected database error occurred. Please try again later.",
        )


@router.post(
    "/login",
    response_model=TokenResponse,
    status_code=status.HTTP_200_OK,
    summary="User Login",
    description="Authenticates user credentials and issues a signed JWT access token.",
)
def login_user(
    payload: UserLoginRequest,
    db: Session = Depends(get_db),
) -> TokenResponse:
    """Authenticate user with email and password, returning a signed JWT access token."""
    normalized_email = payload.email.strip().lower()

    # Find the user by normalized email
    user = db.scalar(select(User).where(User.email == normalized_email))
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail=GENERIC_AUTH_ERROR_DETAIL,
            headers={"WWW-Authenticate": "Bearer"},
        )

    # Verify the supplied password using Argon2
    if not verify_password(payload.password, user.hashed_password):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail=GENERIC_AUTH_ERROR_DETAIL,
            headers={"WWW-Authenticate": "Bearer"},
        )

    # Generate signed JWT access token
    access_token = create_access_token(subject=user.id)
    expires_in_seconds = settings.ACCESS_TOKEN_EXPIRE_MINUTES * 60

    return TokenResponse(
        access_token=access_token,
        token_type="bearer",
        expires_in=expires_in_seconds,
        user=UserResponse.model_validate(user),
    )


@router.get(
    "/me",
    response_model=UserResponse,
    status_code=status.HTTP_200_OK,
    summary="Get Current User Profile",
    description="Returns the profile information of the currently authenticated user.",
)
def get_me(
    current_user: User = Depends(get_current_user),
) -> User:
    """Return the currently authenticated user's profile information."""
    return current_user
