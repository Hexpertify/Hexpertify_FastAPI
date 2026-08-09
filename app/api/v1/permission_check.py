import uuid
from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession
from app.core.database import get_db
from app.core.dependencies import get_current_user
from app.services.permission_check_service import PermissionCheckService
from app.schemas.permission_check import (
    PermissionCheckRequest, PermissionCheckManyRequest,
    PermissionCheckResponse, PermissionCheckManyResponse
)

router = APIRouter(prefix="/permissions", tags=["Permission Check"])


@router.post("/check", response_model=PermissionCheckResponse)
async def check_permission(
    data: PermissionCheckRequest,
    db: AsyncSession = Depends(get_db),
    current_user=Depends(get_current_user),
):
    service = PermissionCheckService(db)
    result = await service.check_permission(uuid.UUID(data.user_id), data.permission_code)
    return {"has_permission": result}


@router.post("/check-many", response_model=PermissionCheckManyResponse)
async def check_permissions_many(
    data: PermissionCheckManyRequest,
    db: AsyncSession = Depends(get_db),
    current_user=Depends(get_current_user),
):
    service = PermissionCheckService(db)
    results = await service.check_permissions_many(uuid.UUID(data.user_id), data.permission_codes)
    return {"results": results}