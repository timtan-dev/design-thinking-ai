"""
CRUD operations for Projects
"""

from sqlalchemy.orm import Session
from database.models import Project
from typing import List, Optional
from datetime import datetime

def create_project(db: Session, name: str, area: str, goal: str, user_id: Optional[str] = None) -> Project:
    """
    Create a new project

    Args:
        db: Database session
        name: Project name
        area: Project area/domain
        goal: Project goal
        user_id: Optional user identifier

    Returns:
        Created project object
    """
    project = Project(
        name=name,
        area=area,
        goal=goal,
        user_id=user_id
    )
    db.add(project)
    db.commit()
    db.refresh(project)
    return project

def get_project(db: Session, project_id: int) -> Optional[Project]:
    """
    Get a project by ID

    Args:
        db: Database session
        project_id: Project ID

    Returns:
        Project object or None
    """
    return db.query(Project).filter(Project.id == project_id).first()

def get_project_by_name(db: Session, name: str, user_id: Optional[str] = None) -> Optional[Project]:
    """
    Get a project by name

    Args:
        db: Database session
        name: Project name
        user_id: Optional user identifier

    Returns:
        Project object or None
    """
    query = db.query(Project).filter(Project.name == name)
    if user_id:
        query = query.filter(Project.user_id == user_id)
    return query.first()

def list_projects(db: Session, user_id: Optional[str] = None, limit: int = 100) -> List[Project]:
    """
    List all projects

    Args:
        db: Database session
        user_id: Optional user identifier to filter by
        limit: Maximum number of projects to return

    Returns:
        List of project objects
    """
    query = db.query(Project)
    if user_id:
        query = query.filter(Project.user_id == user_id)
    return query.order_by(Project.updated_at.desc()).limit(limit).all()

def update_project(db: Session, project_id: int, **kwargs) -> Optional[Project]:
    """
    Update a project

    Args:
        db: Database session
        project_id: Project ID
        **kwargs: Fields to update (name, area, goal)

    Returns:
        Updated project object or None
    """
    project = get_project(db, project_id)
    if not project:
        return None

    for key, value in kwargs.items():
        if hasattr(project, key):
            setattr(project, key, value)

    project.updated_at = datetime.utcnow()
    db.commit()
    db.refresh(project)
    return project

def delete_project(db: Session, project_id: int) -> bool:
    """
    Delete a project

    Args:
        db: Database session
        project_id: Project ID

    Returns:
        True if deleted, False otherwise
    """
    project = get_project(db, project_id)
    if not project:
        return False

    db.delete(project)
    db.commit()
    return True
