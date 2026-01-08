from fastapi import FastAPI, Depends, HTTPException, status, BackgroundTasks
from fastapi.middleware.cors import CORSMiddleware
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from pydantic import BaseModel, EmailStr, HttpUrl, Field
from datetime import datetime, timedelta
from typing import Optional, List
import enum
import asyncio
import random
import os

# In-memory database simulation
class InMemoryDB:
    users = []
    projects = []
    deployments = []
    refresh_tokens = []
    
    @classmethod
    def get_next_id(cls, collection):
        return len(collection) + 1

db = InMemoryDB()

# Models
class User:
    def __init__(self, email: str, password: str):
        self.id = db.get_next_id(db.users)
        self.email = email
        self.hashed_password = password  # In preview, we don't hash for simplicity
        self.created_at = datetime.utcnow()
        self.is_active = True
        self.is_admin = self.id == 1  # First user is admin

class ProjectStatus(str, enum.Enum):
    ACTIVE = "active"
    INACTIVE = "inactive"
    ERROR = "error"

class Project:
    def __init__(self, name: str, github_url: str, user_id: int):
        self.id = db.get_next_id(db.projects)
        self.name = name
        self.github_url = github_url
        self.status = ProjectStatus.ACTIVE
        self.user_id = user_id
        self.created_at = datetime.utcnow()

class DeploymentStatus(str, enum.Enum):
    PENDING = "pending"
    BUILDING = "building"
    DEPLOYING = "deploying"
    SUCCESS = "success"
    FAILED = "failed"
    CANCELLED = "cancelled"

class Deployment:
    def __init__(self, project_id: int):
        self.id = db.get_next_id(db.deployments)
        self.project_id = project_id
        self.status = DeploymentStatus.PENDING
        self.logs = "Deployment queued...\n"
        self.started_at = datetime.utcnow()
        self.completed_at = None

# Pydantic schemas
class UserCreate(BaseModel):
    email: EmailStr
    # Updated max_length to 128 to match production schema
    password: str = Field(..., min_length=8, max_length=128)

class UserResponse(BaseModel):
    id: int
    email: EmailStr
    created_at: datetime
    is_active: bool

    class Config:
        from_attributes = True

class Token(BaseModel):
    access_token: str
    refresh_token: str
    token_type: str = "bearer"

class ProjectCreate(BaseModel):
    name: str
    github_url: HttpUrl

class ProjectResponse(BaseModel):
    id: int
    name: str
    github_url: str
    status: ProjectStatus
    user_id: int
    created_at: datetime

    class Config:
        from_attributes = True

class DeploymentResponse(BaseModel):
    id: int
    project_id: int
    status: DeploymentStatus
    logs: str
    started_at: datetime
    completed_at: Optional[datetime]

    class Config:
        from_attributes = True

class HealthCheck(BaseModel):
    status: str
    timestamp: datetime
    version: str = "1.0.0"

# App setup
app = FastAPI(
    title="Cloud Deploy API Gateway - Preview",
    version="1.0.0",
    description="Preview version for sandbox environment"
)

# Enable CORS for frontend
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Allow all origins for preview/sandbox
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

security = HTTPBearer()

# Simple JWT simulation (not secure for production!)
def create_token(user_id: int, token_type: str = "access") -> str:
    return f"{token_type}_token_{user_id}_{datetime.utcnow().timestamp()}"

def get_current_user(credentials: HTTPAuthorizationCredentials = Depends(security)):
    token = credentials.credentials
    if not token.startswith("access_token_"):
        raise HTTPException(status_code=401, detail="Invalid token")
    
    try:
        # Extract user ID from token
        parts = token.split("_")
        user_id = int(parts[2])
        
        # Find user
        user = next((u for u in db.users if u.id == user_id), None)
        if not user or not user.is_active:
            raise HTTPException(status_code=401, detail="User not found or inactive")
        return user
    except:
        raise HTTPException(status_code=401, detail="Invalid token")

# Routes
@app.get("/")
def read_root():
    return {
        "message": "Welcome to Cloud Deploy API Gateway",
        "version": "1.0.0",
        "endpoints": {
            "auth": "/auth",
            "projects": "/projects",
            "deployments": "/deployments",
            "health": "/health",
            "docs": "/docs"
        }
    }

@app.get("/health", response_model=HealthCheck)
def health_check():
    return HealthCheck(
        status="healthy",
        timestamp=datetime.utcnow()
    )

@app.post("/auth/register", response_model=UserResponse, status_code=201)
def register(user: UserCreate):
    # Check if user exists
    if any(u.email == user.email for u in db.users):
        raise HTTPException(status_code=400, detail="Email already registered")
    
    # Create user
    new_user = User(email=user.email, password=user.password)
    db.users.append(new_user)
    return new_user

@app.post("/auth/login", response_model=Token)
def login(user: UserCreate):
    # Find user
    db_user = next((u for u in db.users if u.email == user.email and u.hashed_password == user.password), None)
    if not db_user:
        raise HTTPException(status_code=401, detail="Incorrect email or password")
    
    # Create tokens
    access_token = create_token(db_user.id, "access")
    refresh_token = create_token(db_user.id, "refresh")
    
    return {
        "access_token": access_token,
        "refresh_token": refresh_token,
        "token_type": "bearer"
    }

@app.get("/users/me", response_model=UserResponse)
def get_current_user_info(current_user: User = Depends(get_current_user)):
    return current_user

@app.get("/projects", response_model=List[ProjectResponse])
def list_projects(current_user: User = Depends(get_current_user)):
    user_projects = [p for p in db.projects if p.user_id == current_user.id]
    return user_projects

@app.post("/projects", response_model=ProjectResponse, status_code=201)
def create_project(
    project: ProjectCreate,
    current_user: User = Depends(get_current_user)
):
    new_project = Project(
        name=project.name,
        github_url=str(project.github_url),  # Convert HttpUrl to string
        user_id=current_user.id
    )
    db.projects.append(new_project)
    return new_project

async def simulate_deployment(deployment_id: int):
    """Simulate deployment process"""
    await asyncio.sleep(1)
    
    # Find deployment
    deployment = next((d for d in db.deployments if d.id == deployment_id), None)
    if not deployment:
        return
        
    # Simulate process
    deployment.status = DeploymentStatus.BUILDING
    deployment.logs += "Building application...\n"
    await asyncio.sleep(1)
    
    deployment.status = DeploymentStatus.DEPLOYING
    deployment.logs += "Deploying to production...\n"
    await asyncio.sleep(1)
    
    # Random success/failure
    if random.random() > 0.3:  # 70% success rate
        deployment.status = DeploymentStatus.SUCCESS
        deployment.logs += "✓ Deployment successful!\n"
    else:
        deployment.status = DeploymentStatus.FAILED
        deployment.logs += "✗ Deployment failed\n"
        
    deployment.completed_at = datetime.utcnow()

@app.post("/projects/{project_id}/deploy", response_model=DeploymentResponse, status_code=201)
def trigger_deployment(
    project_id: int,
    background_tasks: BackgroundTasks,
    current_user: User = Depends(get_current_user)
):
    # Check if project exists and belongs to user
    project = next((p for p in db.projects if p.id == project_id and p.user_id == current_user.id), None)
    if not project:
        raise HTTPException(status_code=404, detail="Project not found")
    
    # Create deployment
    deployment = Deployment(project_id=project_id)
    db.deployments.append(deployment)
    
    # Start background task
    background_tasks.add_task(simulate_deployment, deployment.id)
    
    return deployment

@app.get("/deployments/{deployment_id}", response_model=DeploymentResponse)
def get_deployment(
    deployment_id: int,
    current_user: User = Depends(get_current_user)
):
    deployment = next((d for d in db.deployments if d.id == deployment_id), None)
    if not deployment:
        raise HTTPException(status_code=404, detail="Deployment not found")
        
    # Check if user owns the project
    project = next((p for p in db.projects if p.id == deployment.project_id), None)
    if not project or project.user_id != current_user.id:
        raise HTTPException(status_code=404, detail="Deployment not found")
        
    return deployment

@app.get("/deployments/{deployment_id}/logs")
def get_deployment_logs(
    deployment_id: int,
    current_user: User = Depends(get_current_user)
):
    deployment = next((d for d in db.deployments if d.id == deployment_id), None)
    if not deployment:
        raise HTTPException(status_code=404, detail="Deployment not found")
        
    # Check if user owns the project
    project = next((p for p in db.projects if p.id == deployment.project_id), None)
    if not project or project.user_id != current_user.id:
        raise HTTPException(status_code=404, detail="Deployment not found")
        
    return {"logs": deployment.logs}

@app.get("/admin/stats")
def get_admin_stats(current_user: User = Depends(get_current_user)):
    # Check if user is admin
    if not current_user.is_admin:
        raise HTTPException(status_code=403, detail="Admin privileges required")
        
    return {
        "users": len(db.users),
        "projects": len(db.projects),
        "deployments": len(db.deployments),
        "timestamp": datetime.utcnow().isoformat()
    }

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
