from pydantic import BaseModel


class PermissionCheckRequest(BaseModel):
    user_id: str
    permission_code: str


class PermissionCheckManyRequest(BaseModel):
    user_id: str
    permission_codes: list[str]


class PermissionCheckResponse(BaseModel):
    has_permission: bool


class PermissionCheckManyResponse(BaseModel):
    results: dict[str, bool]