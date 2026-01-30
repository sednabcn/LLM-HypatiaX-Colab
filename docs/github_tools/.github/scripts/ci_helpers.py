#!/usr/bin/env python3
"""
CI Helper Scripts for GitHub Actions Integration
=================================================
Practical scripts to use in your .github/workflows
"""

import os
import sys
import json
from pathlib import Path
from datetime import datetime
from ci_rate_limit_config import TestScheduler, ExecutionTier, StorageManager


# ============================================================================
# Script 1: check_limits.py - Check if tests should run
# ============================================================================


def check_limits():
    """Check if test execution should proceed based on limits."""
    import argparse

    parser = argparse.ArgumentParser()
    parser.add_argument("--tier", required=True, choices=["free", "team", "enterprise"])
    parser.add_argument(
        "--type",
        required=True,
        choices=["quick_smoke", "standard", "comprehensive", "deep_stability"],
    )
    parser.add_argument("--force", action="store_true", help="Force execution")
    args = parser.parse_args()

    # Map string to enum
    exec_type_map = {
        "quick_smoke": ExecutionTier.QUICK_SMOKE,
        "standard": ExecutionTier.STANDARD,
        "comprehensive": ExecutionTier.COMPREHENSIVE,
        "deep_stability": ExecutionTier.DEEP_STABILITY,
    }
    exec_type = exec_type_map[args.type]

    # Initialize scheduler
    scheduler = TestScheduler(tier=args.tier, config_file=".ci/test_schedule.json")

    # Check if we should run
    should_run, reason = scheduler.should_run(exec_type, force=args.force)

    if should_run:
        print(f"✅ PROCEED: {reason}")

        # Output for GitHub Actions
        if "GITHUB_OUTPUT" in os.environ:
            with open(os.environ["GITHUB_OUTPUT"], "a") as f:
                f.write(f"should_run=true\n")

        # Show usage
        usage = scheduler.get_monthly_usage_report()
        print(
            f"\n📊 Current Usage: {usage['minutes_used']}/{usage['minutes_limit']} min "
            f"({usage['percentage_used']:.1f}%)"
        )

        sys.exit(0)
    else:
        print(f"⏭️  SKIP: {reason}")

        if "GITHUB_OUTPUT" in os.environ:
            with open(os.environ["GITHUB_OUTPUT"], "a") as f:
                f.write(f"should_run=false\n")

        sys.exit(0)  # Exit 0 so workflow doesn't fail


# ============================================================================
# Script 2: record_execution.py - Record test execution
# ============================================================================


def record_execution():
    """Record that tests were executed."""
    import argparse

    parser = argparse.ArgumentParser()
    parser.add_argument("--tier", required=True)
    parser.add_argument("--type", required=True)
    parser.add_argument("--duration", type=int, help="Duration in minutes")
    args = parser.parse_args()

    exec_type_map = {
        "quick_smoke": ExecutionTier.QUICK_SMOKE,
        "standard": ExecutionTier.STANDARD,
        "comprehensive": ExecutionTier.COMPREHENSIVE,
        "deep_stability": ExecutionTier.DEEP_STABILITY,
    }
    exec_type = exec_type_map[args.type]

    scheduler = TestScheduler(tier=args.tier, config_file=".ci/test_schedule.json")

    # If duration not provided, estimate
    duration = args.duration or scheduler._get_estimated_minutes(exec_type)

    scheduler.record_execution(exec_type, duration)

    usage = scheduler.get_monthly_usage_report()
    print(f"📝 Recorded execution: {duration} minutes")
    print(
        f"📊 Monthly total: {usage['minutes_used']}/{usage['minutes_limit']} min "
        f"({usage['percentage_used']:.1f}%)"
    )

    # Warn if approaching limit
    if usage["percentage_used"] > 80:
        print(f"\n⚠️  WARNING: Approaching monthly limit!")
        print(f"   Only {usage['minutes_remaining']} minutes remaining")

    # Create annotation for GitHub Actions
    if "GITHUB_STEP_SUMMARY" in os.environ:
        with open(os.environ["GITHUB_STEP_SUMMARY"], "a") as f:
            f.write(
                f"""
## Monthly CI Usage

- **Used:** {usage["minutes_used"]} / {usage["minutes_limit"]} minutes
- **Percentage:** {usage["percentage_used"]:.1f}%
- **Remaining:** {usage["minutes_remaining"]} minutes
- **Reset Date:** {usage["reset_date"]}
"""
            )


# ============================================================================
# Script 3: cleanup_artifacts.py - Clean up old artifacts
# ============================================================================


def cleanup_artifacts():
    """Clean up old test artifacts."""
    import argparse

    parser = argparse.ArgumentParser()
    parser.add_argument("--tier", required=True)
    parser.add_argument("--keep-last", type=int, default=3, help="Keep last N runs")
    parser.add_argument(
        "--keep-days", type=int, default=14, help="Keep files from last N days"
    )
    args = parser.parse_args()

    # Get storage limit for tier
    limits_map = {"free": 500, "team": 2000, "enterprise": 50000}
    max_storage = limits_map.get(args.tier, 500)

    manager = StorageManager(max_storage_mb=max_storage, artifacts_dir="artifacts")

    print(f"\n🧹 Starting artifact cleanup...")
    manager.cleanup_old_artifacts(keep_last_n=args.keep_last, keep_days=args.keep_days)

    final_usage = manager.get_current_usage_mb()
    print(f"\n✅ Cleanup complete")
    print(
        f"📦 Final storage: {final_usage:.1f}/{max_storage} MB ({final_usage / max_storage * 100:.1f}%)"
    )


# ============================================================================
# Script 4: smart_test_selector.py - Select tests based on changes
# ============================================================================


def smart_test_selector():
    """Select which tests to run based on file changes."""
    import argparse
    import subprocess

    parser = argparse.ArgumentParser()
    parser.add_argument("--base", default="main", help="Base branch")
    parser.add_argument("--head", default="HEAD", help="Head branch")
    args = parser.parse_args()

    # Get changed files
    try:
        result = subprocess.run(
            ["git", "diff", "--name-only", f"{args.base}...{args.head}"],
            capture_output=True,
            text=True,
            check=True,
        )
        changed_files = result.stdout.strip().split("\n")
    except subprocess.CalledProcessError:
        print("⚠️  Could not determine changed files, running all tests")
        print("all")
        sys.exit(0)

    print(f"📝 Changed files: {len(changed_files)}")

    # Categorize changes
    domains_affected = set()
    core_changed = False
    docs_only = True

    for file in changed_files:
        if not file:
            continue

        print(f"   {file}")

        if file.startswith("docs/") or file.endswith(".md"):
            continue

        docs_only = False

        if "mechanics" in file.lower():
            domains_affected.add("mechanics")
        elif "chemistry" in file.lower():
            domains_affected.add("chemistry")
        elif "biology" in file.lower():
            domains_affected.add("biology")
        elif "quantum" in file.lower():
            domains_affected.add("quantum")
        elif "electromagnetism" in file.lower():
            domains_affected.add("electromagnetism")
        elif "thermodynamics" in file.lower():
            domains_affected.add("thermodynamics")

        if any(
            core in file for core in ["hybrid_system", "symbolic_engine", "validator"]
        ):
            core_changed = True

    # Determine test selection
    if docs_only:
        print("\n✅ Documentation-only changes, skipping tests")
        print("skip")
    elif core_changed:
        print("\n⚠️  Core system changes detected, running ALL tests")
        print("all")
    elif domains_affected:
        print(f"\n🎯 Domain-specific changes: {', '.join(domains_affected)}")
        print(",".join(domains_affected))
    else:
        print("\n🔍 Non-domain changes, running critical tests")
        print("critical")

    # Output for GitHub Actions
    if "GITHUB_OUTPUT" in os.environ:
        selection = (
            "all"
            if core_changed
            else "critical" if not domains_affected else ",".join(domains_affected)
        )
        with open(os.environ["GITHUB_OUTPUT"], "a") as f:
            f.write(f"test_selection={selection}\n")
            f.write(f"skip_tests={'true' if docs_only else 'false'}\n")


# ============================================================================
# Script 5: generate_pr_comment.py - Generate PR comment with results
# ============================================================================


def generate_pr_comment():
    """Generate a formatted PR comment with test results."""
    import argparse

    parser = argparse.ArgumentParser()
    parser.add_argument("--report", required=True, help="Path to test report JSON")
    parser.add_argument("--output", default="pr_comment.md", help="Output file")
    args = parser.parse_args()

    # Load report
    with open(args.report, "r") as f:
        report = json.load(f)

    metadata = report["metadata"]
    summary = report["summary"]

    # Build comment
    comment = f"""## 🧪 Test Results

**Status:** {"✅ PASSED" if metadata["passed"] == metadata["total_tests"] else "❌ FAILED"}

| Metric | Value |
|--------|-------|
| Tests Run | {metadata["total_tests"]} |
| Passed | {metadata["passed"]} ✅ |
| Failed | {metadata["failed"]} ❌ |
| Pass Rate | {summary["pass_rate"] * 100:.1f}% |
| Stable Tests | {summary["stable_tests"]} |
| Flaky Tests | {summary["flaky_tests"]} ⚠️ |

"""

    # Add regression info
    if summary.get("regressions", 0) > 0:
        comment += f"""
### ⚠️ Regressions Detected: {summary["regressions"]}

"""
        for reg in report.get("regressions", [])[:5]:  # Top 5
            comment += f"- **{reg['test_name']}** [{reg['severity'].upper()}]: "
            comment += f"R² {reg['baseline_r2']:.3f} → {reg['current_r2']:.3f} "
            comment += f"(Δ {reg['r2_delta']:+.3f})\n"

    # Add flaky test warnings
    if summary.get("flaky_tests", 0) > 0:
        comment += f"""
### 🔄 Flaky Tests Warning: {summary["flaky_tests"]}

These tests show inconsistent results across runs. Consider investigating.

"""
        for flaky in report.get("flaky_tests", [])[:3]:  # Top 3
            metrics = flaky["metrics"]
            comment += f"- **{flaky['test_name']}**: {metrics['pass_rate'] * 100:.0f}% pass rate "
            comment += f"(R² σ={metrics['r2_std']:.4f})\n"

    comment += """
---
<details>
<summary>📊 View detailed results</summary>

"""

    # Add test details
    for result in report.get("test_results", []):
        status = "✅" if result["passed"] else "❌"
        comment += f"\n**{status} {result['test_name']}**\n"
        comment += f"- R²: {result['discovery_r2']:.4f}\n"
        comment += f"- Validation: {result['validation_score']:.1f}/100\n"
        if result.get("discovered_expression"):
            comment += f"- Expression: `{result['discovered_expression']}`\n"

    comment += "\n</details>"

    # Save comment
    with open(args.output, "w") as f:
        f.write(comment)

    print(f"✅ Generated PR comment: {args.output}")


# ============================================================================
# Script 6: alert_on_limit.py - Send alert when approaching limit
# ============================================================================


def alert_on_limit():
    """Check usage and alert if approaching limit."""
    import argparse

    parser = argparse.ArgumentParser()
    parser.add_argument("--tier", required=True)
    parser.add_argument(
        "--threshold", type=float, default=0.8, help="Alert threshold (0-1)"
    )
    args = parser.parse_args()

    scheduler = TestScheduler(tier=args.tier, config_file=".ci/test_schedule.json")
    usage = scheduler.get_monthly_usage_report()

    if usage["percentage_used"] / 100 >= args.threshold:
        print(f"\n🚨 ALERT: CI usage at {usage['percentage_used']:.1f}%")
        print(f"   Used: {usage['minutes_used']}/{usage['minutes_limit']} minutes")
        print(f"   Remaining: {usage['minutes_remaining']} minutes")

        # Create GitHub warning
        if "GITHUB_ENV" in os.environ:
            print(
                f"::warning::CI usage at {usage['percentage_used']:.1f}% "
                f"({usage['minutes_remaining']} minutes remaining)"
            )

        # You could integrate with Slack, Discord, email, etc. here
        # send_slack_alert(usage)

        sys.exit(1)  # Exit with error to get attention
    else:
        print(f"✅ Usage OK: {usage['percentage_used']:.1f}%")
        sys.exit(0)


# ============================================================================
# Main CLI
# ============================================================================

if __name__ == "__main__":
    import sys

    if len(sys.argv) < 2:
        print("Usage: ci_helpers.py <command>")
        print("\nCommands:")
        print("  check-limits       - Check if tests should run")
        print("  record-execution   - Record test execution")
        print("  cleanup-artifacts  - Clean up old artifacts")
        print("  smart-selector     - Select tests based on changes")
        print("  generate-comment   - Generate PR comment")
        print("  alert-on-limit     - Alert if approaching limit")
        sys.exit(1)

    command = sys.argv[1]
    sys.argv = [sys.argv[0]] + sys.argv[2:]  # Remove command from args

    commands = {
        "check-limits": check_limits,
        "record-execution": record_execution,
        "cleanup-artifacts": cleanup_artifacts,
        "smart-selector": smart_test_selector,
        "generate-comment": generate_pr_comment,
        "alert-on-limit": alert_on_limit,
    }

    if command in commands:
        commands[command]()
    else:
        print(f"❌ Unknown command: {command}")
        sys.exit(1)
