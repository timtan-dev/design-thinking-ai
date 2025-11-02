"""Implement Stage - Roadmap Generation and Task Management"""

import streamlit as st
import json
from datetime import datetime
from database.models import (
    ImplementationRoadmap, ImplementationTask, JiraConfig,
    StageSummary, UserTest, TestInsight
)
from services.ai_service import AIService
from utils.time_utils import format_local_time
from config.database import get_db

def render_implement_page(project):
    """Main render function for Implement stage"""

    st.title("🚀 Implement Stage")
    st.markdown(f"**Project:** {project.name}")
    st.markdown("---")

    st.markdown("""
    ### Turn Your Design into Reality
    Create a strategic roadmap, break down development tasks, and sync with Jira.
    """)

    db = get_db()

    # Check if roadmap exists
    roadmap = db.query(ImplementationRoadmap).filter(
        ImplementationRoadmap.project_id == project.id
    ).first()

    # Tab interface
    tab1, tab2, tab3 = st.tabs([
        "📋 Roadmap Generation",
        "✅ Task Breakdown",
        "🔗 Jira Export"
    ])

    with tab1:
        render_roadmap_tab(project, roadmap, db)

    with tab2:
        render_task_breakdown_tab(project, roadmap, db)

    with tab3:
        render_jira_export_tab(project, roadmap, db)

    # Show stage summary if available
    render_stage_summary(project, db)

def render_roadmap_tab(project, roadmap, db):
    """Tab 1: Roadmap Generation"""

    st.markdown("### Strategic Implementation Roadmap")

    # Show badge if roadmap exists
    if roadmap:
        st.success("✅ Roadmap Complete")

    # Display existing roadmap
    if roadmap:
        display_roadmap(roadmap, db)

        st.markdown("---")
        if st.button("🔄 Regenerate Roadmap", type="secondary"):
            st.session_state['regenerate_roadmap'] = True
            st.rerun()

    # Show generation form
    if not roadmap or st.session_state.get('regenerate_roadmap', False):
        st.markdown("---")
        st.markdown("### Generate New Roadmap")

        with st.form("roadmap_form"):
            col1, col2 = st.columns(2)

            with col1:
                team_size = st.number_input(
                    "Team Size",
                    min_value=1,
                    max_value=50,
                    value=5,
                    help="Number of developers on the team"
                )

                sprint_duration = st.number_input(
                    "Sprint Duration (weeks)",
                    min_value=1,
                    max_value=4,
                    value=2,
                    help="Length of each sprint/iteration"
                )

            with col2:
                target_launch_weeks = st.number_input(
                    "Target Launch Timeline (weeks)",
                    min_value=1,
                    max_value=52,
                    value=12,
                    help="Desired time to launch"
                )

                development_approach = st.selectbox(
                    "Development Approach",
                    options=["agile", "waterfall", "hybrid"],
                    help="Methodology for development"
                )

            submitted = st.form_submit_button("🎯 Generate Roadmap", type="primary", use_container_width=True)

            if submitted:
                generate_roadmap(project, team_size, sprint_duration, target_launch_weeks, development_approach, db)
                if 'regenerate_roadmap' in st.session_state:
                    del st.session_state['regenerate_roadmap']
                st.rerun()

def generate_roadmap(project, team_size, sprint_duration, target_launch_weeks, development_approach, db):
    """Generate roadmap using AI"""

    with st.spinner("🧠 Generating strategic roadmap..."):
        # Gather context from previous stages
        context = gather_project_context(project, db)

        # Get test feedback priorities
        test_priorities = gather_test_priorities(project, db)

        # Call AI service
        ai_service = AIService()

        from prompts.implement.roadmap_generation import GENERATE_ROADMAP_PROMPT

        prompt = GENERATE_ROADMAP_PROMPT.format(
            project_name=project.name,
            project_goal=project.goal,
            team_size=team_size,
            sprint_duration=sprint_duration,
            target_launch_weeks=target_launch_weeks,
            development_approach=development_approach,
            project_context=context,
            test_priorities=test_priorities
        )

        roadmap_json = ai_service._call_openai(
            "You are an expert software architect and project manager creating strategic implementation roadmaps.",
            prompt
        )

        # Parse JSON response
        try:
            # Remove markdown code blocks if present
            roadmap_json = roadmap_json.strip()
            if roadmap_json.startswith("```"):
                roadmap_json = roadmap_json.split("```")[1]
                if roadmap_json.startswith("json"):
                    roadmap_json = roadmap_json[4:]

            roadmap_data = json.loads(roadmap_json)

            # Create or update roadmap
            existing_roadmap = db.query(ImplementationRoadmap).filter(
                ImplementationRoadmap.project_id == project.id
            ).first()

            if existing_roadmap:
                # Update existing
                existing_roadmap.team_size = team_size
                existing_roadmap.sprint_duration = sprint_duration
                existing_roadmap.target_launch_weeks = target_launch_weeks
                existing_roadmap.development_approach = development_approach
                existing_roadmap.phases_json = roadmap_data
                existing_roadmap.updated_at = datetime.utcnow()
            else:
                # Create new
                new_roadmap = ImplementationRoadmap(
                    project_id=project.id,
                    team_size=team_size,
                    sprint_duration=sprint_duration,
                    target_launch_weeks=target_launch_weeks,
                    development_approach=development_approach,
                    phases_json=roadmap_data
                )
                db.add(new_roadmap)

            db.commit()
            st.success("✅ Roadmap generated successfully!")

        except json.JSONDecodeError as e:
            st.error(f"Failed to parse AI response: {e}")
            with st.expander("🔍 View Raw Response"):
                st.code(roadmap_json)

def display_roadmap(roadmap, db):
    """Display the generated roadmap"""

    phases = roadmap.phases_json.get("phases", [])

    st.markdown(f"""
    **Configuration:**
    - Team Size: {roadmap.team_size} developers
    - Sprint Duration: {roadmap.sprint_duration} weeks
    - Target Launch: {roadmap.target_launch_weeks} weeks
    - Approach: {roadmap.development_approach.title()}
    """)

    st.markdown("---")

    for idx, phase in enumerate(phases, 1):
        with st.expander(f"📦 {phase['name']}", expanded=(idx == 1)):
            st.markdown(f"**Duration:** {phase['duration_weeks']} weeks")
            st.markdown(f"**Team Allocation:** {phase.get('team_allocation', roadmap.team_size)} developers")

            st.markdown("#### MoSCoW Prioritization")

            col1, col2 = st.columns(2)

            with col1:
                if phase.get('must_have'):
                    st.markdown("**🔴 MUST Have:**")
                    for item in phase['must_have']:
                        st.markdown(f"- {item}")

                if phase.get('should_have'):
                    st.markdown("**🟠 SHOULD Have:**")
                    for item in phase['should_have']:
                        st.markdown(f"- {item}")

            with col2:
                if phase.get('could_have'):
                    st.markdown("**🟡 COULD Have:**")
                    for item in phase['could_have']:
                        st.markdown(f"- {item}")

                if phase.get('wont_have'):
                    st.markdown("**⚪ WON'T Have:**")
                    for item in phase['wont_have']:
                        st.markdown(f"- {item}")

            if phase.get('dependencies'):
                st.markdown("**Dependencies:**")
                for dep in phase['dependencies']:
                    st.markdown(f"- {dep}")

    # Download button
    roadmap_text = generate_roadmap_markdown(roadmap)
    st.download_button(
        "📥 Download Roadmap",
        data=roadmap_text,
        file_name=f"implementation_roadmap_{roadmap.project_id}.md",
        mime="text/markdown",
        use_container_width=True
    )

def render_task_breakdown_tab(project, roadmap, db):
    """Tab 2: Task Breakdown"""

    st.markdown("### Development Task Breakdown")

    # Check if tasks exist
    tasks = []
    if roadmap:
        tasks = db.query(ImplementationTask).filter(
            ImplementationTask.roadmap_id == roadmap.id
        ).order_by(ImplementationTask.order_index).all()

    # Show task generation option
    if not roadmap:
        st.warning("⚠️ Please generate a roadmap first in Tab 1.")
        return

    if not tasks:
        st.info("No tasks generated yet. Click below to generate tasks from your roadmap.")

        if st.button("🎯 Generate Tasks from Roadmap", type="primary"):
            generate_tasks_from_roadmap(project, roadmap, db)
            st.rerun()
    else:
        # Display tasks
        display_task_list(tasks, roadmap, db)

        st.markdown("---")

        col1, col2, col3 = st.columns(3)

        with col1:
            if st.button("🔄 Regenerate All Tasks", type="secondary"):
                # Delete existing tasks
                db.query(ImplementationTask).filter(
                    ImplementationTask.roadmap_id == roadmap.id
                ).delete()
                db.commit()
                st.rerun()

        with col2:
            if st.button("➕ Add Custom Task"):
                st.session_state['show_add_task_dialog'] = True

        with col3:
            # Export options
            export_tasks_to_file(tasks, project)

    # Add task dialog
    if st.session_state.get('show_add_task_dialog', False):
        show_add_task_dialog(roadmap, db)

def generate_tasks_from_roadmap(project, roadmap, db):
    """Generate detailed tasks using AI"""

    with st.spinner("🧠 Generating detailed tasks..."):
        # Gather context
        roadmap_context = json.dumps(roadmap.phases_json, indent=2)
        test_priorities = gather_test_priorities(project, db)

        # Call AI service
        ai_service = AIService()

        from prompts.implement.task_generation import GENERATE_TASKS_PROMPT

        prompt = GENERATE_TASKS_PROMPT.format(
            project_name=project.name,
            project_goal=project.goal,
            roadmap_context=roadmap_context,
            test_priorities=test_priorities
        )

        tasks_json = ai_service._call_openai(
            "You are an expert software developer and project planner creating detailed implementation tasks.",
            prompt
        )

        # Parse JSON response
        try:
            # Remove markdown code blocks if present
            tasks_json = tasks_json.strip()
            if tasks_json.startswith("```"):
                tasks_json = tasks_json.split("```")[1]
                if tasks_json.startswith("json"):
                    tasks_json = tasks_json[4:]

            tasks_data = json.loads(tasks_json)

            # Create tasks
            for idx, task_item in enumerate(tasks_data.get("tasks", [])):
                task = ImplementationTask(
                    roadmap_id=roadmap.id,
                    task_title=task_item['title'],
                    task_description=task_item['description'],
                    priority=task_item['priority'],
                    story_points=task_item.get('story_points'),
                    estimated_hours=task_item.get('estimated_hours'),
                    skills_required=task_item.get('skills_required', ''),
                    acceptance_criteria=json.dumps(task_item.get('acceptance_criteria', [])),
                    dependencies_json=task_item.get('dependencies', []),
                    moscow_category=task_item.get('moscow_category', 'should'),
                    order_index=idx
                )
                db.add(task)

            db.commit()
            st.success(f"✅ Generated {len(tasks_data.get('tasks', []))} tasks!")

        except json.JSONDecodeError as e:
            st.error(f"Failed to parse AI response: {e}")
            with st.expander("🔍 View Raw Response"):
                st.code(tasks_json)

def display_task_list(tasks, roadmap, db):
    """Display tasks with expanders"""

    # Group by priority
    priority_order = ["highest", "high", "medium", "low"]
    priority_icons = {
        "highest": "🔴",
        "high": "🟠",
        "medium": "🟡",
        "low": "🟢"
    }

    moscow_icons = {
        "must": "🔴 MUST",
        "should": "🟠 SHOULD",
        "could": "🟡 COULD",
        "wont": "⚪ WON'T"
    }

    # Show task summary
    st.markdown(f"**Total Tasks:** {len(tasks)}")
    col1, col2, col3, col4 = st.columns(4)
    col1.metric("Must Have", len([t for t in tasks if t.moscow_category == "must"]))
    col2.metric("Should Have", len([t for t in tasks if t.moscow_category == "should"]))
    col3.metric("Could Have", len([t for t in tasks if t.moscow_category == "could"]))
    col4.metric("Total Story Points", sum(t.story_points or 0 for t in tasks))

    st.markdown("---")

    for priority in priority_order:
        priority_tasks = [t for t in tasks if t.priority == priority]

        if priority_tasks:
            st.markdown(f"### {priority_icons[priority]} {priority.title()} Priority")

            for task in priority_tasks:
                # Build expander title
                moscow_badge = moscow_icons.get(task.moscow_category, "")
                jira_status = ""
                if task.jira_issue_key:
                    status_emoji = {"to_do": "☐", "in_progress": "⏳", "done": "✅"}.get(task.jira_status, "☐")
                    jira_status = f"{status_emoji} [{task.jira_issue_key}]"

                title = f"{jira_status} [{moscow_badge}] {task.task_title} ({task.story_points}pts, {task.skills_required})"

                with st.expander(title):
                    st.markdown(f"**Description:** {task.task_description}")

                    col1, col2 = st.columns(2)
                    with col1:
                        st.markdown(f"**Estimated Hours:** {task.estimated_hours}h")
                        st.markdown(f"**Skills Required:** {task.skills_required}")

                    with col2:
                        st.markdown(f"**Story Points:** {task.story_points}")
                        st.markdown(f"**Priority:** {task.priority.title()}")

                    # Acceptance criteria
                    if task.acceptance_criteria:
                        st.markdown("**Acceptance Criteria:**")
                        try:
                            criteria = json.loads(task.acceptance_criteria)
                            for criterion in criteria:
                                st.markdown(f"- {criterion}")
                        except:
                            st.markdown(task.acceptance_criteria)

                    # Dependencies
                    if task.dependencies_json:
                        st.markdown(f"**Dependencies:** {', '.join(map(str, task.dependencies_json))}")

                    # Rationale (if available in description)
                    st.markdown("---")

                    # Action buttons
                    col1, col2 = st.columns(2)

                    with col1:
                        if st.button("✏️ Edit", key=f"edit_{task.id}"):
                            st.session_state['edit_task_id'] = task.id
                            st.rerun()

                    with col2:
                        if st.button("🗑️ Delete", key=f"delete_{task.id}", type="secondary"):
                            db.delete(task)
                            db.commit()
                            st.success("Task deleted!")
                            st.rerun()

@st.dialog("➕ Add Custom Task", width="large")
def show_add_task_dialog(roadmap, db):
    """Dialog for adding custom task"""

    with st.form("add_task_form"):
        title = st.text_input("Task Title", placeholder="e.g., Setup authentication system")
        description = st.text_area("Description", placeholder="Detailed explanation of the task")

        col1, col2 = st.columns(2)

        with col1:
            priority = st.selectbox("Priority", options=["highest", "high", "medium", "low"])
            story_points = st.selectbox("Story Points", options=[1, 2, 3, 5, 8, 13])

        with col2:
            moscow = st.selectbox("MoSCoW", options=["must", "should", "could", "wont"])
            estimated_hours = st.number_input("Estimated Hours", min_value=1, max_value=200, value=8)

        skills = st.multiselect(
            "Skills Required",
            options=["frontend", "backend", "design", "qa", "devops"],
            default=["backend"]
        )

        criteria = st.text_area("Acceptance Criteria (one per line)", placeholder="User can register\nUser can login")

        submitted = st.form_submit_button("Add Task", type="primary")

        if submitted:
            if not title or not description:
                st.error("Please fill in all required fields")
            else:
                # Parse criteria
                criteria_list = [c.strip() for c in criteria.split("\n") if c.strip()]

                task = ImplementationTask(
                    roadmap_id=roadmap.id,
                    task_title=title,
                    task_description=description,
                    priority=priority,
                    story_points=story_points,
                    estimated_hours=estimated_hours,
                    skills_required=", ".join(skills),
                    acceptance_criteria=json.dumps(criteria_list),
                    dependencies_json=[],
                    moscow_category=moscow,
                    order_index=999  # Put at end
                )
                db.add(task)
                db.commit()

                st.success("✅ Task added!")
                st.session_state['show_add_task_dialog'] = False
                st.rerun()

def render_jira_export_tab(project, roadmap, db):
    """Tab 3: Jira Export with OAuth 2.0"""

    from database.models import JiraOAuthToken
    from services.jira_oauth_service import JiraOAuthService

    st.markdown("### Jira Integration via OAuth 2.0")

    if not roadmap:
        st.warning("⚠️ Please generate a roadmap first in Tab 1.")
        return

    tasks = db.query(ImplementationTask).filter(
        ImplementationTask.roadmap_id == roadmap.id
    ).all()

    if not tasks:
        st.warning("⚠️ Please generate tasks first in Tab 2.")
        return

    # For MVP: use a default user_id (in production, get from authentication)
    user_id = project.user_id or "default_user"

    # Check OAuth authorization
    oauth_service = JiraOAuthService()
    is_authorized = oauth_service.is_user_authorized(user_id)

    oauth_token = db.query(JiraOAuthToken).filter(
        JiraOAuthToken.user_id == user_id
    ).first()

    # OAuth Connection Status
    with st.expander("🔐 Jira OAuth Connection", expanded=not is_authorized):
        if is_authorized and oauth_token:
            st.success(f"✅ Connected to Jira as {oauth_token.jira_display_name or oauth_token.jira_email}")
            st.markdown(f"**Jira Account:** {oauth_token.jira_email}")
            st.markdown(f"**Connected:** {format_local_time(oauth_token.created_at)}")

            col1, col2 = st.columns(2)

            with col1:
                if st.button("🔄 Refresh Connection"):
                    try:
                        # Test connection
                        token = oauth_service.get_valid_access_token(user_id)
                        if token:
                            st.success("✅ Connection refreshed successfully!")
                        else:
                            st.error("❌ Failed to refresh. Please reconnect.")
                    except Exception as e:
                        st.error(f"❌ Error: {str(e)}")

            with col2:
                if st.button("🔌 Disconnect Jira", type="secondary"):
                    oauth_service.revoke_token(user_id)
                    st.success("✅ Disconnected from Jira")
                    st.rerun()

        else:
            st.warning("⚠️ Not connected to Jira. Please authorize to enable Jira integration.")
            st.markdown("""
            **How to connect:**
            1. Click 'Connect to Jira' below
            2. You'll be redirected to Atlassian to authorize
            3. Grant permissions and return to this page
            4. Your credentials are securely encrypted and stored
            """)

            if st.button("🔗 Connect to Jira", type="primary"):
                import secrets
                import os

                state = secrets.token_urlsafe(32)
                # Store state in session for CSRF verification
                st.session_state['oauth_state'] = state
                st.session_state['oauth_user_id'] = user_id

                auth_url = oauth_service.get_authorization_url(state)

                # Check environment - use DEBUG flag or explicit env var
                is_production = os.getenv("DEBUG", "True").lower() == "false"

                if is_production:
                    # Production: Use HTML redirect
                    st.markdown(f'<meta http-equiv="refresh" content="0; url={auth_url}">', unsafe_allow_html=True)
                    st.info("Redirecting to Atlassian for authorization...")
                else:
                    # Development: Show clickable link (Streamlit can't redirect in dev mode)
                    st.info("🔗 Click the link below to authorize with Jira:")
                    st.markdown(f"[**Authorize with Atlassian**]({auth_url})", unsafe_allow_html=True)

                    with st.expander("Or copy the full URL"):
                        st.code(auth_url, language="text")

                    st.warning("⚠️ After authorizing, you'll be redirected to `/oauth/callback`. Create that page to complete the flow.")

    if not is_authorized:
        st.markdown("---")
        st.info("👆 Please connect to Jira above to enable task export and sync.")
        return

    # Check for Jira config
    jira_config = db.query(JiraConfig).filter(
        JiraConfig.project_id == project.id
    ).first()

    # Check sync status on page load
    if jira_config and jira_config.last_sync_at:
        time_since_sync = (datetime.utcnow() - jira_config.last_sync_at).total_seconds() / 60
        if time_since_sync > 5:
            st.warning(f"⚠️ Last sync was {int(time_since_sync)} minutes ago. Consider syncing to get latest status.")

    st.markdown("---")

    # Jira Project Configuration
    with st.expander("⚙️ Jira Project Configuration", expanded=not jira_config):
        st.markdown("Configure which Jira project to sync with:")

        with st.form("jira_config_form"):
            # Get accessible resources
            try:
                access_token = oauth_service.get_valid_access_token(user_id)
                resources = oauth_service.get_accessible_resources(access_token)

                if resources:
                    resource_options = [f"{r['name']} ({r['url']})" for r in resources]
                    selected_resource = st.selectbox(
                        "Select Jira Site",
                        options=range(len(resource_options)),
                        format_func=lambda i: resource_options[i]
                    )

                    jira_url = resources[selected_resource]['url']
                    cloud_id = resources[selected_resource]['id']

                    st.markdown(f"**Cloud ID:** `{cloud_id}`")
                else:
                    st.error("No accessible Jira sites found")
                    jira_url = st.text_input("Jira URL", placeholder="https://your-company.atlassian.net")
                    cloud_id = None

            except Exception as e:
                st.error(f"Failed to load Jira sites: {str(e)}")
                jira_url = st.text_input("Jira URL", placeholder="https://your-company.atlassian.net")
                cloud_id = None

            jira_project_key = st.text_input(
                "Jira Project Key",
                value=jira_config.jira_project_key if jira_config else "",
                placeholder="PROJ",
                help="The project key where tasks will be created"
            )

            submitted = st.form_submit_button("💾 Save Configuration", type="primary")

            if submitted:
                if not jira_project_key or not jira_url:
                    st.error("Please fill in all fields")
                else:
                    if jira_config:
                        jira_config.jira_url = jira_url
                        jira_config.jira_project_key = jira_project_key
                        jira_config.jira_cloud_id = cloud_id
                        jira_config.updated_at = datetime.utcnow()
                    else:
                        jira_config = JiraConfig(
                            project_id=project.id,
                            user_id=user_id,
                            jira_url=jira_url,
                            jira_project_key=jira_project_key,
                            jira_cloud_id=cloud_id
                        )
                        db.add(jira_config)

                    db.commit()
                    st.success("✅ Configuration saved!")
                    st.rerun()

    if not jira_config:
        return

    st.markdown("---")

    # Sync status section
    st.markdown("### Sync Status")

    synced_tasks = [t for t in tasks if t.jira_issue_key]
    pending_tasks = [t for t in tasks if not t.jira_issue_key]

    col1, col2, col3 = st.columns(3)
    col1.metric("Total Tasks", len(tasks))
    col2.metric("Synced to Jira", len(synced_tasks))
    col3.metric("Pending Sync", len(pending_tasks))

    if jira_config.last_sync_at:
        st.markdown(f"**Last Sync:** {format_local_time(jira_config.last_sync_at)}")

    st.markdown("---")

    # Export to Jira section
    st.markdown("### Export to Jira")

    if not jira_config.epic_key:
        st.info(f"📦 An Epic will be created with name: **{project.name}**")
    else:
        st.success(f"✅ Epic created: [{jira_config.epic_key}]({jira_config.jira_url}/browse/{jira_config.epic_key})")

    # Preview tasks
    if pending_tasks:
        with st.expander(f"👀 Preview Tasks to Export ({len(pending_tasks)} pending)"):
            for task in pending_tasks[:10]:  # Show first 10
                st.markdown(f"**[{task.moscow_category.upper()}]** {task.task_title}")
                st.markdown(f"- Priority: {task.priority}, Story Points: {task.story_points}")
                st.markdown("---")

            if len(pending_tasks) > 10:
                st.markdown(f"... and {len(pending_tasks) - 10} more tasks")

    # Action buttons
    col1, col2 = st.columns(2)

    with col1:
        if st.button("🚀 Push Tasks to Jira", type="primary", disabled=len(pending_tasks) == 0):
            push_tasks_to_jira(project, roadmap, pending_tasks, jira_config, user_id, db)
            st.rerun()

    with col2:
        if st.button("🔄 Sync Status from Jira", disabled=len(synced_tasks) == 0):
            sync_status_from_jira(project, synced_tasks, jira_config, user_id, db)
            st.rerun()

    st.markdown("---")
    st.info("💡 **Note:** Jira integration uses OAuth 2.0 for secure authentication. Your credentials are encrypted.")

def push_tasks_to_jira(project, roadmap, tasks, jira_config, user_id, db):
    """Push tasks to Jira using OAuth 2.0 and direct API calls"""

    from services.jira_api_service import JiraAPIService

    try:
        # Initialize Jira API service
        jira_service = JiraAPIService(
            user_id=user_id,
            jira_url=jira_config.jira_url,
            cloud_id=jira_config.jira_cloud_id
        )

        with st.spinner("🚀 Pushing tasks to Jira..."):
            # Step 1: Create Epic if not exists
            if not jira_config.epic_key:
                st.info("Creating Epic...")
                epic_response = jira_service.create_epic(
                    project_key=jira_config.jira_project_key,
                    epic_name=project.name,
                    description=f"Implementation roadmap for {project.name}\n\nGoal: {project.goal}"
                )

                jira_config.epic_key = epic_response["key"]
                db.commit()
                st.success(f"✅ Epic created: {epic_response['key']}")

            # Step 2: Create tasks
            success_count = 0
            failed_tasks = []

            progress_bar = st.progress(0)
            status_text = st.empty()

            for idx, task in enumerate(tasks):
                try:
                    status_text.text(f"Creating task {idx + 1}/{len(tasks)}: {task.task_title[:50]}...")

                    issue_response = jira_service.create_task(
                        project_key=jira_config.jira_project_key,
                        task=task,
                        epic_key=jira_config.epic_key
                    )

                    # Update task with Jira issue key
                    task.jira_issue_key = issue_response["key"]
                    task.jira_status = "to_do"
                    success_count += 1

                except Exception as task_error:
                    print(f"Failed to create task {task.task_title}: {task_error}")
                    failed_tasks.append((task.task_title, str(task_error)))

                progress_bar.progress((idx + 1) / len(tasks))

            # Update last sync time
            jira_config.last_sync_at = datetime.utcnow()
            db.commit()

            progress_bar.empty()
            status_text.empty()

            # Show results
            if success_count == len(tasks):
                st.success(f"✅ Successfully created {success_count} tasks in Jira!")
            elif success_count > 0:
                st.warning(f"⚠️ Created {success_count}/{len(tasks)} tasks. {len(failed_tasks)} failed.")
                if failed_tasks:
                    with st.expander("View Failed Tasks"):
                        for task_title, error in failed_tasks:
                            st.error(f"**{task_title}**: {error}")
            else:
                st.error("❌ Failed to create any tasks. Check your Jira configuration.")

    except Exception as e:
        st.error(f"❌ Error pushing tasks to Jira: {str(e)}")
        st.info("Please check your Jira connection and project configuration.")

def sync_status_from_jira(project, tasks, jira_config, user_id, db):
    """Sync task status from Jira using OAuth 2.0 and direct API calls"""

    from services.jira_api_service import JiraAPIService

    try:
        # Initialize Jira API service
        jira_service = JiraAPIService(
            user_id=user_id,
            jira_url=jira_config.jira_url,
            cloud_id=jira_config.jira_cloud_id
        )

        with st.spinner("🔄 Syncing status from Jira..."):
            # Get issue keys
            issue_keys = [task.jira_issue_key for task in tasks if task.jira_issue_key]

            if not issue_keys:
                st.warning("No tasks to sync (no Jira issue keys found)")
                return

            # Bulk fetch statuses
            status_map = jira_service.bulk_get_issue_statuses(issue_keys)

            # Track changes
            updated_count = 0
            status_changes = []

            for task in tasks:
                if task.jira_issue_key and task.jira_issue_key in status_map:
                    new_status = status_map[task.jira_issue_key]

                    if task.jira_status != new_status:
                        old_status = task.jira_status or "unknown"
                        task.jira_status = new_status
                        updated_count += 1
                        status_changes.append((task.task_title, old_status, new_status))

            # Update last sync time
            jira_config.last_sync_at = datetime.utcnow()
            db.commit()

            # Show results
            if updated_count > 0:
                st.success(f"✅ Synced {len(issue_keys)} tasks. {updated_count} status changes detected.")

                with st.expander("View Status Changes"):
                    for title, old, new in status_changes:
                        st.markdown(f"**{title}**: `{old}` → `{new}`")

                # Generate stage summary if significant changes
                if updated_count >= 3:
                    st.info("📊 Generating implementation summary...")
                    # TODO: Call generate_implementation_summary()

            else:
                st.info(f"✅ Synced {len(issue_keys)} tasks. No status changes.")

    except Exception as e:
        st.error(f"❌ Error syncing from Jira: {str(e)}")
        st.info("Please check your Jira connection.")

def gather_project_context(project, db):
    """Gather context from all previous stages"""

    context = f"Project: {project.name}\nGoal: {project.goal}\n\n"

    # Get latest stage summaries
    from database.models import StageSummary

    stages = ["empathise", "define", "ideate", "prototype", "test"]
    for stage in stages:
        summary = db.query(StageSummary).filter(
            StageSummary.project_id == project.id,
            StageSummary.stage == stage
        ).order_by(StageSummary.version.desc()).first()

        if summary:
            context += f"\n### {stage.title()} Stage Summary:\n{summary.summary_text}\n"

    return context

def gather_test_priorities(project, db):
    """Gather priorities from test feedback"""

    tests = db.query(UserTest).filter(
        UserTest.project_id == project.id
    ).all()

    if not tests:
        return "No test feedback available."

    priorities = "Test Feedback Priorities:\n\n"

    for test in tests:
        insights = db.query(TestInsight).filter(
            TestInsight.user_test_id == test.id,
            TestInsight.priority.in_(["critical", "high"])
        ).all()

        if insights:
            priorities += f"## {test.test_name}\n"
            for insight in insights:
                priorities += f"- [{insight.priority.upper()}] {insight.insight_text[:200]}...\n"

    return priorities

def generate_roadmap_markdown(roadmap):
    """Generate markdown export of roadmap"""

    md = f"# Implementation Roadmap\n\n"
    md += f"**Team Size:** {roadmap.team_size} developers\n"
    md += f"**Sprint Duration:** {roadmap.sprint_duration} weeks\n"
    md += f"**Target Launch:** {roadmap.target_launch_weeks} weeks\n"
    md += f"**Approach:** {roadmap.development_approach.title()}\n\n"

    phases = roadmap.phases_json.get("phases", [])

    for phase in phases:
        md += f"## {phase['name']}\n\n"
        md += f"**Duration:** {phase['duration_weeks']} weeks\n\n"

        md += "### MoSCoW Prioritization\n\n"

        if phase.get('must_have'):
            md += "**MUST Have:**\n"
            for item in phase['must_have']:
                md += f"- {item}\n"
            md += "\n"

        if phase.get('should_have'):
            md += "**SHOULD Have:**\n"
            for item in phase['should_have']:
                md += f"- {item}\n"
            md += "\n"

        if phase.get('could_have'):
            md += "**COULD Have:**\n"
            for item in phase['could_have']:
                md += f"- {item}\n"
            md += "\n"

        if phase.get('dependencies'):
            md += "**Dependencies:**\n"
            for dep in phase['dependencies']:
                md += f"- {dep}\n"
            md += "\n"

    return md

def export_tasks_to_file(tasks, project):
    """Export tasks to JSON/CSV"""

    # Prepare task data
    tasks_data = []
    for task in tasks:
        tasks_data.append({
            "title": task.task_title,
            "description": task.task_description,
            "priority": task.priority,
            "story_points": task.story_points,
            "estimated_hours": task.estimated_hours,
            "skills_required": task.skills_required,
            "moscow_category": task.moscow_category,
            "jira_issue_key": task.jira_issue_key,
            "jira_status": task.jira_status
        })

    # JSON export
    json_data = json.dumps({"tasks": tasks_data}, indent=2)

    st.download_button(
        "📥 Export as JSON",
        data=json_data,
        file_name=f"tasks_{project.name}.json",
        mime="application/json",
        use_container_width=True
    )

def render_stage_summary(project, db):
    """Render the implement stage summary"""

    summaries = db.query(StageSummary).filter(
        StageSummary.project_id == project.id,
        StageSummary.stage == "implement"
    ).order_by(StageSummary.version.desc()).all()

    if not summaries:
        return

    st.markdown("---")
    st.markdown("### 📋 Implementation Summary")

    latest_summary = summaries[0]

    with st.expander(f"Summary v{latest_summary.version} - {format_local_time(latest_summary.created_at)}", expanded=True):
        st.markdown(latest_summary.summary_text)

        # Download button
        st.download_button(
            "📥 Download Summary",
            data=latest_summary.summary_text,
            file_name=f"implement_summary_v{latest_summary.version}.md",
            mime="text/markdown",
            use_container_width=True
        )
