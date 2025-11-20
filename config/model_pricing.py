"""
Model pricing configuration for cost calculation.

Prices are per 1M tokens (USD).
Updated as of January 2025.
"""

MODEL_PRICING = {
    # OpenAI GPT Models
    "gpt-5.1": {
        "input": 1.25,   # per 1M input tokens
        "output": 10.00  # per 1M output tokens
    },
    "gpt-5": {
        "input": 1.25,   # per 1M input tokens
        "output": 10.00  # per 1M output tokens
    },
    "gpt-4.1": {
        "input": 3.00,
        "output": 12.00
    },

    # Anthropic Claude Models
    "claude-sonnet-4-5-20250929": {
        "input": 3.00,
        "output": 15.00
    },

    # xAI Grok Models
    "grok-4": {
        "input": 3.00,   # Estimated pricing
        "output": 15.00
    },
}


def calculate_cost(model: str, input_tokens: int, output_tokens: int) -> float:
    """
    Calculate the cost of an API call based on token usage.

    Args:
        model: Model identifier (e.g., "gpt-4o", "claude-sonnet-4-5-20250929")
        input_tokens: Number of input/prompt tokens
        output_tokens: Number of output/completion tokens

    Returns:
        Cost in USD (float)

    Example:
        >>> calculate_cost("gpt-4o", 1000, 500)
        0.0075  # $0.0075
    """
    if model not in MODEL_PRICING:
        # Return 0 for unknown models rather than raising error
        return 0.0

    pricing = MODEL_PRICING[model]

    # Calculate cost: (tokens / 1_000_000) * price_per_1M_tokens
    input_cost = (input_tokens / 1_000_000) * pricing["input"]
    output_cost = (output_tokens / 1_000_000) * pricing["output"]

    return input_cost + output_cost


def format_cost(cost_usd: float) -> str:
    """
    Format cost for display.

    Args:
        cost_usd: Cost in USD

    Returns:
        Formatted string (e.g., "$0.0075", "$0.12", "$1.50")
    """
    if cost_usd < 0.01:
        return f"${cost_usd:.4f}"
    elif cost_usd < 1.00:
        return f"${cost_usd:.3f}"
    else:
        return f"${cost_usd:.2f}"


def format_duration(seconds: float) -> str:
    """
    Format duration for display.

    Args:
        seconds: Duration in seconds

    Returns:
        Formatted string (e.g., "1.2s", "45.3s", "2m 15s")
    """
    if seconds < 60:
        return f"{seconds:.1f}s"
    else:
        minutes = int(seconds // 60)
        remaining_seconds = int(seconds % 60)
        return f"{minutes}m {remaining_seconds}s"
