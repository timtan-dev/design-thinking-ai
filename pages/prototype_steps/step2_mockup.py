"""Step 2: AI-Assisted Mockup Generation with DALL-E"""

import streamlit as st
from database.models import MockupIteration, SketchIteration
from services.ai_service import AIService
from utils.time_utils import format_local_time
from prompts.prototype.mockup_generation import GENERATE_MOCKUP_PROMPT, REFINE_MOCKUP_PROMPT
from pathlib import Path
from datetime import datetime, timezone
import base64
import os

# Create uploads directory for mockups
MOCKUP_DIR = Path("uploads/mockups")
MOCKUP_DIR.mkdir(parents=True, exist_ok=True)

def get_image_for_display(item):
    """
    Get image for display from Base64 data stored in database
    Returns: image bytes suitable for st.image()
    Works for both SketchIteration and MockupIteration
    """
    if hasattr(item, 'image_data') and item.image_data:
        try:
            return base64.b64decode(item.image_data)
        except Exception as e:
            print(f"Error decoding Base64 image: {e}")
            return None
    return None

def render_mockup_step(prototype_page, project, ideate_summary, db):
    """Render the AI mockup generation step"""

    st.markdown("## 🎨 Step 2: AI-Assisted Mockup")

    if prototype_page.mockup_finalized:
        render_finalized_mockup(prototype_page, db)
    else:
        render_mockup_generation(prototype_page, project, ideate_summary, db)

def render_mockup_generation(prototype_page, project, ideate_summary, db):
    """Render the mockup generation and iteration interface"""

    # Get final sketch
    final_sketch = db.query(SketchIteration).filter(
        SketchIteration.id == prototype_page.final_sketch_id
    ).first()

    # Get existing mockup iterations
    mockups = db.query(MockupIteration).filter(
        MockupIteration.prototype_page_id == prototype_page.id
    ).order_by(MockupIteration.iteration_number).all()

    # Layout: Generate | Mockup Versions | Refinement
    col1, col2, col3 = st.columns([1, 1, 1])

    with col1:
        st.markdown("### Generate Mockup")

        # Show final sketch
        if final_sketch:
            with st.expander("📱 Based on your sketch"):
                image_data = get_image_for_display(final_sketch)
                if image_data:
                    st.image(image_data, use_container_width=True)
                else:
                    st.error("Sketch image not available")

        # Style options
        style = st.selectbox(
            "Design Style",
            ["Modern", "Minimalist", "Playful", "Professional", "Elegant"],
            key=f"mockup_style_{prototype_page.id}"
        )

        color_scheme = st.text_input(
            "Color Scheme",
            placeholder="e.g., Blue and calm, Vibrant and energetic",
            key=f"mockup_color_{prototype_page.id}"
        )

        additional_instructions = st.text_area(
            "Additional Instructions",
            placeholder="e.g., Make the mood slider more prominent, add a floating action button",
            key=f"mockup_additional_{prototype_page.id}",
            height=100
        )

        if st.button("✨ Generate Mockup", type="primary", use_container_width=True):
            generate_mockup(prototype_page, project, ideate_summary, final_sketch, style, color_scheme, additional_instructions, db)
            st.rerun()

    with col2:
        st.markdown("### Mockup Versions")
        if mockups:
            for mockup in mockups:
                with st.expander(f"v{mockup.iteration_number} - {format_local_time(mockup.created_at)}", expanded=(mockup == mockups[-1])):
                    image_data = get_image_for_display(mockup)
                    if image_data:
                        st.image(image_data, use_container_width=True)
                    else:
                        st.error("Mockup image not available")
                    if mockup.user_refinement:
                        st.caption(f"📝 {mockup.user_refinement}")

                    # Select this mockup button
                    if st.button(f"⭐ Choose v{mockup.iteration_number}", key=f"choose_mockup_{mockup.id}"):
                        prototype_page.mockup_finalized = True
                        prototype_page.final_mockup_id = mockup.id
                        db.commit()
                        st.success(f"✅ Mockup v{mockup.iteration_number} selected!")
                        st.rerun()
        else:
            st.info("No mockups generated yet")

    with col3:
        st.markdown("### Refinement")
        if mockups:
            st.markdown("**Latest mockup:**")
            latest_mockup = mockups[-1]

            refinement_text = st.text_area(
                "Request changes",
                placeholder="e.g., Make the buttons larger, change color to green",
                key=f"mockup_refinement_{prototype_page.id}",
                height=100
            )

            if st.button("🔄 Regenerate with Changes", use_container_width=True):
                if refinement_text.strip():
                    refine_mockup(prototype_page, project, ideate_summary, final_sketch, latest_mockup, refinement_text, db)
                    st.rerun()
                else:
                    st.warning("Please describe the changes you want")
        else:
            st.info("Generate a mockup first")

def render_finalized_mockup(prototype_page, db):
    """Render the finalized mockup view"""

    st.success("✅ Mockup Finalized")

    final_mockup = db.query(MockupIteration).filter(
        MockupIteration.id == prototype_page.final_mockup_id
    ).first()

    if final_mockup:
        col1, col2 = st.columns([1, 1])

        with col1:
            st.markdown("### Final Mockup")
            image_data = get_image_for_display(final_mockup)
            if image_data:
                st.image(image_data, use_container_width=True)
            else:
                st.error("Mockup image not available")
            st.caption(f"Finalized on: {format_local_time(final_mockup.created_at)}")

        with col2:
            st.markdown("### Details")
            if final_mockup.style_params:
                st.json(final_mockup.style_params)

        # Option to generate new version
        if st.button("🔄 Generate New Version"):
            prototype_page.mockup_finalized = False
            db.commit()
            st.rerun()

def generate_mockup(prototype_page, project, ideate_summary, final_sketch, style, color_scheme, additional_instructions, db):
    """Generate initial mockup using DALL-E/GPT-4o"""

    with st.spinner("🎨 Generating mockup with AI... This may take a moment."):
        ai_service = AIService()

        # Get sketch analysis for context
        sketch_description = final_sketch.ai_analysis if final_sketch else "User sketch"

        # Prepare generation prompt
        ideate_text = ideate_summary.summary_text if ideate_summary else ""

        # Extract key features from ideate summary (simplified)
        key_features = "Based on user research insights"

        prompt = GENERATE_MOCKUP_PROMPT.format(
            style=style.lower(),
            page_name=prototype_page.page_name,
            project_name=project.name,
            project_goal=project.goal,
            sketch_description=sketch_description[:500],  # Limit length
            key_features=key_features,
            color_scheme=color_scheme or "modern and clean",
            must_include_elements="navigation, main content area, interactive elements",
            user_refinement=additional_instructions or "No additional requirements"
        )

        # Generate image using GPT-4o (returns tuple: image_path, error_message)
        temp_image_path, error_message = ai_service.generate_image_with_gpt4o(
            prompt=prompt,
            reference_image_path=None  # No reference for initial generation
        )

        if temp_image_path:
            # Read temp image and convert to Base64
            try:
                timestamp = datetime.now(timezone.utc).strftime("%Y%m%d_%H%M%S")
                local_filename = f"mockup_{prototype_page.id}_{timestamp}.png"

                # Read the temp image and convert to Base64
                with open(temp_image_path, 'rb') as img_file:
                    image_bytes = img_file.read()
                    image_base64 = base64.b64encode(image_bytes).decode('utf-8')

            except Exception as e:
                st.error(f"Error saving image: {str(e)}")
                return

            # Save mockup iteration
            iteration_number = db.query(MockupIteration).filter(
                MockupIteration.prototype_page_id == prototype_page.id
            ).count() + 1

            mockup = MockupIteration(
                prototype_page_id=prototype_page.id,
                iteration_number=iteration_number,
                image_data=image_base64,  # Save Base64 for persistence
                image_filename=local_filename,
                generation_prompt=prompt,
                style_params={
                    "style": style,
                    "color_scheme": color_scheme,
                    "additional_instructions": additional_instructions
                },
                user_refinement=additional_instructions
            )
            db.add(mockup)
            db.commit()

            st.success("✅ Mockup generated successfully!")
        else:
            # Show detailed error message
            if error_message:
                st.error(f"❌ Failed to generate mockup:\n\n{error_message}")
            else:
                st.error("Failed to generate mockup. Please try again.")

def refine_mockup(prototype_page, project, ideate_summary, final_sketch, previous_mockup, refinement_text, db):
    """Refine existing mockup based on user feedback"""

    with st.spinner("🔄 Generating refined mockup..."):
        ai_service = AIService()

        # Get previous style params
        prev_style = previous_mockup.style_params or {}

        # Get previous mockup image path (stored locally)
        previous_image_path = None
        if previous_mockup.image_path:
            previous_image_path = Path(previous_mockup.image_path)
            if not previous_image_path.exists():
                st.warning(f"Previous mockup file not found: {previous_mockup.image_path}")

        prompt = REFINE_MOCKUP_PROMPT.format(
            previous_mockup_description=f"Previous mockup (v{previous_mockup.iteration_number}) - see image above",
            user_refinement=refinement_text,
            color_scheme=prev_style.get('color_scheme', 'modern'),
            style=prev_style.get('style', 'modern'),
            specific_improvements=refinement_text
        )

        # Generate refined image with GPT-4o, passing the previous mockup (returns tuple: image_path, error_message)
        temp_image_path, error_message = ai_service.generate_image_with_gpt4o(
            prompt=prompt,
            reference_image_path=str(previous_image_path) if previous_image_path else None
        )

        if temp_image_path:
            # Read temp image and convert to Base64
            try:
                timestamp = datetime.now(timezone.utc).strftime("%Y%m%d_%H%M%S")
                local_filename = f"mockup_{prototype_page.id}_{timestamp}.png"

                # Read the temp image and convert to Base64
                with open(temp_image_path, 'rb') as img_file:
                    image_bytes = img_file.read()
                    image_base64 = base64.b64encode(image_bytes).decode('utf-8')

            except Exception as e:
                st.error(f"Error saving refined image: {str(e)}")
                return

            iteration_number = db.query(MockupIteration).filter(
                MockupIteration.prototype_page_id == prototype_page.id
            ).count() + 1

            mockup = MockupIteration(
                prototype_page_id=prototype_page.id,
                iteration_number=iteration_number,
                image_data=image_base64,  # Save Base64 for persistence
                image_filename=local_filename,
                generation_prompt=prompt,
                style_params=prev_style,
                user_refinement=refinement_text
            )
            db.add(mockup)
            db.commit()

            st.success("✅ Refined mockup generated!")
        else:
            # Show detailed error message
            if error_message:
                st.error(f"❌ Failed to generate refined mockup:\n\n{error_message}")
            else:
                st.error("Failed to generate refined mockup. Please try again.")
