"""
Stage Tabs Component
Display clickable stage navigation tabs
"""

import streamlit as st

def display_stage_tabs(current_stage: int = 1):
    """
    Display stage navigation tabs

    Args:
        current_stage: Current active stage number (1-6)
    """
    stages = [
        ("💭", "Empathise"),
        ("📋", "Define"),
        ("💡", "Ideate"),
        ("🔨", "Prototype"),
        ("🧪", "Test"),
        ("🚀", "Implement")
    ]

    cols = st.columns(6)

    for i, (emoji, name) in enumerate(stages, 1):
        with cols[i-1]:
            if i == current_stage:
                st.markdown(f"""
                <div style="background-color: #0068c9; color: white; padding: 0.5rem;
                            border-radius: 0.5rem; text-align: center;">
                    <div style="font-size: 1.5rem;">{emoji}</div>
                    <div style="font-size: 0.8rem; font-weight: bold;">{name}</div>
                </div>
                """, unsafe_allow_html=True)
            else:
                st.markdown(f"""
                <div style="background-color: #f0f2f6; padding: 0.5rem;
                            border-radius: 0.5rem; text-align: center; cursor: pointer;">
                    <div style="font-size: 1.5rem;">{emoji}</div>
                    <div style="font-size: 0.8rem;">{name}</div>
                </div>
                """, unsafe_allow_html=True)
