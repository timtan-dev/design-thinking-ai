# Deployment Guide

## 🚀 Streamlit Cloud Deployment

### Prerequisites

✅ GitHub repository with your code
✅ Streamlit Cloud account (free at https://streamlit.io/cloud)
✅ API keys for AI providers

### Step 1: Push to GitHub

```bash
git add .
git commit -m "Ready for deployment"
git push origin main
```

### Step 2: Deploy on Streamlit Cloud

1. Go to https://share.streamlit.io/
2. Click **"New app"**
3. Select your GitHub repository
4. Set main file: `app.py`
5. Click **"Deploy"**

### Step 3: Configure Secrets

In Streamlit Cloud dashboard, go to **Settings → Secrets** and add:

```toml
# Required - OpenAI API Key
OPENAI_API_KEY = "sk-proj-your-key-here"

# Optional - Anthropic API Key (for Claude models)
ANTHROPIC_API_KEY = "sk-ant-your-key-here"

# Optional - xAI API Key (for Grok models)
XAI_API_KEY = "xai-your-key-here"

# Database (uses SQLite by default)
DATABASE_URL = "sqlite:///./design_thinking.db"

# Application
SECRET_KEY = "your-secure-secret-key-here"
DEBUG = "False"

# Optional - Jira Integration
JIRA_OAUTH_CLIENT_ID = "your-oauth-client-id"
JIRA_OAUTH_CLIENT_SECRET = "your-oauth-client-secret"
JIRA_OAUTH_REDIRECT_URI = "https://your-app.streamlit.app/oauth_callback"
ENCRYPTION_KEY = "your-encryption-key-here"
```

### Step 4: Verify Dependencies

✅ `requirements.txt` includes:
```
langchain-openai>=1.0.0
langchain-anthropic>=1.0.0
langchain-core>=1.0.0
```

These are automatically installed by Streamlit Cloud!

---

## 📦 How Streamlit Cloud Works

### Dependency Installation

**Yes!** Streamlit Cloud automatically installs packages from `requirements.txt` during deployment:

1. **Build Phase**:
   - Reads `requirements.txt`
   - Creates virtual environment
   - Installs all packages via `pip install -r requirements.txt`

2. **Runtime**:
   - Your app runs with all dependencies available
   - No manual installation needed

### Environment Variables

Streamlit Cloud uses **Secrets Management** instead of `.env` files:
- Add secrets in the Streamlit Cloud dashboard
- Access via `st.secrets` or environment variables
- Our code handles both (see `config/settings.py`)

---

## 🔑 API Keys Setup

### OpenAI (Required)

1. Get key: https://platform.openai.com/api-keys
2. Add to Streamlit Secrets:
   ```toml
   OPENAI_API_KEY = "sk-proj-..."
   ```

### Anthropic (Optional - for Claude)

1. Get key: https://console.anthropic.com/
2. Add to Streamlit Secrets:
   ```toml
   ANTHROPIC_API_KEY = "sk-ant-..."
   ```

### xAI (Optional - for Grok)

1. Get key: https://x.ai/api
2. Add to Streamlit Secrets:
   ```toml
   XAI_API_KEY = "xai-..."
   ```

---

## ✅ Deployment Checklist

Before deploying:

- [ ] `requirements.txt` includes LangChain packages
- [ ] Code pushed to GitHub
- [ ] API keys ready
- [ ] Database migrations run locally (creates schema)
- [ ] Custom CSS in `assets/styles/main.css`
- [ ] No `.env` file in repository (use .gitignore)

After deploying:

- [ ] App loads successfully
- [ ] Can create new project
- [ ] Model dropdown shows all options
- [ ] Can select different models
- [ ] AI generation works
- [ ] Model badges display correctly

---

## 🐛 Troubleshooting

### "Module not found" Error

**Problem**: `ModuleNotFoundError: No module named 'langchain_openai'`

**Solution**:
1. Check `requirements.txt` includes LangChain packages
2. Redeploy (Streamlit Cloud will reinstall)
3. Check build logs for installation errors

### "API key not set" Error

**Problem**: `ValueError: OPENAI_API_KEY not set`

**Solution**:
1. Go to Streamlit Cloud dashboard → Settings → Secrets
2. Add the missing API key
3. App will automatically restart

### App Won't Start

**Problem**: App shows error during startup

**Solutions**:
1. Check **Logs** in Streamlit Cloud dashboard
2. Verify `app.py` is the main file
3. Check for syntax errors in Python files
4. Verify all imports are correct

### Database Issues

**Problem**: Database errors or missing tables

**Solution**:
1. Database auto-creates on first run
2. Or include pre-configured `design_thinking.db` in repo
3. Run migrations locally first, then commit database

---

## 📊 Monitoring

### View Logs

1. Streamlit Cloud dashboard
2. Click on your app
3. View **Logs** tab
4. Monitor errors and performance

### Usage Analytics

Available in Streamlit Cloud dashboard:
- Active users
- App usage statistics
- Error rates
- Performance metrics

---

## 🔄 Updates

### Deploy New Changes

```bash
git add .
git commit -m "Update: description of changes"
git push origin main
```

Streamlit Cloud **automatically redeploys** on every push to main branch!

### Rollback

If deployment fails:
1. Streamlit Cloud keeps previous version running
2. Fix the issue
3. Push again
4. Or revert commit and push

---

## 💰 Cost Considerations

### Streamlit Cloud

- **Free tier**: 1 private app, unlimited public apps
- **Team tier**: $20/month for more apps

### AI Provider Costs

**OpenAI:**
- GPT-4.1: ~$2.50 / 1M input tokens, ~$10 / 1M output
- o1: ~$15 / 1M input tokens, ~$60 / 1M output

**Anthropic:**
- Claude Sonnet 4.5: ~$3 / 1M input, ~$15 / 1M output

**xAI:**
- Grok 4: Pricing TBD (check https://x.ai/api)

**Tip**: Set usage limits in each provider's dashboard!

---

## 🔒 Security Best Practices

### Never Commit Secrets

✅ **DO:**
- Use Streamlit Secrets
- Use `.gitignore` for `.env`
- Rotate API keys regularly

❌ **DON'T:**
- Commit `.env` file
- Hardcode API keys
- Share secrets in code

### Database Security

For production:
- Consider PostgreSQL instead of SQLite
- Regular backups
- Encrypt sensitive data

---

## 📚 Additional Resources

- **Streamlit Docs**: https://docs.streamlit.io/
- **Streamlit Cloud**: https://docs.streamlit.io/streamlit-community-cloud
- **LangChain Docs**: https://python.langchain.com/
- **OpenAI API**: https://platform.openai.com/docs
- **Anthropic API**: https://docs.anthropic.com/

---

## ✨ Success!

Your app is now live! Users can:
- Create design thinking projects
- Choose from multiple AI models
- Generate content with GPT, Claude, or Grok
- See which model created each response
- Track all work in a database

Share your app URL: `https://your-app.streamlit.app`
