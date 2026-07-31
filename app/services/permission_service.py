import uuid
from fastapi import HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from app.repositories.permission_repository import PermissionRepository
from app.schemas.permission import PermissionCreate, PermissionUpdate


class PermissionService:
    def __init__(self, db: AsyncSession):
        self.repo = PermissionRepository(db)

    async def list_permissions(self):
        return await self.repo.get_all()

    async def get_permission(self, permission_id: uuid.UUID):
        permission = await self.repo.get_by_id(permission_id)
        if not permission:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Permission not found")
        return permission

    async def create_permission(self, data: PermissionCreate):
        existing = await self.repo.get_by_code(data.code)
        if existing:
            raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail="Permission code already exists")
        return await self.repo.create(data)

    async def update_permission(self, permission_id: uuid.UUID, data: PermissionUpdate):
        permission = await self.get_permission(permission_id)
        if data.code and data.code != permission.code:
            existing = await self.repo.get_by_code(data.code)
            if existing:
                raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail="Permission code already exists")
        return await self.repo.update(permission, data)

    async def delete_permission(self, permission_id: uuid.UUID):
        permission = await self.get_permission(permission_id)
        await self.repo.delete(permission)