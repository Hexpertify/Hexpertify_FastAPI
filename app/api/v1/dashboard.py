from fastapi import APIRouter, Depends
from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession
from app.core.database import get_db
from app.core.dependencies import get_current_user
from app.models.user import User
from app.models.role import Role
from app.models.permission import Permission
from app.models.menu import Menu

router = APIRouter(prefix="/dashboard", tags=["Dashboard"])


@router.get("/")
async def get_dashboard(current_user=Depends(get_current_user)):
    return {"message": f"Welcome, {current_user.first_name}", "user_id": str(current_user.id)}


@router.get("/stats")
async def get_stats(db: AsyncSession = Depends(get_db), current_user=Depends(get_current_user)):
    user_count = (await db.execute(select(func.count()).select_from(User))).scalar()
    role_count = (await db.execute(select(func.count()).select_from(Role))).scalar()
    permission_count = (await db.execute(select(func.count()).select_from(Permission))).scalar()
    menu_count = (await db.execute(select(func.count()).select_from(Menu))).scalar()
    active_users = (await db.execute(select(func.count()).select_from(User).where(User.is_active == True))).scalar()

    return {
        "total_users": user_count,
        "active_users": active_users,
        "total_roles": role_count,
        "total_permissions": permission_count,
        "total_menus": menu_count,
    }


@router.get("/widgets")
async def get_widgets(current_user=Depends(get_current_user)):
    return {"widgets": []}