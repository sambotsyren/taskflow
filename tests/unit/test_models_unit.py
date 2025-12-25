# tests/unit/test_models_unit.py
import pytest
from sqlalchemy.exc import IntegrityError
from sqlalchemy import select, func

from app.models.user import User
from app.models.project import Project
from app.models.task import Task, TaskStatus


def _count(db, model):
    return db.scalar(select(func.count()).select_from(model))


def test_user_email_is_unique(db_session):
    u1 = User(email="dup@test.com", password_hash="x", role="user", is_active=True)
    db_session.add(u1)
    db_session.commit()

    u2 = User(email="dup@test.com", password_hash="y", role="user", is_active=True)
    db_session.add(u2)

    with pytest.raises(IntegrityError):
        db_session.commit()


def test_cascade_delete_user_deletes_projects_and_tasks(db_session):
    u = User(email="owner@test.com", password_hash="x", role="user", is_active=True)
    p = Project(title="My Project")
    p.owner = u

    t1 = Task(title="T1")
    t2 = Task(title="T2")
    t1.project = p
    t2.project = p

    db_session.add_all([u, p, t1, t2])
    db_session.commit()

    assert _count(db_session, User) == 1
    assert _count(db_session, Project) == 1
    assert _count(db_session, Task) == 2

    db_session.delete(u)
    db_session.commit()

    assert _count(db_session, User) == 0
    assert _count(db_session, Project) == 0
    assert _count(db_session, Task) == 0


def test_task_defaults(db_session):
    u = User(email="u@test.com", password_hash="x", role="user", is_active=True)
    p = Project(title="P")
    p.owner = u

    t = Task(title="Hello")
    t.project = p

    db_session.add_all([u, p, t])
    db_session.commit()
    db_session.refresh(t)

    assert t.status == TaskStatus.todo
    assert t.priority == 3
    assert t.due_date is None
