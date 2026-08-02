import uuid
from fastapi import HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from app.repositories.role_menu_repository import RoleMenuRepository
from app.repositories.role_repository import RoleRepository
from app.repositories.menu_repository import MenuRepository


class RoleMenuService:
    def __init__(self, db: AsyncSession):
        self.repo = RoleMenuRepository(db)
        self.role_repo = RoleRepository(db)
        self.menu_repo = MenuRepository(db)

    async def _ensure_role_exists(self, role_id: uuid.UUID):
        role = await self.role_repo.get_by_id(role_id)
        if not role:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Role not found")
        return role

    async def _ensure_menu_exists(self, menu_id: uuid.UUID):
        menu = await self.menu_repo.get_by_id(menu_id)
        if not menu:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Menu not found")
        return menu

    async def get_menus_for_role(self, role_id: uuid.UUID):
        await self._ensure_role_exists(role_id)
        return await self.repo.get_menus_for_role(role_id)

    async def add_menu(self, role_id: uuid.UUID, menu_id: uuid.UUID):
        await self._ensure_role_exists(role_id)
        await self._ensure_menu_exists(menu_id)
        if await self.repo.exists(role_id, menu_id):
            raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail="Menu already assigned to role")
        await self.repo.add_menu(role_id, menu_id)
        return await self.repo.get_menus_for_role(role_id)

    async def replace_menus(self, role_id: uuid.UUID, menu_ids: list[uuid.UUID]):
        await self._ensure_role_exists(role_id)
        for menu_id in menu_ids:
            await self._ensure_menu_exists(menu_id)
        await self.repo.replace_menus(role_id, menu_ids)
        return await self.repo.get_menus_for_role(role_id)

    async def remove_menu(self, role_id: uuid.UUID, menu_id: uuid.UUID):
        await self._ensure_role_exists(role_id)
        if not await self.repo.exists(role_id, menu_id):
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Menu not assigned to role")
        await self.repo.remove_menu(role_id, menu_id)