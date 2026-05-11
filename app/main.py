from fastapi import FastAPI

from app.api.documents import router as documents_router
from app.api.health import router as health_router
from app.api.queries import router as queries_router
from app.core.config import get_settings
from app.core.logging import configure_logging


def create_app() -> FastAPI:
    configure_logging()
    settings = get_settings()

    app = FastAPI(
        title=settings.app_name,
        debug=settings.app_debug,
        version="0.1.0",
        description="DAGGER backend API",
    )

    app.include_router(health_router, prefix=settings.api_prefix)
    app.include_router(documents_router, prefix=settings.api_prefix)
    app.include_router(queries_router, prefix=settings.api_prefix)
    return app


app = create_app()
