from fastapi import APIRouter
from datetime import datetime
import psutil
import os

from schemas import HealthCheck
from config import settings

router = APIRouter(prefix="/health", tags=["health"])


@router.get("/", response_model=HealthCheck)
def health_check():
    """Basic health check endpoint"""
    return HealthCheck(
        status="healthy",
        timestamp=datetime.utcnow(),
        version=settings.VERSION
    )


@router.get("/detailed")
def detailed_health_check():
    """Detailed health check with system metrics"""
    # Get system metrics
    cpu_percent = psutil.cpu_percent(interval=0.1)
    memory = psutil.virtual_memory()
    disk = psutil.disk_usage('/')
    
    # Get database connection status (simplified)
    db_status = "unknown"
    try:
        # In a real implementation, you would test the database connection
        db_status = "connected"
    except Exception:
        db_status = "disconnected"
    
    return {
        "status": "healthy",
        "timestamp": datetime.utcnow().isoformat(),
        "version": settings.VERSION,
        "system": {
            "cpu_percent": cpu_percent,
            "memory_percent": memory.percent,
            "disk_percent": disk.percent,
            "process_id": os.getpid()
        },
        "services": {
            "database": db_status,
            "api": "running"
        }
    }


@router.get("/ready")
def readiness_probe():
    """Kubernetes readiness probe endpoint"""
    # Check if application is ready to receive traffic
    # In a real implementation, check database connections, external services, etc.
    return {
        "status": "ready",
        "timestamp": datetime.utcnow().isoformat()
    }


@router.get("/live")
def liveness_probe():
    """Kubernetes liveness probe endpoint"""
    # Check if application is still alive
    return {
        "status": "alive",
        "timestamp": datetime.utcnow().isoformat()
    }
