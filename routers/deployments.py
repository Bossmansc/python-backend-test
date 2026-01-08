from fastapi import APIRouter, Depends, HTTPException, status, BackgroundTasks
from sqlalchemy.orm import Session
from datetime import datetime
import asyncio
import random

from database import get_db
from models import Deployment, Project, User, DeploymentStatus
from schemas import Deployment as DeploymentSchema, DeploymentCreate
from dependencies import get_current_user

router = APIRouter(prefix="/deployments", tags=["deployments"])


async def simulate_deployment(deployment_id: int, db: Session):
    """Simulate deployment process in background"""
    await asyncio.sleep(2)  # Initial delay
    
    # Get deployment
    deployment = db.query(Deployment).filter(Deployment.id == deployment_id).first()
    if not deployment:
        return
    
    # Simulate building
    deployment.status = DeploymentStatus.BUILDING
    deployment.logs = "Starting build process...\n"
    db.commit()
    
    await asyncio.sleep(3)
    deployment.logs += "✓ Dependencies installed\n"
    deployment.logs += "✓ Building application...\n"
    db.commit()
    
    # Simulate deploying
    deployment.status = DeploymentStatus.DEPLOYING
    deployment.logs += "✓ Build completed successfully\n"
    deployment.logs += "Starting deployment...\n"
    db.commit()
    
    await asyncio.sleep(2)
    
    # Randomly succeed or fail
    if random.random() > 0.2:  # 80% success rate
        deployment.status = DeploymentStatus.SUCCESS
        deployment.logs += "✓ Deployment completed successfully!\n"
    else:
        deployment.status = DeploymentStatus.FAILED
        deployment.logs += "✗ Deployment failed: Build timeout\n"
    
    deployment.completed_at = datetime.utcnow()
    db.commit()


@router.post("/projects/{project_id}/deploy", response_model=DeploymentSchema, status_code=status.HTTP_201_CREATED)
def trigger_deployment(
    project_id: int,
    background_tasks: BackgroundTasks,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    # Check if project exists and belongs to user
    project = db.query(Project).filter(
        Project.id == project_id,
        Project.user_id == current_user.id
    ).first()
    
    if not project:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Project not found"
        )
    
    # Create deployment record
    deployment = Deployment(
        project_id=project_id,
        status=DeploymentStatus.PENDING,
        logs="Deployment queued...\n"
    )
    
    db.add(deployment)
    db.commit()
    db.refresh(deployment)
    
    # Start background deployment simulation
    background_tasks.add_task(simulate_deployment, deployment.id, db)
    
    return deployment


@router.get("/{deployment_id}", response_model=DeploymentSchema)
def get_deployment(
    deployment_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    deployment = db.query(Deployment).join(Project).filter(
        Deployment.id == deployment_id,
        Project.user_id == current_user.id
    ).first()
    
    if not deployment:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Deployment not found"
        )
    
    return deployment


@router.get("/{deployment_id}/logs")
def get_deployment_logs(
    deployment_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    deployment = db.query(Deployment).join(Project).filter(
        Deployment.id == deployment_id,
        Project.user_id == current_user.id
    ).first()
    
    if not deployment:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Deployment not found"
        )
    
    return {"logs": deployment.logs}


@router.post("/{deployment_id}/cancel")
def cancel_deployment(
    deployment_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    deployment = db.query(Deployment).join(Project).filter(
        Deployment.id == deployment_id,
        Project.user_id == current_user.id
    ).first()
    
    if not deployment:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Deployment not found"
        )
    
    # Only allow cancellation if deployment is still running
    if deployment.status in [DeploymentStatus.SUCCESS, DeploymentStatus.FAILED, DeploymentStatus.CANCELLED]:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Cannot cancel deployment with status: {deployment.status}"
        )
    
    deployment.status = DeploymentStatus.CANCELLED
    deployment.completed_at = datetime.utcnow()
    deployment.logs += "\n✗ Deployment cancelled by user\n"
    
    db.commit()
    
    return {"message": "Deployment cancelled successfully"}
