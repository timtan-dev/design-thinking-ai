"""
Design Thinking AI Agent - Main Application
Single-page app with sidebar navigation and purple gradient theme
"""

import streamlit as st
from datetime import datetime
from config.database import init_db, get_db
from database.models import Project, ResearchData, GeneratedContent
from utils.session_manager import initialize_session_state
from utils.project_tabs import render_project_header, render_stage_tabs, update_project_stage
from pages.empathise import render_empathise_page
from pages.define import render_define_page
from pages.ideate import render_ideate_page
from pages.prototype import render_prototype_page
from pages.test import render_test_page
from pages.implement import render_implement_page

import os

# Page configuration
st.set_page_config(
    page_title="Design Thinking AI Agent",
    page_icon="🧠",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Load custom CSS
def load_css():
    """Load custom CSS styles"""
    try:
        with open('assets/styles/main.css') as f:
            st.markdown(f'<style>{f.read()}</style>', unsafe_allow_html=True)
    except FileNotFoundError:
        pass

# Stage configuration
STAGES = {
    1: {"name": "Empathise", "icon": "💭", "indicator": "🟢"},
    2: {"name": "Define", "icon": "📋", "indicator": "🔴"},
    3: {"name": "Ideate", "icon": "💡", "indicator": "🟡"},
    4: {"name": "Prototype", "icon": "🔨", "indicator": "🟣"},
    5: {"name": "Test", "icon": "🧪", "indicator": "🔵"},
    6: {"name": "Implement", "icon": "✅", "indicator": "✅"}
}

def render_sidebar():
    """Render the sidebar with project list and navigation"""
    with st.sidebar:
        # Sidebar header
        st.title("🧠 Design Thinking AI")

        # New project button
        if st.button("➕ New Project", key="new_project_btn", use_container_width=True):
            open_new_project_dialog()

        # Search bar
        st.markdown("---")
        # search_query = st.text_input("🔍 Search projects", key="search_projects", label_visibility="collapsed", placeholder="Search projects...")

        # Get all projects from database
        db = get_db()
        projects = db.query(Project).order_by(Project.updated_at.desc()).all()
        db.close()

        # Display projects
        if projects:
            # st.title("Recent Projects")

            st.markdown('## Project List')
            for project in projects:
                render_project_item(project)



        if not projects:
            st.info("No projects yet. Create your first project!")

@st.dialog('Create New Project')
def open_new_project_dialog():
    """Display a popup dialog for creating a new project"""
    name = st.text_input("Project Name")
    area = st.text_input("Area/Domain")
    goal = st.text_area("Goal")

    submit = st.button("Create", use_container_width=True)

    if submit and name and area and goal:
        create_project(name, area, goal)
        st.rerun()


def render_project_item(project):
    """Render a single project item in the sidebar"""
    is_active = st.session_state.get('current_project_id') == project.id
    active_class = "active" if is_active else ""

    stage_info = STAGES.get(project.current_stage, STAGES[1])
    stage_indicator = stage_info['indicator']
    stage_name = stage_info['name']

    # Format date
    last_modified = project.updated_at.strftime("%b %d, %Y")

    # Create clickable project item
    if st.button(
        f"{project.name}",
        key=f"project_{project.id}",
        use_container_width=True,
        type="secondary" if not is_active else "primary"
    ):
        st.session_state.current_project_id = project.id
        st.session_state.current_stage = project.current_stage
        st.rerun()

    # Show metadata below button
    st.caption(f"{stage_indicator} {stage_name} • {last_modified}")

def create_project(name, area, goal):
    """Create a new project in the database"""
    db = get_db()
    try:
        new_project = Project(
            name=name,
            area=area,
            goal=goal,
            current_stage=1
        )
        db.add(new_project)
        db.commit()
        db.refresh(new_project)

        # Set as current project
        st.session_state.current_project_id = new_project.id
        st.session_state.current_stage = 1
        st.success(f"Project '{name}' created successfully!")
    except Exception as e:
        db.rollback()
        st.error(f"Error creating project: {str(e)}")
    finally:
        db.close()

def get_current_project():
    """Get the current project from database"""
    project_id = st.session_state.get('current_project_id')
    if not project_id:
        return None

    db = get_db()
    project = db.query(Project).filter(Project.id == project_id).first()
    db.close()
    return project


def render_placeholder_stage(stage_name):
    """Render placeholder for other stages"""
    st.markdown(f"""
        <div class="section-header">
            <span class="section-icon">{STAGES[st.session_state.current_stage]['icon']}</span>
            <span class="section-title">{stage_name} Stage</span>
        </div>
    """, unsafe_allow_html=True)

    st.info(f"🚧 The {stage_name} stage is coming soon! Currently implementing Empathise and Define stages.")


def main():
    """Main application entry point"""
    # Initialize database
    init_db()

    # Initialize session state
    initialize_session_state()

    # Load custom styles
    load_css()

    # Render sidebar
    render_sidebar()

    # Get current project
    current_project = get_current_project()

    # Main content
    if not current_project:
        # No project selected - show welcome screen
        st.title("Welcome to Design Thinking AI Agent 🧠")
        st.markdown("""
        ### Get Started

        This AI-powered tool guides you through the complete Design Thinking process,
        helping you innovate and solve problems systematically.

        **👈 Create a new project or select an existing one from the sidebar to begin!**

        ### The 6 Stages of Design Thinking

        1. **💭 Empathise** - Understand your users through research
        2. **📋 Define** - Analyze data and define the problem
        3. **💡 Ideate** - Generate creative solutions
        4. **🔨 Prototype** - Build tangible representations
        5. **🧪 Test** - Validate your solutions with users
        6. **✅ Implement** - Create an implementation plan

        ### Features
        - 📊 Structured research data collection
        - 🤖 AI-powered insights and analysis
        - 💾 Automatic progress tracking
        - 📄 Export comprehensive reports
        """)
    else:
        # Project selected - show project interface
        render_project_header(current_project)

        # Render stage tabs
        current_stage = st.session_state.get('current_stage', current_project.current_stage)
        render_stage_tabs(current_stage)

        # Render stage content
        if current_stage == 1:
            render_empathise_page(current_project)
        elif current_stage == 2:
            render_define_page(current_project)
        elif current_stage == 3:
            render_ideate_page(current_project)
        elif current_stage == 4:
            render_prototype_page(current_project)
        elif current_stage == 5:
            render_test_page(current_project)
        elif current_stage == 6:
            render_implement_page(current_project)

if __name__ == "__main__":
    main()
