import uuid
from sqlalchemy import select, delete
from sqlalchemy.ext.asyncio import AsyncSession
from app.models.user_role import UserRole
from app.models.role import Role


class UserRoleRepository:
    def __init__(self, db: AsyncSession):
        self.db = db

    async def get_roles_for_user(self, user_id: uuid.UUID):
        result = await self.db.execute(
            select(Role).join(UserRole, UserRole.role_id == Role.id).where(UserRole.user_id == user_id)
        )
        return result.scalars().all()

    async def exists(self, user_id: uuid.UUID, role_id: uuid.UUID):
        result = await self.db.execute(
            select(UserRole).where(UserRole.user_id == user_id, UserRole.role_id == role_id)
        )
        return result.scalar_one_or_none() is not None

    async def add_role(self, user_id: uuid.UUID, role_id: uuid.UUID):
        link = UserRole(user_id=user_id, role_id=role_id)
        self.db.add(link)
        await self.db.commit()

    async def replace_roles(self, user_id: uuid.UUID, role_ids: list[uuid.UUID]):
        await self.db.execute(delete(UserRole).where(UserRole.user_id == user_id))
        for role_id in role_ids:
            self.db.add(UserRole(user_id=user_id, role_id=role_id))
        await self.db.commit()

    async def remove_role(self, user_id: uuid.UUID, role_id: uuid.UUID):
        await self.db.execute(
            delete(UserRole).where(UserRole.user_id == user_id, UserRole.role_id == role_id)
        )
        await self.db.commit()