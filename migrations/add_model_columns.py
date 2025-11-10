"""
Database Migration: Add model tracking columns
Adds preferred_model to projects table and model_used to generated_content table
"""

from sqlalchemy import create_engine, text
from config.settings import Settings
import sys

def run_migration():
    """Add model tracking columns to projects and generated_content tables"""

    engine = create_engine(Settings.DATABASE_URL)

    try:
        with engine.connect() as conn:
            print("Starting migration: Adding model tracking columns...")

            # Add preferred_model to projects table
            print("  Adding preferred_model column to projects...")
            conn.execute(text("""
                ALTER TABLE projects
                ADD COLUMN preferred_model VARCHAR(100) DEFAULT 'gpt-4o'
            """))

            # Add model_used to generated_content table
            print("  Adding model_used column to generated_content...")
            conn.execute(text("""
                ALTER TABLE generated_content
                ADD COLUMN model_used VARCHAR(100)
            """))

            conn.commit()
            print("✅ Migration completed successfully!")
            print("\nChanges made:")
            print("  - projects.preferred_model: Default AI model for project (default: gpt-4o)")
            print("  - generated_content.model_used: Tracks which model generated each content")
            return True

    except Exception as e:
        print(f"❌ Migration failed: {str(e)}")
        print("\nNote: If columns already exist, this is normal.")
        return False
    finally:
        engine.dispose()

if __name__ == "__main__":
    success = run_migration()
    sys.exit(0 if success else 1)
