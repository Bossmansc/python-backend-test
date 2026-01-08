#!/usr/bin/env python3
"""
Setup script for Cloud Deploy API Gateway
"""
import os
import sys
from pathlib import Path

def setup_project():
    """Setup the project environment"""
    print("🔧 Setting up Cloud Deploy API Gateway...")
    
    # Check Python version
    if sys.version_info < (3, 9):
        print("❌ Python 3.9 or higher is required")
        sys.exit(1)
    
    # Create necessary directories
    directories = [
        "logs",
        "nginx/ssl",
        "nginx/logs",
        "postgres/backups",
        "kubernetes",
    ]
    
    for directory in directories:
        Path(directory).mkdir(parents=True, exist_ok=True)
        print(f"📁 Created directory: {directory}")
    
    # Copy .env.example to .env if it doesn't exist
    if not Path(".env").exists():
        if Path(".env.example").exists():
            with open(".env.example", "r") as src:
                with open(".env", "w") as dst:
                    dst.write(src.read())
            print("📄 Created .env file from .env.example")
            print("⚠️  Please edit .env with your configuration")
        else:
            print("⚠️  .env.example not found, creating basic .env")
            with open(".env", "w") as f:
                f.write("""# Database
DATABASE_URL=postgresql://user:password@localhost/cloud_deploy

# Redis
REDIS_URL=redis://localhost:6379/0

# JWT
SECRET_KEY=your-secret-key-change-in-production
ALGORITHM=HS256
ACCESS_TOKEN_EXPIRE_MINUTES=30
REFRESH_TOKEN_EXPIRE_DAYS=7

# CORS
FRONTEND_URL=http://localhost:3000

# App
APP_NAME=Cloud Deploy API Gateway
VERSION=1.0.0
ENVIRONMENT=development

# Server
HOST=0.0.0.0
PORT=8000
WORKERS=4
LOG_LEVEL=info
RUN_MIGRATIONS=false
""")
    
    # Install dependencies
    print("\n📦 Installing dependencies...")
    os.system("pip install -r requirements_complete.txt")
    
    # Run database migrations
    print("\n🔄 Running database migrations...")
    os.system("python create_tables.py")
    
    # Setup pre-commit hooks
    if Path(".pre-commit-config.yaml").exists():
        print("\n🔧 Setting up pre-commit hooks...")
        os.system("pre-commit install")
    
    print("\n✅ Setup complete!")
    print("\n🚀 To start the application:")
    print("   Development: make dev")
    print("   Production:  make prod")
    print("   Docker:      make docker-up")
    print("\n📚 For more commands: make help")

if __name__ == "__main__":
    setup_project()
