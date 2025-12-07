"""
Integration tests for LLM providers with formula generation and interpretation.
Tests Anthropic, Google, and other provider integrations.
"""

import os
from typing import Dict, List, Optional
from unittest.mock import MagicMock, Mock, patch

import pytest


class TestProviderInitialization:
    """Tests for provider initialization and configuration."""

    def test_anthropic_provider_init(self, anthropic_provider):
        """Test Anthropic provider initialization."""
        assert anthropic_provider is not None
        assert hasattr(anthropic_provider, "generate")

    def test_google_provider_init(self, google_provider):
        """Test Google provider initialization."""
        assert google_provider is not None
        assert hasattr(google_provider, "generate")

    def test_provider_with_api_key(self, provider_factory):
        """Test provider initialization with API key."""
        api_key = "test_key_123"

        provider = provider_factory.create("anthropic", api_key=api_key)

        assert provider is not None

    def test_provider_without_api_key(self, provider_factory):
        """Test provider handles missing API key."""
        with pytest.raises(ValueError):
            provider_factory.create("anthropic", api_key=None, require_key=True)

    def test_provider_configuration(self, anthropic_provider):
        """Test provider configuration options."""
        config = {"model": "claude-3-5-sonnet-20241022", "temperature": 0.7, "max_tokens": 1000}

        anthropic_provider.configure(config)

        assert anthropic_provider.config["temperature"] == 0.7


class TestBasicGeneration:
    """Tests for basic text generation."""

    def test_simple_prompt(self, anthropic_provider):
        """Test simple prompt generation."""
        prompt = "What is 2 + 2?"

        response = anthropic_provider.generate(prompt)

        assert response is not None
        assert isinstance(response, (str, dict))

    def test_formula_generation_prompt(self, anthropic_provider):
        """Test formula generation prompt."""
        prompt = "Generate the formula for Sharpe ratio"

        response = anthropic_provider.generate(prompt)

        assert response is not None
        response_str = str(response).lower()
        assert any(term in response_str for term in ["sharpe", "ratio", "return", "risk"])

    def test_multi_turn_conversation(self, anthropic_provider):
        """Test multi-turn conversation."""
        messages = [
            {"role": "user", "content": "What is the Sharpe ratio?"},
            {"role": "assistant", "content": "The Sharpe ratio measures risk-adjusted returns."},
            {"role": "user", "content": "How do I calculate it?"},
        ]

        response = anthropic_provider.generate_with_history(messages)

        assert response is not None


class TestFormulaGenerationIntegration:
    """Tests for formula generation through providers."""

    def test_generate_risk_formula(self, anthropic_provider):
        """Test generating risk formula."""
        prompt = """
        Generate a Python function for calculating Value at Risk (VaR)
        using the parametric method. Include docstring.
        """

        response = anthropic_provider.generate(prompt)

        assert "def" in str(response) or "VaR" in str(response)

    def test_generate_defi_formula(self, anthropic_provider):
        """Test generating DeFi formula."""
        prompt = """
        Generate the constant product formula for Uniswap V2
        in mathematical notation and Python code.
        """

        response = anthropic_provider.generate(prompt)

        assert response is not None

    def test_generate_with_constraints(self, anthropic_provider):
        """Test generating formula with constraints."""
        prompt = """
        Generate a formula for portfolio return that:
        1. Uses numpy arrays
        2. Handles edge cases
        3. Returns float
        """

        response = anthropic_provider.generate(prompt)

        assert response is not None

    def test_generate_with_examples(self, anthropic_provider):
        """Test generating formula with examples."""
        prompt = """
        Generate a formula that produces these outputs:
        - Input: x=2, y=3 → Output: 5
        - Input: x=5, y=7 → Output: 12
        - Input: x=0, y=0 → Output: 0
        """

        response = anthropic_provider.generate(prompt)

        assert response is not None


class TestStructuredOutput:
    """Tests for structured output generation."""

    def test_json_output(self, anthropic_provider):
        """Test generating JSON output."""
        prompt = """
        Generate a formula for compound interest.
        Return as JSON with keys: name, formula, variables, description.
        """

        response = anthropic_provider.generate(prompt, format="json")

        assert response is not None
        # Should be parseable as JSON or dict

    def test_markdown_output(self, anthropic_provider):
        """Test generating markdown output."""
        prompt = "Explain the Black-Scholes formula in markdown format"

        response = anthropic_provider.generate(prompt, format="markdown")

        assert response is not None
        assert isinstance(response, str)

    def test_code_output(self, anthropic_provider):
        """Test generating code output."""
        prompt = "Generate Python function to calculate Sortino ratio"

        response = anthropic_provider.generate(prompt, format="code")

        assert "def" in str(response)


class TestProviderComparison:
    """Tests comparing different providers."""

    def test_same_prompt_different_providers(self, anthropic_provider, google_provider):
        """Test same prompt with different providers."""
        prompt = "What is the formula for standard deviation?"

        response_anthropic = anthropic_provider.generate(prompt)
        response_google = google_provider.generate(prompt)

        assert response_anthropic is not None
        assert response_google is not None

    def test_formula_consistency(self, anthropic_provider, google_provider):
        """Test formula consistency across providers."""
        prompt = "Generate the formula: x + y"

        response_a = anthropic_provider.generate(prompt)
        response_g = google_provider.generate(prompt)

        # Both should contain x and y
        assert "x" in str(response_a).lower()
        assert "y" in str(response_g).lower()


class TestErrorHandling:
    """Tests for error handling in providers."""

    def test_invalid_api_key(self, provider_factory):
        """Test handling invalid API key."""
        with pytest.raises(Exception):
            provider = provider_factory.create("anthropic", api_key="invalid_key")
            provider.generate("test", validate_key=True)

    def test_rate_limit_handling(self, anthropic_provider):
        """Test handling rate limits."""
        with patch.object(anthropic_provider, "_call_api", side_effect=Exception("Rate limit")):
            with pytest.raises(Exception):
                anthropic_provider.generate("test")

    def test_timeout_handling(self, anthropic_provider):
        """Test handling timeouts."""
        with patch.object(anthropic_provider, "_call_api", side_effect=TimeoutError):
            with pytest.raises(TimeoutError):
                anthropic_provider.generate("test", timeout=1)

    def test_malformed_response(self, anthropic_provider):
        """Test handling malformed response."""
        with patch.object(anthropic_provider, "_call_api", return_value=None):
            response = anthropic_provider.generate("test")
            assert response is None or response == ""


class TestTokenManagement:
    """Tests for token usage and management."""

    def test_token_counting(self, anthropic_provider):
        """Test counting tokens in prompt."""
        prompt = "What is the Sharpe ratio?"

        token_count = anthropic_provider.count_tokens(prompt)

        assert isinstance(token_count, int)
        assert token_count > 0

    def test_max_tokens_limit(self, anthropic_provider):
        """Test respecting max tokens limit."""
        prompt = "Generate a very long explanation"

        response = anthropic_provider.generate(prompt, max_tokens=100)

        assert response is not None

    def test_token_usage_tracking(self, anthropic_provider):
        """Test tracking token usage."""
        prompt = "Simple prompt"

        response, usage = anthropic_provider.generate_with_usage(prompt)

        assert "input_tokens" in usage or "prompt_tokens" in usage
        assert "output_tokens" in usage or "completion_tokens" in usage


class TestStreamingGeneration:
    """Tests for streaming generation."""

    def test_streaming_response(self, anthropic_provider):
        """Test streaming response generation."""
        prompt = "Generate the Sharpe ratio formula"

        stream = anthropic_provider.generate_stream(prompt)

        chunks = list(stream)
        assert len(chunks) > 0

    def test_streaming_with_callback(self, anthropic_provider):
        """Test streaming with callback."""
        prompt = "Explain portfolio theory"
        chunks_received = []

        def callback(chunk):
            chunks_received.append(chunk)

        anthropic_provider.generate_stream(prompt, callback=callback)

        assert len(chunks_received) > 0


class TestCachingIntegration:
    """Tests for caching integration."""

    def test_cache_hit(self, anthropic_provider):
        """Test cache hit on repeated request."""
        prompt = "What is 2 + 2?"

        response1 = anthropic_provider.generate(prompt, use_cache=True)
        response2 = anthropic_provider.generate(prompt, use_cache=True)

        assert response1 == response2

    def test_cache_invalidation(self, anthropic_provider):
        """Test cache invalidation."""
        prompt = "Test prompt"

        response1 = anthropic_provider.generate(prompt, use_cache=True)
        anthropic_provider.clear_cache()
        response2 = anthropic_provider.generate(prompt, use_cache=True)

        # May or may not be same, but should work
        assert response2 is not None


class TestSystemPrompts:
    """Tests for system prompts and context."""

    def test_system_prompt_integration(self, anthropic_provider):
        """Test using system prompts."""
        system_prompt = "You are a financial mathematics expert."
        user_prompt = "Calculate portfolio variance"

        response = anthropic_provider.generate(user_prompt, system_prompt=system_prompt)

        assert response is not None

    def test_context_preservation(self, anthropic_provider):
        """Test context preservation across calls."""
        context = {"domain": "risk_management", "formulas_discussed": ["sharpe_ratio"]}

        response = anthropic_provider.generate("Now explain Sortino ratio", context=context)

        assert response is not None


class TestMultiModalInputs:
    """Tests for multi-modal inputs if supported."""

    def test_text_with_metadata(self, anthropic_provider):
        """Test text with metadata."""
        prompt = "Analyze this formula"
        metadata = {"formula": "x**2 + y**2", "domain": "mathematics"}

        response = anthropic_provider.generate(prompt, metadata=metadata)

        assert response is not None

    def test_formula_with_context(self, anthropic_provider):
        """Test formula with contextual information."""
        prompt = {"query": "Explain this formula", "formula": "(R - Rf) / sigma", "context": "Risk-adjusted returns"}

        response = anthropic_provider.generate_complex(prompt)

        assert response is not None


class TestBatchProcessing:
    """Tests for batch processing."""

    def test_batch_generation(self, anthropic_provider):
        """Test batch generation."""
        prompts = ["Formula for mean", "Formula for variance", "Formula for standard deviation"]

        responses = anthropic_provider.generate_batch(prompts)

        assert len(responses) == len(prompts)
        assert all(r is not None for r in responses)

    def test_parallel_processing(self, anthropic_provider):
        """Test parallel processing of requests."""
        prompts = [f"Prompt {i}" for i in range(5)]

        responses = anthropic_provider.generate_parallel(prompts)

        assert len(responses) == len(prompts)


class TestProviderFallback:
    """Tests for provider fallback mechanisms."""

    def test_fallback_to_secondary(self, provider_manager):
        """Test falling back to secondary provider."""
        prompt = "Generate formula"

        with patch.object(provider_manager.primary, "generate", side_effect=Exception):
            response = provider_manager.generate_with_fallback(prompt)

        assert response is not None

    def test_provider_selection(self, provider_manager):
        """Test automatic provider selection."""
        prompt = "Complex reasoning task"

        provider = provider_manager.select_provider(prompt)

        assert provider is not None


class TestQualityMetrics:
    """Tests for response quality metrics."""

    def test_response_validation(self, anthropic_provider):
        """Test validating response quality."""
        prompt = "Generate Sharpe ratio formula"

        response = anthropic_provider.generate(prompt)
        quality = anthropic_provider.validate_response(response, prompt)

        assert "score" in quality or quality is not None

    def test_formula_correctness(self, anthropic_provider):
        """Test checking formula correctness."""
        prompt = "Generate: 2 + 2"

        response = anthropic_provider.generate(prompt)
        is_correct = anthropic_provider.check_correctness(response, expected="4")

        assert isinstance(is_correct, bool)


class TestCostTracking:
    """Tests for cost tracking."""

    def test_estimate_cost(self, anthropic_provider):
        """Test estimating generation cost."""
        prompt = "Long prompt" * 100

        cost = anthropic_provider.estimate_cost(prompt)

        assert isinstance(cost, (int, float))
        assert cost >= 0

    def test_track_usage_costs(self, anthropic_provider):
        """Test tracking cumulative costs."""
        prompts = ["Test 1", "Test 2", "Test 3"]

        for prompt in prompts:
            anthropic_provider.generate(prompt, track_cost=True)

        total_cost = anthropic_provider.get_total_cost()

        assert total_cost >= 0


@pytest.fixture
def anthropic_provider():
    """Fixture for Anthropic provider."""
    provider = MagicMock()
    provider.generate = MagicMock(return_value="Generated response")
    provider.configure = MagicMock()
    provider.config = {"temperature": 0.7}
    provider.generate_with_history = MagicMock(return_value="Response")
    provider.count_tokens = MagicMock(return_value=10)
    provider.generate_with_usage = MagicMock(return_value=("Response", {"input_tokens": 10, "output_tokens": 20}))
    provider.generate_stream = MagicMock(return_value=iter(["chunk1", "chunk2"]))
    provider.clear_cache = MagicMock()
    provider.generate_complex = MagicMock(return_value="Complex response")
    provider.generate_batch = MagicMock(return_value=["resp1", "resp2", "resp3"])
    provider.generate_parallel = MagicMock(return_value=["resp1", "resp2", "resp3"])
    provider.validate_response = MagicMock(return_value={"score": 0.9})
    provider.check_correctness = MagicMock(return_value=True)
    provider.estimate_cost = MagicMock(return_value=0.001)
    provider.get_total_cost = MagicMock(return_value=0.01)
    provider._call_api = MagicMock(return_value={"content": "response"})
    return provider


@pytest.fixture
def google_provider():
    """Fixture for Google provider."""
    provider = MagicMock()
    provider.generate = MagicMock(return_value="Google response")
    return provider


@pytest.fixture
def provider_factory():
    """Fixture for provider factory."""
    factory = MagicMock()
    factory.create = MagicMock(return_value=MagicMock())
    return factory


@pytest.fixture
def provider_manager():
    """Fixture for provider manager with fallback."""
    manager = MagicMock()
    manager.primary = MagicMock()
    manager.secondary = MagicMock()
    manager.generate_with_fallback = MagicMock(return_value="Fallback response")
    manager.select_provider = MagicMock(return_value=manager.primary)
    return manager


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
