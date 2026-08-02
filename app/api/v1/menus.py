import uuid
from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession
from app.core.database import get_db
from app.services.menu_service import MenuService
from app.schemas.menu import MenuCreate, MenuUpdate, MenuOut, MenuTreeOut

router = APIRouter(prefix="/menus", tags=["Menus"])


@router.get("/", response_model=list[MenuOut])
async def list_menus(db: AsyncSession = Depends(get_db)):
    service = MenuService(db)
    return await service.list_menus()


@router.get("/tree", response_model=list[MenuTreeOut])
async def get_menu_tree(db: AsyncSession = Depends(get_db)):
    service = MenuService(db)
    return await service.get_menu_tree()


@router.get("/{menu_id}", response_model=MenuOut)
async def get_menu(menu_id: uuid.UUID, db: AsyncSession = Depends(get_db)):
    service = MenuService(db)
    return await service.get_menu(menu_id)


@router.post("/", response_model=MenuOut, status_code=201)
async def create_menu(data: MenuCreate, db: AsyncSession = Depends(get_db)):
    service = MenuService(db)
    return await service.create_menu(data)


@router.put("/{menu_id}", response_model=MenuOut)
async def update_menu(menu_id: uuid.UUID, data: MenuUpdate, db: AsyncSession = Depends(get_db)):
    service = MenuService(db)
    return await service.update_menu(menu_id, data)


@router.delete("/{menu_id}", status_code=204)
async def delete_menu(menu_id: uuid.UUID, db: AsyncSession = Depends(get_db)):
    service = MenuService(db)
    await service.delete_menu(menu_id)