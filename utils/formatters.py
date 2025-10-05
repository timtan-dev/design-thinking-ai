"""
Formatters
Data formatting and display utilities
"""

import json
from typing import Any, Dict, List
from datetime import datetime
import re

def format_date(dt: datetime, format_str: str = "%Y-%m-%d %H:%M") -> str:
    """
    Format datetime object

    Args:
        dt: Datetime object
        format_str: Format string

    Returns:
        Formatted date string
    """
    if dt is None:
        return "N/A"
    return dt.strftime(format_str)

def format_json(data: Dict) -> str:
    """
    Format dictionary as pretty JSON

    Args:
        data: Dictionary to format

    Returns:
        Formatted JSON string
    """
    return json.dumps(data, indent=2)

def clean_text(text: str) -> str:
    """
    Clean text by removing extra whitespace and special characters

    Args:
        text: Text to clean

    Returns:
        Cleaned text
    """
    # Remove extra whitespace
    text = re.sub(r'\s+', ' ', text)

    # Strip leading/trailing whitespace
    text = text.strip()

    return text

def truncate_text(text: str, max_length: int = 100, suffix: str = "...") -> str:
    """
    Truncate text to specified length

    Args:
        text: Text to truncate
        max_length: Maximum length
        suffix: Suffix to add when truncated

    Returns:
        Truncated text
    """
    if len(text) <= max_length:
        return text

    return text[:max_length - len(suffix)] + suffix

def format_list_as_bullets(items: List[str]) -> str:
    """
    Format list as bullet points

    Args:
        items: List of items

    Returns:
        Formatted string with bullets
    """
    return "\n".join([f"• {item}" for item in items])

def format_number(number: float, decimals: int = 2) -> str:
    """
    Format number with specified decimals

    Args:
        number: Number to format
        decimals: Number of decimal places

    Returns:
        Formatted number string
    """
    return f"{number:.{decimals}f}"

def dict_to_markdown_table(data: Dict[str, Any]) -> str:
    """
    Convert dictionary to markdown table

    Args:
        data: Dictionary to convert

    Returns:
        Markdown table string
    """
    lines = ["| Key | Value |", "|-----|-------|"]

    for key, value in data.items():
        key_formatted = str(key).replace('_', ' ').title()
        value_formatted = str(value)
        lines.append(f"| {key_formatted} | {value_formatted} |")

    return "\n".join(lines)

def extract_keywords(text: str, max_keywords: int = 10) -> List[str]:
    """
    Extract keywords from text

    Args:
        text: Text to analyze
        max_keywords: Maximum number of keywords

    Returns:
        List of keywords
    """
    # Simple keyword extraction by word frequency
    words = re.findall(r'\b[a-z]{4,}\b', text.lower())

    # Common stopwords to exclude
    stopwords = {'this', 'that', 'with', 'from', 'have', 'been', 'were', 'they', 'what', 'when', 'where', 'which', 'there', 'would', 'could', 'should', 'about', 'their', 'these', 'those'}

    # Filter and count
    filtered_words = [w for w in words if w not in stopwords]
    from collections import Counter
    word_freq = Counter(filtered_words).most_common(max_keywords)

    return [word for word, count in word_freq]
