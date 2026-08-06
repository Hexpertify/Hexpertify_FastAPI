from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession
from app.core.database import get_db
from app.repositories.role_repository import RoleRepository
from app.repositories.permission_repository import PermissionRepository
from app.repositories.menu_repository import MenuRepository
from app.schemas.lookup import LookupItem

router = APIRouter(prefix="/lookup", tags=["Lookup"])


@router.get("/roles", response_model=list[LookupItem])
async def lookup_roles(db: AsyncSession = Depends(get_db)):
    repo = RoleRepository(db)
    roles = await repo.get_all()
    return [{"id": r.id, "code": r.code, "name": r.name} for r in roles if r.is_active]


@router.get("/permissions", response_model=list[LookupItem])
async def lookup_permissions(db: AsyncSession = Depends(get_db)):
    repo = PermissionRepository(db)
    permissions = await repo.get_all()
    return [{"id": p.id, "code": p.code, "name": p.name} for p in permissions if p.is_active]


@router.get("/menus", response_model=list[LookupItem])
async def lookup_menus(db: AsyncSession = Depends(get_db)):
    repo = MenuRepository(db)
    menus = await repo.get_all()
    return [{"id": m.id, "code": m.code, "name": m.name} for m in menus if m.is_active]