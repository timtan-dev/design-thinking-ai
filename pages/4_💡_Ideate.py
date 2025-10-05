"""
Ideate Stage - Generate and Evaluate Ideas
Brainstorm creative solutions
"""

import streamlit as st
from components.project_header import display_project_header
from utils.session_manager import require_project
from services.ai_service import AIService
from config.database import get_db
from database.crud.stages import create_or_update_stage_progress, get_stage_progress
import json

st.set_page_config(page_title="Ideate - Design Thinking AI", page_icon="💡", layout="wide")

if not require_project():
    st.stop()

st.title("💡 Stage 3: Ideate")
st.markdown("**Generate creative solutions to your defined problem**")

display_project_header()

st.markdown("---")

project_id = st.session_state.current_project['id']
db = get_db()
stage_data = get_stage_progress(db, project_id, 3)
current_data = stage_data.data if stage_data and stage_data.data else {}

# Brainstorming
st.header("1. Brainstorming")

col1, col2 = st.columns([2, 1])

with col1:
    ideas_text = st.text_area(
        "Ideas (one per line)",
        value=current_data.get('ideas', ''),
        placeholder="Enter your ideas here, one per line...",
        height=200
    )

with col2:
    st.markdown("**Brainstorming Tips:**")
    st.markdown("""
    - Quantity over quality
    - No criticism
    - Wild ideas welcome
    - Build on others' ideas
    - Stay focused on topic
    """)

if st.button("Generate Ideas with AI", key="gen_ideas"):
    with st.spinner("Generating ideas..."):
        ai_service = AIService()
        generated = ai_service.generate_ideas(st.session_state.current_project)
        st.success("AI-Generated Ideas:")
        st.write(generated)

# SCAMPER Method
st.markdown("---")
st.header("2. SCAMPER Method")
st.markdown("Apply systematic creativity techniques")

scamper_methods = {
    "Substitute": "What can you substitute?",
    "Combine": "What can you combine?",
    "Adapt": "What can you adapt?",
    "Modify": "What can you modify?",
    "Put to other uses": "How else can this be used?",
    "Eliminate": "What can you eliminate?",
    "Reverse": "What can you reverse?"
}

scamper_data = current_data.get('scamper', {})

for method, question in scamper_methods.items():
    scamper_data[method] = st.text_input(
        f"{method}: {question}",
        value=scamper_data.get(method, ''),
        key=f"scamper_{method}"
    )

# Idea Clustering
st.markdown("---")
st.header("3. Idea Clustering")

clusters = st.text_area(
    "Group similar ideas into clusters",
    value=current_data.get('clusters', ''),
    placeholder="Cluster 1: Theme Name\n- Idea 1\n- Idea 2\n\nCluster 2: Theme Name\n- Idea 3\n- Idea 4",
    height=150
)

# Idea Evaluation Matrix
st.markdown("---")
st.header("4. Idea Evaluation Matrix")
st.markdown("Evaluate ideas based on Impact vs. Feasibility")

if 'ideas_matrix' not in current_data:
    current_data['ideas_matrix'] = []

idea_name = st.text_input("Idea Name")
col1, col2 = st.columns(2)
with col1:
    impact = st.slider("Impact", 1, 10, 5, key="impact")
with col2:
    feasibility = st.slider("Feasibility", 1, 10, 5, key="feasibility")

if st.button("Add to Matrix"):
    if idea_name:
        current_data['ideas_matrix'].append({
            'name': idea_name,
            'impact': impact,
            'feasibility': feasibility
        })
        st.success(f"Added '{idea_name}' to evaluation matrix")

# Display matrix
if current_data.get('ideas_matrix'):
    st.subheader("Evaluation Matrix")
    for idea in current_data['ideas_matrix']:
        st.write(f"**{idea['name']}** - Impact: {idea['impact']}/10, Feasibility: {idea['feasibility']}/10")

# Save
if st.button("Save Ideate Stage", type="primary"):
    data = {
        'ideas': ideas_text,
        'scamper': scamper_data,
        'clusters': clusters,
        'ideas_matrix': current_data.get('ideas_matrix', [])
    }

    create_or_update_stage_progress(
        db=db,
        project_id=project_id,
        stage_number=3,
        status="in_progress",
        data=data
    )

    st.success("✅ Ideate stage progress saved!")

# Complete
if st.button("Mark Ideate Stage as Complete"):
    create_or_update_stage_progress(
        db=db,
        project_id=project_id,
        stage_number=3,
        status="completed"
    )
    st.success("✅ Ideate stage complete! Proceed to Prototype.")

db.close()
