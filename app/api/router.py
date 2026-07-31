from fastapi import APIRouter
from app.api.v1 import roles, users, permissions, menus, user_roles

api_router = APIRouter()
api_router.include_router(roles.router)
api_router.include_router(users.router)
api_router.include_router(permissions.router)
api_router.include_router(menus.router)
api_router.include_router(user_roles.router)