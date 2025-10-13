import streamlit as st
from config.database import get_db
from database.models import GeneratedContent, ResearchData

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
    placeholder_content = f"## {content_name} Analysis\nPlaceholder analysis content."
    db = get_db()
    try:
        generated = GeneratedContent(project_id=project_id, content_type=content_type, content=placeholder_content)
        db.add(generated)
        db.commit()
        st.success(f"{content_name} generated successfully!")
    finally:
        db.close()
