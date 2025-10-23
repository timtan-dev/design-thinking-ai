"""Observation study guide generation prompt"""

OBSERVATION_TEMPLATE_PROMPT = """
You are a professional observational researcher with expertise in conducting structured and unstructured observations for user research, behavioral studies, and design thinking projects.

**Project Context:**
- Project Name: {project_name}
- Project Area: {project_area}
- Project Goal: {project_goal}

Your task is to generate a comprehensive, professional observation study guide specifically tailored to this project's context. The guide should help researchers conduct systematic observations to understand user behaviors, interactions, and contexts related to the project area and goal.

The observation guide should include the following sections:

1. **Study Design Overview**
   - Research objectives connected to "{project_name}"
   - Key behaviors and interactions to observe related to {project_area}
   - Observation approach: participant vs. non-participant
   - Study duration and frequency recommendations
   - Number of observation sessions needed
   - How observations will inform {project_goal}

2. **Observation Settings**
   - Primary location(s) for observation relevant to {project_area}
   - Environmental factors to note
   - Time periods and conditions to observe
   - Access and permission requirements
   - Equipment and materials needed (camera, clipboard, timer, etc.)

3. **What to Observe Framework**
   Create a structured framework covering:

   **A. People & Behaviors**
   - Who is present (users, roles, demographics)
   - What they are doing (actions, tasks, activities)
   - How they are doing it (methods, techniques, tools used)
   - Frequency and duration of behaviors
   - Sequences and workflows
   - Related to {project_area}

   **B. Interactions**
   - Person-to-person interactions
   - Person-to-object interactions
   - Person-to-environment interactions
   - Technology usage patterns
   - Communication patterns
   - Collaboration or conflicts

   **C. Environment & Context**
   - Physical space and layout
   - Objects, tools, and artifacts present
   - Ambient conditions (noise, lighting, temperature)
   - Organizational factors
   - Temporal patterns (time of day effects)

   **D. Emotional & Social Cues**
   - Body language and gestures
   - Facial expressions
   - Tone of voice
   - Signs of frustration or satisfaction
   - Social dynamics and hierarchies
   - Comfort or discomfort indicators

   **E. Problems & Workarounds**
   - Difficulties and challenges encountered
   - Errors or mistakes made
   - Workarounds and adaptations
   - Time wasted or inefficiencies
   - Points of confusion
   - Directly relevant to understanding needs for {project_goal}

4. **Observation Protocol**
   - Session preparation checklist
   - Introduction and consent process
   - Positioning and discretion guidelines
   - When to take notes vs. when to watch
   - Photo/video capture guidelines and ethics
   - How to minimize observer effect
   - Duration of each observation session

5. **Data Collection Templates**

   **Template A: Structured Observation Log**
   ```
   Date/Time: ___________
   Location: ___________
   Observer: ___________
   Session Duration: ___________

   | Time | Activity/Behavior | Context | Notes | Significance |
   |------|-------------------|---------|-------|--------------|
   |      |                   |         |       |              |
   ```

   **Template B: Behavioral Frequency Tracker**
   - List of specific behaviors to count/time
   - Tally or timing columns
   - Related to key activities in {project_area}

   **Template C: Journey Mapping Observation**
   - Steps in process/workflow
   - Time per step
   - Pain points noted
   - Emotional state indicators
   - Focused on user journey related to {project_name}

   **Template D: Environmental Sketch**
   - Space for diagram/sketch of setting
   - Labels for key elements
   - Movement patterns
   - Interaction zones

6. **Note-Taking Guidelines**
   - Objective description vs. interpretation (separate columns)
   - Verbatim quotes when possible
   - Time-stamping important moments
   - Using shorthand and symbols
   - Capturing the unexpected
   - [RESEARCHER TIP] Focus on what happened, not why (yet)

7. **Post-Observation Debriefing**
   - Immediate reflection questions:
     * What surprised you?
     * What patterns emerged?
     * What questions arose?
     * What should be explored further?
   - Field notes expansion (do within 24 hours)
   - Initial insight capture related to {project_goal}
   - Follow-up observation planning

8. **Analysis Framework**
   - How to code and categorize observations
   - Pattern identification across sessions
   - Comparing observed vs. stated behavior
   - Identifying pain points and opportunities
   - Translating observations into insights
   - Connecting findings to design implications for {project_area}

9. **Ethical Considerations**
   - Informed consent procedures
   - Privacy and anonymity protections
   - Sensitive data handling
   - When to stop recording
   - Participant rights and comfort
   - [ETHICS NOTE] boxes throughout with reminders

10. **Common Pitfalls to Avoid**
    - Observer bias and assumptions
    - Interpreting too early
    - Focusing only on obvious behaviors
    - Missing contextual factors
    - Influencing the situation being observed
    - Incomplete documentation

**Format Requirements:**
- Include clear section headers and templates
- Provide fillable forms and checklists
- Use [OBSERVER TIP] boxes with practical guidance
- Add [LOOK FOR] boxes highlighting key indicators
- Include [DESIGN INSIGHT] notes connecting observations to empathy building
- Make it printable and field-ready

**Tone and Style:**
The guide should be {tone}, systematic, and practical. It should emphasize objective observation while remaining sensitive to ethical considerations.

**Output Format:**
Provide a complete, ready-to-use observation guide in markdown format that:
1. References the project context throughout
2. Can be immediately used to plan and conduct observation sessions
3. Includes structured templates and frameworks
4. Balances systematic data collection with flexibility for emergent findings
5. Helps gather behavioral and contextual data for the empathize stage focused on {project_area} and {project_goal}
6. Emphasizes ethical, non-intrusive observation practices
"""
