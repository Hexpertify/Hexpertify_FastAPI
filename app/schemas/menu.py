import uuid
from datetime import datetime
from pydantic import BaseModel, ConfigDict


class MenuBase(BaseModel):
    parent_id: uuid.UUID | None = None
    code: str
    name: str
    route: str | None = None
    icon: str | None = None
    sort_order: int = 0


class MenuCreate(MenuBase):
    pass


class MenuUpdate(BaseModel):
    parent_id: uuid.UUID | None = None
    code: str | None = None
    name: str | None = None
    route: str | None = None
    icon: str | None = None
    sort_order: int | None = None
    is_visible: bool | None = None
    is_active: bool | None = None


class MenuOut(MenuBase):
    model_config = ConfigDict(from_attributes=True)

    id: uuid.UUID
    is_visible: bool
    is_active: bool
    created_at: datetime
    updated_at: datetime


class MenuTreeOut(MenuOut):
    children: list["MenuTreeOut"] = []