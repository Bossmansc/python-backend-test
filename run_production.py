#!/usr/bin/env python3
"""
Production runner script with enhanced features
"""
import os
import sys
import uvicorn
from dotenv import load_dotenv
import logging
from utils.logger import setup_logger

# Load environment variables
load_dotenv()

# Setup logger
logger = setup_logger()

def check_environment():
    """Check if required environment variables are set"""
    required_vars = [
        "DATABASE_URL",
        "SECRET_KEY",
        "FRONTEND_URL",
    ]
    
    missing_vars = []
    for var in required_vars:
        if not os.getenv(var):
            missing_vars.append(var)
    
    if missing_vars:
        logger.error(f"Missing required environment variables: {', '.join(missing_vars)}")
        logger.error("Please set these variables in your .env file")
        return False
    
    return True

def run_migrations():
    """Run database migrations if needed"""
    if os.getenv("RUN_MIGRATIONS", "false").lower() == "true":
        logger.info("🔄 Running database migrations...")
        try:
            os.system("alembic upgrade head")
            logger.info("✅ Database migrations completed")
        except Exception as e:
            logger.error(f"❌ Database migrations failed: {e}")
            return False
    return True

def main():
    """Main application runner"""
    # Get configuration from environment
    host = os.getenv("HOST", "0.0.0.0")
    port = int(os.getenv("PORT", 8000))
    reload = os.getenv("ENVIRONMENT", "production") == "development"
    workers = int(os.getenv("WORKERS", 4))
    log_level = os.getenv("LOG_LEVEL", "info")
    
    # Print startup banner
    print("=" * 60)
    print(f"🚀 {os.getenv('APP_NAME', 'Cloud Deploy API Gateway')}")
    print("=" * 60)
    print(f"📡 Host: {host}")
    print(f"🔌 Port: {port}")
    print(f"🔄 Reload: {reload}")
    print(f"👷 Workers: {workers}")
    print(f"🌍 Environment: {os.getenv('ENVIRONMENT', 'production')}")
    print(f"📊 Log Level: {log_level}")
    print(f"🗄️  Database: {os.getenv('DATABASE_URL', 'Not configured').split('@')[-1] if '@' in os.getenv('DATABASE_URL', '') else 'Not configured'}")
    print(f"💾 Redis: {os.getenv('REDIS_URL', 'Not configured')}")
    print("=" * 60)
    
    # Check environment
    if not check_environment():
        sys.exit(1)
    
    # Run migrations
    if not run_migrations():
        sys.exit(1)
    
    # Log startup
    logger.info(f"Starting {os.getenv('APP_NAME', 'Cloud Deploy API Gateway')}")
    logger.info(f"Environment: {os.getenv('ENVIRONMENT', 'production')}")
    logger.info(f"Host: {host}:{port}")
    
    # Run the application
    try:
        uvicorn.run(
            "main_complete:app",
            host=host,
            port=port,
            reload=reload,
            workers=workers if not reload else 1,
            log_level=log_level,
            access_log=True,
            log_config=None
        )
    except KeyboardInterrupt:
        logger.info("Shutting down gracefully...")
    except Exception as e:
        logger.error(f"Application failed to start: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main()
