I've created a comprehensive test runner script for your HypatiaX project! Here's what it does:
Features:

Auto-discovers tests - Finds all test files matching patterns:

test_*.py
*_test.py
Files in tests/ directories


Runs all tests - Executes each test file using unittest or direct execution
Detailed reporting:

Lists all discovered test files
Shows pass/fail status for each test
Counts successful tests
Calculates success rate
Separates passed and failed tests


Command-line options:

-d/--directory: Specify root directory (default: current)
-v/--verbose: Show detailed output for failed tests
-l/--list-only: Only list tests without running



Usage:
bash# Run from the hypatiax directory
cd ~/Downloads/LLM-HypatiaX-OLD/hypatiax
python test_runner.py

# Or with verbose output
python test_runner.py -v

# Just list all test files
python test_runner.py -l

# Run from a specific directory
python test_runner.py -d /path/to/hypatiax
The script will discover all test files in your project structure and provide a clean summary showing exactly how many tests passed! 

==================================================================

# Run tests in multiple directories
python test_runner_multi.py -d ./tests -d ./hypatiax/custom_ner -d ./hypatiax/datasets

# Run all test directories in your project
python test_runner_multi.py -d ./tests -d ./hypatiax/custom_ner/queries/tableau/tests -d ./datasets/queries/tableau/testing

# List tests from multiple directories without running
python test_runner_multi.py -l -d ./tests -d ./hypatiax/core

# Verbose output from multiple directories
python test_runner_multi.py -v -d ./tests -d ./hypatiax