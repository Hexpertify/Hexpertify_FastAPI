import uuid
from pydantic import BaseModel, ConfigDict


class RoleMenuAssign(BaseModel):
    menu_id: uuid.UUID


class RoleMenuBulkAssign(BaseModel):
    menu_ids: list[uuid.UUID]


class MenuOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: uuid.UUID
    code: str
    name: str