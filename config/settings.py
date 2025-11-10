"""
Application Settings
Load and manage environment variables and configuration
"""

import os
from dotenv import load_dotenv
from pathlib import Path

# Load environment variables
load_dotenv()

# Try to import streamlit for secrets (only available when running in Streamlit)
try:
    import streamlit as st
    HAS_STREAMLIT = True
except ImportError:
    HAS_STREAMLIT = False
    st = None

class Settings:
    """Application configuration settings"""

    # API Keys
    # Priority: Streamlit secrets > Environment variables > Empty string
    @classmethod
    def _get_secret(cls, key: str, default: str = '') -> str:
        """Get secret from Streamlit secrets or environment variables"""
        # Try Streamlit secrets first (for deployment)
        if HAS_STREAMLIT and st is not None:
            try:
                # Check if secrets are available
                if hasattr(st, 'secrets'):
                    return st.secrets.get(key, os.getenv(key, default))
            except Exception:
                # If secrets not available or any error, fall back to .env
                pass

        # Fall back to environment variables (for local development)
        return os.getenv(key, default)

    OPENAI_API_KEY = _get_secret.__func__(None, 'OPENAI_API_KEY', '')
    ANTHROPIC_API_KEY = _get_secret.__func__(None, 'ANTHROPIC_API_KEY', '')
    XAI_API_KEY = _get_secret.__func__(None, 'XAI_API_KEY', '')  # For Grok models

    # Database
    DATABASE_URL = os.getenv('DATABASE_URL', 'sqlite:///./design_thinking.db')

    # Security
    SECRET_KEY = os.getenv('SECRET_KEY', 'dev-secret-key-change-in-production')

    # Application
    APP_NAME = os.getenv('APP_NAME', 'Design Thinking AI Agent')
    DEBUG = os.getenv('DEBUG', 'True').lower() == 'true'

    # File Upload
    MAX_FILE_SIZE_MB = int(os.getenv('MAX_FILE_SIZE_MB', '10'))
    ALLOWED_FILE_TYPES = ['csv', 'txt', 'pdf', 'docx', 'xlsx', 'png', 'jpg', 'jpeg']

    # Directories
    BASE_DIR = Path(__file__).resolve().parent.parent
    UPLOAD_DIR = BASE_DIR / 'data' / 'uploads'
    EXPORT_DIR = BASE_DIR / 'data' / 'exports'
    TEMPLATE_DIR = BASE_DIR / 'assets' / 'templates'

    # OpenAI
    OPENAI_MODEL = os.getenv('OPENAI_MODEL', 'gpt-4.1')
    OPENAI_TEMPERATURE = float(os.getenv('OPENAI_TEMPERATURE', '0.7'))
    OPENAI_MAX_TOKENS = int(os.getenv('OPENAI_MAX_TOKENS', '2000'))

    @classmethod
    def ensure_directories(cls):
        """Create necessary directories if they don't exist"""
        cls.UPLOAD_DIR.mkdir(parents=True, exist_ok=True)
        cls.EXPORT_DIR.mkdir(parents=True, exist_ok=True)
        cls.TEMPLATE_DIR.mkdir(parents=True, exist_ok=True)

    @classmethod
    def validate(cls):
        """Validate required settings"""
        if not cls.OPENAI_API_KEY:
            raise ValueError("OPENAI_API_KEY not set in environment variables")
        return True

# Ensure directories exist on import
Settings.ensure_directories()
