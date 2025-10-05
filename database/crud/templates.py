"""
CRUD operations for Templates
"""

from sqlalchemy.orm import Session
from database.models import Template
from typing import Optional, List

def get_template(db: Session, method_type: str) -> Optional[Template]:
    """
    Get template by method type

    Args:
        db: Database session
        method_type: Method type (interview, survey, etc.)

    Returns:
        Template object or None
    """
    return db.query(Template).filter(
        Template.method_type == method_type,
        Template.is_active == True
    ).first()

def list_templates(db: Session, active_only: bool = True) -> List[Template]:
    """
    List all templates

    Args:
        db: Database session
        active_only: Only return active templates

    Returns:
        List of Template objects
    """
    query = db.query(Template)
    if active_only:
        query = query.filter(Template.is_active == True)
    return query.all()

def create_template(
    db: Session,
    method_type: str,
    template_content: str,
    version: str = "1.0"
) -> Template:
    """
    Create a new template

    Args:
        db: Database session
        method_type: Method type
        template_content: Template content
        version: Template version

    Returns:
        Created Template object
    """
    template = Template(
        method_type=method_type,
        template_content=template_content,
        version=version
    )
    db.add(template)
    db.commit()
    db.refresh(template)
    return template

def update_template(
    db: Session,
    method_type: str,
    template_content: str,
    version: Optional[str] = None
) -> Optional[Template]:
    """
    Update an existing template

    Args:
        db: Database session
        method_type: Method type
        template_content: New template content
        version: Optional new version

    Returns:
        Updated Template object or None
    """
    template = get_template(db, method_type)
    if not template:
        return None

    template.template_content = template_content
    if version:
        template.version = version

    db.commit()
    db.refresh(template)
    return template
