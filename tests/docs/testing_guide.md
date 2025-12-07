# HypatiaX Testing Guide

## Test Structure

tests_new/ ├── unit/ # Fast, isolated tests ├── integration/ # Tests with dependencies ├── e2e/ # Full system tests ├── benchmark/ # Performance tests └── fixtures/ # Reusable test data

## Running Tests

### Run All Tests

```bash
pytest tests_new/
Run by Test Level
# Unit tests only (fast)
pytest tests_new/unit/

# Integration tests (slower)
pytest tests_new/integration/

# E2E tests (slowest)
pytest tests_new/e2e/
Run by Domain
# LLM tests
pytest tests_new/unit/llm/ tests_new/integration/llm/

# NER tests
pytest tests_new/unit/ner/ tests_new/integration/ner/

# Symbolic tests
pytest tests_new/unit/symbolic/ tests_new/integration/symbolic/
Run by Marker
# Fast tests only
pytest tests_new/ -m "not slow"

# Specific domain
pytest tests_new/ -m "llm"

# Multiple markers
pytest tests_new/ -m "unit and symbolic"
Writing Tests
Unit Test Example
# tests_new/unit/symbolic/test_new_feature.py
def test_formula_parsing(basic_formulas, formula_parser):
    \"\"\"Test formula parsing with basic formulas\"\"\"
    for formula in basic_formulas:
        result = formula_parser.parse(formula)
        assert result is not None
Using Fixtures
Fixtures are auto-discovered from:
    • tests_new/fixtures/domain/
    • tests_new/unit/domain/conftest.py
    • tests_new/integration/domain/conftest.py
def test_with_fixtures(anthropic_response, symbolic_engine):
    # Fixtures automatically injected by pytest
    result = symbolic_engine.evaluate(anthropic_response)
    assert result
Creating New Fixtures
Add fixtures to appropriate domain:
# tests_new/fixtures/symbolic/formulas/fixtures.py
@pytest.fixture
def my_new_formula_fixture():
    return "x^2 + 2*x + 1"
Fixture is now available in all tests automatically!
