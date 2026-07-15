"""FastAPI app entry point."""
import logging

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse

from app.api import (
    admin_router, ai_router, auth_router, bills_router,
    complaints_router, notices_router, reports_router, residents_router,
    societies_router, visitors_router, notifications_router,
)
from app.core.config import settings
from app.db.base import create_all

logging.basicConfig(level=logging.INFO,
                    format="%(asctime)s %(levelname)s %(name)s: %(message)s")

app = FastAPI(title=settings.APP_NAME, version=settings.APP_VERSION)


@app.on_event("startup")
def _startup() -> None:
    # In production, Alembic migrations handle schema. For dev/sandbox SQLite,
    # creating on startup is the simplest way to ensure tables exist.
    create_all()


app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.CORS_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.get("/health")
def health() -> dict:
    return {"status": "ok", "version": settings.APP_VERSION, "service": settings.APP_NAME}


# Mount API v1 routers
_PREFIX = settings.API_V1_PREFIX
app.include_router(auth_router, prefix=_PREFIX)
app.include_router(residents_router, prefix=_PREFIX)
app.include_router(societies_router, prefix=_PREFIX)
app.include_router(complaints_router, prefix=_PREFIX)
app.include_router(visitors_router, prefix=_PREFIX)
app.include_router(notifications_router, prefix=_PREFIX)
app.include_router(bills_router, prefix=_PREFIX)
app.include_router(notices_router, prefix=_PREFIX)
app.include_router(ai_router, prefix=_PREFIX)
app.include_router(reports_router, prefix=_PREFIX)
app.include_router(admin_router, prefix=_PREFIX)


@app.exception_handler(Exception)
def _unhandled(request, exc):  # pragma: no cover
    logging.exception("Unhandled error: %s", exc)
    return JSONResponse(status_code=500, content={"detail": "Internal server error"})
