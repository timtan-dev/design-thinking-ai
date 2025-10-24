import streamlit as st
from config.database import get_db
from database.models import PrototypePage, SketchIteration, MockupIteration, Project, StageSummary
from services.ai_service import AIService
from datetime import datetime, timezone
from utils.time_utils import format_local_time
import os
from pathlib import Path

def render_prototype_page(project):
    """Main prototype page with page tabs and progressive steps"""
    st.markdown('<div style="margin-top: 2rem;"></div>', unsafe_allow_html=True)

    db = get_db()

    # Get or create prototype pages for this project
    prototype_pages = db.query(PrototypePage).filter(
        PrototypePage.project_id == project.id
    ).order_by(PrototypePage.order_index).all()

    # If no pages exist, create a default "Home" page
    if not prototype_pages:
        default_page = PrototypePage(
            project_id=project.id,
            page_name="Home",
            order_index=0
        )
        db.add(default_page)
        db.commit()
        prototype_pages = [default_page]

    # Level 1: Page Tabs
    page_names = [page.page_name for page in prototype_pages] + ["➕ Add Page"]

    # Use session state to track active page
    if 'active_prototype_page_index' not in st.session_state:
        st.session_state.active_prototype_page_index = 0

    selected_tab_index = st.session_state.active_prototype_page_index

    # Create tabs for each page
    tabs = st.tabs(page_names)

    # Render each tab
    for idx, tab in enumerate(tabs[:-1]):  # Exclude the "Add Page" tab
        with tab:
            render_page_content(prototype_pages[idx], project, db)

    # Handle "Add Page" tab
    with tabs[-1]:
        render_add_page_tab(project, db)

    db.close()

def render_page_content(prototype_page, project, db):
    """Render the content for a specific prototype page"""

    # Get ideate summary
    ideate_summary = db.query(StageSummary).filter(
        StageSummary.project_id == project.id,
        StageSummary.stage == "ideate"
    ).order_by(StageSummary.created_at.desc()).first()

    # Progress indicator
    render_progress_indicator(prototype_page)

    st.markdown("---")

    # Step 1: Sketch-to-Digital (Always visible)
    render_step_1_sketch(prototype_page, project, ideate_summary, db)

    # Step 2: AI-Assisted Mockup (Visible only if sketch finalized)
    if prototype_page.sketch_finalized:
        st.markdown("---")
        render_step_2_mockup(prototype_page, project, ideate_summary, db)

    # Step 3: HTML/CSS Generation (Visible only if mockup finalized)
    if prototype_page.mockup_finalized:
        st.markdown("---")
        render_step_3_code(prototype_page, project, db)

def render_progress_indicator(prototype_page):
    """Render the progress indicator showing which steps are complete"""
    st.markdown("### Process Progress")

    # Determine status for each step
    step1_status = "✅" if prototype_page.sketch_finalized else "●"
    step2_status = "✅" if prototype_page.mockup_finalized else ("●" if prototype_page.sketch_finalized else "○")
    step3_status = "✅" if prototype_page.code_generated else ("●" if prototype_page.mockup_finalized else "○")

    step1_line = "━━━━━━" if prototype_page.sketch_finalized else "━━━━━━"
    step2_line = "━━━━━━" if prototype_page.mockup_finalized else "━━━━━━"

    # Create progress display
    col1, col2, col3 = st.columns(3)

    with col1:
        if prototype_page.sketch_finalized:
            st.markdown(f"**{step1_status} Step 1: Sketch** ✓")
        else:
            st.markdown(f"**{step1_status} Step 1: Sketch**")

    with col2:
        if prototype_page.mockup_finalized:
            st.markdown(f"**{step2_status} Step 2: Mockup** ✓")
        elif prototype_page.sketch_finalized:
            st.markdown(f"**{step2_status} Step 2: Mockup**")
        else:
            st.markdown(f"**{step2_status} Step 2: Mockup** (locked)")

    with col3:
        if prototype_page.code_generated:
            st.markdown(f"**{step3_status} Step 3: Code** ✓")
        elif prototype_page.mockup_finalized:
            st.markdown(f"**{step3_status} Step 3: Code**")
        else:
            st.markdown(f"**{step3_status} Step 3: Code** (locked)")

def render_step_1_sketch(prototype_page, project, ideate_summary, db):
    """Render Step 1: Sketch-to-Digital"""
    from pages.prototype_steps.step1_sketch import render_sketch_step
    render_sketch_step(prototype_page, project, ideate_summary, db)

def render_step_2_mockup(prototype_page, project, ideate_summary, db):
    """Render Step 2: AI-Assisted Mockup"""
    from pages.prototype_steps.step2_mockup import render_mockup_step
    render_mockup_step(prototype_page, project, ideate_summary, db)

def render_step_3_code(prototype_page, project, db):
    """Render Step 3: HTML/CSS Generation"""
    from pages.prototype_steps.step3_code import render_code_step
    render_code_step(prototype_page, project, db)

def render_add_page_tab(project, db):
    """Render the 'Add Page' tab content"""
    st.markdown("### Add New Prototype Page")
    st.markdown("Create additional pages for your prototype (e.g., Profile, Settings, etc.)")

    new_page_name = st.text_input(
        "Page Name",
        placeholder="e.g., Profile, Settings, Dashboard",
        key="new_page_name_input"
    )

    if st.button("➕ Create Page", type="primary", use_container_width=True):
        if new_page_name.strip():
            # Check if page name already exists
            existing = db.query(PrototypePage).filter(
                PrototypePage.project_id == project.id,
                PrototypePage.page_name == new_page_name.strip()
            ).first()

            if existing:
                st.error(f"Page '{new_page_name}' already exists!")
            else:
                # Get max order index
                max_order = db.query(PrototypePage).filter(
                    PrototypePage.project_id == project.id
                ).count()

                # Create new page
                new_page = PrototypePage(
                    project_id=project.id,
                    page_name=new_page_name.strip(),
                    order_index=max_order
                )
                db.add(new_page)
                db.commit()

                st.success(f"✅ Page '{new_page_name}' created!")
                st.rerun()
        else:
            st.warning("Please enter a page name")
