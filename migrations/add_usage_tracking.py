#!/usr/bin/env python3
"""
Migration: Add usage tracking columns (cost, duration, tokens) to generated_content and brainstorm_ideas tables
"""
import sys
import os

# Add project root to path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from config.database import engine
from sqlalchemy import text

def upgrade():
    """Add usage tracking columns to generated_content and brainstorm_ideas tables"""
    with engine.connect() as conn:
        # Add columns to generated_content table
        print("Adding usage tracking columns to generated_content table...")
        conn.execute(text("""
            ALTER TABLE generated_content
            ADD COLUMN duration_seconds REAL
        """))
        conn.execute(text("""
            ALTER TABLE generated_content
            ADD COLUMN input_tokens INTEGER
        """))
        conn.execute(text("""
            ALTER TABLE generated_content
            ADD COLUMN output_tokens INTEGER
        """))
        conn.execute(text("""
            ALTER TABLE generated_content
            ADD COLUMN cost_usd REAL
        """))
        conn.commit()
        print("✅ Added usage tracking columns to generated_content table")

        # Add columns to brainstorm_ideas table
        print("\nAdding usage tracking columns to brainstorm_ideas table...")
        conn.execute(text("""
            ALTER TABLE brainstorm_ideas
            ADD COLUMN duration_seconds REAL
        """))
        conn.execute(text("""
            ALTER TABLE brainstorm_ideas
            ADD COLUMN input_tokens INTEGER
        """))
        conn.execute(text("""
            ALTER TABLE brainstorm_ideas
            ADD COLUMN output_tokens INTEGER
        """))
        conn.execute(text("""
            ALTER TABLE brainstorm_ideas
            ADD COLUMN cost_usd REAL
        """))
        conn.commit()
        print("✅ Added usage tracking columns to brainstorm_ideas table")

def downgrade():
    """Remove usage tracking columns from generated_content and brainstorm_ideas tables"""
    with engine.connect() as conn:
        # SQLite doesn't support DROP COLUMN directly, so we'd need to recreate the tables
        # For now, just document the downgrade
        print("⚠️  Downgrade not implemented for SQLite")
        print("    To downgrade, you would need to recreate the tables without usage tracking columns")

if __name__ == "__main__":
    print("=" * 60)
    print("Migration: Add usage tracking (cost, duration, tokens)")
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
