import uuid
from datetime import datetime
from pydantic import BaseModel, ConfigDict


class RoleBase(BaseModel):
    code: str
    name: str
    description: str | None = None


class RoleCreate(RoleBase):
    pass


class RoleUpdate(BaseModel):
    code: str | None = None
    name: str | None = None
    description: str | None = None
    is_active: bool | None = None


class RoleOut(RoleBase):
    model_config = ConfigDict(from_attributes=True)

    id: uuid.UUID
    is_active: bool
    created_at: datetime
    updated_at: datetime