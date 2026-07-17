"""Health check routes."""

from fastapi import APIRouter

from app.core.config import get_settings

router = APIRouter(tags=["health"])


@router.get("/health")
async def health_check() -> dict[str, str]:
    """Report the application's current health status."""

    settings = get_settings()
    return {
        "status": "healthy",
        "application": settings.app_name,
        "version": settings.app_version,
    }
