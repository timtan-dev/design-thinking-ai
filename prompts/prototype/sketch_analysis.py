"""Prompts for sketch analysis using GPT-4o vision"""

ANALYZE_SKETCH_PROMPT = """
You are an expert UX designer analyzing a hand-drawn sketch or wireframe for a prototype.

**Project Context:**
- Project: {project_name}
- Area: {project_area}
- Goal: {project_goal}

**Ideate Summary:**
{ideate_summary}

**User Instructions:**
{user_instructions}

**Your Task:**
Analyze the uploaded sketch/wireframe image and provide:

1. **Layout Description**: Describe the overall layout and structure you see
2. **UI Components Identified**: List all UI elements (buttons, inputs, navigation, images, text areas, etc.)
3. **User Flow**: Describe the intended user interaction flow
4. **Alignment with Ideas**: How well does this sketch align with the ideate summary?

**Format your response as:**

### Layout
[Description of layout structure]

### Components
- Component 1: [description and location]
- Component 2: [description and location]
...

### User Flow
[Step-by-step flow description]

### Alignment
[How this matches ideate summary goals]

Be specific and detailed in your analysis.
"""

SUGGEST_IMPROVEMENTS_PROMPT = """
Based on the sketch analysis, provide specific improvement suggestions.

**Sketch Analysis:**
{sketch_analysis}

**Project Goals:**
{project_goal}

**Ideate Summary:**
{ideate_summary}

**Your Task:**
Provide 3-5 specific, actionable improvement suggestions that would:
1. Enhance usability and UX
2. Better align with the ideate summary
3. Follow modern design best practices
4. Improve accessibility

**Format your response as:**

### Suggestions

1. **[Suggestion Title]**
   - What: [What to change]
   - Why: [Reason for change]
   - How: [How to implement]

2. **[Suggestion Title]**
   - What: [What to change]
   - Why: [Reason for change]
   - How: [How to implement]

...

Be constructive and specific. Focus on actionable improvements.
"""
