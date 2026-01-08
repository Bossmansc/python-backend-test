from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from sqlalchemy import func, desc, and_
from datetime import datetime, timedelta
from typing import List, Optional
from database import get_db
from dependencies import get_current_user, require_admin
from models import User, Project, Deployment, DeploymentStatus
from utils.validation import validator

router = APIRouter(prefix="/analytics", tags=["analytics"])

@router.get("/user/stats")
def get_user_analytics(
    start_date: Optional[str] = None,
    end_date: Optional[str] = None,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Get analytics for the current user"""
    # Set default date range (last 30 days)
    if not end_date:
        end_date = datetime.utcnow().isoformat()
    if not start_date:
        start_date = (datetime.utcnow() - timedelta(days=30)).isoformat()
        
    # Validate date range
    is_valid, error = validator.validate_date_range(start_date, end_date)
    if not is_valid:
        raise HTTPException(status_code=400, detail=error)
        
    # Convert dates
    start = datetime.fromisoformat(start_date.replace('Z', '+00:00'))
    end = datetime.fromisoformat(end_date.replace('Z', '+00:00'))
    
    # Get user's projects
    projects = db.query(Project).filter(
        Project.user_id == current_user.id,
        Project.created_at.between(start, end)
    ).all()
    
    # Get deployments for user's projects
    deployments = db.query(Deployment).join(Project).filter(
        Project.user_id == current_user.id,
        Deployment.started_at.between(start, end)
    ).all()
    
    # Calculate statistics
    total_projects = len(projects)
    total_deployments = len(deployments)
    
    # Deployment status breakdown
    status_counts = {}
    for deployment in deployments:
        status = deployment.status.value
        status_counts[status] = status_counts.get(status, 0) + 1
        
    # Success rate
    successful_deployments = status_counts.get('success', 0)
    success_rate = (successful_deployments / total_deployments * 100) if total_deployments > 0 else 0
    
    # Average deployment time
    deployment_times = []
    for deployment in deployments:
        if deployment.completed_at and deployment.started_at:
            duration = (deployment.completed_at - deployment.started_at).total_seconds()
            deployment_times.append(duration)
            
    avg_deployment_time = sum(deployment_times) / len(deployment_times) if deployment_times else 0
    
    # Daily deployment trend
    daily_trend = {}
    for deployment in deployments:
        date_str = deployment.started_at.date().isoformat()
        daily_trend[date_str] = daily_trend.get(date_str, 0) + 1
        
    return {
        "period": {
            "start": start_date,
            "end": end_date,
            "days": (end - start).days
        },
        "summary": {
            "total_projects": total_projects,
            "total_deployments": total_deployments,
            "success_rate": round(success_rate, 2),
            "avg_deployment_time_seconds": round(avg_deployment_time, 2)
        },
        "deployment_status": status_counts,
        "daily_trend": daily_trend,
        "projects": [
            {
                "id": p.id,
                "name": p.name,
                "status": p.status.value,
                "deployment_count": len(p.deployments)
            }
            for p in projects[:10]  # Limit to 10 projects
        ]
    }

@router.get("/admin/overview")
def get_admin_overview(
    db: Session = Depends(get_db),
    admin: User = Depends(require_admin)
):
    """Get admin overview analytics"""
    # Total statistics
    total_users = db.query(User).count()
    total_projects = db.query(Project).count()
    total_deployments = db.query(Deployment).count()
    
    # Active users (last 30 days)
    thirty_days_ago = datetime.utcnow() - timedelta(days=30)
    active_users = db.query(User).filter(
        User.created_at >= thirty_days_ago
    ).count()
    
    # Deployment success rate
    successful_deployments = db.query(Deployment).filter(
        Deployment.status == DeploymentStatus.SUCCESS
    ).count()
    success_rate = (successful_deployments / total_deployments * 100) if total_deployments > 0 else 0
    
    # Monthly growth
    current_month_start = datetime.utcnow().replace(day=1, hour=0, minute=0, second=0, microsecond=0)
    last_month_start = (current_month_start - timedelta(days=1)).replace(day=1)
    
    # New users this month
    new_users_this_month = db.query(User).filter(
        User.created_at >= current_month_start
    ).count()
    
    # New users last month
    new_users_last_month = db.query(User).filter(
        User.created_at >= last_month_start,
        User.created_at < current_month_start
    ).count()
    
    user_growth = (
        ((new_users_this_month - new_users_last_month) / new_users_last_month * 100)
        if new_users_last_month > 0 else 100
    )
    
    # Top users by project count
    top_users = db.query(
        User.id,
        User.email,
        func.count(Project.id).label('project_count')
    ).join(Project).group_by(User.id).order_by(desc('project_count')).limit(10).all()
    
    # Deployment trend (last 7 days)
    deployment_trend = {}
    for i in range(7):
        date = datetime.utcnow() - timedelta(days=i)
        date_str = date.date().isoformat()
        start_of_day = date.replace(hour=0, minute=0, second=0, microsecond=0)
        end_of_day = date.replace(hour=23, minute=59, second=59, microsecond=999999)
        
        daily_deployments = db.query(Deployment).filter(
            Deployment.started_at.between(start_of_day, end_of_day)
        ).count()
        deployment_trend[date_str] = daily_deployments
        
    return {
        "timestamp": datetime.utcnow().isoformat(),
        "overview": {
            "total_users": total_users,
            "active_users_last_30_days": active_users,
            "total_projects": total_projects,
            "total_deployments": total_deployments,
            "deployment_success_rate": round(success_rate, 2)
        },
        "growth": {
            "new_users_this_month": new_users_this_month,
            "new_users_last_month": new_users_last_month,
            "user_growth_percentage": round(user_growth, 2)
        },
        "top_users": [
            {
                "id": user_id,
                "email": email,
                "project_count": project_count
            }
            for user_id, email, project_count in top_users
        ],
        "deployment_trend_last_7_days": deployment_trend
    }

@router.get("/project/{project_id}")
def get_project_analytics(
    project_id: int,
    start_date: Optional[str] = None,
    end_date: Optional[str] = None,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Get analytics for a specific project"""
    # Check if project exists and user has access
    project = db.query(Project).filter(
        Project.id == project_id,
        Project.user_id == current_user.id
    ).first()
    
    if not project:
        raise HTTPException(status_code=404, detail="Project not found")
        
    # Set default date range (all time)
    if not end_date:
        end_date = datetime.utcnow().isoformat()
    if not start_date:
        start_date = project.created_at.isoformat()
        
    # Validate date range
    is_valid, error = validator.validate_date_range(start_date, end_date)
    if not is_valid:
        raise HTTPException(status_code=400, detail=error)
        
    # Convert dates
    start = datetime.fromisoformat(start_date.replace('Z', '+00:00'))
    end = datetime.fromisoformat(end_date.replace('Z', '+00:00'))
    
    # Get project deployments in date range
    deployments = db.query(Deployment).filter(
        Deployment.project_id == project_id,
        Deployment.started_at.between(start, end)
    ).order_by(Deployment.started_at.desc()).all()
    
    # Calculate statistics
    total_deployments = len(deployments)
    
    # Deployment status breakdown
    status_counts = {}
    deployment_durations = []
    
    for deployment in deployments:
        status = deployment.status.value
        status_counts[status] = status_counts.get(status, 0) + 1
        
        if deployment.completed_at and deployment.started_at:
            duration = (deployment.completed_at - deployment.started_at).total_seconds()
            deployment_durations.append(duration)
            
    # Success rate
    successful_deployments = status_counts.get('success', 0)
    success_rate = (successful_deployments / total_deployments * 100) if total_deployments > 0 else 0
    
    # Average deployment time
    avg_deployment_time = sum(deployment_durations) / len(deployment_durations) if deployment_durations else 0
    
    # Monthly deployment count
    monthly_deployments = {}
    for deployment in deployments:
        month_key = deployment.started_at.strftime("%Y-%m")
        monthly_deployments[month_key] = monthly_deployments.get(month_key, 0) + 1
        
    # Recent deployments (last 5)
    recent_deployments = [
        {
            "id": d.id,
            "status": d.status.value,
            "started_at": d.started_at.isoformat(),
            "completed_at": d.completed_at.isoformat() if d.completed_at else None,
            "duration_seconds": (
                (d.completed_at - d.started_at).total_seconds()
                if d.completed_at and d.started_at else None
            )
        }
        for d in deployments[:5]
    ]
    
    return {
        "project": {
            "id": project.id,
            "name": project.name,
            "status": project.status.value,
            "created_at": project.created_at.isoformat()
        },
        "period": {
            "start": start_date,
            "end": end_date
        },
        "summary": {
            "total_deployments": total_deployments,
            "success_rate": round(success_rate, 2),
            "avg_deployment_time_seconds": round(avg_deployment_time, 2),
            "failed_deployments": status_counts.get('failed', 0)
        },
        "deployment_status": status_counts,
        "monthly_trend": monthly_deployments,
        "recent_deployments": recent_deployments
    }
