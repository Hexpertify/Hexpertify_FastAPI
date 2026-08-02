import uuid
from pydantic import BaseModel, ConfigDict


class UserRoleAssign(BaseModel):
    role_id: uuid.UUID


class UserRoleBulkAssign(BaseModel):
    role_ids: list[uuid.UUID]


class RoleOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: uuid.UUID
    code: str
    name: str