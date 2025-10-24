import streamlit as st
from config.database import get_db
from database.models import BrainstormIdea, StageSummary, Project, IdeaCategorization
from services.ai_service import AIService
from datetime import datetime

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

    # Check if Define stage summary exists
    define_summary = db.query(StageSummary).filter(
        StageSummary.project_id == project.id,
        StageSummary.stage == "define"
    ).order_by(StageSummary.created_at.desc()).first()

    # Check if seed ideas already generated
    existing_seeds = db.query(BrainstormIdea).filter(
        BrainstormIdea.project_id == project.id,
        BrainstormIdea.idea_type.like('seed_%')
    ).order_by(BrainstormIdea.order_index).all()

    # Create tabs for the three brainstorming sessions
    tab1, tab2, tab3 = st.tabs(["💡 Pre-brainstorm", "🚀 Idea Expansion", "🗂️ Idea Categorization"])

    # Tab 1: Pre-brainstorm Seed Ideas
    with tab1:
        if not existing_seeds:
            # Check if Define stage is completed
            if not define_summary:
                st.warning("⚠️ Please complete the Define stage first!")
                st.info("""
                **To generate seed ideas, you need to:**
                1. Go to the **Define** stage
                2. Generate at least one analysis (Empathy Map, Persona, Journey Map, etc.)
                """)
            else:
                if st.button("✨ Generate Seed Ideas", type="primary", use_container_width=True):
                    generate_seed_ideas(project.id)
                    db.close()
                    st.rerun()
        else:
            # Display existing seed ideas
            display_seed_ideas(existing_seeds)

    # Tab 2: Real-time Idea Expansion
    with tab2:
        # Get existing expansions
        expansions = db.query(BrainstormIdea).filter(
            BrainstormIdea.project_id == project.id,
            BrainstormIdea.idea_type == 'expansion'
        ).order_by(BrainstormIdea.created_at).all()

        # Display existing expansions
        for expansion in expansions:
            with st.expander(f"💭 {expansion.parent.idea_text if expansion.parent else 'Idea'}", expanded=False):
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
    """Generate 15 seed ideas (5 practical, 5 bold, 5 wild)"""
    from prompts.ideate.brainstorming import BRAINSTORM_SEED_IDEAS_PROMPT
    
    db = get_db()
    try:
        project = db.query(Project).filter(Project.id == project_id).first()
        
        # Get latest Define stage summary
        latest_summary = db.query(StageSummary).filter(
            StageSummary.project_id == project_id,
            StageSummary.stage == "define"
        ).order_by(StageSummary.created_at.desc()).first()
        
        problem_summary = latest_summary.summary_text if latest_summary else f"Solve problems in {project.area} to achieve {project.goal}"
        
        with st.spinner("🤖 Generating seed ideas... This may take a moment."):
            ai_service = AIService()
            
            user_prompt = f"Generate 15 diverse solution ideas for the project."
            
            system_prompt = BRAINSTORM_SEED_IDEAS_PROMPT.format(
                project_name=project.name,
                project_area=project.area,
                project_goal=project.goal,
                problem_summary=problem_summary
            )
            
            result = ai_service._call_openai(system_prompt, user_prompt)
            
            if result:
                # Parse and save ideas (simplified - you'd parse the result properly)
                # For now, save as single text per category
                parse_and_save_seed_ideas(project_id, result, db)
                st.success("✅ Seed ideas generated!")
            
    except Exception as e:
        st.error(f"Error: {str(e)}")
    finally:
        db.close()

def parse_and_save_seed_ideas(project_id, ai_result, db):
    """Parse AI result and save to database"""
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
            ai_service = AIService()

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
                    idea_text=user_idea
                )
                db.add(parent)
                db.flush()

                # Save expansion
                expanded = BrainstormIdea(
                    project_id=project_id,
                    idea_type='expansion',
                    idea_text=expansion,
                    parent_id=parent.id
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

        ai_service = AIService()

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
                existing.updated_at = datetime.utcnow()
            else:
                # Create new
                categorization = IdeaCategorization(
                    project_id=project_id,
                    categorization_text=categorization_result
                )
                db.add(categorization)

            db.commit()

    except Exception as e:
        # Silent fail - categorization is optional
        pass
    finally:
        db.close()