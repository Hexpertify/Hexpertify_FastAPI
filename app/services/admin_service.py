import uuid
from fastapi import HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from app.core.config import settings
from app.repositories.role_repository import RoleRepository
from app.repositories.permission_repository import PermissionRepository
from app.repositories.menu_repository import MenuRepository
from app.repositories.user_repository import UserRepository
from app.repositories.user_role_repository import UserRoleRepository
from app.schemas.role import RoleCreate
from app.schemas.permission import PermissionCreate
from app.schemas.menu import MenuCreate
from app.schemas.user import UserCreate


DEFAULT_ROLES = [
    {"code": "SUPER_ADMIN", "name": "Super Admin", "description": "Full system access"},
    {"code": "ADMIN", "name": "Admin", "description": "Administrative access"},
    {"code": "MANAGER", "name": "Manager", "description": "Department manager"},
    {"code": "EMPLOYEE", "name": "Employee", "description": "Standard employee"},
]

DEFAULT_PERMISSIONS = [
    {"code": "user.create", "name": "Create User", "resource": "user", "action": "create"},
    {"code": "user.read", "name": "View User", "resource": "user", "action": "read"},
    {"code": "user.update", "name": "Update User", "resource": "user", "action": "update"},
    {"code": "user.delete", "name": "Delete User", "resource": "user", "action": "delete"},
    {"code": "role.create", "name": "Create Role", "resource": "role", "action": "create"},
    {"code": "role.read", "name": "View Role", "resource": "role", "action": "read"},
    {"code": "role.update", "name": "Update Role", "resource": "role", "action": "update"},
    {"code": "role.delete", "name": "Delete Role", "resource": "role", "action": "delete"},
    {"code": "permission.create", "name": "Create Permission", "resource": "permission", "action": "create"},
    {"code": "permission.read", "name": "View Permission", "resource": "permission", "action": "read"},
    {"code": "permission.update", "name": "Update Permission", "resource": "permission", "action": "update"},
    {"code": "permission.delete", "name": "Delete Permission", "resource": "permission", "action": "delete"},
    {"code": "menu.create", "name": "Create Menu", "resource": "menu", "action": "create"},
    {"code": "menu.read", "name": "View Menu", "resource": "menu", "action": "read"},
    {"code": "menu.update", "name": "Update Menu", "resource": "menu", "action": "update"},
    {"code": "menu.delete", "name": "Delete Menu", "resource": "menu", "action": "delete"},
]

DEFAULT_MENUS = [
    {"code": "DASHBOARD", "name": "Dashboard", "route": "/dashboard", "icon": "dashboard", "sort_order": 1},
    {"code": "ADMIN", "name": "Administration", "route": "/admin", "icon": "admin_panel_settings", "sort_order": 2},
]


class AdminService:
    def __init__(self, db: AsyncSession):
        self.db = db
        self.role_repo = RoleRepository(db)
        self.permission_repo = PermissionRepository(db)
        self.menu_repo = MenuRepository(db)
        self.user_repo = UserRepository(db)
        self.user_role_repo = UserRoleRepository(db)

    def _check_secret(self, provided_secret: str):
        if provided_secret != settings.ADMIN_BOOTSTRAP_SECRET:
            raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Invalid bootstrap secret")

    async def seed_defaults(self, provided_secret: str):
        self._check_secret(provided_secret)

        created = {"roles": 0, "permissions": 0, "menus": 0}

        for role_data in DEFAULT_ROLES:
            existing = await self.role_repo.get_by_code(role_data["code"])
            if not existing:
                await self.role_repo.create(RoleCreate(**role_data))
                created["roles"] += 1

        for perm_data in DEFAULT_PERMISSIONS:
            existing = await self.permission_repo.get_by_code(perm_data["code"])
            if not existing:
                await self.permission_repo.create(PermissionCreate(**perm_data))
                created["permissions"] += 1

        for menu_data in DEFAULT_MENUS:
            existing = await self.menu_repo.get_by_code(menu_data["code"])
            if not existing:
                await self.menu_repo.create(MenuCreate(**menu_data))
                created["menus"] += 1

        return created

    async def create_super_admin(self, provided_secret: str, user_data: dict):
        self._check_secret(provided_secret)

        existing_user = await self.user_repo.get_by_email(user_data["email"])
        if existing_user:
            raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail="Email already registered")

        super_admin_role = await self.role_repo.get_by_code("SUPER_ADMIN")
        if not super_admin_role:
            super_admin_role = await self.role_repo.create(
                RoleCreate(code="SUPER_ADMIN", name="Super Admin", description="Full system access")
            )

        new_user = await self.user_repo.create(UserCreate(**user_data))
        await self.user_role_repo.add_role(new_user.id, super_admin_role.id)

        return new_user

    async def reset_permissions(self, provided_secret: str):
        self._check_secret(provided_secret)
        created = 0
        for perm_data in DEFAULT_PERMISSIONS:
            existing = await self.permission_repo.get_by_code(perm_data["code"])
            if not existing:
                await self.permission_repo.create(PermissionCreate(**perm_data))
                created += 1
        return {"permissions_created": created}

    async def sync_menus(self, provided_secret: str):
        self._check_secret(provided_secret)
        created = 0
        for menu_data in DEFAULT_MENUS:
            existing = await self.menu_repo.get_by_code(menu_data["code"])
            if not existing:
                await self.menu_repo.create(MenuCreate(**menu_data))
                created += 1
        return {"menus_created": created}