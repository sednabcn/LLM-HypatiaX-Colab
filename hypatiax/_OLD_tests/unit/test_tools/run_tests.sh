#!/bin/bash
# run_tests.sh - Run pytest with the correct Python environment

set -e  # Exit on error

echo "🔧 Python Environment Test Runner"
echo "=================================="
echo ""

# Colors
GREEN='\033[0;32m'
RED='\033[0;31m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# Check if virtual environment is active
if [ -z "$VIRTUAL_ENV" ]; then
    echo -e "${RED}❌ No virtual environment detected!${NC}"
    echo "Please activate your virtual environment first:"
    echo "  source ~/Downloads/py312/bin/activate"
    exit 1
fi

echo -e "${GREEN}✓ Virtual environment active: $VIRTUAL_ENV${NC}"
echo ""

# Get Python and pytest paths
PYTHON_PATH=$(which python)
VENV_PYTEST="$VIRTUAL_ENV/bin/pytest"

echo "Python path: $PYTHON_PATH"
echo "Looking for pytest in venv: $VENV_PYTEST"
echo ""

# Check if pytest is installed in venv
if [ ! -f "$VENV_PYTEST" ]; then
    echo -e "${YELLOW}⚠️  pytest not found in virtual environment${NC}"
    echo "Installing pytest..."
    pip install pytest
    echo ""
fi

# Verify pysr is available
echo "Checking dependencies..."
python -c "from pysr import PySRRegressor; print('✓ pysr found')" 2>/dev/null
if [ $? -ne 0 ]; then
    echo -e "${RED}❌ pysr not found in this environment${NC}"
    echo "Installing pysr..."
    pip install pysr
    echo ""
else
    echo -e "${GREEN}✓ pysr available${NC}"
fi

python -c "import numpy; print('✓ numpy found')" 2>/dev/null || pip install numpy
echo ""

# Run pytest using python -m pytest to ensure correct environment
echo "Running tests..."
echo "=================================="
python -m pytest hypatiax/tests/unit/test_tools/test_symbolic_engine.py -v "$@"

exit_code=$?

if [ $exit_code -eq 0 ]; then
    echo ""
    echo -e "${GREEN}✅ All tests passed!${NC}"
else
    echo ""
    echo -e "${RED}❌ Some tests failed (exit code: $exit_code)${NC}"
fi

exit $exit_code
