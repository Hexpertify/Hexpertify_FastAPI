import uuid
from sqlalchemy import select, delete
from sqlalchemy.ext.asyncio import AsyncSession
from app.models.role_menu import RoleMenu
from app.models.menu import Menu


class RoleMenuRepository:
    def __init__(self, db: AsyncSession):
        self.db = db

    async def get_menus_for_role(self, role_id: uuid.UUID):
        result = await self.db.execute(
            select(Menu).join(RoleMenu, RoleMenu.menu_id == Menu.id).where(RoleMenu.role_id == role_id)
        )
        return result.scalars().all()

    async def exists(self, role_id: uuid.UUID, menu_id: uuid.UUID):
        result = await self.db.execute(
            select(RoleMenu).where(RoleMenu.role_id == role_id, RoleMenu.menu_id == menu_id)
        )
        return result.scalar_one_or_none() is not None

    async def add_menu(self, role_id: uuid.UUID, menu_id: uuid.UUID):
        link = RoleMenu(role_id=role_id, menu_id=menu_id)
        self.db.add(link)
        await self.db.commit()

    async def replace_menus(self, role_id: uuid.UUID, menu_ids: list[uuid.UUID]):
        await self.db.execute(delete(RoleMenu).where(RoleMenu.role_id == role_id))
        for menu_id in menu_ids:
            self.db.add(RoleMenu(role_id=role_id, menu_id=menu_id))
        await self.db.commit()

    async def remove_menu(self, role_id: uuid.UUID, menu_id: uuid.UUID):
        await self.db.execute(
            delete(RoleMenu).where(RoleMenu.role_id == role_id, RoleMenu.menu_id == menu_id)
        )
        await self.db.commit()