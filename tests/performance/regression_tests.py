"""
HypatiaX Performance Regression Tests
Automated tests to catch performance degradation on every code change
Week 2-3: Performance Monitoring Infrastructure
"""

import json
import time
import warnings
from dataclasses import dataclass
from pathlib import Path
from typing import Any, Dict, List, Optional

import numpy as np
import pytest

# ============================================================================
# Regression Test Configuration
# ============================================================================

BASELINE_FILE = Path("tests/performance/baseline_performance.json")

# Performance baselines (in milliseconds)
# These should be updated when intentional performance improvements are made
PERFORMANCE_BASELINES = {
    "symbolic_validation": {
        "p50": 0.8,
        "p95": 1.0,
        "p99": 1.5,
        "allowed_regression": 0.2,
    },  # 20% regression allowed
    "dimensional_validation": {
        "p50": 0.3,
        "p95": 0.5,
        "p99": 0.8,
        "allowed_regression": 0.2,
    },
    "domain_validation": {
        "p50": 0.6,
        "p95": 0.8,
        "p99": 1.2,
        "allowed_regression": 0.2,
    },
    "ensemble_validation": {
        "p50": 1.5,
        "p95": 2.0,
        "p99": 3.0,
        "allowed_regression": 0.2,
    },
    "symbolic_regression_small": {
        "p50": 50.0,
        "p95": 100.0,
        "p99": 150.0,
        "allowed_regression": 0.3,  # ML operations can vary more
    },
    "end_to_end_workflow": {
        "p50": 500.0,
        "p95": 1000.0,
        "p99": 1500.0,
        "allowed_regression": 0.25,
    },
}


@dataclass
class RegressionResult:
    """Store regression test results."""

    operation: str
    current_p50: float
    current_p95: float
    current_p99: float
    baseline_p50: float
    baseline_p95: float
    baseline_p99: float
    p50_regression: float
    p95_regression: float
    p99_regression: float
    passes: bool
    message: str


class PerformanceRegressionChecker:
    """Check for performance regressions against baselines."""

    def __init__(self, baseline_file: Path = BASELINE_FILE):
        self.baseline_file = baseline_file
        self.baselines = self._load_baselines()
        self.results: List[RegressionResult] = []

    def _load_baselines(self) -> Dict[str, Dict[str, float]]:
        """Load baseline performance data."""
        if self.baseline_file.exists():
            with open(self.baseline_file) as f:
                return json.load(f)
        return PERFORMANCE_BASELINES.copy()

    def save_baselines(self, force: bool = False):
        """Save current results as new baseline."""
        if not force and self.baseline_file.exists():
            warnings.warn(
                f"Baseline file {self.baseline_file} already exists. "
                f"Use force=True to overwrite."
            )
            return

        baselines = {}
        for result in self.results:
            baselines[result.operation] = {
                "p50": result.current_p50,
                "p95": result.current_p95,
                "p99": result.current_p99,
                "allowed_regression": 0.2,
            }

        self.baseline_file.parent.mkdir(parents=True, exist_ok=True)
        with open(self.baseline_file, "w") as f:
            json.dump(baselines, f, indent=2)

        print(f"✅ Saved new baseline to {self.baseline_file}")

    def check_regression(
        self, operation: str, measurements: List[float], strict: bool = False
    ) -> RegressionResult:
        """
        Check if performance has regressed.

        Args:
            operation: Name of the operation
            measurements: List of timing measurements in ms
            strict: If True, fail on any regression

        Returns:
            RegressionResult with comparison details
        """
        # Get baseline
        baseline = self.baselines.get(operation, {})
        if not baseline:
            warnings.warn(f"No baseline for {operation}, creating one")
            baseline = {
                "p50": np.percentile(measurements, 50),
                "p95": np.percentile(measurements, 95),
                "p99": np.percentile(measurements, 99),
                "allowed_regression": 0.2,
            }

        # Calculate current performance
        current_p50 = float(np.percentile(measurements, 50))
        current_p95 = float(np.percentile(measurements, 95))
        current_p99 = float(np.percentile(measurements, 99))

        baseline_p50 = float(baseline["p50"])
        baseline_p95 = float(baseline["p95"])
        baseline_p99 = float(baseline["p99"])
        allowed_regression = baseline.get("allowed_regression", 0.2)

        # Calculate regression percentages
        p50_regression = (current_p50 - baseline_p50) / baseline_p50
        p95_regression = (current_p95 - baseline_p95) / baseline_p95
        p99_regression = (current_p99 - baseline_p99) / baseline_p99

        # Check if regression exceeds threshold
        threshold = 0.0 if strict else allowed_regression

        passes = (
            p50_regression <= threshold
            and p95_regression <= threshold
            and p99_regression <= threshold
        )

        if passes:
            if max(p50_regression, p95_regression, p99_regression) < 0:
                message = f"✅ IMPROVED: {operation} is faster than baseline"
            else:
                message = f"✅ PASS: {operation} within acceptable range"
        else:
            worst = max(p50_regression, p95_regression, p99_regression)
            message = (
                f"❌ REGRESSION: {operation} is {worst*100:.1f}% slower "
                f"(allowed: {threshold*100:.1f}%)"
            )

        result = RegressionResult(
            operation=operation,
            current_p50=current_p50,
            current_p95=current_p95,
            current_p99=current_p99,
            baseline_p50=baseline_p50,
            baseline_p95=baseline_p95,
            baseline_p99=baseline_p99,
            p50_regression=p50_regression,
            p95_regression=p95_regression,
            p99_regression=p99_regression,
            passes=passes,
            message=message,
        )

        self.results.append(result)
        return result

    def measure_and_check(
        self,
        func,
        *args,
        operation: str,
        iterations: int = 100,
        warmup: int = 5,
        strict: bool = False,
        **kwargs,
    ) -> RegressionResult:
        """
        Measure performance and check against baseline.

        Args:
            func: Function to measure
            *args: Positional arguments for func
            operation: Operation name
            iterations: Number of measurements
            warmup: Number of warmup iterations
            strict: If True, fail on any regression
            **kwargs: Keyword arguments for func

        Returns:
            RegressionResult
        """
        # Warmup
        for _ in range(warmup):
            try:
                func(*args, **kwargs)
            except Exception:
                pass

        # Measure
        measurements = []
        for _ in range(iterations):
            start = time.perf_counter()
            try:
                func(*args, **kwargs)
            except Exception:
                pass
            end = time.perf_counter()
            measurements.append((end - start) * 1000)  # Convert to ms

        return self.check_regression(operation, measurements, strict=strict)

    def print_summary(self):
        """Print summary of all regression checks."""
        # Guard clause - check if there are any results
        if not self.results:
            print("\n⚠️  No regression test results to display")
            return

        print("\n" + "=" * 80)
        print("Performance Regression Test Summary")
        print("=" * 80)

        for result in self.results:
            print(f"\n{result.message}")
            print(f"  Operation: {result.operation}")
            print(
                f"  P50: {result.current_p50:7.2f}ms (baseline: {result.baseline_p50:7.2f}ms, "
                f"Δ {result.p50_regression*100:+.1f}%)"
            )
            print(
                f"  P95: {result.current_p95:7.2f}ms (baseline: {result.baseline_p95:7.2f}ms, "
                f"Δ {result.p95_regression*100:+.1f}%)"
            )
            print(
                f"  P99: {result.current_p99:7.2f}ms (baseline: {result.baseline_p99:7.2f}ms, "
                f"Δ {result.p99_regression*100:+.1f}%)"
            )

        passed = sum(1 for r in self.results if r.passes)
        total = len(self.results)

        print("\n" + "-" * 80)

        # Additional guard for division by zero
        if total > 0:
            print(f"Results: {passed}/{total} passed ({(passed/total)*100:.1f}%)")
        else:
            print("Results: No tests recorded")

        print("=" * 80 + "\n")


# ============================================================================
# Regression Test Suite
# ============================================================================


@pytest.mark.regression
class TestValidationRegression:
    """Regression tests for validation performance."""

    @pytest.fixture(autouse=True)
    def setup(self):
        """Setup regression checker."""
        self.checker = PerformanceRegressionChecker()
        yield
        self.checker.print_summary()

        # Fail if any regressions detected
        failed = [r for r in self.checker.results if not r.passes]
        if failed:
            messages = [r.message for r in failed]
            pytest.fail(f"Performance regressions detected:\n" + "\n".join(messages))

    def test_symbolic_validation_regression(self, mock_symbolic_validator):
        """Test symbolic validation hasn't regressed."""
        expression = "x**2 + 3*x + 2"

        result = self.checker.measure_and_check(
            mock_symbolic_validator.validate,
            expression,
            operation="symbolic_validation",
            iterations=500,
        )

        print(f"\n{result.message}")

    def test_dimensional_validation_regression(self, mock_dimensional_validator):
        """Test dimensional validation hasn't regressed."""
        expression = "m * g * h"
        dimensions = {"m": "[M]", "g": "[L][T^-2]", "h": "[L]"}

        result = self.checker.measure_and_check(
            mock_dimensional_validator.validate,
            expression,
            dimensions,
            operation="dimensional_validation",
            iterations=500,
        )

        print(f"\n{result.message}")

    def test_domain_validation_regression(self, mock_domain_validator):
        """Test domain validation hasn't regressed."""
        expression = "sqrt(x*y)"
        domain = "defi"

        result = self.checker.measure_and_check(
            mock_domain_validator.validate,
            expression,
            domain,
            operation="domain_validation",
            iterations=500,
        )

        print(f"\n{result.message}")

    def test_ensemble_validation_regression(self, mock_ensemble_validator):
        """Test ensemble validation hasn't regressed."""
        expression = "x**2 + 3*x + 2"

        result = self.checker.measure_and_check(
            mock_ensemble_validator.validate,
            expression,
            operation="ensemble_validation",
            iterations=300,
        )

        print(f"\n{result.message}")


@pytest.mark.regression
class TestDataProcessingRegression:
    """Regression tests for data processing."""

    @pytest.fixture(autouse=True)
    def setup(self):
        """Setup regression checker."""
        self.checker = PerformanceRegressionChecker()
        yield
        self.checker.print_summary()

    def test_small_dataset_regression(self, simple_data):
        """Test small dataset processing hasn't regressed."""
        X, y = simple_data

        def process():
            return np.mean(X), np.std(y)

        result = self.checker.measure_and_check(
            process, operation="small_dataset_processing", iterations=2000
        )

        assert result.passes, result.message

    def test_medium_dataset_regression(self, quadratic_data):
        """Test medium dataset processing hasn't regressed."""
        X, y = quadratic_data

        def process():
            return np.corrcoef(X.flatten(), y)[0, 1]

        result = self.checker.measure_and_check(
            process, operation="medium_dataset_processing", iterations=1000
        )

        assert result.passes, result.message

    def test_large_dataset_regression(self, generate_benchmark_data):
        """Test large dataset processing hasn't regressed."""
        X, y = generate_benchmark_data(size="xlarge")

        def process():
            return np.polyfit(X.flatten(), y, deg=2)

        result = self.checker.measure_and_check(
            process, operation="large_dataset_processing", iterations=200
        )

        assert result.passes, result.message


@pytest.mark.regression
@pytest.mark.slow
class TestEndToEndRegression:
    """Regression tests for complete workflows."""

    @pytest.fixture(autouse=True)
    def setup(self):
        """Setup regression checker."""
        self.checker = PerformanceRegressionChecker()
        yield
        self.checker.print_summary()

    def test_complete_workflow_regression(
        self, mock_symbolic_engine, mock_ensemble_validator, defi_amm_data
    ):
        """Test complete discovery-validation workflow hasn't regressed."""
        X, y = defi_amm_data

        def workflow():
            # Simulate complete workflow
            mock_symbolic_engine.fit(X, y)
            predictions = mock_symbolic_engine.predict(X)
            expression = mock_symbolic_engine.get_best_expression()
            validation = mock_ensemble_validator.validate(expression)
            return predictions, validation

        result = self.checker.measure_and_check(
            workflow, operation="end_to_end_workflow", iterations=50
        )

        assert result.passes, result.message


# ============================================================================
# Comparative Regression Tests
# ============================================================================


@pytest.mark.regression
class TestComparativeRegression:
    """Compare performance across different scenarios."""

    @pytest.fixture(autouse=True)
    def setup(self):
        """Setup regression checker."""
        self.checker = PerformanceRegressionChecker()
        yield
        self.checker.print_summary()

    def test_complexity_scaling(self, mock_ensemble_validator):
        """Test that validation time scales appropriately with complexity."""
        expressions = {
            "simple": "x + 1",
            "medium": "x**2 + 3*x + 2",
            "complex": "x**3 + 2*x**2 + 3*x + 4",
            "very_complex": "sqrt(x**3 + 2*x**2) / (x + 1)",
        }

        timings = {}
        for name, expr in expressions.items():
            measurements = []
            for _ in range(100):
                start = time.perf_counter()
                mock_ensemble_validator.validate(expr)
                end = time.perf_counter()
                measurements.append((end - start) * 1000)

            timings[name] = np.median(measurements)

        # Complexity should increase time, but not excessively
        # Complex should be < 5x simple
        ratio = timings["complex"] / timings["simple"]
        assert ratio < 5.0, f"Complexity scaling too steep: {ratio:.2f}x"

        print(f"\n✅ Complexity scaling acceptable:")
        for name, time_ms in timings.items():
            print(f"  {name:15s}: {time_ms:.3f}ms")

    def test_batch_vs_single(self, mock_ensemble_validator):
        """Test batch validation vs single validation."""
        expressions = [f"x**{i} + {i}" for i in range(2, 7)]

        # Single validation
        single_times = []
        for expr in expressions:
            start = time.perf_counter()
            for _ in range(20):
                mock_ensemble_validator.validate(expr)
            end = time.perf_counter()
            single_times.append(end - start)

        total_single = sum(single_times)

        # Batch validation (simulated)
        start = time.perf_counter()
        for _ in range(20):
            for expr in expressions:
                mock_ensemble_validator.validate(expr)
        total_batch = time.perf_counter() - start

        # Batch should not be significantly slower
        # (allows some overhead but not excessive)
        ratio = total_batch / total_single
        assert ratio < 1.5, f"Batch overhead too high: {ratio:.2f}x"

        print(f"\n✅ Batch efficiency: {ratio:.2f}x overhead (acceptable)")


# ============================================================================
# Utility Functions
# ============================================================================


def update_baseline(force: bool = False):
    """Update baseline performance measurements."""
    checker = PerformanceRegressionChecker()

    print("Running performance measurements to establish new baseline...")
    # Run all regression tests to populate results
    pytest.main([__file__, "-v", "-m", "regression", "--tb=no"])

    checker.save_baselines(force=force)


if __name__ == "__main__":
    import sys

    if len(sys.argv) > 1 and sys.argv[1] == "--update-baseline":
        update_baseline(force="--force" in sys.argv)
    else:
        print(
            "Run regression tests with: pytest tests/performance/regression_tests.py -v -m regression"
        )
        print(
            "Update baseline with: python tests/performance/regression_tests.py --update-baseline"
        )
        print(
            "Force update baseline: python tests/performance/regression_tests.py --update-baseline --force"
        )
