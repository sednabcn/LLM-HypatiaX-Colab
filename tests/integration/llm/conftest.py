"""
Pytest configuration and fixtures for LLM interpretation and generation tests.
Provides fixtures for providers, interpreters, generators, and test data.
"""

import json
import os
from typing import Dict, List, Optional
from unittest.mock import MagicMock, Mock, patch

import pytest

# ============================================================================
# Provider Fixtures
# ============================================================================


@pytest.fixture
def mock_anthropic_provider():
    """Mock Anthropic API provider."""
    provider = MagicMock()
    provider.model = "claude-3-5-sonnet-20241022"
    provider.generate = MagicMock(
        return_value={
            "content": "Generated response about formulas",
            "model": "claude-3-5-sonnet-20241022",
            "usage": {"input_tokens": 50, "output_tokens": 100},
        }
    )
    return provider


@pytest.fixture
def mock_google_provider():
    """Mock Google AI provider."""
    provider = MagicMock()
    provider.model = "gemini-pro"
    provider.generate = MagicMock(
        return_value={
            "text": "Generated response",
            "usage_metadata": {"prompt_token_count": 50, "candidates_token_count": 100},
        }
    )
    return provider


@pytest.fixture
def provider_factory(mock_anthropic_provider, mock_google_provider):
    """Factory for creating provider instances."""
    factory = MagicMock()

    def create_provider(provider_type, **kwargs):
        if provider_type == "anthropic":
            return mock_anthropic_provider
        elif provider_type == "google":
            return mock_google_provider
        else:
            raise ValueError(f"Unknown provider type: {provider_type}")

    factory.create = create_provider
    return factory


@pytest.fixture
def real_anthropic_client():
    """Real Anthropic client for integration tests"""
    api_key = os.getenv("ANTHROPIC_API_KEY")
    if not api_key:
        pytest.skip("ANTHROPIC_API_KEY not set")

    from anthropic import Anthropic

    return Anthropic(api_key=api_key)


@pytest.fixture
def real_google_client():
    """Real Google client for integration tests"""
    api_key = os.getenv("GOOGLE_API_KEY")
    if not api_key:
        pytest.skip("GOOGLE_API_KEY not set")

    import google.generativeai as genai

    genai.configure(api_key=api_key)
    return genai


@pytest.fixture
def llm_integration_config():
    """Configuration for LLM integration tests"""
    return {"timeout": 30, "max_retries": 3, "backoff_factor": 2}


# ============================================================================
# Interpreter Fixtures
# ============================================================================


@pytest.fixture
def llm_interpreter(mock_anthropic_provider):
    """LLM interpreter instance."""
    interpreter = MagicMock()
    interpreter.provider = mock_anthropic_provider
    interpreter.interpret = MagicMock(return_value="Sharpe Ratio = (R - Rf) / sigma")
    interpreter.parse_response = MagicMock(
        return_value={"formula": "sharpe_ratio", "expression": "(R - Rf) / sigma", "variables": ["R", "Rf", "sigma"]}
    )
    return interpreter


@pytest.fixture
def enhanced_interpreter(llm_interpreter):
    """Enhanced interpreter with symbolic capabilities."""
    interpreter = llm_interpreter

    # Add symbolic methods
    interpreter.to_symbolic = MagicMock(return_value="symbolic_expression")
    interpreter.simplify = MagicMock(return_value="simplified_expr")
    interpreter.differentiate = MagicMock(return_value="derivative")
    interpreter.integrate_expr = MagicMock(return_value="integral")

    return interpreter


# ============================================================================
# Generator Fixtures
# ============================================================================


@pytest.fixture
def formula_generator(mock_anthropic_provider):
    """Formula generator instance."""
    generator = MagicMock()
    generator.provider = mock_anthropic_provider
    generator.generate = MagicMock(return_value="generated_formula")
    generator.validate = MagicMock(return_value=True)
    generator.get_supported_domains = MagicMock(return_value=["risk", "defi", "statistics"])
    return generator


# ============================================================================
# Test Data Fixtures
# ============================================================================


@pytest.fixture
def sample_formulas():
    """Sample formulas for testing."""
    return {
        "sharpe_ratio": {
            "name": "Sharpe Ratio",
            "formula": "(R - Rf) / sigma",
            "variables": {"R": "portfolio return", "Rf": "risk-free rate", "sigma": "volatility"},
            "domain": "risk",
        },
        "var_parametric": {
            "name": "Value at Risk (Parametric)",
            "formula": "mu - z * sigma",
            "variables": {"mu": "expected return", "z": "z-score", "sigma": "volatility"},
            "domain": "risk",
        },
        "constant_product": {
            "name": "Constant Product",
            "formula": "x * y = k",
            "variables": {"x": "token x reserves", "y": "token y reserves", "k": "constant"},
            "domain": "defi",
        },
        "impermanent_loss": {
            "name": "Impermanent Loss",
            "formula": "2 * sqrt(price_ratio) / (1 + price_ratio) - 1",
            "variables": {"price_ratio": "final_price / initial_price"},
            "domain": "defi",
        },
    }


@pytest.fixture
def sample_queries():
    """Sample queries for testing interpretation."""
    return [
        "What is the Sharpe ratio?",
        "Calculate Value at Risk",
        "Explain Uniswap constant product formula",
        "How do I calculate impermanent loss?",
        "Generate formula for portfolio variance",
        "What is the difference between Sharpe and Sortino ratio?",
    ]


@pytest.fixture
def sample_contexts():
    """Sample contexts for contextual generation."""
    return {
        "risk_management": {
            "domain": "risk",
            "previous_formulas": ["sharpe_ratio", "sortino_ratio"],
            "variables_defined": ["R", "Rf", "sigma"],
        },
        "defi_protocols": {
            "domain": "defi",
            "protocol": "uniswap_v2",
            "previous_formulas": ["constant_product"],
            "variables_defined": ["x", "y", "k"],
        },
        "portfolio_analysis": {
            "domain": "finance",
            "focus": "return_metrics",
            "previous_formulas": ["mean_return", "weighted_return"],
        },
    }


@pytest.fixture
def sample_test_cases():
    """Sample test cases for formula verification."""
    return {
        "addition": {
            "formula": "x + y",
            "tests": [
                {"input": {"x": 1, "y": 2}, "expected": 3},
                {"input": {"x": 0, "y": 0}, "expected": 0},
                {"input": {"x": -1, "y": 1}, "expected": 0},
            ],
        },
        "multiplication": {
            "formula": "x * y",
            "tests": [
                {"input": {"x": 2, "y": 3}, "expected": 6},
                {"input": {"x": 0, "y": 5}, "expected": 0},
                {"input": {"x": -2, "y": 3}, "expected": -6},
            ],
        },
        "percentage_change": {
            "formula": "(new - old) / old",
            "tests": [
                {"input": {"old": 100, "new": 110}, "expected": 0.1},
                {"input": {"old": 50, "new": 45}, "expected": -0.1},
                {"input": {"old": 100, "new": 100}, "expected": 0.0},
            ],
        },
    }


# ============================================================================
# Validation Fixtures
# ============================================================================


@pytest.fixture
def symbolic_validator():
    """Symbolic validator for formulas."""
    validator = MagicMock()
    validator.validate = MagicMock(return_value=True)
    validator.check_syntax = MagicMock(return_value=True)
    validator.check_dimensions = MagicMock(return_value=True)
    validator.extract_variables = MagicMock(return_value=["x", "y"])
    return validator


@pytest.fixture
def domain_validator():
    """Domain-specific validator."""
    validator = MagicMock()
    validator.validate_domain = MagicMock(return_value=True)
    validator.check_constraints = MagicMock(return_value=True)
    validator.get_domain_rules = MagicMock(return_value={})
    return validator


# ============================================================================
# Integration Test Fixtures
# ============================================================================


@pytest.fixture
def integration_system(llm_interpreter, formula_generator, symbolic_validator):
    """Complete integration system."""
    system = {
        "interpreter": llm_interpreter,
        "generator": formula_generator,
        "validator": symbolic_validator,
        "enabled": True,
    }
    return system


@pytest.fixture
def mock_llm_response():
    """Mock LLM response data."""
    return {
        "text": """
        The Sharpe Ratio is calculated as:

        Sharpe = (R - Rf) / σ

        Where:
        - R is the portfolio return
        - Rf is the risk-free rate
        - σ (sigma) is the portfolio volatility
        """,
        "formulas": [{"name": "Sharpe Ratio", "expression": "(R - Rf) / sigma", "variables": ["R", "Rf", "sigma"]}],
    }


# ============================================================================
# Performance Test Fixtures
# ============================================================================


@pytest.fixture
def performance_monitor():
    """Performance monitoring fixture."""
    monitor = MagicMock()
    monitor.start_timer = MagicMock()
    monitor.stop_timer = MagicMock()
    monitor.get_duration = MagicMock(return_value=0.5)
    monitor.get_memory_usage = MagicMock(return_value=100)
    return monitor


# ============================================================================
# Configuration Fixtures
# ============================================================================


@pytest.fixture
def test_config():
    """Test configuration settings."""
    return {
        "provider": {"default": "anthropic", "fallback": "google", "timeout": 30},
        "generation": {"max_tokens": 1000, "temperature": 0.7, "top_p": 0.9},
        "validation": {"enabled": True, "strict_mode": False, "check_dimensions": True},
        "caching": {"enabled": True, "ttl": 3600},
    }


@pytest.fixture
def api_keys():
    """API keys for testing (use environment variables)."""
    return {"anthropic": os.getenv("ANTHROPIC_API_KEY", "test_key"), "google": os.getenv("GOOGLE_API_KEY", "test_key")}


# ============================================================================
# Cleanup Fixtures
# ============================================================================


@pytest.fixture(autouse=True)
def cleanup():
    """Cleanup after each test."""
    yield
    # Cleanup code here if needed


# ============================================================================
# Parametrization Helpers
# ============================================================================


@pytest.fixture
def domain_parameters():
    """Parameters for domain-specific tests."""
    return [
        ("risk", "sharpe_ratio", ["R", "Rf", "sigma"]),
        ("defi", "constant_product", ["x", "y", "k"]),
        ("statistics", "mean", ["x", "n"]),
    ]


# ============================================================================
# Marker Definitions
# ============================================================================


def pytest_configure(config):
    """Register custom markers."""
    config.addinivalue_line("markers", "llm: tests that require LLM API access")
    config.addinivalue_line("markers", "slow: slow running tests")
    config.addinivalue_line("markers", "integration: integration tests")
    config.addinivalue_line("markers", "unit: unit tests")
    config.addinivalue_line("markers", "provider(name): tests for specific provider")
    config.addinivalue_line("markers", "domain(name): tests for specific domain")


# ============================================================================
# Skip Conditions
# ============================================================================


@pytest.fixture
def skip_if_no_api_key():
    """Skip test if API key not available."""

    def _skip_if_no_key(provider_name):
        key = os.getenv(f"{provider_name.upper()}_API_KEY")
        if not key:
            pytest.skip(f"No API key for {provider_name}")

    return _skip_if_no_key


# ============================================================================
# Helper Functions
# ============================================================================


@pytest.fixture
def assert_formula_valid():
    """Helper to assert formula validity."""

    def _assert_valid(formula, expected_vars=None):
        assert formula is not None
        assert len(str(formula)) > 0
        if expected_vars:
            formula_str = str(formula).lower()
            for var in expected_vars:
                assert var.lower() in formula_str

    return _assert_valid


@pytest.fixture
def compare_formulas():
    """Helper to compare formula equivalence."""

    def _compare(formula1, formula2, tolerance=1e-6):
        # Mock comparison - in real implementation would use symbolic comparison
        return str(formula1) == str(formula2)

    return _compare


# ============================================================================
# Database/Storage Fixtures (if needed)
# ============================================================================


@pytest.fixture
def formula_database():
    """Mock formula database."""
    db = MagicMock()
    db.get = MagicMock(return_value={"name": "test", "formula": "x + y"})
    db.save = MagicMock(return_value=True)
    db.search = MagicMock(return_value=[])
    return db


# ============================================================================
# Logging Fixtures
# ============================================================================


@pytest.fixture
def test_logger():
    """Test logger fixture."""
    import logging

    logger = logging.getLogger("test_logger")
    logger.setLevel(logging.DEBUG)
    return logger


# ============================================================================
# Session-scoped Fixtures
# ============================================================================


@pytest.fixture(scope="session")
def session_provider():
    """Session-scoped provider for expensive setup."""
    provider = MagicMock()
    yield provider
    # Cleanup


# ============================================================================
# Async Fixtures (if needed)
# ============================================================================


@pytest.fixture
async def async_provider():
    """Async provider fixture."""
    provider = MagicMock()
    provider.generate_async = MagicMock(return_value="async response")
    return provider
