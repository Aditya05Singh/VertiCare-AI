import bcrypt
from datetime import datetime, timedelta, timezone
from typing import Any, Optional, Dict, Union
from jose import jwt, JWTError
from app.core.config import settings


def hash_password(password: str) -> str:
    """Generate a secure salted bcrypt hash for a plaintext password."""
    # Truncate to 72 bytes as per bcrypt specification
    pwd_bytes = password.encode("utf-8")[:72]
    salt = bcrypt.gensalt(rounds=12)
    hashed = bcrypt.hashpw(pwd_bytes, salt)
    return hashed.decode("utf-8")


def verify_password(plain_password: str, hashed_password: str) -> bool:
    """Verify a plaintext password against a stored bcrypt hash."""
    try:
        pwd_bytes = plain_password.encode("utf-8")[:72]
        hash_bytes = hashed_password.encode("utf-8")
        return bcrypt.checkpw(pwd_bytes, hash_bytes)
    except Exception:
        return False


def create_access_token(
    user_id: str,
    role: str,
    email: str,
    expires_delta: Optional[timedelta] = None
) -> str:
    """
    Create a signed JWT access token containing only minimal non-sensitive identity claims.
    DO NOT store passwords or sensitive health records in the JWT claims payload.
    """
    if expires_delta:
        expire = datetime.now(timezone.utc) + expires_delta
    else:
        expire = datetime.now(timezone.utc) + timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)

    to_encode: Dict[str, Any] = {
        "sub": str(user_id),
        "role": str(role),
        "email": str(email).lower(),
        "exp": expire,
        "iat": datetime.now(timezone.utc),
        "type": "access"
    }

    return jwt.encode(to_encode, settings.SECRET_KEY, algorithm=settings.ALGORITHM)


def verify_token(token: str) -> Optional[Dict[str, Any]]:
    """Decode and validate a JWT access token."""
    try:
        payload = jwt.decode(
            token,
            settings.SECRET_KEY,
            algorithms=[settings.ALGORITHM]
        )
        if "sub" not in payload or "role" not in payload:
            return None
        return payload
    except JWTError:
        return None
