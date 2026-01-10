"""Google/Gemini API fixtures"""

from unittest.mock import Mock

import pytest


@pytest.fixture
def google_api_key():
    """Test Google API key"""
    return "AIzaSy-test-api-key-67890"


@pytest.fixture
def gemini_mock_response():
    """Standard Gemini API response"""
    return {
        "candidates": [
            {
                "content": {
                    "parts": [{"text": "This is a test response from Gemini"}],
                    "role": "model",
                },
                "finish_reason": "STOP",
                "safety_ratings": [],
            }
        ],
        "usage_metadata": {
            "prompt_token_count": 8,
            "candidates_token_count": 15,
            "total_token_count": 23,
        },
    }


@pytest.fixture
def mock_gemini_client():
    """Mock Gemini client for testing"""
    client = Mock()

    mock_response = Mock()
    mock_response.text = "Mock Gemini response"
    mock_response.candidates = [Mock(content=Mock(parts=[Mock(text="Mock response")]))]

    client.generate_content.return_value = mock_response

    return client
