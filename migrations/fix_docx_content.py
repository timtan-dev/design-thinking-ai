#!/usr/bin/env python3
"""
Migration script to fix corrupted .docx file content in database.
Re-extracts text from .docx files that were saved as binary data.
"""
import os
import sys
from docx import Document

# Add project root to path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from config.database import get_db
from database.models import ResearchData


def fix_docx_content():
    """Re-extract text content from .docx files stored in database"""
    db = get_db()

    try:
        # Find all research data with corrupted .docx content
        all_data = db.query(ResearchData).all()
        fixed_count = 0
        error_count = 0

        print(f"Found {len(all_data)} research data records")
        print("Scanning for corrupted .docx files...\n")

        for data in all_data:
            # Check if content starts with 'PK' (ZIP signature for .docx files)
            if data.file_content and data.file_content.startswith('PK'):
                print(f"Processing ID {data.id}: {data.file_path}")

                try:
                    # Check if physical file exists
                    if not os.path.exists(data.file_path):
                        print(f"  ⚠️  Physical file not found: {data.file_path}")
                        error_count += 1
                        continue

                    # Extract text from .docx file
                    doc = Document(data.file_path)
                    extracted_text = '\n'.join([paragraph.text for paragraph in doc.paragraphs])

                    if not extracted_text.strip():
                        print(f"  ⚠️  No text content found in document")
                        error_count += 1
                        continue

                    # Update database record
                    data.file_content = extracted_text
                    data.processed = False  # Mark as unprocessed so AI can re-analyze

                    print(f"  ✅ Extracted {len(extracted_text)} characters")
                    print(f"  Preview: {extracted_text[:100]}...")
                    fixed_count += 1

                except Exception as e:
                    print(f"  ❌ Error processing file: {str(e)}")
                    error_count += 1

        # Commit all changes
        if fixed_count > 0:
            db.commit()
            print(f"\n✅ Successfully fixed {fixed_count} records")

        if error_count > 0:
            print(f"⚠️  {error_count} records had errors")

        if fixed_count == 0 and error_count == 0:
            print("✅ No corrupted .docx records found")

    except Exception as e:
        print(f"❌ Migration failed: {str(e)}")
        db.rollback()
        sys.exit(1)
    finally:
        db.close()


if __name__ == "__main__":
    print("=" * 60)
    print("DOCX Content Fix Migration")
    print("=" * 60)
    print()

    fix_docx_content()

    print()
    print("=" * 60)
    print("Migration complete!")
    print("=" * 60)
