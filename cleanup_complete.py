#!/usr/bin/env python3
"""
Complete cleanup script to remove duplicate/unused files
"""
import os
import shutil

# Files to keep (latest versions)
KEEP_FILES = [
    # Core application
    "main_complete.py",
    "run_complete.py",
    "requirements_complete.txt",
    "docker-compose.complete.yml",
    "Dockerfile.complete",
    "README_complete.md",
    "cleanup_complete.py",
    # Core modules
    "config.py",
    "database.py",
    "models.py",
    "schemas.py",
    "dependencies.py",
    # Routers
    "routers/auth.py",
    "routers/projects.py",
    "routers/deployments.py",
    "routers/users.py",
    "routers/health.py",
    "routers/admin.py",
    "routers/cache.py",
    "routers/analytics.py",
    # Middleware
    "middleware/rate_limiter.py",
    "middleware/request_logger.py",
    # Utils
    "utils/security.py",
    "utils/email_validator.py",
    "utils/logger.py",
    "utils/cache.py",
    "utils/validation.py",
    # Tests
    "test_api_complete.py",
    # Database migrations
    "alembic/env.py",
    "alembic.ini",
    "alembic/script.py.mako",
    "alembic/versions/001_initial_migration.py",
    "alembic/versions/002_add_admin_field.py",
    # Deployment
    "create_tables.py",
    ".env.example",
    "render.yaml",
    # Kubernetes
    "kubernetes/deployment.yaml",
    "kubernetes/postgres.yaml",
    "kubernetes/secrets.yaml",
    # Nginx
    "nginx/nginx.conf",
]

# Files to delete (duplicates/old versions)
DELETE_FILES = [
    "main.py",
    "main_updated.py",
    "main_final.py",
    "run.py",
    "run_final.py",
    "requirements.txt",
    "requirements_updated.txt",
    "requirements_final.txt",
    "docker-compose.yml",
    "docker-compose.prod.yml",
    "Dockerfile",
    "Dockerfile.prod",
    "README.md",
    "README_updated.md",
    "test_api.py",
    "models_updated.py",
    "routers/admin_updated.py",
    "cleanup.py",
]

def cleanup_files():
    """Remove duplicate and old files"""
    print("🧹 Starting cleanup...")
    deleted_count = 0
    kept_count = 0
    
    # Delete specified files
    for file_path in DELETE_FILES:
        if os.path.exists(file_path):
            try:
                if os.path.isdir(file_path):
                    shutil.rmtree(file_path)
                else:
                    os.remove(file_path)
                print(f"🗑️  Deleted: {file_path}")
                deleted_count += 1
            except Exception as e:
                print(f"⚠️  Error deleting {file_path}: {e}")
                
    # Verify kept files exist
    for file_path in KEEP_FILES:
        if os.path.exists(file_path):
            kept_count += 1
        else:
            print(f"⚠️  Warning: Expected file not found: {file_path}")
            
    print(f"\n✅ Cleanup complete!")
    print(f"📊 Deleted {deleted_count} files")
    print(f"📊 Kept {kept_count} files")
    
    # Create __init__.py files if they don't exist
    init_files = [
        "utils/__init__.py",
        "middleware/__init__.py",
        "routers/__init__.py",
        "alembic/__init__.py",
    ]
    
    for init_file in init_files:
        if not os.path.exists(init_file):
            try:
                os.makedirs(os.path.dirname(init_file), exist_ok=True)
                with open(init_file, "w") as f:
                    f.write("# Package initialization\n")
                print(f"📁 Created: {init_file}")
            except Exception as e:
                print(f"⚠️  Error creating {init_file}: {e}")
                
    # Create logs directory
    logs_dir = "logs"
    if not os.path.exists(logs_dir):
        os.makedirs(logs_dir)
        print(f"📁 Created: {logs_dir}/")
        
    # Create nginx directories
    nginx_dirs = ["nginx/ssl", "nginx/logs"]
    for nginx_dir in nginx_dirs:
        if not os.path.exists(nginx_dir):
            os.makedirs(nginx_dir, exist_ok=True)
            print(f"📁 Created: {nginx_dir}/")

    print("\n🎯 Project structure is now clean and organized!")
    print("🚀 Use 'python run_complete.py' to start the application")
    print("🐳 Use 'docker-compose -f docker-compose.complete.yml up' for Docker")

if __name__ == "__main__":
    cleanup_files()
