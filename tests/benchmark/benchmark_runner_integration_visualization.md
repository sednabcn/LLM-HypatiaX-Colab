"""
HypatiaX Complete Benchmarking Infrastructure

- Benchmark runner script
- Integration with existing benchmark_suite.py
- Visualization and reporting

Files to create:

1. tests/benchmarks/run_benchmarks.py         - Main runner script
2. tests/benchmarks/integration.py            - Integration with benchmark_suite
3. tests/benchmarks/visualize.py              - Visualization & reporting
4. tests/benchmarks/compare_results.py        - Compare benchmark runs
"""

# ============================================================================

# FILE 1: tests/benchmarks/run_benchmarks.py

# Main Benchmark Runner Script

# ============================================================================

"""
Main Benchmark Runner

Orchestrates all benchmark execution with comprehensive reporting.

Usage:
    # Run all benchmarks
    python tests/benchmarks/run_benchmarks.py

    # Run specific components
    python tests/benchmarks/run_benchmarks.py --components validation,llm

    # Run and generate HTML report
    python tests/benchmarks/run_benchmarks.py --html-report

    # Compare with baseline
    python tests/benchmarks/run_benchmarks.py --compare-baseline

    # CI/CD mode (fail on regression)
    python tests/benchmarks/run_benchmarks.py --ci-mode
"""

import argparse
import json
import sys
import time
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Optional

import pytest

class BenchmarkRunner:
    """Orchestrate benchmark execution and reporting."""

    def __init__(self, output_dir: Path = None):
        self.output_dir = output_dir or Path("benchmark_results")
        self.output_dir.mkdir(parents=True, exist_ok=True)

        self.timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        self.results_file = self.output_dir / f"results_{self.timestamp}.json"

        self.components = {
            "validation": "tests/benchmarks/test_validation_benchmarks.py",
            "llm": "tests/benchmarks/test_llm_benchmarks.py",
            "symbolic": "tests/benchmarks/test_symbolic_regression_benchmarks.py",
            "description": "tests/benchmarks/test_description_mapping_benchmarks.py",
        }

    def run_component(self, component: str, markers: List[str] = None) -> Dict:
        """Run benchmarks for a specific component."""
        if component not in self.components:
            raise ValueError(f"Unknown component: {component}")

        test_file = self.components[component]

        print(f"\n{'='*80}")
        print(f"Running {component.upper()} Benchmarks")
        print(f"{'='*80}")

        # Build pytest arguments
        args = [
            test_file,
            "-v",
            "--benchmark-output", str(self.results_file),
            "--tb=short",
        ]

        # Add markers if specified
        if markers:
            args.extend(["-m", " and ".join(markers)])

        # Run pytest
        start_time = time.time()
        exit_code = pytest.main(args)
        elapsed = time.time() - start_time

        return {
            "component": component,
            "exit_code": exit_code,
            "elapsed_seconds": elapsed,
            "passed": exit_code == 0,
        }

    def run_all(self,
                components: List[str] = None,
                include_slow: bool = False,
                ci_mode: bool = False) -> Dict:
        """Run all or selected component benchmarks."""

        components = components or list(self.components.keys())

        print(f"\n🚀 HypatiaX Benchmark Suite")
        print(f"Timestamp: {self.timestamp}")
        print(f"Components: {', '.join(components)}")
        print(f"Output: {self.results_file}")

        results = {
            "timestamp": self.timestamp,
            "components": {},
            "summary": {},
        }

        markers = []
        if not include_slow:
            markers.append("not slow")

        # Run each component
        for component in components:
            try:
                result = self.run_component(component, markers)
                results["components"][component] = result
            except Exception as e:
                print(f"❌ Error running {component}: {e}")
                results["components"][component] = {
                    "component": component,
                    "exit_code": 1,
                    "error": str(e),
                    "passed": False,
                }

        # Generate summary
        total_components = len(results["components"])
        passed_components = sum(1 for r in results["components"].values() if r.get("passed"))
        total_time = sum(r.get("elapsed_seconds", 0) for r in results["components"].values())

        results["summary"] = {
            "total_components": total_components,
            "passed_components": passed_components,
            "failed_components": total_components - passed_components,
            "pass_rate": f"{(passed_components/total_components)*100:.1f}%",
            "total_time_seconds": total_time,
        }

        # Save results
        with open(self.results_file, "w") as f:
            json.dump(results, f, indent=2)

        # Print summary
        self.print_summary(results)

        # CI mode: fail if any component failed
        if ci_mode and passed_components < total_components:
            sys.exit(1)

        return results

    def print_summary(self, results: Dict):
        """Print benchmark summary."""
        print(f"\n{'='*80}")
        print(f"Benchmark Summary")
        print(f"{'='*80}\n")

        for component, result in results["components"].items():
            status = "✅ PASS" if result.get("passed") else "❌ FAIL"
            elapsed = result.get("elapsed_seconds", 0)
            print(f"{status} {component:20s} {elapsed:6.2f}s")

        summary = results["summary"]
        print(f"\n{'-'*80}")
        print(f"Total: {summary['total_components']} components")
        print(f"Passed: {summary['passed_components']} ({summary['pass_rate']})")
        print(f"Failed: {summary['failed_components']}")
        print(f"Time: {summary['total_time_seconds']:.2f}s")
        print(f"{'='*80}\n")

        print(f"📊 Results saved to: {self.results_file}")

def main():
    """Main entry point."""
    parser = argparse.ArgumentParser(description="Run HypatiaX benchmarks")

    parser.add_argument(
        "--components",
        type=str,
        help="Comma-separated list of components (validation,llm,symbolic,description)",
    )
    parser.add_argument(
        "--include-slow",
        action="store_true",
        help="Include slow tests (LLM integration)",
    )
    parser.add_argument(
        "--ci-mode",
        action="store_true",
        help="CI/CD mode: fail on any regression",
    )
    parser.add_argument(
        "--compare-baseline",
        action="store_true",
        help="Compare with baseline results",
    )
    parser.add_argument(
        "--html-report",
        action="store_true",
        help="Generate HTML report",
    )
    parser.add_argument(
        "--output-dir",
        type=Path,
        default=Path("benchmark_results"),
        help="Output directory for results",
    )

    args = parser.parse_args()

    # Parse components
    components = None
    if args.components:
        components = [c.strip() for c in args.components.split(",")]

    # Run benchmarks
    runner = BenchmarkRunner(output_dir=args.output_dir)
    results = runner.run_all(
        components=components,
        include_slow=args.include_slow,
        ci_mode=args.ci_mode,
    )

    # Compare with baseline if requested
    if args.compare_baseline:
        from tests.benchmarks.compare_results import compare_with_baseline
        compare_with_baseline(runner.results_file)

    # Generate HTML report if requested
    if args.html_report:
        from tests.benchmarks.visualize import generate_html_report
        generate_html_report(runner.results_file)

if __name__ == "__main__":
    main()

# ============================================================================

# FILE 2: tests/benchmarks/integration.py

# Integration with existing benchmark_suite.py

# ============================================================================

"""
Integration Layer

Bridges component benchmarks with the existing benchmark_suite.py infrastructure.
Provides unified interface and shared utilities.
"""

import json
from pathlib import Path
from typing import Any, Dict, List

from tests.performance.benchmark_suite import BenchmarkSuite, BenchmarkResult

class UnifiedBenchmarkRegistry:
    """
    Central registry for all benchmarks (suite + components).

    Provides:
    - Unified result storage
    - Cross-benchmark comparisons
    - Historical tracking
    - Aggregated reporting
    """

    def __init__(self, storage_path: Path = None):
        self.storage_path = storage_path or Path("benchmark_results/registry.json")
        self.storage_path.parent.mkdir(parents=True, exist_ok=True)
        self.registry = self._load_registry()

    def _load_registry(self) -> Dict:
        """Load existing registry or create new."""
        if self.storage_path.exists():
            with open(self.storage_path) as f:
                return json.load(f)
        return {
            "benchmarks": {},
            "history": [],
        }

    def save_registry(self):
        """Persist registry to disk."""
        with open(self.storage_path, "w") as f:
            json.dump(self.registry, f, indent=2)

    def register_benchmark_suite_results(self, suite: BenchmarkSuite):
        """Register results from benchmark_suite.py."""
        timestamp = suite.results[0].timestamp if suite.results else None

        for result in suite.results:
            self.register_result(
                benchmark_id=f"suite.{result.operation}",
                result=result.to_dict(),
                timestamp=result.timestamp,
                source="benchmark_suite",
            )

    def register_component_results(self,
                                   component: str,
                                   results: List[Dict],
                                   timestamp: str):
        """Register results from component benchmarks."""
        for result in results:
            self.register_result(
                benchmark_id=f"component.{component}.{result.get('name', 'unknown')}",
                result=result,
                timestamp=timestamp,
                source=f"component_{component}",
            )

    def register_result(self,
                       benchmark_id: str,
                       result: Dict,
                       timestamp: str,
                       source: str):
        """Register individual benchmark result."""
        if benchmark_id not in self.registry["benchmarks"]:
            self.registry["benchmarks"][benchmark_id] = {
                "id": benchmark_id,
                "source": source,
                "history": [],
            }

        # Add to history
        self.registry["benchmarks"][benchmark_id]["history"].append({
            "timestamp": timestamp,
            "result": result,
        })

        # Keep only last 50 results
        if len(self.registry["benchmarks"][benchmark_id]["history"]) > 50:
            self.registry["benchmarks"][benchmark_id]["history"] = \
                self.registry["benchmarks"][benchmark_id]["history"][-50:]

        # Update global history
        self.registry["history"].append({
            "timestamp": timestamp,
            "benchmark_id": benchmark_id,
            "source": source,
        })

        self.save_registry()

    def get_benchmark_history(self, benchmark_id: str) -> List[Dict]:
        """Get historical results for a benchmark."""
        if benchmark_id in self.registry["benchmarks"]:
            return self.registry["benchmarks"][benchmark_id]["history"]
        return []

    def get_all_benchmarks(self) -> Dict:
        """Get all registered benchmarks."""
        return self.registry["benchmarks"]

    def detect_regressions(self, threshold: float = 0.20) -> List[Dict]:
        """
        Detect performance regressions across all benchmarks.

        Args:
            threshold: Regression threshold (0.20 = 20% slower)

        Returns:
            List of regressions with details
        """
        regressions = []

        for benchmark_id, benchmark in self.registry["benchmarks"].items():
            history = benchmark["history"]

            if len(history) < 2:
                continue

            # Compare latest with previous
            current = history[-1]["result"]
            previous = history[-2]["result"]

            # Extract performance metric (prefer p95)
            current_perf = current.get("p95", current.get("mean", 0))
            previous_perf = previous.get("p95", previous.get("mean", 0))

            if previous_perf == 0:
                continue

            regression = (current_perf - previous_perf) / previous_perf

            if regression > threshold:
                regressions.append({
                    "benchmark_id": benchmark_id,
                    "current": current_perf,
                    "previous": previous_perf,
                    "regression_percent": regression * 100,
                    "timestamp": history[-1]["timestamp"],
                })

        return regressions

# Example integration with existing benchmark_suite.py

def integrate_with_benchmark_suite():
    """
    Example: How to integrate component benchmarks with benchmark_suite.py
    """
    from tests.performance.benchmark_suite import BenchmarkSuite

    # Run existing benchmark suite
    suite = BenchmarkSuite(output_file="benchmark_results/suite_results.json")

    # ... run benchmarks ...

    # Register with unified registry
    registry = UnifiedBenchmarkRegistry()
    registry.register_benchmark_suite_results(suite)

    print("✅ Results registered with unified benchmark system")

# ============================================================================

# FILE 3: tests/benchmarks/visualize.py

# Visualization and Reporting

# ============================================================================

"""
Benchmark Visualization and Reporting

Generates:

- HTML reports with charts
- Trend analysis
- Comparison views
- Performance dashboards
"""

import json
from datetime import datetime
from pathlib import Path
from typing import Dict, List

import numpy as np

class BenchmarkVisualizer:
    """Generate visualizations and reports from benchmark results."""

    def __init__(self, results_dir: Path = None):
        self.results_dir = results_dir or Path("benchmark_results")
        self.results_dir.mkdir(parents=True, exist_ok=True)

    def generate_html_report(self, results_file: Path) -> Path:
        """Generate interactive HTML report."""
        with open(results_file) as f:
            results = json.load(f)

        html = self._build_html_report(results)

        output_file = self.results_dir / f"report_{results.get('timestamp', 'latest')}.html"
        with open(output_file, "w") as f:
            f.write(html)

        print(f"📊 HTML report generated: {output_file}")
        return output_file

    def _build_html_report(self, results: Dict) -> str:
        """Build HTML report content."""
        timestamp = results.get("timestamp", "Unknown")
        summary = results.get("summary", {})
        components = results.get("components", {})

        # Build component sections
        component_html = ""
        for component, result in components.items():
            status_icon = "✅" if result.get("passed") else "❌"
            elapsed = result.get("elapsed_seconds", 0)

            component_html += f"""
            <div class="component-card {'passed' if result.get('passed') else 'failed'}">
                <h3>{status_icon} {component.title()}</h3>
                <p>Time: {elapsed:.2f}s</p>
                <p>Status: {'Passed' if result.get('passed') else 'Failed'}</p>
            </div>
            """

        html = f"""
<!DOCTYPE html>
<html>
<head>
    <title>HypatiaX Benchmark Report - {timestamp}</title>
    <style>
        body {{
            font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif;
            max-width: 1200px;
            margin: 0 auto;
            padding: 20px;
            background: #f5f5f5;
        }}
        .header {{
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            color: white;
            padding: 30px;
            border-radius: 10px;
            margin-bottom: 30px;
        }}
        .summary {{
            background: white;
            padding: 20px;
            border-radius: 10px;
            margin-bottom: 30px;
            box-shadow: 0 2px 4px rgba(0,0,0,0.1);
        }}
        .summary-grid {{
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
            gap: 20px;
        }}
        .summary-item {{
            text-align: center;
        }}
        .summary-value {{
            font-size: 2.5em;
            font-weight: bold;
            color: #667eea;
        }}
        .summary-label {{
            color: #666;
            margin-top: 5px;
        }}
        .components {{
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(250px, 1fr));
            gap: 20px;
        }}
        .component-card {{
            background: white;
            padding: 20px;
            border-radius: 10px;
            box-shadow: 0 2px 4px rgba(0,0,0,0.1);
        }}
        .component-card.passed {{
            border-left: 4px solid #48bb78;
        }}
        .component-card.failed {{
            border-left: 4px solid #f56565;
        }}
        .component-card h3 {{
            margin-top: 0;
        }}
        .chart-container {{
            background: white;
            padding: 20px;
            border-radius: 10px;
            margin-top: 20px;
            box-shadow: 0 2px 4px rgba(0,0,0,0.1);
        }}
    </style>
    <script src="https://cdn.jsdelivr.net/npm/chart.js"></script>
</head>
<body>
    <div class="header">
        <h1>🚀 HypatiaX Benchmark Report</h1>
        <p>Generated: {timestamp}</p>
    </div>

    <div class="summary">
        <h2>Summary</h2>
        <div class="summary-grid">
            <div class="summary-item">
                <div class="summary-value">{summary.get('total_components', 0)}</div>
                <div class="summary-label">Total Components</div>
            </div>
            <div class="summary-item">
                <div class="summary-value">{summary.get('passed_components', 0)}</div>
                <div class="summary-label">Passed</div>
            </div>
            <div class="summary-item">
                <div class="summary-value">{summary.get('failed_components', 0)}</div>
                <div class="summary-label">Failed</div>
            </div>
            <div class="summary-item">
                <div class="summary-value">{summary.get('pass_rate', 'N/A')}</div>
                <div class="summary-label">Pass Rate</div>
            </div>
            <div class="summary-item">
                <div class="summary-value">{summary.get('total_time_seconds', 0):.1f}s</div>
                <div class="summary-label">Total Time</div>
            </div>
        </div>
    </div>

    <h2>Components</h2>
    <div class="components">
        {component_html}
    </div>

    <div class="chart-container">
        <h2>Performance Overview</h2>
        <canvas id="performanceChart"></canvas>
    </div>

    <script>
        const ctx = document.getElementById('performanceChart').getContext('2d');
        new Chart(ctx, {{
            type: 'bar',
            data: {{
                labels: {list(components.keys())},
                datasets: [{{
                    label: 'Execution Time (seconds)',
                    data: {[r.get('elapsed_seconds', 0) for r in components.values()]},
                    backgroundColor: 'rgba(102, 126, 234, 0.5)',
                    borderColor: 'rgba(102, 126, 234, 1)',
                    borderWidth: 1
                }}]
            }},
            options: {{
                responsive: true,
                scales: {{
                    y: {{
                        beginAtZero: true
                    }}
                }}
            }}
        }});
    </script>
</body>
</html>
"""
        return html

    def generate_trend_analysis(self, benchmark_id: str = None) -> Dict:
        """Generate trend analysis from historical data."""
        registry = UnifiedBenchmarkRegistry()

        if benchmark_id:
            history = registry.get_benchmark_history(benchmark_id)
        else:
            # Analyze all benchmarks
            all_benchmarks = registry.get_all_benchmarks()
            history = []
            for bench in all_benchmarks.values():
                history.extend(bench["history"])

        if not history:
            return {"error": "No historical data available"}

        # Extract performance metrics over time
        timestamps = []
        values = []

        for entry in history:
            timestamps.append(entry["timestamp"])
            result = entry["result"]
            value = result.get("p95", result.get("mean", 0))
            values.append(value)

        # Calculate trend
        if len(values) >= 2:
            trend = (values[-1] - values[0]) / values[0] * 100
        else:
            trend = 0

        return {
            "benchmark_id": benchmark_id,
            "data_points": len(values),
            "current": values[-1] if values else 0,
            "baseline": values[0] if values else 0,
            "trend_percent": trend,
            "improving": trend < 0,  # Lower is better
            "timestamps": timestamps,
            "values": values,
        }

def generate_html_report(results_file: Path):
    """Convenience function to generate HTML report."""
    visualizer = BenchmarkVisualizer()
    return visualizer.generate_html_report(results_file)

# ============================================================================

# FILE 4: tests/benchmarks/compare_results.py

# Compare benchmark results across runs

# ============================================================================

"""
Benchmark Comparison Tool

Compare benchmark results across different runs to identify:

- Performance regressions
- Performance improvements
- Stability issues
"""

import json
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Tuple

class BenchmarkComparator:
    """Compare benchmark results across runs."""

    def __init__(self, results_dir: Path = None):
        self.results_dir = results_dir or Path("benchmark_results")

    def get_available_results(self) -> List[Path]:
        """Get all available result files."""
        return sorted(self.results_dir.glob("results_*.json"), reverse=True)

    def load_results(self, results_file: Path) -> Dict:
        """Load results from file."""
        with open(results_file) as f:
            return json.load(f)

    def compare_two_runs(self,
                        current_file: Path,
                        baseline_file: Path) -> Dict:
        """Compare two benchmark runs."""
        current = self.load_results(current_file)
        baseline = self.load_results(baseline_file)

        comparison = {
            "current_timestamp": current.get("timestamp"),
            "baseline_timestamp": baseline.get("timestamp"),
            "components": {},
            "regressions": [],
            "improvements": [],
        }

        # Compare each component
        for component in current.get("components", {}).keys():
            if component not in baseline.get("components", {}):
                continue

            current_time = current["components"][component].get("elapsed_seconds", 0)
            baseline_time = baseline["components"][component].get("elapsed_seconds", 0)

            if baseline_time == 0:
                continue

            change_percent = ((current_time - baseline_time) / baseline_time) * 100

            comparison["components"][component] = {
                "current": current_time,
                "baseline": baseline_time,
                "change_percent": change_percent,
                "improved": change_percent < -5,  # >5% faster
                "regressed": change_percent > 10,  # >10% slower
            }

            if change_percent > 10:
                comparison["regressions"].append({
                    "component": component,
                    "change_percent": change_percent,
                    "current": current_time,
                    "baseline": baseline_time,
                })
            elif change_percent < -5:
                comparison["improvements"].append({
                    "component": component,
                    "change_percent": change_percent,
                    "current": current_time,
                    "baseline": baseline_time,
                })

        return comparison

    def print_comparison(self, comparison: Dict):
        """Print comparison results."""
        print(f"\n{'='*80}")
        print(f"Benchmark Comparison")
        print(f"{'='*80}")
        print(f"Current:  {comparison['current_timestamp']}")
        print(f"Baseline: {comparison['baseline_timestamp']}")
        print(f"{'='*80}\n")

        # Print component comparisons
        for component, data in comparison["components"].items():
            status = "📈" if data["improved"] else "📉" if data["regressed"] else "➡️"
            change = data["change_percent"]

            print(f"{status} {component:20s}: {change:+6.1f}% "
                  f"({data['baseline']:.2f}s → {data['current']:.2f}s)")

        # Print regressions
        if comparison["regressions"]:
            print(f"\n❌ Regressions Detected ({len(comparison['regressions'])}):")
            for reg in comparison["regressions"]:
                print(f"   {reg['component']:20s}: {reg['change_percent']:+.1f}%")

        # Print improvements
        if comparison["improvements"]:
            print(f"\n✅ Improvements ({len(comparison['improvements'])}):")
            for imp in comparison["improvements"]:
                print(f"   {imp['component']:20s}: {imp['change_percent']:+.1f}%")

        print(f"\n{'='*80}\n")

def compare_with_baseline(current_file: Path, baseline_file: Path = None):
    """Compare current results with baseline."""
    comparator = BenchmarkComparator()

    if baseline_file is None:
        # Use most recent file as baseline
        available = comparator.get_available_results()
        if len(available) < 2:
            print("⚠️  No baseline available for comparison")
            return

        baseline_file = available[1]  # Second most recent

    comparison = comparator.compare_two_runs(current_file, baseline_file)
    comparator.print_comparison(comparison)

    # Return exit code for CI/CD
    if comparison["regressions"]:
        return 1
    return 0

# ============================================================================

# FILE 5: tests/benchmarks/dashboard.py

# Real-time Performance Dashboard

# ============================================================================

"""
Real-time Performance Dashboard

Live monitoring dashboard for benchmark results.
Updates automatically as new benchmarks run.
"""

import json
import time
from pathlib import Path
from typing import Dict

def generate_dashboard_html() -> str:
    """Generate real-time dashboard HTML."""
    html = """
<!DOCTYPE html>
<html>
<head>
    <title>HypatiaX Performance Dashboard</title>
    <style>
        body {
            font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif;
            margin: 0;
            padding: 20px;
            background: #1a1a2e;
            color: white;
        }
        .dashboard {
            max-width: 1400px;
            margin: 0 auto;
        }
        .header {
            text-align: center;
            margin-bottom: 30px;
        }
        .metrics-grid {
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(250px, 1fr));
            gap: 20px;
            margin-bottom: 30px;
        }
        .metric-card {
            background: #16213e;
            padding: 20px;
            border-radius: 10px;
            border-left: 4px solid #0f3460;
        }
        .metric-card.good {
            border-left-color: #48bb78;
        }
        .metric-card.warning {
            border-left-color: #ed8936;
        }
        .metric-card.bad {
            border-left-color: #f56565;
        }
        .metric-value {
            font-size: 2.5em;
            font-weight: bold;
            margin: 10px 0;
        }
        .metric-label {
            color: #a0aec0;
            font-size: 0.9em;
        }
        .trend {
            font-size: 0.9em;
            margin-top: 10px;
        }
        .trend.up {
            color: #48bb78;
        }
        .trend.down {
            color: #f56565;
        }
        .chart-section {
            background: #16213e;
            padding: 20px;
            border-radius: 10px;
            margin-top: 20px;
        }
        .last-updated {
            text-align: center;
            color: #a0aec0;
            margin-top: 20px;
        }
    </style>
    <script src="https://cdn.jsdelivr.net/npm/chart.js"></script>
</head>
<body>
    <div class="dashboard">
        <div class="header">
            <h1>🚀 HypatiaX Performance Dashboard</h1>
            <p>Real-time Benchmark Monitoring</p>
        </div>

        <div class="metrics-grid" id="metricsGrid">
            <!-- Metrics will be inserted here -->
        </div>
