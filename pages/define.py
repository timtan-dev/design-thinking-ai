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

    # if not research_data:
    #     st.warning("⚠️ No research data uploaded yet.")
    #     return

    generated_types = {c.content_type for c in generated_content}
    st.markdown('<div class="cards-grid">', unsafe_allow_html=True)
    cols = st.columns(3)
    for idx, (method_key, method_info) in enumerate(ANALYSIS_METHODS.items()):
        with cols[idx % 3]:
            is_generated = method_key in generated_types
            status_text = "✓ Analysis Generated" if is_generated else "Click to generate"
            with st.container():
                st.markdown(f"""
                    <div class="method-card">
                        <div class="method-icon">{method_info['icon']}</div>
                        <div class="method-name">{method_info['name']}</div>
                        <div class="method-status">{status_text}</div>
                    </div>
                """, unsafe_allow_html=True)
                if st.button(f"🤖 Generate {method_info['name']}", key=f"generate_{method_key}"):
                    generate_analysis(project.id, method_key, method_info['name'], research_data)
                    st.rerun()

def generate_analysis(project_id, content_type, content_name, research_data):
    """Generate AI-powered analysis using uploaded research data"""
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

            # Format research data for AI service
            research_data_list = []
            for data in research_data:
                research_data_list.append({
                    'method_type': data.method_type,
                    'file_content': data.file_content,
                    'file_path': data.file_path
                })

            # Prepare project dict for AI service
            project_dict = {
                'name': project.name,
                'area': project.area,
                'goal': project.goal
            }

            # Generate content based on type
            generated_content = None

            if content_type == "empathy_map":
                generated_content = ai_service.create_empathy_map(project_dict, research_data_list)

            elif content_type == "persona":
                generated_content = ai_service.create_persona(project_dict, research_data_list)

            elif content_type == "journey_map":
                generated_content = ai_service.create_journey_map(project_dict, research_data_list)

            elif content_type == "affinity_map":
                generated_content = ai_service.create_affinity_map(project_dict, research_data_list)

            elif content_type == "storytelling":
                generated_content = ai_service.create_user_story(project_dict, research_data_list)

            elif content_type == "stakeholder_map":
                generated_content = ai_service.create_stakeholder_map(project_dict, research_data_list)

            else:
                st.error(f"Unknown analysis type: {content_type}")
                return

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

            # Show preview in expander
            with st.expander("📄 View Generated Content", expanded=True):
                st.markdown(generated_content)

    except Exception as e:
        st.error(f"Error generating {content_name}: {str(e)}")
        db.rollback()

    finally:
        db.close()
