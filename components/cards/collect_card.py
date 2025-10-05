"""
Collect Data Card Component
Card for data collection methods with upload and generation
"""

import streamlit as st
from services.ai_service import AIService
from services.file_processor import save_uploaded_file

def collect_data_card(method_name: str, description: str):
    """
    Display a data collection method card

    Args:
        method_name: Name of the research method
        description: Brief description of the method
    """
    with st.expander(f"📊 {method_name}", expanded=False):
        st.markdown(f"*{description.capitalize()}*")

        col1, col2 = st.columns(2)

        with col1:
            if st.button(f"Generate {method_name} Template", key=f"gen_{method_name}"):
                with st.spinner(f"Generating {method_name.lower()} template..."):
                    ai_service = AIService()
                    project = st.session_state.get('current_project', {})

                    if method_name == "Interview":
                        result = ai_service.generate_interview_questions(project)
                    elif method_name == "Survey":
                        result = ai_service.generate_survey_questions(project)
                    elif method_name == "Ethnography":
                        result = ai_service.generate_ethnography_guide(project)
                    elif method_name == "Focus Group":
                        result = ai_service.generate_focus_group_guide(project)
                    elif method_name == "Observation":
                        result = ai_service.generate_observation_checklist(project)
                    elif method_name == "Diary Study":
                        result = ai_service.generate_diary_study_template(project)
                    else:
                        result = "Template generation coming soon..."

                    st.success("Generated Template:")
                    st.write(result)

        with col2:
            uploaded_file = st.file_uploader(
                f"Upload {method_name} Data",
                type=['csv', 'txt', 'pdf', 'docx'],
                key=f"upload_{method_name}"
            )

            if uploaded_file:
                project_id = st.session_state.current_project['id']
                file_path = save_uploaded_file(uploaded_file, project_id, method_name.lower())
                if file_path:
                    st.success(f"✅ Uploaded: {uploaded_file.name}")

                    # Save to database
                    from config.database import get_db
                    from database.models import ResearchData

                    db = get_db()
                    research_data = ResearchData(
                        project_id=project_id,
                        method_type=method_name.lower(),
                        file_path=file_path
                    )
                    db.add(research_data)
                    db.commit()
                    db.close()
