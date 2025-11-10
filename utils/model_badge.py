"""
Model Badge Utility
Helper functions for displaying AI model information
"""

import streamlit as st

# Model display names
MODEL_DISPLAY_NAMES = {
    "gpt-5": "GPT-5",
    "gpt-4.1": "GPT-4.1",
    "claude-sonnet-4-5-20250929": "Claude Sonnet 4.5",
    "grok-4": "Grok 4",
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
