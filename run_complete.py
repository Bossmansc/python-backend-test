#!/usr/bin/env python3
"""
Complete application runner script with all features
"""
import os
import sys
import uvicorn
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

if __name__ == "__main__":
    # Get configuration from environment
    host = os.getenv("HOST", "0.0.0.0")
    port = int(os.getenv("PORT", 8000))
    reload = os.getenv("ENVIRONMENT", "development") == "development"
    workers = int(os.getenv("WORKERS", 1))
    log_level = os.getenv("LOG_LEVEL", "info")
    
    print("=" * 60)
    print(f"🚀 Starting {os.getenv('APP_NAME', 'Cloud Deploy API Gateway')}")
    print("=" * 60)
    print(f"📡 Host: {host}")
    print(f"🔌 Port: {port}")
    print(f"🔄 Reload: {reload}")
    print(f"👷 Workers: {workers}")
    print(f"🌍 Environment: {os.getenv('ENVIRONMENT', 'development')}")
    print(f"📊 Log Level: {log_level}")
    print(f"🗄️  Database: {os.getenv('DATABASE_URL', 'Not configured').split('@')[-1] if '@' in os.getenv('DATABASE_URL', '') else 'Not configured'}")
    print(f"💾 Redis: {os.getenv('REDIS_URL', 'Not configured')}")
    print("=" * 60)
    
    # Run migrations if needed
    if os.getenv("RUN_MIGRATIONS", "false").lower() == "true":
        print("🔄 Running database migrations...")
        os.system("alembic upgrade head")
    
    # Create logs directory
    logs_dir = "logs"
    if not os.path.exists(logs_dir):
        os.makedirs(logs_dir)
        print(f"📁 Created logs directory: {logs_dir}")
    
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
