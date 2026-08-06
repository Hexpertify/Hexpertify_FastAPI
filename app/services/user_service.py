import uuid
from fastapi import HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from app.repositories.user_repository import UserRepository
from app.schemas.user import UserCreate, UserUpdate


class UserService:
    def __init__(self, db: AsyncSession):
        self.repo = UserRepository(db)

    async def list_users(self):
        return await self.repo.get_all()

    async def get_user(self, user_id: uuid.UUID):
        user = await self.repo.get_by_id(user_id)
        if not user:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="User not found")
        return user

    async def create_user(self, data: UserCreate):
        existing = await self.repo.get_by_email(data.email)
        if existing:
            raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail="Email already registered")
        return await self.repo.create(data)

    async def update_user(self, user_id: uuid.UUID, data: UserUpdate):
        user = await self.get_user(user_id)
        if data.email and data.email != user.email:
            existing = await self.repo.get_by_email(data.email)
            if existing:
                raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail="Email already registered")
        return await self.repo.update(user, data)

    async def delete_user(self, user_id: uuid.UUID):
        user = await self.get_user(user_id)
        await self.repo.delete(user)

    async def update_status(self, user_id: uuid.UUID, is_active: bool):
        user = await self.get_user(user_id)
        user.is_active = is_active
        await self.repo.db.commit()
        await self.repo.db.refresh(user)
        return user