"""
Session Manager
Manage Streamlit session state
"""

import streamlit as st
from typing import Dict, Any, Optional

def initialize_session_state():
    """Initialize session state variables"""
    if 'current_project' not in st.session_state:
        st.session_state.current_project = None

    if 'user_id' not in st.session_state:
        st.session_state.user_id = None

def set_current_project(project: Dict[str, Any]):
    """
    Set current project in session state

    Args:
        project: Project dictionary with id, name, area, goal
    """
    st.session_state.current_project = project

def get_current_project() -> Optional[Dict[str, Any]]:
    """
    Get current project from session state

    Returns:
        Project dictionary or None
    """
    return st.session_state.get('current_project')

def clear_current_project():
    """Clear current project from session state"""
    st.session_state.current_project = None

def require_project() -> bool:
    """
    Check if a project is selected, show warning if not

    Returns:
        True if project exists, False otherwise
    """
    if not st.session_state.get('current_project'):
        st.warning("⚠️ Please select or create a project from the Home page first.")
        st.info("Navigate to **Home** to get started.")
        return False
    return True

def set_stage_data(stage_number: int, data: Dict[str, Any]):
    """
    Store stage-specific data in session state

    Args:
        stage_number: Stage number (1-6)
        data: Stage data dictionary
    """
    key = f'stage_{stage_number}_data'
    st.session_state[key] = data

def get_stage_data(stage_number: int) -> Optional[Dict[str, Any]]:
    """
    Get stage-specific data from session state

    Args:
        stage_number: Stage number (1-6)

    Returns:
        Stage data dictionary or None
    """
    key = f'stage_{stage_number}_data'
    return st.session_state.get(key)

def clear_all_session_data():
    """Clear all session data"""
    for key in list(st.session_state.keys()):
        del st.session_state[key]
    initialize_session_state()
