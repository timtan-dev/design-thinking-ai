import streamlit as st
from config.database import get_db
from database.models import BrainstormIdea, StageSummary, Project, IdeaCategorization, GeneratedContent
from services.ai_service import AIService
from datetime import datetime, timezone
from utils.time_utils import format_local_time
from utils.model_badge import display_model_badge

IDEATE_METHODS = {
    "brainstorming": {"name": "Brainstorming", "icon": "🧠"},
    "mind_mapping": {"name": "Mind Mapping", "icon": "🗺️"},
    "scamper": {"name": "SCAMPER", "icon": "🔧"}
}

def render_ideate_page(project):
    st.markdown('<div style="margin-top: 2rem;"></div>', unsafe_allow_html=True)
    
    st.markdown('<div class="cards-grid">', unsafe_allow_html=True)
    cols = st.columns(3)
    
    for idx, (method_key, method_info) in enumerate(IDEATE_METHODS.items()):
        with cols[idx % 3]:
            if st.button(
                f"{method_info['icon']} {method_info['name']}",
                key=f"card_{method_key}",
                use_container_width=True,
                type="secondary"
            ):
                if method_key == "brainstorming":
                    open_brainstorming_dialog(project)
                elif method_key == "mind_mapping":
                    st.info("Mind Mapping coming soon!")
                elif method_key == "scamper":
                    st.info("SCAMPER coming soon!")
    
    st.markdown("</div>", unsafe_allow_html=True)

@st.dialog("🧠 Brainstorming")
def open_brainstorming_dialog(project):

    db = get_db()

    # Check if Define stage has generated content
    define_content = db.query(GeneratedContent).filter(
        GeneratedContent.project_id == project.id,
        GeneratedContent.content_type.in_([
            'empathy_map', 'persona', 'journey_map',
            'affinity_map', 'storytelling', 'stakeholder_map'
        ])
    ).all()

    # Check if seed ideas already generated
    existing_seeds = db.query(BrainstormIdea).filter(
        BrainstormIdea.project_id == project.id,
        BrainstormIdea.idea_type.like('seed_%')
    ).order_by(BrainstormIdea.order_index).all()

    # Create tabs for the three brainstorming sessions
    tab1, tab2, tab3 = st.tabs(["💡 Pre-brainstorm", "🚀 Idea Expansion", "🗂️ Idea Categorization"])

    # Tab 1: Pre-brainstorm Seed Ideas
    with tab1:
        # Check if Define stage is completed
        if not define_content:
            st.warning("⚠️ Please complete the Define stage first!")
            st.info("""
            **To generate seed ideas, you need to:**
            1. Go to the **Define** stage
            2. Generate at least one analysis (Empathy Map, Persona, Journey Map, etc.)
            """)
        else:
            # Show existing seed ideas or generate button
            if existing_seeds:
                latest_seed = max(existing_seeds, key=lambda x: x.created_at)

                # Show model badge
                display_model_badge(latest_seed.model_used)

                # Show timestamp
                st.markdown(f"<small style='color: gray;'>Last updated: {format_local_time(latest_seed.created_at)}</small>", unsafe_allow_html=True)

                # Display existing seed ideas
                st.markdown("")
                display_seed_ideas(existing_seeds)

                # Display regenerate button
                st.markdown("")
                if st.button("🔄 Regenerate Seed Ideas", type="primary", use_container_width=True):
                    # Delete existing seeds before regenerating
                    db.query(BrainstormIdea).filter(
                        BrainstormIdea.project_id == project.id,
                        BrainstormIdea.idea_type.like('seed_%')
                    ).delete()
                    db.commit()
                    success = generate_seed_ideas(project.id)
                    db.close()
                    if success:
                        st.toast("✅ Seeds regenerated! Reopen Brainstorming to see the new ideas.", icon="✨")
                        st.rerun()
            else:
                # No seeds yet - show generate button
                if st.button("✨ Generate Seed Ideas", type="primary", use_container_width=True):
                    success = generate_seed_ideas(project.id)
                    db.close()
                    if success:
                        st.toast("✅ Seed ideas generated! Reopen Brainstorming to see the results.", icon="✨")
                        st.rerun()

    # Tab 2: Real-time Idea Expansion
    with tab2:
        # Get existing expansions
        expansions = db.query(BrainstormIdea).filter(
            BrainstormIdea.project_id == project.id,
            BrainstormIdea.idea_type == 'expansion'
        ).order_by(BrainstormIdea.created_at).all()

        # Display existing expansions
        for expansion in expansions:
            idea_label = expansion.parent.idea_text if expansion.parent else 'Idea'
            timestamp = format_local_time(expansion.created_at)
            with st.expander(f"💭 {idea_label} | {timestamp}", expanded=False):
                st.markdown(expansion.idea_text)

        # New expansion input
        user_idea = st.text_input(
            "Enter your idea to expand:",
            key="new_idea_input",
            placeholder="Type your idea here..."
        )

        if st.button("🔍 Expand It", key="expand_new_idea", use_container_width=True):
            if user_idea.strip():
                expand_idea(project.id, user_idea)
                db.close()
                st.rerun()
            else:
                st.warning("Please enter an idea first")

    # Tab 3: Idea Categorization
    with tab3:
        # Get latest categorization
        categorization = db.query(IdeaCategorization).filter(
            IdeaCategorization.project_id == project.id
        ).order_by(IdeaCategorization.updated_at.desc()).first()

        if categorization:
            st.markdown(f"<small style='color: gray;'>Last updated: {format_local_time(categorization.updated_at)}</small>", unsafe_allow_html=True)
            st.markdown("")
            st.markdown(categorization.categorization_text)
        else:
            st.info("💡 Categorization will appear here automatically after you expand ideas.")

    db.close()

def display_seed_ideas(seeds):
    """Display seed ideas grouped by type"""
    practical = [s for s in seeds if s.idea_type == 'seed_practical']
    bold = [s for s in seeds if s.idea_type == 'seed_bold']
    wild = [s for s in seeds if s.idea_type == 'seed_wild']
    
    st.markdown("#### 🎯 Practical Ideas")
    for idea in practical:
        st.markdown(f"- {idea.idea_text}")
    
    st.markdown("#### 🚀 Bold Ideas")
    for idea in bold:
        st.markdown(f"- {idea.idea_text}")
    
    st.markdown("#### 🌟 Wild Ideas")
    for idea in wild:
        st.markdown(f"- {idea.idea_text}")

def generate_seed_ideas(project_id):
    """
    Generate 15 seed ideas (5 practical, 5 bold, 5 wild)

    Returns:
        bool: True if successful, False if failed
    """
    from prompts.ideate.brainstorming import BRAINSTORM_SEED_IDEAS_PROMPT

    db = get_db()
    try:
        project = db.query(Project).filter(Project.id == project_id).first()
        if not project:
            st.error("Project not found!")
            return False

        # Get all latest Define stage content for each content type
        content_types = ['empathy_map', 'persona', 'journey_map', 'affinity_map', 'storytelling', 'stakeholder_map']
        problem_define = ""

        for content_type in content_types:
            latest_content = db.query(GeneratedContent).filter(
                GeneratedContent.project_id == project_id,
                GeneratedContent.content_type == content_type
            ).order_by(GeneratedContent.created_at.desc()).first()

            if latest_content:
                # Add content type header
                content_name = content_type.replace('_', ' ').title()
                problem_define += f"\n**{content_name}:**\n{latest_content.content}\n\n"

        # Fallback if no Define content (shouldn't happen due to check in dialog)
        if not problem_define.strip():
            problem_define = f"Solve problems in {project.area} to achieve {project.goal}"

        with st.spinner("🤖 Generating seed ideas... This may take a moment."):
            try:
                ai_service = AIService(model=project.preferred_model)
            except ValueError as e:
                if "API_KEY not set" in str(e):
                    st.error(f"❌ API key missing: {str(e)}")
                else:
                    st.error(f"Configuration error: {str(e)}")
                return False

            user_prompt = f"Generate 15 diverse solution ideas for the project based on the problem definition."

            system_prompt = BRAINSTORM_SEED_IDEAS_PROMPT.format(
                project_name=project.name,
                project_area=project.area,
                project_goal=project.goal,
                problem_define=problem_define
            )

            result = ai_service._call_openai(system_prompt, user_prompt)

            if result:
                # Parse and save ideas with model info
                parse_and_save_seed_ideas(project_id, result, project.preferred_model, db)
                st.success("✅ Seed ideas generated!")
                return True
            else:
                st.error("Failed to generate seed ideas. Please try again.")
                return False

    except Exception as e:
        st.error(f"Error: {str(e)}")
        return False
    finally:
        db.close()

def parse_and_save_seed_ideas(project_id, ai_result, model_used, db):
    """Parse AI result and save to database with model tracking"""
    # This is simplified - implement proper parsing
    lines = ai_result.split('\n')
    order = 0
    current_type = None

    for line in lines:
        line = line.strip()
        if 'PRACTICAL' in line.upper():
            current_type = 'seed_practical'
        elif 'BOLD' in line.upper():
            current_type = 'seed_bold'
        elif 'WILD' in line.upper():
            current_type = 'seed_wild'
        elif line.startswith('-') or line.startswith('*'):
            if current_type:
                idea = BrainstormIdea(
                    project_id=project_id,
                    idea_type=current_type,
                    idea_text=line.lstrip('-* '),
                    model_used=model_used,
                    order_index=order
                )
                db.add(idea)
                order += 1

    db.commit()

def expand_idea(project_id, user_idea):
    """Expand a user's idea using AI"""
    from prompts.ideate.brainstorming import BRAINSTORM_EXPAND_IDEA_PROMPT

    db = get_db()
    try:
        project = db.query(Project).filter(Project.id == project_id).first()

        # Get latest summary
        latest_summary = db.query(StageSummary).filter(
            StageSummary.project_id == project_id,
            StageSummary.stage == "define"
        ).order_by(StageSummary.created_at.desc()).first()

        problem_summary = latest_summary.summary_text if latest_summary else f"{project.goal}"

        with st.spinner("🔍 Expanding your idea..."):
            ai_service = AIService(model=project.preferred_model)

            system_prompt = BRAINSTORM_EXPAND_IDEA_PROMPT.format(
                project_name=project.name,
                project_area=project.area,
                problem_summary=problem_summary,
                user_idea=user_idea
            )

            expansion = ai_service._call_openai(system_prompt, f"Expand this idea: {user_idea}")

            if expansion:
                # Save parent idea
                parent = BrainstormIdea(
                    project_id=project_id,
                    idea_type='user_input',
                    idea_text=user_idea,
                    model_used=None  # User input, no model used
                )
                db.add(parent)
                db.flush()

                # Save expansion with model info
                expanded = BrainstormIdea(
                    project_id=project_id,
                    idea_type='expansion',
                    idea_text=expansion,
                    parent_id=parent.id,
                    model_used=project.preferred_model
                )
                db.add(expanded)
                db.commit()

                # Trigger categorization quietly in background
                categorize_ideas(project_id)

    except Exception as e:
        st.error(f"Error: {str(e)}")
    finally:
        db.close()

def categorize_ideas(project_id):
    """Categorize all ideas for a project"""
    from prompts.ideate.brainstorming import BRAINSTORM_CATEGORIZE_IDEAS_PROMPT

    db = get_db()
    try:
        project = db.query(Project).filter(Project.id == project_id).first()

        # Get all seed ideas and expansions
        all_ideas = db.query(BrainstormIdea).filter(
            BrainstormIdea.project_id == project_id
        ).order_by(BrainstormIdea.created_at).all()

        if not all_ideas:
            return

        # Format all ideas for the prompt
        ideas_text = ""
        for idea in all_ideas:
            if idea.idea_type in ('user_input', 'expansion'):
                ideas_text += f"- {idea.idea_text}\n"

        ai_service = AIService(model=project.preferred_model)

        system_prompt = BRAINSTORM_CATEGORIZE_IDEAS_PROMPT.format(
            project_name=project.name,
            project_area=project.area,
            all_ideas=ideas_text
        )

        categorization_result = ai_service._call_openai(system_prompt, "Categorize all ideas into themes")

        if categorization_result:
            # Check if categorization already exists
            existing = db.query(IdeaCategorization).filter(
                IdeaCategorization.project_id == project_id
            ).first()

            if existing:
                # Update existing
                existing.categorization_text = categorization_result
                existing.updated_at = datetime.now(timezone.utc)
            else:
                # Create new
                categorization = IdeaCategorization(
                    project_id=project_id,
                    categorization_text=categorization_result
                )
                db.add(categorization)

            db.commit()

            # Generate ideate stage summary after categorization
            generate_ideate_summary(project_id)

    except Exception:
        # Silent fail - categorization is optional
        pass
    finally:
        db.close()

def generate_ideate_summary(project_id):
    """
    Automatically generate Ideate stage summary from brainstorming, mind mapping, and SCAMPER results.
    Called silently after categorization is updated.
    Keeps only 1 summary per project for ideate stage (overwrites previous version).
    """
    db = get_db()
    try:
        # Get project
        project = db.query(Project).filter(Project.id == project_id).first()
        if not project:
            return

        # Collect all ideation data
        ideation_data = ""

        # 1. Get brainstorming categorization
        categorization = db.query(IdeaCategorization).filter(
            IdeaCategorization.project_id == project_id
        ).order_by(IdeaCategorization.updated_at.desc()).first()

        if categorization:
            ideation_data += f"**Brainstorming Categories:**\n{categorization.categorization_text}\n\n"

        # 2. Get seed ideas
        seed_ideas = db.query(BrainstormIdea).filter(
            BrainstormIdea.project_id == project_id,
            BrainstormIdea.idea_type.like('seed_%')
        ).order_by(BrainstormIdea.order_index).all()

        if seed_ideas:
            ideation_data += "**Seed Ideas:**\n"
            for idea in seed_ideas[:10]:  # Limit to first 10
                ideation_data += f"- {idea.idea_text}\n"
            ideation_data += "\n"

        # 3. Get expansions (user-generated ideas)
        expansions = db.query(BrainstormIdea).filter(
            BrainstormIdea.project_id == project_id,
            BrainstormIdea.idea_type == 'expansion'
        ).order_by(BrainstormIdea.created_at.desc()).limit(5).all()

        if expansions:
            ideation_data += "**Expanded Ideas:**\n"
            for expansion in expansions:
                # Get first 100 chars
                preview = expansion.idea_text[:100] + "..." if len(expansion.idea_text) > 100 else expansion.idea_text
                ideation_data += f"- {preview}\n"
            ideation_data += "\n"

        # TODO: Add mind mapping results when implemented
        # TODO: Add SCAMPER results when implemented

        # Only generate summary if we have ideation data
        if not ideation_data.strip():
            return

        # Generate summary using AI
        from prompts.summary import IDEATE_STAGE_SUMMARY_PROMPT
        ai_service = AIService(model=project.preferred_model)

        system_prompt = IDEATE_STAGE_SUMMARY_PROMPT.format(
            project_name=project.name,
            project_area=project.area,
            project_goal=project.goal,
            ideation_data=ideation_data
        )

        user_prompt = "Synthesize the ideation results into a concise summary."

        summary_text = ai_service._call_openai(system_prompt, user_prompt)

        if summary_text:
            # Check if summary already exists for this project's ideate stage
            existing_summary = db.query(StageSummary).filter(
                StageSummary.project_id == project_id,
                StageSummary.stage == "ideate"
            ).first()

            if existing_summary:
                # Update existing summary (keep only 1 version)
                existing_summary.summary_text = summary_text
                existing_summary.created_at = datetime.now(timezone.utc)
            else:
                # Create new summary
                new_summary = StageSummary(
                    project_id=project_id,
                    stage="ideate",
                    summary_text=summary_text,
                    version=1
                )
                db.add(new_summary)

            db.commit()

    except Exception:
        # Silently fail - don't interrupt user experience
        pass
    finally:
        db.close()