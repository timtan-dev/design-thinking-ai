"""
Database Configuration
SQLAlchemy setup and session management
"""

from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker, Session
from config.settings import Settings
from contextlib import contextmanager

# Create database engine
engine = create_engine(
    Settings.DATABASE_URL,
    connect_args={"check_same_thread": False} if "sqlite" in Settings.DATABASE_URL else {},
    echo=Settings.DEBUG
)

# Create SessionLocal class
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# Create Base class for models
Base = declarative_base()

def init_db():
    """Initialize database - create all tables"""
    from database.models import Project, StageProgress, ResearchData, GeneratedContent, Template
    Base.metadata.create_all(bind=engine)

def get_db() -> Session:
    """
    Get database session

    Returns:
        Session: SQLAlchemy database session
    """
    db = SessionLocal()
    try:
        return db
    except Exception as e:
        db.close()
        raise e

@contextmanager
def get_db_context():
    """
    Context manager for database sessions

    Usage:
        with get_db_context() as db:
            # Use db session
            pass
    """
    db = SessionLocal()
    try:
        yield db
        db.commit()
    except Exception as e:
        db.rollback()
        raise e
    finally:
        db.close()
