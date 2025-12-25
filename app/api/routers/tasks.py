from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy import select
from sqlalchemy.orm import Session

from app.api.deps import get_db, get_current_user
from app.models.project import Project
from app.models.task import Task
from app.models.user import User
from app.schemas.task import TaskCreate, TaskUpdate, TaskOut

router = APIRouter()

def _get_project_or_404(db: Session, project_id: int) -> Project:
    project = db.get(Project, project_id)
    if not project:
        raise HTTPException(status_code=404, detail="Project not found")
    return project

def _ensure_owner_or_admin(owner_id: int, user: User):
    if user.role != "admin" and owner_id != user.id:
        raise HTTPException(status_code=403, detail="Forbidden")

@router.get("/projects/{project_id}/tasks", response_model=list[TaskOut])
def list_tasks(project_id: int, db: Session = Depends(get_db), user: User = Depends(get_current_user)):
    project = _get_project_or_404(db, project_id)
    _ensure_owner_or_admin(project.owner_id, user)

    return list(db.scalars(select(Task).where(Task.project_id == project_id)).all())

@router.post("/projects/{project_id}/tasks", response_model=TaskOut, status_code=201)
def create_task(project_id: int, payload: TaskCreate, db: Session = Depends(get_db), user: User = Depends(get_current_user)):
    project = _get_project_or_404(db, project_id)
    _ensure_owner_or_admin(project.owner_id, user)

    task = Task(
        project_id=project_id,
        title=payload.title,
        description=payload.description,
        priority=payload.priority,
        due_date=payload.due_date,
    )
    db.add(task)
    db.commit()
    db.refresh(task)
    return task

@router.patch("/tasks/{task_id}", response_model=TaskOut)
def update_task(task_id: int, payload: TaskUpdate, db: Session = Depends(get_db), user: User = Depends(get_current_user)):
    task = db.get(Task, task_id)
    if not task:
        raise HTTPException(status_code=404, detail="Task not found")

    project = db.get(Project, task.project_id)
    if not project:
        raise HTTPException(status_code=404, detail="Project not found")

    _ensure_owner_or_admin(project.owner_id, user)

    if payload.title is not None:
        task.title = payload.title
    if payload.description is not None:
        task.description = payload.description
    if payload.status is not None:
        task.status = payload.status
    if payload.priority is not None:
        task.priority = payload.priority
    if payload.due_date is not None:
        task.due_date = payload.due_date

    db.commit()
    db.refresh(task)
    return task

@router.delete("/tasks/{task_id}", status_code=204)
def delete_task(task_id: int, db: Session = Depends(get_db), user: User = Depends(get_current_user)):
    task = db.get(Task, task_id)
    if not task:
        raise HTTPException(status_code=404, detail="Task not found")

    project = db.get(Project, task.project_id)
    if not project:
        raise HTTPException(status_code=404, detail="Project not found")

    _ensure_owner_or_admin(project.owner_id, user)

    db.delete(task)
    db.commit()
    return None
