from fastapi import FastAPI
from .routers import predict, health, model_info
from .database import engine
from .models import Base


def create_app() -> FastAPI:
    app = FastAPI(title="ML API", version="0.1.0")

    Base.metadata.create_all(bind=engine)

    app.include_router(predict.router)
    app.include_router(health.router)
    app.include_router(model_info.router)

    return app


app = create_app()
