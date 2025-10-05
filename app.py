"""
Design Thinking AI Agent - Main Application
Streamlit app with multi-page navigation and project management
"""

import streamlit as st
from config.database import init_db
from config.settings import Settings
from utils.session_manager import initialize_session_state

# Page configuration
st.set_page_config(
    page_title="Design Thinking AI Agent",
    page_icon="🎨",
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

# Initialize
def main():
    """Main application entry point"""
    # Initialize database
    init_db()

    # Initialize session state
    initialize_session_state()

    # Load custom styles
    load_css()

    # Welcome message
    st.sidebar.title("🎨 Design Thinking AI")
    st.sidebar.markdown("---")

    # Display current project if selected
    if st.session_state.get('current_project'):
        project = st.session_state.current_project
        st.sidebar.success(f"**Current Project:** {project['name']}")
        st.sidebar.markdown(f"**Area:** {project['area']}")
    else:
        st.sidebar.info("No project selected. Go to Home to create or select a project.")

    st.sidebar.markdown("---")
    st.sidebar.markdown("""
    ### Navigation
    Use the pages above to navigate through the Design Thinking stages:

    1. 🏠 **Home** - Project Management
    2. 💭 **Empathise** - User Research
    3. 📋 **Define** - Problem Definition
    4. 💡 **Ideate** - Idea Generation
    5. 🔨 **Prototype** - Build Solutions
    6. 🧪 **Test** - Validate Ideas
    7. 🚀 **Implement** - Launch Plan
    """)

    # Main content
    st.title("Welcome to Design Thinking AI Agent")
    st.markdown("""
    This AI-powered tool guides you through the complete Design Thinking process,
    helping you innovate and solve problems systematically.

    ### Getting Started
    1. Navigate to **Home** to create a new project or select an existing one
    2. Follow the Design Thinking stages from **Empathise** to **Implement**
    3. Use AI assistance at each stage to generate insights and content

    ### Features
    - 📊 Structured research data collection and analysis
    - 🤖 AI-powered template generation
    - 💾 Automatic progress saving
    - 📄 Export comprehensive reports
    - 🔄 Collaborative project management
    """)

if __name__ == "__main__":
    main()
