import uuid
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from app.core.database import get_db
from app.repositories.audit_log_repository import AuditLogRepository
from app.schemas.audit_log import AuditLogOut
from app.permissions.decorators import require_roles

router = APIRouter(prefix="/audit-logs", tags=["Audit Logs"])


@router.get("/", response_model=list[AuditLogOut])
async def list_audit_logs(
    db: AsyncSession = Depends(get_db),
    current_user=Depends(require_roles("ADMIN", "SUPER_ADMIN")),
):
    repo = AuditLogRepository(db)
    return await repo.get_all()


@router.get("/{log_id}", response_model=AuditLogOut)
async def get_audit_log(
    log_id: uuid.UUID,
    db: AsyncSession = Depends(get_db),
    current_user=Depends(require_roles("ADMIN", "SUPER_ADMIN")),
):
    repo = AuditLogRepository(db)
    log = await repo.get_by_id(log_id)
    if not log:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Audit log not found")
    return log