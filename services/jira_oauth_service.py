"""Jira OAuth 2.0 Authentication Service"""

import os
import requests
from datetime import datetime, timedelta
from typing import Optional, Dict, Any
from cryptography.fernet import Fernet
from database.models import JiraOAuthToken
from config.database import get_db

# Try to import streamlit for secrets (only available when running in Streamlit)
try:
    import streamlit as st
    HAS_STREAMLIT = True
except ImportError:
    HAS_STREAMLIT = False

def _get_secret(key: str, default: str = None) -> str:
    """Get secret from Streamlit secrets or environment variables"""
    if HAS_STREAMLIT and hasattr(st, 'secrets') and key in st.secrets:
        return st.secrets[key]
    return os.getenv(key, default)

class JiraOAuthService:
    """Handle Jira OAuth 2.0 authentication and token management"""

    def __init__(self):
        self.client_id = _get_secret("JIRA_OAUTH_CLIENT_ID")
        self.client_secret = _get_secret("JIRA_OAUTH_CLIENT_SECRET")
        self.redirect_uri = _get_secret("JIRA_OAUTH_REDIRECT_URI", "https://design-thinking-ai-chen2106.streamlit.app/oauth/callback")
        self.encryption_key = _get_secret("ENCRYPTION_KEY")

        if self.encryption_key:
            self.cipher = Fernet(self.encryption_key.encode())
        else:
            # Generate a key if not provided (NOT recommended for production)
            self.encryption_key = Fernet.generate_key().decode()
            self.cipher = Fernet(self.encryption_key.encode())
            print("⚠️ WARNING: Using auto-generated encryption key. Set ENCRYPTION_KEY in .env for production!")

        # Atlassian OAuth endpoints
        self.auth_url = "https://auth.atlassian.com/authorize"
        self.token_url = "https://auth.atlassian.com/oauth/token"
        self.resource_url = "https://api.atlassian.com/oauth/token/accessible-resources"

    def get_authorization_url(self, state: str) -> str:
        """
        Generate OAuth authorization URL for user to visit

        Args:
            state: Random state string for CSRF protection

        Returns:
            Full authorization URL
        """
        scopes = [
            "read:jira-work",
            "write:jira-work",
            "read:jira-user",
            "offline_access"  # For refresh token
        ]

        params = {
            "audience": "api.atlassian.com",
            "client_id": self.client_id,
            "scope": " ".join(scopes),
            "redirect_uri": self.redirect_uri,
            "state": state,
            "response_type": "code",
            "prompt": "consent"
        }

        query_string = "&".join([f"{k}={requests.utils.quote(str(v))}" for k, v in params.items()])
        return f"{self.auth_url}?{query_string}"

    def exchange_code_for_token(self, code: str) -> Dict[str, Any]:
        """
        Exchange authorization code for access token

        Args:
            code: Authorization code from OAuth callback

        Returns:
            Token response with access_token, refresh_token, expires_in
        """
        data = {
            "grant_type": "authorization_code",
            "client_id": self.client_id,
            "client_secret": self.client_secret,
            "code": code,
            "redirect_uri": self.redirect_uri
        }

        response = requests.post(self.token_url, data=data)
        response.raise_for_status()

        return response.json()

    def refresh_access_token(self, refresh_token: str) -> Dict[str, Any]:
        """
        Refresh an expired access token

        Args:
            refresh_token: Refresh token from previous authorization

        Returns:
            New token response
        """
        data = {
            "grant_type": "refresh_token",
            "client_id": self.client_id,
            "client_secret": self.client_secret,
            "refresh_token": refresh_token
        }

        response = requests.post(self.token_url, data=data)
        response.raise_for_status()

        return response.json()

    def get_accessible_resources(self, access_token: str) -> list:
        """
        Get list of Jira sites accessible to the user

        Args:
            access_token: Valid OAuth access token

        Returns:
            List of accessible Jira resources (sites)
        """
        headers = {
            "Authorization": f"Bearer {access_token}",
            "Accept": "application/json"
        }

        response = requests.get(self.resource_url, headers=headers)
        response.raise_for_status()

        return response.json()

    def get_user_info(self, access_token: str, cloud_id: str) -> Dict[str, Any]:
        """
        Get user information from Jira

        Args:
            access_token: Valid OAuth access token
            cloud_id: Atlassian cloud ID

        Returns:
            User profile information
        """
        headers = {
            "Authorization": f"Bearer {access_token}",
            "Accept": "application/json"
        }

        response = requests.get(
            f"https://api.atlassian.com/ex/jira/{cloud_id}/rest/api/3/myself",
            headers=headers
        )
        response.raise_for_status()

        return response.json()

    def encrypt_token(self, token: str) -> str:
        """Encrypt a token for database storage"""
        return self.cipher.encrypt(token.encode()).decode()

    def decrypt_token(self, encrypted_token: str) -> str:
        """Decrypt a token from database"""
        return self.cipher.decrypt(encrypted_token.encode()).decode()

    def store_oauth_token(self, user_id: str, token_response: Dict[str, Any],
                         jira_account_id: str, jira_display_name: str = None,
                         jira_email: str = None) -> JiraOAuthToken:
        """
        Store OAuth tokens in database (encrypted)

        Args:
            user_id: Application user ID
            token_response: OAuth token response from Atlassian
            jira_account_id: Jira account ID
            jira_display_name: User's display name in Jira
            jira_email: User's email in Jira

        Returns:
            Created/updated JiraOAuthToken record
        """
        db = get_db()

        # Calculate expiration time
        expires_in = token_response.get("expires_in", 3600)
        expires_at = datetime.utcnow() + timedelta(seconds=expires_in)

        # Encrypt tokens
        encrypted_access = self.encrypt_token(token_response["access_token"])
        encrypted_refresh = self.encrypt_token(token_response["refresh_token"])

        # Check if token already exists for user
        existing_token = db.query(JiraOAuthToken).filter(
            JiraOAuthToken.user_id == user_id
        ).first()

        if existing_token:
            # Update existing token
            existing_token.access_token = encrypted_access
            existing_token.refresh_token = encrypted_refresh
            existing_token.expires_at = expires_at
            existing_token.scope = token_response.get("scope")
            existing_token.jira_account_id = jira_account_id
            existing_token.jira_display_name = jira_display_name
            existing_token.jira_email = jira_email
            existing_token.updated_at = datetime.utcnow()
            db.commit()
            db.refresh(existing_token)
            return existing_token
        else:
            # Create new token
            oauth_token = JiraOAuthToken(
                user_id=user_id,
                access_token=encrypted_access,
                refresh_token=encrypted_refresh,
                expires_at=expires_at,
                scope=token_response.get("scope"),
                jira_account_id=jira_account_id,
                jira_display_name=jira_display_name,
                jira_email=jira_email
            )
            db.add(oauth_token)
            db.commit()
            db.refresh(oauth_token)
            return oauth_token

    def get_valid_access_token(self, user_id: str) -> Optional[str]:
        """
        Get a valid access token for user, refreshing if necessary

        Args:
            user_id: Application user ID

        Returns:
            Valid access token or None if not authorized
        """
        db = get_db()

        oauth_token = db.query(JiraOAuthToken).filter(
            JiraOAuthToken.user_id == user_id
        ).first()

        if not oauth_token:
            return None

        # Check if token is expired
        if datetime.utcnow() >= oauth_token.expires_at:
            # Token expired, refresh it
            try:
                decrypted_refresh = self.decrypt_token(oauth_token.refresh_token)
                token_response = self.refresh_access_token(decrypted_refresh)

                # Update stored tokens
                expires_in = token_response.get("expires_in", 3600)
                oauth_token.access_token = self.encrypt_token(token_response["access_token"])
                oauth_token.refresh_token = self.encrypt_token(token_response["refresh_token"])
                oauth_token.expires_at = datetime.utcnow() + timedelta(seconds=expires_in)
                oauth_token.updated_at = datetime.utcnow()
                db.commit()
                db.refresh(oauth_token)

                return token_response["access_token"]
            except Exception as e:
                print(f"Failed to refresh token: {e}")
                return None

        # Token still valid, decrypt and return
        return self.decrypt_token(oauth_token.access_token)

    def revoke_token(self, user_id: str) -> bool:
        """
        Revoke OAuth token and delete from database

        Args:
            user_id: Application user ID

        Returns:
            True if revoked successfully
        """
        db = get_db()

        oauth_token = db.query(JiraOAuthToken).filter(
            JiraOAuthToken.user_id == user_id
        ).first()

        if oauth_token:
            db.delete(oauth_token)
            db.commit()
            return True

        return False

    def is_user_authorized(self, user_id: str) -> bool:
        """
        Check if user has valid Jira OAuth authorization

        Args:
            user_id: Application user ID

        Returns:
            True if user has valid authorization
        """
        return self.get_valid_access_token(user_id) is not None
