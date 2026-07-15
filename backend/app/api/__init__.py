"""API package."""
from .router import router as auth_router
from .residents import router as residents_router
from .societies import router as societies_router
from .complaints import router as complaints_router
from .visitors import router as visitors_router
from .notifications import router as notifications_router
from .bills import router as bills_router
from .notices import router as notices_router
from .ai import router as ai_router
from .reports import router as reports_router
from .admin import router as admin_router

__all__ = [
    "auth_router", "residents_router", "societies_router", "complaints_router",
    "visitors_router", "notifications_router", "bills_router", "notices_router", "ai_router",
    "reports_router", "admin_router",
]
