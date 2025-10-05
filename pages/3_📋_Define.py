"""
Define Stage - Problem Statement and Focus
Define the core problem to solve
"""

import streamlit as st
from components.project_header import display_project_header
from utils.session_manager import require_project
from services.ai_service import AIService
from config.database import get_db
from database.crud.stages import create_or_update_stage_progress, get_stage_progress

st.set_page_config(page_title="Define - Design Thinking AI", page_icon="📋", layout="wide")

# Require project
if not require_project():
    st.stop()

st.title("📋 Stage 2: Define")
st.markdown("**Frame the problem you're solving**")

display_project_header()

st.markdown("---")

project_id = st.session_state.current_project['id']
db = get_db()
stage_data = get_stage_progress(db, project_id, 2)
current_data = stage_data.data if stage_data and stage_data.data else {}

# Problem Statement
st.header("1. Problem Statement")
st.markdown("Define the core problem based on your research insights")

problem_statement = st.text_area(
    "Problem Statement",
    value=current_data.get('problem_statement', ''),
    placeholder="[User] needs [need] because [insight]",
    help="A clear, user-centered problem statement",
    height=100
)

if st.button("Generate Problem Statement with AI", key="gen_problem"):
    with st.spinner("Generating problem statement..."):
        ai_service = AIService()
        generated = ai_service.generate_problem_statement(st.session_state.current_project)
        st.success("Generated Problem Statement:")
        st.write(generated)

# How Might We Questions
st.markdown("---")
st.header("2. How Might We (HMW) Questions")
st.markdown("Reframe the problem as opportunities for innovation")

hmw_questions = st.text_area(
    "How Might We Questions",
    value=current_data.get('hmw_questions', ''),
    placeholder="How might we...\n• Question 1\n• Question 2\n• Question 3",
    height=150
)

if st.button("Generate HMW Questions with AI", key="gen_hmw"):
    with st.spinner("Generating HMW questions..."):
        ai_service = AIService()
        generated = ai_service.generate_hmw_questions(st.session_state.current_project, problem_statement)
        st.success("Generated HMW Questions:")
        st.write(generated)

# Point of View Statement
st.markdown("---")
st.header("3. Point of View (POV) Statement")
st.markdown("Synthesize your understanding into a focused perspective")

pov_statement = st.text_area(
    "POV Statement",
    value=current_data.get('pov_statement', ''),
    placeholder="We met [user]. We were surprised to discover [insight]. We wonder if [question].",
    height=100
)

# Save progress
if st.button("Save Define Stage", type="primary"):
    data = {
        'problem_statement': problem_statement,
        'hmw_questions': hmw_questions,
        'pov_statement': pov_statement
    }

    create_or_update_stage_progress(
        db=db,
        project_id=project_id,
        stage_number=2,
        status="in_progress",
        data=data
    )

    st.success("✅ Define stage progress saved!")

# Complete stage
if st.button("Mark Define Stage as Complete"):
    create_or_update_stage_progress(
        db=db,
        project_id=project_id,
        stage_number=2,
        status="completed"
    )
    st.success("✅ Define stage complete! Proceed to Ideate.")

db.close()
