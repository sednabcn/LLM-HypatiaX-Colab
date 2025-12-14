# Complete Guide: Designing Benchmarks for Your Project

## 📋 Table of Contents
1. [Why Benchmark?](#why-benchmark)
2. [The 5-Step Benchmark Design Process](#the-5-step-process)
3. [Types of Benchmarks](#types-of-benchmarks)
4. [Performance Metrics to Track](#performance-metrics)
5. [Setting Realistic Targets](#setting-targets)
6. [Implementation Patterns](#implementation-patterns)
7. [Common Pitfalls & Solutions](#pitfalls)
8. [Real-World Examples](#examples)

---

## 🎯 Why Benchmark?

Benchmarks serve multiple critical purposes:

- **Prevent Regressions**: Catch performance degradation before production
- **Guide Optimization**: Know what to optimize and validate improvements
- **Set SLAs**: Establish performance guarantees for users/customers
- **Monitor Trends**: Track performance over time as code evolves
- **Compare Alternatives**: Objectively evaluate different implementations
- **Document Performance**: Create transparency about system capabilities

---

## 🔄 The 5-Step Benchmark Design Process

### Step 1: Identify Critical Operations 🎯

**Questions to ask:**
- What operations do users perform most frequently?
- What operations are performance-critical for user experience?
- What operations consume the most resources (CPU, memory, I/O)?
- What are your system's bottlenecks?

**Example for HypatiaX:**
```python
# Critical operations identified:
CRITICAL_OPERATIONS = {
    "validation": "Users validate formulas constantly - must be < 1ms",
    "llm_calls": "AI explanations - users wait for these - must be < 500ms",
    "symbolic_regression": "Core feature - acceptable if < 100ms",
    "data_processing": "Background task - can be slower",
}
```

**Pro Tip:** Use profiling tools first to identify hotspots:
```python
import cProfile
import pstats

# Profile your application
cProfile.run('your_function()', 'profile_stats')

# Analyze results
stats = pstats.Stats('profile_stats')
stats.sort_stats('cumulative')
stats.print_stats(20)  # Top 20 time consumers
```

---

### Step 2: Define User Scenarios 👥

**Think in terms of real usage patterns:**

**Bad approach:** "Test that function X runs in Y ms"
**Good approach:** "Test that a user can validate 10 formulas in sequence within 5ms total"

**Example scenarios:**

```python
USER_SCENARIOS = {
    "quick_validation": {
        "description": "User types formula, gets instant feedback",
        "operations": ["parse", "validate", "display_errors"],
        "target": "< 50ms total",
        "frequency": "Every keystroke (very high)",
    },

    "formula_discovery": {
        "description": "User uploads data, discovers formula",
        "operations": ["data_validation", "symbolic_regression",
                      "validation", "explanation"],
        "target": "< 2 seconds total",
        "frequency": "1-10 times per session",
    },

    "batch_analysis": {
        "description": "User validates 100 formulas",
        "operations": ["batch_validation", "generate_report"],
        "target": "< 30 seconds",
        "frequency": "Few times per day",
    },
}
```

---

### Step 3: Establish Performance Tiers 📊

Not all operations need the same performance level. Create tiers:

```python
PERFORMANCE_TIERS = {
    "instant": {
        "target": "< 50ms",
        "user_perception": "Instantaneous",
        "examples": ["validation", "syntax_checking", "autocomplete"],
    },

    "fast": {
        "target": "50-200ms",
        "user_perception": "Responsive, no waiting",
        "examples": ["search", "filter", "simple_computation"],
    },

    "acceptable": {
        "target": "200-1000ms",
        "user_perception": "Brief wait, acceptable",
        "examples": ["llm_calls", "complex_analysis", "file_loading"],
    },

    "background": {
        "target": "1-10 seconds",
        "user_perception": "Show progress indicator",
        "examples": ["batch_processing", "report_generation", "model_training"],
    },

    "async": {
        "target": "> 10 seconds",
        "user_perception": "Run in background, notify when done",
        "examples": ["large_dataset_processing", "model_retraining"],
    },
}
```

**Nielsen's Response Time Limits (Psychology-Based):**
- **0.1s**: Feels instantaneous
- **1.0s**: User's flow of thought stays uninterrupted
- **10s**: Limit for keeping user's attention

---

### Step 4: Choose the Right Metrics 📈

Different operations need different metrics:

#### **Latency Metrics** (for user-facing operations)
```python
LATENCY_METRICS = {
    "p50": "Typical user experience",
    "p95": "95% of users see this or better",
    "p99": "Worst case for most users",
    "max": "Absolute worst case",
}
```

**When to use what:**
- **P50 (median)**: Daily performance monitoring
- **P95**: SLA targets, user experience guarantees
- **P99**: Detecting outliers, investigating issues
- **Max**: Identifying edge cases, not for targets

#### **Throughput Metrics** (for system capacity)
```python
THROUGHPUT_METRICS = {
    "ops_per_second": "How many operations system can handle",
    "requests_per_minute": "API capacity",
    "items_processed_per_hour": "Batch job capacity",
}
```

#### **Resource Metrics** (for stability)
```python
RESOURCE_METRICS = {
    "memory_usage": "MB used per operation",
    "memory_growth": "Memory leak detection",
    "cpu_utilization": "% CPU used",
    "disk_io": "Read/write operations",
}
```

#### **Scalability Metrics** (for growth)
```python
SCALABILITY_METRICS = {
    "complexity": "O(n) vs O(n²) behavior",
    "concurrent_users": "System degradation under load",
    "data_size_impact": "Performance vs dataset size",
}
```

---

### Step 5: Set Realistic Targets 🎯

**Framework for setting targets:**

```python
def calculate_target(operation_type, baseline_measurement):
    """
    Set realistic performance targets based on operation type.
    """

    # Start with current performance
    baseline = baseline_measurement

    # Set target based on tier
    if operation_type == "instant":
        target = min(baseline * 0.8, 50)  # 20% better or 50ms max
        regression_allowed = 0.10  # 10% regression OK

    elif operation_type == "fast":
        target = min(baseline * 0.9, 200)
        regression_allowed = 0.15

    elif operation_type == "acceptable":
        target = min(baseline * 1.0, 1000)
        regression_allowed = 0.20

    elif operation_type == "background":
        target = baseline * 1.2  # More lenient
        regression_allowed = 0.30

    return {
        "target_p95": target,
        "allowed_regression": regression_allowed,
        "stretch_goal": target * 0.8,  # Aspirational
    }
```

**Example targets:**

```python
PERFORMANCE_TARGETS = {
    "symbolic_validation": {
        "p50": 0.8,   # Typical: 0.8ms
        "p95": 1.0,   # SLA: 95% under 1ms
        "p99": 1.5,   # 99% under 1.5ms
        "allowed_regression": 0.20,  # Can slow by 20%
    },

    "llm_api_call": {
        "p50": 300,   # Typical: 300ms
        "p95": 500,   # SLA: 95% under 500ms
        "p99": 800,   # 99% under 800ms
        "allowed_regression": 0.30,  # LLMs vary more
    },
}
```

---

## 🧪 Types of Benchmarks

### 1. **Microbenchmarks** 🔬
Test individual functions/operations in isolation.

```python
def test_single_function_performance():
    """Test one specific function."""

    def function_to_test():
        return complex_calculation()

    measurements = []
    for _ in range(1000):
        start = time.perf_counter()
        function_to_test()
        measurements.append(time.perf_counter() - start)

    p95 = np.percentile(measurements, 95)
    assert p95 < TARGET_MS
```

**When to use:**
- Testing core algorithms
- Comparing implementation alternatives
- Validating optimizations

**Pro tip:** Use `timeit` for very accurate microbenchmarks:
```python
import timeit

# Automatically handles warmup and repetition
result = timeit.timeit(
    'function_to_test()',
    setup='from mymodule import function_to_test',
    number=10000
)
print(f"Average: {result/10000*1000:.3f}ms")
```

---

### 2. **Integration Benchmarks** 🔗
Test multiple components working together.

```python
def test_end_to_end_workflow():
    """Test complete user workflow."""

    def complete_workflow():
        # Step 1: Parse input
        parsed = parser.parse(user_input)

        # Step 2: Validate
        validation = validator.validate(parsed)

        # Step 3: Generate explanation
        explanation = llm.explain(parsed)

        return validation, explanation

    # Measure complete workflow
    result = benchmark_suite.measure(
        complete_workflow,
        operation="end_to_end_workflow",
        iterations=100
    )

    assert result.p95 < 1000  # Total workflow < 1s
```

---

### 3. **Load Benchmarks** 📊
Test system behavior under realistic load.

```python
def test_concurrent_users():
    """Simulate 100 concurrent users."""

    from concurrent.futures import ThreadPoolExecutor

    def simulate_user():
        for _ in range(10):  # 10 operations per user
            validate_formula(random_formula())

    with ThreadPoolExecutor(max_workers=100) as executor:
        start = time.time()
        futures = [executor.submit(simulate_user)
                   for _ in range(100)]

        for future in futures:
            future.result()

        elapsed = time.time() - start

    ops_per_second = (100 * 10) / elapsed
    assert ops_per_second > 500  # System handles 500 ops/sec
```

---

### 4. **Stress Benchmarks** 💪
Push system to limits to find breaking points.

```python
def test_stress_limits():
    """Find system limits."""

    operations = 0
    errors = 0

    start = time.time()
    while time.time() - start < 60:  # Run for 60 seconds
        try:
            validate_formula(complex_formula())
            operations += 1
        except Exception:
            errors += 1

    error_rate = errors / operations
    throughput = operations / 60

    print(f"Sustained throughput: {throughput:.0f} ops/sec")
    print(f"Error rate: {error_rate*100:.2f}%")

    assert error_rate < 0.01  # < 1% errors under stress
```

---

### 5. **Regression Benchmarks** 📉
Detect performance degradation over time.

```python
def test_performance_regression():
    """Compare against baseline."""

    # Load historical baseline
    baseline = load_baseline("validation_performance")

    # Measure current performance
    current = measure_performance(validate_formula)

    # Check for regression
    regression = (current.p95 - baseline.p95) / baseline.p95

    assert regression < 0.20, \
        f"Performance regressed by {regression*100:.1f}% (allowed: 20%)"
```

---

### 6. **Comparative Benchmarks** ⚖️
Compare different implementations or approaches.

```python
def test_algorithm_comparison():
    """Compare two algorithms."""

    # Benchmark Algorithm A
    time_a = benchmark(algorithm_a, iterations=1000)

    # Benchmark Algorithm B
    time_b = benchmark(algorithm_b, iterations=1000)

    speedup = time_a / time_b

    print(f"Algorithm B is {speedup:.2f}x faster")

    # Use the faster one
    if speedup > 1.5:
        use_algorithm_b()
```

---

## 📊 Performance Metrics to Track

### Essential Metrics Dashboard

```python
BENCHMARK_REPORT = {
    "latency": {
        "p50": 0.75,      # Median response time
        "p95": 1.02,      # 95th percentile
        "p99": 1.48,      # 99th percentile
        "max": 3.21,      # Worst case
    },

    "throughput": {
        "ops_per_second": 12453,
        "peak_ops_per_second": 15892,
    },

    "resources": {
        "memory_mb": 125.4,
        "memory_growth_mb": 2.1,
        "cpu_percent": 23.5,
    },

    "reliability": {
        "error_rate": 0.002,    # 0.2%
        "timeout_rate": 0.001,  # 0.1%
    },

    "scalability": {
        "10_items": 5.2,
        "100_items": 12.4,
        "1000_items": 87.3,
        "complexity": "O(n)",
    },
}
```

---

## ⚠️ Common Pitfalls & Solutions

### Pitfall 1: **Measuring the Wrong Thing**

**Bad:**
```python
# Only measuring best case
def test_performance():
    result = function()  # Run once
    assert result.time < target
```

**Good:**
```python
# Measuring realistic case with percentiles
def test_performance():
    results = [function() for _ in range(1000)]
    p95 = np.percentile(results, 95)
    assert p95 < target
```

---

### Pitfall 2: **Forgetting Warmup**

**Bad:**
```python
# First run includes JIT compilation, cache misses
measurements = [function() for _ in range(100)]
```

**Good:**
```python
# Warmup first
for _ in range(10):
    function()  # Warmup

measurements = [function() for _ in range(100)]
```

---

### Pitfall 3: **Unrealistic Test Data**

**Bad:**
```python
# Testing with tiny, perfect data
test_data = [1, 2, 3, 4, 5]
```

**Good:**
```python
# Testing with realistic, messy data
test_data = generate_realistic_data(
    size=1000,
    include_nulls=True,
    include_outliers=True,
    include_edge_cases=True
)
```

---

### Pitfall 4: **Ignoring Variance**

**Bad:**
```python
# Single measurement
time = measure_once()
assert time < target
```

**Good:**
```python
# Multiple measurements + statistical analysis
times = [measure() for _ in range(100)]
mean = np.mean(times)
std = np.std(times)
p95 = np.percentile(times, 95)

print(f"Mean: {mean:.2f}ms ± {std:.2f}ms")
assert p95 < target
```

---

### Pitfall 5: **Setting Impossible Targets**

**Bad:**
```python
# Unrealistic target based on hope
TARGET_MS = 0.001  # 1 microsecond for complex operation
```

**Good:**
```python
# Target based on measurement + improvement goal
baseline = measure_current_performance()
TARGET_MS = baseline * 0.8  # 20% improvement goal
```

---

## 💡 Real-World Examples

### Example 1: Web API Benchmark

```python
class APIBenchmarkSuite:
    """Benchmark REST API endpoints."""

    def test_list_endpoint_performance(self):
        """GET /api/formulas should return in < 200ms."""

        measurements = []

        for _ in range(100):
            start = time.perf_counter()
            response = requests.get('http://localhost:8000/api/formulas')
            elapsed = time.perf_counter() - start

            assert response.status_code == 200
            measurements.append(elapsed * 1000)

        p95 = np.percentile(measurements, 95)

        print(f"API latency P95: {p95:.2f}ms")
        assert p95 < 200, f"API too slow: {p95:.2f}ms"

    def test_concurrent_requests(self):
        """API should handle 50 concurrent requests."""

        from concurrent.futures import ThreadPoolExecutor

        def make_request():
            response = requests.get('http://localhost:8000/api/formulas')
            return response.elapsed.total_seconds() * 1000

        with ThreadPoolExecutor(max_workers=50) as executor:
            start = time.time()
            results = list(executor.map(
                lambda _: make_request(),
                range(100)
            ))
            elapsed = time.time() - start

        throughput = 100 / elapsed
        p95_latency = np.percentile(results, 95)

        print(f"Throughput: {throughput:.0f} req/sec")
        print(f"P95 latency: {p95_latency:.2f}ms")

        assert throughput > 50  # At least 50 req/sec
        assert p95_latency < 500  # Under load, still < 500ms
```

---

### Example 2: Database Query Benchmark

```python
class DatabaseBenchmarks:
    """Benchmark database operations."""

    def test_query_performance(self):
        """Common query should complete in < 50ms."""

        measurements = []

        for _ in range(100):
            start = time.perf_counter()

            results = db.session.query(Formula)\
                .filter(Formula.domain == 'defi')\
                .limit(100)\
                .all()

            elapsed = (time.perf_counter() - start) * 1000
            measurements.append(elapsed)

        p95 = np.percentile(measurements, 95)

        assert p95 < 50, f"Query too slow: {p95:.2f}ms"

    def test_query_scaling(self):
        """Query time should scale linearly."""

        sizes = [10, 100, 1000, 10000]
        times = []

        for size in sizes:
            measurements = []
            for _ in range(10):
                start = time.perf_counter()
                results = db.session.query(Formula).limit(size).all()
                measurements.append(time.perf_counter() - start)

            times.append(np.median(measurements))

        # Check scaling factor
        scaling_factor = times[-1] / times[0]
        expected_factor = sizes[-1] / sizes[0]  # Linear: 1000x

        # Should be close to linear (within 2x)
        assert scaling_factor < expected_factor * 2, \
            f"Query scaling non-linear: {scaling_factor:.0f}x vs expected {expected_factor:.0f}x"
```

---

### Example 3: Machine Learning Benchmark

```python
class MLBenchmarks:
    """Benchmark ML model operations."""

    def test_inference_latency(self):
        """Model inference should be < 100ms."""

        # Load model once
        model = load_trained_model()
        sample_input = generate_sample_input()

        # Warmup (important for ML models!)
        for _ in range(10):
            model.predict(sample_input)

        # Measure
        measurements = []
        for _ in range(100):
            start = time.perf_counter()
            prediction = model.predict(sample_input)
            measurements.append((time.perf_counter() - start) * 1000)

        p95 = np.percentile(measurements, 95)

        assert p95 < 100, f"Inference too slow: {p95:.2f}ms"

    def test_batch_inference_efficiency(self):
        """Batch inference should be more efficient."""

        model = load_trained_model()
        single_input = generate_sample_input()
        batch_input = [generate_sample_input() for _ in range(32)]

        # Single inference
        single_time = timeit.timeit(
            lambda: model.predict(single_input),
            number=32
        )

        # Batch inference
        batch_time = timeit.timeit(
            lambda: model.predict_batch(batch_input),
            number=1
        )

        speedup = single_time / batch_time

        print(f"Batch is {speedup:.2f}x faster")
        assert speedup > 2, "Batch inference should be at least 2x faster"
```

---

## 🎓 Best Practices Summary

### ✅ DO:
1. **Measure real user scenarios**, not just isolated functions
2. **Use percentiles** (P95, P99) instead of averages
3. **Include warmup iterations** to exclude cold start effects
4. **Test with realistic data** including edge cases
5. **Run multiple iterations** for statistical significance
6. **Track trends over time** to catch gradual degradation
7. **Set targets based on measurement**, not guesswork
8. **Document why** each benchmark exists

### ❌ DON'T:
1. **Don't test in debug mode** - always use release/optimized builds
2. **Don't ignore variance** - report standard deviation
3. **Don't set arbitrary targets** - base them on requirements
4. **Don't benchmark on loaded systems** - use dedicated hardware
5. **Don't forget cleanup** - ensure tests don't affect each other
6. **Don't only test happy paths** - include error cases
7. **Don't benchmark mocks** - use real implementations when possible

---

## 🚀 Getting Started Checklist

- [ ] List your 10 most critical operations
- [ ] Profile your app to find actual bottlenecks
- [ ] Define 3-5 user scenarios
- [ ] Measure current baseline performance
- [ ] Set realistic targets based on baselines
- [ ] Write microbenchmarks for critical functions
- [ ] Write integration benchmarks for key workflows
- [ ] Set up regression detection
- [ ] Add benchmarks to CI/CD pipeline
- [ ] Create performance dashboard

---

## 📚 Further Reading

- **"Systems Performance" by Brendan Gregg** - Comprehensive performance analysis
- **Google's "The Tail at Scale"** - Why P99 matters
- **Netflix's Performance Blog** - Real-world examples at scale
- **Python Performance Tips** - https://wiki.python.org/moin/PythonSpeed/PerformanceTips

---

*Remember: "You can't improve what you don't measure." Start benchmarking today!* 🎯

📖 Quick Navigation:

The 5-Step Process - Systematic approach from identifying operations to setting targets
Types of Benchmarks - 6 different types (micro, integration, load, stress, regression, comparative)
Performance Metrics - What to measure and when
Setting Targets - Framework for realistic performance goals
Common Pitfalls - 5 major mistakes and how to avoid them
Real Examples - Web APIs, databases, ML models

🎯 Key Takeaways:
Start with these questions:

What do users do most often?
What's performance-critical for UX?
What are my bottlenecks?

Use the tier system:

Instant (< 50ms): validation, autocomplete
Fast (50-200ms): search, filtering
Acceptable (200-1000ms): LLM calls, analysis
Background (1-10s): batch processing

Always measure:

P95 (not just average) - 95% of users see this or better
Run 100+ iterations with warmup
Test with realistic data, not toy examples
