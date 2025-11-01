# MCP Jira Integration Setup Guide

This guide will help you set up the Model Context Protocol (MCP) server for Jira integration in the Implement stage.

## What is MCP?

Model Context Protocol (MCP) is a standardized way for AI applications to interact with external services like Jira. It provides a secure bridge between your Design Thinking AI application and Jira's API.

## Prerequisites

- A Jira account (Jira Cloud or Jira Server)
- Admin or project management permissions in your Jira project
- Python 3.8+ installed
- The Design Thinking AI application running

## Step 1: Get Your Jira API Token

### For Jira Cloud (Atlassian Cloud):

1. Go to [https://id.atlassian.com/manage-profile/security/api-tokens](https://id.atlassian.com/manage-profile/security/api-tokens)
2. Click "Create API token"
3. Give it a label (e.g., "Design Thinking AI")
4. Copy the token immediately (you won't be able to see it again)

### For Jira Server/Data Center:

1. Log in to your Jira instance
2. Go to your profile settings
3. Navigate to Personal Access Tokens
4. Create a new token with appropriate permissions
5. Copy the token

## Step 2: Configure Environment Variables

1. Copy `.env.example` to `.env` if you haven't already:
   ```bash
   cp .env.example .env
   ```

2. Edit `.env` and add your Jira credentials:
   ```bash
   # Jira Integration
   JIRA_EMAIL=your-email@company.com
   JIRA_API_TOKEN=your-api-token-from-step-1
   JIRA_URL=https://your-company.atlassian.net
   JIRA_PROJECT_KEY=PROJ
   ```

   **Replace:**
   - `your-email@company.com` with your Atlassian account email
   - `your-api-token-from-step-1` with the token from Step 1
   - `your-company.atlassian.net` with your Jira instance URL
   - `PROJ` with your Jira project key (e.g., "MYAPP", "DEV")

## Step 3: Install MCP Server Dependencies

```bash
# Install MCP server packages
pip install mcp-server-jira anthropic-mcp
```

## Step 4: Configure MCP Server

Create a configuration file for the MCP server:

```bash
mkdir -p ~/.config/mcp
touch ~/.config/mcp/jira.json
```

Edit `~/.config/mcp/jira.json`:

```json
{
  "servers": {
    "jira": {
      "command": "mcp-server-jira",
      "args": [],
      "env": {
        "JIRA_URL": "https://your-company.atlassian.net",
        "JIRA_EMAIL": "your-email@company.com",
        "JIRA_API_TOKEN": "your-api-token"
      }
    }
  }
}
```

## Step 5: Test the Connection

Run the following test script to verify your Jira connection:

```python
# test_jira_connection.py
import os
import requests
from dotenv import load_dotenv

load_dotenv()

jira_url = os.getenv("JIRA_URL")
jira_email = os.getenv("JIRA_EMAIL")
jira_token = os.getenv("JIRA_API_TOKEN")

# Test connection
response = requests.get(
    f"{jira_url}/rest/api/3/myself",
    auth=(jira_email, jira_token)
)

if response.status_code == 200:
    print("✅ Jira connection successful!")
    print(f"Connected as: {response.json()['displayName']}")
else:
    print(f"❌ Connection failed: {response.status_code}")
    print(response.text)
```

Run the test:
```bash
python test_jira_connection.py
```

## Step 6: Using Jira Integration in the App

Once configured, you can use Jira integration in the Implement stage:

1. Navigate to your project
2. Go to Stage 6: Implement
3. Complete Tab 1 (Roadmap) and Tab 2 (Tasks)
4. Go to Tab 3: Jira Export
5. Configure your Jira project settings
6. Click "Push Tasks to Jira" to export tasks
7. Use "Sync Status from Jira" to pull updates

## Features Available

### Epic Creation
- Automatically creates an Epic in Jira with your project name
- All tasks are linked to this Epic

### Task Export
- Tasks are created as Jira Issues
- Story points are set automatically
- Priority levels are mapped to Jira priorities
- MoSCoW categories are added as labels
- Acceptance criteria are added to the description

### Two-Way Sync
- Status updates from Jira are synced back to the app
- Syncs: To Do, In Progress, Done
- Manual sync button + automatic check on page load

### Sub-task Support
- Tasks with dependencies are created as sub-tasks
- Parent-child relationships are maintained

## Troubleshooting

### Error: "403 Forbidden"
- Check your API token is correct
- Verify your Jira email matches the account
- Ensure you have project permissions

### Error: "404 Not Found"
- Verify your Jira URL is correct
- Check the project key exists
- Ensure the project is accessible to you

### Error: "MCP server not found"
- Make sure you installed `mcp-server-jira`
- Check the MCP config file path
- Restart your terminal session

### Tasks Not Syncing
- Check last sync time (shown in UI)
- Click "Sync Status from Jira" manually
- Verify tasks have `jira_issue_key` set

## Security Notes

- **Never commit `.env` file to version control**
- API tokens have full access to your Jira account
- Rotate tokens regularly (every 90 days recommended)
- Use separate tokens for different applications
- Revoke tokens immediately if compromised

## Additional Resources

- [Jira REST API Documentation](https://developer.atlassian.com/cloud/jira/platform/rest/v3/)
- [MCP Protocol Specification](https://spec.modelcontextprotocol.io/)
- [Atlassian API Tokens Guide](https://support.atlassian.com/atlassian-account/docs/manage-api-tokens-for-your-atlassian-account/)

## Need Help?

If you encounter issues:
1. Check the troubleshooting section above
2. Review your `.env` file configuration
3. Test your Jira credentials with the test script
4. Check application logs for error messages

---

**Note:** MCP Jira integration is optional. You can still use the Implement stage to generate roadmaps and tasks without connecting to Jira. You can export tasks as JSON/CSV and manually import them into your project management tool.
