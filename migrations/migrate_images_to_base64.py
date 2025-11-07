"""
Database Migration: Convert existing images from file paths to Base64
Reads images from image_path, converts to Base64, and stores in image_data column
"""

from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from config.settings import Settings
from database.models import SketchIteration, MockupIteration, Base
import base64
import os
from pathlib import Path
import sys

def migrate_images():
    """Convert all existing images from file paths to Base64"""

    engine = create_engine(Settings.DATABASE_URL)
    Session = sessionmaker(bind=engine)
    session = Session()

    try:
        print("Starting migration: Converting images to Base64...")
        print("=" * 60)

        # Migrate SketchIteration images
        print("\n📸 Processing SketchIteration images...")
        sketches = session.query(SketchIteration).filter(
            SketchIteration.image_path.isnot(None)
        ).all()

        sketch_success = 0
        sketch_fail = 0
        sketch_skip = 0

        for sketch in sketches:
            # Skip if already has Base64 data
            if sketch.image_data:
                sketch_skip += 1
                continue

            if not sketch.image_path:
                continue

            image_path = Path(sketch.image_path)

            if image_path.exists():
                try:
                    # Read image and convert to Base64
                    with open(image_path, 'rb') as img_file:
                        image_bytes = img_file.read()
                        image_base64 = base64.b64encode(image_bytes).decode('utf-8')

                    # Update database record
                    sketch.image_data = image_base64
                    sketch.image_filename = image_path.name

                    sketch_success += 1
                    print(f"  ✓ Sketch #{sketch.id}: {image_path.name}")

                except Exception as e:
                    sketch_fail += 1
                    print(f"  ✗ Sketch #{sketch.id}: Failed - {str(e)}")
            else:
                sketch_fail += 1
                print(f"  ✗ Sketch #{sketch.id}: File not found - {sketch.image_path}")

        # Migrate MockupIteration images
        print("\n🎨 Processing MockupIteration images...")
        mockups = session.query(MockupIteration).filter(
            MockupIteration.image_path.isnot(None)
        ).all()

        mockup_success = 0
        mockup_fail = 0
        mockup_skip = 0

        for mockup in mockups:
            # Skip if already has Base64 data
            if mockup.image_data:
                mockup_skip += 1
                continue

            if not mockup.image_path:
                continue

            image_path = Path(mockup.image_path)

            if image_path.exists():
                try:
                    # Read image and convert to Base64
                    with open(image_path, 'rb') as img_file:
                        image_bytes = img_file.read()
                        image_base64 = base64.b64encode(image_bytes).decode('utf-8')

                    # Update database record
                    mockup.image_data = image_base64
                    mockup.image_filename = image_path.name

                    mockup_success += 1
                    print(f"  ✓ Mockup #{mockup.id}: {image_path.name}")

                except Exception as e:
                    mockup_fail += 1
                    print(f"  ✗ Mockup #{mockup.id}: Failed - {str(e)}")
            else:
                mockup_fail += 1
                print(f"  ✗ Mockup #{mockup.id}: File not found - {mockup.image_path}")

        # Commit all changes
        session.commit()

        # Print summary
        print("\n" + "=" * 60)
        print("Migration Summary:")
        print(f"  Sketches:  ✓ {sketch_success} converted | ✗ {sketch_fail} failed | ⊝ {sketch_skip} skipped")
        print(f"  Mockups:   ✓ {mockup_success} converted | ✗ {mockup_fail} failed | ⊝ {mockup_skip} skipped")
        print(f"  Total:     ✓ {sketch_success + mockup_success} converted | ✗ {sketch_fail + mockup_fail} failed")
        print("=" * 60)

        if sketch_fail + mockup_fail == 0:
            print("✅ Migration completed successfully!")
            return True
        else:
            print("⚠️  Migration completed with some failures.")
            return False

    except Exception as e:
        print(f"❌ Migration failed: {str(e)}")
        session.rollback()
        import traceback
        traceback.print_exc()
        return False

    finally:
        session.close()
        engine.dispose()

if __name__ == "__main__":
    success = migrate_images()
    sys.exit(0 if success else 1)
