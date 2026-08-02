import uuid
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from app.models.user import User
from app.schemas.user import UserCreate, UserUpdate
from app.utils.hashing import hash_password


class UserRepository:
    def __init__(self, db: AsyncSession):
        self.db = db

    async def get_all(self):
        result = await self.db.execute(select(User))
        return result.scalars().all()

    async def get_by_id(self, user_id: uuid.UUID):
        result = await self.db.execute(select(User).where(User.id == user_id))
        return result.scalar_one_or_none()

    async def get_by_email(self, email: str):
        result = await self.db.execute(select(User).where(User.email == email))
        return result.scalar_one_or_none()

    async def create(self, data: UserCreate):
        user_data = data.model_dump(exclude={"password"})
        user = User(**user_data, password_hash=hash_password(data.password))
        self.db.add(user)
        await self.db.commit()
        await self.db.refresh(user)
        return user

    async def update(self, user: User, data: UserUpdate):
        for field, value in data.model_dump(exclude_unset=True).items():
            setattr(user, field, value)
        await self.db.commit()
        await self.db.refresh(user)
        return user

    async def delete(self, user: User):
        await self.db.delete(user)
        await self.db.commit()