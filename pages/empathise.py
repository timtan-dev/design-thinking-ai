import os
import streamlit as st
from config.database import get_db
from database.models import ResearchData
from services.ai_service import AIService

RESEARCH_METHODS = {
    "interview": {"name": "Interview", "icon": "🎤"},
    "survey": {"name": "Survey", "icon": "📝"},
    "ethnography": {"name": "Ethnography", "icon": "👣"},
    "focus_group": {"name": "Focus Group", "icon": "🧍"},
    "observation": {"name": "Observation", "icon": "📸"},
    "diary_study": {"name": "Diary Study", "icon": "📔"}
}

def render_empathise_page(project):
    db = get_db()
    uploaded_data = db.query(ResearchData).filter(ResearchData.project_id == project.id).all()
    db.close()
    uploaded_methods = {data.method_type for data in uploaded_data}

    # Add margin between stage section and method section
    st.markdown('<div style="margin-top: 2rem;"></div>', unsafe_allow_html=True)

    st.markdown('<div class="cards-grid">', unsafe_allow_html=True)
    cols = st.columns(3)

    for idx, (method_key, method_info) in enumerate(RESEARCH_METHODS.items()):
        with cols[idx % 3]:
            is_uploaded = method_key in uploaded_methods

            # Render clickable card
            if st.button(
                f"{method_info['icon']} {method_info['name']}",
                key=f"card_{method_key}",
                use_container_width=True,
                type="primary" if is_uploaded else "secondary"
            ):
                open_method_dialog(project, method_key, method_info["name"])

            # Small caption for status
            if is_uploaded:
                st.caption("✓ Data uploaded")

    st.markdown("</div>", unsafe_allow_html=True)


@st.dialog("Upload Research Data")
def open_method_dialog(project, method_key, method_name):
    """Dialog window for uploading data or downloading a template"""
    st.markdown(f"### {method_name}")

    # File uploader
    uploaded_file = st.file_uploader(
        label="",
        type=["txt", "pdf", "docx", "csv"],
        key=f"upload_dialog_{method_key}"
    )

    # Show save button if file is uploaded
    if uploaded_file:
        if st.button("💾 Save", use_container_width=True):
            save_research_data(project.id, method_key, uploaded_file)
            st.success(f"{method_name} data uploaded successfully!")
            st.rerun()

    st.divider()

    # Template generation section
    st.markdown("### 📝 Generate AI Template")
    generate_template(method_key, method_name, project)



def generate_template(method_type, method_name, project):
    """Generate AI-powered template for research methods"""

    # Import the appropriate prompt based on method type
    if method_type == "interview":
        from prompts.empathise.interview import INTERVIEW_SCRIPT_TEMPLATE_PROMPT as TEMPLATE_PROMPT
    elif method_type == "survey":
        from prompts.empathise.survey import SURVEY_TEMPLATE_PROMPT as TEMPLATE_PROMPT
    elif method_type == "ethnography":
        from prompts.empathise.ethnography import ETHNOGRAPHY_TEMPLATE_PROMPT as TEMPLATE_PROMPT
    elif method_type == "focus_group":
        from prompts.empathise.focus_group import FOCUS_GROUP_TEMPLATE_PROMPT as TEMPLATE_PROMPT
    elif method_type == "observation":
        from prompts.empathise.observation import OBSERVATION_TEMPLATE_PROMPT as TEMPLATE_PROMPT
    elif method_type == "diary_study":
        from prompts.empathise.diary_study import DIARY_STUDY_TEMPLATE_PROMPT as TEMPLATE_PROMPT
    else:
        st.error(f"Template generation not configured for {method_name}")
        return

    # Get user preferences based on method type
    tone_options = ["conversational", "formal", "professional", "friendly"]

    # Method-specific options
    if method_type == "interview":
        interview_type = st.selectbox(
            "Interview Type",
            ["podcast", "video interview", "journalistic interview", "academic interview", "corporate interview"],
            key=f"interview_type_{method_type}"
        )
        additional_context = f"a {interview_type}"
    elif method_type == "survey":
        survey_length = st.selectbox(
            "Survey Length",
            ["short (5-10 questions)", "medium (15-20 questions)", "long (25-30 questions)"],
            key=f"survey_length_{method_type}"
        )
        additional_context = f"{survey_length} survey"
    elif method_type == "ethnography":
        study_duration = st.selectbox(
            "Study Duration",
            ["1 week", "2 weeks", "1 month", "2-3 months"],
            key=f"study_duration_{method_type}"
        )
        additional_context = f"ethnographic study lasting {study_duration}"
    elif method_type == "focus_group":
        group_size = st.selectbox(
            "Group Size",
            ["small (4-6 people)", "medium (6-8 people)", "large (8-10 people)"],
            key=f"group_size_{method_type}"
        )
        additional_context = f"focus group with {group_size}"
    elif method_type == "observation":
        observation_type = st.selectbox(
            "Observation Type",
            ["participant observation", "non-participant observation", "structured observation", "naturalistic observation"],
            key=f"observation_type_{method_type}"
        )
        additional_context = f"{observation_type} study"
    elif method_type == "diary_study":
        study_duration = st.selectbox(
            "Study Duration",
            ["1 week", "2 weeks", "3 weeks", "4 weeks"],
            key=f"diary_duration_{method_type}"
        )
        entry_frequency = st.selectbox(
            "Entry Frequency",
            ["daily", "twice daily", "every other day", "weekly", "event-triggered"],
            key=f"entry_freq_{method_type}"
        )
        additional_context = f"diary study lasting {study_duration} with {entry_frequency} entries"
    else:
        additional_context = method_name

    tone = st.selectbox(
        "Tone",
        tone_options,
        key=f"tone_{method_type}"
    )

    # Generate button
    button_label = {
        "interview": "✨ Generate Script Template",
        "survey": "✨ Generate Survey Template",
        "ethnography": "✨ Generate Study Guide",
        "focus_group": "✨ Generate Discussion Guide",
        "observation": "✨ Generate Observation Guide",
        "diary_study": "✨ Generate Diary Study Guide"
    }.get(method_type, "✨ Generate Template")

    if st.button(button_label, key=f"gen_btn_{method_type}", type="primary", use_container_width=True):
        with st.spinner(f"Generating {method_name} template for {project.name}..."):
            ai_service = AIService()

            user_prompt = f"""
            Generate a professional {method_name} template for {additional_context}.
            Tone: {tone}

            This {method_name} should help gather insights for the "{project.name}" project in the {project.area} space.
            The goal is: {project.goal}

            Make sure the template is comprehensive, professionally structured, and specifically tailored to uncover user needs, pain points, and behaviors related to this project.
            """

            # Call AI service with project context
            system_prompt = TEMPLATE_PROMPT.format(
                project_name=project.name,
                project_area=project.area,
                project_goal=project.goal,
                tone=tone
            )
            template_content = ai_service._call_openai(system_prompt, user_prompt)

            # Show generated template
            show_generated_template(method_name, template_content, method_type, project)

def show_generated_template(method_name, template_content, method_type, project):
    """Display AI-generated template in an expander without saving to database"""

    with st.expander("📄 **Generated Template - Click to Expand/Collapse**", expanded=True):
        st.success(f"✅ Template generated successfully for **{project.name}**!")
        st.caption(f"Project Area: {project.area}")

        st.divider()

        # Display the generated content
        st.markdown(template_content)

        st.divider()

        # Add download button and info
        col1, col2 = st.columns([2, 1])
        with col1:
            st.info("💡 This template is customized for your project and ready to use. It is not saved to the database.")

        with col2:
            # Generate appropriate filename based on method type
            file_suffix = {
                "interview": "script",
                "survey": "survey",
                "ethnography": "guide",
                "focus_group": "discussion_guide",
                "observation": "observation_guide",
                "diary_study": "diary_guide"
            }.get(method_type, "template")

            st.download_button(
                label="📥 Download Template",
                data=template_content,
                file_name=f"{project.name.lower().replace(' ', '_')}_{method_type}_{file_suffix}.md",
                mime="text/markdown",
                use_container_width=True,
                type="primary"
            )


def save_research_data(project_id, method_type, uploaded_file):
    db = get_db()
    try:
        file_content = uploaded_file.read().decode("utf-8", errors="ignore")
        upload_dir = "uploads"
        os.makedirs(upload_dir, exist_ok=True)
        file_path = os.path.join(upload_dir, f"{project_id}_{method_type}_{uploaded_file.name}")
        with open(file_path, "wb") as f:
            uploaded_file.seek(0)
            f.write(uploaded_file.read())
        from database.models import ResearchData
        research_data = ResearchData(
            project_id=project_id,
            method_type=method_type,
            file_path=file_path,
            file_content=file_content,
            processed=False
        )
        db.add(research_data)
        db.commit()
        st.success(f"{uploaded_file.name} uploaded successfully!")
    finally:
        db.close()
