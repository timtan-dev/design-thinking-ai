"""
AI Service - OpenAI API Integration
Wrapper for all AI-powered generation tasks
"""

from openai import OpenAI
from config.settings import Settings
from typing import Dict, Any
import json

class AIService:
    """AI service for generating content using OpenAI API"""

    def __init__(self):
        """Initialize OpenAI client"""
        self.client = OpenAI(api_key=Settings.OPENAI_API_KEY)
        self.model = Settings.OPENAI_MODEL
        self.temperature = Settings.OPENAI_TEMPERATURE
        self.max_tokens = Settings.OPENAI_MAX_TOKENS

    def _call_openai(self, system_prompt: str, user_prompt: str) -> str:
        """
        Make a call to OpenAI API

        Args:
            system_prompt: System instruction
            user_prompt: User message

        Returns:
            Generated text response
        """
        try:
            response = self.client.chat.completions.create(
                model=self.model,
                messages=[
                    {"role": "system", "content": system_prompt},
                    {"role": "user", "content": user_prompt}
                ],
                temperature=self.temperature,
                max_tokens=self.max_tokens
            )
            return response.choices[0].message.content
        except Exception as e:
            return f"Error generating content: {str(e)}"

    def _format_research_data(self, research_data_list: list) -> str:
        """
        Format research data for inclusion in prompts

        Args:
            research_data_list: List of research data dictionaries

        Returns:
            Formatted research data string
        """
        if not research_data_list:
            return "\n\n**NOTE:** No research data has been uploaded yet. Generate a sample analysis based on the project context as a starting template.\n\n"

        research_section = "\n\n**UPLOADED RESEARCH DATA:**\n\n"
        for idx, data in enumerate(research_data_list, 1):
            method_name = data.get('method_type', 'Unknown').replace('_', ' ').title()
            content = data.get('file_content', '')
            research_section += f"--- Research Method {idx}: {method_name} ---\n{content}\n\n"

        return research_section

    # EMPATHISE STAGE - Data Collection

    def generate_interview_questions(self, project: Dict[str, Any]) -> str:
        """Generate interview questions based on project context"""
        from prompts.empathise.interview import INTERVIEW_PROMPT

        user_prompt = f"""
        Project: {project['name']}
        Area: {project['area']}
        Goal: {project['goal']}

        Generate 10-15 interview questions to understand user needs, pain points, and behaviors.
        """

        return self._call_openai(INTERVIEW_PROMPT, user_prompt)

    def generate_survey_questions(self, project: Dict[str, Any]) -> str:
        """Generate survey questions"""
        from prompts.empathise.survey import SURVEY_PROMPT

        user_prompt = f"""
        Project: {project['name']}
        Area: {project['area']}
        Goal: {project['goal']}

        Generate a comprehensive survey with 15-20 questions including multiple choice,
        rating scales, and open-ended questions.
        """

        return self._call_openai(SURVEY_PROMPT, user_prompt)

    def generate_ethnography_guide(self, project: Dict[str, Any]) -> str:
        """Generate ethnography observation guide"""
        system_prompt = "You are an expert in ethnographic research methods for design thinking."

        user_prompt = f"""
        Create an ethnography observation guide for:
        Project: {project['name']}
        Area: {project['area']}
        Goal: {project['goal']}

        Include: observation focus areas, what to look for, documentation methods, and key questions.
        """

        return self._call_openai(system_prompt, user_prompt)

    def generate_focus_group_guide(self, project: Dict[str, Any]) -> str:
        """Generate focus group discussion guide"""
        system_prompt = "You are an expert moderator for focus group discussions."

        user_prompt = f"""
        Create a focus group discussion guide for:
        Project: {project['name']}
        Area: {project['area']}
        Goal: {project['goal']}

        Include: introduction, warm-up questions, main discussion topics, and closing.
        """

        return self._call_openai(system_prompt, user_prompt)

    def generate_observation_checklist(self, project: Dict[str, Any]) -> str:
        """Generate observation checklist"""
        system_prompt = "You are an expert in observational research methods."

        user_prompt = f"""
        Create an observation checklist for:
        Project: {project['name']}
        Area: {project['area']}
        Goal: {project['goal']}

        Include: behaviors to observe, context factors, user interactions, and pain points to note.
        """

        return self._call_openai(system_prompt, user_prompt)

    def generate_diary_study_template(self, project: Dict[str, Any]) -> str:
        """Generate diary study template"""
        system_prompt = "You are an expert in longitudinal user research methods."

        user_prompt = f"""
        Create a diary study template for:
        Project: {project['name']}
        Area: {project['area']}
        Goal: {project['goal']}

        Include: daily prompts, reflection questions, activity tracking, and sentiment capture.
        """

        return self._call_openai(system_prompt, user_prompt)

    # EMPATHISE STAGE - Data Analysis

    def create_empathy_map(self, project: Dict[str, Any], research_data_list: list = None) -> str:
        """Create empathy map from research data"""
        from prompts.empathise.empathy_map import EMPATHY_MAP_PROMPT

        research_section = self._format_research_data(research_data_list)

        user_prompt = f"""
        **Project Context:**
        Project Name: {project['name']}
        Project Area: {project['area']}
        Project Goal: {project['goal']}
        {research_section}
        **Your Task:**
        Analyze the uploaded research data above and create a comprehensive empathy map with sections:
        - SAYS: What the user verbalizes (extract direct quotes from the research data)
        - THINKS: What the user thinks (infer from their responses)
        - DOES: What the user does (identify behaviors from observations/self-reports)
        - FEELS: What the user feels (identify emotional states from the data)

        Base your empathy map entirely on the research data provided. Include specific references to which research method the insights come from (e.g., "Interview 1", "Survey Response", "Observation Notes").
        """

        return self._call_openai(EMPATHY_MAP_PROMPT, user_prompt)

    def create_persona(self, project: Dict[str, Any], research_data_list: list = None) -> str:
        """Create user persona"""
        from prompts.empathise.persona import PERSONA_PROMPT

        research_section = self._format_research_data(research_data_list)

        user_prompt = f"""
        **Project Context:**
        Project: {project['name']}
        Area: {project['area']}
        Goal: {project['goal']}
        {research_section}
        **Your Task:**
        Based on the uploaded research data, create a detailed user persona including:
        - Name, demographics, and background
        - Goals and motivations
        - Frustrations and pain points
        - Behaviors and habits
        - Needs and desires

        Base the persona on real insights from the research data provided.
        """

        return self._call_openai(PERSONA_PROMPT, user_prompt)

    def create_journey_map(self, project: Dict[str, Any], research_data_list: list = None) -> str:
        """Create user journey map"""
        system_prompt = "You are an expert in creating user journey maps for design thinking. Base your analysis on real user research data."

        research_section = self._format_research_data(research_data_list)

        user_prompt = f"""
        **Project Context:**
        Project: {project['name']}
        Area: {project['area']}
        Goal: {project['goal']}
        {research_section}
        **Your Task:**
        Based on the research data, create a user journey map with stages: Awareness, Consideration, Decision, Experience, Post-Experience

        For each stage include: actions, thoughts, emotions, pain points, opportunities.
        Ground your insights in the uploaded research data.
        """

        return self._call_openai(system_prompt, user_prompt)

    def create_affinity_map(self, project: Dict[str, Any], research_data_list: list = None) -> str:
        """Create affinity map from insights"""
        system_prompt = "You are an expert in synthesizing research insights using affinity mapping."

        research_section = self._format_research_data(research_data_list)

        user_prompt = f"""
        **Project Context:**
        Project: {project['name']}
        Area: {project['area']}
        Goal: {project['goal']}
        {research_section}
        **Your Task:**
        Analyze the research data above and create an affinity map by:
        1. Identifying key insights and observations from the data
        2. Grouping related insights into themes
        3. Naming each theme clearly
        4. Providing key findings for each theme

        Base everything on the actual research data provided.
        """

        return self._call_openai(system_prompt, user_prompt)

    def create_user_story(self, project: Dict[str, Any], research_data_list: list = None) -> str:
        """Create user story narrative"""
        system_prompt = "You are an expert storyteller for user-centered design who creates narratives based on real user research."

        research_section = self._format_research_data(research_data_list)

        user_prompt = f"""
        **Project Context:**
        Project: {project['name']}
        Area: {project['area']}
        Goal: {project['goal']}
        {research_section}
        **Your Task:**
        Based on the research data, create a compelling user story narrative that:
        - Brings the user's experience to life
        - Incorporates actual quotes and observations from the research
        - Highlights key pain points and desires
        - Makes the user's journey emotionally resonant

        Ground your story in the real data provided.
        """

        return self._call_openai(system_prompt, user_prompt)

    def create_stakeholder_map(self, project: Dict[str, Any], research_data_list: list = None) -> str:
        """Create stakeholder map"""
        system_prompt = "You are an expert in stakeholder analysis for design thinking projects."

        research_section = self._format_research_data(research_data_list)

        user_prompt = f"""
        **Project Context:**
        Project: {project['name']}
        Area: {project['area']}
        Goal: {project['goal']}
        {research_section}
        **Your Task:**
        Based on the project context and research data, create a stakeholder map that identifies:
        - All relevant stakeholders (users, decision-makers, influencers, etc.)
        - Their interests and needs
        - Their influence level (high/medium/low)
        - Relationships between stakeholders
        - Potential concerns or blockers

        Use insights from the research data where applicable.
        """

        return self._call_openai(system_prompt, user_prompt)

    # DEFINE STAGE

    def generate_problem_statement(self, project: Dict[str, Any]) -> str:
        """Generate problem statement"""
        system_prompt = "You are an expert in defining user-centered problem statements."

        user_prompt = f"""
        Create a clear problem statement for:
        Project: {project['name']}
        Area: {project['area']}
        Goal: {project['goal']}

        Use the format: [User] needs [need] because [insight].
        """

        return self._call_openai(system_prompt, user_prompt)

    def generate_hmw_questions(self, project: Dict[str, Any], problem_statement: str = "") -> str:
        """Generate How Might We questions"""
        system_prompt = "You are an expert in reframing problems as opportunities using HMW questions."

        user_prompt = f"""
        Generate 5-8 "How Might We" questions for:
        Project: {project['name']}
        Problem: {problem_statement if problem_statement else project['goal']}

        Make them actionable, broad enough to allow creativity, but narrow enough to be manageable.
        """

        return self._call_openai(system_prompt, user_prompt)

    # IDEATE STAGE

    def generate_ideas(self, project: Dict[str, Any]) -> str:
        """Generate solution ideas"""
        system_prompt = "You are a creative ideation expert for design thinking."

        user_prompt = f"""
        Generate 15-20 creative solution ideas for:
        Project: {project['name']}
        Area: {project['area']}
        Goal: {project['goal']}

        Include both incremental improvements and breakthrough innovations.
        """

        return self._call_openai(system_prompt, user_prompt)

    # PROTOTYPE STAGE

    def generate_user_flow(self, project: Dict[str, Any], prototype_desc: str = "") -> str:
        """Generate user flow for prototype"""
        system_prompt = "You are an expert in designing user flows and interactions."

        user_prompt = f"""
        Create a detailed user flow for:
        Project: {project['name']}
        Prototype: {prototype_desc if prototype_desc else 'the solution'}

        Show step-by-step user journey through the prototype.
        """

        return self._call_openai(system_prompt, user_prompt)

    # TEST STAGE

    def generate_test_scenarios(self, project: Dict[str, Any]) -> str:
        """Generate test scenarios"""
        system_prompt = "You are an expert in usability testing and creating test scenarios."

        user_prompt = f"""
        Create 5-8 test scenarios for:
        Project: {project['name']}
        Goal: {project['goal']}

        Each scenario should be realistic and test key functionality.
        """

        return self._call_openai(system_prompt, user_prompt)

    def analyze_test_feedback(self, project: Dict[str, Any], feedback: str) -> str:
        """Analyze test feedback"""
        system_prompt = "You are an expert in analyzing user testing feedback and extracting insights."

        user_prompt = f"""
        Analyze this test feedback for:
        Project: {project['name']}

        Feedback:
        {feedback}

        Provide: key insights, patterns, recommendations for improvement.
        """

        return self._call_openai(system_prompt, user_prompt)

    # IMPLEMENT STAGE

    def generate_implementation_roadmap(self, project: Dict[str, Any]) -> str:
        """Generate implementation roadmap"""
        system_prompt = "You are an expert in creating implementation roadmaps and launch plans."

        user_prompt = f"""
        Create a detailed implementation roadmap for:
        Project: {project['name']}
        Area: {project['area']}
        Goal: {project['goal']}

        Include phases, timelines, milestones, and key activities.
        """

        return self._call_openai(system_prompt, user_prompt)
