# Routers package initialization
from .auth import router as auth_router
from .projects import router as projects_router
from .deployments import router as deployments_router
from .users import router as users_router
from .health import router as health_router
from .admin import router as admin_router
from .cache import router as cache_router
from .analytics import router as analytics_router

__all__ = [
    "auth_router",
    "projects_router",
    "deployments_router",
    "users_router",
    "health_router",
    "admin_router",
    "cache_router",
    "analytics_router"
]
