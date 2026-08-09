from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession
from app.core.database import get_db
from app.services.admin_service import AdminService
from app.schemas.admin import CreateSuperAdminRequest, SeedRequest
from app.schemas.user import UserOut

router = APIRouter(prefix="/admin", tags=["Admin"])


@router.post("/seed", status_code=201)
async def seed(data: SeedRequest, db: AsyncSession = Depends(get_db)):
    service = AdminService(db)
    return await service.seed_defaults(data.bootstrap_secret)


@router.post("/create-super-admin", response_model=UserOut, status_code=201)
async def create_super_admin(data: CreateSuperAdminRequest, db: AsyncSession = Depends(get_db)):
    service = AdminService(db)
    user_data = {
        "first_name": data.first_name,
        "last_name": data.last_name,
        "email": data.email,
        "password": data.password,
    }
    return await service.create_super_admin(data.bootstrap_secret, user_data)


@router.post("/reset-permissions", status_code=201)
async def reset_permissions(data: SeedRequest, db: AsyncSession = Depends(get_db)):
    service = AdminService(db)
    return await service.reset_permissions(data.bootstrap_secret)


@router.post("/sync-menus", status_code=201)
async def sync_menus(data: SeedRequest, db: AsyncSession = Depends(get_db)):
    service = AdminService(db)
    return await service.sync_menus(data.bootstrap_secret)