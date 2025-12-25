from datetime import date
from pydantic import BaseModel, Field
from app.models.task import TaskStatus

class TaskCreate(BaseModel):
    title: str = Field(min_length=1, max_length=160)
    description: str | None = None
    priority: int = Field(default=3, ge=1, le=5)
    due_date: date | None = None

class TaskUpdate(BaseModel):
    title: str | None = Field(default=None, min_length=1, max_length=160)
    description: str | None = None
    status: TaskStatus | None = None
    priority: int | None = Field(default=None, ge=1, le=5)
    due_date: date | None = None

class TaskOut(BaseModel):
    id: int
    project_id: int
    title: str
    description: str | None
    status: TaskStatus
    priority: int
    due_date: date | None
