"""
Progress Tracker Component
Visual progress indicator for all stages
"""

import streamlit as st
from config.database import get_db
from database.crud.stages import get_all_stage_progress

def display_progress_tracker(project_id: int):
    """
    Display visual progress for all stages

    Args:
        project_id: Project ID
    """
    db = get_db()
    stages = get_all_stage_progress(db, project_id)
    db.close()

    stage_names = ["Empathise", "Define", "Ideate", "Prototype", "Test", "Implement"]

    # Create progress dictionary
    progress_dict = {}
    for stage in stages:
        progress_dict[stage.stage_number] = stage.status

    # Display progress
    st.markdown("### Project Progress")

    cols = st.columns(6)

    for i in range(1, 7):
        status = progress_dict.get(i, "not_started")

        emoji = {
            "completed": "✅",
            "in_progress": "🔄",
            "not_started": "⭕"
        }.get(status, "⭕")

        color = {
            "completed": "#28a745",
            "in_progress": "#ffc107",
            "not_started": "#6c757d"
        }.get(status, "#6c757d")

        with cols[i-1]:
            st.markdown(f"""
            <div style="text-align: center;">
                <div style="font-size: 2rem;">{emoji}</div>
                <div style="color: {color}; font-size: 0.7rem; font-weight: bold;">
                    {stage_names[i-1]}
                </div>
            </div>
            """, unsafe_allow_html=True)
