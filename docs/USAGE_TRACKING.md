# Usage Tracking Implementation

## Overview

This document describes the implementation of cost and duration tracking for AI-generated content in the Design Thinking AI application.

## Features

- **Duration Tracking**: Records how long each AI generation takes
- **Token Tracking**: Records input and output token counts
- **Cost Calculation**: Automatically calculates cost based on model pricing and token usage
- **Visual Display**: Shows cost and duration badges in the UI

## Implementation Details

### 1. Model Pricing Configuration

**File**: `config/model_pricing.py`

Contains pricing information for all supported AI models:
- OpenAI: GPT-5, GPT-4.1, o1, o1-mini
- Anthropic: Claude Sonnet 4.5, Claude 3 Opus, Claude 3 Sonnet, Claude 3 Haiku
- xAI: Grok 4, Grok Beta

Pricing is stored as cost per 1M tokens (input and output separately).

**Functions**:
- `calculate_cost(model, input_tokens, output_tokens)`: Calculates total cost in USD
- `format_cost(cost_usd)`: Formats cost for display ($0.0075, $0.12, etc.)
- `format_duration(seconds)`: Formats duration for display (5.3s, 2m 15s, etc.)

### 2. AIService Updates

**File**: `services/ai_service.py`

Updated `_call_openai()` method to return a tuple:
```python
(response_content, usage_metadata)
```

**Usage metadata includes**:
- `duration_seconds`: Time taken for API call (float)
- `input_tokens`: Number of input/prompt tokens (int)
- `output_tokens`: Number of output/completion tokens (int)
- `cost_usd`: Calculated cost in USD (float)
- `model`: Model name used (string)

The method automatically:
- Times the API call
- Extracts token usage from LangChain response metadata
- Handles both OpenAI format (token_usage) and Anthropic format (usage)
- Calculates cost using the pricing configuration
- Returns error metadata (all zeros) on failure

### 3. Database Schema Updates

**Files**:
- `database/models.py`
- `migrations/add_usage_tracking.py`

Added columns to `generated_content` and `brainstorm_ideas` tables:
- `duration_seconds` (REAL/Float)
- `input_tokens` (INTEGER)
- `output_tokens` (INTEGER)
- `cost_usd` (REAL/Float)

### 4. Updated Call Sites

**Files updated**:
- `pages/define.py`: Saves usage metrics when generating Define analyses
- `pages/ideate.py`: Saves usage metrics for seed ideas and expansions
- `pages/empathise.py`: Unpacks tuple (template generation doesn't save)
- `pages/test.py`: Unpacks tuple (2 calls)
- `pages/implement.py`: Unpacks tuple (2 calls)
- `pages/prototype_steps/step1_sketch.py`: Unpacks tuple (1 call)
- `pages/prototype_steps/step3_code.py`: Unpacks tuple (1 call)

**Example - Saving with metrics**:
```python
generated_content, usage_metadata = ai_service._call_openai(system_prompt, user_prompt)

new_content = GeneratedContent(
    project_id=project_id,
    content_type=content_type,
    content=generated_content,
    model_used=project.preferred_model,
    duration_seconds=usage_metadata.get('duration_seconds'),
    input_tokens=usage_metadata.get('input_tokens'),
    output_tokens=usage_metadata.get('output_tokens'),
    cost_usd=usage_metadata.get('cost_usd')
)
db.add(new_content)
db.commit()
```

### 5. Display Utilities

**File**: `utils/usage_badge.py`

Provides functions to display usage metrics in the UI:

**Functions**:
- `inject_usage_badge_css()`: Injects CSS styles (call once per page)
- `display_usage_badge()`: Shows compact badge with duration, cost, and token count
- `display_usage_details()`: Shows detailed metrics in an expander
- `display_compact_usage()`: Returns HTML for inline display (tables, lists)

**Example usage**:
```python
from utils.usage_badge import display_usage_badge, inject_usage_badge_css

# At page start
inject_usage_badge_css()

# Display metrics
display_usage_badge(
    duration_seconds=content.duration_seconds,
    cost_usd=content.cost_usd,
    input_tokens=content.input_tokens,
    output_tokens=content.output_tokens
)
```

### 6. UI Integration

**Updated pages**:
- **Define page**: Shows usage badge next to model badge for each analysis
- **Ideate page**: Shows usage badge in brainstorming seed ideas dialog

**Visual appearance**:
- Purple gradient badge: `⏱️ 5.3s · 💰 $0.0075 · 🔢 1.5k`
- Displays duration, cost, and total token count
- Positioned next to the model badge

## Cost Examples

Based on pricing as of January 2025:

### GPT-4o
- Input: $2.50 per 1M tokens
- Output: $10.00 per 1M tokens
- Example: 1,000 input + 500 output = $0.0075

### Claude Sonnet 4.5
- Input: $3.00 per 1M tokens
- Output: $15.00 per 1M tokens
- Example: 2,000 input + 1,500 output = $0.0285

### o1
- Input: $15.00 per 1M tokens
- Output: $60.00 per 1M tokens
- Example: 1,000 input + 500 output = $0.045

## Testing

Run the migration:
```bash
python migrations/add_usage_tracking.py
```

Test pricing calculations:
```bash
python -c "
from config.model_pricing import calculate_cost, format_cost, format_duration

cost = calculate_cost('gpt-4o', 1000, 500)
print(f'Cost: {format_cost(cost)}')

print(f'Duration: {format_duration(125)}')
"
```

## Future Enhancements

Possible improvements:
1. **Project-level cost tracking**: Sum total costs per project
2. **Cost analytics dashboard**: Visualize spending over time
3. **Budget alerts**: Warn when approaching budget limits
4. **Cost comparison**: Compare costs across different models
5. **Export cost reports**: Generate CSV/PDF reports for billing
6. **User-level tracking**: Track costs per user (multi-user support)

## Notes

- Costs are calculated locally based on token counts, not from API responses
- Migration adds columns to existing tables (SQLite doesn't support DROP COLUMN)
- Usage metadata is optional (nullable columns) to support legacy data
- All monetary values are in USD
- Token counts include both system prompts and user prompts
