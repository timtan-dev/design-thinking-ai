"""Step 1: Sketch-to-Digital with AI vision analysis"""

import streamlit as st
from database.models import SketchIteration
from services.ai_service import AIService
from utils.time_utils import format_local_time
from prompts.prototype.sketch_analysis import ANALYZE_SKETCH_PROMPT, SUGGEST_IMPROVEMENTS_PROMPT
import os
from pathlib import Path
from datetime import datetime, timezone
import base64
from io import BytesIO

# Create uploads directory if it doesn't exist
UPLOAD_DIR = Path("uploads/sketches")
UPLOAD_DIR.mkdir(parents=True, exist_ok=True)

def get_image_for_display(sketch):
    """
    Get image for display from Base64 data stored in database
    Returns: image bytes suitable for st.image()
    """
    if sketch.image_data:
        try:
            return base64.b64decode(sketch.image_data)
        except Exception as e:
            print(f"Error decoding Base64 image: {e}")
            return None
    return None

def render_sketch_step(prototype_page, project, ideate_summary, db):
    """Render the sketch upload and analysis step"""

    st.markdown("## 📸 Step 1: Sketch-to-Digital")

    if prototype_page.sketch_finalized:
        render_finalized_sketch(prototype_page, db)
    else:
        render_sketch_upload(prototype_page, project, ideate_summary, db)

def render_sketch_upload(prototype_page, project, ideate_summary, db):
    """Render the sketch upload and iteration interface"""

    # Get existing sketch iterations
    sketches = db.query(SketchIteration).filter(
        SketchIteration.prototype_page_id == prototype_page.id
    ).order_by(SketchIteration.iteration_number).all()

    # Layout: Upload | Iterations | Analysis
    col1, col2, col3 = st.columns([1, 1, 1])

    with col1:
        st.markdown("### Upload Sketch")
        uploaded_file = st.file_uploader(
            "Upload your hand-drawn sketch or wireframe",
            type=['png', 'jpg', 'jpeg', 'heic'],
            key=f"sketch_upload_{prototype_page.id}"
        )

        user_instructions = st.text_area(
            "Instructions (optional)",
            placeholder="e.g., Focus on the mood tracking interface...",
            key=f"sketch_instructions_{prototype_page.id}",
            height=100
        )

        if st.button("🔍 Analyze Sketch", type="primary", use_container_width=True, disabled=not uploaded_file):
            if uploaded_file:
                analyze_and_save_sketch(prototype_page, project, ideate_summary, uploaded_file, user_instructions, db)
                st.rerun()

    with col2:
        st.markdown("### Iterations")
        if sketches:
            for sketch in sketches:
                with st.expander(f"v{sketch.iteration_number} - {format_local_time(sketch.created_at)}", expanded=(sketch == sketches[-1])):
                    image_data = get_image_for_display(sketch)
                    if image_data:
                        st.image(image_data, use_container_width=True)
                    else:
                        st.error("Image not available")
                    if sketch.user_instructions:
                        st.caption(f"📝 {sketch.user_instructions}")
        else:
            st.info("No sketches uploaded yet")

    with col3:
        st.markdown("### AI Analysis")
        if sketches:
            latest_sketch = sketches[-1]
            if latest_sketch.ai_analysis:
                st.markdown(latest_sketch.ai_analysis)

                if latest_sketch.ai_suggestions:
                    st.markdown("---")
                    st.markdown("**💡 Suggestions:**")
                    st.markdown(latest_sketch.ai_suggestions)
            else:
                st.info("Analyzing...")
        else:
            st.info("Upload a sketch to see AI analysis")

    # Finalize button (only show if there are sketches)
    if sketches:
        st.markdown("---")
        col_left, col_right = st.columns([2, 1])

        with col_right:
            if st.button("✅ Finalize Sketch & Continue to Mockup", type="primary", use_container_width=True):
                # Mark sketch as finalized
                latest_sketch = sketches[-1]
                prototype_page.sketch_finalized = True
                prototype_page.final_sketch_id = latest_sketch.id
                db.commit()
                st.success("✅ Sketch finalized! Moving to Step 2...")
                st.rerun()

        with col_left:
            st.caption(f"Total iterations: {len(sketches)}")

def render_finalized_sketch(prototype_page, db):
    """Render the finalized sketch view"""

    st.success("✅ Sketch Finalized")

    final_sketch = db.query(SketchIteration).filter(
        SketchIteration.id == prototype_page.final_sketch_id
    ).first()

    if final_sketch:
        col1, col2 = st.columns([1, 1])

        with col1:
            st.markdown("### Final Sketch")
            image_data = get_image_for_display(final_sketch)
            if image_data:
                st.image(image_data, use_container_width=True)
            else:
                st.error("Image not available")
            st.caption(f"Finalized on: {format_local_time(final_sketch.created_at)}")

        with col2:
            st.markdown("### Analysis")
            if final_sketch.ai_analysis:
                st.markdown(final_sketch.ai_analysis)

        # Option to edit/refine
        if st.button("🔄 Upload Refined Version"):
            prototype_page.sketch_finalized = False
            db.commit()
            st.rerun()

def analyze_and_save_sketch(prototype_page, project, ideate_summary, uploaded_file, user_instructions, db):
    """Analyze uploaded sketch with AI vision and save to database"""

    # Save uploaded file
    iteration_number = db.query(SketchIteration).filter(
        SketchIteration.prototype_page_id == prototype_page.id
    ).count() + 1

    # Get file bytes and convert to Base64 for database storage
    file_bytes = uploaded_file.getbuffer()
    image_base64 = base64.b64encode(file_bytes).decode('utf-8')

    # Create iteration record with Base64 data
    sketch = SketchIteration(
        prototype_page_id=prototype_page.id,
        iteration_number=iteration_number,
        image_data=image_base64,
        image_filename=uploaded_file.name,
        user_instructions=user_instructions
    )
    db.add(sketch)
    db.commit()

    # Save temp file for AI vision analysis (will be deleted after analysis)
    filename = f"page_{prototype_page.id}_v{iteration_number}_{uploaded_file.name}"
    temp_file_path = UPLOAD_DIR / filename
    with open(temp_file_path, "wb") as f:
        f.write(file_bytes)

    # Analyze with AI vision
    with st.spinner("🤖 Analyzing sketch with AI..."):
        ai_service = AIService()

        # Prepare prompts
        ideate_text = ideate_summary.summary_text if ideate_summary else "No ideate summary available"

        analysis_prompt = ANALYZE_SKETCH_PROMPT.format(
            project_name=project.name,
            project_area=project.area,
            project_goal=project.goal,
            ideate_summary=ideate_text,
            user_instructions=user_instructions or "No specific instructions"
        )

        # Call vision API
        analysis = ai_service.analyze_image_with_vision(
            image_path=str(temp_file_path),
            prompt=analysis_prompt
        )

        # Generate suggestions
        suggestions_prompt = SUGGEST_IMPROVEMENTS_PROMPT.format(
            sketch_analysis=analysis,
            project_goal=project.goal,
            ideate_summary=ideate_text
        )

        suggestions = ai_service._call_openai("You are a UX expert providing constructive feedback.", suggestions_prompt)

        # Update sketch with analysis
        sketch.ai_analysis = analysis
        sketch.ai_suggestions = suggestions
        db.commit()
