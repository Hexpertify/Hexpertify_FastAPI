import uuid
from pydantic import BaseModel, ConfigDict


class RolePermissionAssign(BaseModel):
    permission_id: uuid.UUID


class RolePermissionBulkAssign(BaseModel):
    permission_ids: list[uuid.UUID]


class PermissionOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: uuid.UUID
    code: str
    name: str