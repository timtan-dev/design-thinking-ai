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
    """Render the project header section with model selection"""

    # Create two columns: project info (left) and model selector (right)
    col1, col2 = st.columns([3, 1])

    with col1:
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

    with col2:
        # Model selection dropdown
        st.markdown("#### AI Model")
        available_models = {
            "gpt-5": "GPT-5",
            "gpt-4.1": "GPT-4.1",
            "o1": "o1",
            "o1-mini": "o1 Mini",
            "claude-sonnet-4.5-20250514": "Claude Sonnet 4.5",
            "grok-4": "Grok 4",
        }

        # Get current model or default
        current_model = project.preferred_model if project.preferred_model else "gpt-4o"

        # Display model selector
        selected_model = st.selectbox(
            "Select Model",
            options=list(available_models.keys()),
            format_func=lambda x: available_models[x],
            index=list(available_models.keys()).index(current_model) if current_model in available_models else 0,
            key=f"model_selector_{project.id}",
            label_visibility="collapsed"
        )

        # Update project model if changed
        if selected_model != current_model:
            update_project_model(project.id, selected_model)

def render_stage_tabs(current_stage):
    from utils.project_tabs import update_project_stage  # avoid circular import
    st.markdown('### Stages')

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

def update_project_model(project_id, model):
    """Update the preferred AI model for a project"""
    db = get_db()
    try:
        project = db.query(Project).filter(Project.id == project_id).first()
        if project:
            project.preferred_model = model
            project.updated_at = datetime.utcnow()
            db.commit()
            st.success(f"✅ Model updated to {model}")
            st.rerun()
    except Exception as e:
        db.rollback()
        st.error(f"Error updating model: {str(e)}")
    finally:
        db.close()
