import uuid
from fastapi import HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from app.repositories.role_permission_repository import RolePermissionRepository
from app.repositories.role_repository import RoleRepository
from app.repositories.permission_repository import PermissionRepository


class RolePermissionService:
    def __init__(self, db: AsyncSession):
        self.repo = RolePermissionRepository(db)
        self.role_repo = RoleRepository(db)
        self.permission_repo = PermissionRepository(db)

    async def _ensure_role_exists(self, role_id: uuid.UUID):
        role = await self.role_repo.get_by_id(role_id)
        if not role:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Role not found")
        return role

    async def _ensure_permission_exists(self, permission_id: uuid.UUID):
        permission = await self.permission_repo.get_by_id(permission_id)
        if not permission:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Permission not found")
        return permission

    async def get_permissions_for_role(self, role_id: uuid.UUID):
        await self._ensure_role_exists(role_id)
        return await self.repo.get_permissions_for_role(role_id)

    async def add_permission(self, role_id: uuid.UUID, permission_id: uuid.UUID):
        await self._ensure_role_exists(role_id)
        await self._ensure_permission_exists(permission_id)
        if await self.repo.exists(role_id, permission_id):
            raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail="Permission already assigned to role")
        await self.repo.add_permission(role_id, permission_id)
        return await self.repo.get_permissions_for_role(role_id)

    async def replace_permissions(self, role_id: uuid.UUID, permission_ids: list[uuid.UUID]):
        await self._ensure_role_exists(role_id)
        for permission_id in permission_ids:
            await self._ensure_permission_exists(permission_id)
        await self.repo.replace_permissions(role_id, permission_ids)
        return await self.repo.get_permissions_for_role(role_id)

    async def remove_permission(self, role_id: uuid.UUID, permission_id: uuid.UUID):
        await self._ensure_role_exists(role_id)
        if not await self.repo.exists(role_id, permission_id):
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Permission not assigned to role")
        await self.repo.remove_permission(role_id, permission_id)