from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List
from datetime import datetime, timedelta
from database import get_db
from models import User, Project, Deployment
from schemas import User as UserSchema, Project as ProjectSchema, Deployment as DeploymentSchema
from dependencies import get_current_user, require_admin
from config import settings
from sqlalchemy import func

router = APIRouter(prefix="/admin", tags=["admin"])

@router.get("/users", response_model=List[UserSchema])
def list_all_users(
    skip: int = 0,
    limit: int = 100,
    db: Session = Depends(get_db),
    admin: User = Depends(require_admin)
):
    """List all users (admin only)"""
    users = db.query(User).offset(skip).limit(limit).all()
    return users

@router.get("/users/{user_id}", response_model=UserSchema)
def get_user(
    user_id: int,
    db: Session = Depends(get_db),
    admin: User = Depends(require_admin)
):
    """Get user details (admin only)"""
    user = db.query(User).filter(User.id == user_id).first()
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found"
        )
    return user

@router.post("/users/{user_id}/deactivate")
def deactivate_user(
    user_id: int,
    db: Session = Depends(get_db),
    admin: User = Depends(require_admin)
):
    """Deactivate a user (admin only)"""
    user = db.query(User).filter(User.id == user_id).first()
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found"
        )
    user.is_active = False
    db.commit()
    return {"message": f"User {user.email} deactivated"}

@router.post("/users/{user_id}/activate")
def activate_user(
    user_id: int,
    db: Session = Depends(get_db),
    admin: User = Depends(require_admin)
):
    """Activate a user (admin only)"""
    user = db.query(User).filter(User.id == user_id).first()
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found"
        )
    user.is_active = True
    db.commit()
    return {"message": f"User {user.email} activated"}

@router.post("/users/{user_id}/make-admin")
def make_admin(
    user_id: int,
    db: Session = Depends(get_db),
    admin: User = Depends(require_admin)
):
    """Make a user admin (admin only)"""
    user = db.query(User).filter(User.id == user_id).first()
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found"
        )
    user.is_admin = True
    db.commit()
    return {"message": f"User {user.email} is now an admin"}

@router.post("/users/{user_id}/remove-admin")
def remove_admin(
    user_id: int,
    db: Session = Depends(get_db),
    admin: User = Depends(require_admin)
):
    """Remove admin privileges from a user (admin only)"""
    user = db.query(User).filter(User.id == user_id).first()
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found"
        )
    # Don't allow removing admin from yourself
    if user.id == admin.id:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Cannot remove admin privileges from yourself"
        )
    user.is_admin = False
    db.commit()
    return {"message": f"Admin privileges removed from {user.email}"}

@router.get("/stats")
def get_system_stats(
    db: Session = Depends(get_db),
    admin: User = Depends(require_admin)
):
    """Get system statistics (admin only)"""
    # User stats
    total_users = db.query(User).count()
    active_users = db.query(User).filter(User.is_active == True).count()
    admin_users = db.query(User).filter(User.is_admin == True).count()
    
    # Project stats
    total_projects = db.query(Project).count()
    active_projects = db.query(Project).filter(Project.status == "active").count()
    
    # Deployment stats
    total_deployments = db.query(Deployment).count()
    successful_deployments = db.query(Deployment).filter(Deployment.status == "success").count()
    failed_deployments = db.query(Deployment).filter(Deployment.status == "failed").count()
    pending_deployments = db.query(Deployment).filter(Deployment.status == "pending").count()
    
    # Recent activity (last 24 hours)
    twenty_four_hours_ago = datetime.utcnow() - timedelta(hours=24)
    recent_users = db.query(User).filter(User.created_at >= twenty_four_hours_ago).count()
    recent_deployments = db.query(Deployment).filter(Deployment.started_at >= twenty_four_hours_ago).count()
    
    # Storage stats (simulated)
    total_storage_mb = total_projects * 100  # Simulated: 100MB per project
    
    return {
        "users": {
            "total": total_users,
            "active": active_users,
            "admins": admin_users,
            "recent_24h": recent_users
        },
        "projects": {
            "total": total_projects,
            "active": active_projects
        },
        "deployments": {
            "total": total_deployments,
            "successful": successful_deployments,
            "failed": failed_deployments,
            "pending": pending_deployments,
            "recent_24h": recent_deployments
        },
        "storage": {
            "total_mb": total_storage_mb,
            "estimated_cost": total_storage_mb * 0.02  # $0.02 per MB per month
        },
        "timestamp": datetime.utcnow().isoformat()
    }

@router.get("/deployments", response_model=List[DeploymentSchema])
def list_all_deployments(
    skip: int = 0,
    limit: int = 100,
    status: str = None,
    db: Session = Depends(get_db),
    admin: User = Depends(require_admin)
):
    """List all deployments (admin only)"""
    query = db.query(Deployment)
    if status:
        query = query.filter(Deployment.status == status)
    deployments = query.offset(skip).limit(limit).all()
    return deployments

@router.get("/projects", response_model=List[ProjectSchema])
def list_all_projects(
    skip: int = 0,
    limit: int = 100,
    status: str = None,
    db: Session = Depends(get_db),
    admin: User = Depends(require_admin)
):
    """List all projects (admin only)"""
    query = db.query(Project)
    if status:
        query = query.filter(Project.status == status)
    projects = query.offset(skip).limit(limit).all()
    return projects

@router.delete("/projects/{project_id}")
def delete_project_admin(
    project_id: int,
    db: Session = Depends(get_db),
    admin: User = Depends(require_admin)
):
    """Delete any project (admin only)"""
    project = db.query(Project).filter(Project.id == project_id).first()
    if not project:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Project not found"
        )
    db.delete(project)
    db.commit()
    return {"message": f"Project {project.name} deleted by admin"}
