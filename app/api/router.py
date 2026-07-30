from fastapi import APIRouter
from app.api.v1 import roles

api_router = APIRouter()
api_router.include_router(roles.router)