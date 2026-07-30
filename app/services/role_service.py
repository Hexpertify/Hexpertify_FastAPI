import uuid
from fastapi import HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from app.repositories.role_repository import RoleRepository
from app.schemas.role import RoleCreate, RoleUpdate


class RoleService:
    def __init__(self, db: AsyncSession):
        self.repo = RoleRepository(db)

    async def list_roles(self):
        return await self.repo.get_all()

    async def get_role(self, role_id: uuid.UUID):
        role = await self.repo.get_by_id(role_id)
        if not role:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Role not found")
        return role

    async def create_role(self, data: RoleCreate):
        existing = await self.repo.get_by_code(data.code)
        if existing:
            raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail="Role code already exists")
        return await self.repo.create(data)

    async def update_role(self, role_id: uuid.UUID, data: RoleUpdate):
        role = await self.get_role(role_id)
        if data.code and data.code != role.code:
            existing = await self.repo.get_by_code(data.code)
            if existing:
                raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail="Role code already exists")
        return await self.repo.update(role, data)

    async def delete_role(self, role_id: uuid.UUID):
        role = await self.get_role(role_id)
        await self.repo.delete(role)