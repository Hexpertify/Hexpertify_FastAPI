import uuid
from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession
from app.core.database import get_db
from app.services.role_service import RoleService
from app.schemas.role import RoleCreate, RoleUpdate, RoleOut
from app.permissions.decorators import require_roles

router = APIRouter(prefix="/roles", tags=["Roles"])


@router.get("/", response_model=list[RoleOut])
async def list_roles(db: AsyncSession = Depends(get_db)):
    service = RoleService(db)
    return await service.list_roles()


@router.get("/{role_id}", response_model=RoleOut)
async def get_role(role_id: uuid.UUID, db: AsyncSession = Depends(get_db)):
    service = RoleService(db)
    return await service.get_role(role_id)


@router.post("/", response_model=RoleOut, status_code=201)
async def create_role(
    data: RoleCreate,
    db: AsyncSession = Depends(get_db),
    current_user=Depends(require_roles("ADMIN", "SUPER_ADMIN")),
):
    service = RoleService(db)
    return await service.create_role(data)


@router.put("/{role_id}", response_model=RoleOut)
async def update_role(role_id: uuid.UUID, data: RoleUpdate, db: AsyncSession = Depends(get_db)):
    service = RoleService(db)
    return await service.update_role(role_id, data)


@router.delete("/{role_id}", status_code=204)
async def delete_role(role_id: uuid.UUID, db: AsyncSession = Depends(get_db)):
    service = RoleService(db)
    await service.delete_role(role_id)