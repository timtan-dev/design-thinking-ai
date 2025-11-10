#!/usr/bin/env python3
"""
Migration: Add model_used column to brainstorm_ideas table
"""
import sys
import os

# Add project root to path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from config.database import engine
from sqlalchemy import text

def upgrade():
    """Add model_used column to brainstorm_ideas table"""
    with engine.connect() as conn:
        # Add model_used column
        conn.execute(text("""
            ALTER TABLE brainstorm_ideas
            ADD COLUMN model_used VARCHAR(100)
        """))
        conn.commit()
        print("✅ Added model_used column to brainstorm_ideas table")

def downgrade():
    """Remove model_used column from brainstorm_ideas table"""
    with engine.connect() as conn:
        # SQLite doesn't support DROP COLUMN directly, so we'd need to recreate the table
        # For now, just document the downgrade
        print("⚠️  Downgrade not implemented for SQLite")
        print("    To downgrade, you would need to recreate the table without model_used column")

if __name__ == "__main__":
    print("=" * 60)
    print("Migration: Add model_used to brainstorm_ideas")
    print("=" * 60)
    print()

    try:
        upgrade()
        print()
        print("=" * 60)
        print("Migration completed successfully!")
        print("=" * 60)
    except Exception as e:
        print(f"❌ Migration failed: {str(e)}")
        sys.exit(1)
