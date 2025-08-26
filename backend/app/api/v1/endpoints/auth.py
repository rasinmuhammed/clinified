"""
Authentication endpoints
"""

from datetime import timedelta
from typing import Any
from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordRequestForm
from sqlalchemy.ext.asyncio import AsyncSession
import structlog

from app.core.database import get_db
from app.core.security import SecurityService, get_current_user
from app.models.user import User
from app.schemas.auth import (
    TokenResponse,
    UserLogin,
    UserRegister,
    UserResponse,
    RefreshTokenRequest
)
from app.services.auth_service import AuthService
from app.repositories.user_repository import UserRepository

logger = structlog.get_logger()
router = APIRouter()

@router.post("/login", response_model=TokenResponse)
async def login(
    user_credentials: UserLogin,
    db: AsyncSession = Depends(get_db)
) -> Any:
    """User login endpoint"""
    try:
        auth_service = AuthService(db)
        result = await auth_service.authenticate_user(
            email=user_credentials.email,
            password=user_credentials.password
        )
        
        if not result["success"]:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail=result["message"]
            )
        
        user = result["user"]
        
        # Create tokens
        access_token = SecurityService.create_access_token(
            data={"sub": str(user.id), "email": user.email, "roles": user.roles}
        )
        refresh_token = SecurityService.create_refresh_token(
            data={"sub": str(user.id)}
        )
        
        # Update last login
        user_repo = UserRepository(db)
        await user_repo.update_last_login(user.id)
        
        logger.info("User logged in successfully", user_id=str(user.id), email=user.email)
        
        return TokenResponse(
            access_token=access_token,
            refresh_token=refresh_token,
            token_type="bearer",
            expires_in=timedelta(minutes=30).total_seconds(),
            user=UserResponse.from_user(user)
        )
        
    except Exception as e:
        logger.error("Login failed", error=str(e), email=user_credentials.email)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Login failed"
        )

@router.post("/register", response_model=UserResponse)
async def register(
    user_data: UserRegister,
    db: AsyncSession = Depends(get_db)
) -> Any:
    """User registration endpoint"""
    try:
        auth_service = AuthService(db)
        result = await auth_service.register_user(user_data)
        
        if not result["success"]:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=result["message"]
            )
        
        user = result["user"]
        logger.info("User registered successfully", user_id=str(user.id), email=user.email)
        
        return UserResponse.from_user(user)
        
    except Exception as e:
        logger.error("Registration failed", error=str(e), email=user_data.email)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Registration failed"
        )

@router.post("/refresh", response_model=TokenResponse)
async def refresh_token(
    refresh_data: RefreshTokenRequest,
    db: AsyncSession = Depends(get_db)
) -> Any:
    """Refresh access token"""
    try:
        # Verify refresh token
        payload = SecurityService.verify_token(refresh_data.refresh_token)
        if not payload or payload.get("type") != "refresh":
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid refresh token"
            )
        
        user_id = payload.get("sub")
        if not user_id:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid token payload"
            )
        
        # Get user
        user_repo = UserRepository(db)
        user = await user_repo.get_by_id(user_id)
        
        if not user or not user.is_active:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="User not found or inactive"
            )
        
        # Create new access token
        access_token = SecurityService.create_access_token(
            data={"sub": str(user.id), "email": user.email, "roles": user.roles}
        )
        
        logger.info("Token refreshed successfully", user_id=str(user.id))
        
        return TokenResponse(
            access_token=access_token,
            refresh_token=refresh_data.refresh_token,
            token_type="bearer",
            expires_in=timedelta(minutes=30).total_seconds(),
            user=UserResponse.from_user(user)
        )
        
    except Exception as e:
        logger.error("Token refresh failed", error=str(e))
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Token refresh failed"
        )

@router.post("/logout")
async def logout(
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
) -> Any:
    """User logout endpoint"""
    try:
        # In a real implementation, you might want to blacklist the token
        # For now, we'll just log the logout
        logger.info("User logged out", user_id=str(current_user.id))
        
        return {"message": "Successfully logged out"}
        
    except Exception as e:
        logger.error("Logout failed", error=str(e))
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Logout failed"
        )

@router.get("/me", response_model=UserResponse)
async def get_current_user_info(
    current_user: User = Depends(get_current_user)
) -> Any:
    """Get current user information"""
    return UserResponse.from_user(current_user)

@router.post("/verify-email")
async def verify_email(
    token: str,
    db: AsyncSession = Depends(get_db)
) -> Any:
    """Verify user email"""
    try:
        auth_service = AuthService(db)
        result = await auth_service.verify_email(token)
        
        if not result["success"]:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=result["message"]
            )
        
        return {"message": "Email verified successfully"}
        
    except Exception as e:
        logger.error("Email verification failed", error=str(e))
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Email verification failed"
        )

@router.post("/forgot-password")
async def forgot_password(
    email: str,
    db: AsyncSession = Depends(get_db)
) -> Any:
    """Send password reset email"""
    try:
        auth_service = AuthService(db)
        result = await auth_service.forgot_password(email)
        
        if not result["success"]:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=result["message"]
            )
        
        return {"message": "Password reset email sent"}
        
    except Exception as e:
        logger.error("Forgot password failed", error=str(e))
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to send password reset email"
        )

@router.post("/reset-password")
async def reset_password(
    token: str,
    new_password: str,
    db: AsyncSession = Depends(get_db)
) -> Any:
    """Reset password with token"""
    try:
        auth_service = AuthService(db)
        result = await auth_service.reset_password(token, new_password)
        
        if not result["success"]:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=result["message"]
            )
        
        return {"message": "Password reset successfully"}
        
    except Exception as e:
        logger.error("Password reset failed", error=str(e))
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Password reset failed"
        ) 