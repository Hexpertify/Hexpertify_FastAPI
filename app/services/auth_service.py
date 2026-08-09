import uuid
from datetime import datetime, timedelta, timezone
from fastapi import HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from app.repositories.auth_repository import AuthRepository
from app.repositories.user_repository import UserRepository
from app.core.config import settings
from app.utils.hashing import verify_password, hash_password
from app.utils.jwt import create_access_token, create_refresh_token_value, decode_access_token
from app.models.password_reset_token import PasswordResetToken
from app.utils.jwt import create_refresh_token_value as create_random_token


class AuthService:
    def __init__(self, db: AsyncSession):
        self.auth_repo = AuthRepository(db)
        self.user_repo = UserRepository(db)

    async def login(self, email: str, password: str):
        user = await self.user_repo.get_by_email(email)
        if not user or not verify_password(password, user.password_hash):
            raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid email or password")
        if not user.is_active:
            raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Account is inactive")

        access_token = create_access_token(user.id)
        refresh_token_value = create_refresh_token_value()
        expires_at = datetime.now(timezone.utc) + timedelta(days=settings.REFRESH_TOKEN_EXPIRE_DAYS)
        await self.auth_repo.store_refresh_token(user.id, refresh_token_value, expires_at)

        return {"access_token": access_token, "refresh_token": refresh_token_value, "token_type": "bearer"}

    async def refresh(self, refresh_token_value: str):
        stored_token = await self.auth_repo.get_refresh_token(refresh_token_value)
        if not stored_token or stored_token.is_revoked:
            raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid refresh token")

        expires_at = stored_token.expires_at
        if expires_at.tzinfo is None:
            expires_at = expires_at.replace(tzinfo=timezone.utc)
        if expires_at < datetime.now(timezone.utc):
            raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Refresh token expired")

        await self.auth_repo.revoke_refresh_token(stored_token)

        new_access_token = create_access_token(stored_token.user_id)
        new_refresh_token_value = create_refresh_token_value()
        new_expires_at = datetime.now(timezone.utc) + timedelta(days=settings.REFRESH_TOKEN_EXPIRE_DAYS)
        await self.auth_repo.store_refresh_token(stored_token.user_id, new_refresh_token_value, new_expires_at)

        return {"access_token": new_access_token, "refresh_token": new_refresh_token_value, "token_type": "bearer"}

    async def logout(self, refresh_token_value: str):
        stored_token = await self.auth_repo.get_refresh_token(refresh_token_value)
        if stored_token:
            await self.auth_repo.revoke_refresh_token(stored_token)

    async def get_current_user(self, token: str):
        payload = decode_access_token(token)
        if not payload:
            raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid or expired token")
        user_id = uuid.UUID(payload["sub"])
        user = await self.user_repo.get_by_id(user_id)
        if not user or not user.is_active:
            raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="User not found or inactive")
        return user

    async def change_password(self, user, old_password: str, new_password: str):
        if not verify_password(old_password, user.password_hash):
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Old password is incorrect")
        user.password_hash = hash_password(new_password)
        await self.auth_repo.db.commit()

    async def forgot_password(self, email: str):
        user = await self.user_repo.get_by_email(email)
        if not user:
            return  # don't reveal whether email exists

        token_value = create_random_token()
        expires_at = datetime.now(timezone.utc) + timedelta(hours=1)
        reset_token = PasswordResetToken(user_id=user.id, token=token_value, expires_at=expires_at)
        self.auth_repo.db.add(reset_token)
        await self.auth_repo.db.commit()

        # MOCK: in production, email this token. For now, log/return it.
        print(f"[MOCK EMAIL] Password reset token for {email}: {token_value}")
        return token_value

    async def reset_password(self, token: str, new_password: str):
        from sqlalchemy import select
        result = await self.auth_repo.db.execute(
            select(PasswordResetToken).where(PasswordResetToken.token == token)
        )
        reset_token = result.scalar_one_or_none()

        if not reset_token or reset_token.is_used:
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Invalid or used reset token")

        expires_at = reset_token.expires_at
        if expires_at.tzinfo is None:
            expires_at = expires_at.replace(tzinfo=timezone.utc)
        if expires_at < datetime.now(timezone.utc):
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Reset token expired")

        user = await self.user_repo.get_by_id(reset_token.user_id)
        user.password_hash = hash_password(new_password)
        reset_token.is_used = True
        await self.auth_repo.db.commit()