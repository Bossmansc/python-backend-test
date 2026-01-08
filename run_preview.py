#!/usr/bin/env python3
"""
Preview runner for sandbox environment
"""
import uvicorn

if __name__ == "__main__":
    print("🚀 Starting Cloud Deploy API Gateway - Preview")
    print("📡 Host: 0.0.0.0")
    print("🔌 Port: 8000")
    print("🌍 Environment: preview")
    print("=" * 50)
    print("📚 API Documentation: http://localhost:8000/docs")
    print("🏥 Health Check: http://localhost:8000/health")
    print("=" * 50)
    
    uvicorn.run(
        "main_preview:app",
        host="0.0.0.0",
        port=8000,
        reload=True,
        log_level="info"
    )
