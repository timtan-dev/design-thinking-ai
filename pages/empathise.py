import os
import streamlit as st
from config.database import get_db
from database.models import ResearchData

RESEARCH_METHODS = {
    "interview": {"name": "Interview", "icon": "🎤"},
    "survey": {"name": "Survey", "icon": "📝"},
    "ethnography": {"name": "Ethnography", "icon": "👣"},
    "focus_group": {"name": "Focus Group", "icon": "🧍"},
    "observation": {"name": "Observation", "icon": "📸"},
    "diary_study": {"name": "Diary Study", "icon": "📔"}
}

# def render_empathise_page(project):
#     """Render the Empathise stage page with data collection cards"""
#     st.markdown("<div class='section-header'>📊 Collect Data</div>", unsafe_allow_html=True)
#     db = get_db()
#     uploaded_data = db.query(ResearchData).filter(ResearchData.project_id == project.id).all()
#     db.close()
#     uploaded_methods = {data.method_type for data in uploaded_data}

#     st.markdown('<div class="cards-grid">', unsafe_allow_html=True)
#     cols = st.columns(3)
#     for idx, (method_key, method_info) in enumerate(RESEARCH_METHODS.items()):
#         with cols[idx % 3]:
#             is_uploaded = method_key in uploaded_methods
#             status_text = "✓ Data uploaded" if is_uploaded else "Click to upload data"
#             with st.container():
#                 st.markdown(f"""
#                     <div class="method-card">
#                         <div class="method-icon">{method_info['icon']}</div>
#                         <div class="method-name">{method_info['name']}</div>
#                         <div class="method-status">{status_text}</div>
#                     </div>
#                 """, unsafe_allow_html=True)
#                 uploaded_file = st.file_uploader(f"Upload {method_info['name']} data", key=f"upload_{method_key}")
#                 if uploaded_file and st.button(f"💾 Save", key=f"save_{method_key}", use_container_width=True):
#                     save_research_data(project.id, method_key, uploaded_file)
#                     st.rerun()

def render_empathise_page(project):
    """Render the Empathise stage page with data collection cards"""
    st.markdown("""
        <div class="section-header">
            <span class="section-icon">📊</span>
            <span class="section-title">Collect Data</span>
        </div>
    """, unsafe_allow_html=True)

    db = get_db()
    uploaded_data = db.query(ResearchData).filter(ResearchData.project_id == project.id).all()
    db.close()
    uploaded_methods = {data.method_type for data in uploaded_data}

    st.markdown('<div class="cards-grid">', unsafe_allow_html=True)
    cols = st.columns(3)

    for idx, (method_key, method_info) in enumerate(RESEARCH_METHODS.items()):
        with cols[idx % 3]:
            is_uploaded = method_key in uploaded_methods
            status_text = "✓ Data uploaded" if is_uploaded else "Click to upload data"
            card_class = "uploaded" if is_uploaded else ""

            # Render clickable card
            if st.button(
                f"{method_info['icon']} {method_info['name']}",
                key=f"card_{method_key}",
                use_container_width=True,
                type="primary" if is_uploaded else "secondary"
            ):
                open_method_dialog(project.id, method_key, method_info["name"])

            # Small caption for status
            st.caption(status_text)

    st.markdown("</div>", unsafe_allow_html=True)


@st.dialog("Upload Research Data")
def open_method_dialog(project_id, method_key, method_name):
    """Dialog window for uploading data or downloading a template"""
    st.markdown(f"### {method_name} ({method_key})")
    st.markdown("You can upload your collected research data or download a template to guide your data collection.")

    # File uploader
    uploaded_file = st.file_uploader(
        f"Upload {method_name} data",
        type=["txt", "pdf", "docx", "csv"],
        key=f"upload_dialog_{method_key}"
    )

    col1, col2 = st.columns(2)
    with col1:
        if st.button("📥 Download Template", use_container_width=True):
            generate_template(method_key, method_name)

    with col2:
        if uploaded_file and st.button("💾 Save", use_container_width=True):
            save_research_data(project_id, method_key, uploaded_file)
            st.success(f"{method_name} data uploaded successfully!")
            st.rerun()



def generate_template(method_type, method_name):
    """Download template for research method"""
    template = f"# {method_name} Template\nAdd your notes here..."
    st.download_button(
        label=f"📥 Download {method_name} Template",
        data=template,
        file_name=f"{method_type}_template.md",
        mime="text/markdown"
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
