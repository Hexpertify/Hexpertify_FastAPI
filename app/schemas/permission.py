import uuid
from datetime import datetime
from pydantic import BaseModel, ConfigDict


class PermissionBase(BaseModel):
    code: str
    name: str
    description: str | None = None
    resource: str | None = None
    action: str | None = None


class PermissionCreate(PermissionBase):
    pass


class PermissionUpdate(BaseModel):
    code: str | None = None
    name: str | None = None
    description: str | None = None
    resource: str | None = None
    action: str | None = None
    is_active: bool | None = None


class PermissionOut(PermissionBase):
    model_config = ConfigDict(from_attributes=True)

    id: uuid.UUID
    is_active: bool
    created_at: datetime
    updated_at: datetime