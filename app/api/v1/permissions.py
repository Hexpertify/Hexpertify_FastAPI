import uuid
from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession
from app.core.database import get_db
from app.services.permission_service import PermissionService
from app.schemas.permission import PermissionCreate, PermissionUpdate, PermissionOut

router = APIRouter(prefix="/permissions", tags=["Permissions"])


@router.get("/", response_model=list[PermissionOut])
async def list_permissions(db: AsyncSession = Depends(get_db)):
    service = PermissionService(db)
    return await service.list_permissions()


@router.get("/{permission_id}", response_model=PermissionOut)
async def get_permission(permission_id: uuid.UUID, db: AsyncSession = Depends(get_db)):
    service = PermissionService(db)
    return await service.get_permission(permission_id)


@router.post("/", response_model=PermissionOut, status_code=201)
async def create_permission(data: PermissionCreate, db: AsyncSession = Depends(get_db)):
    service = PermissionService(db)
    return await service.create_permission(data)


@router.put("/{permission_id}", response_model=PermissionOut)
async def update_permission(permission_id: uuid.UUID, data: PermissionUpdate, db: AsyncSession = Depends(get_db)):
    service = PermissionService(db)
    return await service.update_permission(permission_id, data)


@router.delete("/{permission_id}", status_code=204)
async def delete_permission(permission_id: uuid.UUID, db: AsyncSession = Depends(get_db)):
    service = PermissionService(db)
    await service.delete_permission(permission_id)