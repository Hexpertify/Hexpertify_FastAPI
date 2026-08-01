import uuid
from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession
from app.core.database import get_db
from app.services.role_menu_service import RoleMenuService
from app.schemas.role_menu import RoleMenuAssign, RoleMenuBulkAssign, MenuOut

router = APIRouter(prefix="/roles", tags=["Role Menus"])


@router.get("/{role_id}/menus", response_model=list[MenuOut])
async def get_role_menus(role_id: uuid.UUID, db: AsyncSession = Depends(get_db)):
    service = RoleMenuService(db)
    return await service.get_menus_for_role(role_id)


@router.put("/{role_id}/menus", response_model=list[MenuOut])
async def replace_role_menus(role_id: uuid.UUID, data: RoleMenuBulkAssign, db: AsyncSession = Depends(get_db)):
    service = RoleMenuService(db)
    return await service.replace_menus(role_id, data.menu_ids)


@router.post("/{role_id}/menus", response_model=list[MenuOut], status_code=201)
async def add_role_menu(role_id: uuid.UUID, data: RoleMenuAssign, db: AsyncSession = Depends(get_db)):
    service = RoleMenuService(db)
    return await service.add_menu(role_id, data.menu_id)


@router.delete("/{role_id}/menus/{menu_id}", status_code=204)
async def remove_role_menu(role_id: uuid.UUID, menu_id: uuid.UUID, db: AsyncSession = Depends(get_db)):
    service = RoleMenuService(db)
    await service.remove_menu(role_id, menu_id)