"""
Analyse Data Card Component
Card for analysis methods with AI generation
"""

import streamlit as st
from services.ai_service import AIService
from config.database import get_db
from database.models import GeneratedContent

def analyse_data_card(method_name: str, description: str):
    """
    Display an analysis method card

    Args:
        method_name: Name of the analysis method
        description: Brief description of the method
    """
    with st.expander(f"🔍 {method_name}", expanded=False):
        st.markdown(f"*{description.capitalize()}*")

        if st.button(f"Generate {method_name}", key=f"gen_analysis_{method_name}", type="primary"):
            with st.spinner(f"Generating {method_name.lower()}..."):
                ai_service = AIService()
                project = st.session_state.get('current_project', {})

                if method_name == "Empathy Map":
                    result = ai_service.create_empathy_map(project)
                    content_type = "empathy_map"
                elif method_name == "Persona":
                    result = ai_service.create_persona(project)
                    content_type = "persona"
                elif method_name == "Journey Map":
                    result = ai_service.create_journey_map(project)
                    content_type = "journey_map"
                elif method_name == "Affinity Map":
                    result = ai_service.create_affinity_map(project)
                    content_type = "affinity_map"
                elif method_name == "Storytelling":
                    result = ai_service.create_user_story(project)
                    content_type = "user_story"
                elif method_name == "Stakeholder Map":
                    result = ai_service.create_stakeholder_map(project)
                    content_type = "stakeholder_map"
                else:
                    result = "Generation coming soon..."
                    content_type = "unknown"

                st.success(f"Generated {method_name}:")
                st.markdown(result)

                # Save to database
                if result != "Generation coming soon...":
                    db = get_db()
                    generated_content = GeneratedContent(
                        project_id=project['id'],
                        stage="empathise",
                        content_type=content_type,
                        content=result
                    )
                    db.add(generated_content)
                    db.commit()
                    db.close()

                    st.info("💾 Saved to project history")
