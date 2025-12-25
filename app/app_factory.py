from fastapi import FastAPI
from sqlalchemy.orm import sessionmaker
from sqlalchemy.engine import Engine
from app.api.router import api_router

from app.db.base import Base
from app.db.session import get_db

def create_app(*, engine_override: Engine | None = None) -> FastAPI:
    fastapi_app = FastAPI(title="TaskFlow API", version="1.0.0")
    fastapi_app.include_router(api_router)


    # middleware и роутеры — как у тебя

    if engine_override is not None:
        # ВАЖНО: так мы НЕ перетираем fastapi_app
        from app.models import user, project, task  # noqa: F401

        Base.metadata.create_all(bind=engine_override)

        TestingSessionLocal = sessionmaker(
            bind=engine_override,
            autoflush=False,
            autocommit=False,
        )

        def override_get_db():
            db = TestingSessionLocal()
            try:
                yield db
            finally:
                db.close()

        fastapi_app.dependency_overrides[get_db] = override_get_db

    return fastapi_app
