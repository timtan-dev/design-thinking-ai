#!/usr/bin/env python
"""
Seed Database
Create sample data for testing
"""

import sys
from pathlib import Path

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent.parent))

from config.database import get_db
from database.crud.projects import create_project
from database.crud.stages import initialize_project_stages, create_or_update_stage_progress

def main():
    """Seed database with sample data"""
    print("Seeding database with sample data...")

    db = get_db()

    try:
        # Create sample project
        project = create_project(
            db=db,
            name="Mobile Banking App Redesign",
            area="Financial Services",
            goal="Improve user experience for mobile banking app to increase user engagement and satisfaction"
        )

        print(f"✅ Created sample project: {project.name} (ID: {project.id})")

        # Initialize stages
        initialize_project_stages(db, project.id)
        print(f"✅ Initialized stages for project {project.id}")

        # Add some stage progress
        create_or_update_stage_progress(
            db=db,
            project_id=project.id,
            stage_number=1,
            status="in_progress",
            data={
                "interviews_conducted": 5,
                "surveys_collected": 50,
                "key_insights": [
                    "Users find the current navigation confusing",
                    "Security features are appreciated but seen as cumbersome",
                    "Users want faster access to frequently used features"
                ]
            }
        )

        print(f"✅ Added progress data for Empathise stage")

        # Create another sample project
        project2 = create_project(
            db=db,
            name="Healthcare Patient Portal",
            area="Healthcare",
            goal="Design an intuitive patient portal for managing appointments and medical records"
        )

        print(f"✅ Created sample project: {project2.name} (ID: {project2.id})")

        initialize_project_stages(db, project2.id)

        print("\n🎉 Database seeding complete!")
        print(f"\nSample projects created:")
        print(f"  1. {project.name} (ID: {project.id})")
        print(f"  2. {project2.name} (ID: {project2.id})")

    except Exception as e:
        print(f"\n❌ Error seeding database: {str(e)}")
        db.rollback()
        sys.exit(1)
    finally:
        db.close()

if __name__ == "__main__":
    main()
