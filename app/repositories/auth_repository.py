import uuid
from datetime import datetime, timezone
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from app.models.refresh_token import RefreshToken


class AuthRepository:
    def __init__(self, db: AsyncSession):
        self.db = db

    async def store_refresh_token(self, user_id: uuid.UUID, token: str, expires_at: datetime):
        refresh_token = RefreshToken(user_id=user_id, token=token, expires_at=expires_at)
        self.db.add(refresh_token)
        await self.db.commit()
        return refresh_token

    async def get_refresh_token(self, token: str):
        result = await self.db.execute(select(RefreshToken).where(RefreshToken.token == token))
        return result.scalar_one_or_none()

    async def revoke_refresh_token(self, refresh_token: RefreshToken):
        refresh_token.is_revoked = True
        await self.db.commit()

    async def revoke_all_for_user(self, user_id: uuid.UUID):
        result = await self.db.execute(
            select(RefreshToken).where(RefreshToken.user_id == user_id, RefreshToken.is_revoked == False)
        )
        tokens = result.scalars().all()
        for token in tokens:
            token.is_revoked = True
        await self.db.commit()