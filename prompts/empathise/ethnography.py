"""Ethnography study guide generation prompt"""

ETHNOGRAPHY_TEMPLATE_PROMPT = """
You are a professional ethnographic researcher with expertise in conducting immersive field studies for user research, anthropological studies, and design thinking projects.

**Project Context:**
- Project Name: {project_name}
- Project Area: {project_area}
- Project Goal: {project_goal}

Your task is to generate a comprehensive, professional ethnography study guide specifically tailored to this project's context. The guide should help researchers conduct effective field observations and immersive studies to understand users in their natural context related to the project area and goal.

The ethnography guide should include the following sections:

1. **Study Overview** (Planning)
   - Research objectives connected to "{project_name}"
   - Key research questions focused on {project_goal}
   - Study duration and timeline recommendations
   - Resources and equipment needed
   - Ethical considerations and consent procedures
   - How findings will inform understanding of {project_area}

2. **Participant Selection** (2-3 criteria sets)
   - Target participant profiles relevant to {project_area}
   - Recruitment strategy and screening criteria
   - Sample size recommendations
   - Diversity and representation considerations
   - Relationship building approach

3. **Observation Contexts** (3-5 settings)
   - Key locations/environments to observe related to {project_area}
   - Time periods and situations of interest
   - Activities and behaviors to focus on
   - Social dynamics to note
   - Environmental factors relevant to {project_goal}

4. **Observation Framework** (Detailed guide)
   - What to observe:
     * Physical environment and artifacts
     * Behaviors and actions
     * Social interactions
     * Communication patterns
     * Workarounds and adaptations
     * Emotional responses and body language
   - How to observe:
     * Observation techniques (participant vs. non-participant)
     * Note-taking strategies
     * Photo/video documentation guidelines
     * Frequency and duration of sessions
   - Questions to ask yourself while observing

5. **Field Notes Template**
   - Structured format for recording observations
   - Sections for: Date/Time, Location, Context, Observations, Interpretations, Questions
   - Prompts for capturing sensory details
   - Space for sketches and diagrams
   - Reflection prompts related to {project_name}

6. **Engagement Activities** (3-5 activities)
   - Contextual inquiry questions to ask participants
   - Artifact collection suggestions
   - Shadowing protocols
   - "Day in the life" documentation approach
   - Cultural probes and activities specific to {project_area}

7. **Analysis Framework**
   - Pattern identification guidance
   - Thematic analysis approach
   - Cultural model mapping
   - Insight synthesis related to {project_goal}
   - How to translate observations into design opportunities

8. **Documentation Checklist**
   - Pre-study preparation items
   - During-study capture requirements
   - Post-session documentation tasks
   - Data organization system
   - Privacy and ethical compliance

**Format Requirements:**
- Include clear section headers and subsections
- Provide specific examples and prompts throughout
- Use [RESEARCHER TIP] boxes with practical advice
- Add [ETHICS NOTE] sections highlighting consent and privacy considerations
- Include [DESIGN THINKING CONNECTION] notes explaining how observations inform empathy
- Make it printable and field-ready for use during research

**Tone and Style:**
The guide should be {tone}, thorough, and practical for field researchers. It should emphasize respect, cultural sensitivity, and ethical research practices.

**Output Format:**
Provide a complete, ready-to-use ethnography study guide in markdown format that:
1. References the project context throughout
2. Can be immediately used to plan and conduct field research
3. Balances structured observation with openness to unexpected insights
4. Includes practical templates and checklists
5. Helps gather rich, contextual data for the empathize stage focused on understanding {project_area} and achieving {project_goal}
6. Emphasizes immersive, long-term engagement over surface-level observation
"""
