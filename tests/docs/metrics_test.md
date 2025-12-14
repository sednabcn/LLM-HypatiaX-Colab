To apply the test metrics tracker only for test_edge_cases.py with verbose output, use:
bash# Run tracker on specific test file
python test_metrics_tracker.py --test-path tests/unit/validators/test_edge_cases.py -v

# Or with the full path (adjust based on your structure)
python test_metrics_tracker.py --test-path tests/unit/validators/test_edge_cases.py
However, I notice the -v flag in the tracker is for verbose test output (which is already default). If you want pytest's verbose mode, the tracker already includes it.
If you want to customize it further, here's an updated version that gives you more control:Test Metrics Tracker & ReporterCode ∙ Version 2     parser.add_argument(
        '--test-path', '-p',
        default='tests/',
        help='Path to tests (default: tests/). Can be a specific file.'
    )
    parser.add_argument(
        '--verbose', '-v',
        action='store_true',
        helTest Metrics Tracker & ReporterCode ∙ Version 4     metrics = tracker.run_tests(
        test_path=args.test_path,
        with_coverage=not args.no_coverage,
        verbose=not args.quiet,
        extra_verbose=args.verbose
    )Perfect! Now you can use it like this:
For test_edge_cases.py specifically:
bash# Basic run
python test_metrics_tracker_test.py --test-path tests/unit/validators/test_edge_cases.py

# With extra verbose output (-vv in pytest)
python test_metrics_tracker_test.py --test-path tests/unit/validators/test_edge_cases.py -v

# Without coverage (faster)
python test_metrics_tracker_test.py --test-path tests/unit/validators/test_edge_cases.py --no-coverage

# Quiet mode (suppress test output, only show metrics)
python test_metrics_tracker_test.py --test-path tests/unit/validators/test_edge_cases.py -q

# With everything
python test_metrics_tracker_test.py -p tests/unit/validators/test_edge_cases.py -v
Quick Commands:
bash# Track edge cases only
python test_metrics_tracker.py -p tests/unit/validators/test_edge_cases.py

# Compare with previous edge case run
python test_metrics_tracker_test.py --compare

# See history
python test_metrics_tracker_test.py --history

# Generate report for edge cases
python test_metrics_tracker_test.py -p tests/unit/validators/test_edge_cases.py --report edge_cases_report.md
```

The tracker will now:
1. Run **only** `test_edge_cases.py`
2. Track its 31 tests (100% pass rate)
3. Store metrics separately in history
4. Show comparisons over time

You'll see output like:
```
🧪 Test Metrics Tracker
======================================================================
Running tests...
...
======================================================================
CURRENT METRICS:
======================================================================
Timestamp: 2024-12-09T...
Total Tests: 31
Passed: 31 (100.0%)
Failed: 0
...
🎉 All tests passing!
