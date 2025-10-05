"""
Implement Stage - Launch Plan and Reporting
Create implementation roadmap and final report
"""

import streamlit as st
from components.project_header import display_project_header
from utils.session_manager import require_project
from services.ai_service import AIService
from services.export_service import generate_final_report
from config.database import get_db
from database.crud.stages import create_or_update_stage_progress, get_stage_progress

st.set_page_config(page_title="Implement - Design Thinking AI", page_icon="🚀", layout="wide")

if not require_project():
    st.stop()

st.title("🚀 Stage 6: Implement")
st.markdown("**Plan and execute the launch of your solution**")

display_project_header()

st.markdown("---")

project_id = st.session_state.current_project['id']
db = get_db()
stage_data = get_stage_progress(db, project_id, 6)
current_data = stage_data.data if stage_data and stage_data.data else {}

# Implementation Roadmap
st.header("1. Implementation Roadmap")

roadmap = st.text_area(
    "Create an implementation timeline",
    value=current_data.get('roadmap', ''),
    placeholder="Phase 1 (Month 1-2): Development\n• Task 1\n• Task 2\n\nPhase 2 (Month 3): Testing\n• Task 3",
    height=200
)

if st.button("Generate Roadmap with AI"):
    with st.spinner("Generating implementation roadmap..."):
        ai_service = AIService()
        generated = ai_service.generate_implementation_roadmap(st.session_state.current_project)
        st.success("AI-Generated Roadmap:")
        st.write(generated)

# Resource Planning
st.markdown("---")
st.header("2. Resource Planning")

col1, col2 = st.columns(2)

with col1:
    team_resources = st.text_area(
        "Team & Roles",
        value=current_data.get('team', ''),
        placeholder="• Project Manager: Name\n• Developers: 3\n• Designers: 2",
        height=150
    )

with col2:
    budget_resources = st.text_area(
        "Budget & Tools",
        value=current_data.get('budget', ''),
        placeholder="Development: $X\nMarketing: $Y\nTools: List here",
        height=150
    )

# Success Metrics
st.markdown("---")
st.header("3. Success Metrics (KPIs)")

metrics = st.text_area(
    "Define how you'll measure success",
    value=current_data.get('metrics', ''),
    placeholder="• User adoption rate: Target 1000 users in 3 months\n• Customer satisfaction: NPS > 50\n• Revenue: $X per month",
    height=150
)

# Risk Management
st.markdown("---")
st.header("4. Risk Management")

risks = st.text_area(
    "Identify potential risks and mitigation strategies",
    value=current_data.get('risks', ''),
    placeholder="Risk 1: Technical challenges\nMitigation: Hire specialist\n\nRisk 2: Market competition\nMitigation: Focus on unique value prop",
    height=150
)

# Launch Plan
st.markdown("---")
st.header("5. Launch Plan")

col1, col2 = st.columns(2)

with col1:
    launch_date = st.date_input("Target Launch Date")

with col2:
    launch_type = st.selectbox(
        "Launch Type",
        ["Soft Launch", "Full Launch", "Phased Rollout", "Beta Program"]
    )

launch_activities = st.text_area(
    "Launch Activities",
    value=current_data.get('launch_activities', ''),
    placeholder="• Pre-launch: Marketing campaign\n• Launch day: Press release\n• Post-launch: User onboarding",
    height=150
)

# Save
if st.button("Save Implement Stage", type="primary"):
    data = {
        'roadmap': roadmap,
        'team': team_resources,
        'budget': budget_resources,
        'metrics': metrics,
        'risks': risks,
        'launch_date': str(launch_date),
        'launch_type': launch_type,
        'launch_activities': launch_activities
    }

    create_or_update_stage_progress(
        db=db,
        project_id=project_id,
        stage_number=6,
        status="in_progress",
        data=data
    )

    st.success("✅ Implement stage progress saved!")

# Final Report Generation
st.markdown("---")
st.header("6. Generate Final Report")

st.markdown("Export a comprehensive report of your Design Thinking journey")

col1, col2 = st.columns(2)

with col1:
    report_format = st.selectbox("Report Format", ["PDF", "DOCX", "Both"])

with col2:
    include_sections = st.multiselect(
        "Include Sections",
        ["Executive Summary", "Empathise", "Define", "Ideate", "Prototype", "Test", "Implement"],
        default=["Executive Summary", "Empathise", "Define", "Ideate", "Prototype", "Test", "Implement"]
    )

if st.button("Generate Report", type="primary"):
    with st.spinner("Generating comprehensive report..."):
        try:
            report_path = generate_final_report(
                project_id=project_id,
                format=report_format.lower(),
                sections=include_sections
            )
            st.success(f"✅ Report generated successfully!")
            st.download_button(
                label="Download Report",
                data=open(report_path, 'rb').read(),
                file_name=f"design_thinking_report_{project_id}.{report_format.lower()}",
                mime="application/pdf" if report_format == "PDF" else "application/vnd.openxmlformats-officedocument.wordprocessingml.document"
            )
        except Exception as e:
            st.error(f"Error generating report: {str(e)}")

# Complete
st.markdown("---")
if st.button("Mark Implement Stage as Complete", type="primary"):
    create_or_update_stage_progress(
        db=db,
        project_id=project_id,
        stage_number=6,
        status="completed"
    )
    st.success("🎉 Congratulations! Your Design Thinking project is complete!")
    st.balloons()

db.close()
