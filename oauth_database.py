# Run this in Python or create a migration script
from config.database import init_db, Base, engine
from database.models import JiraOAuthToken, JiraConfig

# Create new tables
Base.metadata.create_all(bind=engine)