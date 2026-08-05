from fastapi import Depends, HTTPException, status
from app.core.dependencies import get_current_user
from app.repositories.user_role_repository import UserRoleRepository
from app.core.database import get_db
from sqlalchemy.ext.asyncio import AsyncSession


def require_roles(*allowed_role_codes: str):
    async def role_checker(
        current_user=Depends(get_current_user),
        db: AsyncSession = Depends(get_db),
    ):
        repo = UserRoleRepository(db)
        user_roles = await repo.get_roles_for_user(current_user.id)
        user_role_codes = {role.code for role in user_roles}

        if not user_role_codes.intersection(allowed_role_codes):
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="You do not have permission to access this resource",
            )
        return current_user

    return role_checker