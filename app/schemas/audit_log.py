import uuid
from datetime import datetime
from pydantic import BaseModel
from pydantic import BaseModel, ConfigDict


class AuditLogOut(BaseModel):
    id: uuid.UUID
    actor_id: uuid.UUID | None
    action: str
    resource_type: str
    resource_id: str | None
    details: dict | None
    created_at: datetime

model_config = ConfigDict(from_attributes=True)