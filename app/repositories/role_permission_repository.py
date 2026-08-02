import uuid
from sqlalchemy import select, delete
from sqlalchemy.ext.asyncio import AsyncSession
from app.models.role_permission import RolePermission
from app.models.permission import Permission


class RolePermissionRepository:
    def __init__(self, db: AsyncSession):
        self.db = db

    async def get_permissions_for_role(self, role_id: uuid.UUID):
        result = await self.db.execute(
            select(Permission).join(RolePermission, RolePermission.permission_id == Permission.id)
            .where(RolePermission.role_id == role_id)
        )
        return result.scalars().all()

    async def exists(self, role_id: uuid.UUID, permission_id: uuid.UUID):
        result = await self.db.execute(
            select(RolePermission).where(
                RolePermission.role_id == role_id, RolePermission.permission_id == permission_id
            )
        )
        return result.scalar_one_or_none() is not None

    async def add_permission(self, role_id: uuid.UUID, permission_id: uuid.UUID):
        link = RolePermission(role_id=role_id, permission_id=permission_id)
        self.db.add(link)
        await self.db.commit()

    async def replace_permissions(self, role_id: uuid.UUID, permission_ids: list[uuid.UUID]):
        await self.db.execute(delete(RolePermission).where(RolePermission.role_id == role_id))
        for permission_id in permission_ids:
            self.db.add(RolePermission(role_id=role_id, permission_id=permission_id))
        await self.db.commit()

    async def remove_permission(self, role_id: uuid.UUID, permission_id: uuid.UUID):
        await self.db.execute(
            delete(RolePermission).where(
                RolePermission.role_id == role_id, RolePermission.permission_id == permission_id
            )
        )
        await self.db.commit()