"""
Data Analyzer Service
Process and analyze uploaded research data
"""

from typing import Dict, List, Any
import re
from collections import Counter

def analyze_text_data(text: str) -> Dict[str, Any]:
    """
    Analyze text data and extract insights

    Args:
        text: Text content to analyze

    Returns:
        Dictionary with analysis results
    """
    # Basic text statistics
    words = text.split()
    word_count = len(words)
    sentence_count = len(re.split(r'[.!?]+', text))

    # Common words (excluding stopwords)
    stopwords = {'the', 'a', 'an', 'and', 'or', 'but', 'in', 'on', 'at', 'to', 'for', 'of', 'with', 'by', 'from', 'as', 'is', 'was', 'are', 'were', 'been', 'be', 'have', 'has', 'had', 'do', 'does', 'did', 'will', 'would', 'could', 'should', 'may', 'might', 'must', 'can', 'this', 'that', 'these', 'those', 'i', 'you', 'he', 'she', 'it', 'we', 'they', 'what', 'which', 'who', 'when', 'where', 'why', 'how'}

    cleaned_words = [word.lower().strip('.,!?;:') for word in words if word.lower() not in stopwords and len(word) > 3]
    word_freq = Counter(cleaned_words).most_common(10)

    # Sentiment indicators (simple keyword-based)
    positive_words = {'good', 'great', 'excellent', 'love', 'happy', 'satisfied', 'easy', 'helpful', 'useful', 'amazing', 'perfect'}
    negative_words = {'bad', 'poor', 'hate', 'difficult', 'frustrating', 'confusing', 'slow', 'terrible', 'awful', 'useless', 'annoying'}

    positive_count = sum(1 for word in cleaned_words if word in positive_words)
    negative_count = sum(1 for word in cleaned_words if word in negative_words)

    sentiment = 'neutral'
    if positive_count > negative_count + 2:
        sentiment = 'positive'
    elif negative_count > positive_count + 2:
        sentiment = 'negative'

    return {
        'word_count': word_count,
        'sentence_count': sentence_count,
        'top_words': word_freq,
        'sentiment': sentiment,
        'positive_indicators': positive_count,
        'negative_indicators': negative_count
    }

def analyze_csv_data(data: List[Dict]) -> Dict[str, Any]:
    """
    Analyze CSV data

    Args:
        data: List of dictionaries from CSV

    Returns:
        Dictionary with analysis results
    """
    if not data:
        return {'error': 'No data provided'}

    row_count = len(data)
    columns = list(data[0].keys()) if data else []

    # Analyze each column
    column_analysis = {}
    for col in columns:
        values = [row.get(col, '') for row in data if row.get(col)]
        unique_values = len(set(values))

        column_analysis[col] = {
            'total_values': len(values),
            'unique_values': unique_values,
            'sample_values': values[:5]
        }

    return {
        'row_count': row_count,
        'column_count': len(columns),
        'columns': columns,
        'column_analysis': column_analysis
    }

def extract_key_themes(text: str, num_themes: int = 5) -> List[str]:
    """
    Extract key themes from text

    Args:
        text: Text to analyze
        num_themes: Number of themes to extract

    Returns:
        List of key themes
    """
    # Simple keyword extraction based on frequency
    words = text.lower().split()
    stopwords = {'the', 'a', 'an', 'and', 'or', 'but', 'in', 'on', 'at', 'to', 'for', 'of', 'with', 'by', 'from'}

    # Extract phrases (2-3 words)
    phrases = []
    for i in range(len(words) - 1):
        if words[i] not in stopwords and words[i + 1] not in stopwords:
            phrases.append(f"{words[i]} {words[i + 1]}")

    phrase_freq = Counter(phrases).most_common(num_themes)

    return [phrase for phrase, count in phrase_freq if count > 1]

def identify_pain_points(text: str) -> List[str]:
    """
    Identify pain points from text

    Args:
        text: Text to analyze

    Returns:
        List of identified pain points
    """
    pain_indicators = [
        'difficult', 'hard', 'frustrating', 'confusing', 'slow', 'complicated',
        'annoying', 'problem', 'issue', 'challenge', 'struggle', 'can\'t', 'unable',
        'doesn\'t work', 'broken', 'error', 'fail', 'wish', 'need', 'want'
    ]

    sentences = re.split(r'[.!?]+', text.lower())
    pain_points = []

    for sentence in sentences:
        if any(indicator in sentence for indicator in pain_indicators):
            pain_points.append(sentence.strip())

    return pain_points[:10]  # Return top 10
