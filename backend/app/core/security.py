"""Security, password hashing, and JWT utilities for SpecTrace.

Implements secure password hashing via Argon2 (pwdlib) and JSON Web Token (JWT)
generation and validation via PyJWT.
"""

from datetime import datetime, timedelta, timezone
from typing import Any, Dict, Optional, Union
import jwt
from jwt.exceptions import ExpiredSignatureError, InvalidTokenError, PyJWTError
from pwdlib import PasswordHash
from pwdlib.exceptions import HashVerificationError, UnknownHashError
from pwdlib.hashers.argon2 import Argon2Hasher

from app.core.config import settings

# Initialize PasswordHash configured with Argon2Hasher
password_hash: PasswordHash = PasswordHash((Argon2Hasher(),))


def hash_password(password: str) -> str:
    """Hash a plain-text password using the Argon2 algorithm.

    Args:
        password: The plain-text password to hash.

    Returns:
        The Argon2-hashed password string.

    Raises:
        ValueError: If the password is empty, whitespace-only, or not a string.
    """
    if not isinstance(password, str) or not password.strip():
        raise ValueError("Password cannot be empty")
    return password_hash.hash(password)


def verify_password(plain_password: str, hashed_password: str) -> bool:
    """Verify a plain-text password against a hashed password.

    Args:
        plain_password: The plain-text password to verify.
        hashed_password: The stored hashed password string.

    Returns:
        True if the password matches the hash, False otherwise.
    """
    if not plain_password or not hashed_password:
        return False
    if not isinstance(plain_password, str) or not isinstance(hashed_password, str):
        return False

    try:
        return password_hash.verify(plain_password, hashed_password)
    except (UnknownHashError, HashVerificationError):
        return False


def create_access_token(
    subject: Union[str, int],
    expires_delta: Optional[timedelta] = None,
    extra_claims: Optional[Dict[str, Any]] = None,
) -> str:
    """Create a signed JWT access token containing the user ID as subject.

    Args:
        subject: The unique user identifier to store in the 'sub' claim.
        expires_delta: Optional custom token expiration duration.
        extra_claims: Optional extra claims dictionary to include in the payload.

    Returns:
        Encoded and cryptographically signed JWT string.
    """
    now = datetime.now(timezone.utc)
    if expires_delta is not None:
        expire = now + expires_delta
    else:
        expire = now + timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)

    payload: Dict[str, Any] = {
        "sub": str(subject),
        "iat": int(now.timestamp()),
        "exp": int(expire.timestamp()),
    }
    if extra_claims:
        payload.update(extra_claims)

    encoded_jwt: str = jwt.encode(
        payload,
        settings.SECRET_KEY,
        algorithm=settings.JWT_ALGORITHM,
    )
    return encoded_jwt


def decode_access_token(token: str) -> Optional[Dict[str, Any]]:
    """Decode and validate a JWT access token safely.

    Rejects expired, malformed, or tampered tokens safely by returning None.

    Args:
        token: The encoded JWT token string.

    Returns:
        Decoded payload dictionary if valid and unexpired; None otherwise.
    """
    if not token or not isinstance(token, str):
        return None

    try:
        payload = jwt.decode(
            token,
            settings.SECRET_KEY,
            algorithms=[settings.JWT_ALGORITHM],
            options={"require": ["exp", "sub"]},
        )
        return payload
    except (ExpiredSignatureError, InvalidTokenError, PyJWTError):
        return None
