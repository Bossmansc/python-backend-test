from pydantic import BaseModel, EmailStr, HttpUrl, Field
from datetime import datetime
from typing import Optional, List
import enum

# --- Token Schemas ---
class Token(BaseModel):
    access_token: str
    refresh_token: str
    token_type: str = "bearer"

class TokenData(BaseModel):
    user_id: Optional[int] = None

class RefreshTokenCreate(BaseModel):
    refresh_token: str

# --- User Schemas ---
class UserBase(BaseModel):
    email: EmailStr

class UserCreate(UserBase):
    # Increased max_length to 128. 
    # The backend will now pre-hash this, so we are no longer limited by bcrypt's 72 bytes.
    password: str = Field(..., min_length=8, max_length=128)

class User(UserBase):
    id: int
    created_at: datetime
    is_active: bool
    is_admin: bool = False

    class Config:
        from_attributes = True

# --- Project & Deployment Enums ---
class ProjectStatus(str, enum.Enum):
    ACTIVE = "active"
    INACTIVE = "inactive"
    ERROR = "error"

class DeploymentStatus(str, enum.Enum):
    PENDING = "pending"
    BUILDING = "building"
    DEPLOYING = "deploying"
    SUCCESS = "success"
    FAILED = "failed"
    CANCELLED = "cancelled"

# --- Project Schemas (Base) ---
class ProjectBase(BaseModel):
    name: str
    github_url: HttpUrl

class ProjectCreate(ProjectBase):
    pass

class Project(ProjectBase):
    id: int
    status: ProjectStatus
    user_id: int
    created_at: datetime

    class Config:
        from_attributes = True

# --- Deployment Schemas ---
class DeploymentBase(BaseModel):
    pass

class DeploymentCreate(DeploymentBase):
    pass

class Deployment(DeploymentBase):
    id: int
    project_id: int
    status: DeploymentStatus
    logs: str
    started_at: datetime
    completed_at: Optional[datetime]

    class Config:
        from_attributes = True

# --- Project Schemas (Extended) ---
class ProjectWithDeployments(Project):
    deployments: List[Deployment] = []

# --- System Schemas ---
class HealthCheck(BaseModel):
    status: str
    timestamp: datetime
    version: str
