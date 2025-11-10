"""
Model Badge Utility
Helper functions for displaying AI model information
"""

import streamlit as st

# Model display names
MODEL_DISPLAY_NAMES = {
    "gpt-4o": "GPT-4o",
    "gpt-4o-mini": "GPT-4o Mini",
    "o1": "o1",
    "o1-mini": "o1 Mini",
    "gpt-4.1": "GPT-4.1",  # Legacy model
}

def display_model_badge(model_name: str):
    """
    Display a badge showing which AI model was used

    Args:
        model_name: The model identifier (e.g., "gpt-4o", "gpt-4o-mini")
    """
    if not model_name:
        # Show empty badge for legacy content without model info
        st.markdown(
            '<div class="model-badge model-badge-empty">Model: Not tracked</div>',
            unsafe_allow_html=True
        )
        return

    display_name = MODEL_DISPLAY_NAMES.get(model_name, model_name)

    st.markdown(
        f'<div class="model-badge">🤖 Model: <strong>{display_name}</strong></div>',
        unsafe_allow_html=True
    )

def get_model_display_name(model_name: str) -> str:
    """
    Get the display name for a model

    Args:
        model_name: The model identifier

    Returns:
        Human-readable model name
    """
    if not model_name:
        return "Not tracked"
    return MODEL_DISPLAY_NAMES.get(model_name, model_name)
