# 🚀 HypatiaX Integration Quick Start
## Week 2-3: Real LLM Integration Setup

Get up and running with the updated HypatiaX Hybrid Discovery System in under 10 minutes.

---

## 📦 Installation

### Step 1: Install Dependencies

```bash
# Core dependencies
pip install numpy sympy anthropic google-genai

# Testing dependencies
pip install pytest pytest-asyncio pytest-cov psutil

# Optional: For rich output formatting
pip install rich
```

### Step 2: Set Up API Keys

Create a `.env` file in your project root:

```bash
# .env file
ANTHROPIC_API_KEY=sk-ant-api03-your-key-here
GEMINI_API_KEY=AIzaSy-your-key-here
```

Or export directly:

```bash
export ANTHROPIC_API_KEY="sk-ant-api03-your-key-here"
export GEMINI_API_KEY="AIzaSy-your-key-here"
```

**Get API Keys:**
- Anthropic Claude: https://console.anthropic.com/
- Google Gemini: https://aistudio.google.com/app/apikey

---

## 🎯 Basic Usage

### Example 1: Simple Discovery with Claude

```python
from hypatiax.tools.symbolic.hybrid_system import HybridDiscoverySystem
import numpy as np

# Initialize system with Anthropic Claude
system = HybridDiscoverySystem(
    domain='defi',
    primary_llm='anthropic',
    enable_fallback=True
)

# Generate sample data (AMM constant product)
np.random.seed(42)
X = np.random.uniform(10, 1000, (100, 2))
y = np.sqrt(X[:, 0] * X[:, 1])

# Run complete workflow
result = system.discover_validate_interpret(
    X=X,
    y=y,
    variable_names=['reserve0', 'reserve1'],
    variable_descriptions={
        'reserve0': 'Token 0 reserves',
        'reserve1': 'Token 1 reserves'
    },
    variable_units={
        'reserve0': 'tokens',
        'reserve1': 'tokens'
    },
    description="AMM Formula Discovery"
)

print(f"Expression: {result['discovery']['expression']}")
print(f"R² Score: {result['discovery']['r2_score']:.4f}")
print(f"Validation: {result['validation']['total_score']:.1f}/100")
print(f"Interpretation: {result['interpretation']['interpretation']}")
```

### Example 2: Using Gemini with Fallback

```python
# Initialize with Gemini primary, Claude fallback
system = HybridDiscoverySystem(
    domain='finance',
    primary_llm='google',  # Use Gemini first
    enable_fallback=True,   # Fallback to Claude if Gemini fails
    max_retries=3
)

# Run workflow (same as above)
result = system.discover_validate_interpret(...)

# Check which provider was used
print(f"Provider: {result['interpretation']['provider']}")
print(f"Fallback count: {system.stats['fallback_count']}")
```

### Example 3: Statistics and Monitoring

```python
# Get system statistics
stats = system.get_statistics()

print(f"Total runs: {stats['total_runs']}")
print(f"Success rate: {stats['success_rate']:.1%}")
print(f"\nLLM Usage:")
print(f"  Anthropic calls: {stats['llm_usage']['anthropic']['calls']}")
print(f"  Google calls: {stats['llm_usage']['google']['calls']}")
print(f"  Fallback count: {stats['llm_usage']['fallback_count']}")
```

---

## 🧪 Running Tests

### Quick Test Run (Unit Tests Only)

```bash
# Run fast unit tests
pytest tests/integration/ -v -m "not slow"

# Expected output:
# ✓ ~200 tests pass in < 30 seconds
```

### Full Integration Tests

```bash
# Run with real API calls (requires API keys)
pytest tests/integration/ -v --run-integration

# Or run specific test file
pytest tests/integration/test_real_llm_integration.py -v
```

### Load Tests (1,000+ Operations)

```bash
# Run comprehensive load tests
pytest tests/integration/test_performance_integration.py::TestLoadTests -v --run-load-tests

# Expected: ~1000 operations in < 120 seconds
```

### With Coverage Report

```bash
pytest tests/integration/ --cov=hypatiax.tools.symbolic --cov-report=html

# Open htmlcov/index.html to view coverage
```

---

## 🔍 Verification Checklist

Run these commands to verify everything is working:

```bash
# 1. Check Python version (3.8+)
python --version

# 2. Verify packages installed
pip list | grep -E "(anthropic|google-genai|pytest)"

# 3. Check API keys set
echo $ANTHROPIC_API_KEY | head -c 20
echo $GEMINI_API_KEY | head -c 20

# 4. Run smoke test
python -c "from hypatiax.tools.symbolic.hybrid_system import HybridDiscoverySystem; print('✓ Import successful')"

# 5. Run quick test
pytest tests/integration/test_real_llm_integration.py::TestAnthropicIntegration::test_anthropic_client_initialization -v
```

**Expected Output:**
```
✓ Python 3.8+
✓ anthropic==0.25.0
✓ google-genai==0.3.0
✓ pytest==7.4.0
✓ API keys configured
✓ Import successful
✓ Tests passing
```

---

## 🎨 Advanced Features

### Custom Retry Configuration

```python
system = HybridDiscoverySystem(
    domain='defi',
    max_retries=5,          # More retry attempts
    retry_delay=2.0,        # Longer initial delay
    enable_fallback=True
)
```

### Custom Validation Weights

```python
system = HybridDiscoverySystem(
    domain='finance',
    validation_weights={
        'symbolic': 0.35,      # Increase symbolic validation
        'dimensional': 0.25,
        'domain': 0.25,
        'consistency': 0.15
    }
)
```

### Disable LLM Interpretation

```python
# Run without LLM (faster, no API calls)
result = system.discover_validate_interpret(
    X=X, y=y,
    variable_names=['x', 'y'],
    variable_descriptions={'x': 'Input', 'y': 'Output'},
    variable_units={'x': 'units', 'y': 'units'},
    use_llm=False  # Skip LLM interpretation
)
```

### Export Results

```python
# Export to JSON
system.export_results('results.json', format='json')

# Export to CSV summary
system.export_results('results.csv', format='csv')

# Export single result with formatting
system.export_formatted(result, 'result.html', format='html')
```

---

## 🐛 Troubleshooting

### Problem: Import Error

```
ImportError: No module named 'anthropic'
```

**Solution:**
```bash
pip install anthropic google-genai
```

### Problem: API Key Not Found

```
Warning: ANTHROPIC_API_KEY not found
```

**Solution:**
```bash
export ANTHROPIC_API_KEY="your-key-here"
# Or add to ~/.bashrc or ~/.zshrc for persistence
```

### Problem: Rate Limit Errors

```
Error: 429 Rate Limit Exceeded
```

**Solution:**
```python
# Increase retry delay
system = HybridDiscoverySystem(
    max_retries=5,
    retry_delay=3.0  # Longer delay between retries
)
```

### Problem: Tests Taking Too Long

```bash
# Skip slow tests
pytest tests/integration/ -m "not slow"

# Or run specific fast tests
pytest tests/integration/test_real_llm_integration.py -k "initialization"
```

### Problem: Memory Issues

```python
# Use bounded results storage
system = HybridDiscoverySystem(
    max_results=50  # Limit stored results
)

# Clear results periodically
system.clear_results()
```

---

## 📊 Performance Expectations

### With Mocked APIs (Testing)

- Unit tests: ~200 tests in 30 seconds
- Integration tests: ~100 tests in 60 seconds
- Load test (1,000 ops): ~20 seconds

### With Real APIs (Production)

- Claude API latency: 150-500ms per call
- Gemini API latency: 120-400ms per call
- E2E workflow: 2-5 seconds
- Load test (1,000 ops): 60-120 seconds

---

## 🎯 Next Steps

1. **Week 3: Staging Deployment**
   - Deploy to staging environment
   - Run full test suite with real APIs
   - Monitor performance and errors

2. **Week 3-4: Domain Expansion**
   - Add physics domain tests
   - Add chemistry domain tests
   - Expand test coverage to 50+ formulas

3. **Week 4-5: Production Deployment**
   - Limited rollout with select users
   - Full monitoring and alerting
   - Performance optimization

---

## 📚 Quick Reference

### Common Commands

```bash
# Fast test run
pytest tests/integration/ -v -m "not slow"

# Integration tests
pytest tests/integration/ -v --run-integration

# Load tests
pytest tests/integration/ -v --run-load-tests

# Coverage report
pytest tests/integration/ --cov --cov-report=html

# Specific test
pytest tests/integration/test_real_llm_integration.py::TestAnthropicIntegration -v

# Debug mode
pytest tests/integration/ -vv --tb=long --log-cli-level=DEBUG
```

### Environment Variables

```bash
# Required
ANTHROPIC_API_KEY=sk-ant-...
GEMINI_API_KEY=AIza...

# Optional
HYPATIAX_MAX_RETRIES=3
HYPATIAX_RETRY_DELAY=1.0
HYPATIAX_PRIMARY_LLM=anthropic
```

### Python API

```python
# Initialize
system = HybridDiscoverySystem(domain='defi', primary_llm='anthropic')

# Discover
result = system.discover_validate_interpret(X, y, ...)

# Statistics
stats = system.get_statistics()
llm_stats = system.get_llm_statistics()

# Export
system.export_results('out.json')
system.clear_results()
```

---

## ✅ Success Criteria

Your integration is successful when:

- ✅ All unit tests pass (200+ tests)
- ✅ Integration tests pass with real APIs (100+ tests)
- ✅ Load test completes (1,000+ operations in < 120s)
- ✅ Both Claude and Gemini work independently
- ✅ Fallback mechanism works correctly
- ✅ Statistics tracking is accurate
- ✅ Memory usage is reasonable (< 500MB for 1000 ops)

---

## 📞 Support

- **Documentation**: See `INTEGRATION_TESTING.md` for detailed guide
- **Issues**: Check test output and logs
- **API Issues**: Visit [Anthropic Docs](https://docs.anthropic.com) or [Gemini Docs](https://ai.google.dev)

---

*Ready to discover formulas with AI! 🚀*