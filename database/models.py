"""
Database Models
SQLAlchemy ORM models for all database tables
"""

from sqlalchemy import Column, Integer, String, Text, DateTime, ForeignKey, Boolean, JSON
from sqlalchemy.orm import relationship
from datetime import datetime
from config.database import Base

class Project(Base):
    """Project model - represents a design thinking project"""
    __tablename__ = "projects"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(255), nullable=False)
    area = Column(String(255), nullable=False)
    goal = Column(Text, nullable=False)
    current_stage = Column(Integer, default=1)  # 1-6 for the six stages
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    user_id = Column(String(255), nullable=True)  # For future multi-user support

    # Relationships
    stage_progress = relationship("StageProgress", back_populates="project", cascade="all, delete-orphan")
    research_data = relationship("ResearchData", back_populates="project", cascade="all, delete-orphan")
    generated_content = relationship("GeneratedContent", back_populates="project", cascade="all, delete-orphan")

    def __repr__(self):
        return f"<Project(id={self.id}, name='{self.name}', area='{self.area}')>"

class StageProgress(Base):
    """Stage progress tracking for each project"""
    __tablename__ = "stage_progress"

    id = Column(Integer, primary_key=True, index=True)
    project_id = Column(Integer, ForeignKey("projects.id"), nullable=False)
    stage_number = Column(Integer, nullable=False)  # 1-6 for the six stages
    status = Column(String(50), default="not_started")  # not_started, in_progress, completed
    data = Column(JSON, nullable=True)  # Stage-specific data
    completed_at = Column(DateTime, nullable=True)

    # Relationships
    project = relationship("Project", back_populates="stage_progress")

    def __repr__(self):
        return f"<StageProgress(project_id={self.project_id}, stage={self.stage_number}, status='{self.status}')>"

class ResearchData(Base):
    """Research data collected during empathise stage"""
    __tablename__ = "research_data"

    id = Column(Integer, primary_key=True, index=True)
    project_id = Column(Integer, ForeignKey("projects.id"), nullable=False)
    method_type = Column(String(100), nullable=False)  # interview, survey, ethnography, etc.
    file_path = Column(Text, nullable=True)
    file_content = Column(Text, nullable=True)
    processed = Column(Boolean, default=False)
    created_at = Column(DateTime, default=datetime.utcnow)

    # Relationships
    project = relationship("Project", back_populates="research_data")

    def __repr__(self):
        return f"<ResearchData(id={self.id}, project_id={self.project_id}, method='{self.method_type}')>"

class GeneratedContent(Base):
    """AI-generated content for various stages"""
    __tablename__ = "generated_content"

    id = Column(Integer, primary_key=True, index=True)
    project_id = Column(Integer, ForeignKey("projects.id"), nullable=False)
    content_type = Column(String(100), nullable=False)  # empathy_map, persona, journey_map, etc.
    content = Column(Text, nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow)

    # Relationships
    project = relationship("Project", back_populates="generated_content")

    def __repr__(self):
        return f"<GeneratedContent(id={self.id}, type='{self.content_type}')>"

class Template(Base):
    """Template storage for various research methods"""
    __tablename__ = "templates"

    id = Column(Integer, primary_key=True, index=True)
    method_type = Column(String(100), nullable=False, unique=True)
    template_content = Column(Text, nullable=False)
    version = Column(String(20), default="1.0")
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    def __repr__(self):
        return f"<Template(method='{self.method_type}', version='{self.version}')>"

class StageSummary(Base):
    """AI-generated summaries for each stage"""
    __tablename__ = "stage_summaries"

    id = Column(Integer, primary_key=True, index=True)
    project_id = Column(Integer, ForeignKey("projects.id"), nullable=False)
    stage = Column(String(50), nullable=False)  # empathise, define, ideate, etc.
    summary_text = Column(Text, nullable=False)
    version = Column(Integer, default=1)  # Auto-increment for each new summary
    created_at = Column(DateTime, default=datetime.utcnow)

    # Relationships
    project = relationship("Project")

    def __repr__(self):
        return f"<StageSummary(project_id={self.project_id}, stage='{self.stage}', version={self.version})>"

class BrainstormIdea(Base):
    """Brainstorming ideas - both seed ideas and expansions"""
    __tablename__ = "brainstorm_ideas"

    id = Column(Integer, primary_key=True, index=True)
    project_id = Column(Integer, ForeignKey("projects.id"), nullable=False)
    idea_type = Column(String(50), nullable=False)  # seed_practical, seed_bold, seed_wild, expansion
    idea_text = Column(Text, nullable=False)
    parent_id = Column(Integer, ForeignKey("brainstorm_ideas.id"), nullable=True)  # For expansions
    order_index = Column(Integer, default=0)  # For maintaining order
    created_at = Column(DateTime, default=datetime.utcnow)

    # Relationships
    project = relationship("Project")
    parent = relationship("BrainstormIdea", remote_side=[id], backref="expansions")

    def __repr__(self):
        return f"<BrainstormIdea(id={self.id}, type='{self.idea_type}', project_id={self.project_id})>"
