# Jira OAuth 2.0 Integration Setup Guide

This guide will help you set up OAuth 2.0 authentication for Jira integration in the Design Thinking AI application.

## Overview

The application uses **Atlassian OAuth 2.0 (3LO)** for secure, per-user Jira authentication. Each user connects their own Jira account, and credentials are encrypted and stored securely in the database.

## Prerequisites

- An Atlassian account with access to Jira
- Admin access to create an OAuth 2.0 app in Atlassian Developer Console
- Python 3.8+ with required dependencies installed

## Step 1: Create an Atlassian OAuth 2.0 App

### 1.1 Go to Atlassian Developer Console

Visit [https://developer.atlassian.com/console/myapps/](https://developer.atlassian.com/console/myapps/)

### 1.2 Create a New App

1. Click "Create" → "OAuth 2.0 integration"
2. Enter app name: "Design Thinking AI" (or your preferred name)
3. Click "Create"

### 1.3 Configure Permissions

1. Click on your newly created app
2. Go to "Permissions" tab
3. Add the following scopes:
   - `read:jira-work` - Read Jira project and issue data
   - `write:jira-work` - Create and update Jira issues
   - `read:jira-user` - Read user information
   - `offline_access` - Get refresh tokens for long-term access

4. Click "Save changes"

### 1.4 Configure OAuth 2.0 Settings

1. Go to "Authorization" tab
2. Add Callback URL:
   - For local development: `http://localhost:8501/oauth_callback`
   - For production: `https://yourdomain.com/oauth_callback`

   **Note:** Streamlit automatically creates routes from files in `pages/` directory. The file `pages/oauth_callback.py` becomes accessible at `/oauth_callback`.

3. Note down:
   - **Client ID** (shown on the Settings page)
   - **Client Secret** (click "Generate secret" if not shown)

## Step 2: Configure Environment Variables

1. Open your `.env` file (or create one from `.env.example`):

```bash
# Jira OAuth 2.0 Configuration
JIRA_OAUTH_CLIENT_ID=your-client-id-here
JIRA_OAUTH_CLIENT_SECRET=your-client-secret-here
JIRA_OAUTH_REDIRECT_URI=http://localhost:8501/oauth_callback

# Encryption key for storing tokens (generate with: python -c "from cryptography.fernet import Fernet; print(Fernet.generate_key().decode())")
ENCRYPTION_KEY=your-generated-encryption-key-here
```

2. Generate an encryption key:

```bash
python -c "from cryptography.fernet import Fernet; print(Fernet.generate_key().decode())"
```

Copy the output and paste it as `ENCRYPTION_KEY` in your `.env` file.

**⚠️ IMPORTANT:** Keep this key secret! If lost, all stored OAuth tokens will be unrecoverable.

## Step 3: Install Dependencies

Install the required Python packages:

```bash
pip install cryptography requests sqlalchemy
```

## Step 4: Run Database Migration

The application needs new database tables for OAuth tokens. Run the migration:

```python
# Run this in Python or create a migration script
from config.database import init_db, Base, engine
from database.models import JiraOAuthToken, JiraConfig

# Create new tables
Base.metadata.create_all(bind=engine)
```

Or use Alembic if you have it set up:

```bash
alembic revision --autogenerate -m "Add Jira OAuth tables"
alembic upgrade head
```

## Step 5: Implement OAuth Callback (Production Only)

For production deployment, you need to handle the OAuth callback. Create a callback endpoint:

### Option A: Streamlit Component (Recommended)

Create `pages/oauth_callback.py`:

```python
import streamlit as st
from services.jira_oauth_service import JiraOAuthService
from database.models import JiraOAuthToken
from config.database import get_db

# Get auth code from URL
query_params = st.experimental_get_query_params()
code = query_params.get("code", [None])[0]
state = query_params.get("state", [None])[0]

if code:
    try:
        oauth_service = JiraOAuthService()

        # Exchange code for tokens
        token_response = oauth_service.exchange_code_for_token(code)

        # Get accessible resources
        resources = oauth_service.get_accessible_resources(token_response["access_token"])

        if resources:
            cloud_id = resources[0]["id"]

            # Get user info
            user_info = oauth_service.get_user_info(token_response["access_token"], cloud_id)

            # Store tokens (use proper user_id from session)
            user_id = st.session_state.get("user_id", "default_user")

            oauth_service.store_oauth_token(
                user_id=user_id,
                token_response=token_response,
                jira_account_id=user_info["accountId"],
                jira_display_name=user_info.get("displayName"),
                jira_email=user_info.get("emailAddress")
            )

            st.success("✅ Successfully connected to Jira!")
            st.info("You can close this tab and return to the application.")
        else:
            st.error("No accessible Jira sites found.")

    except Exception as e:
        st.error(f"❌ OAuth authorization failed: {str(e)}")
else:
    st.error("No authorization code received")
```

### Option B: Flask/FastAPI Endpoint

If using a separate backend, create an OAuth callback endpoint:

```python
from flask import Flask, request, redirect
from services.jira_oauth_service import JiraOAuthService

app = Flask(__name__)

@app.route('/oauth/callback')
def oauth_callback():
    code = request.args.get('code')
    state = request.args.get('state')

    # Verify state (CSRF protection)
    # ... implement state verification ...

    oauth_service = JiraOAuthService()

    try:
        # Exchange code for tokens
        token_response = oauth_service.exchange_code_for_token(code)

        # Get user info and store tokens
        # ... implementation ...

        # Redirect back to main app
        return redirect('/implement?oauth=success')

    except Exception as e:
        return redirect(f'/implement?oauth=error&message={str(e)}')
```

## Step 6: Test the Integration

### 6.1 Start the Application

```bash
streamlit run app.py
```

### 6.2 Navigate to Implement Stage

1. Create or open a project
2. Go to Stage 6: Implement
3. Click on Tab 3: Jira Export

### 6.3 Connect to Jira

1. Click "Connect to Jira" button
2. You'll see the OAuth authorization URL
3. **For development:** Copy the URL and paste it in your browser
4. **For production:** The button should redirect automatically
5. Authorize the application in Atlassian
6. You'll be redirected back to the callback URL
7. Return to the Implement page - you should see "Connected" status

### 6.4 Configure Jira Project

1. Select your Jira site from the dropdown
2. Enter your Jira project key (e.g., "PROJ")
3. Click "Save Configuration"

### 6.5 Push Tasks

1. Generate roadmap (Tab 1) and tasks (Tab 2) if not done
2. Go to Tab 3: Jira Export
3. Click "Push Tasks to Jira"
4. Tasks will be created in your Jira project with an Epic

### 6.6 Sync Status

1. Make changes to task status in Jira (move to "In Progress", "Done", etc.)
2. Click "Sync Status from Jira"
3. Status updates will be reflected in the application

## Security Best Practices

### 1. Encryption Key Management

- **Never commit `.env` file to version control**
- Store encryption key in secure secret management (AWS Secrets Manager, Azure Key Vault, etc.)
- Rotate encryption key periodically (requires re-encryption of all tokens)

### 2. OAuth Token Storage

- Tokens are encrypted using Fernet (symmetric encryption)
- Each user's tokens are stored separately
- Tokens are automatically refreshed when expired

### 3. HTTPS in Production

- **Always use HTTPS** in production
- Atlassian requires HTTPS for OAuth redirect URIs
- Use SSL/TLS certificates from trusted CA

### 4. State Parameter (CSRF Protection)

The application uses a random `state` parameter for CSRF protection. In production, verify the state parameter in the callback:

```python
# Store state in session before redirect
import secrets
state = secrets.token_urlsafe(32)
st.session_state['oauth_state'] = state

# Verify in callback
received_state = request.args.get('state')
expected_state = st.session_state.get('oauth_state')
if received_state != expected_state:
    raise Exception("Invalid state parameter - possible CSRF attack")
```

## Troubleshooting

### Error: "Invalid client_id or client_secret"

- Check that you copied the Client ID and Secret correctly from Atlassian Developer Console
- Ensure no extra spaces or newlines in `.env` file

### Error: "Redirect URI mismatch"

- Verify the redirect URI in `.env` matches exactly what's configured in Atlassian
- Include the protocol (http:// or https://)
- No trailing slashes

### Error: "No accessible resources found"

- Ensure the OAuth app has been approved by Jira admin
- Check that the user has access to at least one Jira site
- Verify the `read:jira-work` scope is included

### Error: "Token expired"

- Tokens are automatically refreshed - this should not happen
- If it does, click "Disconnect" and reconnect to get a fresh token

### Error: "Encryption/Decryption failed"

- Check that `ENCRYPTION_KEY` in `.env` is correct
- If you changed the key, all existing tokens are invalid - users must reconnect

### Error: "Failed to create task - customfield_10016 does not exist"

- Story points field ID varies by Jira instance
- Check your Jira custom field IDs: Settings → Issues → Custom fields
- Update `services/jira_api_service.py` line with your story points field ID

## Production Deployment Checklist

- [ ] Set up HTTPS with valid SSL certificate
- [ ] Configure production OAuth redirect URI in Atlassian
- [ ] Store secrets in secure secret management system
- [ ] Set `DEBUG=False` in `.env`
- [ ] Implement proper user authentication
- [ ] Set up database backups (includes encrypted tokens)
- [ ] Configure logging and error monitoring
- [ ] Test OAuth flow end-to-end
- [ ] Document custom Jira field IDs for your instance
- [ ] Set up token refresh monitoring

## Additional Resources

- [Atlassian OAuth 2.0 Documentation](https://developer.atlassian.com/cloud/jira/platform/oauth-2-3lo-apps/)
- [Jira REST API Reference](https://developer.atlassian.com/cloud/jira/platform/rest/v3/)
- [Fernet Encryption Documentation](https://cryptography.io/en/latest/fernet/)

## Support

If you encounter issues:
1. Check the troubleshooting section above
2. Review application logs for detailed error messages
3. Verify all environment variables are set correctly
4. Test OAuth flow with Atlassian's OAuth playground
5. Check Jira API permissions in Developer Console

---

**Note:** This integration is designed for production use with multi-user support. Each user maintains their own Jira connection with their personal credentials, ensuring proper access control and audit trails.
