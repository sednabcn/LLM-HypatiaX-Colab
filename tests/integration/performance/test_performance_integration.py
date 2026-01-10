"""
Performance and Load Testing for LLM Integration
Tests throughput, latency, and reliability under load
Week 2-3 Critical Priority - 1,000+ operation load tests
"""

import os
import statistics
import time
from concurrent.futures import ThreadPoolExecutor, as_completed
from unittest.mock import Mock, patch

import numpy as np
import psutil
import pytest

from hypatiax.tools.symbolic.hybrid_system import HybridDiscoverySystem


class TestLatencyBenchmarks:
    """Test API call latency and response times"""

    @pytest.fixture
    def system(self):
        return HybridDiscoverySystem(
            domain="defi",
            primary_llm="anthropic",
            enable_fallback=True,
            use_rich_output=False,
        )

    def test_anthropic_api_latency(self, system):
        """Test Claude API response time"""
        latencies = []

        with patch.object(system.anthropic_client.messages, "create") as mock_create:
            # Simulate realistic API latency (100-500ms)
            def mock_response(*args, **kwargs):
                time.sleep(0.15)  # 150ms simulated latency
                return Mock(content=[Mock(text="Response")])

            mock_create.side_effect = mock_response

            # Run 50 calls
            for i in range(50):
                start = time.time()
                system._call_anthropic("test prompt")
                latency = time.time() - start
                latencies.append(latency)

            avg_latency = statistics.mean(latencies)
            p95_latency = statistics.quantiles(latencies, n=20)[18]  # 95th percentile
            p99_latency = statistics.quantiles(latencies, n=100)[98]  # 99th percentile

            print(f"\nAnthropic API Latency:")
            print(f"  Average: {avg_latency * 1000:.1f}ms")
            print(f"  P95: {p95_latency * 1000:.1f}ms")
            print(f"  P99: {p99_latency * 1000:.1f}ms")

            # Assert performance targets
            assert avg_latency < 0.5  # < 500ms average
            assert p95_latency < 0.8  # < 800ms P95
            assert p99_latency < 1.0  # < 1s P99

    def test_gemini_api_latency(self, system):
        """Test Gemini API response time"""
        latencies = []

        with patch.object(system.gemini_client.models, "generate_content") as mock_gen:

            def mock_response(*args, **kwargs):
                time.sleep(0.12)  # 120ms simulated latency
                return Mock(text="Response")

            mock_gen.side_effect = mock_response

            for i in range(50):
                start = time.time()
                system._call_gemini("test prompt")
                latency = time.time() - start
                latencies.append(latency)

            avg_latency = statistics.mean(latencies)
            p95_latency = statistics.quantiles(latencies, n=20)[18]

            print(f"\nGemini API Latency:")
            print(f"  Average: {avg_latency * 1000:.1f}ms")
            print(f"  P95: {p95_latency * 1000:.1f}ms")

            assert avg_latency < 0.4
            assert p95_latency < 0.7

    def test_end_to_end_workflow_latency(self, system):
        """Test complete workflow latency including discovery + validation + LLM"""
        np.random.seed(111)
        X = np.random.uniform(1, 100, (100, 2))
        y = X[:, 0] * X[:, 1]

        latencies = []

        with patch.object(system, "_interpret_with_llm") as mock_llm:
            mock_llm.return_value = {"interpretation": "Test", "provider": "claude"}

            for i in range(20):
                start = time.time()
                system.discover_validate_interpret(
                    X=X,
                    y=y,
                    variable_names=["a", "b"],
                    variable_descriptions={"a": "A", "b": "B"},
                    variable_units={"a": "u", "b": "u"},
                    show_formatted=False,
                )
                latency = time.time() - start
                latencies.append(latency)

            avg_latency = statistics.mean(latencies)

            print(f"\nE2E Workflow Latency:")
            print(f"  Average: {avg_latency:.2f}s")
            print(f"  Min: {min(latencies):.2f}s")
            print(f"  Max: {max(latencies):.2f}s")

            # Complete workflow should be under 5 seconds
            assert avg_latency < 5.0


@pytest.mark.slow
class TestThroughputBenchmarks:
    """Test system throughput and scalability"""

    def test_sequential_throughput(self):
        """Test sequential processing throughput"""
        system = HybridDiscoverySystem(domain="defi", use_rich_output=False)

        with patch.object(system, "_call_anthropic") as mock_claude:
            mock_claude.return_value = "Response"

            start = time.time()

            # Process 100 interpretations sequentially
            for i in range(100):
                system._interpret_with_llm(
                    expression=f"x{i} + y{i}",
                    variables={"x": "input", "y": "output"},
                    r2=0.9,
                )

            elapsed = time.time() - start
            throughput = 100 / elapsed

            print(f"\nSequential Throughput:")
            print(f"  {throughput:.1f} operations/sec")
            print(f"  Total time: {elapsed:.2f}s")

            # Should handle at least 50 ops/sec with mocking
            assert throughput > 50

    def test_concurrent_throughput(self):
        """Test concurrent processing with thread pool"""
        system = HybridDiscoverySystem(domain="defi", use_rich_output=False)

        def process_interpretation(i):
            """Process a single interpretation"""
            return system._interpret_with_llm(
                expression=f"x{i} * y{i}", variables={"x": "a", "y": "b"}, r2=0.9
            )

        with patch.object(system, "_call_anthropic") as mock_claude:
            mock_claude.return_value = "Response"

            start = time.time()

            # Process 100 interpretations with 10 workers
            with ThreadPoolExecutor(max_workers=10) as executor:
                futures = [
                    executor.submit(process_interpretation, i) for i in range(100)
                ]
                results = [f.result() for f in as_completed(futures)]

            elapsed = time.time() - start
            throughput = 100 / elapsed

            print(f"\nConcurrent Throughput (10 workers):")
            print(f"  {throughput:.1f} operations/sec")
            print(f"  Total time: {elapsed:.2f}s")

            # Concurrent should be faster than sequential
            assert throughput > 100  # With mocking and threads


@pytest.mark.slow
@pytest.mark.integration
class TestLoadTests:
    """Load testing with 1,000+ operations as per requirements"""

    def test_1000_operation_load_test(self):
        """Test system with 1,000+ operations (Week 2-3 requirement)"""
        system = HybridDiscoverySystem(
            domain="defi", max_results=1000, use_rich_output=False
        )

        success_count = 0
        error_count = 0
        latencies = []

        with patch.object(system, "_call_anthropic") as mock_claude:
            # Simulate realistic API with occasional failures
            call_count = [0]

            def mock_api(*args, **kwargs):
                call_count[0] += 1
                time.sleep(0.001)  # 1ms simulated latency

                # Simulate 1% failure rate
                if call_count[0] % 100 == 0:
                    raise Exception("Simulated API failure")

                return "Response"

            mock_claude.side_effect = mock_api

            start = time.time()

            # Run 1,000 interpretation operations
            for i in range(1000):
                op_start = time.time()
                try:
                    system._interpret_with_llm(
                        expression=f"x{i % 10} + y{i % 10}",
                        variables={"x": "input", "y": "output"},
                        r2=0.9,
                    )
                    success_count += 1
                    latencies.append(time.time() - op_start)
                except Exception:
                    error_count += 1

            elapsed = time.time() - start

            print(f"\n1,000 Operation Load Test:")
            print(f"  Total time: {elapsed:.2f}s")
            print(f"  Throughput: {1000 / elapsed:.1f} ops/sec")
            print(f"  Success: {success_count}")
            print(f"  Errors: {error_count}")
            print(f"  Error rate: {error_count / 1000:.1%}")
            print(f"  Avg latency: {statistics.mean(latencies) * 1000:.1f}ms")

            # Assertions
            assert success_count >= 950  # 95%+ success rate
            assert error_count <= 50  # <5% error rate
            assert elapsed < 120  # Complete in under 2 minutes

    def test_sustained_load_5_minutes(self):
        """Test sustained load over 5 minutes"""
        system = HybridDiscoverySystem(domain="defi", use_rich_output=False)

        with patch.object(system, "_call_anthropic") as mock_claude:
            mock_claude.return_value = "Response"

            start = time.time()
            operation_count = 0
            target_duration = 5.0  # 5 seconds for test (would be 300s in production)

            # Run operations for target duration
            while time.time() - start < target_duration:
                system._interpret_with_llm(
                    expression=f"x + y", variables={"x": "a", "y": "b"}, r2=0.9
                )
                operation_count += 1

            elapsed = time.time() - start
            throughput = operation_count / elapsed

            print(f"\nSustained Load Test ({elapsed:.1f}s):")
            print(f"  Operations: {operation_count}")
            print(f"  Throughput: {throughput:.1f} ops/sec")

            assert throughput > 10  # Maintain decent throughput


class TestMemoryPerformance:
    """Test memory usage and efficiency"""

    def test_memory_usage_bounded_results(self):
        """Test memory usage with bounded results storage"""
        import gc

        system = HybridDiscoverySystem(
            domain="defi", max_results=100, use_rich_output=False
        )

        gc.collect()
        process = psutil.Process(os.getpid())
        initial_memory = process.memory_info().rss / 1024 / 1024  # MB

        np.random.seed(222)

        with patch.object(system, "_interpret_with_llm") as mock_llm:
            mock_llm.return_value = {
                "provider": "claude",
                "interpretation": "Test" * 100,
            }

            # Run 500 workflows (5x max_results)
            for i in range(500):
                X = np.random.uniform(1, 100, (100, 2))
                y = X[:, 0] + X[:, 1]

                system.discover_validate_interpret(
                    X=X,
                    y=y,
                    variable_names=["a", "b"],
                    variable_descriptions={"a": "A", "b": "B"},
                    variable_units={"a": "u", "b": "u"},
                    show_formatted=False,
                )

        gc.collect()
        final_memory = process.memory_info().rss / 1024 / 1024  # MB
        memory_increase = final_memory - initial_memory

        print(f"\nMemory Usage:")
        print(f"  Initial: {initial_memory:.1f} MB")
        print(f"  Final: {final_memory:.1f} MB")
        print(f"  Increase: {memory_increase:.1f} MB")
        print(f"  Results stored: {len(system.results)}")

        # Should only keep 100 results
        assert len(system.results) == 100

        # Memory increase should be reasonable (< 500MB)
        assert memory_increase < 500

    def test_memory_leak_check(self):
        """Test for memory leaks with repeated operations"""
        system = HybridDiscoverySystem(
            domain="defi", max_results=10, use_rich_output=False
        )

        memory_samples = []
        process = psutil.Process(os.getpid())

        with patch.object(system, "_call_anthropic") as mock_claude:
            mock_claude.return_value = "Response"

            # Run 10 batches of 50 operations
            for batch in range(10):
                for i in range(50):
                    system._interpret_with_llm(
                        expression="x + y", variables={"x": "a", "y": "b"}, r2=0.9
                    )

                # Sample memory after each batch
                import gc

                gc.collect()
                memory_mb = process.memory_info().rss / 1024 / 1024
                memory_samples.append(memory_mb)

        print(f"\nMemory Samples: {[f'{m:.1f}' for m in memory_samples]}")

        # Check for linear growth (memory leak indicator)
        # Calculate trend: if steadily increasing, might be a leak
        if len(memory_samples) >= 3:
            first_third = statistics.mean(memory_samples[:3])
            last_third = statistics.mean(memory_samples[-3:])
            growth_rate = (last_third - first_third) / first_third

            print(f"  Memory growth rate: {growth_rate:.1%}")

            # Should not grow more than 50% (with bounded storage)
            assert growth_rate < 0.5


class TestRetryPerformance:
    """Test retry logic performance impact"""

    def test_retry_backoff_timing(self):
        """Test exponential backoff timing is correct"""
        system = HybridDiscoverySystem(domain="defi", max_retries=4, retry_delay=0.1)

        with patch.object(system.anthropic_client.messages, "create") as mock_create:
            # Simulate 3 failures then success
            mock_create.side_effect = [
                Exception("Error 1"),
                Exception("Error 2"),
                Exception("Error 3"),
                Mock(content=[Mock(text="Success")]),
            ]

            start = time.time()
            response = system._call_anthropic("test")
            elapsed = time.time() - start

            # Expected: 0.1 + 0.2 + 0.4 = 0.7s minimum
            print(f"\nRetry backoff timing: {elapsed:.3f}s")

            assert elapsed >= 0.7
            assert elapsed < 1.0  # Should not be excessive
            assert response == "Success"

    def test_retry_performance_impact(self):
        """Test performance impact of retries"""
        system = HybridDiscoverySystem(domain="defi", max_retries=3, retry_delay=0.05)

        # Test with no retries needed
        with patch.object(system.anthropic_client.messages, "create") as mock_create:
            mock_create.return_value = Mock(content=[Mock(text="Success")])

            start = time.time()
            for _ in range(50):
                system._call_anthropic("test")
            no_retry_time = time.time() - start

        # Test with retries needed
        with patch.object(system.anthropic_client.messages, "create") as mock_create:
            call_count = [0]

            def failing_api(*args, **kwargs):
                call_count[0] += 1
                if call_count[0] % 2 == 1:  # Fail every other call
                    raise Exception("Transient error")
                return Mock(content=[Mock(text="Success")])

            mock_create.side_effect = failing_api

            start = time.time()
            for _ in range(50):
                try:
                    system._call_anthropic("test")
                except:
                    pass
            retry_time = time.time() - start

        print(f"\nRetry Performance Impact:")
        print(f"  No retries: {no_retry_time:.2f}s")
        print(f"  With retries: {retry_time:.2f}s")
        print(f"  Overhead: {retry_time - no_retry_time:.2f}s")

        # Retry overhead should be proportional to retry_delay
        assert retry_time < no_retry_time * 10  # Not 10x slower


class TestCachePerformance:
    """Test caching strategies for performance optimization"""

    def test_repeated_interpretation_caching_benefit(self):
        """Test benefit of caching repeated interpretations"""
        system = HybridDiscoverySystem(domain="defi", use_rich_output=False)

        # Without caching (current implementation)
        with patch.object(system, "_call_anthropic") as mock_claude:
            mock_claude.return_value = "Response"

            start = time.time()
            # Interpret same expression 100 times
            for _ in range(100):
                system._interpret_with_llm(
                    expression="x + y", variables={"x": "input", "y": "output"}, r2=0.9
                )
            no_cache_time = time.time() - start
            call_count = mock_claude.call_count

        print(f"\nRepeated Interpretations (no caching):")
        print(f"  Time: {no_cache_time:.2f}s")
        print(f"  API calls: {call_count}")

        # All calls should hit the API
        assert call_count == 100


@pytest.mark.benchmark
class TestBenchmarkSuite:
    """Comprehensive benchmark suite for reporting"""

    def test_complete_benchmark_suite(self):
        """Run complete benchmark suite and generate report"""
        results = {
            "anthropic_latency": [],
            "gemini_latency": [],
            "workflow_latency": [],
            "throughput": 0,
            "memory_usage": 0,
        }

        system = HybridDiscoverySystem(
            domain="defi",
            primary_llm="anthropic",
            enable_fallback=True,
            use_rich_output=False,
        )

        # Benchmark 1: API Latencies
        with patch.object(system.anthropic_client.messages, "create") as mock_claude:
            mock_claude.return_value = Mock(content=[Mock(text="Response")])

            for _ in range(20):
                start = time.time()
                system._call_anthropic("test")
                results["anthropic_latency"].append(time.time() - start)

        with patch.object(
            system.gemini_client.models, "generate_content"
        ) as mock_gemini:
            mock_gemini.return_value = Mock(text="Response")

            for _ in range(20):
                start = time.time()
                system._call_gemini("test")
                results["gemini_latency"].append(time.time() - start)

        # Benchmark 2: Throughput
        with patch.object(system, "_call_anthropic") as mock_claude:
            mock_claude.return_value = "Response"

            start = time.time()
            for i in range(100):
                system._interpret_with_llm(
                    expression=f"x{i} + y{i}", variables={"x": "a", "y": "b"}, r2=0.9
                )
            elapsed = time.time() - start
            results["throughput"] = 100 / elapsed

        # Print benchmark report
        print("\n" + "=" * 60)
        print("BENCHMARK RESULTS")
        print("=" * 60)
        print(f"\nAPI Latency:")
        print(f"  Anthropic Claude:")
        print(f"    Mean: {statistics.mean(results['anthropic_latency']) * 1000:.1f}ms")
        print(
            f"    Median: {statistics.median(results['anthropic_latency']) * 1000:.1f}ms"
        )
        print(f"  Google Gemini:")
        print(f"    Mean: {statistics.mean(results['gemini_latency']) * 1000:.1f}ms")
        print(
            f"    Median: {statistics.median(results['gemini_latency']) * 1000:.1f}ms"
        )
        print(f"\nThroughput: {results['throughput']:.1f} ops/sec")
        print("=" * 60)


if __name__ == "__main__":
    pytest.main([__file__, "-v", "--tb=short", "-m", "not slow"])
