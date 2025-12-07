Create `tests/QUICK_REFERENCE.md`:

```markdown
# Test Quick Reference

## Common Commands

```bash
# Run all tests
pytest

# Run fast tests only
pytest -m "not slow"

# Run specific domain
pytest tests/unit/symbolic/

# Run with coverage
pytest --cov=hypatiax

# Run and stop on first failure
pytest -x

# Run last failed tests
pytest --lf

# Show print statements
pytest -s

# Very verbose
pytest -vv
Finding Fixtures
All fixtures in tests/fixtures/domain/:
    • LLM: tests/fixtures/llm/
    • NER: tests/fixtures/ner/
    • Symbolic: tests/fixtures/symbolic/
    • DeFi: tests/fixtures/defi/
Writing New Tests
    1. Choose location: tests/{unit|integration|e2e}/domain/
    2. Create test file: test_feature_name.py
    3. Use fixtures: def test_something(fixture_name):
    4. Run: pytest tests/unit/domain/test_feature_name.py
Adding Fixtures
    1. Choose domain: tests/fixtures/domain/
    2. Add to appropriate file: fixtures.py
    3. Import in registry: tests/fixtures/conftest.py
    4. Use in tests: Automatic discovery!

---
### Step 10.1: Run Complete Test Suite
```bash
# Run everything
pytest tests/ -v --tb=short

# Generate coverage report
pytest tests/ --cov=hypatiax --cov-report=html --cov-report=term

# Check coverage
open htmlcov/index.html  # or xdg-open on Linux
