from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy import select
from sqlalchemy.orm import Session

from app.api.deps import get_db, get_current_user
from app.models.project import Project
from app.models.user import User
from app.schemas.project import ProjectCreate, ProjectUpdate, ProjectOut

router = APIRouter()

def _get_project_or_404(db: Session, project_id: int) -> Project:
    project = db.get(Project, project_id)
    if not project:
        raise HTTPException(status_code=404, detail="Project not found")
    return project

def _ensure_owner_or_admin(project: Project, user: User):
    if user.role != "admin" and project.owner_id != user.id:
        raise HTTPException(status_code=403, detail="Forbidden")

@router.get("", response_model=list[ProjectOut])
def list_projects(db: Session = Depends(get_db), user: User = Depends(get_current_user)):
    if user.role == "admin":
        return list(db.scalars(select(Project)).all())
    return list(db.scalars(select(Project).where(Project.owner_id == user.id)).all())

@router.post("", response_model=ProjectOut, status_code=201)
def create_project(payload: ProjectCreate, db: Session = Depends(get_db), user: User = Depends(get_current_user)):
    project = Project(owner_id=user.id, title=payload.title, description=payload.description)
    db.add(project)
    db.commit()
    db.refresh(project)
    return project

@router.get("/{project_id}", response_model=ProjectOut)
def get_project(project_id: int, db: Session = Depends(get_db), user: User = Depends(get_current_user)):
    project = _get_project_or_404(db, project_id)
    _ensure_owner_or_admin(project, user)
    return project

@router.patch("/{project_id}", response_model=ProjectOut)
def update_project(project_id: int, payload: ProjectUpdate, db: Session = Depends(get_db), user: User = Depends(get_current_user)):
    project = _get_project_or_404(db, project_id)
    _ensure_owner_or_admin(project, user)

    if payload.title is not None:
        project.title = payload.title
    if payload.description is not None:
        project.description = payload.description

    db.commit()
    db.refresh(project)
    return project

@router.delete("/{project_id}", status_code=204)
def delete_project(project_id: int, db: Session = Depends(get_db), user: User = Depends(get_current_user)):
    project = _get_project_or_404(db, project_id)
    _ensure_owner_or_admin(project, user)

    db.delete(project)
    db.commit()
    return None
