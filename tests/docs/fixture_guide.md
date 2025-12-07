```markdown
# Fixture Organization Guide

## Fixture Locations

### Domain Fixtures
Located in `tests_new/fixtures/domain/`:
- `llm/` - LLM provider fixtures
- `ner/` - NER entity and sentence fixtures
- `symbolic/` - Formula and expression fixtures
- `defi/` - DeFi protocol and risk fixtures
- `data/` - Dataset fixtures
- `models/` - ML model fixtures
- `common/` - Shared utilities

### Test-Level Fixtures
Located in `conftest.py` at each level:
- `tests_new/unit/domain/conftest.py` - Unit test fixtures
- `tests_new/integration/domain/conftest.py` - Integration fixtures
- `tests_new/e2e/conftest.py` - E2E fixtures

## Adding New Fixtures

### Step 1: Choose Location
- Reused across many tests? → `tests_new/fixtures/domain/`
- Specific to test level? → `tests_new/unit|integration/domain/conftest.py`

### Step 2: Create Fixture
```python
@pytest.fixture
def my_fixture():
    return "test data"
Step 3: Import in Registry (if in fixtures/)
# tests_new/fixtures/conftest.py
from tests_new.fixtures.domain.module import *
Step 4: Use in Tests
def test_something(my_fixture):
    assert my_fixture == "test data"
Fixture Scopes
    • function (default) - New instance per test
    • class - Shared within test class
    • module - Shared within test file
    • session - Shared across entire test run
Example:
@pytest.fixture(scope="session")
def expensive_setup():
    # Runs once for entire test session
    return setup_database()
