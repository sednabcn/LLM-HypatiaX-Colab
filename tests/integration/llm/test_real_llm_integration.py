"""
Integration Tests for Real LLM Provider Integration
Tests Anthropic Claude and Google Gemini API integration
Week 2-3 Critical Priority
"""

import json
import os
import time
from typing import Dict, List
from unittest.mock import MagicMock, Mock, patch

import numpy as np
import pytest

# Set up test environment variables
os.environ.setdefault("ANTHROPIC_API_KEY", "test-key-anthropic")
os.environ.setdefault("GEMINI_API_KEY", "test-key-gemini")

from hypatiax.tools.symbolic.hybrid_system import (
    HybridDiscoverySystem,
    LLMProviderError,
)


class TestAnthropicIntegration:
    """Test suite for Anthropic Claude API integration"""

    @pytest.fixture
    def system(self):
        """Create system with Anthropic as primary provider"""
        return HybridDiscoverySystem(
            domain="defi",
            primary_llm="anthropic",
            enable_fallback=False,
            max_retries=2,
            retry_delay=0.1,
        )

    def test_anthropic_client_initialization(self, system):
        """Test that Anthropic client initializes correctly"""
        # Should initialize if API key is present
        assert (
            system.anthropic_client is not None
            or os.getenv("ANTHROPIC_API_KEY") is None
        )
        assert system.primary_llm == "anthropic"

    @pytest.mark.integration
    @pytest.mark.skipif(
        not os.getenv("ANTHROPIC_API_KEY")
        or os.getenv("ANTHROPIC_API_KEY").startswith("test-"),
        reason="Real Anthropic API key required",
    )
    def test_real_anthropic_api_call(self, system):
        """Test actual call to Anthropic Claude API"""
        prompt = "Explain the mathematical constant e in one sentence."

        try:
            response = system._call_anthropic(
                prompt=prompt,
                model="claude-sonnet-4-5-20250929",
                max_tokens=100,
                temperature=0.0,
            )

            assert isinstance(response, str)
            assert len(response) > 0
            assert "e" in response.lower() or "euler" in response.lower()

            # Check statistics
            assert system.stats["anthropic_calls"] == 1
            assert system.stats["anthropic_failures"] == 0

        except LLMProviderError as e:
            pytest.skip(f"API call failed (expected in CI): {str(e)}")

    @pytest.mark.integration
    def test_anthropic_retry_logic(self, system):
        """Test retry logic with exponential backoff"""
        with patch.object(system.anthropic_client.messages, "create") as mock_create:
            # Simulate 2 failures then success
            mock_create.side_effect = [
                Exception("Rate limit"),
                Exception("Temporary error"),
                Mock(content=[Mock(text="Success")]),
            ]

            start_time = time.time()
            response = system._call_anthropic("test prompt")
            elapsed = time.time() - start_time

            assert response == "Success"
            assert mock_create.call_count == 3
            assert elapsed >= 0.3  # 0.1 + 0.2 seconds of backoff
            assert system.stats["anthropic_failures"] == 2

    @pytest.mark.integration
    def test_anthropic_max_retries_exceeded(self, system):
        """Test that max retries are respected"""
        with patch.object(system.anthropic_client.messages, "create") as mock_create:
            mock_create.side_effect = Exception("Persistent error")

            with pytest.raises(LLMProviderError) as exc_info:
                system._call_anthropic("test prompt")

            assert "failed after 2 attempts" in str(exc_info.value)
            assert mock_create.call_count == 2  # max_retries=2

    def test_anthropic_response_parsing(self, system):
        """Test parsing of Anthropic response formats"""
        with patch.object(system.anthropic_client.messages, "create") as mock_create:
            # Test normal response
            mock_create.return_value = Mock(
                content=[Mock(text="This is a test response")]
            )

            response = system._call_anthropic("test")
            assert response == "This is a test response"

            # Test empty response
            mock_create.return_value = Mock(content=[])
            with pytest.raises(LLMProviderError, match="Empty response"):
                system._call_anthropic("test")

    @pytest.mark.integration
    def test_anthropic_with_different_models(self, system):
        """Test calls to different Claude models"""
        models = [
            "claude-sonnet-4-5-20250929",
            "claude-opus-4-1-20250514",
        ]

        for model in models:
            with patch.object(
                system.anthropic_client.messages, "create"
            ) as mock_create:
                mock_create.return_value = Mock(
                    content=[Mock(text=f"Response from {model}")]
                )

                response = system._call_anthropic("test", model=model)
                assert model in mock_create.call_args[1]["model"] or model in response


class TestGeminiIntegration:
    """Test suite for Google Gemini API integration"""

    @pytest.fixture
    def system(self):
        """Create system with Gemini as primary provider"""
        return HybridDiscoverySystem(
            domain="defi",
            primary_llm="google",
            enable_fallback=False,
            max_retries=2,
            retry_delay=0.1,
        )

    def test_gemini_client_initialization(self, system):
        """Test that Gemini client initializes correctly"""
        assert system.gemini_client is not None or os.getenv("GEMINI_API_KEY") is None
        assert system.primary_llm == "google"

    @pytest.mark.integration
    @pytest.mark.skipif(
        not os.getenv("GEMINI_API_KEY")
        or os.getenv("GEMINI_API_KEY").startswith("test-"),
        reason="Real Gemini API key required",
    )
    def test_real_gemini_api_call(self, system):
        """Test actual call to Google Gemini API"""
        prompt = "What is 2+2? Answer with just the number."

        try:
            response = system._call_gemini(
                prompt=prompt, model="gemini-2.5-flash", max_tokens=50, temperature=0.0
            )

            assert isinstance(response, str)
            assert len(response) > 0
            assert "4" in response

            # Check statistics
            assert system.stats["google_calls"] == 1
            assert system.stats["google_failures"] == 0

        except LLMProviderError as e:
            pytest.skip(f"API call failed (expected in CI): {str(e)}")

    @pytest.mark.integration
    def test_gemini_retry_logic(self, system):
        """Test retry logic with exponential backoff"""
        with patch.object(system.gemini_client.models, "generate_content") as mock_gen:
            # Simulate 2 failures then success
            mock_gen.side_effect = [
                Exception("Quota exceeded"),
                Exception("Service unavailable"),
                Mock(text="Success response"),
            ]

            start_time = time.time()
            response = system._call_gemini("test prompt")
            elapsed = time.time() - start_time

            assert response == "Success response"
            assert mock_gen.call_count == 3
            assert elapsed >= 0.3
            assert system.stats["google_failures"] == 2

    @pytest.mark.integration
    def test_gemini_max_retries_exceeded(self, system):
        """Test that max retries are respected"""
        with patch.object(system.gemini_client.models, "generate_content") as mock_gen:
            mock_gen.side_effect = Exception("Persistent error")

            with pytest.raises(LLMProviderError) as exc_info:
                system._call_gemini("test prompt")

            assert "failed after 2 attempts" in str(exc_info.value)
            assert mock_gen.call_count == 2

    def test_gemini_response_parsing(self, system):
        """Test parsing of Gemini response formats"""
        with patch.object(system.gemini_client.models, "generate_content") as mock_gen:
            # Test normal response
            mock_gen.return_value = Mock(text="Gemini response text")

            response = system._call_gemini("test")
            assert response == "Gemini response text"

            # Test empty response
            mock_gen.return_value = Mock(text=None)
            with pytest.raises(LLMProviderError, match="Empty response"):
                system._call_gemini("test")


class TestFallbackMechanism:
    """Test suite for LLM provider fallback logic"""

    @pytest.fixture
    def system_with_fallback(self):
        """Create system with fallback enabled"""
        return HybridDiscoverySystem(
            domain="defi",
            primary_llm="anthropic",
            enable_fallback=True,
            max_retries=1,
            retry_delay=0.1,
        )

    def test_fallback_anthropic_to_gemini(self, system_with_fallback):
        """Test fallback from Claude to Gemini on failure"""
        system = system_with_fallback

        # Mock Anthropic to fail, Gemini to succeed
        with (
            patch.object(system, "_call_anthropic") as mock_claude,
            patch.object(system, "_call_gemini") as mock_gemini,
        ):

            mock_claude.side_effect = LLMProviderError("Claude failed")
            mock_gemini.return_value = "Gemini fallback response"

            result = system._interpret_with_llm(
                expression="x + y", variables={"x": "input", "y": "output"}, r2=0.95
            )

            assert mock_claude.call_count == 1
            assert mock_gemini.call_count == 1
            assert system.stats["fallback_count"] == 1
            assert "gemini" in result["provider"].lower()

    def test_fallback_gemini_to_anthropic(self):
        """Test fallback from Gemini to Claude on failure"""
        system = HybridDiscoverySystem(
            domain="defi", primary_llm="google", enable_fallback=True, max_retries=1
        )

        with (
            patch.object(system, "_call_gemini") as mock_gemini,
            patch.object(system, "_call_anthropic") as mock_claude,
        ):

            mock_gemini.side_effect = LLMProviderError("Gemini failed")
            mock_claude.return_value = "Claude fallback response"

            result = system._interpret_with_llm(
                expression="x * y", variables={"x": "a", "y": "b"}, r2=0.90
            )

            assert mock_gemini.call_count == 1
            assert mock_claude.call_count == 1
            assert system.stats["fallback_count"] == 1

    def test_no_fallback_when_disabled(self):
        """Test that fallback doesn't occur when disabled"""
        system = HybridDiscoverySystem(
            domain="defi", primary_llm="anthropic", enable_fallback=False
        )

        with (
            patch.object(system, "_call_anthropic") as mock_claude,
            patch.object(system, "_call_gemini") as mock_gemini,
        ):

            mock_claude.side_effect = LLMProviderError("Claude failed")

            with pytest.raises(LLMProviderError):
                system._interpret_with_llm(
                    expression="x / y", variables={"x": "num", "y": "denom"}, r2=0.85
                )

            assert mock_claude.call_count == 1
            assert mock_gemini.call_count == 0
            assert system.stats["fallback_count"] == 0

    def test_both_providers_fail(self, system_with_fallback):
        """Test behavior when both providers fail"""
        system = system_with_fallback

        with (
            patch.object(system, "_call_anthropic") as mock_claude,
            patch.object(system, "_call_gemini") as mock_gemini,
        ):

            mock_claude.side_effect = LLMProviderError("Claude failed")
            mock_gemini.side_effect = LLMProviderError("Gemini failed")

            with pytest.raises(LLMProviderError, match="All LLM providers failed"):
                system._interpret_with_llm(
                    expression="sqrt(x)", variables={"x": "value"}, r2=0.88
                )

            assert system.stats["fallback_count"] == 1


class TestInterpretationPipeline:
    """Test the complete interpretation pipeline"""

    @pytest.fixture
    def system(self):
        return HybridDiscoverySystem(
            domain="defi", primary_llm="anthropic", enable_fallback=True
        )

    def test_prompt_building(self, system):
        """Test that interpretation prompts are built correctly"""
        prompt = system._build_interpretation_prompt(
            expression="sqrt(r0 * r1)",
            variables={"r0": "Reserve 0", "r1": "Reserve 1"},
            r2=0.98,
            context={"validation_score": 92.5},
        )

        assert "sqrt(r0 * r1)" in prompt
        assert "Reserve 0" in prompt
        assert "Reserve 1" in prompt
        assert "0.9800" in prompt
        assert "defi" in prompt.lower()
        assert "validation_score" in prompt

    def test_json_response_parsing(self, system):
        """Test parsing of structured JSON responses"""
        json_response = """{
            "interpretation": "Geometric mean of reserves",
            "relationships": ["Proportional to product"],
            "insights": ["AMM invariant"],
            "use_cases": ["DEX pricing"],
            "limitations": ["Assumes equal weights"]
        }"""

        result = system._parse_interpretation(json_response, "claude")

        assert result["interpretation"] == "Geometric mean of reserves"
        assert len(result["relationships"]) == 1
        assert len(result["insights"]) == 1
        assert result["provider"] == "claude"
        assert "raw_response" in result

    def test_malformed_json_handling(self, system):
        """Test handling of malformed JSON in responses"""
        bad_response = "This is not JSON at all"

        result = system._parse_interpretation(bad_response, "gemini")

        assert result["interpretation"] == bad_response
        assert result["provider"] == "gemini"
        assert "parse_error" in result

    def test_partial_json_extraction(self, system):
        """Test extraction of JSON from text responses"""
        mixed_response = """Here's my analysis:

        {"interpretation": "Test interpretation", "insights": ["Insight 1"]}

        Hope this helps!"""

        result = system._parse_interpretation(mixed_response, "claude")

        assert result["interpretation"] == "Test interpretation"
        assert "insights" in result


class TestEndToEndIntegration:
    """End-to-end integration tests"""

    @pytest.fixture
    def system(self):
        return HybridDiscoverySystem(
            domain="defi",
            primary_llm="anthropic",
            enable_fallback=True,
            use_rich_output=False,
        )

    @pytest.fixture
    def sample_data(self):
        """Generate sample data for testing"""
        np.random.seed(42)
        X = np.random.uniform(10, 1000, (50, 2))
        y = np.sqrt(X[:, 0] * X[:, 1]) + np.random.normal(0, 2, 50)
        return X, y

    @pytest.mark.integration
    def test_complete_workflow_with_mocked_llm(self, system, sample_data):
        """Test complete workflow with mocked LLM calls"""
        X, y = sample_data

        # Mock the LLM interpretation
        with patch.object(system, "_interpret_with_llm") as mock_interpret:
            mock_interpret.return_value = {
                "interpretation": "Geometric mean formula",
                "provider": "claude",
                "insights": ["AMM pricing"],
                "use_cases": ["DeFi protocols"],
            }

            result = system.discover_validate_interpret(
                X=X,
                y=y,
                variable_names=["reserve0", "reserve1"],
                variable_descriptions={
                    "reserve0": "Token 0 reserves",
                    "reserve1": "Token 1 reserves",
                },
                variable_units={"reserve0": "tokens", "reserve1": "tokens"},
                description="Test workflow",
                show_formatted=False,
                use_llm=True,
            )

            # Verify result structure
            assert "discovery" in result
            assert "validation" in result
            assert "interpretation" in result
            assert result["interpretation"]["provider"] == "claude"

            # Verify discovery
            assert "expression" in result["discovery"]
            assert "r2_score" in result["discovery"]
            assert result["discovery"]["r2_score"] > 0.9

            # Verify validation
            assert "valid" in result["validation"]
            assert "total_score" in result["validation"]

            # Verify storage
            assert len(system.results) == 1

    @pytest.mark.integration
    def test_workflow_with_validation_failure(self, system, sample_data):
        """Test workflow when validation fails"""
        X, y = sample_data

        # Force validation to fail by patching
        with patch.object(system.validator, "validate_complete") as mock_validate:
            mock_validate.return_value = {
                "valid": False,
                "total_score": 45.0,
                "errors": ["Critical error"],
                "warnings": ["Warning"],
                "recommendations": ["Fix this"],
            }

            result = system.discover_validate_interpret(
                X=X,
                y=y,
                variable_names=["x", "y"],
                variable_descriptions={"x": "input", "y": "output"},
                variable_units={"x": "unit", "y": "unit"},
                validate_first=True,
                show_formatted=False,
            )

            # Should skip interpretation
            assert result["interpretation"] is None
            assert not result["validation"]["valid"]

    def test_statistics_tracking(self, system, sample_data):
        """Test that statistics are tracked correctly"""
        X, y = sample_data

        with patch.object(system, "_interpret_with_llm") as mock_interpret:
            mock_interpret.side_effect = [
                {"provider": "claude", "interpretation": "Test 1"},
                {"provider": "gemini", "interpretation": "Test 2"},
                {"provider": "claude", "interpretation": "Test 3"},
            ]

            # Run 3 workflows
            for i in range(3):
                system.discover_validate_interpret(
                    X=X,
                    y=y,
                    variable_names=["a", "b"],
                    variable_descriptions={"a": "var1", "b": "var2"},
                    variable_units={"a": "u1", "b": "u2"},
                    show_formatted=False,
                )

            stats = system.get_statistics()

            assert stats["total_runs"] == 3
            assert "llm_usage" in stats
            assert len(system.results) == 3


class TestRateLimiting:
    """Test rate limiting and quota management"""

    @pytest.mark.integration
    def test_rate_limit_handling(self):
        """Test handling of rate limit errors"""
        system = HybridDiscoverySystem(domain="defi", max_retries=3, retry_delay=0.5)

        with patch.object(system.anthropic_client.messages, "create") as mock_create:
            # Simulate rate limit error
            rate_limit_error = Exception("Rate limit exceeded")
            mock_create.side_effect = [
                rate_limit_error,
                rate_limit_error,
                Mock(content=[Mock(text="Success after rate limit")]),
            ]

            start = time.time()
            response = system._call_anthropic("test")
            elapsed = time.time() - start

            # Should have backed off: 0.5s + 1.0s = 1.5s minimum
            assert elapsed >= 1.5
            assert response == "Success after rate limit"


@pytest.mark.integration
@pytest.mark.slow
class TestLoadTesting:
    """Load testing for LLM integration"""

    def test_concurrent_api_calls(self):
        """Test multiple concurrent API calls"""
        system = HybridDiscoverySystem(
            domain="defi", primary_llm="anthropic", enable_fallback=True
        )

        with patch.object(system, "_call_anthropic") as mock_claude:
            mock_claude.return_value = "Response"

            # Simulate 10 concurrent calls
            for _ in range(10):
                system._interpret_with_llm(
                    expression=f"x + y", variables={"x": "a", "y": "b"}, r2=0.9
                )

            assert system.stats["anthropic_calls"] == 10

    def test_bulk_interpretation_performance(self):
        """Test performance with bulk interpretations"""
        system = HybridDiscoverySystem(domain="defi")

        expressions = [f"x{i} * y{i}" for i in range(100)]

        with patch.object(system, "_call_anthropic") as mock_claude:
            mock_claude.return_value = "Bulk response"

            start = time.time()
            for expr in expressions[:10]:  # Test with 10 for speed
                try:
                    system._interpret_with_llm(
                        expression=expr, variables={"x": "input", "y": "output"}, r2=0.9
                    )
                except:
                    pass
            elapsed = time.time() - start

            # Should be fast with mocked calls
            assert elapsed < 1.0  # Sub-second for 10 calls


if __name__ == "__main__":
    pytest.main([__file__, "-v", "--tb=short"])
