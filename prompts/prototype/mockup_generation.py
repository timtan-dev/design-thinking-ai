"""Prompts for AI mockup generation using DALL-E or similar"""

GENERATE_MOCKUP_PROMPT = """
Create a {style} mobile app mockup for {page_name} page.

**Project:** {project_name}
**Purpose:** {project_goal}

**Based on this sketch:**
[User's finalized sketch shows: {sketch_description}]

**Key Features to Include:**
{key_features}

**Style Requirements:**
- Design Style: {style}
- Color Scheme: {color_scheme}
- Must include: {must_include_elements}

**Additional Instructions:**
{user_refinement}

Create a clean, professional mobile app mockup that matches the sketch layout but with polished UI design.
Focus on modern UX patterns, clear hierarchy, and visual appeal.
Make it look like a real app interface with proper spacing, typography, and visual elements.
"""

REFINE_MOCKUP_PROMPT = """
Create an improved version of the previous mockup with these changes:

**Previous Mockup Description:**
{previous_mockup_description}

**Requested Changes:**
{user_refinement}

**Maintain:**
- Overall layout structure
- Core UI elements
- Color scheme: {color_scheme}
- Style: {style}

**Improve:**
{specific_improvements}

Generate a refined mockup that addresses the requested changes while maintaining consistency.
"""
