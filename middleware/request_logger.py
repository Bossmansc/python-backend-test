from fastapi import Request
from datetime import datetime
import time
from utils.logger import logger


async def request_logger_middleware(request: Request, call_next):
    """Middleware to log all HTTP requests"""
    
    # Skip logging for health checks to reduce noise
    if request.url.path.startswith("/health"):
        return await call_next(request)
    
    # Get client IP
    client_ip = request.client.host if request.client else "unknown"
    
    # Start timer
    start_time = time.time()
    
    try:
        # Process request
        response = await call_next(request)
        
        # Calculate processing time
        process_time = (time.time() - start_time) * 1000
        
        # Log successful request
        logger.info(
            f"HTTP {request.method} {request.url.path} - "
            f"Status: {response.status_code} - "
            f"Client: {client_ip} - "
            f"Time: {process_time:.2f}ms"
        )
        
        # Add custom headers
        response.headers["X-Process-Time"] = f"{process_time:.2f}ms"
        response.headers["X-Request-ID"] = str(int(start_time * 1000))
        
        return response
        
    except Exception as e:
        # Log error
        process_time = (time.time() - start_time) * 1000
        logger.error(
            f"HTTP {request.method} {request.url.path} - "
            f"Error: {type(e).__name__} - "
            f"Client: {client_ip} - "
            f"Time: {process_time:.2f}ms"
        )
        raise


async def error_handler_middleware(request: Request, call_next):
    """Middleware to handle and log errors"""
    try:
        return await call_next(request)
    except Exception as e:
        from utils.logger import log_error
        log_error(e, f"Request: {request.method} {request.url.path}")
        raise
