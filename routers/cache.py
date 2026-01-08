from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from database import get_db
from dependencies import get_current_user, require_admin
from utils.cache import cache
from models import User

router = APIRouter(prefix="/cache", tags=["cache"])

@router.get("/stats")
def get_cache_stats(
    admin: User = Depends(require_admin)
):
    """Get cache statistics (admin only)"""
    stats = cache.get_stats()
    return {
        "cache": stats,
        "timestamp": "2024-01-01T00:00:00Z"  # Would use actual timestamp
    }

@router.post("/clear")
def clear_cache(
    pattern: str = "*",
    admin: User = Depends(require_admin)
):
    """Clear cache entries (admin only)"""
    if pattern == "*":
        pattern = "*"
    cleared = cache.clear_pattern(pattern)
    return {
        "message": f"Cleared {cleared} cache entries matching pattern: {pattern}",
        "cleared_count": cleared
    }

@router.get("/keys")
def list_cache_keys(
    pattern: str = "*",
    limit: int = 100,
    admin: User = Depends(require_admin)
):
    """List cache keys (admin only)"""
    if not cache.is_connected():
        return {"keys": [], "count": 0}
        
    try:
        keys = cache.redis_client.keys(pattern)[:limit]
        return {
            "keys": [key.decode('utf-8') if isinstance(key, bytes) else key for key in keys],
            "count": len(keys),
            "pattern": pattern
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error listing keys: {str(e)}")

@router.delete("/key/{key}")
def delete_cache_key(
    key: str,
    admin: User = Depends(require_admin)
):
    """Delete specific cache key (admin only)"""
    deleted = cache.delete(key)
    return {
        "message": f"Cache key {'deleted' if deleted else 'not found'}",
        "key": key,
        "deleted": deleted
    }

@router.get("/health")
def cache_health_check():
    """Check cache health"""
    is_healthy = cache.is_connected()
    return {
        "status": "healthy" if is_healthy else "unhealthy",
        "connected": is_healthy,
        "service": "redis"
    }
