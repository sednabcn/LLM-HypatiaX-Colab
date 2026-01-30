#!/usr/bin/env python3
"""
CI/CD Rate Limiting and Resource Management Configuration
=========================================================
Manages test execution frequency and resource usage for private repos
to avoid hitting GitHub Actions, storage, and API limits.

Author: HypatiaX Team
Date: 2026-01-03
"""

import os
import json
import time
from pathlib import Path
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Tuple
from dataclasses import dataclass
from enum import Enum


# ============================================================================
# EXECUTION STRATEGIES
# ============================================================================


class ExecutionTier(Enum):
    """Different test execution tiers with different resource usage."""

    QUICK_SMOKE = "quick_smoke"  # 1-2 min, critical tests only
    STANDARD = "standard"  # 5-10 min, important tests
    COMPREHENSIVE = "comprehensive"  # 20-30 min, all tests
    DEEP_STABILITY = "deep_stability"  # 1-2 hours, multiple runs for stability


@dataclass
class ResourceLimits:
    """Resource limits for different environments."""

    max_execution_time_minutes: int
    max_storage_mb: int
    max_api_calls_per_hour: int
    max_retries_per_test: int
    max_parallel_jobs: int

    @classmethod
    def for_github_free(cls):
        """GitHub Free tier limits."""
        return cls(
            max_execution_time_minutes=6 * 60,  # 6 hours/month = ~360 min
            max_storage_mb=500,  # 500 MB storage
            max_api_calls_per_hour=1000,  # Conservative API limit
            max_retries_per_test=2,
            max_parallel_jobs=1,
        )

    @classmethod
    def for_github_team(cls):
        """GitHub Team tier limits."""
        return cls(
            max_execution_time_minutes=3000,  # 3000 min/month
            max_storage_mb=2000,  # 2 GB storage
            max_api_calls_per_hour=5000,
            max_retries_per_test=3,
            max_parallel_jobs=2,
        )

    @classmethod
    def for_github_enterprise(cls):
        """GitHub Enterprise tier limits."""
        return cls(
            max_execution_time_minutes=50000,  # 50000 min/month
            max_storage_mb=50000,  # 50 GB storage
            max_api_calls_per_hour=15000,
            max_retries_per_test=5,
            max_parallel_jobs=4,
        )


# ============================================================================
# FREQUENCY SCHEDULER
# ============================================================================


class TestScheduler:
    """
    Manages test execution frequency to stay within limits.

    Recommended frequencies:
    - QUICK_SMOKE: Every commit (PR checks)
    - STANDARD: Daily (scheduled)
    - COMPREHENSIVE: Weekly (Sunday nights)
    - DEEP_STABILITY: Monthly (1st of month)
    """

    def __init__(self, tier: str = "free", config_file: str = ".ci/test_schedule.json"):
        self.tier = tier
        self.config_file = config_file
        self.limits = self._get_limits(tier)
        self.schedule = self._load_schedule()

    def _get_limits(self, tier: str) -> ResourceLimits:
        """Get resource limits based on tier."""
        limits_map = {
            "free": ResourceLimits.for_github_free(),
            "team": ResourceLimits.for_github_team(),
            "enterprise": ResourceLimits.for_github_enterprise(),
        }
        return limits_map.get(tier, ResourceLimits.for_github_free())

    def _load_schedule(self) -> Dict:
        """Load execution schedule from config."""
        if Path(self.config_file).exists():
            with open(self.config_file, "r") as f:
                return json.load(f)

        # Default schedule
        return {
            "last_runs": {},
            "monthly_minutes_used": 0,
            "monthly_reset_date": datetime.now().replace(day=1).isoformat(),
        }

    def _save_schedule(self):
        """Save schedule to config file."""
        Path(self.config_file).parent.mkdir(parents=True, exist_ok=True)
        with open(self.config_file, "w") as f:
            json.dump(self.schedule, f, indent=2)

    def should_run(
        self, execution_type: ExecutionTier, force: bool = False
    ) -> Tuple[bool, str]:
        """
        Determine if a test suite should run based on schedule and limits.

        Returns:
            (should_run, reason)
        """
        if force:
            return True, "Forced execution"

        # Check monthly budget
        reset_date = datetime.fromisoformat(self.schedule["monthly_reset_date"])
        if datetime.now().month != reset_date.month:
            # Reset monthly counter
            self.schedule["monthly_minutes_used"] = 0
            self.schedule["monthly_reset_date"] = (
                datetime.now().replace(day=1).isoformat()
            )
            self._save_schedule()

        # Estimate execution time for this tier
        estimated_minutes = self._get_estimated_minutes(execution_type)

        if (
            self.schedule["monthly_minutes_used"] + estimated_minutes
            > self.limits.max_execution_time_minutes
        ):
            return (
                False,
                f"Monthly limit reached ({self.schedule['monthly_minutes_used']}/{self.limits.max_execution_time_minutes} min used)",
            )

        # Check last run time
        last_run_key = execution_type.value
        if last_run_key in self.schedule["last_runs"]:
            last_run = datetime.fromisoformat(self.schedule["last_runs"][last_run_key])
            min_interval = self._get_min_interval(execution_type)

            if datetime.now() - last_run < min_interval:
                next_run = last_run + min_interval
                return (
                    False,
                    f"Too soon. Next run: {next_run.strftime('%Y-%m-%d %H:%M')}",
                )

        return True, "Schedule check passed"

    def _get_estimated_minutes(self, execution_type: ExecutionTier) -> int:
        """Estimate execution time for tier."""
        estimates = {
            ExecutionTier.QUICK_SMOKE: 2,
            ExecutionTier.STANDARD: 8,
            ExecutionTier.COMPREHENSIVE: 25,
            ExecutionTier.DEEP_STABILITY: 90,
        }
        return estimates.get(execution_type, 10)

    def _get_min_interval(self, execution_type: ExecutionTier) -> timedelta:
        """Get minimum interval between runs for this tier."""
        intervals = {
            ExecutionTier.QUICK_SMOKE: timedelta(minutes=5),  # Can run frequently
            ExecutionTier.STANDARD: timedelta(hours=20),  # ~Daily
            ExecutionTier.COMPREHENSIVE: timedelta(days=6),  # ~Weekly
            ExecutionTier.DEEP_STABILITY: timedelta(days=28),  # ~Monthly
        }
        return intervals.get(execution_type, timedelta(days=1))

    def record_execution(self, execution_type: ExecutionTier, actual_minutes: int):
        """Record that a test suite was executed."""
        self.schedule["last_runs"][execution_type.value] = datetime.now().isoformat()
        self.schedule["monthly_minutes_used"] += actual_minutes
        self._save_schedule()

    def get_monthly_usage_report(self) -> Dict:
        """Get monthly usage statistics."""
        used = self.schedule["monthly_minutes_used"]
        limit = self.limits.max_execution_time_minutes

        return {
            "minutes_used": used,
            "minutes_limit": limit,
            "percentage_used": (used / limit * 100) if limit > 0 else 0,
            "minutes_remaining": max(0, limit - used),
            "reset_date": self.schedule["monthly_reset_date"],
            "tier": self.tier,
        }


# ============================================================================
# TEST CONFIGURATION BY TIER
# ============================================================================


class TieredTestConfig:
    """Configure test parameters based on execution tier."""

    @staticmethod
    def get_config(execution_type: ExecutionTier, limits: ResourceLimits) -> Dict:
        """Get test configuration for execution tier."""

        if execution_type == ExecutionTier.QUICK_SMOKE:
            return {
                "test_selection": "critical_only",  # 5-8 most critical tests
                "max_retries": 1,
                "num_samples": 200,  # Reduced data size
                "timeout_per_test": 20,  # seconds
                "enable_deep_analysis": False,
                "save_detailed_logs": False,
                "generate_plots": False,
                "tests_to_run": [
                    "mechanics_kinetic_energy",
                    "chemistry_ideal_gas_law",
                    "electromagnetism_coulombs_law",
                    "thermodynamics_stefan_boltzmann",
                    "quantum_planck",
                ],
            }

        elif execution_type == ExecutionTier.STANDARD:
            return {
                "test_selection": "high_priority",  # 15-20 important tests
                "max_retries": min(2, limits.max_retries_per_test),
                "num_samples": 300,
                "timeout_per_test": 45,
                "enable_deep_analysis": False,
                "save_detailed_logs": True,
                "generate_plots": False,
                "tests_to_run": "domain_critical",  # Critical tests per domain
            }

        elif execution_type == ExecutionTier.COMPREHENSIVE:
            return {
                "test_selection": "all",
                "max_retries": min(3, limits.max_retries_per_test),
                "num_samples": 400,
                "timeout_per_test": 60,
                "enable_deep_analysis": True,
                "save_detailed_logs": True,
                "generate_plots": True,
                "tests_to_run": "all",
            }

        elif execution_type == ExecutionTier.DEEP_STABILITY:
            return {
                "test_selection": "all",
                "max_retries": limits.max_retries_per_test,
                "num_samples": 500,
                "timeout_per_test": 120,
                "enable_deep_analysis": True,
                "save_detailed_logs": True,
                "generate_plots": True,
                "stability_runs": 5,  # Run each test 5 times
                "tests_to_run": "all",
            }

        return {}


# ============================================================================
# STORAGE MANAGER
# ============================================================================


class StorageManager:
    """Manage artifact storage to stay within limits."""

    def __init__(self, max_storage_mb: int, artifacts_dir: str = "artifacts"):
        self.max_storage_mb = max_storage_mb
        self.artifacts_dir = Path(artifacts_dir)
        self.artifacts_dir.mkdir(parents=True, exist_ok=True)

    def get_current_usage_mb(self) -> float:
        """Get current storage usage in MB."""
        total = 0
        for file in self.artifacts_dir.rglob("*"):
            if file.is_file():
                total += file.stat().st_size
        return total / (1024 * 1024)

    def cleanup_old_artifacts(self, keep_last_n: int = 5, keep_days: int = 30):
        """Clean up old artifacts to free space."""
        current_usage = self.get_current_usage_mb()

        print(f"📦 Storage: {current_usage:.1f}/{self.max_storage_mb} MB")

        if current_usage < self.max_storage_mb * 0.8:
            print("✅ Storage within limits")
            return

        print("🧹 Cleaning old artifacts...")

        # Get all artifact files with timestamps
        files_with_time = []
        for file in self.artifacts_dir.rglob("*"):
            if file.is_file():
                files_with_time.append((file, file.stat().st_mtime))

        # Sort by modification time (oldest first)
        files_with_time.sort(key=lambda x: x[1])

        # Keep last N files per type
        kept_files = set()
        for pattern in ["*.json", "*.txt", "*.png"]:
            matching = [f for f, t in files_with_time if f.match(pattern)]
            kept_files.update(matching[-keep_last_n:])

        # Keep files from last N days
        cutoff_time = time.time() - (keep_days * 24 * 60 * 60)
        for file, mtime in files_with_time:
            if mtime > cutoff_time:
                kept_files.add(file)

        # Delete old files
        deleted_count = 0
        freed_mb = 0
        for file, mtime in files_with_time:
            if file not in kept_files:
                size_mb = file.stat().st_size / (1024 * 1024)
                file.unlink()
                deleted_count += 1
                freed_mb += size_mb

        print(f"🗑️  Deleted {deleted_count} files, freed {freed_mb:.1f} MB")

    def should_save_artifact(self, artifact_type: str) -> bool:
        """Check if we should save this artifact type based on storage."""
        current_usage = self.get_current_usage_mb()

        # Priority saving based on storage pressure
        if current_usage > self.max_storage_mb * 0.9:
            # Critical storage - only essential files
            return artifact_type in ["summary_report", "baseline"]
        elif current_usage > self.max_storage_mb * 0.7:
            # High storage - skip large files
            return artifact_type not in ["plots", "detailed_logs"]
        else:
            # Normal - save everything
            return True


# ============================================================================
# GITHUB ACTIONS INTEGRATION
# ============================================================================


class GitHubActionsConfig:
    """Generate GitHub Actions workflow configurations."""

    @staticmethod
    def generate_workflow(tier: str = "free", repo_name: str = "my-repo") -> str:
        """Generate optimized GitHub Actions workflow YAML."""

        limits = {
            "free": ResourceLimits.for_github_free(),
            "team": ResourceLimits.for_github_team(),
            "enterprise": ResourceLimits.for_github_enterprise(),
        }[tier]

        workflow = f"""name: Stability Tests

on:
  # Pull requests - quick smoke tests only
  pull_request:
    branches: [ main, develop ]

  # Daily tests - standard suite
  schedule:
    - cron: '0 2 * * *'  # 2 AM daily

  # Weekly comprehensive - Sunday nights
  workflow_dispatch:
    inputs:
      execution_tier:
        description: 'Execution tier'
        required: true
        default: 'standard'
        type: choice
        options:
          - quick_smoke
          - standard
          - comprehensive
          - deep_stability

env:
  TIER: {tier}
  PYTHON_VERSION: '3.10'

jobs:
  check-limits:
    runs-on: ubuntu-latest
    outputs:
      should_run: ${{{{ steps.check.outputs.should_run }}}}
      execution_type: ${{{{ steps.check.outputs.execution_type }}}}

    steps:
      - uses: actions/checkout@v4

      - name: Check execution limits
        id: check
        run: |
          # Determine execution type based on trigger
          if [ "${{{{ github.event_name }}}}" = "pull_request" ]; then
            EXEC_TYPE="quick_smoke"
          elif [ "${{{{ github.event_name }}}}" = "schedule" ]; then
            EXEC_TYPE="standard"
          elif [ "${{{{ github.event_name }}}}" = "workflow_dispatch" ]; then
            EXEC_TYPE="${{{{ inputs.execution_tier }}}}"
          else
            EXEC_TYPE="quick_smoke"
          fi

          echo "execution_type=$EXEC_TYPE" >> $GITHUB_OUTPUT

          # Check if we should run (would need Python script)
          python .ci/check_limits.py --tier {tier} --type $EXEC_TYPE
          echo "should_run=true" >> $GITHUB_OUTPUT

  test-suite:
    needs: check-limits
    if: needs.check-limits.outputs.should_run == 'true'
    runs-on: ubuntu-latest
    timeout-minutes: {min(limits.max_execution_time_minutes, 60)}

    steps:
      - uses: actions/checkout@v4

      - name: Set up Python
        uses: actions/setup-python@v5
        with:
          python-version: ${{{{ env.PYTHON_VERSION }}}}
          cache: 'pip'

      - name: Install dependencies
        run: |
          pip install -r requirements.txt

      - name: Restore cache
        uses: actions/cache@v4
        with:
          path: |
            .ci/test_history.json
            .ci/baseline_results.json
          key: test-cache-${{{{ runner.os }}}}-${{{{ hashFiles('**/*.py') }}}}
          restore-keys: |
            test-cache-${{{{ runner.os }}}}-

      - name: Run tests
        run: |
          python run_robust_tests.py \\
            --tier {tier} \\
            --execution-type ${{{{ needs.check-limits.outputs.execution_type }}}} \\
            --max-retries {limits.max_retries_per_test} \\
            --save-baseline \\
            --output reports/

      - name: Cleanup artifacts
        if: always()
        run: |
          python -c "
          from pp import StorageManager
          sm = StorageManager({limits.max_storage_mb}, 'artifacts')
          sm.cleanup_old_artifacts(keep_last_n=3, keep_days=14)
          "

      - name: Upload reports
        if: always()
        uses: actions/upload-artifact@v4
        with:
          name: test-reports-${{{{ needs.check-limits.outputs.execution_type }}}}
          path: reports/
          retention-days: 14  # Reduce to save storage

      - name: Comment on PR
        if: github.event_name == 'pull_request'
        uses: actions/github-script@v7
        with:
          script: |
            const fs = require('fs');
            const report = fs.readFileSync('reports/summary.txt', 'utf8');
            github.rest.issues.createComment({{
              issue_number: context.issue.number,
              owner: context.repo.owner,
              repo: context.repo.repo,
              body: '## Test Results\\n```\\n' + report + '\\n```'
            }});

      - name: Record execution
        if: always()
        run: |
          python .ci/record_execution.py \\
            --tier {tier} \\
            --type ${{{{ needs.check-limits.outputs.execution_type }}}} \\
            --duration ${{{{ job.duration }}}}

  monthly-deep-test:
    # Run comprehensive stability analysis monthly
    if: github.event_name == 'schedule' && github.event.schedule == '0 2 1 * *'
    runs-on: ubuntu-latest
    timeout-minutes: 120

    steps:
      - uses: actions/checkout@v4
      # ... similar setup ...
      - name: Run deep stability analysis
        run: |
          python run_robust_tests.py \\
            --tier {tier} \\
            --execution-type deep_stability \\
            --stability-runs 10
"""
        return workflow


# ============================================================================
# USAGE EXAMPLE
# ============================================================================


def create_example_integration():
    """Create example integration script."""

    script = '''#!/usr/bin/env python3
"""
Example: Running tests with rate limiting
"""
import sys
from pp import RobustTestRunner
from ci_rate_limit_config import (
    TestScheduler,
    ExecutionTier,
    TieredTestConfig,
    StorageManager
)

def main():
    # Initialize with your tier
    tier = "free"  # or "team", "enterprise"

    # Check if we should run
    scheduler = TestScheduler(tier=tier)
    execution_type = ExecutionTier.STANDARD

    should_run, reason = scheduler.should_run(execution_type)

    if not should_run:
        print(f"⏭️  Skipping tests: {reason}")
        sys.exit(0)

    print(f"✅ {reason}")

    # Get configuration for this tier
    config = TieredTestConfig.get_config(
        execution_type,
        scheduler.limits
    )

    # Cleanup old artifacts first
    storage = StorageManager(scheduler.limits.max_storage_mb)
    storage.cleanup_old_artifacts()

    # Run tests with tier-appropriate configuration
    runner = RobustTestRunner(
        max_retries=config['max_retries'],
        base_seed=42
    )

    # ... load your test functions ...
    test_functions = {}  # Your tests here

    start_time = time.time()
    results, metadata = runner.run_test_suite(
        test_functions=test_functions,
        save_baseline=True,
        save_history=True,
        generate_reports=storage.should_save_artifact('reports')
    )

    # Record execution
    actual_minutes = (time.time() - start_time) / 60
    scheduler.record_execution(execution_type, int(actual_minutes))

    # Print usage report
    usage = scheduler.get_monthly_usage_report()
    print(f"\\n📊 Monthly Usage: {usage['minutes_used']}/{usage['minutes_limit']} min "
          f"({usage['percentage_used']:.1f}%)")

    # Exit with appropriate code
    if metadata['failed'] > 0:
        sys.exit(1)

if __name__ == '__main__':
    main()
'''

    return script


# ============================================================================
# MAIN
# ============================================================================

if __name__ == "__main__":
    import argparse

    parser = argparse.ArgumentParser(description="CI/CD Rate Limiting Configuration")
    parser.add_argument(
        "--generate-workflow",
        action="store_true",
        help="Generate GitHub Actions workflow",
    )
    parser.add_argument(
        "--tier", default="free", choices=["free", "team", "enterprise"]
    )
    parser.add_argument("--repo", default="my-repo")
    parser.add_argument(
        "--check-limits", action="store_true", help="Check current usage against limits"
    )

    args = parser.parse_args()

    if args.generate_workflow:
        workflow = GitHubActionsConfig.generate_workflow(args.tier, args.repo)
        output_file = ".github/workflows/stability-tests.yml"
        Path(output_file).parent.mkdir(parents=True, exist_ok=True)
        with open(output_file, "w") as f:
            f.write(workflow)
        print(f"✅ Generated workflow: {output_file}")

    elif args.check_limits:
        scheduler = TestScheduler(tier=args.tier)
        usage = scheduler.get_monthly_usage_report()
        print(f"\n📊 Monthly Usage Report ({args.tier.upper()} tier)")
        print(f"Minutes used: {usage['minutes_used']}/{usage['minutes_limit']}")
        print(f"Percentage: {usage['percentage_used']:.1f}%")
        print(f"Remaining: {usage['minutes_remaining']} minutes")
        print(f"Reset date: {usage['reset_date']}")

    else:
        print("Example usage:")
        print(f"  python {__file__} --generate-workflow --tier free")
        print(f"  python {__file__} --check-limits --tier team")
