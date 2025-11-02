"""
Jira OAuth 2.0 Callback Handler
Handles the OAuth redirect from Atlassian after user authorization
"""

import streamlit as st
from services.jira_oauth_service import JiraOAuthService
from config.database import get_db

# Page configuration
st.set_page_config(
    page_title="Jira OAuth - Design Thinking AI",
    page_icon="🔗",
    layout="centered"
)

# Title
st.title("🔗 Jira OAuth Authorization")

# Get query parameters from URL
query_params = st.query_params

code = query_params.get("code")
state = query_params.get("state")
error = query_params.get("error")

# Handle OAuth error
if error:
    st.error(f"❌ Authorization failed: {error}")
    error_description = query_params.get("error_description", "No additional details")
    st.info(f"Details: {error_description}")

    st.markdown("---")
    st.markdown("### What to do next:")
    st.markdown("""
    1. Return to the Implement page
    2. Try clicking "Connect to Jira" again
    3. If the issue persists, check your OAuth app configuration in Atlassian Developer Console
    """)

    if st.button("← Back to Home"):
        st.switch_page("app.py")

    st.stop()

# Check for required parameters
if not code or not state:
    st.error("❌ Missing authorization code or state parameter")
    st.warning("This page should only be accessed via OAuth redirect from Atlassian.")

    st.markdown("---")
    st.info("If you arrived here by mistake, please navigate to your project and use the 'Connect to Jira' button in the Implement stage.")

    if st.button("← Back to Home"):
        st.switch_page("app.py")

    st.stop()

# Verify state (CSRF protection)
expected_state = st.session_state.get('oauth_state')

if not expected_state:
    st.error("❌ No OAuth session found")
    st.warning("Your session may have expired. Please restart the OAuth flow.")

    st.markdown("---")
    st.info("💡 **Tip:** Make sure you complete the authorization within a few minutes of starting it.")

    if st.button("← Back to Home"):
        st.switch_page("app.py")

    st.stop()

if state != expected_state:
    st.error("❌ Invalid state parameter - possible CSRF attack detected")
    st.warning("The state parameter doesn't match. This could indicate a security issue.")

    st.markdown("---")
    st.markdown("### Security Notice:")
    st.markdown("""
    The OAuth state parameter validation failed. This is a security measure to prevent CSRF attacks.

    **What happened:**
    - Expected state: `{}`
    - Received state: `{}`

    **What to do:**
    1. Clear your browser cache
    2. Return to the Implement page
    3. Try the authorization again
    """.format(expected_state[:20] + "...", state[:20] + "..."))

    if st.button("← Back to Home"):
        st.switch_page("app.py")

    st.stop()

# Get user_id from session (for demo mode, defaults to default_user)
user_id = st.session_state.get('oauth_user_id', 'default_user')

# Process OAuth callback
try:
    with st.spinner("🔄 Processing authorization..."):
        oauth_service = JiraOAuthService()

        # Step 1: Exchange authorization code for tokens
        with st.status("Exchanging authorization code...", expanded=True) as status:
            st.write("📡 Requesting access token from Atlassian...")
            token_response = oauth_service.exchange_code_for_token(code)
            st.write("✅ Access token received!")
            status.update(label="Token exchange complete", state="complete")

        # Step 2: Get accessible Jira sites
        with st.status("Fetching your Jira sites...", expanded=True) as status:
            st.write("🔍 Querying accessible Jira Cloud sites...")
            resources = oauth_service.get_accessible_resources(token_response["access_token"])

            if not resources:
                status.update(label="No Jira sites found", state="error")
                st.error("❌ No accessible Jira sites found for your account.")
                st.info("Please ensure you have access to at least one Jira Cloud site and try again.")
                st.stop()

            # Use first resource (in production, let user choose)
            cloud_id = resources[0]["id"]
            jira_site_name = resources[0]["name"]
            jira_url = resources[0]["url"]

            st.write(f"✅ Found {len(resources)} site(s)")
            st.write(f"🏢 Using: **{jira_site_name}**")
            status.update(label="Jira sites retrieved", state="complete")

        # Step 3: Get user information from Jira
        with st.status("Retrieving your Jira profile...", expanded=True) as status:
            st.write("👤 Fetching user information...")
            user_info = oauth_service.get_user_info(token_response["access_token"], cloud_id)

            st.write(f"✅ Hello, **{user_info.get('displayName')}**!")
            status.update(label="User info retrieved", state="complete")

        # Step 4: Store tokens securely
        with st.status("Storing credentials...", expanded=True) as status:
            st.write("🔐 Encrypting and storing OAuth tokens...")

            oauth_service.store_oauth_token(
                user_id=user_id,
                token_response=token_response,
                jira_account_id=user_info["accountId"],
                jira_display_name=user_info.get("displayName"),
                jira_email=user_info.get("emailAddress")
            )

            st.write("✅ Credentials securely stored!")
            status.update(label="Credentials saved", state="complete")

    # Clear OAuth session data (no longer needed)
    if 'oauth_state' in st.session_state:
        del st.session_state['oauth_state']
    if 'oauth_user_id' in st.session_state:
        del st.session_state['oauth_user_id']

    # Success message
    st.success("✅ Successfully connected to Jira!")
    st.balloons()

    # Show connection details
    st.markdown("---")
    st.markdown("### 🎉 Connection Successful!")

    col1, col2 = st.columns(2)

    with col1:
        st.markdown("**Jira Site:**")
        st.info(f"🏢 {jira_site_name}")

        st.markdown("**Account:**")
        st.info(f"👤 {user_info.get('displayName')}")

    with col2:
        st.markdown("**Email:**")
        st.info(f"📧 {user_info.get('emailAddress')}")

        st.markdown("**Account ID:**")
        st.code(user_info['accountId'], language=None)

    st.markdown("---")

    # Security notice
    with st.expander("🔒 Security Information"):
        st.markdown("""
        **Your credentials are secure:**
        - OAuth tokens are encrypted using Fernet (symmetric encryption)
        - Stored in local database with encryption key from .env
        - Automatically refreshed before expiration
        - Can be disconnected anytime from the Implement page

        **What you authorized:**
        - Read Jira work (issues, projects, users)
        - Write Jira work (create/update issues)
        - Offline access (refresh tokens for long-term access)
        """)

    # Next steps
    st.markdown("### 🚀 Next Steps")

    st.markdown("""
    1. **Navigate to your project** using the sidebar
    2. **Go to the Implement stage** (Stage 6)
    3. **Click on "Jira Export" tab** (Tab 3)
    4. **Configure your Jira project** and start pushing tasks!
    """)

    # Navigation button
    if st.button("📂 Go to Projects", type="primary", use_container_width=True):
        st.switch_page("app.py")

except Exception as e:
    # Error handling
    st.error(f"❌ OAuth authorization failed")

    st.markdown("### Error Details:")
    with st.expander("🔍 View Technical Details", expanded=True):
        st.code(str(e), language="text")

        # Show helpful debugging info
        st.markdown("**Debug Information:**")
        st.json({
            "error_type": type(e).__name__,
            "error_message": str(e),
            "user_id": user_id,
            "has_code": bool(code),
            "has_state": bool(state)
        })

    st.markdown("---")
    st.markdown("### 🔧 Troubleshooting Steps:")

    st.markdown("""
    1. **Check OAuth App Configuration:**
       - Go to [Atlassian Developer Console](https://developer.atlassian.com/console/myapps/)
       - Verify Client ID and Secret match your `.env` file
       - Ensure redirect URI is: `http://localhost:8501/oauth_callback`

    2. **Check Environment Variables:**
       - `JIRA_OAUTH_CLIENT_ID` - Should match Atlassian app
       - `JIRA_OAUTH_CLIENT_SECRET` - Should match Atlassian app
       - `JIRA_OAUTH_REDIRECT_URI` - Should be `http://localhost:8501/oauth_callback`
       - `ENCRYPTION_KEY` - Must be set (run: `python -c "from cryptography.fernet import Fernet; print(Fernet.generate_key().decode())"`)

    3. **Check OAuth Scopes:**
       - Ensure your app has these scopes enabled:
         - `read:jira-work`
         - `write:jira-work`
         - `read:jira-user`
         - `offline_access`

    4. **Check Console Logs:**
       - Look in your terminal for detailed error messages
       - The error above shows what went wrong

    5. **Try Again:**
       - Clear your browser cache
       - Restart the Streamlit app
       - Try the authorization flow again
    """)

    st.markdown("---")

    col1, col2 = st.columns(2)

    with col1:
        if st.button("🔄 Try Again", type="primary", use_container_width=True):
            st.switch_page("app.py")

    with col2:
        if st.button("📖 View Setup Guide", use_container_width=True):
            st.info("See SETUP_JIRA.md in the project root for detailed setup instructions")
