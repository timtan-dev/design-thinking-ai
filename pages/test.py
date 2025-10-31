"""Test Stage - User Feedback Collection and Analysis"""

import streamlit as st
from database.models import UserTest, TestFeedback, TestInsight, PrototypePage, StageSummary
from services.ai_service import AIService
from utils.time_utils import format_local_time
from config.database import get_db

def render_test_page(project):
    """Main render function for Test stage"""

    st.title("🧪 Test Stage")
    st.markdown(f"**Project:** {project.name}")
    st.markdown("---")

    st.markdown("""
    ### Validate Your Prototype
    Collect feedback from users and get AI-powered insights to improve your design.
    """)

    db = get_db()

    # Check if there are any prototype pages
    prototype_pages = db.query(PrototypePage).filter(
        PrototypePage.project_id == project.id
    ).all()

    if not prototype_pages:
        st.warning("⚠️ No prototypes found. Please complete the Prototype stage first.")
        return

    # Main layout: Cards for test types
    st.markdown("### Test Methods")

    col1, col2, col3 = st.columns(3)

    with col1:
        if st.button("📝 Feedback Collection", type="primary", use_container_width=True):
            st.session_state['show_feedback_dialog'] = True

    with col2:
        st.button("🔍 Usability Testing", type="secondary", use_container_width=True, disabled=True)
        st.caption("Coming soon")

    with col3:
        st.button("🆎 A/B Testing", type="secondary", use_container_width=True, disabled=True)
        st.caption("Coming soon")

    # Show feedback collection dialog
    if st.session_state.get('show_feedback_dialog', False):
        show_feedback_collection_dialog(project, prototype_pages, db)

    # Display existing tests
    st.markdown("---")
    st.markdown("### Test Results")

    existing_tests = db.query(UserTest).filter(
        UserTest.project_id == project.id
    ).order_by(UserTest.created_at.desc()).all()

    if existing_tests:
        for test in existing_tests:
            render_test_result_card(test, db)
    else:
        st.info("No tests conducted yet. Click 'Feedback Collection' to start!")

    # Show stage summary if available
    render_stage_summary(project, db)

@st.dialog("📝 Feedback Collection", width="large")
def show_feedback_collection_dialog(project, prototype_pages, db):
    """Dialog for collecting user feedback"""

    st.markdown("Collect and analyze user feedback on your prototype.")

    # Tab layout
    tab1, tab2 = st.tabs(["📥 Setup Test", "📊 View Results"])

    with tab1:
        render_setup_test_tab(project, prototype_pages, db)

    with tab2:
        render_view_results_tab(project, db)

def render_setup_test_tab(project, prototype_pages, db):
    """Tab for setting up a new test"""

    st.markdown("#### Create New Test")

    # Test details
    test_name = st.text_input(
        "Test Name",
        placeholder="e.g., First User Feedback Round",
        key="test_name_input"
    )

    # Select prototype page (optional)
    page_options = ["All pages"] + [page.page_name for page in prototype_pages]
    selected_page = st.selectbox(
        "Prototype Page (Optional)",
        page_options,
        key="test_page_select"
    )

    st.markdown("#### Collect Feedback")
    st.markdown("Add feedback from each participant:")

    # Dynamic feedback collection
    if 'feedback_entries' not in st.session_state:
        st.session_state.feedback_entries = [{'participant': '', 'feedback': '', 'rating': 3}]

    feedback_data = []

    for idx, entry in enumerate(st.session_state.feedback_entries):
        st.markdown(f"**Participant {idx + 1}**")
        col1, col2 = st.columns([2, 1])

        with col1:
            participant_name = st.text_input(
                "Name (Optional)",
                value=entry['participant'],
                placeholder=f"Participant {idx + 1}",
                key=f"participant_name_{idx}"
            )

        with col2:
            rating = st.select_slider(
                "Rating",
                options=[1, 2, 3, 4, 5],
                value=entry['rating'],
                key=f"rating_{idx}"
            )

        feedback_text = st.text_area(
            "Feedback",
            value=entry['feedback'],
            placeholder="What did they say about the prototype? (observations, quotes, issues, suggestions)",
            height=100,
            key=f"feedback_text_{idx}"
        )

        feedback_data.append({
            'participant': participant_name or f"Participant {idx + 1}",
            'feedback': feedback_text,
            'rating': rating
        })

        st.markdown("---")

    # Buttons
    col1, col2, col3 = st.columns([1, 1, 2])

    with col1:
        if st.button("➕ Add Participant"):
            st.session_state.feedback_entries.append({'participant': '', 'feedback': '', 'rating': 3})
            st.rerun()

    with col2:
        if len(st.session_state.feedback_entries) > 1:
            if st.button("➖ Remove Last"):
                st.session_state.feedback_entries.pop()
                st.rerun()

    with col3:
        if st.button("🚀 Save & Analyze", type="primary", use_container_width=True):
            if not test_name:
                st.error("Please enter a test name")
            elif not any(f['feedback'].strip() for f in feedback_data):
                st.error("Please add at least one feedback entry")
            else:
                save_and_analyze_feedback(project, test_name, selected_page, feedback_data, prototype_pages, db)
                st.session_state.feedback_entries = [{'participant': '', 'feedback': '', 'rating': 3}]
                st.session_state['show_feedback_dialog'] = False
                st.rerun()

def save_and_analyze_feedback(project, test_name, selected_page, feedback_data, prototype_pages, db):
    """Save feedback and run AI analysis"""

    with st.spinner("💾 Saving feedback and running AI analysis..."):
        # Determine prototype page ID
        prototype_page_id = None
        if selected_page != "All pages":
            prototype_page = next((p for p in prototype_pages if p.page_name == selected_page), None)
            if prototype_page:
                prototype_page_id = prototype_page.id

        # Create user test record
        user_test = UserTest(
            project_id=project.id,
            prototype_page_id=prototype_page_id,
            test_type="feedback",
            test_name=test_name,
            participant_count=len([f for f in feedback_data if f['feedback'].strip()])
        )
        db.add(user_test)
        db.commit()
        db.refresh(user_test)

        # Save individual feedback items
        for feedback_item in feedback_data:
            if feedback_item['feedback'].strip():
                test_feedback = TestFeedback(
                    user_test_id=user_test.id,
                    participant_name=feedback_item['participant'],
                    feedback_text=feedback_item['feedback'],
                    rating=feedback_item['rating']
                )
                db.add(test_feedback)

        db.commit()

        # Run AI analysis
        analyze_test_feedback(user_test, project, selected_page, db)

        st.success("✅ Feedback saved and analyzed successfully!")

def analyze_test_feedback(user_test, project, page_name, db):
    """Run AI analysis on collected feedback"""

    # Get all feedback for this test
    feedback_items = db.query(TestFeedback).filter(
        TestFeedback.user_test_id == user_test.id
    ).all()

    if not feedback_items:
        return

    # Prepare feedback data for AI
    feedback_data = ""
    for idx, item in enumerate(feedback_items, 1):
        feedback_data += f"\n### {item.participant_name} (Rating: {item.rating}/5)\n"
        feedback_data += f"{item.feedback_text}\n"

    # Call AI service
    ai_service = AIService()

    from prompts.test.feedback_analysis import ANALYZE_FEEDBACK_PROMPT

    prompt = ANALYZE_FEEDBACK_PROMPT.format(
        project_name=project.name,
        project_goal=project.goal,
        page_name=page_name if page_name != "All pages" else "All prototype pages",
        feedback_data=feedback_data
    )

    analysis_result = ai_service._call_openai(
        "You are an expert UX researcher specializing in analyzing user feedback and providing actionable insights.",
        prompt
    )

    # Save analysis as insight
    insight = TestInsight(
        user_test_id=user_test.id,
        insight_type="comprehensive_analysis",
        insight_text=analysis_result,
        priority=None
    )
    db.add(insight)
    db.commit()

    # Generate stage summary (silently in background)
    generate_test_stage_summary(project, db)

def render_view_results_tab(project, db):
    """Tab for viewing existing test results"""

    tests = db.query(UserTest).filter(
        UserTest.project_id == project.id,
        UserTest.test_type == "feedback"
    ).order_by(UserTest.created_at.desc()).all()

    if not tests:
        st.info("No tests yet. Use the 'Setup Test' tab to create your first test.")
        return

    for test in tests:
        with st.expander(f"📊 {test.test_name} - {format_local_time(test.created_at)}", expanded=(test == tests[0])):
            st.markdown(f"**Participants:** {test.participant_count}")
            if test.prototype_page_id:
                page = db.query(PrototypePage).filter(PrototypePage.id == test.prototype_page_id).first()
                if page:
                    st.markdown(f"**Page:** {page.page_name}")

            # Show feedback
            feedback_items = db.query(TestFeedback).filter(
                TestFeedback.user_test_id == test.id
            ).all()

            if feedback_items:
                st.markdown("#### Feedback")
                for item in feedback_items:
                    st.markdown(f"**{item.participant_name}** - Rating: {'⭐' * item.rating}")
                    st.markdown(f"> {item.feedback_text}")
                    st.markdown("")

            # Show AI analysis
            insights = db.query(TestInsight).filter(
                TestInsight.user_test_id == test.id
            ).all()

            if insights:
                st.markdown("---")
                st.markdown("#### AI Analysis")
                for insight in insights:
                    st.markdown(insight.insight_text)

def render_test_result_card(test, db):
    """Render a card for each test result"""

    with st.expander(f"📊 {test.test_name} - {format_local_time(test.created_at)}", expanded=False):
        col1, col2 = st.columns([3, 1])

        with col1:
            st.markdown(f"**Type:** {test.test_type.replace('_', ' ').title()}")
            st.markdown(f"**Participants:** {test.participant_count}")

            if test.prototype_page_id:
                page = db.query(PrototypePage).filter(PrototypePage.id == test.prototype_page_id).first()
                if page:
                    st.markdown(f"**Page:** {page.page_name}")

        with col2:
            # Calculate average rating
            feedback_items = db.query(TestFeedback).filter(
                TestFeedback.user_test_id == test.id
            ).all()

            if feedback_items:
                avg_rating = sum(f.rating for f in feedback_items if f.rating) / len(feedback_items)
                st.metric("Avg Rating", f"{avg_rating:.1f}/5")

        # Show AI insights
        insights = db.query(TestInsight).filter(
            TestInsight.user_test_id == test.id
        ).all()

        if insights:
            st.markdown("---")
            st.markdown("#### AI Insights")
            for insight in insights:
                st.markdown(insight.insight_text)

def generate_test_stage_summary(project, db):
    """Generate overall summary for the test stage (background)"""

    # Get all tests
    tests = db.query(UserTest).filter(
        UserTest.project_id == project.id
    ).all()

    if not tests:
        return

    # Prepare all test results
    all_test_results = ""
    for test in tests:
        all_test_results += f"\n## {test.test_name} ({test.test_type})\n"
        all_test_results += f"Participants: {test.participant_count}\n\n"

        # Get insights
        insights = db.query(TestInsight).filter(
            TestInsight.user_test_id == test.id
        ).all()

        for insight in insights:
            all_test_results += f"{insight.insight_text}\n\n"

    # Call AI to generate summary
    ai_service = AIService()

    from prompts.test.feedback_analysis import GENERATE_TEST_SUMMARY_PROMPT

    prompt = GENERATE_TEST_SUMMARY_PROMPT.format(
        project_name=project.name,
        project_goal=project.goal,
        all_test_results=all_test_results
    )

    summary_text = ai_service._call_openai(
        "You are a UX research director creating executive summaries of user testing results.",
        prompt
    )

    # Get current version
    current_version = db.query(StageSummary).filter(
        StageSummary.project_id == project.id,
        StageSummary.stage == "test"
    ).count()

    # Save summary
    summary = StageSummary(
        project_id=project.id,
        stage="test",
        summary_text=summary_text,
        version=current_version + 1
    )
    db.add(summary)
    db.commit()

def render_stage_summary(project, db):
    """Render the test stage summary"""

    summaries = db.query(StageSummary).filter(
        StageSummary.project_id == project.id,
        StageSummary.stage == "test"
    ).order_by(StageSummary.version.desc()).all()

    if not summaries:
        return

    st.markdown("---")
    st.markdown("### 📋 Test Stage Summary")

    latest_summary = summaries[0]

    with st.expander(f"Summary v{latest_summary.version} - {format_local_time(latest_summary.created_at)}", expanded=True):
        st.markdown(latest_summary.summary_text)

        # Download button
        st.download_button(
            "📥 Download Summary",
            data=latest_summary.summary_text,
            file_name=f"test_summary_v{latest_summary.version}.md",
            mime="text/markdown",
            use_container_width=True
        )

    # Show older versions
    if len(summaries) > 1:
        with st.expander(f"📜 Previous Versions ({len(summaries) - 1})"):
            for summary in summaries[1:]:
                st.markdown(f"**Version {summary.version}** - {format_local_time(summary.created_at)}")
                st.markdown(summary.summary_text)
                st.markdown("---")
