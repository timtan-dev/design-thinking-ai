#!/usr/bin/env python
"""
Initialize Database
Create all database tables
"""

import sys
from pathlib import Path

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent.parent))

from config.database import init_db, engine
from database.models import Base
from config.settings import Settings

def main():
    """Initialize database tables"""
    print("Initializing Design Thinking AI database...")
    print(f"Database URL: {Settings.DATABASE_URL}")

    try:
        # Create all tables
        init_db()

        # Verify tables were created
        from sqlalchemy import inspect
        inspector = inspect(engine)
        tables = inspector.get_table_names()

        print(f"\n✅ Successfully created {len(tables)} tables:")
        for table in tables:
            print(f"  - {table}")

        print("\nDatabase initialization complete!")

    except Exception as e:
        print(f"\n❌ Error initializing database: {str(e)}")
        sys.exit(1)

if __name__ == "__main__":
    main()
