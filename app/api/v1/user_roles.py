import uuid
from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession
from app.core.database import get_db
from app.services.user_role_service import UserRoleService
from app.schemas.user_role import UserRoleAssign, UserRoleBulkAssign, RoleOut
from app.permissions.decorators import require_roles

router = APIRouter(prefix="/users", tags=["User Roles"])


@router.get("/{user_id}/roles", response_model=list[RoleOut])
async def get_user_roles(user_id: uuid.UUID, db: AsyncSession = Depends(get_db)):
    service = UserRoleService(db)
    return await service.get_roles_for_user(user_id)


@router.put("/{user_id}/roles", response_model=list[RoleOut])
async def replace_user_roles(
    user_id: uuid.UUID,
    data: UserRoleBulkAssign,
    db: AsyncSession = Depends(get_db),
    current_user=Depends(require_roles("ADMIN", "SUPER_ADMIN")),
):
    service = UserRoleService(db)
    return await service.replace_roles(user_id, data.role_ids)


@router.post("/{user_id}/roles", response_model=list[RoleOut], status_code=201)
async def add_user_role(
    user_id: uuid.UUID,
    data: UserRoleAssign,
    db: AsyncSession = Depends(get_db),
    current_user=Depends(require_roles("ADMIN", "SUPER_ADMIN")),
):
    service = UserRoleService(db)
    return await service.add_role(user_id, data.role_id)


@router.delete("/{user_id}/roles/{role_id}", status_code=204)
async def remove_user_role(
    user_id: uuid.UUID,
    role_id: uuid.UUID,
    db: AsyncSession = Depends(get_db),
    current_user=Depends(require_roles("ADMIN", "SUPER_ADMIN")),
):
    service = UserRoleService(db)
    await service.remove_role(user_id, role_id)