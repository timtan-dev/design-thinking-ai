"""
Application Settings
Load and manage environment variables and configuration
"""

import os
from dotenv import load_dotenv
from pathlib import Path

# Load environment variables
load_dotenv()

class Settings:
    """Application configuration settings"""

    # API Keys
    OPENAI_API_KEY = os.getenv('OPENAI_API_KEY', '')

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
    OPENAI_MODEL = os.getenv('OPENAI_MODEL', 'gpt-4o-mini')
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
