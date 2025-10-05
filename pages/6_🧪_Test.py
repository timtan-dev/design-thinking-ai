"""
Test Stage - Validate Solutions with Users
Test prototypes and gather feedback
"""

import streamlit as st
from components.project_header import display_project_header
from utils.session_manager import require_project
from services.ai_service import AIService
from config.database import get_db
from database.crud.stages import create_or_update_stage_progress, get_stage_progress

st.set_page_config(page_title="Test - Design Thinking AI", page_icon="🧪", layout="wide")

if not require_project():
    st.stop()

st.title("🧪 Stage 5: Test")
st.markdown("**Validate your prototype with real users**")

display_project_header()

st.markdown("---")

project_id = st.session_state.current_project['id']
db = get_db()
stage_data = get_stage_progress(db, project_id, 5)
current_data = stage_data.data if stage_data and stage_data.data else {}

# Test Plan
st.header("1. Test Plan")

col1, col2 = st.columns(2)

with col1:
    test_objectives = st.text_area(
        "Test Objectives",
        value=current_data.get('objectives', ''),
        placeholder="What do you want to learn from testing?\n• Objective 1\n• Objective 2",
        height=150
    )

with col2:
    test_participants = st.text_area(
        "Target Participants",
        value=current_data.get('participants', ''),
        placeholder="Who will test the prototype?\n• Persona 1: 5 users\n• Persona 2: 3 users",
        height=150
    )

# Test Scenarios
st.markdown("---")
st.header("2. Test Scenarios")

test_scenarios = st.text_area(
    "Test Scenarios",
    value=current_data.get('scenarios', ''),
    placeholder="Scenario 1: Ask user to complete task X\nScenario 2: Ask user to find feature Y\n...",
    height=150
)

if st.button("Generate Test Scenarios with AI"):
    with st.spinner("Generating test scenarios..."):
        ai_service = AIService()
        generated = ai_service.generate_test_scenarios(st.session_state.current_project)
        st.success("AI-Generated Test Scenarios:")
        st.write(generated)

# Feedback Collection
st.markdown("---")
st.header("3. Collect Feedback")

if 'feedback_entries' not in current_data:
    current_data['feedback_entries'] = []

with st.form("feedback_form"):
    st.subheader("Add Feedback Entry")

    participant_id = st.text_input("Participant ID", placeholder="P1, P2, etc.")
    feedback_text = st.text_area("Feedback", placeholder="What did the participant say/observe?", height=100)
    feedback_type = st.selectbox("Type", ["Positive", "Negative", "Suggestion", "Observation"])

    submitted = st.form_submit_button("Add Feedback")

    if submitted and participant_id and feedback_text:
        current_data['feedback_entries'].append({
            'participant': participant_id,
            'feedback': feedback_text,
            'type': feedback_type
        })
        st.success("Feedback added!")

# Display feedback
if current_data.get('feedback_entries'):
    st.subheader("Collected Feedback")
    for i, entry in enumerate(current_data['feedback_entries']):
        emoji = {"Positive": "✅", "Negative": "❌", "Suggestion": "💡", "Observation": "👁️"}
        st.write(f"{emoji.get(entry['type'], '📝')} **{entry['participant']}**: {entry['feedback']}")

# Results Analysis
st.markdown("---")
st.header("4. Results Analysis")

col1, col2 = st.columns(2)

with col1:
    what_worked = st.text_area(
        "What Worked Well",
        value=current_data.get('what_worked', ''),
        placeholder="• Feature X was intuitive\n• Users completed task quickly",
        height=150
    )

with col2:
    what_failed = st.text_area(
        "What Didn't Work",
        value=current_data.get('what_failed', ''),
        placeholder="• Feature Y was confusing\n• Users couldn't find Z",
        height=150
    )

# Insights and Next Steps
st.markdown("---")
st.header("5. Key Insights & Next Steps")

insights = st.text_area(
    "Key Insights",
    value=current_data.get('insights', ''),
    placeholder="What did you learn from testing?",
    height=100
)

next_steps = st.text_area(
    "Next Steps",
    value=current_data.get('next_steps', ''),
    placeholder="What changes will you make based on feedback?\n• Iteration 1\n• Iteration 2",
    height=100
)

if st.button("Analyze Feedback with AI"):
    with st.spinner("Analyzing feedback..."):
        ai_service = AIService()
        feedback_text = "\n".join([f"{e['type']}: {e['feedback']}" for e in current_data.get('feedback_entries', [])])
        analysis = ai_service.analyze_test_feedback(st.session_state.current_project, feedback_text)
        st.success("AI Analysis:")
        st.write(analysis)

# Save
if st.button("Save Test Stage", type="primary"):
    data = {
        'objectives': test_objectives,
        'participants': test_participants,
        'scenarios': test_scenarios,
        'feedback_entries': current_data.get('feedback_entries', []),
        'what_worked': what_worked,
        'what_failed': what_failed,
        'insights': insights,
        'next_steps': next_steps
    }

    create_or_update_stage_progress(
        db=db,
        project_id=project_id,
        stage_number=5,
        status="in_progress",
        data=data
    )

    st.success("✅ Test stage progress saved!")

# Complete
if st.button("Mark Test Stage as Complete"):
    create_or_update_stage_progress(
        db=db,
        project_id=project_id,
        stage_number=5,
        status="completed"
    )
    st.success("✅ Test stage complete! Proceed to Implement.")

db.close()
