# Masters Project Expo Setup Guide

## Overview

This guide explains how to set up the Design Thinking AI application for your masters project expo/demonstration to teachers and students.

## Demo Architecture: Single-User Mode

For educational purposes, the application runs in **single-user demo mode**:
- ✅ **No login required** - immediate access for all attendees
- ✅ **Shared projects** - everyone can see and learn from all projects
- ✅ **Quick onboarding** - students can start creating projects immediately
- ✅ **Collaborative learning** - view examples created by others

**Note:** In production deployment, this would be a multi-user system with authentication and project isolation.

## Jira Integration for Demo

### Current Behavior:
- **One Jira connection** serves all demo users
- **Your Jira account** (`timchan6633`) is used for all task exports
- All projects export to **your Jira workspace**

### How It Works:

1. **Pre-authorize Jira (Before Expo)**
   - You (the presenter) connect your Jira account once
   - Connection persists for all demo sessions
   - Students don't need to authorize Jira

2. **During Expo**
   - Students create projects and generate tasks
   - When they click "Push to Jira", tasks go to your Jira workspace
   - They can see the tasks created in your Jira (via share screen)

3. **User Mapping**
   ```
   Demo User 1 (Student A) → timchan6633's Jira → Project "Student A's App"
   Demo User 2 (Student B) → timchan6633's Jira → Project "Student B's App"
   Demo User 3 (Teacher)   → timchan6633's Jira → Project "Demo Project"
   ```

All use the **same OAuth token** stored with `user_id = "default_user"`.

## Pre-Expo Setup Checklist

### 1. Set Up Demo Environment

```bash
# Clone repository
git clone <your-repo-url>
cd design-thinking-ai

# Create virtual environment
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt
```

### 2. Configure Environment Variables

Create `.env` file:

```bash
# OpenAI API Key (required for AI features)
OPENAI_API_KEY=sk-proj-your-key-here

# Database (SQLite for demo)
DATABASE_URL=sqlite:///./demo_expo.db

# Jira OAuth (for Implement stage demo)
JIRA_OAUTH_CLIENT_ID=VhFPD8tI5RVq4YSu9KXeyNeDdf8WJZK8
JIRA_OAUTH_CLIENT_SECRET=your-secret-here
JIRA_OAUTH_REDIRECT_URI=http://localhost:8501/oauth/callback
ENCRYPTION_KEY=your-encryption-key-here

# Demo mode
DEBUG=True
APP_NAME=Design Thinking AI - Demo
```

### 3. Initialize Database

```bash
python -c "from config.database import init_db; init_db()"
```

### 4. Pre-Authorize Jira (One-Time Setup)

**Before the expo**, authorize your Jira account:

1. Start the app: `streamlit run app.py`
2. Create a demo project
3. Go to Implement stage → Tab 3: Jira Export
4. Click "Connect to Jira"
5. Authorize with your Atlassian account
6. Configure Jira project (use a demo project in your Jira workspace)

This OAuth token will persist for all demo users.

### 5. Create Sample Projects (Optional)

Prepare 2-3 example projects showing different stages:
- **Project 1:** Complete all 6 stages (shows full workflow)
- **Project 2:** Stopped at Prototype stage (shows in-progress work)
- **Project 3:** Empty (for live demo creation)

## Expo Day Workflow

### Opening (5 minutes)
1. **Welcome & Context**
   - Explain Design Thinking methodology
   - Show the 6-stage process diagram
   - Mention this is a demo/prototype

2. **Demo Mode Explanation**
   ```
   "This is running in demo mode - everyone shares the same workspace.
   In production, each user would have private projects and their own Jira connection.
   For today, we'll use my Jira account for demonstrations."
   ```

### Live Demonstration (10 minutes)

#### Option A: Complete Walkthrough (Use Pre-Made Project)
1. **Empathise Stage:** Show uploaded research data & AI analysis
2. **Define Stage:** Show problem statement & persona generation
3. **Ideate Stage:** Show brainstorming and AI categorization
4. **Prototype Stage:** Show mockup generation from sketches
5. **Test Stage:** Show feedback collection & analysis
6. **Implement Stage:** Show roadmap & Jira integration (live push tasks)

#### Option B: Interactive Demo (Create New Project Live)
1. Create project: "Mobile App for Student Study Groups"
2. **Empathise:** Upload sample survey data (have prepared CSV)
3. **Define:** Generate AI problem statement
4. **Ideate:** AI brainstorm 15 ideas
5. **Prototype:** Upload hand-drawn sketch → AI mockup
6. **Implement:** Generate roadmap → Push 3 tasks to Jira (show in browser)

### Q&A / Hands-On (5-10 minutes)
- Let students/teachers try creating their own project
- Guide them through 1-2 stages
- Show how Jira sync works

## Jira Workspace Organization

Create a dedicated **Expo Demo** project in your Jira:

```
Jira Project: "DTAI-DEMO"

Epics:
├── [DTAI-DEMO-1] Project A Implementation
├── [DTAI-DEMO-2] Project B Implementation
└── [DTAI-DEMO-3] Project C Implementation

Tasks (auto-created by app):
├── [DTAI-DEMO-10] Setup authentication system (8pts, Backend)
├── [DTAI-DEMO-11] Create dashboard UI (5pts, Frontend)
└── ...
```

**Before each demo:** Archive old tasks or create fresh project.

## Technical Architecture Explanation (For Technical Audience)

### Current: Single-User Demo Mode

```
┌─────────────────────────────────────┐
│   Demo Users (Students/Teachers)    │
└────────────┬────────────────────────┘
             │ (All use user_id="default_user")
             ▼
┌─────────────────────────────────────┐
│       SQLite Database (Local)        │
│  - All projects visible to everyone  │
│  - One OAuth token (timchan6633)     │
└────────────┬────────────────────────┘
             │
             ▼
┌─────────────────────────────────────┐
│    Jira (timchan6633's workspace)   │
│  - All tasks created here            │
│  - Shared for all demo users         │
└─────────────────────────────────────┘
```

### Production: Multi-User Mode

```
┌─────────────────────────────────────┐
│           Real Users                 │
│   User A  │  User B  │  User C       │
└────┬──────┴────┬─────┴───┬───────────┘
     │           │          │
     ▼           ▼          ▼
┌────────────────────────────────────┐
│      PostgreSQL (Cloud)             │
│  user_id: alice → Projects: [1,2]   │
│  user_id: bob   → Projects: [3]     │
│  user_id: carol → Projects: [4,5]   │
└────┬───────────┬───────────┬────────┘
     │           │            │
     ▼           ▼            ▼
┌─────────┐ ┌──────────┐ ┌──────────┐
│ Jira A  │ │  Jira B  │ │  Jira C  │
│ (Alice) │ │  (Bob)   │ │ (Carol)  │
└─────────┘ └──────────┘ └──────────┘
```

## FAQ for Expo Attendees

**Q: Can I use this with my own Jira account?**

A: In this demo version, everyone shares the presenter's Jira connection. For personal use, you'd need to:
1. Set up your own instance
2. Create an Atlassian OAuth app
3. Connect your Jira account
4. Deploy with user authentication

**Q: Are projects private?**

A: No, in demo mode all projects are visible to everyone. This is intentional for learning purposes. Production version would have user accounts and private projects.

**Q: Can I take this home and use it?**

A: Yes! The code is open source. You'll need to:
1. Set up OpenAI API key ($)
2. Set up Jira OAuth app (free for <10 users)
3. Run locally or deploy to cloud

**Q: How does the AI know about Design Thinking?**

A: The application uses carefully crafted prompts that guide GPT-4o through each stage of the Design Thinking process, following Stanford d.school methodology.

## Cleanup After Expo

1. **Archive Demo Projects:**
   ```sql
   -- Connect to database
   sqlite3 demo_expo.db
   DELETE FROM projects WHERE created_at < '2025-01-01';
   ```

2. **Clear Jira Tasks:**
   - Go to your Jira project
   - Bulk delete demo tasks
   - Or archive the demo project

3. **Reset OAuth (Optional):**
   ```sql
   DELETE FROM jira_oauth_tokens WHERE user_id = 'default_user';
   ```

## Presentation Tips

### Do's ✅
- **Prepare backup scenarios** (pre-generated content if AI is slow)
- **Test internet connection** (AI + Jira require internet)
- **Have screenshots ready** (in case of API failures)
- **Explain limitations** ("This is a prototype demonstrating the concept")
- **Show code briefly** (if technical audience is interested)

### Don'ts ❌
- **Don't generate 50 tasks** during demo (show 3-5 max)
- **Don't skip explaining what's happening** (narrate AI processing)
- **Don't assume non-technical knowledge** (explain OAuth, API, etc.)
- **Don't hide when things break** (use as teaching moment)

## Emergency Fallback Plan

If internet/API fails during demo:

1. **Switch to pre-recorded video** showing full workflow
2. **Show screenshots** of each stage instead of live demo
3. **Focus on explaining the concept** rather than live demo
4. **Show code architecture** on screen

## Contact & Support

- **GitHub:** [Your repository URL]
- **Documentation:** See `SETUP_JIRA.md` for production setup
- **Email:** [Your email for questions]

---

**Good luck with your expo presentation!** 🎓🚀
