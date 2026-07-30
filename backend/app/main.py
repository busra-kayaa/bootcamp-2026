"""FastAPI application entry point."""

try:
    from fastapi import FastAPI
except Exception:  # pragma: no cover - provide a lightweight stub when FastAPI isn't available (e.g., in editor)
    # This stub allows static analysis / editors to open the project without installed dependencies.
    class FastAPI:  # minimal runtime-safe placeholder
        def __init__(self, *args, **kwargs):
            pass

        def add_middleware(self, *args, **kwargs):
            pass

        def include_router(self, *args, **kwargs):
            pass
from fastapi.middleware.cors import CORSMiddleware

from app.api.routes.health_routes import router as health_router
# Eksik olan router'ları import ediyoruz
from app.api.routes.document_routes import router as document_router
from app.api.routes.analysis_routes import router as analysis_router
from app.api.routes.job_routes import router as job_router

from app.core.config import get_settings

settings = get_settings()

app = FastAPI(
    title=settings.app_name,
    version=settings.app_version,
    debug=settings.debug,
)

app.add_middleware(
    CORSMiddleware,
    # .env dosyasında FRONTEND_URL=http://localhost:5173 olduğundan emin ol
    allow_origins=[settings.frontend_url], 
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Router'ları ana uygulamaya bağlıyoruz
app.include_router(health_router)
app.include_router(document_router, prefix="/api/v1")
app.include_router(analysis_router, prefix="/api/v1")
app.include_router(job_router, prefix="/api/v1")