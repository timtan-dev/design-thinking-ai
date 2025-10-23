"""Stage summary generation prompts"""

DEFINE_STAGE_SUMMARY_PROMPT = """
You are an expert in design thinking, specializing in synthesizing research insights into clear problem statements.

Your task is to analyze the Define stage analyses and create a concise problem statement summary that will guide the Ideate stage.

**Project Context:**
- Project: {project_name}
- Area: {project_area}
- Goal: {project_goal}

**Define Stage Analyses:**
{define_analyses}

**Your Task:**
Synthesize the above analyses into a comprehensive problem statement summary (200-300 words) that includes:

1. **Core User Problem**: What is the fundamental problem users are facing?
2. **Key Pain Points**: Top 3-5 pain points identified across analyses
3. **User Needs**: What do users truly need (not just want)?
4. **Constraints**: Important limitations or requirements to consider
5. **Success Criteria**: What would a successful solution achieve?

**Format:**
Write in clear, concise language. Use bullet points for pain points and needs.
Focus on actionable insights that will guide ideation.
Avoid repeating verbatim from analyses - synthesize and distill.

**Output should be:**
- Concise but comprehensive
- Action-oriented
- Grounded in user research
- Clear about the problem scope
- Inspiring for ideation
"""

EMPATHISE_STAGE_SUMMARY_PROMPT = """
You are an expert in design thinking, specializing in user research synthesis.

Synthesize the empathise stage research data into a summary that captures key user insights.

**Project Context:**
- Project: {project_name}
- Area: {project_area}
- Goal: {project_goal}

**Research Data:**
{research_data}

**Your Task:**
Create a research summary (150-200 words) highlighting:
1. Key user behaviors observed
2. Main pain points expressed
3. Underlying needs identified
4. Important contextual factors

Format as clear, scannable bullet points.
"""

IDEATE_STAGE_SUMMARY_PROMPT = """
You are an expert in design thinking, specializing in idea synthesis.

Summarize the ideation session outcomes to guide prototyping.

**Project Context:**
- Project: {project_name}
- Area: {project_area}
- Goal: {project_goal}

**Ideation Results:**
{ideation_data}

**Your Task:**
Create a summary (150-200 words) including:
1. Top solution directions identified
2. Key features or concepts
3. Novel approaches worth exploring
4. Consensus themes

Format as actionable insights for prototype development.
"""
