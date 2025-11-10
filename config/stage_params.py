"""
Stage-specific AI parameters configuration
Different stages require different creativity/consistency levels

Parameter support by model:
- GPT-5: Only max_tokens (no temperature/top_p)
- Claude: Only temperature and max_tokens (no top_p)
- GPT-4.1: temperature, top_p, and max_tokens
- Grok-4: temperature, top_p, and max_tokens

The ai_service.py automatically filters parameters based on the model.
"""

# Define Stage Parameters
# Focus: Analytical, structured, evidence-based insights
DEFINE_STAGE_PARAMS = {
    "temperature": 0.3,      # Low - more focused and consistent analysis
    "top_p": 0.85,           # Moderate - balanced creativity in expression
    "max_tokens": None       # Use default (16000)
}

# Ideate Stage Parameters
# Focus: Creative, diverse, unconventional ideas
IDEATE_STAGE_PARAMS = {
    "temperature": 0.9,      # High - maximum creativity and diversity
    "top_p": 0.95,           # High - explore diverse possibilities
    "max_tokens": None       # Use default (16000)
}

# Empathise Stage Parameters
# Focus: Template generation and research data analysis
EMPATHISE_STAGE_PARAMS = {
    "temperature": 0.4,      # Low-moderate - structured templates
    "top_p": 0.85,           # Moderate - some flexibility in wording
    "max_tokens": None       # Use default (16000)
}

# Prototype Stage Parameters
# Focus: Design suggestions and code generation
PROTOTYPE_STAGE_PARAMS = {
    "temperature": 0.5,      # Moderate - balance creativity and correctness
    "top_p": 0.9,            # Moderate-high - explore design options
    "max_tokens": None       # Use default (16000)
}

# Test Stage Parameters
# Focus: Feedback analysis and insight generation
TEST_STAGE_PARAMS = {
    "temperature": 0.4,      # Low-moderate - analytical insights
    "top_p": 0.85,           # Moderate - balanced analysis
    "max_tokens": None       # Use default (16000)
}

# Implement Stage Parameters
# Focus: Roadmap and task generation
IMPLEMENT_STAGE_PARAMS = {
    "temperature": 0.3,      # Low - structured, consistent planning
    "top_p": 0.85,           # Moderate - balanced approach
    "max_tokens": None       # Use default (16000)
}


def get_stage_params(stage: str) -> dict:
    """
    Get AI parameters for a specific stage

    Args:
        stage: Stage name (define, ideate, empathise, prototype, test, implement)

    Returns:
        Dictionary with temperature, top_p, and max_tokens
    """
    params_map = {
        "define": DEFINE_STAGE_PARAMS,
        "ideate": IDEATE_STAGE_PARAMS,
        "empathise": EMPATHISE_STAGE_PARAMS,
        "prototype": PROTOTYPE_STAGE_PARAMS,
        "test": TEST_STAGE_PARAMS,
        "implement": IMPLEMENT_STAGE_PARAMS,
    }

    return params_map.get(stage.lower(), DEFINE_STAGE_PARAMS)
