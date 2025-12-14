To see the test pass rate and coverage metrics, you can run pytest with coverage reporting. Here are the commands:
View Test Pass Rate
bash# Run all tests with summary statistics
pytest tests/ -v --tb=short

# Get a detailed summary with pass/fail counts
pytest tests/ --tb=short -q

# Run with coverage report
pytest tests/ --cov=domains --cov-report=term-missing

# Generate an HTML coverage report (more detailed)
pytest tests/ --cov=domains --cov-report=html

# View coverage with branch coverage
pytest tests/ --cov=domains --cov-branch --cov-report=term
See Overall Statistics
bash# Summary of all tests
pytest tests/ -v --tb=line | tail -20

# Count passing vs failing tests
pytest tests/ --collect-only -q | wc -l  # Total tests
pytest tests/ -q | grep "passed"  # Pass count
For the Edge Cases Specifically
From your output, you can already see:

31 passed in 3.35s = 100% pass rate for edge case tests ✅

To see the overall project pass rate across all test files:
bash# Run all tests and see summary
pytest tests/ -v --tb=short

# Or for a cleaner summary
pytest tests/ -q --tb=line

# With timing information
pytest tests/ --durations=10 -v
To Track Improvement Over Time
bash# Generate a detailed report
pytest tests/ --cov=domains --cov-report=term-missing --cov-report=html -v > test_report.txt

# Then check the HTML report
open htmlcov/index.html  # On macOS
xdg-open htmlcov/index.html  # On Linux
The 71.4% → 80%+ improvement you mentioned likely refers to:

Code coverage percentage (lines of code tested)
Test pass rate (passing tests / total tests)
