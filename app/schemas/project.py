from pydantic import BaseModel, Field

class ProjectCreate(BaseModel):
    title: str = Field(min_length=1, max_length=120)
    description: str | None = None

class ProjectUpdate(BaseModel):
    title: str | None = Field(default=None, min_length=1, max_length=120)
    description: str | None = None

class ProjectOut(BaseModel):
    id: int
    owner_id: int
    title: str
    description: str | None
