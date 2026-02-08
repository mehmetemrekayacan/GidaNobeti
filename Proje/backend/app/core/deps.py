"""
FastAPI Dependencies - Auth, DB, Role-based Permissions (TASK-BE-007)
"""
import uuid
from typing import Callable
from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select

from app.db.session import get_db
from app.db.models.user import User, UserRole
from app.core.security import decode_access_token

security = HTTPBearer(auto_error=False)


# Redis blacklist kontrolü (TASK-BE-007 - future)
# TODO: Token blacklist Redis ile implement edilecek (logout, token invalidation)


async def get_current_user(
    credentials: HTTPAuthorizationCredentials | None = Depends(security),
    db: AsyncSession = Depends(get_db)
) -> User:
    """JWT'den kullanıcı çıkar. Token yoksa 401."""
    if not credentials:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Authentication required",
            headers={"WWW-Authenticate": "Bearer"},
        )
    token = credentials.credentials
    payload = decode_access_token(token)
    if not payload or "sub" not in payload:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid or expired token",
        )
    try:
        user_id = uuid.UUID(payload["sub"])
    except (ValueError, TypeError):
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid token")
    result = await db.execute(select(User).where(User.id == user_id))
    user = result.scalar_one_or_none()
    if not user:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="User not found")
    if not user.is_active:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Account inactive")
    return user


def require_roles(*allowed_roles: UserRole) -> Callable:
    """
    Role-based permission dependency. Sadece belirtilen roller erişebilir.
    Kullanım: current_user: User = Depends(require_roles(UserRole.DORM_MANAGER, UserRole.SYS_ADMIN))
    """
    async def role_checker(current_user: User = Depends(get_current_user)) -> User:
        if current_user.role not in allowed_roles:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail=f"Bu işlem için yetkiniz yok. Gerekli roller: {[r.value for r in allowed_roles]}",
            )
        return current_user
    return role_checker


# Admin panel için kısayol: DORM_MANAGER veya SYS_ADMIN
require_admin = require_roles(UserRole.DORM_MANAGER, UserRole.SYS_ADMIN)

# Sadece öğrenci (STUDENT) için
require_student = require_roles(UserRole.STUDENT)
