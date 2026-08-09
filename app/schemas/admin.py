from pydantic import BaseModel, EmailStr


class CreateSuperAdminRequest(BaseModel):
    bootstrap_secret: str
    first_name: str
    last_name: str | None = None
    email: EmailStr
    password: str


class SeedRequest(BaseModel):
    bootstrap_secret: str