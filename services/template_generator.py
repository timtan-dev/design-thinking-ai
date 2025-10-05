"""
Template Generator Service
Generate downloadable templates for research methods
"""

from typing import Dict
import json

def generate_interview_template() -> str:
    """Generate interview template"""
    return """
# Interview Guide Template

## Introduction
- Introduce yourself and the project
- Explain the purpose of the interview
- Confirm consent and recording permission
- Estimated duration: 30-45 minutes

## Warm-up Questions (5 minutes)
1. Tell me a bit about yourself and your background
2. How do you currently [relevant activity]?

## Main Questions (25-30 minutes)

### Understanding Current Experience
3. Walk me through a typical day/scenario when you [use product/service]
4. What challenges or frustrations do you face?
5. What works well for you?

### Needs and Motivations
6. What are you trying to achieve when you [activity]?
7. Why is this important to you?
8. What would make this easier/better?

### Context and Behavior
9. How often do you [activity]?
10. What tools or methods do you currently use?
11. Who else is involved in this process?

### Future and Desires
12. If you could change one thing, what would it be?
13. What's missing from current solutions?

## Closing (5 minutes)
14. Is there anything else you'd like to share?
15. Any questions for me?

## Notes Section
- Key insights:
- Pain points:
- Opportunities:
- Follow-up needed:
"""

def generate_survey_template() -> str:
    """Generate survey template"""
    return """
# Survey Template

## Section 1: Screening
1. [Demographic question 1]
2. [Demographic question 2]
3. [Usage frequency question]

## Section 2: Current Experience
4. How satisfied are you with [product/service]? (1-5 scale)
5. What do you use [product/service] for? (Multiple choice)
6. How often do you [activity]? (Frequency scale)

## Section 3: Needs and Preferences
7. What features are most important to you? (Ranking)
8. What improvements would you like to see? (Open-ended)
9. What frustrates you most? (Multiple choice)

## Section 4: Behavior and Context
10. When do you typically [activity]? (Time/situation)
11. What devices do you use? (Multiple choice)
12. Who else is involved? (Selection)

## Section 5: Future Interest
13. Would you be interested in [new feature]? (Yes/No/Maybe)
14. What would make you switch to a new solution? (Open-ended)

## Section 6: Additional Feedback
15. Any other comments or suggestions? (Open-ended)

Thank you for your participation!
"""

def generate_empathy_map_template() -> Dict:
    """Generate empathy map template structure"""
    return {
        "says": [
            "Direct quotes from users",
            "What they verbalize"
        ],
        "thinks": [
            "What occupies their thoughts",
            "Concerns and aspirations"
        ],
        "does": [
            "Actions and behaviors",
            "What they actually do"
        ],
        "feels": [
            "Emotional state",
            "Worries and desires"
        ]
    }

def generate_persona_template() -> Dict:
    """Generate persona template structure"""
    return {
        "name": "Persona Name",
        "demographics": {
            "age": "",
            "occupation": "",
            "location": ""
        },
        "background": "Brief background story",
        "goals": [
            "Primary goal 1",
            "Primary goal 2"
        ],
        "frustrations": [
            "Main frustration 1",
            "Main frustration 2"
        ],
        "behaviors": [
            "Key behavior 1",
            "Key behavior 2"
        ],
        "motivations": [
            "What drives them",
            "What they value"
        ],
        "quote": "A characteristic quote from this persona"
    }

def generate_journey_map_template() -> Dict:
    """Generate journey map template structure"""
    return {
        "stages": [
            {
                "name": "Awareness",
                "actions": ["Action 1", "Action 2"],
                "thoughts": ["Thought 1", "Thought 2"],
                "emotions": "Emotional state",
                "pain_points": ["Pain point 1"],
                "opportunities": ["Opportunity 1"]
            },
            {
                "name": "Consideration",
                "actions": [],
                "thoughts": [],
                "emotions": "",
                "pain_points": [],
                "opportunities": []
            },
            {
                "name": "Decision",
                "actions": [],
                "thoughts": [],
                "emotions": "",
                "pain_points": [],
                "opportunities": []
            },
            {
                "name": "Experience",
                "actions": [],
                "thoughts": [],
                "emotions": "",
                "pain_points": [],
                "opportunities": []
            },
            {
                "name": "Post-Experience",
                "actions": [],
                "thoughts": [],
                "emotions": "",
                "pain_points": [],
                "opportunities": []
            }
        ]
    }
