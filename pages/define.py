import streamlit as st
from config.database import get_db
from database.models import GeneratedContent, ResearchData, Project
from services.ai_service import AIService

ANALYSIS_METHODS = {
    "empathy_map": {"name": "Empathy Map", "icon": "🧩"},
    "persona": {"name": "Persona", "icon": "👤"},
    "journey_map": {"name": "Journey Map", "icon": "📈"},
    "affinity_map": {"name": "Affinity Map", "icon": "🗂️"},
    "storytelling": {"name": "Storytelling", "icon": "📚"},
    "stakeholder_map": {"name": "Stakeholder Map", "icon": "🌐"}
}

def render_define_page(project):
    db = get_db()
    generated_content = db.query(GeneratedContent).filter(GeneratedContent.project_id == project.id).all()
    research_data = db.query(ResearchData).filter(ResearchData.project_id == project.id).all()
    db.close()

    # Group generated content by type
    content_by_type = {}
    for content in generated_content:
        if content.content_type not in content_by_type:
            content_by_type[content.content_type] = []
        content_by_type[content.content_type].append(content)

    # Add margin between stage section and method section
    st.markdown('<div style="margin-top: 2rem;"></div>', unsafe_allow_html=True)

    st.markdown('<div class="cards-grid">', unsafe_allow_html=True)
    cols = st.columns(3)

    for idx, (method_key, method_info) in enumerate(ANALYSIS_METHODS.items()):
        with cols[idx % 3]:
            is_generated = method_key in content_by_type

            # Render clickable card
            if st.button(
                f"{method_info['icon']} {method_info['name']}",
                key=f"card_{method_key}",
                use_container_width=True,
                type="primary" if is_generated else "secondary"
            ):
                open_analysis_dialog(project, method_key, method_info["name"], research_data)

            # Small caption for status
            if is_generated:
                count = len(content_by_type[method_key])
                st.caption(f"✓ {count} analysis generated")

    st.markdown("</div>", unsafe_allow_html=True)


@st.dialog("Analysis Manager")
def open_analysis_dialog(project, method_key, method_name, research_data):
    """Dialog window for viewing existing analyses and generating new ones"""
    st.markdown(f"### {method_name}")

    # Fetch existing generated content for this method
    db = get_db()
    existing_content = db.query(GeneratedContent).filter(
        GeneratedContent.project_id == project.id,
        GeneratedContent.content_type == method_key
    ).order_by(GeneratedContent.created_at.desc()).all()
    db.close()

    # Show existing analyses in expanders
    if existing_content:
        st.markdown(f"**{len(existing_content)} Existing Analysis** {'Results' if len(existing_content) > 1 else 'Result'}")

        for idx, content in enumerate(existing_content, 1):
            # Format timestamp
            created_time = content.created_at.strftime("%Y-%m-%d %H:%M")

            with st.expander(f"📄 Analysis #{idx} - Generated on {created_time}", expanded=(idx == 1)):
                st.markdown(content.content)

                # Add download button
                st.download_button(
                    label="📥 Download",
                    data=content.content,
                    file_name=f"{project.name.lower().replace(' ', '_')}_{method_key}_{idx}.md",
                    mime="text/markdown",
                    key=f"download_{method_key}_{content.id}",
                    use_container_width=True
                )

        st.divider()

    # Generate new analysis section
    st.markdown("### 🤖 Generate New Analysis")

    if not research_data:
        st.warning("⚠️ No research data uploaded yet. The AI will generate a sample analysis based on project context.")
    else:
        st.info(f"📊 {len(research_data)} research file(s) will be analyzed")

    if st.button("✨ Generate New Analysis", key=f"gen_btn_{method_key}", type="primary", use_container_width=True):
        generate_analysis(project.id, method_key, method_name, research_data)
        st.rerun()


def generate_analysis(project_id, content_type, content_name, research_data):
    """Generate AI-powered analysis using uploaded research data"""

    # Import the appropriate prompt based on content type
    if content_type == "empathy_map":
        from prompts.define.empathy_map import EMPATHY_MAP_PROMPT as ANALYSIS_PROMPT
    elif content_type == "persona":
        from prompts.define.persona import PERSONA_PROMPT as ANALYSIS_PROMPT
    elif content_type == "journey_map":
        from prompts.define.journey_map import JOURNEY_MAP_PROMPT as ANALYSIS_PROMPT
    elif content_type == "affinity_map":
        from prompts.define.affinity_map import AFFINITY_MAP_PROMPT as ANALYSIS_PROMPT
    elif content_type == "storytelling":
        from prompts.define.storytelling import STORYTELLING_PROMPT as ANALYSIS_PROMPT
    elif content_type == "stakeholder_map":
        from prompts.define.stakeholder_map import STAKEHOLDER_MAP_PROMPT as ANALYSIS_PROMPT
    else:
        st.error(f"Unknown analysis type: {content_type}")
        return

    db = get_db()

    try:
        # Fetch project object
        project = db.query(Project).filter(Project.id == project_id).first()
        if not project:
            st.error("Project not found!")
            return

        # Show generating message
        with st.spinner(f"🤖 Generating {content_name}... This may take a moment."):
            # Initialize AI service
            ai_service = AIService()

            # Format research data
            research_section = ""
            if research_data:
                research_section = "\n**Research Data:**\n"
                for idx, data in enumerate(research_data, 1):
                    method_name = data.method_type.replace('_', ' ').title()
                    research_section += f"\n--- {method_name} Data {idx} ---\n"
                    research_section += f"{data.file_content[:5000]}\n"  # Limit to first 5000 chars per file

            # Build user prompt
            user_prompt = f"""
            **Project Context:**
            Project: {project.name}
            Area: {project.area}
            Goal: {project.goal}
            {research_section}

            Generate a comprehensive {content_name.lower()} based on the research data provided above.
            Include specific references to the research data sources.
            """

            # Call AI service
            generated_content = ai_service._call_openai(ANALYSIS_PROMPT, user_prompt)

            if not generated_content:
                st.error("Failed to generate content. Please try again.")
                return

            # Save to database
            new_content = GeneratedContent(
                project_id=project_id,
                content_type=content_type,
                content=generated_content
            )
            db.add(new_content)
            db.commit()

            st.success(f"✅ {content_name} generated successfully!")

    except Exception as e:
        st.error(f"Error generating {content_name}: {str(e)}")
        db.rollback()

    finally:
        db.close()
