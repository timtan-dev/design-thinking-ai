"""Step 3: HTML/CSS Wireframe Code Generation"""

import streamlit as st
from database.models import MockupIteration
from services.ai_service import AIService
from prompts.prototype.code_generation import GENERATE_HTML_CSS_PROMPT, GENERATE_TAILWIND_HTML_PROMPT

def render_code_step(prototype_page, project, db):
    """Render the HTML/CSS code generation step"""

    st.markdown("## 💻 Step 3: HTML/CSS Wireframe")

    # Get final mockup
    final_mockup = db.query(MockupIteration).filter(
        MockupIteration.id == prototype_page.final_mockup_id
    ).first()

    if not final_mockup:
        st.warning("No mockup selected. Please complete Step 2 first.")
        return

    # Layout: Generate Code | Live Preview
    col1, col2 = st.columns([1, 1])

    with col1:
        st.markdown("### Generated Code")

        # Framework selection
        framework = st.selectbox(
            "Framework",
            ["Plain HTML/CSS", "Tailwind CSS", "Bootstrap"],
            key=f"code_framework_{prototype_page.id}"
        )

        # Generate code button
        if not prototype_page.code_generated or st.button("🔄 Regenerate Code"):
            generate_code(prototype_page, project, final_mockup, framework, db)
            st.rerun()

        # Display generated code
        if prototype_page.html_code:
            # Show tabs for HTML and CSS
            code_tab1, code_tab2 = st.tabs(["HTML", "CSS"])

            with code_tab1:
                st.code(prototype_page.html_code, language="html")
                st.download_button(
                    "📥 Download HTML",
                    data=prototype_page.html_code,
                    file_name=f"{prototype_page.page_name.lower()}.html",
                    mime="text/html",
                    use_container_width=True
                )

            with code_tab2:
                if prototype_page.css_code:
                    st.code(prototype_page.css_code, language="css")
                    st.download_button(
                        "📥 Download CSS",
                        data=prototype_page.css_code,
                        file_name=f"{prototype_page.page_name.lower()}.css",
                        mime="text/css",
                        use_container_width=True
                    )
                else:
                    st.info("CSS is embedded in HTML")

    with col2:
        st.markdown("### Live Preview")

        # Show final mockup reference
        with st.expander("🎨 Original Mockup"):
            st.image(final_mockup.image_path, use_container_width=True)

        # Display live preview
        if prototype_page.html_code:
            st.markdown("---")
            st.components.v1.html(prototype_page.html_code, height=600, scrolling=True)
        else:
            st.info("Generate code to see preview")

    # Complete button
    if prototype_page.code_generated:
        st.markdown("---")
        col_left, col_right = st.columns([3, 1])

        with col_right:
            if st.button("✅ Complete This Page", type="primary", use_container_width=True):
                st.success(f"✅ Prototype for '{prototype_page.page_name}' page completed!")
                st.balloons()

        with col_left:
            st.markdown("🎉 **Congratulations!** Your wireframe is ready for testing.")

def generate_code(prototype_page, project, final_mockup, framework, db):
    """Generate HTML/CSS code from mockup"""

    with st.spinner("💻 Generating code... This may take a moment."):
        ai_service = AIService(model=project.preferred_model)

        # Create mockup description (could use vision API to analyze the mockup image)
        mockup_description = f"""
        This is a mockup for the {prototype_page.page_name} page of {project.name}.
        Style: {final_mockup.style_params.get('style', 'modern')} design
        Color scheme: {final_mockup.style_params.get('color_scheme', 'clean and modern')}
        """

        # Choose appropriate prompt based on framework
        if framework == "Tailwind CSS":
            prompt = GENERATE_TAILWIND_HTML_PROMPT.format(
                project_name=project.name,
                page_name=prototype_page.page_name,
                mockup_description=mockup_description
            )
        else:
            prompt = GENERATE_HTML_CSS_PROMPT.format(
                project_name=project.name,
                page_name=prototype_page.page_name,
                project_goal=project.goal,
                mockup_description=mockup_description,
                framework=framework
            )

        # Generate code
        code_output = ai_service._call_openai(
            "You are an expert frontend developer generating production-ready HTML/CSS code.",
            prompt
        )

        # Parse HTML and CSS from output
        html_code, css_code = parse_code_output(code_output, framework)

        # Save to database
        prototype_page.html_code = html_code
        prototype_page.css_code = css_code
        prototype_page.code_generated = True
        db.commit()

        st.success("✅ Code generated successfully!")

def parse_code_output(code_output, framework):
    """Parse HTML and CSS from AI output"""

    # Extract HTML
    html_start = code_output.find("```html")
    html_end = code_output.find("```", html_start + 7)

    if html_start != -1 and html_end != -1:
        html_code = code_output[html_start + 7:html_end].strip()
    else:
        # Fallback: try to find any code block
        html_code = code_output.strip()

    # For Tailwind, CSS is embedded, so return None for CSS
    if framework == "Tailwind CSS":
        return html_code, None

    # Extract CSS if it's separate
    css_start = code_output.find("```css")
    css_end = code_output.find("```", css_start + 6)

    if css_start != -1 and css_end != -1:
        css_code = code_output[css_start + 6:css_end].strip()
        return html_code, css_code

    # CSS might be embedded in HTML
    return html_code, None
