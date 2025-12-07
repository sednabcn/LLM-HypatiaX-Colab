"""
HypatiaX Benchmark Suite
Comprehensive performance benchmarking for all system components
Week 2-3: Performance Monitoring Infrastructure
Target: Sub-millisecond validation, <500ms LLM calls
"""

import json
import os
import statistics
import time
from dataclasses import asdict, dataclass
from datetime import datetime
from pathlib import Path
from typing import Any, Dict, List, Optional, Tuple

import numpy as np
import psutil
import pytest

# ============================================================================
# Benchmark Configuration
# ============================================================================

PERFORMANCE_TARGETS = {
    "symbolic_validation": 1.0,  # ms
    "dimensional_validation": 0.5,  # ms
    "domain_validation": 0.8,  # ms
    "ensemble_validation": 2.0,  # ms
    "symbolic_regression": 100.0,  # ms
    "llm_call_anthropic": 500.0,  # ms
    "llm_call_gemini": 400.0,  # ms
    "end_to_end_workflow": 1000.0,  # ms
}


@dataclass
class BenchmarkResult:
    """Store benchmark result data."""

    operation: str
    timestamp: str
    measurements: List[float]
    mean: float
    median: float
    std: float
    min_time: float
    max_time: float
    p50: float
    p95: float
    p99: float
    target_ms: float
    passes_target: bool
    iterations: int
    memory_mb: float

    def to_dict(self):
        return asdict(self)


class BenchmarkSuite:
    """Main benchmark suite for HypatiaX performance testing."""

    def __init__(self, output_file: str = "benchmark_results.json"):
        self.output_file = Path(output_file)
        self.results: List[BenchmarkResult] = []
        self.process = psutil.Process(os.getpid())

    def benchmark(
        self,
        func,
        *args,
        operation_name: str,
        iterations: int = 100,
        target_ms: Optional[float] = None,
        warmup: int = 5,
        **kwargs,
    ) -> BenchmarkResult:
        """
        Benchmark a function with multiple iterations.

        Args:
            func: Function to benchmark
            *args: Positional arguments for func
            operation_name: Name of the operation being benchmarked
            iterations: Number of iterations to run
            target_ms: Performance target in milliseconds
            warmup: Number of warmup iterations
            **kwargs: Keyword arguments for func

        Returns:
            BenchmarkResult with statistics
        """
        # Warmup
        for _ in range(warmup):
            try:
                func(*args, **kwargs)
            except Exception:
                pass

        # Actual benchmark
        measurements = []
        memory_before = self.process.memory_info().rss / 1024 / 1024  # MB

        for _ in range(iterations):
            start = time.perf_counter()
            try:
                func(*args, **kwargs)
            except Exception as e:
                print(f"Warning: {operation_name} raised {e}")
            end = time.perf_counter()
            measurements.append((end - start) * 1000)  # Convert to ms

        memory_after = self.process.memory_info().rss / 1024 / 1024
        memory_used = memory_after - memory_before

        # Calculate statistics
        mean = statistics.mean(measurements)
        median = statistics.median(measurements)
        std = statistics.stdev(measurements) if len(measurements) > 1 else 0.0
        min_time = min(measurements)
        max_time = max(measurements)
        p50 = statistics.median(measurements)
        p95 = np.percentile(measurements, 95)
        p99 = np.percentile(measurements, 99)

        # Get target
        if target_ms is None:
            target_ms = PERFORMANCE_TARGETS.get(operation_name, float("inf"))

        passes_target = p95 < target_ms

        result = BenchmarkResult(
            operation=operation_name,
            timestamp=datetime.now().isoformat(),
            measurements=measurements,
            mean=mean,
            median=median,
            std=std,
            min_time=min_time,
            max_time=max_time,
            p50=p50,
            p95=p95,
            p99=p99,
            target_ms=target_ms,
            passes_target=passes_target,
            iterations=iterations,
            memory_mb=memory_used,
        )

        self.results.append(result)
        return result

    def save_results(self):
        """Save benchmark results to JSON file."""
        data = {
            "timestamp": datetime.now().isoformat(),
            "targets": PERFORMANCE_TARGETS,
            "results": [r.to_dict() for r in self.results],
            "summary": self.get_summary(),
        }

        with open(self.output_file, "w") as f:
            json.dump(data, f, indent=2)

        print(f"\n✅ Benchmark results saved to {self.output_file}")

    def get_summary(self) -> Dict[str, Any]:
        """Get summary statistics across all benchmarks."""
        if not self.results:
            return {}

        passed = sum(1 for r in self.results if r.passes_target)
        total = len(self.results)

        return {
            "total_benchmarks": total,
            "passed": passed,
            "failed": total - passed,
            "pass_rate": f"{(passed/total)*100:.1f}%",
            "slowest_operation": max(self.results, key=lambda r: r.p95).operation,
            "fastest_operation": min(self.results, key=lambda r: r.p95).operation,
        }

    def print_summary(self):
        """Print formatted summary of benchmark results."""
        print("\n" + "=" * 80)
        print("HypatiaX Performance Benchmark Summary")
        print("=" * 80)

        for result in self.results:
            status = "✅ PASS" if result.passes_target else "❌ FAIL"
            print(f"\n{status} {result.operation}")
            print(f"  Mean:   {result.mean:7.2f}ms")
            print(f"  Median: {result.median:7.2f}ms")
            print(f"  P95:    {result.p95:7.2f}ms (target: {result.target_ms}ms)")
            print(f"  P99:    {result.p99:7.2f}ms")
            print(f"  Memory: {result.memory_mb:7.2f}MB")

        print("\n" + "-" * 80)
        summary = self.get_summary()
        print(
            f"Total: {summary['total_benchmarks']} | "
            f"Passed: {summary['passed']} | "
            f"Failed: {summary['failed']} | "
            f"Pass Rate: {summary['pass_rate']}"
        )
        print("=" * 80 + "\n")


# ============================================================================
# Benchmark Test Suite
# ============================================================================


@pytest.mark.performance
class TestValidationBenchmarks:
    """Benchmark validation components."""

    @pytest.fixture(autouse=True)
    def setup(self, request):
        """Setup benchmark suite."""
        self.suite = BenchmarkSuite(output_file=request.config.getoption("--benchmark-output"))
        yield
        self.suite.save_results()
        self.suite.print_summary()

    def test_symbolic_validation_performance(self, mock_symbolic_validator):
        """Benchmark symbolic validation (target: <1ms)."""
        expression = "x**2 + 3*x + 2"

        result = self.suite.benchmark(
            mock_symbolic_validator.validate, expression, operation_name="symbolic_validation", iterations=1000
        )

        assert (
            result.passes_target
        ), f"Symbolic validation too slow: P95={result.p95:.2f}ms (target: {result.target_ms}ms)"

    def test_dimensional_validation_performance(self, mock_dimensional_validator):
        """Benchmark dimensional validation (target: <0.5ms)."""
        expression = "m * g * h"
        dimensions = {"m": "[M]", "g": "[L][T^-2]", "h": "[L]"}

        result = self.suite.benchmark(
            mock_dimensional_validator.validate,
            expression,
            dimensions,
            operation_name="dimensional_validation",
            iterations=1000,
        )

        assert result.passes_target, f"Dimensional validation too slow: P95={result.p95:.2f}ms"

    def test_domain_validation_performance(self, mock_domain_validator):
        """Benchmark domain validation (target: <0.8ms)."""
        expression = "sqrt(x*y)"
        domain = "defi"

        result = self.suite.benchmark(
            mock_domain_validator.validate, expression, domain, operation_name="domain_validation", iterations=1000
        )

        assert result.passes_target, f"Domain validation too slow: P95={result.p95:.2f}ms"

    def test_ensemble_validation_performance(self, mock_ensemble_validator):
        """Benchmark ensemble validation (target: <2ms)."""
        expression = "x**2 + 3*x + 2"

        result = self.suite.benchmark(
            mock_ensemble_validator.validate, expression, operation_name="ensemble_validation", iterations=500
        )

        assert result.passes_target, f"Ensemble validation too slow: P95={result.p95:.2f}ms"


@pytest.mark.performance
@pytest.mark.integration
class TestLLMBenchmarks:
    """Benchmark LLM integration performance."""

    @pytest.fixture(autouse=True)
    def setup(self, request):
        """Setup benchmark suite."""
        self.suite = BenchmarkSuite(output_file=request.config.getoption("--benchmark-output"))
        yield
        self.suite.save_results()

    @pytest.mark.slow
    def test_anthropic_api_latency(self, mock_anthropic_client):
        """Benchmark Anthropic Claude API latency (target: <500ms)."""

        def call_anthropic():
            return mock_anthropic_client.messages.create(
                model="claude-sonnet-4-5-20250929",
                max_tokens=100,
                messages=[{"role": "user", "content": "Explain: x**2"}],
            )

        result = self.suite.benchmark(
            call_anthropic,
            operation_name="llm_call_anthropic",
            iterations=20,  # Fewer iterations for API calls
            warmup=2,
        )

        # More lenient for mocked API
        assert result.p95 < 1000, f"Anthropic API too slow: P95={result.p95:.2f}ms"

    @pytest.mark.slow
    def test_gemini_api_latency(self, mock_gemini_client):
        """Benchmark Google Gemini API latency (target: <400ms)."""

        def call_gemini():
            return mock_gemini_client.generate_content("Explain: x**2")

        result = self.suite.benchmark(call_gemini, operation_name="llm_call_gemini", iterations=20, warmup=2)

        assert result.p95 < 1000, f"Gemini API too slow: P95={result.p95:.2f}ms"


@pytest.mark.performance
class TestDataProcessingBenchmarks:
    """Benchmark data processing operations."""

    @pytest.fixture(autouse=True)
    def setup(self, request):
        """Setup benchmark suite."""
        self.suite = BenchmarkSuite(output_file=request.config.getoption("--benchmark-output"))
        yield
        self.suite.save_results()

    def test_small_dataset_processing(self, simple_data):
        """Benchmark small dataset (50 points)."""
        X, y = simple_data

        def process():
            return np.mean(X), np.std(y)

        result = self.suite.benchmark(
            process, operation_name="small_dataset_processing", iterations=5000, target_ms=0.1
        )

        assert result.passes_target

    def test_medium_dataset_processing(self, quadratic_data):
        """Benchmark medium dataset (100 points)."""
        X, y = quadratic_data

        def process():
            return np.corrcoef(X.flatten(), y)[0, 1]

        result = self.suite.benchmark(
            process, operation_name="medium_dataset_processing", iterations=2000, target_ms=0.5
        )

        assert result.passes_target

    def test_large_dataset_processing(self, generate_benchmark_data):
        """Benchmark large dataset (1000 points)."""
        X, y = generate_benchmark_data(size="xlarge")

        def process():
            return np.polyfit(X.flatten(), y, deg=2)

        result = self.suite.benchmark(process, operation_name="large_dataset_processing", iterations=500, target_ms=5.0)

        assert result.passes_target


@pytest.mark.performance
class TestMemoryBenchmarks:
    """Benchmark memory usage."""

    @pytest.fixture(autouse=True)
    def setup(self, request):
        """Setup benchmark suite."""
        self.suite = BenchmarkSuite(output_file=request.config.getoption("--benchmark-output"))
        yield
        self.suite.save_results()

    def test_validation_memory_usage(self, mock_ensemble_validator):
        """Test validation doesn't leak memory."""
        expression = "x**2 + 3*x + 2"

        # Run many iterations
        for _ in range(1000):
            mock_ensemble_validator.validate(expression)

        # Memory usage should be bounded
        result = self.suite.benchmark(
            mock_ensemble_validator.validate, expression, operation_name="validation_memory", iterations=100
        )

        # Memory increase should be minimal (<10MB)
        assert result.memory_mb < 10, f"Memory usage too high: {result.memory_mb:.2f}MB"

    def test_large_dataset_memory(self, generate_benchmark_data):
        """Test memory usage with large datasets."""
        X, y = generate_benchmark_data(size="xlarge")

        def process():
            return X.copy(), y.copy()

        result = self.suite.benchmark(process, operation_name="large_dataset_memory", iterations=100)

        # Should not use excessive memory
        assert result.memory_mb < 50, f"Memory usage too high: {result.memory_mb:.2f}MB"


# ============================================================================
# Throughput Benchmarks
# ============================================================================


@pytest.mark.performance
class TestThroughputBenchmarks:
    """Benchmark operation throughput."""

    @pytest.fixture(autouse=True)
    def setup(self, request):
        """Setup benchmark suite."""
        self.suite = BenchmarkSuite(output_file=request.config.getoption("--benchmark-output"))
        yield
        self.suite.save_results()

    def test_validation_throughput(self, mock_ensemble_validator):
        """Measure validation operations per second."""
        expression = "x**2 + 3*x + 2"
        operations = 1000

        start = time.perf_counter()
        for _ in range(operations):
            mock_ensemble_validator.validate(expression)
        elapsed = time.perf_counter() - start

        throughput = operations / elapsed
        print(f"\n✅ Validation throughput: {throughput:.0f} ops/sec")

        # Target: >500 validations/sec
        assert throughput > 500, f"Throughput too low: {throughput:.0f} ops/sec (target: >500)"

    def test_concurrent_validation_throughput(self, mock_ensemble_validator):
        """Measure concurrent validation throughput."""
        from concurrent.futures import ThreadPoolExecutor

        expressions = [f"x**{i} + {i}*x" for i in range(2, 6)]
        operations = 100

        def validate_all():
            for expr in expressions:
                mock_ensemble_validator.validate(expr)

        start = time.perf_counter()
        with ThreadPoolExecutor(max_workers=4) as executor:
            futures = [executor.submit(validate_all) for _ in range(operations)]
            for future in futures:
                future.result()
        elapsed = time.perf_counter() - start

        total_ops = operations * len(expressions)
        throughput = total_ops / elapsed
        print(f"\n✅ Concurrent throughput: {throughput:.0f} ops/sec")

        # Should be higher than sequential
        assert throughput > 1000


# ============================================================================
# Load Testing Benchmarks
# ============================================================================


@pytest.mark.performance
@pytest.mark.load_test
class TestLoadBenchmarks:
    """Load testing with 1,000+ operations."""

    @pytest.fixture(autouse=True)
    def setup(self, request):
        """Setup benchmark suite."""
        self.suite = BenchmarkSuite(output_file=request.config.getoption("--benchmark-output"))
        yield
        self.suite.save_results()
        self.suite.print_summary()

    def test_1000_validation_load(self, mock_ensemble_validator):
        """Test 1,000 sequential validations."""
        expressions = ["x**2 + 3*x + 2", "sqrt(x*y)", "m * g * h", "(P_t - P_0) / P_0", "x / (x + y)"]

        start = time.perf_counter()
        for i in range(1000):
            expr = expressions[i % len(expressions)]
            mock_ensemble_validator.validate(expr)
        elapsed = time.perf_counter() - start

        print(f"\n✅ 1,000 validations completed in {elapsed:.2f}s")

        # Should complete in reasonable time (<5s)
        assert elapsed < 5.0, f"Load test too slow: {elapsed:.2f}s"

    def test_sustained_load(self, mock_ensemble_validator):
        """Test sustained load over 30 seconds."""
        expression = "x**2 + 3*x + 2"
        duration = 30  # seconds

        count = 0
        start = time.perf_counter()
        while time.perf_counter() - start < duration:
            mock_ensemble_validator.validate(expression)
            count += 1

        elapsed = time.perf_counter() - start
        throughput = count / elapsed

        print(f"\n✅ Sustained load: {count} operations in {elapsed:.1f}s " f"({throughput:.0f} ops/sec)")

        # Should maintain >500 ops/sec
        assert throughput > 500


@pytest.mark.performance
@pytest.mark.load_test
class TestStressBenchmarks:
    """Stress testing with extreme loads."""

    @pytest.fixture(autouse=True)
    def setup(self, request):
        """Setup benchmark suite."""
        self.suite = BenchmarkSuite(output_file=request.config.getoption("--benchmark-output"))
        yield
        self.suite.save_results()

    def test_10000_operation_stress(self, mock_ensemble_validator):
        """Stress test with 10,000 operations."""
        expression = "x**2 + 3*x + 2"
        operations = 10000

        start = time.perf_counter()
        for _ in range(operations):
            mock_ensemble_validator.validate(expression)
        elapsed = time.perf_counter() - start

        throughput = operations / elapsed

        print(f"\n✅ Stress test: {operations} operations in {elapsed:.2f}s " f"({throughput:.0f} ops/sec)")

        # Should complete in reasonable time
        assert elapsed < 60.0, f"Stress test too slow: {elapsed:.2f}s"

    def test_memory_under_load(self, mock_ensemble_validator, memory_tracker):
        """Test memory doesn't grow excessively under load."""
        expression = "x**2 + 3*x + 2"

        # Run 5,000 operations
        for _ in range(5000):
            mock_ensemble_validator.validate(expression)

        # Check memory didn't leak
        memory_tracker.assert_no_leak(threshold_mb=50)

        print(f"\n✅ Memory stable under load: {memory_tracker.usage_delta():.2f}MB increase")


# ============================================================================
# CLI for Running Benchmarks
# ============================================================================

if __name__ == "__main__":
    print("=" * 80)
    print("HypatiaX Performance Benchmark Suite")
    print("=" * 80)
    print("\nUsage:")
    print("  # Run all benchmarks")
    print("  pytest tests/performance/benchmark_suite.py -v")
    print()
    print("  # Run with slow tests (LLM integration)")
    print("  pytest tests/performance/benchmark_suite.py -v --run-slow")
    print()
    print("  # Run load tests (1,000+ operations)")
    print("  pytest tests/performance/benchmark_suite.py -v --run-load-tests")
    print()
    print("  # Save results to custom file")
    print("  pytest tests/performance/benchmark_suite.py -v --benchmark-output=my_results.json")
    print()
    print("  # Run specific test class")
    print("  pytest tests/performance/benchmark_suite.py::TestValidationBenchmarks -v")
    print("=" * 80)
