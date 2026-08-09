import uuid
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from app.models.user_role import UserRole
from app.models.role_permission import RolePermission
from app.models.permission import Permission


class PermissionCheckService:
    def __init__(self, db: AsyncSession):
        self.db = db

    async def _get_user_permission_codes(self, user_id: uuid.UUID) -> set[str]:
        result = await self.db.execute(
            select(Permission.code)
            .join(RolePermission, RolePermission.permission_id == Permission.id)
            .join(UserRole, UserRole.role_id == RolePermission.role_id)
            .where(UserRole.user_id == user_id)
        )
        return set(result.scalars().all())

    async def check_permission(self, user_id: uuid.UUID, permission_code: str) -> bool:
        user_permissions = await self._get_user_permission_codes(user_id)
        return permission_code in user_permissions

    async def check_permissions_many(self, user_id: uuid.UUID, permission_codes: list[str]) -> dict[str, bool]:
        user_permissions = await self._get_user_permission_codes(user_id)
        return {code: (code in user_permissions) for code in permission_codes}