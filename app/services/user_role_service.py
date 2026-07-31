import uuid
from fastapi import HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from app.repositories.user_role_repository import UserRoleRepository
from app.repositories.user_repository import UserRepository
from app.repositories.role_repository import RoleRepository


class UserRoleService:
    def __init__(self, db: AsyncSession):
        self.repo = UserRoleRepository(db)
        self.user_repo = UserRepository(db)
        self.role_repo = RoleRepository(db)

    async def _ensure_user_exists(self, user_id: uuid.UUID):
        user = await self.user_repo.get_by_id(user_id)
        if not user:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="User not found")
        return user

    async def _ensure_role_exists(self, role_id: uuid.UUID):
        role = await self.role_repo.get_by_id(role_id)
        if not role:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Role not found")
        return role

    async def get_roles_for_user(self, user_id: uuid.UUID):
        await self._ensure_user_exists(user_id)
        return await self.repo.get_roles_for_user(user_id)

    async def add_role(self, user_id: uuid.UUID, role_id: uuid.UUID):
        await self._ensure_user_exists(user_id)
        await self._ensure_role_exists(role_id)
        if await self.repo.exists(user_id, role_id):
            raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail="Role already assigned to user")
        await self.repo.add_role(user_id, role_id)
        return await self.repo.get_roles_for_user(user_id)

    async def replace_roles(self, user_id: uuid.UUID, role_ids: list[uuid.UUID]):
        await self._ensure_user_exists(user_id)
        for role_id in role_ids:
            await self._ensure_role_exists(role_id)
        await self.repo.replace_roles(user_id, role_ids)
        return await self.repo.get_roles_for_user(user_id)

    async def remove_role(self, user_id: uuid.UUID, role_id: uuid.UUID):
        await self._ensure_user_exists(user_id)
        if not await self.repo.exists(user_id, role_id):
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Role not assigned to user")
        await self.repo.remove_role(user_id, role_id)