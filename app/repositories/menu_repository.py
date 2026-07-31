import uuid
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from app.models.menu import Menu
from app.schemas.menu import MenuCreate, MenuUpdate


class MenuRepository:
    def __init__(self, db: AsyncSession):
        self.db = db

    async def get_all(self):
        result = await self.db.execute(select(Menu).order_by(Menu.sort_order))
        return result.scalars().all()

    async def get_by_id(self, menu_id: uuid.UUID):
        result = await self.db.execute(select(Menu).where(Menu.id == menu_id))
        return result.scalar_one_or_none()

    async def get_by_code(self, code: str):
        result = await self.db.execute(select(Menu).where(Menu.code == code))
        return result.scalar_one_or_none()

    async def get_root_menus(self):
        result = await self.db.execute(
            select(Menu).where(Menu.parent_id.is_(None)).order_by(Menu.sort_order)
        )
        return result.scalars().all()

    async def get_children(self, parent_id: uuid.UUID):
        result = await self.db.execute(
            select(Menu).where(Menu.parent_id == parent_id).order_by(Menu.sort_order)
        )
        return result.scalars().all()

    async def create(self, data: MenuCreate):
        menu = Menu(**data.model_dump())
        self.db.add(menu)
        await self.db.commit()
        await self.db.refresh(menu)
        return menu

    async def update(self, menu: Menu, data: MenuUpdate):
        for field, value in data.model_dump(exclude_unset=True).items():
            setattr(menu, field, value)
        await self.db.commit()
        await self.db.refresh(menu)
        return menu

    async def delete(self, menu: Menu):
        await self.db.delete(menu)
        await self.db.commit()