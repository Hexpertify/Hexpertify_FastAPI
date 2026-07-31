import uuid
from fastapi import HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from app.repositories.menu_repository import MenuRepository
from app.schemas.menu import MenuCreate, MenuUpdate


class MenuService:
    def __init__(self, db: AsyncSession):
        self.repo = MenuRepository(db)

    async def list_menus(self):
        return await self.repo.get_all()

    async def get_menu(self, menu_id: uuid.UUID):
        menu = await self.repo.get_by_id(menu_id)
        if not menu:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Menu not found")
        return menu

    async def create_menu(self, data: MenuCreate):
        existing = await self.repo.get_by_code(data.code)
        if existing:
            raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail="Menu code already exists")
        if data.parent_id:
            parent = await self.repo.get_by_id(data.parent_id)
            if not parent:
                raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Parent menu does not exist")
        return await self.repo.create(data)

    async def update_menu(self, menu_id: uuid.UUID, data: MenuUpdate):
        menu = await self.get_menu(menu_id)
        if data.code and data.code != menu.code:
            existing = await self.repo.get_by_code(data.code)
            if existing:
                raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail="Menu code already exists")
        if data.parent_id:
            if data.parent_id == menu_id:
                raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Menu cannot be its own parent")
            parent = await self.repo.get_by_id(data.parent_id)
            if not parent:
                raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Parent menu does not exist")
        return await self.repo.update(menu, data)

    async def delete_menu(self, menu_id: uuid.UUID):
        menu = await self.get_menu(menu_id)
        await self.repo.delete(menu)

    async def get_menu_tree(self):
        roots = await self.repo.get_root_menus()
        return [await self._build_tree_node(menu) for menu in roots]

    async def _build_tree_node(self, menu):
        children = await self.repo.get_children(menu.id)
        node = {
            "id": menu.id,
            "parent_id": menu.parent_id,
            "code": menu.code,
            "name": menu.name,
            "route": menu.route,
            "icon": menu.icon,
            "sort_order": menu.sort_order,
            "is_visible": menu.is_visible,
            "is_active": menu.is_active,
            "created_at": menu.created_at,
            "updated_at": menu.updated_at,
            "children": [await self._build_tree_node(child) for child in children],
        }
        return node