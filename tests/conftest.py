import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import StaticPool

from app.app_factory import create_app
from app.db.base import Base
from app.core.security import hash_password
from app.models.user import User


@pytest.fixture()
def test_engine():
    engine = create_engine(
        "sqlite+pysqlite:///:memory:",
        connect_args={"check_same_thread": False},
        poolclass=StaticPool,  # <-- фикс: одно соединение на все
    )
    return engine


@pytest.fixture()
def client(test_engine):
    app = create_app(engine_override=test_engine)
    with TestClient(app) as c:
        yield c


@pytest.fixture()
def db_session(test_engine):
    SessionLocal = sessionmaker(bind=test_engine, autoflush=False, autocommit=False)
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


def register_user(client: TestClient, email: str, password: str):
    return client.post("/auth/register", json={"email": email, "password": password})


def login_user(client: TestClient, email: str, password: str):
    # OAuth2PasswordRequestForm -> form-data
    return client.post("/auth/login", data={"username": email, "password": password})


def auth_headers(access_token: str):
    return {"Authorization": f"Bearer {access_token}"}


@pytest.fixture()
def admin_user(db_session):
    admin = User(
        email="admin@test.com",
        password_hash=hash_password("adminpass"),
        role="admin",
        is_active=True,
    )
    db_session.add(admin)
    db_session.commit()
    db_session.refresh(admin)
    return admin
