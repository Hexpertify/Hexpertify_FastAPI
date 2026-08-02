import uuid
from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession
from app.core.database import get_db
from app.services.role_permission_service import RolePermissionService
from app.schemas.role_permission import RolePermissionAssign, RolePermissionBulkAssign, PermissionOut

router = APIRouter(prefix="/roles", tags=["Role Permissions"])


@router.get("/{role_id}/permissions", response_model=list[PermissionOut])
async def get_role_permissions(role_id: uuid.UUID, db: AsyncSession = Depends(get_db)):
    service = RolePermissionService(db)
    return await service.get_permissions_for_role(role_id)


@router.put("/{role_id}/permissions", response_model=list[PermissionOut])
async def replace_role_permissions(role_id: uuid.UUID, data: RolePermissionBulkAssign, db: AsyncSession = Depends(get_db)):
    service = RolePermissionService(db)
    return await service.replace_permissions(role_id, data.permission_ids)


@router.post("/{role_id}/permissions", response_model=list[PermissionOut], status_code=201)
async def add_role_permission(role_id: uuid.UUID, data: RolePermissionAssign, db: AsyncSession = Depends(get_db)):
    service = RolePermissionService(db)
    return await service.add_permission(role_id, data.permission_id)


@router.delete("/{role_id}/permissions/{permission_id}", status_code=204)
async def remove_role_permission(role_id: uuid.UUID, permission_id: uuid.UUID, db: AsyncSession = Depends(get_db)):
    service = RolePermissionService(db)
    await service.remove_permission(role_id, permission_id)