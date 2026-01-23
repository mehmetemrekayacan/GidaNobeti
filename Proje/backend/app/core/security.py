"""
Security Utilities - Password Hashing & JWT
"""
from passlib.context import CryptContext
from jose import JWTError, jwt
from datetime import datetime, timedelta
from app.core.config import settings
import hashlib

# Password hashing context
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")


def hash_tckn(tckn: str) -> str:
    """
    Hash TCKN using SHA-256 for secure storage.
    Args:
        tckn: TC Kimlik No (plain text)
    Returns:
        Hashed TCKN (hex string)
    """
    return hashlib.sha256(tckn.encode()).hexdigest()


def hash_password(password: str) -> str:
    """
    Hash password using bcrypt.
    Args:
        password: Plain text password
    Returns:
        Hashed password
    """
    return pwd_context.hash(password)


def verify_password(plain_password: str, hashed_password: str) -> bool:
    """
    Verify password against hash.
    Args:
        plain_password: Plain text password
        hashed_password: Bcrypt hash
    Returns:
        True if password matches
    """
    return pwd_context.verify(plain_password, hashed_password)


def create_access_token(data: dict, expires_delta: timedelta | None = None) -> str:
    """
    Create JWT access token.
    Args:
        data: Payload data (user_id, role, etc.)
        expires_delta: Token expiration time
    Returns:
        JWT token string
    """
    to_encode = data.copy()
    
    if expires_delta:
        expire = datetime.utcnow() + expires_delta
    else:
        expire = datetime.utcnow() + timedelta(minutes=60)
    
    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(to_encode, settings.SECRET_KEY, algorithm=settings.ALGORITHM)
    return encoded_jwt


def decode_access_token(token: str) -> dict | None:
    """
    Decode and verify JWT token.
    Args:
        token: JWT token string
    Returns:
        Decoded payload or None if invalid
    """
    try:
        payload = jwt.decode(token, settings.SECRET_KEY, algorithms=[settings.ALGORITHM])
        return payload
    except JWTError:
        return None
