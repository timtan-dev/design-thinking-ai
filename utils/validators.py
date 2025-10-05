"""
Validators
File and input validation functions
"""

from config.settings import Settings
from typing import Tuple
import os

def validate_file_type(filename: str, allowed_types: list = None) -> Tuple[bool, str]:
    """
    Validate file type

    Args:
        filename: Name of the file
        allowed_types: List of allowed extensions (without dot)

    Returns:
        Tuple of (is_valid, error_message)
    """
    if allowed_types is None:
        allowed_types = Settings.ALLOWED_FILE_TYPES

    file_ext = filename.split('.')[-1].lower()

    if file_ext not in allowed_types:
        return False, f"File type .{file_ext} not allowed. Allowed types: {', '.join(allowed_types)}"

    return True, ""

def validate_file_size(file_size: int, max_size_mb: int = None) -> Tuple[bool, str]:
    """
    Validate file size

    Args:
        file_size: File size in bytes
        max_size_mb: Maximum allowed size in MB

    Returns:
        Tuple of (is_valid, error_message)
    """
    if max_size_mb is None:
        max_size_mb = Settings.MAX_FILE_SIZE_MB

    max_bytes = max_size_mb * 1024 * 1024

    if file_size > max_bytes:
        return False, f"File too large. Maximum size: {max_size_mb}MB"

    return True, ""

def validate_project_name(name: str) -> Tuple[bool, str]:
    """
    Validate project name

    Args:
        name: Project name

    Returns:
        Tuple of (is_valid, error_message)
    """
    if not name or len(name.strip()) == 0:
        return False, "Project name cannot be empty"

    if len(name) > 255:
        return False, "Project name too long (max 255 characters)"

    # Check for invalid characters
    invalid_chars = ['<', '>', ':', '"', '/', '\\', '|', '?', '*']
    if any(char in name for char in invalid_chars):
        return False, f"Project name contains invalid characters: {', '.join(invalid_chars)}"

    return True, ""

def sanitize_filename(filename: str) -> str:
    """
    Sanitize filename to remove invalid characters

    Args:
        filename: Original filename

    Returns:
        Sanitized filename
    """
    invalid_chars = ['<', '>', ':', '"', '/', '\\', '|', '?', '*']

    sanitized = filename
    for char in invalid_chars:
        sanitized = sanitized.replace(char, '_')

    return sanitized

def validate_text_input(text: str, min_length: int = 1, max_length: int = 10000) -> Tuple[bool, str]:
    """
    Validate text input

    Args:
        text: Text to validate
        min_length: Minimum length
        max_length: Maximum length

    Returns:
        Tuple of (is_valid, error_message)
    """
    if not text or len(text.strip()) < min_length:
        return False, f"Text must be at least {min_length} characters"

    if len(text) > max_length:
        return False, f"Text too long (max {max_length} characters)"

    return True, ""
