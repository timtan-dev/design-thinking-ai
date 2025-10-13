# utils/project_tabs.py

from datetime import datetime
import streamlit as st
from database.models import Project
from config.database import get_db

STAGES = {
    1: {"name": "Empathise", "icon": "💭", "indicator": "🟢"},
    2: {"name": "Define", "icon": "📋", "indicator": "🔴"},
    3: {"name": "Ideate", "icon": "💡", "indicator": "🟡"},
    4: {"name": "Prototype", "icon": "🔨", "indicator": "🟣"},
    5: {"name": "Test", "icon": "🧪", "indicator": "🔵"},
    6: {"name": "Implement", "icon": "✅", "indicator": "✅"}
}


def render_project_header(project):
    """Render the project header section"""
    st.markdown(f"""
        <div class="project-header">
            <div class="project-title">{project.name}</div>
            <div class="project-info">
                <div class="project-info-item">
                    <span>📍</span>
                    <span>{project.area}</span>
                </div>
                <div class="project-info-item">
                    <span>🎯</span>
                    <span>{project.goal}</span>
                </div>
            </div>
        </div>
    """, unsafe_allow_html=True)

def render_stage_tabs(current_stage):
    from utils.project_tabs import update_project_stage  # avoid circular import
    cols = st.columns(6)
    for idx, (stage_num, stage_info) in enumerate(STAGES.items()):
        with cols[idx]:
            if st.button(
                f"{stage_num}\n{stage_info['name']}",
                key=f"stage_tab_{stage_num}",
                use_container_width=True,
                type="primary" if stage_num == current_stage else "secondary"
            ):
                st.session_state.current_stage = stage_num
                update_project_stage(st.session_state.current_project_id, stage_num)
                st.rerun()

def update_project_stage(project_id, stage):
    db = get_db()
    try:
        project = db.query(Project).filter(Project.id == project_id).first()
        if project:
            project.current_stage = stage
            project.updated_at = datetime.utcnow()
            db.commit()
    except Exception as e:
        db.rollback()
        st.error(f"Error updating stage: {str(e)}")
    finally:
        db.close()
