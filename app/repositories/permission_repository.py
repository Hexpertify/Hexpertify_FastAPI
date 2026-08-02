import uuid
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from app.models.permission import Permission
from app.schemas.permission import PermissionCreate, PermissionUpdate


class PermissionRepository:
    def __init__(self, db: AsyncSession):
        self.db = db

    async def get_all(self):
        result = await self.db.execute(select(Permission))
        return result.scalars().all()

    async def get_by_id(self, permission_id: uuid.UUID):
        result = await self.db.execute(select(Permission).where(Permission.id == permission_id))
        return result.scalar_one_or_none()

    async def get_by_code(self, code: str):
        result = await self.db.execute(select(Permission).where(Permission.code == code))
        return result.scalar_one_or_none()

    async def create(self, data: PermissionCreate):
        permission = Permission(**data.model_dump())
        self.db.add(permission)
        await self.db.commit()
        await self.db.refresh(permission)
        return permission

    async def update(self, permission: Permission, data: PermissionUpdate):
        for field, value in data.model_dump(exclude_unset=True).items():
            setattr(permission, field, value)
        await self.db.commit()
        await self.db.refresh(permission)
        return permission

    async def delete(self, permission: Permission):
        await self.db.delete(permission)
        await self.db.commit()