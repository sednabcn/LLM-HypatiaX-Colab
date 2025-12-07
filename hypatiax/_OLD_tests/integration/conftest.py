"""
Pytest Configuration for HypatiaX Integration Tests
Provides shared fixtures, markers, and test utilities
"""

import os
import sys
from pathlib import Path
from unittest.mock import MagicMock, Mock

import numpy as np
import pytest

# Add project root to path
project_root = Path(__file__).parent.parent.parent
sys.path.insert(0, str(project_root))


# ============================================================================
# MARKERS
# ============================================================================


def pytest_configure(config):
    """Register custom markers"""
    config.addinivalue_line("markers", "integration: Real API integration tests (requires API keys)")
    config.addinivalue_line("markers", "slow: Tests that take more than 10 seconds")
    config.addinivalue_line("markers", "benchmark: Performance benchmark tests")
    config.addinivalue_line("markers", "unit: Fast unit tests")
    config.addinivalue_line("markers", "e2e: End-to-end workflow tests")


# ============================================================================
# FIXTURES - TEST DATA
# ============================================================================


@pytest.fixture
def sample_data_small():
    """Small dataset for quick tests (50 samples)"""
    np.random.seed(42)
    n = 50
    X = np.random.uniform(1, 100, (n, 2))
    y = X[:, 0] + X[:, 1] + np.random.normal(0, 1, n)
    return X, y


@pytest.fixture
def sample_data_medium():
    """Medium dataset for standard tests (200 samples)"""
    np.random.seed(123)
    n = 200
    X = np.random.uniform(1, 100, (n, 3))
    y = X[:, 0] * X[:, 1] + X[:, 2] + np.random.normal(0, 5, n)
    return X, y


@pytest.fixture
def sample_data_large():
    """Large dataset for performance tests (1000 samples)"""
    np.random.seed(456)
    n = 1000
    X = np.random.uniform(1, 1000, (n, 4))
    y = np.sqrt(X[:, 0] * X[:, 1]) + X[:, 2] / (X[:, 3] + 1)
    y += np.random.normal(0, 10, n)
    return X, y


@pytest.fixture
def defi_amm_data():
    """DeFi AMM constant product data"""
    np.random.seed(789)
    n = 200
    reserve0 = np.random.uniform(100, 10000, n)
    reserve1 = np.random.uniform(100, 10000, n)
    k = reserve0 * reserve1
    y = k + np.random.normal(0, k * 0.01, n)
    return np.column_stack([reserve0, reserve1]), y


@pytest.fixture
def defi_il_data():
    """DeFi impermanent loss data"""
    np.random.seed(101)
    n = 200
    price_ratio = np.random.uniform(0.1, 10.0, n)
    il = 2 * np.sqrt(price_ratio) / (1 + price_ratio) - 1
    y = il + np.random.normal(0, 0.01, n)
    return price_ratio.reshape(-1, 1), y


# ============================================================================
# FIXTURES - SYSTEM CONFIGURATIONS
# ============================================================================


@pytest.fixture
def basic_system():
    """Basic HybridDiscoverySystem for testing"""
    from hypatiax.tools.symbolic.hybrid_system import HybridDiscoverySystem

    return HybridDiscoverySystem(
        domain="defi", primary_llm="anthropic", enable_fallback=True, use_rich_output=False, max_results=100
    )


@pytest.fixture
def system_anthropic_only():
    """System with only Anthropic provider"""
    from hypatiax.tools.symbolic.hybrid_system import HybridDiscoverySystem

    return HybridDiscoverySystem(domain="defi", primary_llm="anthropic", enable_fallback=False, use_rich_output=False)


@pytest.fixture
def system_gemini_only():
    """System with only Gemini provider"""
    from hypatiax.tools.symbolic.hybrid_system import HybridDiscoverySystem

    return HybridDiscoverySystem(domain="defi", primary_llm="google", enable_fallback=False, use_rich_output=False)


@pytest.fixture
def system_with_fallback():
    """System with fallback enabled"""
    from hypatiax.tools.symbolic.hybrid_system import HybridDiscoverySystem

    return HybridDiscoverySystem(
        domain="defi",
        primary_llm="anthropic",
        enable_fallback=True,
        max_retries=2,
        retry_delay=0.1,
        use_rich_output=False,
    )


# ============================================================================
# FIXTURES - MOCKED LLM RESPONSES
# ============================================================================


@pytest.fixture
def mock_claude_response():
    """Standard mock response for Claude API"""
    return Mock(content=[Mock(text='{"interpretation": "Test interpretation", "provider": "claude"}')])


@pytest.fixture
def mock_gemini_response():
    """Standard mock response for Gemini API"""
    return Mock(text='{"interpretation": "Test interpretation", "provider": "gemini"}')


@pytest.fixture
def mock_interpretation_response():
    """Standard interpretation response"""
    return {
        "interpretation": "This formula calculates a mathematical relationship",
        "provider": "claude",
        "relationships": ["Variable x affects output linearly"],
        "insights": ["Strong correlation observed"],
        "use_cases": ["Predictive modeling", "Data analysis"],
        "limitations": ["Assumes linear relationship"],
    }


# ============================================================================
# FIXTURES - API CLIENT MOCKS
# ============================================================================


@pytest.fixture
def mock_anthropic_client():
    """Mocked Anthropic client"""
    client = MagicMock()
    client.messages.create.return_value = Mock(content=[Mock(text="Mocked Claude response")])
    return client


@pytest.fixture
def mock_gemini_client():
    """Mocked Gemini client"""
    client = MagicMock()
    client.models.generate_content.return_value = Mock(text="Mocked Gemini response")
    return client


# ============================================================================
# FIXTURES - ENVIRONMENT SETUP
# ============================================================================


@pytest.fixture(autouse=True)
def setup_test_env():
    """Set up test environment variables"""
    # Save original values
    original_env = {}
    test_keys = ["ANTHROPIC_API_KEY", "GEMINI_API_KEY", "GOOGLE_API_KEY"]

    for key in test_keys:
        original_env[key] = os.environ.get(key)

    # Set test values if not already set
    if not os.environ.get("ANTHROPIC_API_KEY"):
        os.environ["ANTHROPIC_API_KEY"] = "test-anthropic-key"
    if not os.environ.get("GEMINI_API_KEY"):
        os.environ["GEMINI_API_KEY"] = "test-gemini-key"

    yield

    # Restore original values
    for key, value in original_env.items():
        if value is None:
            os.environ.pop(key, None)
        else:
            os.environ[key] = value


@pytest.fixture
def clean_environment():
    """Clean environment (no API keys set)"""
    original_keys = {
        "ANTHROPIC_API_KEY": os.environ.get("ANTHROPIC_API_KEY"),
        "GEMINI_API_KEY": os.environ.get("GEMINI_API_KEY"),
        "GOOGLE_API_KEY": os.environ.get("GOOGLE_API_KEY"),
    }

    # Remove all API keys
    for key in original_keys:
        os.environ.pop(key, None)

    yield

    # Restore
    for key, value in original_keys.items():
        if value is not None:
            os.environ[key] = value


# ============================================================================
# FIXTURES - TEMPORARY FILES
# ============================================================================


@pytest.fixture
def temp_output_dir(tmp_path):
    """Temporary directory for test output"""
    output_dir = tmp_path / "test_output"
    output_dir.mkdir()
    return output_dir


@pytest.fixture
def temp_export_file(tmp_path):
    """Temporary file for export tests"""
    return tmp_path / "test_export.json"


# ============================================================================
# HELPER FUNCTIONS
# ============================================================================


def has_real_api_key(provider="anthropic"):
    """Check if real API key is available"""
    if provider == "anthropic":
        key = os.environ.get("ANTHROPIC_API_KEY", "")
        return key and not key.startswith("test-")
    elif provider == "gemini" or provider == "google":
        key = os.environ.get("GEMINI_API_KEY", "") or os.environ.get("GOOGLE_API_KEY", "")
        return key and not key.startswith("test-")
    return False


def skip_without_api_key(provider="anthropic"):
    """Decorator to skip tests without real API key"""
    reason = f"Real {provider.capitalize()} API key required"
    return pytest.mark.skipif(not has_real_api_key(provider), reason=reason)


# ============================================================================
# TEST UTILITIES
# ============================================================================


class TestMetrics:
    """Helper class for tracking test metrics"""

    def __init__(self):
        self.latencies = []
        self.errors = []
        self.success_count = 0
        self.failure_count = 0

    def record_success(self, latency=None):
        """Record a successful operation"""
        self.success_count += 1
        if latency is not None:
            self.latencies.append(latency)

    def record_failure(self, error):
        """Record a failed operation"""
        self.failure_count += 1
        self.errors.append(str(error))

    def get_stats(self):
        """Get summary statistics"""
        import statistics

        stats = {
            "success_count": self.success_count,
            "failure_count": self.failure_count,
            "total_count": self.success_count + self.failure_count,
            "success_rate": self.success_count / max(1, self.success_count + self.failure_count),
        }

        if self.latencies:
            stats.update(
                {
                    "avg_latency": statistics.mean(self.latencies),
                    "median_latency": statistics.median(self.latencies),
                    "min_latency": min(self.latencies),
                    "max_latency": max(self.latencies),
                }
            )

        return stats


@pytest.fixture
def test_metrics():
    """Fixture providing TestMetrics instance"""
    return TestMetrics()


# ============================================================================
# PYTEST HOOKS
# ============================================================================


def pytest_collection_modifyitems(config, items):
    """Modify test collection"""
    # Add 'unit' marker to tests without other markers
    for item in items:
        if not any(mark.name in ["integration", "slow", "benchmark", "e2e"] for mark in item.iter_markers()):
            item.add_marker(pytest.mark.unit)


def pytest_runtest_setup(item):
    """Setup for each test"""
    # Skip integration tests if no API keys available (unless explicitly running them)
    if "integration" in [mark.name for mark in item.iter_markers()]:
        if not has_real_api_key("anthropic") and not has_real_api_key("gemini"):
            # Check if user explicitly wants to run integration tests
            if not item.config.getoption("-m") or "integration" not in item.config.getoption("-m"):
                pytest.skip("Integration tests require real API keys")


@pytest.hookimpl(tryfirst=True, hookwrapper=True)
def pytest_runtest_makereport(item, call):
    """Make test results available to fixtures"""
    outcome = yield
    rep = outcome.get_result()

    # Store test results for cleanup/logging
    setattr(item, f"rep_{rep.when}", rep)


def pytest_terminal_summary(terminalreporter, exitstatus, config):
    """Add custom summary information"""
    # Count tests by marker
    passed = len(terminalreporter.stats.get("passed", []))
    failed = len(terminalreporter.stats.get("failed", []))
    skipped = len(terminalreporter.stats.get("skipped", []))

    terminalreporter.write_sep("=", "HypatiaX Integration Test Summary")
    terminalreporter.write_line(f"Total Passed: {passed}")
    terminalreporter.write_line(f"Total Failed: {failed}")
    terminalreporter.write_line(f"Total Skipped: {skipped}")

    # Check API key availability
    has_anthropic = has_real_api_key("anthropic")
    has_gemini = has_real_api_key("gemini")

    terminalreporter.write_sep("-", "API Configuration")
    terminalreporter.write_line(f"Anthropic API: {'✓ Available' if has_anthropic else '✗ Not configured'}")
    terminalreporter.write_line(f"Gemini API: {'✓ Available' if has_gemini else '✗ Not configured'}")

    if not has_anthropic and not has_gemini:
        terminalreporter.write_line("\n⚠ Warning: No real API keys configured. Integration tests will be skipped.")
        terminalreporter.write_line("Set ANTHROPIC_API_KEY or GEMINI_API_KEY to run real API tests.")


# ============================================================================
# COMMAND LINE OPTIONS
# ============================================================================


def pytest_addoption(parser):
    """Add custom command line options"""
    parser.addoption("--run-slow", action="store_true", default=False, help="Run slow tests")
    parser.addoption(
        "--run-integration", action="store_true", default=False, help="Run integration tests (requires API keys)"
    )
    parser.addoption("--run-load-tests", action="store_true", default=False, help="Run load tests (1,000+ operations)")


def pytest_collection_modifyitems(config, items):
    """Modify test collection based on command line options"""
    run_slow = config.getoption("--run-slow")
    run_integration = config.getoption("--run-integration")
    run_load = config.getoption("--run-load-tests")

    skip_slow = pytest.mark.skip(reason="Use --run-slow to run slow tests")
    skip_integration = pytest.mark.skip(reason="Use --run-integration to run integration tests")
    skip_load = pytest.mark.skip(reason="Use --run-load-tests to run load tests")

    for item in items:
        # Skip slow tests unless requested
        if "slow" in item.keywords and not run_slow:
            item.add_marker(skip_slow)

        # Skip integration tests unless requested or API keys available
        if "integration" in item.keywords and not run_integration:
            if not has_real_api_key("anthropic") and not has_real_api_key("gemini"):
                item.add_marker(skip_integration)

        # Skip load tests unless requested
        if "TestLoadTests" in str(item.nodeid) and not run_load:
            item.add_marker(skip_load)
