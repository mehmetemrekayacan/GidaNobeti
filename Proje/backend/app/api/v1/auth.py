"""
Authentication Endpoints - Register & Login
"""
from fastapi import APIRouter, HTTPException, Depends, status
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from datetime import timedelta, datetime, timezone
from app.db.session import get_db
from app.db.models.user import User, UserRole
from app.schemas.auth import RegisterRequest, LoginRequest, TokenResponse, UserResponse
from app.core.security import hash_tckn, hash_password, verify_password, create_access_token
from app.core.config import settings

router = APIRouter(prefix="/auth", tags=["Authentication"])


@router.post("/register", response_model=TokenResponse, status_code=status.HTTP_201_CREATED)
async def register(
    request: RegisterRequest,
    db: AsyncSession = Depends(get_db)
):
    """
    Register new user (Student).
    
    Steps:
    1. Validate TCKN uniqueness
    2. Hash TCKN & password
    3. Create User record
    4. Generate JWT token
    5. Return token + user info
    """
    try:
        # Hash TCKN for lookup
        tckn_hash_value = hash_tckn(request.tckn)
        
        # Check if TCKN already exists
        stmt = select(User).where(User.tckn_hash == tckn_hash_value)
        result = await db.execute(stmt)
        existing_user = result.scalar_one_or_none()
        
        if existing_user:
            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT,
                detail="TCKN already registered"
            )
        
        # Check email uniqueness if provided
        if request.email:
            stmt = select(User).where(User.email == request.email)
            result = await db.execute(stmt)
            existing_email = result.scalar_one_or_none()
            
            if existing_email:
                raise HTTPException(
                    status_code=status.HTTP_409_CONFLICT,
                    detail="Email already in use"
                )
        
        # Create new user
        new_user = User(
            tckn_hash=tckn_hash_value,
            password_hash=hash_password(request.password),
            full_name=request.full_name,
            email=request.email,
            phone_number=request.phone,
            dorm_id=request.dorm_id,
            room_number=request.room_number,
            role=UserRole.STUDENT,
            is_active=True,
            is_verified=False  # Requires verification later
        )
        
        db.add(new_user)
        await db.commit()
        await db.refresh(new_user)
        
        # Generate JWT token
        access_token_expires = timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)
        access_token = create_access_token(
            data={
                "sub": str(new_user.id),
                "role": new_user.role.value,
                "tckn_hash": new_user.tckn_hash
            },
            expires_delta=access_token_expires
        )
        
        return TokenResponse(
            access_token=access_token,
            token_type="bearer",
            expires_in=settings.ACCESS_TOKEN_EXPIRE_MINUTES * 60,
            user=UserResponse.from_user(new_user)
        )
    except HTTPException:
        raise
    except Exception as e:
        await db.rollback()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Registration failed: {str(e)}"
        )


@router.post("/login", response_model=TokenResponse)
async def login(
    request: LoginRequest,
    db: AsyncSession = Depends(get_db)
):
    """
    User login with TCKN & password.
    
    Steps:
    1. Hash TCKN for lookup
    2. Find user by tckn_hash
    3. Verify password
    4. Check account status (active, not locked)
    5. Generate JWT token
    6. Update last_login_at
    """
    try:
        # Hash TCKN for lookup
        tckn_hash_value = hash_tckn(request.tckn)

        # Find user
        stmt = select(User).where(User.tckn_hash == tckn_hash_value)
        result = await db.execute(stmt)
        user = result.scalar_one_or_none()

        if not user:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid TCKN or password"
            )

        # Check if account is locked (BEFORE password check)
        if user.lockout_until:
            if datetime.now(timezone.utc) < user.lockout_until:
                raise HTTPException(
                    status_code=status.HTTP_403_FORBIDDEN,
                    detail="Account locked due to multiple failed login attempts. Try again in 30 minutes."
                )
            else:
                # Reset lockout if time has passed
                user.lockout_until = None
                user.login_attempts = 0
                await db.commit()

        # Verify password
        if not verify_password(request.password, user.password_hash):
            # Increment login attempts
            user.login_attempts += 1

            # Lock account after 5 failed attempts
            if user.login_attempts >= 5:
                user.lockout_until = datetime.now(timezone.utc) + timedelta(minutes=30)
                await db.commit()
                raise HTTPException(
                    status_code=status.HTTP_403_FORBIDDEN,
                    detail="Account locked due to multiple failed login attempts. Try again in 30 minutes."
                )

            await db.commit()
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid TCKN or password"
            )

        # Check if account is active
        if not user.is_active:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Account is deactivated"
            )

        # Reset login attempts on successful login
        user.login_attempts = 0
        user.last_login_at = datetime.now(timezone.utc)
        await db.commit()
        await db.refresh(user)

        # Generate JWT token
        access_token_expires = timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)
        access_token = create_access_token(
            data={
                "sub": str(user.id),
                "role": user.role.value,
                "tckn_hash": user.tckn_hash
            },
            expires_delta=access_token_expires
        )

        return TokenResponse(
            access_token=access_token,
            token_type="bearer",
            expires_in=settings.ACCESS_TOKEN_EXPIRE_MINUTES * 60,
            user=UserResponse.from_user(user)
        )
    except HTTPException:
        raise
    except Exception as e:
        await db.rollback()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Login failed: {str(e)}"
        )
