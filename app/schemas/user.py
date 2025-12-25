from pydantic import BaseModel, EmailStr, Field

class UserCreate(BaseModel):
    email: EmailStr
    password: str = Field(min_length=6, max_length=72)

class UserOut(BaseModel):
    id: int
    email: EmailStr
    role: str
    is_active: bool

class UserAdminUpdate(BaseModel):
    role: str | None = None   # "user" | "admin"
    is_active: bool | None = None
