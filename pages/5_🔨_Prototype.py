"""
Prototype Stage - Build Solution Representations
Create prototypes to test ideas
"""

import streamlit as st
from components.project_header import display_project_header
from utils.session_manager import require_project
from services.ai_service import AIService
from services.file_processor import save_uploaded_file
from config.database import get_db
from database.crud.stages import create_or_update_stage_progress, get_stage_progress

st.set_page_config(page_title="Prototype - Design Thinking AI", page_icon="🔨", layout="wide")

if not require_project():
    st.stop()

st.title("🔨 Stage 4: Prototype")
st.markdown("**Build tangible representations of your ideas**")

display_project_header()

st.markdown("---")

project_id = st.session_state.current_project['id']
db = get_db()
stage_data = get_stage_progress(db, project_id, 4)
current_data = stage_data.data if stage_data and stage_data.data else {}

# Prototype Description
st.header("1. Prototype Description")

prototype_desc = st.text_area(
    "Describe your prototype",
    value=current_data.get('description', ''),
    placeholder="What are you building? What key features will it demonstrate?",
    height=150
)

prototype_type = st.selectbox(
    "Prototype Type",
    ["Paper Prototype", "Digital Mockup", "Interactive Prototype", "Physical Model", "Storyboard", "Other"],
    index=0 if not current_data.get('type') else ["Paper Prototype", "Digital Mockup", "Interactive Prototype", "Physical Model", "Storyboard", "Other"].index(current_data.get('type', 'Paper Prototype'))
)

# User Flow
st.markdown("---")
st.header("2. User Flow")

user_flow = st.text_area(
    "Define the user flow",
    value=current_data.get('user_flow', ''),
    placeholder="Step 1: User lands on homepage\nStep 2: User clicks on feature X\nStep 3: System shows Y\n...",
    height=200
)

if st.button("Generate User Flow with AI"):
    with st.spinner("Generating user flow..."):
        ai_service = AIService()
        generated = ai_service.generate_user_flow(st.session_state.current_project, prototype_desc)
        st.success("AI-Generated User Flow:")
        st.write(generated)

# Feature List
st.markdown("---")
st.header("3. Feature List")

col1, col2 = st.columns([3, 1])

with col1:
    features = st.text_area(
        "List key features to include",
        value=current_data.get('features', ''),
        placeholder="• Feature 1: Description\n• Feature 2: Description\n• Feature 3: Description",
        height=150
    )

with col2:
    st.markdown("**Priority Levels:**")
    st.markdown("""
    - 🔴 Must Have
    - 🟡 Should Have
    - 🟢 Nice to Have
    """)

# Mockup Upload
st.markdown("---")
st.header("4. Upload Mockups/Sketches")

uploaded_files = st.file_uploader(
    "Upload prototype images",
    accept_multiple_files=True,
    type=['png', 'jpg', 'jpeg', 'pdf']
)

if uploaded_files:
    saved_files = []
    for uploaded_file in uploaded_files:
        file_path = save_uploaded_file(uploaded_file, project_id)
        if file_path:
            saved_files.append(file_path)
            st.success(f"Uploaded: {uploaded_file.name}")

    if 'mockup_files' not in current_data:
        current_data['mockup_files'] = []
    current_data['mockup_files'].extend(saved_files)

# Display uploaded mockups
if current_data.get('mockup_files'):
    st.subheader("Uploaded Mockups")
    for file_path in current_data['mockup_files'][-5:]:  # Show last 5
        st.write(f"📎 {file_path.split('/')[-1]}")

# Materials Needed
st.markdown("---")
st.header("5. Materials & Resources")

materials = st.text_area(
    "List materials and resources needed",
    value=current_data.get('materials', ''),
    placeholder="• Design tool: Figma\n• Team members: Designer, Developer\n• Time needed: 2 days",
    height=100
)

# Save
if st.button("Save Prototype Stage", type="primary"):
    data = {
        'description': prototype_desc,
        'type': prototype_type,
        'user_flow': user_flow,
        'features': features,
        'materials': materials,
        'mockup_files': current_data.get('mockup_files', [])
    }

    create_or_update_stage_progress(
        db=db,
        project_id=project_id,
        stage_number=4,
        status="in_progress",
        data=data
    )

    st.success("✅ Prototype stage progress saved!")

# Complete
if st.button("Mark Prototype Stage as Complete"):
    create_or_update_stage_progress(
        db=db,
        project_id=project_id,
        stage_number=4,
        status="completed"
    )
    st.success("✅ Prototype stage complete! Proceed to Test.")

db.close()
