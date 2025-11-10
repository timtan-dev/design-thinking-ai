# Quick Start Guide

## ✅ Installation Complete

All dependencies are installed and ready to use!

## 🚀 Start the Application

```bash
streamlit run app.py
```

## 🔑 API Keys Setup

The application uses multiple AI providers. Add your API keys to `.env`:

```bash
# Required - for GPT models and image generation
OPENAI_API_KEY=sk-proj-your-key-here

# Optional - for Claude models
ANTHROPIC_API_KEY=sk-ant-your-key-here

# Optional - for Grok models
XAI_API_KEY=xai-your-key-here
```

**Get API Keys:**
- OpenAI: https://platform.openai.com/api-keys
- Anthropic: https://console.anthropic.com/
- xAI: https://x.ai/api

## 🤖 Available AI Models

Once running, select from the dropdown in the project header:

### OpenAI Models
- **GPT-5** - Latest GPT model
- **GPT-4.1** - Standard GPT-4
- **o1** - Advanced reasoning model
- **o1 Mini** - Faster reasoning model

### Anthropic Models (requires ANTHROPIC_API_KEY)
- **Claude Sonnet 4.5** - Most capable Claude model

### xAI Models (requires XAI_API_KEY)
- **Grok 4** - xAI's latest model

## 🧹 Troubleshooting

If you encounter import errors after code changes:

```bash
./clear_cache.sh
streamlit run app.py
```

Or manually:
```bash
find . -type d -name "__pycache__" -exec rm -rf {} +
find . -name "*.pyc" -delete
streamlit run app.py
```

## 📚 Documentation

- **LangChain Setup**: `docs/LANGCHAIN_SETUP.md`
- **API Documentation**: Full guide for multi-provider setup
- **Cost Comparison**: Model pricing and recommendations

## ✨ Features

- **Project-Level Model Selection** - Choose AI model per project
- **Model Tracking** - Every answer shows which model generated it
- **Multi-Provider Support** - Switch between OpenAI, Claude, Grok
- **Automatic Parameter Handling** - LangChain manages model differences
- **Model Badges** - Visual indication of model used for each response

## 🎯 Next Steps

1. Start the app: `streamlit run app.py`
2. Create a new project
3. Select your preferred AI model
4. Begin your design thinking journey!

## 💡 Pro Tips

- **Cost Optimization**: Use GPT-4.1 for most tasks, o1 for complex reasoning
- **Quality**: Try Claude Sonnet 4.5 for detailed analysis
- **Experimentation**: Switch models mid-project to compare outputs
- **Legacy Content**: Old content shows "Model: Not tracked" badge

Enjoy your enhanced Design Thinking AI experience! 🚀
