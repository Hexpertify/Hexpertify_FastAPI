from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession
from app.core.database import get_db
from app.core.dependencies import get_current_user
from app.services.user_service import UserService
from app.schemas.user import UserOut
from app.schemas.profile import ProfileUpdate
from app.schemas.user import UserUpdate

router = APIRouter(prefix="/profile", tags=["Profile"])


@router.get("/", response_model=UserOut)
async def get_profile(current_user=Depends(get_current_user)):
    return current_user


@router.put("/", response_model=UserOut)
async def update_profile(
    data: ProfileUpdate,
    current_user=Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    service = UserService(db)
    update_data = UserUpdate(**data.model_dump(exclude_unset=True))
    return await service.update_user(current_user.id, update_data)


@router.put("/avatar")
async def update_avatar(current_user=Depends(get_current_user)):
    return {"message": "Avatar upload not yet implemented — requires file storage setup"}