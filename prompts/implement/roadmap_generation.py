"""Prompts for generating implementation roadmap"""

GENERATE_ROADMAP_PROMPT = """You are an expert software project manager creating an implementation roadmap.

Project Context:
- Project Name: {project_name}
- Project Goal: {project_goal}
- Team Size: {team_size} people
- Sprint Duration: {sprint_duration} weeks
- Target Launch: {target_launch_weeks} weeks from now
- Development Approach: {development_approach}

Previous Stage Insights:
{empathise_summary}

{define_summary}

{ideate_summary}

{prototype_summary}

{test_summary}

Generate a strategic implementation roadmap with 3 phases (MVP → Beta → Launch).

For each phase, provide:
1. **Phase Name & Duration** (e.g., "MVP - Weeks 1-4")
2. **Must-Have Features** (critical from test feedback, highest priority)
3. **Should-Have Features** (high value, medium effort)
4. **Could-Have Features** (nice-to-have, lower priority)
5. **Won't-Have Features** (future consideration)
6. **Dependencies** (what must be completed first)
7. **Team Allocation** (how many people needed for this phase)

**IMPORTANT**:
- Prioritize based on test feedback ratings and critical issues
- Include features mentioned in test insights as "MUST" if rated critical
- Consider dependencies (e.g., auth before dashboard)
- Be realistic with timelines given team size

Output in **valid JSON format only** (no markdown, no code blocks):
{{
  "phases": [
    {{
      "name": "Phase 1: MVP",
      "duration_weeks": 4,
      "weeks": "1-4",
      "must_have": ["Feature 1", "Feature 2"],
      "should_have": ["Feature 3"],
      "could_have": ["Feature 4"],
      "wont_have": ["Feature 5"],
      "dependencies": ["Feature X must complete before Feature Y"],
      "team_allocation": 5,
      "rationale": "Why this phase structure"
    }}
  ],
  "overall_timeline": "12 weeks",
  "critical_path": ["Key milestone 1", "Key milestone 2"],
  "success_metrics": ["Metric 1", "Metric 2"]
}}"""

GENERATE_IMPLEMENTATION_SUMMARY = """You are a project director creating an executive summary of the implementation plan.

Project: {project_name}

Roadmap Overview:
{roadmap_data}

Implementation Tasks:
- Total Tasks: {total_tasks}
- Tasks Synced to Jira: {synced_tasks}
- Tasks Pending: {pending_tasks}

Task Progress (from Jira):
{task_progress}

Create a concise executive summary (2-3 paragraphs) covering:
1. Implementation plan overview (phases, timeline)
2. Current progress status (% complete, tasks done/total)
3. Next immediate steps
4. Any blockers or risks

Keep it actionable and focused on outcomes."""
