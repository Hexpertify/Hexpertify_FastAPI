from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession
from app.core.database import get_db
from app.core.dependencies import get_current_user
from app.services.auth_service import AuthService
from app.schemas.auth import (
    LoginRequest, TokenResponse, RefreshRequest, ChangePasswordRequest
)
from app.schemas.user import UserOut

router = APIRouter(prefix="/auth", tags=["Authentication"])


@router.post("/login", response_model=TokenResponse)
async def login(data: LoginRequest, db: AsyncSession = Depends(get_db)):
    service = AuthService(db)
    return await service.login(data.email, data.password)


@router.post("/refresh-token", response_model=TokenResponse)
async def refresh_token(data: RefreshRequest, db: AsyncSession = Depends(get_db)):
    service = AuthService(db)
    return await service.refresh(data.refresh_token)


@router.post("/logout", status_code=204)
async def logout(data: RefreshRequest, db: AsyncSession = Depends(get_db)):
    service = AuthService(db)
    await service.logout(data.refresh_token)


@router.get("/me", response_model=UserOut)
async def get_me(current_user=Depends(get_current_user)):
    return current_user


@router.post("/change-password", status_code=204)
async def change_password(
    data: ChangePasswordRequest,
    current_user=Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    service = AuthService(db)
    await service.change_password(current_user, data.old_password, data.new_password)