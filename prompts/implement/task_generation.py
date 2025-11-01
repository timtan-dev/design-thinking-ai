"""Prompts for generating implementation tasks"""

GENERATE_TASKS_PROMPT = """You are an expert software developer and project planner creating detailed implementation tasks.

Project: {project_name}
Goal: {project_goal}

Roadmap Context:
{roadmap_context}

Test Feedback Priorities:
{test_priorities}

Generate a comprehensive list of granular, actionable development tasks.

For each task, provide:
- **Title**: Brief, clear task name (max 100 chars)
- **Description**: Detailed explanation of what needs to be built
- **Priority**: highest, high, medium, or low (based on MoSCoW + test feedback)
- **Story Points**: 1, 2, 3, 5, 8, or 13 (Fibonacci scale)
  - 1-2: Simple tasks (< 4 hours)
  - 3-5: Medium tasks (4-16 hours)
  - 8-13: Complex tasks (16+ hours)
- **Estimated Hours**: Realistic time estimate
- **Skills Required**: frontend, backend, design, qa, devops (comma-separated)
- **Acceptance Criteria**: 3-5 bullet points defining "done"
- **Dependencies**: Task IDs that must complete first (empty array if none)
- **MoSCoW Category**: must, should, could, or wont
- **Rationale**: ONE sentence explaining story point estimate (be concise!)

**IMPORTANT**:
- Break down large features into small, manageable tasks
- Each task should be completable in 1-3 days
- Tasks with 13 points should be rare (only for very complex features)
- Consider technical dependencies (auth before dashboard, DB before API)
- Prioritize critical issues from test feedback as "must" + "highest"

Output in **valid JSON format only** (no markdown, no code blocks):
{{
  "tasks": [
    {{
      "title": "Setup authentication system",
      "description": "Implement JWT-based authentication with user registration, login, and password reset flows",
      "priority": "highest",
      "story_points": 8,
      "estimated_hours": 16,
      "skills_required": "backend",
      "acceptance_criteria": [
        "User can register with email and password",
        "User can login and receive JWT token",
        "Password reset flow works via email"
      ],
      "dependencies": [],
      "moscow_category": "must",
      "rationale": "Complex feature requiring security best practices and email integration"
    }}
  ]
}}"""
