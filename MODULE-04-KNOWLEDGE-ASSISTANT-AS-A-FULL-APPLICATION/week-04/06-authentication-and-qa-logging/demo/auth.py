"""Authentication utilities: bcrypt password hashing and JWT tokens.

Teaches: one-way hashing, constant-time comparison, stateless auth.
"""

import os
from datetime import datetime, timedelta, timezone

import bcrypt
import jwt
from dotenv import load_dotenv
from fastapi import Depends, HTTPException
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials

load_dotenv()

SECRET_KEY = os.getenv("JWT_SECRET_KEY", "change-me-in-production")
ALGORITHM = "HS256"
TOKEN_EXPIRY_HOURS = 24

security = HTTPBearer()


# ── Password hashing ───────────────────────────────────────────────

def hash_password(plain: str) -> str:
    """Hash a password with a random salt for storage."""
    return bcrypt.hashpw(plain.encode(), bcrypt.gensalt()).decode()


def verify_password(plain: str, hashed: str) -> bool:
    """Check a password against its stored hash (constant-time)."""
    return bcrypt.checkpw(plain.encode(), hashed.encode())


# ── JWT tokens ─────────────────────────────────────────────────────

def create_token(username: str) -> str:
    """Create a JWT with the username and a 24-hour expiry."""
    payload = {
        "sub": username,
        "exp": datetime.now(timezone.utc) + timedelta(hours=TOKEN_EXPIRY_HOURS),
    }
    return jwt.encode(payload, SECRET_KEY, algorithm=ALGORITHM)


def decode_token(token: str) -> dict:
    """Decode and verify a JWT. Raises jwt.PyJWTError on failure."""
    return jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])


# ── FastAPI dependency ─────────────────────────────────────────────

def get_current_user(
    creds: HTTPAuthorizationCredentials = Depends(security),
) -> str:
    """FastAPI dependency: extract username from the Bearer token."""
    try:
        payload = jwt.decode(creds.credentials, SECRET_KEY, algorithms=[ALGORITHM])
        username = payload.get("sub")
        if username is None:
            raise HTTPException(401, "Invalid token")
        return username
    except jwt.ExpiredSignatureError:
        raise HTTPException(401, "Token has expired")
    except jwt.PyJWTError:
        raise HTTPException(401, "Invalid token")
