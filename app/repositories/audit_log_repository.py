import uuid
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from app.models.audit_log import AuditLog


class AuditLogRepository:
    def __init__(self, db: AsyncSession):
        self.db = db

    async def create(self, actor_id, action, resource_type, resource_id=None, details=None):
        log = AuditLog(
            actor_id=actor_id, action=action, resource_type=resource_type,
            resource_id=str(resource_id) if resource_id else None, details=details
        )
        self.db.add(log)
        await self.db.commit()
        return log

    async def get_all(self):
        result = await self.db.execute(select(AuditLog).order_by(AuditLog.created_at.desc()))
        return result.scalars().all()

    async def get_by_id(self, log_id: uuid.UUID):
        result = await self.db.execute(select(AuditLog).where(AuditLog.id == log_id))
        return result.scalar_one_or_none()