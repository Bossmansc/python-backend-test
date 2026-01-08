from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from contextlib import asynccontextmanager
from datetime import datetime
import os
from database import engine, Base
from config import settings
from routers import auth, projects, deployments, users, health
from routers import admin as admin_router
from routers.cache import router as cache_router
from routers.analytics import router as analytics_router
from middleware.rate_limiter import rate_limit_middleware
from middleware.request_logger import request_logger_middleware, error_handler_middleware
from utils.logger import logger, setup_logger
from schemas import HealthCheck

@asynccontextmanager
async def lifespan(app: FastAPI):
    # Startup
    logger.info(f"🚀 {settings.APP_NAME} v{settings.VERSION} starting up...")
    logger.info(f"🌍 Environment: {os.getenv('ENVIRONMENT', 'development')}")
    logger.info(f"📡 Database: {settings.DATABASE_URL.split('@')[-1] if '@' in settings.DATABASE_URL else settings.DATABASE_URL}")
    
    # Create tables
    Base.metadata.create_all(bind=engine)
    logger.info("✅ Database tables created/verified")
    
    yield
    
    # Shutdown
    logger.info("👋 Shutting down...")

app = FastAPI(
    title=settings.APP_NAME,
    version=settings.VERSION,
    description="""
    API Gateway for Cloud Deployment Platform
    """,
    docs_url="/docs",
    redoc_url="/redoc",
    lifespan=lifespan,
    contact={
        "name": "Cloud Deploy Support",
        "email": "support@clouddeploy.example.com",
        "url": "https://clouddeploy.example.com/support"
    },
    license_info={
        "name": "MIT",
        "url": "https://opensource.org/licenses/MIT",
    },
    terms_of_service="https://clouddeploy.example.com/terms",
    servers=[
        {"url": "http://localhost:8000", "description": "Development server"},
        {"url": "https://api.clouddeploy.example.com", "description": "Production server"}
    ]
)

# Configure CORS
# Updated to allow all origins in sandbox/dev to prevent "Is backend running?" errors
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"], 
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Add rate limiting middleware
app.middleware("http")(rate_limit_middleware)

# Add request logging middleware
app.middleware("http")(request_logger_middleware)
app.middleware("http")(error_handler_middleware)

# Include routers
app.include_router(auth.router)
app.include_router(projects.router)
app.include_router(deployments.router)
app.include_router(users.router)
app.include_router(health.router)
app.include_router(admin_router.router)
app.include_router(cache_router)
app.include_router(analytics_router)

@app.get("/", tags=["root"])
def read_root():
    return {
        "message": f"Welcome to {settings.APP_NAME}",
        "version": settings.VERSION,
        "description": "Cloud Deployment Platform API Gateway",
        "endpoints": {
            "authentication": "/auth",
            "projects": "/projects",
            "deployments": "/deployments",
            "users": "/users",
            "health": "/health",
            "analytics": "/analytics",
            "cache": "/cache (admin only)",
            "admin": "/admin (admin only)",
            "documentation": "/docs"
        },
        "timestamp": datetime.utcnow().isoformat(),
        "status": "operational"
    }

@app.get("/info")
def get_api_info():
    """Get API information"""
    return {
        "name": settings.APP_NAME,
        "version": settings.VERSION,
        "environment": os.getenv("ENVIRONMENT", "development"),
        "uptime": "0s",  # Would need to track startup time
        "support": {
            "email": "support@clouddeploy.example.com",
            "documentation": "https://docs.clouddeploy.example.com",
            "status": "https://status.clouddeploy.example.com"
        },
        "limits": {
            "rate_limit": "60 requests per minute",
            "max_projects_per_user": 100,
            "max_deployments_per_project": 1000
        }
    }

@app.get("/openapi.json", include_in_schema=False)
def get_openapi():
    """Get OpenAPI schema"""
    return app.openapi()

if __name__ == "__main__":
    import uvicorn
    # Get port from environment variable (for Render deployment)
    port = int(os.getenv("PORT", 8000))
    uvicorn.run(
        "main_complete:app",
        host="0.0.0.0",
        port=port,
        reload=True if os.getenv("ENVIRONMENT") == "development" else False,
        log_config=None
    )
