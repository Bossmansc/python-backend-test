import logging
import sys
from logging.handlers import RotatingFileHandler
from datetime import datetime
import os


def setup_logger(name: str = "cloud_deploy_api"):
    """Setup application logger with file and console handlers"""
    
    # Create logs directory if it doesn't exist
    logs_dir = "logs"
    if not os.path.exists(logs_dir):
        os.makedirs(logs_dir)
    
    # Create logger
    logger = logging.getLogger(name)
    logger.setLevel(logging.INFO)
    
    # Remove existing handlers to avoid duplicates
    logger.handlers.clear()
    
    # Console handler
    console_handler = logging.StreamHandler(sys.stdout)
    console_handler.setLevel(logging.INFO)
    
    # File handler with rotation
    file_handler = RotatingFileHandler(
        filename=f"{logs_dir}/app.log",
        maxBytes=10 * 1024 * 1024,  # 10MB
        backupCount=5
    )
    file_handler.setLevel(logging.INFO)
    
    # Formatter
    formatter = logging.Formatter(
        '%(asctime)s - %(name)s - %(levelname)s - %(message)s',
        datefmt='%Y-%m-%d %H:%M:%S'
    )
    
    console_handler.setFormatter(formatter)
    file_handler.setFormatter(formatter)
    
    # Add handlers
    logger.addHandler(console_handler)
    logger.addHandler(file_handler)
    
    return logger


# Global logger instance
logger = setup_logger()


class RequestLogger:
    """Middleware for logging HTTP requests"""
    
    @staticmethod
    async def log_request(request, call_next):
        """Log incoming requests"""
        start_time = datetime.utcnow()
        
        # Log request
        logger.info(f"Request: {request.method} {request.url.path} - Client: {request.client.host}")
        
        # Process request
        response = await call_next(request)
        
        # Calculate processing time
        process_time = (datetime.utcnow() - start_time).total_seconds() * 1000
        
        # Log response
        logger.info(
            f"Response: {request.method} {request.url.path} - "
            f"Status: {response.status_code} - "
            f"Time: {process_time:.2f}ms"
        )
        
        # Add custom header
        response.headers["X-Process-Time"] = str(process_time)
        
        return response


def log_deployment_event(deployment_id: int, event: str, details: dict = None):
    """Log deployment events"""
    log_message = f"Deployment {deployment_id}: {event}"
    if details:
        log_message += f" - Details: {details}"
    logger.info(log_message)


def log_user_event(user_id: int, event: str, details: dict = None):
    """Log user events"""
    log_message = f"User {user_id}: {event}"
    if details:
        log_message += f" - Details: {details}"
    logger.info(log_message)


def log_error(error: Exception, context: str = ""):
    """Log errors with context"""
    error_message = f"Error: {type(error).__name__}: {str(error)}"
    if context:
        error_message = f"{context} - {error_message}"
    logger.error(error_message, exc_info=True)


def log_system_event(event: str, details: dict = None):
    """Log system events"""
    log_message = f"System: {event}"
    if details:
        log_message += f" - Details: {details}"
    logger.info(log_message)
