"""
Helper Functions
General utility functions
"""

import hashlib
import secrets
from typing import List, Dict, Any
from datetime import datetime, timedelta

def generate_unique_id(prefix: str = "") -> str:
    """
    Generate unique identifier

    Args:
        prefix: Optional prefix for the ID

    Returns:
        Unique ID string
    """
    timestamp = datetime.now().strftime("%Y%m%d%H%M%S")
    random_part = secrets.token_hex(4)
    return f"{prefix}{timestamp}_{random_part}" if prefix else f"{timestamp}_{random_part}"

def hash_text(text: str) -> str:
    """
    Generate hash of text

    Args:
        text: Text to hash

    Returns:
        Hash string
    """
    return hashlib.sha256(text.encode()).hexdigest()

def chunk_list(items: List[Any], chunk_size: int) -> List[List[Any]]:
    """
    Split list into chunks

    Args:
        items: List to chunk
        chunk_size: Size of each chunk

    Returns:
        List of chunks
    """
    return [items[i:i + chunk_size] for i in range(0, len(items), chunk_size)]

def merge_dicts(*dicts: Dict) -> Dict:
    """
    Merge multiple dictionaries

    Args:
        *dicts: Dictionaries to merge

    Returns:
        Merged dictionary
    """
    result = {}
    for d in dicts:
        result.update(d)
    return result

def get_time_ago(dt: datetime) -> str:
    """
    Get human-readable time ago string

    Args:
        dt: Datetime object

    Returns:
        Time ago string (e.g., "2 hours ago")
    """
    if dt is None:
        return "Never"

    now = datetime.utcnow()
    diff = now - dt

    if diff.days > 365:
        years = diff.days // 365
        return f"{years} year{'s' if years != 1 else ''} ago"
    elif diff.days > 30:
        months = diff.days // 30
        return f"{months} month{'s' if months != 1 else ''} ago"
    elif diff.days > 0:
        return f"{diff.days} day{'s' if diff.days != 1 else ''} ago"
    elif diff.seconds > 3600:
        hours = diff.seconds // 3600
        return f"{hours} hour{'s' if hours != 1 else ''} ago"
    elif diff.seconds > 60:
        minutes = diff.seconds // 60
        return f"{minutes} minute{'s' if minutes != 1 else ''} ago"
    else:
        return "Just now"

def calculate_completion_percentage(completed: int, total: int) -> float:
    """
    Calculate completion percentage

    Args:
        completed: Number of completed items
        total: Total number of items

    Returns:
        Percentage (0-100)
    """
    if total == 0:
        return 0.0
    return (completed / total) * 100

def safe_divide(numerator: float, denominator: float, default: float = 0.0) -> float:
    """
    Safe division with default for division by zero

    Args:
        numerator: Numerator
        denominator: Denominator
        default: Default value if division by zero

    Returns:
        Result of division or default
    """
    if denominator == 0:
        return default
    return numerator / denominator
