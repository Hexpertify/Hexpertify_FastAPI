import uuid
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from app.models.role import Role
from app.schemas.role import RoleCreate, RoleUpdate


class RoleRepository:
    def __init__(self, db: AsyncSession):
        self.db = db

    async def get_all(self):
        result = await self.db.execute(select(Role))
        return result.scalars().all()

    async def get_by_id(self, role_id: uuid.UUID):
        result = await self.db.execute(select(Role).where(Role.id == role_id))
        return result.scalar_one_or_none()

    async def get_by_code(self, code: str):
        result = await self.db.execute(select(Role).where(Role.code == code))
        return result.scalar_one_or_none()

    async def create(self, data: RoleCreate):
        role = Role(**data.model_dump())
        self.db.add(role)
        await self.db.commit()
        await self.db.refresh(role)
        return role

    async def update(self, role: Role, data: RoleUpdate):
        for field, value in data.model_dump(exclude_unset=True).items():
            setattr(role, field, value)
        await self.db.commit()
        await self.db.refresh(role)
        return role

    async def delete(self, role: Role):
        await self.db.delete(role)
        await self.db.commit()