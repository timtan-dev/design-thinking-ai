"""
Custom File Uploader Component
Enhanced file upload with drag-drop styling
"""

import streamlit as st

def custom_file_uploader(label: str, file_types: list = None, key: str = None):
    """
    Custom styled file uploader

    Args:
        label: Upload field label
        file_types: Allowed file types
        key: Unique key for the uploader

    Returns:
        Uploaded file object or None
    """
    st.markdown(f"""
    <div style="border: 2px dashed #0068c9; border-radius: 0.5rem; padding: 2rem;
                text-align: center; background-color: #f0f8ff; margin: 1rem 0;">
        <p style="margin: 0; color: #0068c9; font-weight: bold;">📤 {label}</p>
        <p style="margin: 0.5rem 0 0 0; font-size: 0.8rem; color: #666;">
            Drag and drop or click to browse
        </p>
    </div>
    """, unsafe_allow_html=True)

    return st.file_uploader(
        label,
        type=file_types,
        key=key,
        label_visibility="collapsed"
    )
