from app.app_factory import create_app
from app.db.session import engine
from app.db.base import Base  # чтобы модели подхватились

app = create_app()

@app.on_event("startup")
def on_startup():
    Base.metadata.create_all(bind=engine)
