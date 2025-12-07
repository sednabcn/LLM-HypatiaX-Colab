"""Anthropic/Claude API fixtures"""

from unittest.mock import MagicMock, Mock

import pytest


@pytest.fixture
def anthropic_api_key():
    """Test Anthropic API key"""
    return "sk-ant-test-api-key-12345"


@pytest.fixture
def anthropic_mock_response():
    """Standard Anthropic API response"""
    return {
        "id": "msg_01XYZ123",
        "type": "message",
        "role": "assistant",
        "content": [{"type": "text", "text": "This is a test response from Claude"}],
        "model": "claude-sonnet-4-5-20250929",
        "stop_reason": "end_turn",
        "usage": {"input_tokens": 10, "output_tokens": 25},
    }


@pytest.fixture
def anthropic_error_response():
    """Anthropic API error response"""
    return {"type": "error", "error": {"type": "rate_limit_error", "message": "Rate limit exceeded"}}


@pytest.fixture
def anthropic_streaming_response():
    """Anthropic streaming response chunks"""
    return [
        {"type": "content_block_start", "index": 0, "content_block": {"type": "text", "text": ""}},
        {"type": "content_block_delta", "index": 0, "delta": {"type": "text_delta", "text": "Hello "}},
        {"type": "content_block_delta", "index": 0, "delta": {"type": "text_delta", "text": "world"}},
        {"type": "content_block_stop", "index": 0},
    ]


@pytest.fixture
def mock_anthropic_client():
    """Mock Anthropic client for testing"""
    client = Mock()

    # Configure mock response
    mock_message = Mock()
    mock_message.content = [Mock(type="text", text="Mock response")]
    mock_message.model = "claude-sonnet-4-5-20250929"
    mock_message.stop_reason = "end_turn"

    client.messages.create.return_value = mock_message

    return client


@pytest.fixture
def anthropic_test_prompts():
    """Common test prompts for Anthropic"""
    return {
        "simple": "What is 2+2?",
        "complex": "Explain quantum computing in simple terms",
        "creative": "Write a haiku about testing",
        "long": "Summarize the history of computer science in detail" * 10,
    }
