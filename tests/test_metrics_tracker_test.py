#!/usr/bin/env python3
"""
Test Metrics Tracker & Reporter
================================
Automatically tracks and reports test pass rates, coverage, and improvements over time.

Usage:
    python test_metrics_tracker.py
    python test_metrics_tracker.py --compare  # Compare with previous run
    python test_metrics_tracker.py --history  # Show historical trends
"""

import argparse
import json
import re
import subprocess
import sys
from dataclasses import asdict, dataclass
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Optional, Tuple


@dataclass
class TestMetrics:
    """Test execution metrics."""

    timestamp: str
    total_tests: int
    passed: int
    failed: int
    skipped: int
    errors: int
    pass_rate: float
    duration: float
    coverage_percent: Optional[float] = None
    coverage_lines_covered: Optional[int] = None
    coverage_lines_total: Optional[int] = None
    branch_coverage: Optional[float] = None

    def __str__(self) -> str:
        lines = [
            f"Timestamp: {self.timestamp}",
            f"Total Tests: {self.total_tests}",
            f"Passed: {self.passed} ({self.pass_rate:.1f}%)",
            f"Failed: {self.failed}",
            f"Skipped: {self.skipped}",
            f"Errors: {self.errors}",
            f"Duration: {self.duration:.2f}s",
        ]
        if self.coverage_percent is not None:
            lines.append(f"Coverage: {self.coverage_percent:.1f}%")
            if self.coverage_lines_covered and self.coverage_lines_total:
                lines.append(
                    f"Lines: {self.coverage_lines_covered}/{self.coverage_lines_total}"
                )
        if self.branch_coverage is not None:
            lines.append(f"Branch Coverage: {self.branch_coverage:.1f}%")
        return "\n".join(lines)


@dataclass
class TestComparison:
    """Comparison between two test runs."""

    current: TestMetrics
    previous: TestMetrics

    @property
    def pass_rate_change(self) -> float:
        return self.current.pass_rate - self.previous.pass_rate

    @property
    def coverage_change(self) -> Optional[float]:
        if self.current.coverage_percent and self.previous.coverage_percent:
            return self.current.coverage_percent - self.previous.coverage_percent
        return None

    @property
    def tests_added(self) -> int:
        return self.current.total_tests - self.previous.total_tests

    def __str__(self) -> str:
        lines = [
            "=" * 70,
            "TEST METRICS COMPARISON",
            "=" * 70,
            "",
            "CURRENT RUN:",
            "-" * 70,
            str(self.current),
            "",
            "PREVIOUS RUN:",
            "-" * 70,
            str(self.previous),
            "",
            "CHANGES:",
            "-" * 70,
        ]

        # Pass rate change
        pass_change = self.pass_rate_change
        pass_symbol = "📈" if pass_change > 0 else "📉" if pass_change < 0 else "➡️"
        lines.append(
            f"{pass_symbol} Pass Rate: {pass_change:+.1f}% "
            f"({self.previous.pass_rate:.1f}% → {self.current.pass_rate:.1f}%)"
        )

        # Coverage change
        if self.coverage_change is not None:
            cov_change = self.coverage_change
            cov_symbol = "📈" if cov_change > 0 else "📉" if cov_change < 0 else "➡️"
            lines.append(
                f"{cov_symbol} Coverage: {cov_change:+.1f}% "
                f"({self.previous.coverage_percent:.1f}% → {self.current.coverage_percent:.1f}%)"
            )

        # Tests added/removed
        tests_change = self.tests_added
        test_symbol = "➕" if tests_change > 0 else "➖" if tests_change < 0 else "➡️"
        lines.append(
            f"{test_symbol} Total Tests: {tests_change:+d} "
            f"({self.previous.total_tests} → {self.current.total_tests})"
        )

        # Failed tests change
        failed_change = self.current.failed - self.previous.failed
        failed_symbol = (
            "✅" if failed_change < 0 else "❌" if failed_change > 0 else "➡️"
        )
        lines.append(
            f"{failed_symbol} Failed Tests: {failed_change:+d} "
            f"({self.previous.failed} → {self.current.failed})"
        )

        # Duration change
        duration_change = self.current.duration - self.previous.duration
        duration_symbol = (
            "⚡" if duration_change < 0 else "🐌" if duration_change > 0 else "➡️"
        )
        lines.append(
            f"{duration_symbol} Duration: {duration_change:+.2f}s "
            f"({self.previous.duration:.2f}s → {self.current.duration:.2f}s)"
        )

        lines.append("=" * 70)
        return "\n".join(lines)


class TestMetricsTracker:
    """Tracks and reports test metrics over time."""

    def __init__(self, history_file: str = ".test_metrics_history.json"):
        self.history_file = Path(history_file)
        self.history: List[Dict] = self._load_history()

    def _load_history(self) -> List[Dict]:
        """Load test history from file."""
        if self.history_file.exists():
            try:
                with open(self.history_file, "r") as f:
                    return json.load(f)
            except Exception as e:
                print(f"Warning: Could not load history: {e}", file=sys.stderr)
        return []

    def _save_history(self):
        """Save test history to file."""
        try:
            with open(self.history_file, "w") as f:
                json.dump(self.history, f, indent=2)
        except Exception as e:
            print(f"Warning: Could not save history: {e}", file=sys.stderr)

    def run_tests(
        self,
        test_path: str = "tests/",
        with_coverage: bool = True,
        verbose: bool = True,
        extra_verbose: bool = False,
    ) -> TestMetrics:
        """Run tests and collect metrics."""
        print("Running tests...", flush=True)

        # Build pytest command
        cmd = ["pytest", test_path]

        # Add verbosity
        if extra_verbose:
            cmd.append("-vv")
        else:
            cmd.append("-v")

        cmd.append("--tb=short")

        if with_coverage:
            cmd.extend(
                [
                    "--cov=domains",
                    "--cov-report=term-missing",
                    "--cov-report=json",
                    "--cov-branch",
                ]
            )

        # Run tests
        start_time = datetime.now()
        result = subprocess.run(cmd, capture_output=True, text=True)
        end_time = datetime.now()
        duration = (end_time - start_time).total_seconds()

        # Parse output
        output = result.stdout + result.stderr

        if verbose:
            print("\n" + "=" * 70)
            print("TEST OUTPUT:")
            print("=" * 70)
            print(output)
            print("=" * 70 + "\n")

        # Extract test counts
        metrics = self._parse_test_output(output, duration)

        # Extract coverage if available
        if with_coverage:
            coverage_data = self._parse_coverage()
            if coverage_data:
                metrics.coverage_percent = coverage_data.get("coverage_percent")
                metrics.coverage_lines_covered = coverage_data.get("lines_covered")
                metrics.coverage_lines_total = coverage_data.get("lines_total")
                metrics.branch_coverage = coverage_data.get("branch_coverage")

        return metrics

    def _parse_test_output(self, output: str, duration: float) -> TestMetrics:
        """Parse pytest output to extract metrics."""
        timestamp = datetime.now().isoformat()

        # Extract test results using regex
        # Pattern: "31 passed in 3.35s" or "28 passed, 3 failed in 5.21s"
        patterns = {
            "passed": r"(\d+)\s+passed",
            "failed": r"(\d+)\s+failed",
            "skipped": r"(\d+)\s+skipped",
            "error": r"(\d+)\s+error",
        }

        counts = {}
        for key, pattern in patterns.items():
            match = re.search(pattern, output)
            counts[key] = int(match.group(1)) if match else 0

        total_tests = sum(counts.values())
        passed = counts["passed"]
        pass_rate = (passed / total_tests * 100) if total_tests > 0 else 0

        return TestMetrics(
            timestamp=timestamp,
            total_tests=total_tests,
            passed=passed,
            failed=counts["failed"],
            skipped=counts["skipped"],
            errors=counts["error"],
            pass_rate=pass_rate,
            duration=duration,
        )

    def _parse_coverage(self) -> Optional[Dict]:
        """Parse coverage data from coverage.json."""
        coverage_file = Path("coverage.json")
        if not coverage_file.exists():
            return None

        try:
            with open(coverage_file, "r") as f:
                data = json.load(f)

            totals = data.get("totals", {})

            lines_covered = totals.get("covered_lines", 0)
            lines_total = totals.get("num_statements", 0)
            coverage_percent = totals.get("percent_covered", 0)

            # Branch coverage if available
            branches_covered = totals.get("covered_branches", 0)
            branches_total = totals.get("num_branches", 0)
            branch_coverage = None
            if branches_total > 0:
                branch_coverage = (branches_covered / branches_total) * 100

            return {
                "coverage_percent": coverage_percent,
                "lines_covered": lines_covered,
                "lines_total": lines_total,
                "branch_coverage": branch_coverage,
            }
        except Exception as e:
            print(f"Warning: Could not parse coverage: {e}", file=sys.stderr)
            return None

    def save_metrics(self, metrics: TestMetrics):
        """Save metrics to history."""
        self.history.append(asdict(metrics))
        self._save_history()
        print(f"\n✅ Metrics saved to {self.history_file}")

    def get_latest(self) -> Optional[TestMetrics]:
        """Get the most recent metrics."""
        if not self.history:
            return None
        return TestMetrics(**self.history[-1])

    def get_comparison(self) -> Optional[TestComparison]:
        """Compare current with previous run."""
        if len(self.history) < 2:
            return None
        current = TestMetrics(**self.history[-1])
        previous = TestMetrics(**self.history[-2])
        return TestComparison(current, previous)

    def show_history(self, limit: int = 10):
        """Show historical trends."""
        if not self.history:
            print("No test history available.")
            return

        print("=" * 70)
        print("TEST METRICS HISTORY")
        print("=" * 70)
        print()

        # Show recent runs
        recent = self.history[-limit:]

        print(
            f"{'Date':<20} {'Tests':<8} {'Passed':<8} {'Failed':<8} "
            f"{'Pass%':<8} {'Cov%':<8} {'Duration':<10}"
        )
        print("-" * 70)

        for entry in recent:
            metrics = TestMetrics(**entry)
            date = metrics.timestamp[:19].replace("T", " ")
            cov = (
                f"{metrics.coverage_percent:.1f}" if metrics.coverage_percent else "N/A"
            )

            print(
                f"{date:<20} {metrics.total_tests:<8} {metrics.passed:<8} "
                f"{metrics.failed:<8} {metrics.pass_rate:<8.1f} "
                f"{cov:<8} {metrics.duration:<10.2f}s"
            )

        print("=" * 70)

        # Show trends
        if len(self.history) >= 2:
            first = TestMetrics(**self.history[0])
            last = TestMetrics(**self.history[-1])

            print("\nOVERALL TRENDS:")
            print("-" * 70)

            pass_change = last.pass_rate - first.pass_rate
            print(
                f"Pass Rate: {first.pass_rate:.1f}% → {last.pass_rate:.1f}% "
                f"({pass_change:+.1f}%)"
            )

            if last.coverage_percent and first.coverage_percent:
                cov_change = last.coverage_percent - first.coverage_percent
                print(
                    f"Coverage: {first.coverage_percent:.1f}% → "
                    f"{last.coverage_percent:.1f}% ({cov_change:+.1f}%)"
                )

            test_change = last.total_tests - first.total_tests
            print(
                f"Total Tests: {first.total_tests} → {last.total_tests} "
                f"({test_change:+d})"
            )

            print("=" * 70)

    def generate_report(self, output_file: Optional[str] = None):
        """Generate a detailed markdown report."""
        if not self.history:
            print("No test history available.")
            return

        latest = TestMetrics(**self.history[-1])

        lines = [
            "# Test Metrics Report",
            "",
            f"Generated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}",
            "",
            "## Current Metrics",
            "",
            "```",
            str(latest),
            "```",
            "",
        ]

        # Add comparison if available
        if len(self.history) >= 2:
            comparison = self.get_comparison()
            lines.extend(
                [
                    "## Comparison with Previous Run",
                    "",
                    "```",
                    str(comparison),
                    "```",
                    "",
                ]
            )

        # Add trend chart
        if len(self.history) >= 3:
            lines.extend(
                [
                    "## Historical Trends",
                    "",
                    "### Pass Rate Trend",
                    "",
                ]
            )

            for entry in self.history[-10:]:
                metrics = TestMetrics(**entry)
                date = metrics.timestamp[:10]
                bar_length = int(metrics.pass_rate / 2)
                bar = "█" * bar_length
                lines.append(f"{date}: {bar} {metrics.pass_rate:.1f}%")

            lines.append("")

            if any(TestMetrics(**e).coverage_percent for e in self.history[-10:]):
                lines.extend(
                    [
                        "### Coverage Trend",
                        "",
                    ]
                )

                for entry in self.history[-10:]:
                    metrics = TestMetrics(**entry)
                    if metrics.coverage_percent:
                        date = metrics.timestamp[:10]
                        bar_length = int(metrics.coverage_percent / 2)
                        bar = "█" * bar_length
                        lines.append(f"{date}: {bar} {metrics.coverage_percent:.1f}%")

                lines.append("")

        report = "\n".join(lines)

        if output_file:
            with open(output_file, "w") as f:
                f.write(report)
            print(f"\n📊 Report saved to {output_file}")
        else:
            print("\n" + report)


def main():
    """Main entry point."""
    parser = argparse.ArgumentParser(
        description="Track and report test metrics over time"
    )
    parser.add_argument(
        "--compare", "-c", action="store_true", help="Compare with previous run"
    )
    parser.add_argument(
        "--history", "-H", action="store_true", help="Show historical trends"
    )
    parser.add_argument(
        "--no-coverage", action="store_true", help="Skip coverage analysis (faster)"
    )
    parser.add_argument(
        "--test-path",
        "-p",
        default="tests/",
        help="Path to tests (default: tests/). Can be a specific file.",
    )
    parser.add_argument(
        "--verbose", "-v", action="store_true", help="Extra verbose pytest output"
    )
    parser.add_argument("--report", "-r", help="Generate markdown report to file")
    parser.add_argument(
        "--quiet", "-q", action="store_true", help="Suppress test output"
    )
    parser.add_argument(
        "--limit",
        "-l",
        type=int,
        default=10,
        help="Number of history entries to show (default: 10)",
    )

    args = parser.parse_args()

    tracker = TestMetricsTracker()

    # Show history only
    if args.history:
        tracker.show_history(limit=args.limit)
        return

    # Show comparison only
    if args.compare:
        comparison = tracker.get_comparison()
        if comparison:
            print(comparison)
        else:
            print("Need at least 2 test runs to compare.")
        return

    # Generate report only
    if args.report and not args.compare and not args.history:
        tracker.generate_report(args.report)
        return

    # Run tests and collect metrics
    print("🧪 Test Metrics Tracker")
    print("=" * 70)

    metrics = tracker.run_tests(
        test_path=args.test_path,
        with_coverage=not args.no_coverage,
        verbose=not args.quiet,
        extra_verbose=args.verbose,
    )

    # Save metrics
    tracker.save_metrics(metrics)

    # Display current metrics
    print("\n" + "=" * 70)
    print("CURRENT METRICS:")
    print("=" * 70)
    print(metrics)
    print("=" * 70)

    # Show comparison if available
    comparison = tracker.get_comparison()
    if comparison:
        print("\n" + str(comparison))

    # Generate report if requested
    if args.report:
        tracker.generate_report(args.report)

    # Show summary
    print("\n" + "=" * 70)
    print("SUMMARY:")
    print("=" * 70)

    if metrics.pass_rate == 100:
        print("🎉 All tests passing!")
    elif metrics.pass_rate >= 90:
        print("✅ Excellent test coverage!")
    elif metrics.pass_rate >= 80:
        print("👍 Good test coverage")
    elif metrics.pass_rate >= 70:
        print("⚠️  Needs improvement")
    else:
        print("❌ Critical: Low pass rate")

    if metrics.coverage_percent:
        if metrics.coverage_percent >= 90:
            print("🎯 Excellent code coverage!")
        elif metrics.coverage_percent >= 80:
            print("✅ Good code coverage")
        elif metrics.coverage_percent >= 70:
            print("👍 Acceptable code coverage")
        else:
            print("⚠️  Low code coverage")

    if comparison:
        if comparison.pass_rate_change > 0:
            print(f"📈 Improved by {comparison.pass_rate_change:.1f}%")
        elif comparison.pass_rate_change < 0:
            print(f"📉 Decreased by {abs(comparison.pass_rate_change):.1f}%")


if __name__ == "__main__":
    main()
