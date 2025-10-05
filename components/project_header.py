"""
Project Header Component
Display current project information
"""

import streamlit as st

def display_project_header():
    """Display project information header"""
    if not st.session_state.get('current_project'):
        return

    project = st.session_state.current_project

    with st.container():
        st.markdown(f"""
        <div style="background-color: #f0f2f6; padding: 1rem; border-radius: 0.5rem; margin-bottom: 1rem;">
            <h3 style="margin: 0;">📁 {project['name']}</h3>
            <p style="margin: 0.5rem 0 0 0;">
                <strong>Area:</strong> {project['area']} |
                <strong>Goal:</strong> {project['goal'][:100]}{'...' if len(project['goal']) > 100 else ''}
            </p>
        </div>
        """, unsafe_allow_html=True)
