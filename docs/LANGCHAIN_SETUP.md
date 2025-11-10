# LangChain Multi-Provider Setup

This document explains how to use multiple AI providers (OpenAI, Anthropic, xAI) with the Design Thinking AI application using LangChain.

## Overview

The application now supports three AI providers through LangChain:

- **OpenAI**: GPT-4, GPT-5, o1, o1-mini models
- **Anthropic**: Claude Sonnet 4.5, Claude Opus 4
- **xAI**: Grok 4, Grok Beta

LangChain automatically handles:
- Model-specific parameter requirements (e.g., o1 models using `max_completion_tokens`)
- Provider-specific API formats
- System message compatibility
- Error handling and retries

## Installation

LangChain dependencies are already installed. If you need to reinstall:

```bash
pip install langchain-openai langchain-anthropic langchain-core
```

## Configuration

### 1. Set Up API Keys

Add your API keys to `.env` file:

```bash
# OpenAI (Required)
OPENAI_API_KEY=sk-proj-your-api-key-here

# Anthropic (Optional - for Claude models)
ANTHROPIC_API_KEY=sk-ant-your-api-key-here

# xAI (Optional - for Grok models)
XAI_API_KEY=xai-your-api-key-here
```

### 2. Get API Keys

**OpenAI:**
1. Visit https://platform.openai.com/api-keys
2. Create new secret key
3. Copy key to `.env`

**Anthropic (Claude):**
1. Visit https://console.anthropic.com/
2. Go to API Keys section
3. Create new API key
4. Copy key to `.env`

**xAI (Grok):**
1. Visit https://x.ai/api
2. Sign up for API access
3. Generate API key
4. Copy key to `.env`

## Available Models

### OpenAI Models
- `gpt-5` - GPT-5 (latest)
- `gpt-4.1` - GPT-4.1
- `o1` - Reasoning model (no temperature, uses max_completion_tokens)
- `o1-mini` - Smaller reasoning model

### Anthropic Models
- `claude-sonnet-4.5-20250514` - Claude Sonnet 4.5 (most capable)
- `claude-sonnet-4-20250514` - Claude Sonnet 4
- `claude-opus-4-20250514` - Claude Opus 4 (largest)

### xAI Models
- `grok-4` - Grok 4 (latest)
- `grok-beta` - Grok Beta (experimental)

## Usage

### In the UI

1. Open a project
2. Click the **AI Model** dropdown in the top-right
3. Select your preferred model
4. All AI-generated content will use this model

### Programmatically

```python
from services.ai_service import AIService

# Initialize with specific model
service = AIService(model="claude-sonnet-4.5-20250514")

# Call the service
response = service._call_openai(
    system_prompt="You are a helpful assistant",
    user_prompt="Explain design thinking"
)
```

## How It Works

### Provider Detection

The `AIService` class automatically detects the provider based on model name prefix:

```python
# OpenAI models
if model.startswith(('gpt', 'o1')):
    llm = ChatOpenAI(model=model, ...)

# Anthropic models
elif model.startswith('claude'):
    llm = ChatAnthropic(model=model, ...)

# xAI models
elif model.startswith('grok'):
    llm = ChatOpenAI(model=model, base_url="https://api.x.ai/v1", ...)
```

### Automatic Parameter Handling

LangChain handles model-specific requirements:

**o1 Models:**
- Automatically converts to `max_completion_tokens`
- Disables `temperature` parameter
- Handles system message limitations

**Claude Models:**
- Uses Anthropic API format
- Handles token limits (200k context)
- Manages system messages correctly

**Grok Models:**
- Uses OpenAI-compatible API
- Routes to xAI endpoint
- Handles xAI-specific features

### Message Flow

```
User Request
    ↓
AIService._call_openai()
    ↓
Create LangChain messages [SystemMessage, HumanMessage]
    ↓
LangChain llm.invoke()
    ↓
Provider-specific API call (OpenAI/Anthropic/xAI)
    ↓
Response returned
    ↓
Saved to database with model_used field
```

## Cost Comparison

| Model | Provider | Input ($/1M tokens) | Output ($/1M tokens) |
|-------|----------|---------------------|----------------------|
| gpt-5 | OpenAI | ~$2.50 | ~$10.00 |
| gpt-4.1 | OpenAI | ~$2.50 | ~$10.00 |
| o1 | OpenAI | ~$15.00 | ~$60.00 |
| claude-sonnet-4.5 | Anthropic | ~$3.00 | ~$15.00 |
| claude-opus-4 | Anthropic | ~$15.00 | ~$75.00 |
| grok-4 | xAI | TBD | TBD |

## Troubleshooting

### "API key not set" Error

**Problem:** `ANTHROPIC_API_KEY not set in environment variables`

**Solution:**
1. Add key to `.env` file
2. Restart the Streamlit app
3. Verify `.env` is in project root

### Provider-Specific Issues

**OpenAI:**
- Verify billing is enabled
- Check rate limits
- Ensure model access (o1 requires specific tier)

**Anthropic:**
- Verify Claude API access
- Check model availability in your region
- Ensure correct model name format

**xAI:**
- Verify Grok API beta access
- Check endpoint availability
- Confirm model naming convention

### Testing Connection

```python
from services.ai_service import AIService

# Test OpenAI
try:
    service = AIService(model="gpt-4.1")
    result = service._call_openai("Test", "Hello")
    print(f"OpenAI: ✅ {result[:50]}...")
except Exception as e:
    print(f"OpenAI: ❌ {e}")

# Test Anthropic
try:
    service = AIService(model="claude-sonnet-4.5-20250514")
    result = service._call_openai("Test", "Hello")
    print(f"Anthropic: ✅ {result[:50]}...")
except Exception as e:
    print(f"Anthropic: ❌ {e}")
```

## Migration from Native SDK

The old implementation manually handled o1 model differences:

```python
# OLD: Manual handling
if is_o1_model:
    messages = [{"role": "user", "content": f"{system}\n\n{user}"}]
    response = client.create(model=model, max_completion_tokens=tokens)
else:
    messages = [{"role": "system", ...}, {"role": "user", ...}]
    response = client.create(model=model, temperature=temp, max_tokens=tokens)
```

**NEW: LangChain automatic handling:**

```python
# NEW: Automatic handling
messages = [SystemMessage(content=system), HumanMessage(content=user)]
response = self.llm.invoke(messages)  # LangChain handles everything!
```

## Benefits

✅ **Automatic Parameter Handling** - No more manual o1 detection
✅ **Multi-Provider Support** - Easy to add Claude, Grok, etc.
✅ **Unified Interface** - Same code works for all providers
✅ **Better Error Handling** - Built-in retries and logging
✅ **Future-Proof** - Easy to add new models/providers

## Next Steps

- Add more Claude models (Haiku, Sonnet 3.5)
- Implement model-specific features (Claude's tools, o1's reasoning)
- Add cost tracking per model
- Implement streaming responses
- Add RAG/vector search capabilities
