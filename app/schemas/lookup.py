import uuid
from pydantic import BaseModel


class LookupItem(BaseModel):
    id: uuid.UUID
    code: str
    name: str