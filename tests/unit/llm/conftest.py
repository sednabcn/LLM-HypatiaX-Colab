"""LLM unit test fixtures"""

from unittest.mock import Mock, patch

import pytest


@pytest.fixture
def mock_llm_client():
    """Generic mock LLM client"""
    client = Mock()
    client.generate.return_value = "Mock response"
    return client


@pytest.fixture
def llm_test_config():
    """LLM test configuration"""
    return {"model": "test-model", "temperature": 0.7, "max_tokens": 1000}


@pytest.fixture
def mock_api_call():
    """Mock external API calls"""
    with patch("requests.post") as mock_post:
        mock_post.return_value.status_code = 200
        mock_post.return_value.json.return_value = {"result": "success"}
        yield mock_post
