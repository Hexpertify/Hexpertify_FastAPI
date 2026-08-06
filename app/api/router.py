from fastapi import APIRouter
from app.api.v1 import roles, users, permissions, menus, user_roles, role_permissions, role_menus, auth, admin, permission_check

api_router = APIRouter()
api_router.include_router(auth.router)
api_router.include_router(admin.router)
api_router.include_router(roles.router)
api_router.include_router(users.router)
api_router.include_router(permissions.router)
api_router.include_router(menus.router)
api_router.include_router(user_roles.router)
api_router.include_router(role_permissions.router)
api_router.include_router(role_menus.router)
api_router.include_router(permission_check.router)