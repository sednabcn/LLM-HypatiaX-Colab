#!/bin/bash
# Run Ensemble Validator Tests with Metrics Tracking
# Usage: bash run_ensemble_tests.sh

echo "🧪 Running Ensemble Validator Test Suite..."
echo "=========================================="
echo ""

# Option 1: Run tests directly with pytest (recommended first)
echo "Running pytest directly..."
pytest tests/unit/validators/test_ensemble_validator.py -v --tb=short --cov=hypatiax.tools.validation.ensemble_validator --cov-report=term-missing --cov-report=json

echo ""
echo "=========================================="
echo ""

# Check if test ran successfully
if [ $? -eq 0 ]; then
    echo "✅ Tests completed successfully!"
else
    echo "❌ Tests encountered errors"
fi

echo ""
echo "To track metrics over time, run:"
echo "python test_metrics_tracker_test.py -p tests/unit/validators/test_ensemble_validator.py --report ensemble_validator_report.md"
