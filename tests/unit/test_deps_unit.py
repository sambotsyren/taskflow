# tests/unit/test_deps_unit.py
import pytest
from fastapi import HTTPException

from app.api import deps
from app.models.user import User


def test_get_current_user_ok(db_session, monkeypatch):
    u = User(email="u@test.com", password_hash="x", role="user", is_active=True)
    db_session.add(u)
    db_session.commit()
    db_session.refresh(u)

    monkeypatch.setattr(deps, "decode_token", lambda _t: {"sub": str(u.id), "type": "access"})

    current = deps.get_current_user(db=db_session, token="fake-token")
    assert current.id == u.id
    assert current.email == "u@test.com"


def test_get_current_user_rejects_refresh_token(db_session, monkeypatch):
    u = User(email="u2@test.com", password_hash="x", role="user", is_active=True)
    db_session.add(u)
    db_session.commit()
    db_session.refresh(u)

    monkeypatch.setattr(deps, "decode_token", lambda _t: {"sub": str(u.id), "type": "refresh"})

    with pytest.raises(HTTPException) as e:
        deps.get_current_user(db=db_session, token="fake-token")
    assert e.value.status_code == 401


def test_get_current_user_inactive_forbidden(db_session, monkeypatch):
    u = User(email="u3@test.com", password_hash="x", role="user", is_active=False)
    db_session.add(u)
    db_session.commit()
    db_session.refresh(u)

    monkeypatch.setattr(deps, "decode_token", lambda _t: {"sub": str(u.id), "type": "access"})

    with pytest.raises(HTTPException) as e:
        deps.get_current_user(db=db_session, token="fake-token")
    assert e.value.status_code == 401


def test_require_admin_allows_admin():
    admin = User(email="a@test.com", password_hash="x", role="admin", is_active=True)
    assert deps.require_admin(current_user=admin) is admin


def test_require_admin_forbids_non_admin():
    u = User(email="u@test.com", password_hash="x", role="user", is_active=True)

    with pytest.raises(HTTPException) as e:
        deps.require_admin(current_user=u)
    assert e.value.status_code == 403
