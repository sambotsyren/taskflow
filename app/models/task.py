import enum
from datetime import date

from sqlalchemy import String, ForeignKey, Integer, Date, Enum, Text
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.base import Base

class TaskStatus(str, enum.Enum):
    todo = "todo"
    in_progress = "in_progress"
    done = "done"

class Task(Base):
    __tablename__ = "tasks"

    id: Mapped[int] = mapped_column(primary_key=True)
    project_id: Mapped[int] = mapped_column(ForeignKey("projects.id"), index=True)

    title: Mapped[str] = mapped_column(String(160), nullable=False)
    description: Mapped[str | None] = mapped_column(Text, default=None)

    status: Mapped[TaskStatus] = mapped_column(Enum(TaskStatus), default=TaskStatus.todo, nullable=False)
    priority: Mapped[int] = mapped_column(Integer, default=3)  # 1..5
    due_date: Mapped[date | None] = mapped_column(Date, default=None)

    project = relationship("Project", back_populates="tasks")
