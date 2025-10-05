"""
Home Page - Project Management
Create new projects and select existing ones
"""

import streamlit as st
from config.database import get_db
from database.crud.projects import create_project, list_projects, get_project
from database.crud.stages import initialize_project_stages
from utils.session_manager import set_current_project

st.set_page_config(page_title="Home - Design Thinking AI", page_icon="🏠", layout="wide")

st.title("🏠 Home - Project Management")

# Tabs for Create and Select
tab1, tab2 = st.tabs(["Create New Project", "Select Existing Project"])

with tab1:
    st.subheader("Create a New Design Thinking Project")

    with st.form("create_project_form"):
        project_name = st.text_input(
            "Project Name",
            placeholder="e.g., Mobile Banking App Redesign",
            help="Choose a descriptive name for your project"
        )

        project_area = st.text_input(
            "Project Area/Domain",
            placeholder="e.g., Financial Services, Healthcare, Education",
            help="What domain or industry does this project belong to?"
        )

        project_goal = st.text_area(
            "Project Goal",
            placeholder="Describe what you want to achieve with this project...",
            help="What problem are you trying to solve or what opportunity are you exploring?",
            height=150
        )

        submitted = st.form_submit_button("Create Project", type="primary", use_container_width=True)

        if submitted:
            if not project_name or not project_area or not project_goal:
                st.error("Please fill in all fields to create a project.")
            else:
                try:
                    db = get_db()

                    # Create project
                    new_project = create_project(
                        db=db,
                        name=project_name,
                        area=project_area,
                        goal=project_goal
                    )

                    # Initialize stages
                    initialize_project_stages(db, new_project.id)

                    # Set as current project
                    set_current_project({
                        'id': new_project.id,
                        'name': new_project.name,
                        'area': new_project.area,
                        'goal': new_project.goal
                    })

                    st.success(f"✅ Project '{project_name}' created successfully!")
                    st.info("Navigate to **Empathise** stage to begin your Design Thinking journey.")

                    db.close()

                except Exception as e:
                    st.error(f"Error creating project: {str(e)}")

with tab2:
    st.subheader("Select an Existing Project")

    try:
        db = get_db()
        projects = list_projects(db)

        if not projects:
            st.info("No projects found. Create a new project in the 'Create New Project' tab.")
        else:
            # Display projects as cards
            for project in projects:
                with st.container():
                    col1, col2, col3 = st.columns([3, 2, 1])

                    with col1:
                        st.markdown(f"### {project.name}")
                        st.markdown(f"**Area:** {project.area}")

                    with col2:
                        st.markdown(f"**Created:** {project.created_at.strftime('%Y-%m-%d')}")
                        st.markdown(f"**Updated:** {project.updated_at.strftime('%Y-%m-%d')}")

                    with col3:
                        if st.button("Select", key=f"select_{project.id}", use_container_width=True):
                            set_current_project({
                                'id': project.id,
                                'name': project.name,
                                'area': project.area,
                                'goal': project.goal
                            })
                            st.success(f"Selected project: {project.name}")
                            st.rerun()

                    with st.expander("View Goal"):
                        st.write(project.goal)

                    st.markdown("---")

        db.close()

    except Exception as e:
        st.error(f"Error loading projects: {str(e)}")

# Display current project info
if st.session_state.get('current_project'):
    st.markdown("---")
    st.subheader("Current Project")

    project = st.session_state.current_project

    col1, col2 = st.columns(2)
    with col1:
        st.info(f"**Name:** {project['name']}")
        st.info(f"**Area:** {project['area']}")

    with col2:
        st.info(f"**Goal:** {project['goal']}")

    if st.button("Clear Selection"):
        st.session_state.current_project = None
        st.rerun()
