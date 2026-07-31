from fastapi import APIRouter
from app.api.v1 import roles, users, permissions

api_router = APIRouter()
api_router.include_router(roles.router)
api_router.include_router(users.router)
api_router.include_router(permissions.router)