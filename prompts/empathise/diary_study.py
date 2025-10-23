"""Diary study guide generation prompt"""

DIARY_STUDY_TEMPLATE_PROMPT = """
You are a professional researcher with expertise in designing and conducting diary studies for user research, behavioral analysis, and design thinking projects.

**Project Context:**
- Project Name: {project_name}
- Project Area: {project_area}
- Project Goal: {project_goal}

Your task is to generate a comprehensive, professional diary study guide specifically tailored to this project's context. The guide should help researchers design and facilitate longitudinal self-reporting studies that capture user experiences, behaviors, and contexts over time related to the project area and goal.

The diary study guide should include the following sections:

1. **Study Overview & Design**
   - Research objectives connected to "{project_name}"
   - What you hope to learn about {project_area}
   - Study duration (recommended: 1-4 weeks)
   - Entry frequency (daily, twice-daily, weekly, or event-triggered)
   - Number of participants needed
   - Compensation and incentive structure
   - How findings will inform {project_goal}

2. **Participant Recruitment & Onboarding**
   - Target participant criteria relevant to {project_area}
   - Screening questions
   - Onboarding session plan
   - Orientation materials
   - Technology setup and training
   - Building commitment and motivation
   - Sample timeline and expectations

3. **Participant Instructions Package**
   Create a complete guide for participants including:

   **Welcome Letter**
   - Thank you and study purpose related to {project_name}
   - Why their participation matters
   - What to expect over the study period
   - Time commitment (e.g., 5-10 minutes per entry)
   - Privacy and data usage
   - Incentive details

   **How to Complete Your Diary**
   - Step-by-step instructions
   - When to make entries (timing)
   - Where to record (app, form, physical diary)
   - What to include in each entry
   - Tips for quality entries
   - Examples of good vs. poor entries
   - Technical support contact

   **Study Timeline**
   - Week-by-week breakdown
   - Special activities or prompts per week
   - Mid-study check-in plans
   - Final submission deadline

4. **Diary Entry Templates**

   **Template A: Daily Experience Entry**
   ```
   Date: ___________
   Time: ___________

   Today's Activity/Experience related to [project area]:
   [Open text field]

   Context - Where were you? Who was with you?
   [Open text field]

   What were you trying to accomplish?
   [Open text field]

   How did it go? (Rate 1-5: Very Poor to Very Good)
   ☐ 1  ☐ 2  ☐ 3  ☐ 4  ☐ 5

   What worked well?
   [Open text field]

   What was frustrating or challenging?
   [Open text field]

   How did this make you feel?
   [Open text field]

   Photo or screenshot (optional):
   [Upload field]

   Any other observations:
   [Open text field]
   ```

   **Template B: Event-Triggered Entry**
   (To be completed when a specific event occurs related to {project_area})
   ```
   Date & Time: ___________

   What just happened?
   [Open text field]

   What triggered this?
   [Open text field]

   What did you do?
   [Open text field]

   Outcome:
   [Open text field]

   Capture the moment (photo/video/audio):
   [Upload field]
   ```

   **Template C: Weekly Reflection**
   ```
   Week: ___________

   This week's highlights:
   [Open text field]

   This week's lowlights:
   [Open text field]

   Patterns I noticed:
   [Open text field]

   Something surprising:
   [Open text field]

   Questions or thoughts:
   [Open text field]
   ```

5. **Prompt Library**
   Create 15-20 specific prompts tailored to {project_area} that can be rotated or randomly assigned:

   - Daily prompts (for routine entries)
   - Situation-specific prompts (for particular contexts)
   - Reflection prompts (for deeper thinking)
   - Comparative prompts (compare today vs. yesterday, ideal vs. reality)
   - Creative prompts (drawings, metaphors, stories)

   Each prompt should relate to exploring {project_goal}

   Examples:
   - "Describe a moment today when you interacted with [relevant to project area]..."
   - "What would have made today's experience better?"
   - "Take a photo of something that represents your challenge with [project area]"

6. **Multimedia Capture Guidelines**
   - Photo instructions: What to photograph and why
   - Video instructions: Short clips (15-30 sec) capturing moments
   - Audio notes: When and how to use voice recordings
   - Screenshots: Capturing digital interactions
   - Privacy considerations: What NOT to capture
   - Quality tips: Lighting, framing, clarity

7. **Researcher's Implementation Plan**

   **Pre-Launch (1-2 weeks before)**
   - Finalize templates and tools
   - Recruit participants
   - Create study materials
   - Set up data collection system
   - Conduct orientation sessions

   **During Study**
   - Daily monitoring of submissions
   - Engagement maintenance strategies:
     * Weekly check-in messages
     * Responding to participant questions
     * Gentle reminders for missing entries
     * Encouragement and appreciation
   - Troubleshooting technical issues
   - Adaptive prompts based on emerging themes

   **Post-Study**
   - Closing interviews or debrief sessions
   - Final questionnaire
   - Incentive distribution
   - Thank you communications

8. **Keeping Participants Engaged**
   - Motivation strategies
   - Communication plan and frequency
   - Gamification elements (streaks, badges, completion milestones)
   - Mid-study surprise and delight moments
   - Regular acknowledgment of contributions
   - [ENGAGEMENT TIP] boxes with proven techniques

9. **Data Analysis Framework**
   - Organizing and coding diary entries
   - Identifying patterns across participants and over time
   - Timeline and journey mapping
   - Sentiment analysis over duration
   - Comparing early vs. late study insights
   - Extracting themes and insights relevant to {project_area}
   - Translating findings into design opportunities for {project_name}

10. **Quality Control**
    - Criteria for complete entries
    - Red flags for low-quality data
    - How to handle missing entries
    - When to follow up with participants
    - Ensuring data richness and depth

11. **Ethical Considerations**
    - Informed consent for longitudinal study
    - Privacy in personal spaces and moments
    - Right to skip entries or withdraw
    - Sensitive content handling
    - Data security for ongoing collection
    - [ETHICS NOTE] reminders throughout

12. **Tools & Technology Recommendations**
    - Suggested platforms (Google Forms, specialized diary study apps, etc.)
    - Mobile vs. web considerations
    - Offline capability needs
    - Notification and reminder systems
    - Data export and storage

**Format Requirements:**
- Include clear, participant-friendly language in all templates
- Provide complete examples of filled entries
- Use [PARTICIPANT TIP] boxes in participant-facing materials
- Add [RESEARCHER NOTE] boxes in implementation sections
- Include [DESIGN THINKING CONNECTION] explaining how longitudinal data builds empathy
- Make materials both digital-friendly and printable

**Tone and Style:**
Participant-facing materials should be {tone}, encouraging, and appreciative. Researcher-facing materials should be thorough and practical. Overall tone should emphasize collaboration and value of participant contributions.

**Output Format:**
Provide a complete, ready-to-use diary study guide in markdown format that:
1. References the project context throughout
2. Includes both participant instructions and researcher implementation guide
3. Can be immediately adapted for a diary study
4. Provides 3-5 entry templates and 15-20 prompts
5. Helps gather rich, longitudinal data for the empathize stage focused on understanding experiences in {project_area} and achieving {project_goal}
6. Includes strategies for maintaining engagement throughout the study period
"""
