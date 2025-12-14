"""
HypatiaX Pytest Configuration
Provides shared fixtures, markers, and test utilities for the entire test suite
Week 2-3: Performance Monitoring Infrastructure
"""

import json
import os
import sys
import tempfile
import time
from pathlib import Path
from typing import Any, Dict, List, Tuple
from unittest.mock import MagicMock, Mock

import numpy as np
import pytest

# Add project root to path
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

# ============================================================================
# Ensure PySR uses system Julia
# ============================================================================
os.environ["JULIA_EXE"] = "/usr/bin/julia"

try:
    import pysr

    # Minimal PySRRegressor run to precompile Julia packages
    X = np.array([[0.0], [1.0]])
    y = np.array([0.0, 1.0])
    reg = pysr.PySRRegressor(niterations=1, maxsize=2)
    reg.fit(X, y)
except Exception:
    # Ignore if already precompiled or if in CI environment
    pass


# ============================================================================
# Pytest Configuration
# ============================================================================


def pytest_configure(config):
    """Configure custom markers and test settings."""
    config.addinivalue_line("markers", "slow: marks tests as slow (deselect with '-m \"not slow\"')")
    config.addinivalue_line("markers", "integration: marks tests requiring external services")
    config.addinivalue_line("markers", "performance: marks performance and benchmark tests")
    config.addinivalue_line("markers", "edge_case: marks edge case detection tests")
    config.addinivalue_line("markers", "defi: marks DeFi-specific tests")
    config.addinivalue_line("markers", "physics: marks physics domain tests")
    config.addinivalue_line("markers", "chemistry: marks chemistry domain tests")
    config.addinivalue_line("markers", "load_test: marks load and stress tests")
    config.addinivalue_line("markers", "regression: marks regression tests")


def pytest_addoption(parser):
    """Add custom command-line options."""
    parser.addoption("--run-slow", action="store_true", default=False, help="Run slow tests")
    parser.addoption(
        "--run-integration",
        action="store_true",
        default=False,
        help="Run integration tests requiring external services",
    )
    parser.addoption(
        "--run-load-tests", action="store_true", default=False, help="Run load and stress tests (1,000+ operations)"
    )
    parser.addoption(
        "--performance-threshold",
        type=float,
        default=1.0,
        help="Performance threshold in milliseconds (default: 1.0ms)",
    )
    parser.addoption(
        "--benchmark-output", type=str, default="benchmark_results.json", help="Output file for benchmark results"
    )


def pytest_collection_modifyitems(config, items):
    """Modify test collection based on command-line options."""
    skip_slow = pytest.mark.skip(reason="need --run-slow option to run")
    skip_integration = pytest.mark.skip(reason="need --run-integration option to run")
    skip_load = pytest.mark.skip(reason="need --run-load-tests option to run")

    for item in items:
        if "slow" in item.keywords and not config.getoption("--run-slow"):
            item.add_marker(skip_slow)
        if "integration" in item.keywords and not config.getoption("--run-integration"):
            item.add_marker(skip_integration)
        if "load_test" in item.keywords and not config.getoption("--run-load-tests"):
            item.add_marker(skip_load)


# ============================================================================
# Session-Level Fixtures
# ============================================================================


@pytest.fixture(scope="session")
def project_root_dir():
    """Project root directory."""
    return Path(__file__).parent.parent


@pytest.fixture(scope="session")
def performance_threshold(request):
    """Get performance threshold from command line or use default (1ms)."""
    return request.config.getoption("--performance-threshold")


@pytest.fixture(scope="session")
def benchmark_output_file(request):
    """Get benchmark output file path."""
    return Path(request.config.getoption("--benchmark-output"))


@pytest.fixture(scope="session")
def test_data_dir():
    """Create temporary directory for test data."""
    with tempfile.TemporaryDirectory() as tmpdir:
        yield Path(tmpdir)


@pytest.fixture(scope="session")
def api_keys():
    """Load API keys from environment."""
    return {
        "anthropic": os.getenv("ANTHROPIC_API_KEY", "test-key-anthropic"),
        "gemini": os.getenv("GEMINI_API_KEY", "test-key-gemini"),
    }


# ============================================================================
# Function-Level Fixtures
# ============================================================================


@pytest.fixture
def temp_dir(tmp_path):
    """Temporary directory for test files."""
    return tmp_path


@pytest.fixture
def simple_data():
    """Generate simple linear test data."""
    np.random.seed(42)
    X = np.linspace(0, 10, 50).reshape(-1, 1)
    y = 2 * X.flatten() + 1 + np.random.normal(0, 0.1, 50)
    return X, y


@pytest.fixture
def quadratic_data():
    """Generate quadratic test data."""
    np.random.seed(42)
    X = np.linspace(-5, 5, 100).reshape(-1, 1)
    y = X.flatten() ** 2 + 3 * X.flatten() + 2 + np.random.normal(0, 0.5, 100)
    return X, y


@pytest.fixture
def defi_amm_data():
    """Generate DeFi AMM test data (x*y = k)."""
    np.random.seed(42)
    k = 1000000  # Constant product
    X = np.linspace(100, 10000, 100).reshape(-1, 1)
    y = k / X.flatten() + np.random.normal(0, 1, 100)
    return X, y


@pytest.fixture
def defi_il_data():
    """Generate DeFi Impermanent Loss test data."""
    np.random.seed(42)
    # Price ratios
    r = np.linspace(0.1, 10, 100)
    # IL = sqrt(r) / ((1+r)/2) - 1
    y = np.sqrt(r) / ((1 + r) / 2) - 1
    X = r.reshape(-1, 1)
    return X, y


@pytest.fixture
def edge_case_data():
    """Generate data with edge cases."""
    return {
        "empty": (np.array([[]]), np.array([])),
        "single_point": (np.array([[1.0]]), np.array([1.0])),
        "large_numbers": (np.array([[1e10]]), np.array([1e10])),
        "zero_division": (np.array([[0.0]]), np.array([1.0])),
        "nan": (np.array([[np.nan]]), np.array([1.0])),
        "inf": (np.array([[np.inf]]), np.array([1.0])),
    }


@pytest.fixture
def mock_symbolic_engine():
    """Create mock SymbolicRegressionEngine."""
    mock_engine = MagicMock()
    mock_engine.fit.return_value = None
    mock_engine.predict.return_value = np.array([1.0, 2.0, 3.0])
    mock_engine.get_best_expression.return_value = "x**2 + 3*x + 2"
    mock_engine.get_feature_importance.return_value = {"x": 1.0}
    return mock_engine


@pytest.fixture
def mock_symbolic_validator():
    """Create mock SymbolicValidator."""
    mock = MagicMock()
    mock.validate.return_value = {"is_valid": True, "score": 90.0, "complexity": 5, "issues": []}
    return mock


@pytest.fixture
def mock_dimensional_validator():
    """Create mock DimensionalValidator."""
    mock = MagicMock()
    mock.validate.return_value = {"is_valid": True, "score": 95.0, "dimensional_consistency": True, "issues": []}
    return mock


@pytest.fixture
def mock_domain_validator():
    """Create mock DomainValidator."""
    mock = MagicMock()
    mock.validate.return_value = {
        "is_valid": True,
        "score": 88.0,
        "domain_compliance": True,
        "constraints_satisfied": True,
        "issues": [],
    }
    return mock


@pytest.fixture
def mock_ensemble_validator():
    """Create mock EnsembleValidator."""
    mock = MagicMock()
    mock.validate.return_value = {
        "is_valid": True,
        "total_score": 91.0,
        "passes_threshold": True,
        "validation_results": {},
        "issues": [],
    }
    return mock


@pytest.fixture
def mock_anthropic_client():
    """Create mock Anthropic API client."""
    mock = MagicMock()
    mock_response = MagicMock()
    mock_response.content = [MagicMock(type="text", text="This formula represents quadratic growth.")]
    mock.messages.create.return_value = mock_response
    return mock


@pytest.fixture
def mock_gemini_client():
    """Create mock Google Gemini API client."""
    mock = MagicMock()
    mock_response = MagicMock()
    mock_response.text = "This formula represents exponential decay."
    mock.generate_content.return_value = mock_response
    return mock


# ============================================================================
# Performance Monitoring Fixtures
# ============================================================================


@pytest.fixture
def timer():
    """Simple timer context manager for performance testing."""

    class Timer:
        def __init__(self):
            self.start = None
            self.end = None
            self.elapsed = None

        def __enter__(self):
            self.start = time.perf_counter()
            return self

        def __exit__(self, *args):
            self.end = time.perf_counter()
            self.elapsed = (self.end - self.start) * 1000  # Convert to ms

    return Timer


@pytest.fixture
def performance_tracker():
    """Track performance metrics across multiple operations."""

    class PerformanceTracker:
        def __init__(self):
            self.measurements = []

        def measure(self, func, *args, **kwargs):
            """Measure execution time of a function."""
            start = time.perf_counter()
            result = func(*args, **kwargs)
            end = time.perf_counter()
            elapsed_ms = (end - start) * 1000
            self.measurements.append(elapsed_ms)
            return result, elapsed_ms

        def get_stats(self):
            """Get performance statistics."""
            if not self.measurements:
                return {}
            return {
                "count": len(self.measurements),
                "mean": np.mean(self.measurements),
                "median": np.median(self.measurements),
                "std": np.std(self.measurements),
                "min": np.min(self.measurements),
                "max": np.max(self.measurements),
                "p50": np.percentile(self.measurements, 50),
                "p95": np.percentile(self.measurements, 95),
                "p99": np.percentile(self.measurements, 99),
            }

        def assert_below_threshold(self, threshold_ms):
            """Assert all measurements are below threshold."""
            stats = self.get_stats()
            assert stats["max"] < threshold_ms, f"Max time {stats['max']:.2f}ms exceeds threshold {threshold_ms}ms"

    return PerformanceTracker()


@pytest.fixture
def memory_tracker():
    """Track memory usage during tests."""
    import psutil

    class MemoryTracker:
        def __init__(self):
            self.process = psutil.Process(os.getpid())
            self.baseline = self.process.memory_info().rss / 1024 / 1024  # MB

        def current_usage(self):
            """Get current memory usage in MB."""
            return self.process.memory_info().rss / 1024 / 1024

        def usage_delta(self):
            """Get memory usage increase from baseline."""
            return self.current_usage() - self.baseline

        def assert_no_leak(self, threshold_mb=50):
            """Assert memory hasn't increased by more than threshold."""
            delta = self.usage_delta()
            assert delta < threshold_mb, f"Memory increased by {delta:.2f}MB (threshold: {threshold_mb}MB)"

    return MemoryTracker()


# ============================================================================
# Test Data Generators
# ============================================================================


@pytest.fixture
def generate_test_formulas():
    """Generate various test formulas."""

    def _generate(domain="defi", count=10):
        formulas = {
            "defi": [
                "sqrt(x*y)",  # AMM constant product
                "sqrt(r) / ((1+r)/2) - 1",  # Impermanent Loss
                "(P_t - P_0) / P_0",  # Simple return
                "x / (x + y)",  # Pool share
                "0.003 * x * y / (x + y)**2",  # Trading fee
            ],
            "physics": [
                "0.5 * m * v**2",  # Kinetic energy
                "m * g * h",  # Potential energy
                "F * d",  # Work
                "m * a",  # Force
                "G * m1 * m2 / r**2",  # Gravitational force
            ],
            "chemistry": [
                "k * [A] * [B]",  # Rate equation
                "K_eq * [A] / [B]",  # Equilibrium
                "exp(-E_a / (R*T))",  # Arrhenius
                "pH = -log10([H+])",  # pH
            ],
        }
        return formulas.get(domain, [])[:count]

    return _generate


@pytest.fixture
def generate_benchmark_data():
    """Generate data for benchmarking."""

    def _generate(size="medium", domain="defi"):
        sizes = {"tiny": 10, "small": 50, "medium": 100, "large": 500, "xlarge": 1000}
        n = sizes.get(size, 100)

        np.random.seed(42)
        if domain == "defi":
            X = np.random.uniform(100, 10000, (n, 1))
            y = 1000000 / X.flatten() + np.random.normal(0, 10, n)
        else:
            X = np.random.uniform(-10, 10, (n, 1))
            y = X.flatten() ** 2 + np.random.normal(0, 1, n)

        return X, y

    return _generate


# ============================================================================
# Cleanup Fixtures
# ============================================================================


@pytest.fixture(autouse=True)
def cleanup_after_test():
    """Cleanup after each test."""
    yield
    # Add cleanup code here if needed
    pass


@pytest.fixture(scope="session", autouse=True)
def cleanup_after_session(benchmark_output_file):
    """Cleanup after entire test session."""
    yield
    # Optionally archive old benchmark results
    if benchmark_output_file.exists():
        timestamp = time.strftime("%Y%m%d_%H%M%S")
        archive_path = benchmark_output_file.with_name(f"benchmark_results_{timestamp}.json")
        benchmark_output_file.rename(archive_path)


# ============================================================================
# Utility Functions
# ============================================================================


def assert_performance_target(elapsed_ms, target_ms, operation_name=""):
    """Assert performance meets target with helpful error message."""
    if operation_name:
        msg = f"{operation_name} took {elapsed_ms:.2f}ms (target: {target_ms}ms)"
    else:
        msg = f"Operation took {elapsed_ms:.2f}ms (target: {target_ms}ms)"

    assert elapsed_ms < target_ms, msg


def create_test_config(overrides: Dict[str, Any] = None) -> Dict[str, Any]:
    """Create test configuration with optional overrides."""
    config = {
        "validation_threshold": 85.0,
        "edge_case_penalty": 15.0,
        "dimensional_penalty": 20.0,
        "max_complexity": 10,
        "timeout_seconds": 30,
        "enable_fallback": True,
        "max_retries": 3,
    }
    if overrides:
        config.update(overrides)
    return config
