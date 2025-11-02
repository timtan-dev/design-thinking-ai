"""OAuth Callback Handler for Jira Integration"""

import streamlit as st
from services.jira_oauth_service import JiraOAuthService
from database.models import JiraOAuthToken
from config.database import get_db

st.set_page_config(page_title="Jira OAuth Callback", page_icon="🔗")

st.title("🔗 Jira OAuth Authorization")

# Get query parameters from URL
query_params = st.query_params

code = query_params.get("code")
state = query_params.get("state")
error = query_params.get("error")

if error:
    st.error(f"❌ Authorization failed: {error}")
    st.info("Please try again or check your OAuth app configuration.")
    if st.button("Return to Implement Page"):
        st.switch_page("app.py")
    st.stop()

if not code or not state:
    st.error("❌ No authorization code received")
    st.info("This page should only be accessed via OAuth redirect from Atlassian.")
    if st.button("Return to Home"):
        st.switch_page("app.py")
    st.stop()

# Verify state (CSRF protection)
expected_state = st.session_state.get('oauth_state')
if state != expected_state:
    st.error("❌ Invalid state parameter - possible CSRF attack detected")
    st.warning("Please restart the OAuth flow from the Implement page.")
    if st.button("Return to Implement Page"):
        st.switch_page("app.py")
    st.stop()

# Get user_id from session
user_id = st.session_state.get('oauth_user_id', 'default_user')

try:
    with st.spinner("🔄 Exchanging authorization code for access token..."):
        oauth_service = JiraOAuthService()

        # Exchange code for tokens
        st.info("Requesting access token from Atlassian...")
        token_response = oauth_service.exchange_code_for_token(code)

        # Get accessible resources (Jira sites)
        st.info("Fetching your accessible Jira sites...")
        resources = oauth_service.get_accessible_resources(token_response["access_token"])

        if not resources:
            st.error("❌ No accessible Jira sites found for your account.")
            st.info("Please ensure you have access to at least one Jira Cloud site.")
            st.stop()

        # Use first resource (in production, let user choose)
        cloud_id = resources[0]["id"]
        jira_site_name = resources[0]["name"]
        jira_url = resources[0]["url"]

        st.success(f"✅ Found Jira site: **{jira_site_name}** ({jira_url})")

        # Get user info from Jira
        st.info("Retrieving your Jira user information...")
        user_info = oauth_service.get_user_info(token_response["access_token"], cloud_id)

        # Store tokens in database (encrypted)
        st.info("Securely storing your credentials...")
        oauth_service.store_oauth_token(
            user_id=user_id,
            token_response=token_response,
            jira_account_id=user_info["accountId"],
            jira_display_name=user_info.get("displayName"),
            jira_email=user_info.get("emailAddress")
        )

        # Clear OAuth session data
        if 'oauth_state' in st.session_state:
            del st.session_state['oauth_state']
        if 'oauth_user_id' in st.session_state:
            del st.session_state['oauth_user_id']

        # Success!
        st.success("✅ Successfully connected to Jira!")

        st.markdown(f"""
        ### Connection Details:
        - **Jira Site:** {jira_site_name}
        - **Account:** {user_info.get('displayName')} ({user_info.get('emailAddress')})
        - **Account ID:** {user_info['accountId']}

        Your credentials are encrypted and securely stored.
        """)

        st.balloons()

        st.markdown("---")
        st.info("👉 You can now return to the Implement page to configure your Jira project and push tasks.")

        if st.button("🚀 Go to Implement Page", type="primary"):
            # In Streamlit, we can't directly navigate, but we can show instructions
            st.info("Please navigate to your project and go to the Implement stage → Jira Export tab")
            # Note: In production with multi-page app, use st.switch_page()

except Exception as e:
    st.error(f"❌ OAuth authorization failed: {str(e)}")

    with st.expander("🔍 Error Details"):
        st.code(str(e))

    st.markdown("---")
    st.markdown("### Troubleshooting:")
    st.markdown("""
    - Check that your `JIRA_OAUTH_CLIENT_ID` and `JIRA_OAUTH_CLIENT_SECRET` are correct in `.env`
    - Verify the redirect URI matches exactly: `http://localhost:8501/oauth/callback`
    - Ensure your OAuth app has the required scopes: `read:jira-work`, `write:jira-work`, `read:jira-user`, `offline_access`
    - Check the terminal/console for detailed error messages
    """)

    if st.button("Try Again"):
        st.rerun()
