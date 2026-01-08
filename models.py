from sqlalchemy import Column, Integer, String, DateTime, Boolean, ForeignKey, Text, Enum
from sqlalchemy.sql import func
from sqlalchemy.orm import relationship, validates
import enum
from database import Base

class User(Base):
    __tablename__ = "users"
    id = Column(Integer, primary_key=True, index=True)
    email = Column(String, unique=True, index=True, nullable=False)
    hashed_password = Column(String, nullable=False)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    is_active = Column(Boolean, default=True)
    is_admin = Column(Boolean, default=False, nullable=False)
    projects = relationship("Project", back_populates="owner")
    refresh_tokens = relationship("RefreshToken", back_populates="user")

class ProjectStatus(str, enum.Enum):
    ACTIVE = "active"
    INACTIVE = "inactive"
    ERROR = "error"

class Project(Base):
    __tablename__ = "projects"
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, nullable=False)
    github_url = Column(String, nullable=False)
    status = Column(Enum(ProjectStatus), default=ProjectStatus.ACTIVE)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    owner = relationship("User", back_populates="projects")
    deployments = relationship("Deployment", back_populates="project")
    
    @validates('github_url')
    def validate_github_url(self, key, value):
        """Convert HttpUrl to string before storing in database"""
        # If value has a __str__ method (like Pydantic's HttpUrl), convert it
        if hasattr(value, '__str__'):
            return str(value)
        return value
    
    @validates('status')
    def validate_status(self, key, value):
        """Ensure status is a valid ProjectStatus enum value"""
        if isinstance(value, str):
            # Convert string to enum
            try:
                return ProjectStatus(value.lower())
            except ValueError:
                # If invalid, return default
                return ProjectStatus.ACTIVE
        elif isinstance(value, ProjectStatus):
            return value
        else:
            return ProjectStatus.ACTIVE

class DeploymentStatus(str, enum.Enum):
    PENDING = "pending"
    BUILDING = "building"
    DEPLOYING = "deploying"
    SUCCESS = "success"
    FAILED = "failed"
    CANCELLED = "cancelled"

class Deployment(Base):
    __tablename__ = "deployments"
    id = Column(Integer, primary_key=True, index=True)
    project_id = Column(Integer, ForeignKey("projects.id"), nullable=False)
    status = Column(Enum(DeploymentStatus), default=DeploymentStatus.PENDING)
    logs = Column(Text, default="")
    started_at = Column(DateTime(timezone=True), server_default=func.now())
    completed_at = Column(DateTime(timezone=True), nullable=True)
    project = relationship("Project", back_populates="deployments")

class RefreshToken(Base):
    __tablename__ = "refresh_tokens"
    id = Column(Integer, primary_key=True, index=True)
    token = Column(String, unique=True, index=True, nullable=False)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    expires_at = Column(DateTime(timezone=True), nullable=False)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    user = relationship("User", back_populates="refresh_tokens")
