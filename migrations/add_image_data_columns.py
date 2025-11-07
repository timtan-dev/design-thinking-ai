"""
Database Migration: Add image_data and image_filename columns
Adds Base64 image storage columns to SketchIteration and MockupIteration tables
"""

from sqlalchemy import create_engine, text
from config.settings import Settings
import sys

def run_migration():
    """Add image_data and image_filename columns to iteration tables"""

    engine = create_engine(Settings.DATABASE_URL)

    try:
        with engine.connect() as conn:
            print("Starting migration: Adding image_data columns...")

            # Add columns to sketch_iterations table
            print("  Adding columns to sketch_iterations...")
            conn.execute(text("""
                ALTER TABLE sketch_iterations
                ADD COLUMN image_data TEXT
            """))
            conn.execute(text("""
                ALTER TABLE sketch_iterations
                ADD COLUMN image_filename TEXT
            """))

            # Add columns to mockup_iterations table
            print("  Adding columns to mockup_iterations...")
            conn.execute(text("""
                ALTER TABLE mockup_iterations
                ADD COLUMN image_data TEXT
            """))
            conn.execute(text("""
                ALTER TABLE mockup_iterations
                ADD COLUMN image_filename TEXT
            """))

            conn.commit()
            print("✅ Migration completed successfully!")
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
