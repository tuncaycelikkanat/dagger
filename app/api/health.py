from fastapi import APIRouter

from app.core.config import get_settings

router = APIRouter(prefix="/health", tags=["Health"])


@router.get("")
def health_check() -> dict[str, str]:
    settings = get_settings()

    return {
        "status": "ok",
        "app": "DAGGER",
        "environment": settings.app_env
    }
