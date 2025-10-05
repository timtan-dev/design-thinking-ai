"""
Empathise Stage - User Research and Analysis
Collect data and analyze to understand users
"""

import streamlit as st
from components.project_header import display_project_header
from components.cards.collect_card import collect_data_card
from components.cards.analyse_card import analyse_data_card
from utils.session_manager import require_project

st.set_page_config(page_title="Empathise - Design Thinking AI", page_icon="💭", layout="wide")

# Require project to be selected
if not require_project():
    st.stop()

st.title("💭 Stage 1: Empathise")
st.markdown("**Understand your users through research and analysis**")

# Display project header
display_project_header()

st.markdown("---")

# Two column layout
col1, col2 = st.columns(2)

with col1:
    st.header("📊 Collect Data")
    st.markdown("Gather insights through various research methods")

    # Research methods
    methods = [
        ("Interview", "conduct in-depth one-on-one conversations"),
        ("Survey", "gather quantitative data from many users"),
        ("Ethnography", "observe users in their natural environment"),
        ("Focus Group", "facilitate group discussions"),
        ("Observation", "watch users interact with products/services"),
        ("Diary Study", "track user experiences over time")
    ]

    for method_name, description in methods:
        collect_data_card(method_name, description)

with col2:
    st.header("🔍 Analyse Data")
    st.markdown("Transform raw data into actionable insights")

    # Analysis methods
    analysis_methods = [
        ("Empathy Map", "understand what users think, feel, say, and do"),
        ("Persona", "create representative user archetypes"),
        ("Journey Map", "visualize user experience over time"),
        ("Affinity Map", "group insights into themes"),
        ("Storytelling", "craft narratives from user data"),
        ("Stakeholder Map", "identify all involved parties")
    ]

    for method_name, description in analysis_methods:
        analyse_data_card(method_name, description)

st.markdown("---")

# Stage completion
if st.button("Mark Empathise Stage as Complete", type="primary"):
    from config.database import get_db
    from database.crud.stages import create_or_update_stage_progress

    project_id = st.session_state.current_project['id']
    db = get_db()

    create_or_update_stage_progress(
        db=db,
        project_id=project_id,
        stage_number=1,
        status="completed"
    )

    db.close()
    st.success("✅ Empathise stage marked as complete! Proceed to Define stage.")
