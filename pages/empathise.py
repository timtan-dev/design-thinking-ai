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
    if method_key == "interview":
        st.markdown("### 📝 Generate AI Template")
        generate_template(method_key, method_name, project)
    else:
        # Simple download for other methods
        template_content = f"# {method_name} Template\nAdd your notes here..."
        st.download_button(
            label="📥 Download Template",
            data=template_content,
            file_name=f"{method_key}_template.md",
            mime="text/markdown",
            use_container_width=True
        )



def generate_template(method_type, method_name, project):
    """Generate AI-powered template for interview research method"""
    from prompts.empathise.interview import INTERVIEW_SCRIPT_TEMPLATE_PROMPT

    # Get user preferences - these are always shown
    tone_options = ["conversational", "formal", "inspirational", "journalistic"]
    interview_type = st.selectbox(
        "Interview Type",
        ["podcast", "video interview", "journalistic interview", "academic interview", "corporate interview"],
        key=f"interview_type_{method_type}"
    )
    tone = st.selectbox(
        "Tone",
        tone_options,
        key=f"tone_{method_type}"
    )

    # Generate button
    if st.button("✨ Generate Script Template", key=f"gen_btn_{method_type}", type="primary", use_container_width=True):
        with st.spinner(f"Generating {method_name} template for {project.name}..."):
            ai_service = AIService()

            user_prompt = f"""
            Generate a professional interview script template for a {interview_type}.
            Tone: {tone}

            The interview should help gather insights for the "{project.name}" project in the {project.area} space.
            The goal is: {project.goal}

            Include all required sections: Introduction, Warm-up Questions, Main Discussion (with 3 topic placeholders), and Closing.
            Make sure the questions are specifically tailored to uncover user needs, pain points, and behaviors related to this project.
            """

            # Call AI service with project context
            system_prompt = INTERVIEW_SCRIPT_TEMPLATE_PROMPT.format(
                project_name=project.name,
                project_area=project.area,
                project_goal=project.goal,
                tone=tone
            )
            template_content = ai_service._call_openai(system_prompt, user_prompt)

            # Open dialog to show generated template
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
            st.download_button(
                label="📥 Download Template",
                data=template_content,
                file_name=f"{project.name.lower().replace(' ', '_')}_{method_type}_script_template.md",
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
