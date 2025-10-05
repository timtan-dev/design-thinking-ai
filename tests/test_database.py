"""
Database Tests
Test database connections and CRUD operations
"""

import pytest
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from config.database import Base
from database.models import Project, StageProgress
from database.crud.projects import create_project, get_project, list_projects

# Test database URL
TEST_DATABASE_URL = "sqlite:///:memory:"

@pytest.fixture
def test_db():
    """Create test database"""
    engine = create_engine(TEST_DATABASE_URL)
    Base.metadata.create_all(engine)
    TestSessionLocal = sessionmaker(bind=engine)
    db = TestSessionLocal()
    yield db
    db.close()
    Base.metadata.drop_all(engine)

def test_create_project(test_db):
    """Test project creation"""
    project = create_project(
        db=test_db,
        name="Test Project",
        area="Testing",
        goal="Test project creation"
    )

    assert project.id is not None
    assert project.name == "Test Project"
    assert project.area == "Testing"
    assert project.goal == "Test project creation"

def test_get_project(test_db):
    """Test getting a project"""
    project = create_project(
        db=test_db,
        name="Test Project",
        area="Testing",
        goal="Test"
    )

    retrieved = get_project(test_db, project.id)
    assert retrieved is not None
    assert retrieved.id == project.id
    assert retrieved.name == project.name

def test_list_projects(test_db):
    """Test listing projects"""
    create_project(test_db, "Project 1", "Area 1", "Goal 1")
    create_project(test_db, "Project 2", "Area 2", "Goal 2")

    projects = list_projects(test_db)
    assert len(projects) == 2
