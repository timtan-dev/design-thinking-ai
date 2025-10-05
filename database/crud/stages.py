"""
CRUD operations for Stage Progress
"""

from sqlalchemy.orm import Session
from database.models import StageProgress
from typing import Optional, List
from datetime import datetime

def get_stage_progress(db: Session, project_id: int, stage_number: int) -> Optional[StageProgress]:
    """
    Get stage progress for a specific stage

    Args:
        db: Database session
        project_id: Project ID
        stage_number: Stage number (1-6)

    Returns:
        StageProgress object or None
    """
    return db.query(StageProgress).filter(
        StageProgress.project_id == project_id,
        StageProgress.stage_number == stage_number
    ).first()

def get_all_stage_progress(db: Session, project_id: int) -> List[StageProgress]:
    """
    Get all stage progress for a project

    Args:
        db: Database session
        project_id: Project ID

    Returns:
        List of StageProgress objects
    """
    return db.query(StageProgress).filter(
        StageProgress.project_id == project_id
    ).order_by(StageProgress.stage_number).all()

def create_or_update_stage_progress(
    db: Session,
    project_id: int,
    stage_number: int,
    status: str,
    data: Optional[dict] = None
) -> StageProgress:
    """
    Create or update stage progress

    Args:
        db: Database session
        project_id: Project ID
        stage_number: Stage number (1-6)
        status: Status (not_started, in_progress, completed)
        data: Optional stage-specific data

    Returns:
        StageProgress object
    """
    stage = get_stage_progress(db, project_id, stage_number)

    if stage:
        stage.status = status
        if data:
            stage.data = data
        if status == "completed":
            stage.completed_at = datetime.utcnow()
    else:
        stage = StageProgress(
            project_id=project_id,
            stage_number=stage_number,
            status=status,
            data=data,
            completed_at=datetime.utcnow() if status == "completed" else None
        )
        db.add(stage)

    db.commit()
    db.refresh(stage)
    return stage

def update_stage_data(db: Session, project_id: int, stage_number: int, data: dict) -> Optional[StageProgress]:
    """
    Update stage data

    Args:
        db: Database session
        project_id: Project ID
        stage_number: Stage number
        data: Data to update/merge

    Returns:
        Updated StageProgress object or None
    """
    stage = get_stage_progress(db, project_id, stage_number)
    if not stage:
        return None

    if stage.data:
        stage.data.update(data)
    else:
        stage.data = data

    db.commit()
    db.refresh(stage)
    return stage

def initialize_project_stages(db: Session, project_id: int):
    """
    Initialize all stages for a new project

    Args:
        db: Database session
        project_id: Project ID
    """
    for stage_num in range(1, 7):  # 6 stages
        existing = get_stage_progress(db, project_id, stage_num)
        if not existing:
            stage = StageProgress(
                project_id=project_id,
                stage_number=stage_num,
                status="not_started"
            )
            db.add(stage)
    db.commit()
