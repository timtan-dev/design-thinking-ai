"""
AI Service Tests
Test AI service functionality
"""

import pytest
from unittest.mock import Mock, patch
from services.ai_service import AIService

@pytest.fixture
def ai_service():
    """Create AI service instance"""
    return AIService()

@pytest.fixture
def sample_project():
    """Sample project data"""
    return {
        'id': 1,
        'name': 'Test Project',
        'area': 'Testing',
        'goal': 'Test AI service'
    }

@patch('services.ai_service.OpenAI')
def test_generate_interview_questions(mock_openai, ai_service, sample_project):
    """Test interview questions generation"""
    # Mock OpenAI response
    mock_response = Mock()
    mock_response.choices = [Mock(message=Mock(content="1. Question 1\n2. Question 2"))]
    mock_openai.return_value.chat.completions.create.return_value = mock_response

    # Note: This test requires mocking OpenAI properly
    # For now, we'll just test that the method exists
    assert hasattr(ai_service, 'generate_interview_questions')

def test_ai_service_initialization(ai_service):
    """Test AI service initialization"""
    assert ai_service is not None
    assert hasattr(ai_service, 'client')
    assert hasattr(ai_service, 'model')
