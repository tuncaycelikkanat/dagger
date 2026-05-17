from fastapi import APIRouter

from app.core.config import get_settings

router = APIRouter(prefix="/health", tags=["Health"])

# Simple health check endpoint to verify that the API is running and return basic app info.
@router.get("")
def health_check() -> dict[str, str]:
    settings = get_settings()

    return {
        "status": "ok",
        "app": settings.app_name,
        "environment": settings.app_env,
    }

# Health check endpoint for the LLM provider to verify connectivity and return provider info.
@router.get("/llm")
def llm_health_check() -> dict[str, str]:
    settings = get_settings()

    return {
        "status": "ok",
        "provider": settings.default_llm_provider,
        "default_model": settings.ollama_model_default,
        "architect_model": settings.ollama_model_architect,
        "auditor_model": settings.ollama_model_auditor,
        "coder_model": settings.ollama_model_coder,
    }
