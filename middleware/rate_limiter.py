from fastapi import HTTPException, Request
from fastapi.responses import JSONResponse
from datetime import datetime, timedelta
from typing import Dict, Tuple
import time


class RateLimiter:
    def __init__(self, requests_per_minute: int = 60):
        self.requests_per_minute = requests_per_minute
        self.requests: Dict[str, list] = {}
    
    def is_rate_limited(self, client_ip: str) -> Tuple[bool, int]:
        """Check if client is rate limited"""
        now = time.time()
        
        # Clean old requests (older than 1 minute)
        if client_ip in self.requests:
            self.requests[client_ip] = [
                req_time for req_time in self.requests[client_ip]
                if now - req_time < 60
            ]
        else:
            self.requests[client_ip] = []
        
        # Check if rate limited
        if len(self.requests[client_ip]) >= self.requests_per_minute:
            # Calculate retry after seconds
            oldest_request = min(self.requests[client_ip])
            retry_after = int(60 - (now - oldest_request))
            return True, retry_after
        
        # Add current request
        self.requests[client_ip].append(now)
        return False, 0


# Global rate limiter instance
rate_limiter = RateLimiter(requests_per_minute=60)


async def rate_limit_middleware(request: Request, call_next):
    """Middleware to rate limit requests"""
    # Skip rate limiting for health checks
    if request.url.path.startswith("/health"):
        return await call_next(request)
    
    client_ip = request.client.host if request.client else "unknown"
    
    is_limited, retry_after = rate_limiter.is_rate_limited(client_ip)
    
    if is_limited:
        return JSONResponse(
            status_code=429,
            content={
                "detail": f"Rate limit exceeded. Try again in {retry_after} seconds.",
                "retry_after": retry_after
            },
            headers={"Retry-After": str(retry_after)}
        )
    
    # Add rate limit headers to response
    response = await call_next(request)
    response.headers["X-RateLimit-Limit"] = str(rate_limiter.requests_per_minute)
    response.headers["X-RateLimit-Remaining"] = str(
        rate_limiter.requests_per_minute - len(rate_limiter.requests.get(client_ip, []))
    )
    
    return response
