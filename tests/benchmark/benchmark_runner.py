"""
HypatiaX Complete Benchmarking Infrastructure
=============================================

Complete suite of tools for running, tracking, and visualizing benchmarks.

Files to create in your project:
1. tests/benchmarks/run_benchmarks.py - Main runner (this file, sections 1-2)
2. tests/benchmarks/integration.py - Integration layer (section 3)
3. tests/benchmarks/visualize.py - Visualization (section 4)
4. tests/benchmarks/compare_results.py - Comparison tool (section 5)

Quick Start:
    # Run all benchmarks
    python tests/benchmarks/run_benchmarks.py

    # Run specific components with HTML report
    python tests/benchmarks/run_benchmarks.py --components validation,llm --html-report

    # CI mode (fail on regression)
    python tests/benchmarks/run_benchmarks.py --ci-mode --compare-baseline
"""

# ============================================================================
# SECTION 1: Main Benchmark Runner
# File: tests/benchmarks/run_benchmarks.py
# ============================================================================

import argparse
import json
import sys
import time
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Optional

import pytest


class BenchmarkRunner:
    """Orchestrate benchmark execution with comprehensive reporting."""

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
        print(f"🔍 Running {component.upper()} Benchmarks")
        print(f"{'='*80}")

        # Build pytest arguments
        args = [
            test_file,
            "-v",
            "--tb=short",
            f"--json-report",
            f"--json-report-file={self.output_dir}/component_{component}_{self.timestamp}.json",
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
            "test_file": test_file,
        }

    def run_all(
        self,
        components: List[str] = None,
        include_slow: bool = False,
        ci_mode: bool = False,
    ) -> Dict:
        """Run all or selected component benchmarks."""

        components = components or list(self.components.keys())

        print(f"\n{'='*80}")
        print(f"🚀 HypatiaX Benchmark Suite")
        print(f"{'='*80}")
        print(f"📅 Timestamp: {self.timestamp}")
        print(f"📦 Components: {', '.join(components)}")
        print(f"💾 Output: {self.results_file}")
        print(f"⏱️  Include slow: {include_slow}")
        print(f"{'='*80}\n")

        results = {
            "timestamp": self.timestamp,
            "components": {},
            "summary": {},
            "metadata": {
                "include_slow": include_slow,
                "ci_mode": ci_mode,
                "python_version": sys.version,
            },
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
        passed_components = sum(
            1 for r in results["components"].values() if r.get("passed")
        )
        total_time = sum(
            r.get("elapsed_seconds", 0) for r in results["components"].values()
        )

        results["summary"] = {
            "total_components": total_components,
            "passed_components": passed_components,
            "failed_components": total_components - passed_components,
            "pass_rate": f"{(passed_components/total_components)*100:.1f}%",
            "total_time_seconds": total_time,
            "success": passed_components == total_components,
        }

        # Save results
        with open(self.results_file, "w") as f:
            json.dump(results, f, indent=2)

        # Print summary
        self.print_summary(results)

        # CI mode: fail if any component failed
        if ci_mode and not results["summary"]["success"]:
            print("\n❌ CI Mode: Benchmarks failed, exiting with code 1")
            sys.exit(1)

        return results

    def print_summary(self, results: Dict):
        """Print benchmark summary."""
        print(f"\n{'='*80}")
        print(f"📊 Benchmark Summary")
        print(f"{'='*80}\n")

        for component, result in results["components"].items():
            status = "✅ PASS" if result.get("passed") else "❌ FAIL"
            elapsed = result.get("elapsed_seconds", 0)
            print(f"{status} {component:20s} {elapsed:6.2f}s")

        summary = results["summary"]
        print(f"\n{'-'*80}")
        print(f"📦 Total: {summary['total_components']} components")
        print(f"✅ Passed: {summary['passed_components']} ({summary['pass_rate']})")
        print(f"❌ Failed: {summary['failed_components']}")
        print(f"⏱️  Time: {summary['total_time_seconds']:.2f}s")
        print(f"{'='*80}\n")

        print(f"💾 Results saved to: {self.results_file}")


# ============================================================================
# SECTION 2: CLI Interface
# ============================================================================


def main():
    """Main entry point for benchmark runner."""
    parser = argparse.ArgumentParser(
        description="Run HypatiaX benchmarks with comprehensive reporting",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  # Run all benchmarks (fast tests only)
  python run_benchmarks.py

  # Run specific components with slow tests
  python run_benchmarks.py --components validation,llm --include-slow

  # Generate HTML report
  python run_benchmarks.py --html-report

  # CI/CD mode with comparison
  python run_benchmarks.py --ci-mode --compare-baseline

  # Full production run
  python run_benchmarks.py --include-slow --html-report --compare-baseline
        """,
    )

    parser.add_argument(
        "--components",
        type=str,
        help="Comma-separated list: validation,llm,symbolic,description (default: all)",
    )
    parser.add_argument(
        "--include-slow",
        action="store_true",
        help="Include slow tests like LLM integration benchmarks",
    )
    parser.add_argument(
        "--ci-mode",
        action="store_true",
        help="CI/CD mode: exit with error code on any failure",
    )
    parser.add_argument(
        "--compare-baseline",
        action="store_true",
        help="Compare results with previous baseline",
    )
    parser.add_argument(
        "--html-report",
        action="store_true",
        help="Generate interactive HTML report",
    )
    parser.add_argument(
        "--output-dir",
        type=Path,
        default=Path("benchmark_results"),
        help="Output directory for results (default: benchmark_results)",
    )

    args = parser.parse_args()

    # Parse components
    components = None
    if args.components:
        components = [c.strip() for c in args.components.split(",")]

    # Run benchmarks
    print("🎯 Starting HypatiaX Benchmark Suite...")
    runner = BenchmarkRunner(output_dir=args.output_dir)
    results = runner.run_all(
        components=components,
        include_slow=args.include_slow,
        ci_mode=args.ci_mode,
    )

    # Compare with baseline if requested
    if args.compare_baseline:
        print("\n📈 Comparing with baseline...")
        try:
            from tests.benchmarks.compare_results import compare_with_baseline

            exit_code = compare_with_baseline(runner.results_file)
            if args.ci_mode and exit_code != 0:
                print("❌ Performance regression detected!")
                sys.exit(1)
        except ImportError:
            print("⚠️  Comparison module not available")

    # Generate HTML report if requested
    if args.html_report:
        print("\n📊 Generating HTML report...")
        try:
            from tests.benchmarks.visualize import generate_html_report

            report_path = generate_html_report(runner.results_file)
            print(f"✅ Report available at: {report_path}")
        except ImportError:
            print("⚠️  Visualization module not available")

    print("\n✨ Benchmark suite complete!")


if __name__ == "__main__":
    main()


# ============================================================================
# SECTION 3: Integration Layer
# File: tests/benchmarks/integration.py
# ============================================================================

"""
Integration with existing benchmark_suite.py

Provides unified interface for both component benchmarks and the existing
benchmark suite, enabling cross-benchmark comparisons and historical tracking.
"""

from pathlib import Path
from typing import Dict, List, Optional


class UnifiedBenchmarkRegistry:
    """
    Central registry bridging component benchmarks and benchmark_suite.py.

    Features:
    - Unified result storage across all benchmark types
    - Cross-benchmark performance comparisons
    - Historical trend tracking
    - Regression detection
    """

    def __init__(self, storage_path: Path = None):
        self.storage_path = storage_path or Path(
            "benchmark_results/unified_registry.json"
        )
        self.storage_path.parent.mkdir(parents=True, exist_ok=True)
        self.registry = self._load_registry()

    def _load_registry(self) -> Dict:
        """Load existing registry or create new."""
        if self.storage_path.exists():
            with open(self.storage_path) as f:
                return json.load(f)
        return {
            "version": "1.0.0",
            "benchmarks": {},
            "history": [],
            "baselines": {},
        }

    def save_registry(self):
        """Persist registry to disk."""
        with open(self.storage_path, "w") as f:
            json.dump(self.registry, f, indent=2)
        print(f"💾 Registry saved to {self.storage_path}")

    def register_suite_results(self, suite_results: Dict):
        """
        Register results from benchmark_suite.py.

        Example suite_results format:
        {
            "timestamp": "20241214_120000",
            "results": [
                {"operation": "validation", "mean": 0.5, "p95": 0.8, ...},
                ...
            ]
        }
        """
        timestamp = suite_results.get("timestamp", datetime.now().isoformat())

        for result in suite_results.get("results", []):
            benchmark_id = f"suite.{result.get('operation', 'unknown')}"
            self.register_result(
                benchmark_id=benchmark_id,
                result=result,
                timestamp=timestamp,
                source="benchmark_suite",
            )

        self.save_registry()
        print(f"✅ Registered {len(suite_results.get('results', []))} suite results")

    def register_component_results(self, component_results: Dict):
        """
        Register results from component benchmarks.

        Example component_results format:
        {
            "timestamp": "20241214_120000",
            "components": {
                "validation": {"passed": true, "elapsed_seconds": 5.2},
                ...
            }
        }
        """
        timestamp = component_results.get("timestamp", datetime.now().isoformat())

        for component, result in component_results.get("components", {}).items():
            benchmark_id = f"component.{component}"
            self.register_result(
                benchmark_id=benchmark_id,
                result=result,
                timestamp=timestamp,
                source=f"component_{component}",
            )

        self.save_registry()
        print(
            f"✅ Registered {len(component_results.get('components', {}))} component results"
        )

    def register_result(
        self, benchmark_id: str, result: Dict, timestamp: str, source: str
    ):
        """Register individual benchmark result."""
        if benchmark_id not in self.registry["benchmarks"]:
            self.registry["benchmarks"][benchmark_id] = {
                "id": benchmark_id,
                "source": source,
                "history": [],
                "baseline": None,
            }

        # Add to history
        self.registry["benchmarks"][benchmark_id]["history"].append(
            {
                "timestamp": timestamp,
                "result": result,
            }
        )

        # Keep only last 100 results
        if len(self.registry["benchmarks"][benchmark_id]["history"]) > 100:
            self.registry["benchmarks"][benchmark_id]["history"] = self.registry[
                "benchmarks"
            ][benchmark_id]["history"][-100:]

        # Update global history
        self.registry["history"].append(
            {
                "timestamp": timestamp,
                "benchmark_id": benchmark_id,
                "source": source,
            }
        )

    def set_baseline(self, benchmark_id: str, timestamp: str = None):
        """Set a specific result as the baseline for comparisons."""
        if benchmark_id not in self.registry["benchmarks"]:
            raise ValueError(f"Benchmark {benchmark_id} not found")

        history = self.registry["benchmarks"][benchmark_id]["history"]

        if timestamp:
            # Find specific timestamp
            baseline = next((h for h in history if h["timestamp"] == timestamp), None)
            if not baseline:
                raise ValueError(f"Timestamp {timestamp} not found for {benchmark_id}")
        else:
            # Use most recent
            baseline = history[-1] if history else None

        if baseline:
            self.registry["benchmarks"][benchmark_id]["baseline"] = baseline
            self.save_registry()
            print(f"✅ Set baseline for {benchmark_id}: {baseline['timestamp']}")

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
            baseline = benchmark.get("baseline")

            if not baseline or len(history) < 1:
                continue

            # Compare latest with baseline
            current = history[-1]["result"]
            baseline_result = baseline["result"]

            # Extract performance metric
            current_perf = self._extract_performance(current)
            baseline_perf = self._extract_performance(baseline_result)

            if baseline_perf == 0:
                continue

            regression = (current_perf - baseline_perf) / baseline_perf

            if regression > threshold:
                regressions.append(
                    {
                        "benchmark_id": benchmark_id,
                        "current": current_perf,
                        "baseline": baseline_perf,
                        "regression_percent": regression * 100,
                        "current_timestamp": history[-1]["timestamp"],
                        "baseline_timestamp": baseline["timestamp"],
                    }
                )

        return regressions

    def _extract_performance(self, result: Dict) -> float:
        """Extract performance metric from result (prefer p95, then mean)."""
        return result.get("p95", result.get("elapsed_seconds", result.get("mean", 0)))

    def get_benchmark_history(self, benchmark_id: str, limit: int = None) -> List[Dict]:
        """Get historical results for a specific benchmark."""
        if benchmark_id not in self.registry["benchmarks"]:
            return []

        history = self.registry["benchmarks"][benchmark_id]["history"]
        return history[-limit:] if limit else history

    def get_all_benchmarks(self) -> Dict:
        """Get all registered benchmarks."""
        return self.registry["benchmarks"]


# Example usage function
def integrate_benchmark_results():
    """
    Example: How to integrate both benchmark types.
    Call this after running benchmarks.
    """
    registry = UnifiedBenchmarkRegistry()

    # Register component benchmark results
    component_results = Path("benchmark_results").glob("results_*.json")
    for results_file in sorted(component_results, reverse=True)[:1]:  # Latest only
        with open(results_file) as f:
            results = json.load(f)
        registry.register_component_results(results)

    # Optionally: Register suite results if you have them
    # suite_file = Path("benchmark_results/suite_results.json")
    # if suite_file.exists():
    #     with open(suite_file) as f:
    #         suite_results = json.load(f)
    #     registry.register_suite_results(suite_results)

    # Detect regressions
    regressions = registry.detect_regressions(threshold=0.15)
    if regressions:
        print(f"\n⚠️  {len(regressions)} performance regressions detected:")
        for reg in regressions:
            print(f"  - {reg['benchmark_id']}: +{reg['regression_percent']:.1f}%")
    else:
        print("\n✅ No performance regressions detected")

    return registry


# ============================================================================
# SECTION 4: Visualization
# File: tests/benchmarks/visualize.py
# ============================================================================

"""
Benchmark Visualization and Reporting

Generates interactive HTML reports with charts and trend analysis.
"""

import json
from datetime import datetime
from pathlib import Path
from typing import Dict, List


class BenchmarkVisualizer:
    """Generate visualizations and reports from benchmark results."""

    def __init__(self, results_dir: Path = None):
        self.results_dir = results_dir or Path("benchmark_results")
        self.results_dir.mkdir(parents=True, exist_ok=True)

    def generate_html_report(self, results_file: Path) -> Path:
        """Generate interactive HTML report with charts."""
        with open(results_file) as f:
            results = json.load(f)

        html = self._build_html_report(results)

        output_file = (
            self.results_dir / f"report_{results.get('timestamp', 'latest')}.html"
        )
        with open(output_file, "w") as f:
            f.write(html)

        print(f"📊 HTML report generated: {output_file}")
        return output_file

    def _build_html_report(self, results: Dict) -> str:
        """Build complete HTML report with styling and charts."""
        timestamp = results.get("timestamp", "Unknown")
        summary = results.get("summary", {})
        components = results.get("components", {})

        # Build component cards
        component_cards = ""
        component_labels = []
        component_times = []

        for component, result in components.items():
            status_icon = "✅" if result.get("passed") else "❌"
            elapsed = result.get("elapsed_seconds", 0)
            status_class = "passed" if result.get("passed") else "failed"

            component_cards += f"""
            <div class="component-card {status_class}">
                <h3>{status_icon} {component.title()}</h3>
                <div class="metric-grid">
                    <div class="metric">
                        <div class="metric-value">{elapsed:.2f}s</div>
                        <div class="metric-label">Execution Time</div>
                    </div>
                    <div class="metric">
                        <div class="metric-value">{'PASS' if result.get('passed') else 'FAIL'}</div>
                        <div class="metric-label">Status</div>
                    </div>
                </div>
            </div>
            """

            component_labels.append(component.title())
            component_times.append(elapsed)

        # Generate HTML
        html = f"""
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>HypatiaX Benchmark Report - {timestamp}</title>
    <style>
        * {{
            margin: 0;
            padding: 0;
            box-sizing: border-box;
        }}

        body {{
            font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, Oxygen, Ubuntu, sans-serif;
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            min-height: 100vh;
            padding: 20px;
        }}

        .container {{
            max-width: 1400px;
            margin: 0 auto;
        }}

        .header {{
            background: white;
            padding: 40px;
            border-radius: 15px;
            margin-bottom: 30px;
            box-shadow: 0 10px 30px rgba(0,0,0,0.2);
            text-align: center;
        }}

        .header h1 {{
            color: #667eea;
            font-size: 2.5em;
            margin-bottom: 10px;
        }}

        .header .subtitle {{
            color: #666;
            font-size: 1.1em;
        }}

        .summary-grid {{
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
            gap: 20px;
            margin-bottom: 30px;
        }}

        .summary-card {{
            background: white;
            padding: 30px;
            border-radius: 15px;
            text-align: center;
            box-shadow: 0 5px 15px rgba(0,0,0,0.1);
            transition: transform 0.3s;
        }}

        .summary-card:hover {{
            transform: translateY(-5px);
        }}

        .summary-value {{
            font-size: 3em;
            font-weight: bold;
            color: #667eea;
            margin-bottom: 10px;
        }}

        .summary-label {{
            color: #666;
            font-size: 1em;
        }}

        .components-section {{
            margin-bottom: 30px;
        }}

        .section-title {{
            color: white;
            font-size: 2em;
            margin-bottom: 20px;
            text-align: center;
        }}

        .components-grid {{
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(300px, 1fr));
            gap: 20px;
        }}

        .component-card {{
            background: white;
            padding: 30px;
            border-radius: 15px;
            box-shadow: 0 5px 15px rgba(0,0,0,0.1);
            transition: transform 0.3s;
        }}

        .component-card:hover {{
            transform: translateY(-5px);
        }}

        .component-card.passed {{
            border-left: 5px solid #48bb78;
        }}

        .component-card.failed {{
            border-left: 5px solid #f56565;
        }}

        .component-card h3 {{
            margin-bottom: 20px;
            color: #333;
        }}

        .metric-grid {{
            display: grid;
            grid-template-columns: repeat(2, 1fr);
            gap: 15px;
        }}

        .metric {{
            text-align: center;
        }}

        .metric-value {{
            font-size: 1.8em;
            font-weight: bold;
            color: #667eea;
        }}

        .metric-label {{
            color: #999;
            font-size: 0.9em;
            margin-top: 5px;
        }}

        .chart-section {{
            background: white;
            padding: 30px;
            border-radius: 15px;
            box-shadow: 0 5px 15px rgba(0,0,0,0.1);
            margin-bottom: 30px;
        }}

        .chart-section h2 {{
            color: #333;
            margin-bottom: 20px;
        }}

        .footer {{
            text-align: center;
            color: white;
            padding: 20px;
            font-size: 0.9em;
        }}

        canvas {{
            max-height: 400px;
        }}
    </style>
    <script src="https://cdn.jsdelivr.net/npm/chart.js@3.9.1/dist/chart.min.js"></script>
</head>
<body>
    <div class="container">
        <div class="header">
            <h1>🚀 HypatiaX Benchmark Report</h1>
            <p class="subtitle">Generated: {timestamp}</p>
        </div>

        <div class="summary-grid">
            <div class="summary-card">
                <div class="summary-value">{summary.get('total_components', 0)}</div>
                <div class="summary-label">Total Components</div>
            </div>
            <div class="summary-card">
                <div class="summary-value">{summary.get('passed_components', 0)}</div>
                <div class="summary-label">Passed</div>
            </div>
            <div class="summary-card">
                <div class="summary-value">{summary.get('failed_components', 0)}</div>
                <div class="summary-label">Failed</div>
            </div>
            <div class="summary-card">
                <div class="summary-value">{summary.get('pass_rate', 'N/A')}</div>
                <div class="summary-label">Pass Rate</div>
            </div>
            <div class="summary-card">
                <div class="summary-value">{summary.get('total_time_seconds', 0):.1f}s</div>
                <div class="summary-label">Total Time</div>
            </div>
        </div>

        <h2 class="section-title">Component Results</h2>
        <div class="components-grid">
            {component_cards}
        </div>

        <div class="chart-section">
            <h2>⏱️ Execution Time Breakdown</h2>
            <canvas id="performanceChart"></canvas>
        </div>

        <div class="footer">
            <p>HypatiaX Benchmark Suite v1.0.0</p>
            <p>For more details, see the JSON results file</p>
        </div>
    </div>

    <script>
        const ctx = document.getElementById('performanceChart').getContext('2d');
        new Chart(ctx, {{
            type: 'bar',
            data: {{
                labels: {json.dumps(component_labels)},
                datasets: [{{
                    label: 'Execution Time (seconds)',
                    data: {json.dumps(component_times)},
                    backgroundColor: [
                        'rgba(102, 126, 234, 0.8)',
                        'rgba(118, 75, 162, 0.8)',
                        'rgba(72, 187, 120, 0.8)',
                        'rgba(237, 137, 54, 0.8)',
                    ],
                    borderColor: [
                        'rgba(102, 126, 234, 1)',
                        'rgba(118, 75, 162, 1)',
                        'rgba(72, 187, 120, 1)',
                        'rgba(237, 137, 54, 1)',
                    ],
                    borderWidth: 2,
                    borderRadius: 10,
                }}]
            }},
            options: {{
                responsive: true,
                maintainAspectRatio: true,
                plugins: {{
                    legend: {{
                        display: false
                    }},
                    tooltip: {{
                        backgroundColor: 'rgba(0, 0, 0, 0.8)',
                        padding: 12,
                        titleFont: {{
                            size: 14
                        }},
                        bodyFont: {{
                            size: 13
                        }}
                    }}
                }},
                scales: {{
                    y: {{
                        beginAtZero: true,
                        title: {{
                            display: true,
                            text: 'Time (seconds)'
                        }},
                        grid: {{
                            color: 'rgba(0, 0, 0, 0.05)'
                        }}
                    }},
                    x: {{
                        grid: {{
                            display: false
                        }}
                    }}
                }}
            }}
        }});
    </script>
</body>
</html>
"""
        return html


def generate_html_report(results_file: Path) -> Path:
    """Convenience function to generate HTML report."""
    visualizer = BenchmarkVisualizer()
    return visualizer.generate_html_report(results_file)


# ============================================================================
# SECTION 5: Comparison Tool
# File: tests/benchmarks/compare_results.py
# ============================================================================

"""
Benchmark Comparison Tool

Compare benchmark results across different runs to identify:
- Performance regressions (>10% slower)
- Performance improvements (>5% faster)
- Stability issues
- Trend analysis
"""

import json
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Optional, Tuple


class BenchmarkComparator:
    """Compare benchmark results across runs."""

    def __init__(self, results_dir: Path = None):
        self.results_dir = results_dir or Path("benchmark_results")

    def get_available_results(self) -> List[Path]:
        """Get all available result files, sorted by timestamp (newest first)."""
        return sorted(self.results_dir.glob("results_*.json"), reverse=True)

    def load_results(self, results_file: Path) -> Dict:
        """Load results from file."""
        with open(results_file) as f:
            return json.load(f)

    def compare_two_runs(self, current_file: Path, baseline_file: Path) -> Dict:
        """
        Compare two benchmark runs in detail.

        Returns:
            Dict with comparison results including regressions and improvements
        """
        current = self.load_results(current_file)
        baseline = self.load_results(baseline_file)

        comparison = {
            "current_timestamp": current.get("timestamp"),
            "baseline_timestamp": baseline.get("timestamp"),
            "components": {},
            "regressions": [],
            "improvements": [],
            "overall_change": 0.0,
        }

        total_change = 0.0
        comparison_count = 0

        # Compare each component
        current_components = current.get("components", {})
        baseline_components = baseline.get("components", {})

        for component in current_components.keys():
            if component not in baseline_components:
                continue

            current_time = current_components[component].get("elapsed_seconds", 0)
            baseline_time = baseline_components[component].get("elapsed_seconds", 0)

            if baseline_time == 0:
                continue

            change_percent = ((current_time - baseline_time) / baseline_time) * 100
            total_change += change_percent
            comparison_count += 1

            comparison["components"][component] = {
                "current": current_time,
                "baseline": baseline_time,
                "change_percent": change_percent,
                "change_seconds": current_time - baseline_time,
                "improved": change_percent < -5,  # >5% faster
                "regressed": change_percent > 10,  # >10% slower
                "stable": -5 <= change_percent <= 10,
            }

            # Track significant changes
            if change_percent > 10:
                comparison["regressions"].append(
                    {
                        "component": component,
                        "change_percent": change_percent,
                        "current": current_time,
                        "baseline": baseline_time,
                        "severity": (
                            "critical"
                            if change_percent > 50
                            else "high" if change_percent > 25 else "medium"
                        ),
                    }
                )
            elif change_percent < -5:
                comparison["improvements"].append(
                    {
                        "component": component,
                        "change_percent": change_percent,
                        "current": current_time,
                        "baseline": baseline_time,
                    }
                )

        # Calculate overall change
        if comparison_count > 0:
            comparison["overall_change"] = total_change / comparison_count

        return comparison

    def print_comparison(self, comparison: Dict):
        """Print detailed comparison results with color-coded output."""
        print(f"\n{'='*80}")
        print(f"📊 Benchmark Comparison Report")
        print(f"{'='*80}")
        print(f"📅 Current:  {comparison['current_timestamp']}")
        print(f"📅 Baseline: {comparison['baseline_timestamp']}")
        print(f"{'='*80}\n")

        # Print component-by-component comparison
        print("🔍 Component Analysis:")
        print(
            f"{'Component':<20} {'Change':<12} {'Baseline':<12} {'Current':<12} {'Status'}"
        )
        print("-" * 80)

        for component, data in sorted(comparison["components"].items()):
            change = data["change_percent"]
            baseline = data["baseline"]
            current = data["current"]

            # Determine status icon
            if data["improved"]:
                status = "✅ IMPROVED"
            elif data["regressed"]:
                status = "❌ REGRESSED"
            else:
                status = "➡️  STABLE"

            # Format change with sign
            change_str = f"{change:+.1f}%"

            print(
                f"{component:<20} {change_str:<12} {baseline:<12.2f} {current:<12.2f} {status}"
            )

        # Overall summary
        print(f"\n{'-'*80}")
        overall = comparison["overall_change"]
        overall_status = (
            "improved" if overall < -5 else "regressed" if overall > 10 else "stable"
        )
        print(f"📈 Overall Change: {overall:+.1f}% ({overall_status})")
        print(f"{'-'*80}\n")

        # Print regressions with severity
        if comparison["regressions"]:
            print(f"❌ Performance Regressions ({len(comparison['regressions'])}):")
            for reg in sorted(
                comparison["regressions"],
                key=lambda x: x["change_percent"],
                reverse=True,
            ):
                severity_icon = (
                    "🔴"
                    if reg["severity"] == "critical"
                    else "🟠" if reg["severity"] == "high" else "🟡"
                )
                print(
                    f"   {severity_icon} {reg['component']:<20} {reg['change_percent']:+6.1f}% "
                    f"({reg['baseline']:.2f}s → {reg['current']:.2f}s)"
                )
            print()

        # Print improvements
        if comparison["improvements"]:
            print(f"✅ Performance Improvements ({len(comparison['improvements'])}):")
            for imp in sorted(
                comparison["improvements"], key=lambda x: x["change_percent"]
            ):
                print(
                    f"   ⚡ {imp['component']:<20} {imp['change_percent']:+6.1f}% "
                    f"({imp['baseline']:.2f}s → {imp['current']:.2f}s)"
                )
            print()

        # No changes
        if not comparison["regressions"] and not comparison["improvements"]:
            print("➡️  All components stable (no significant changes)\n")

        print(f"{'='*80}\n")

    def generate_comparison_report(
        self, current_file: Path, baseline_file: Path, output_file: Path = None
    ) -> Path:
        """Generate a detailed comparison report as JSON."""
        comparison = self.compare_two_runs(current_file, baseline_file)

        if output_file is None:
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            output_file = self.results_dir / f"comparison_{timestamp}.json"

        with open(output_file, "w") as f:
            json.dump(comparison, f, indent=2)

        print(f"💾 Comparison report saved to: {output_file}")
        return output_file

    def analyze_trend(self, component: str = None, limit: int = 10) -> Dict:
        """
        Analyze performance trend over last N runs.

        Args:
            component: Specific component to analyze (None = all)
            limit: Number of recent runs to analyze

        Returns:
            Trend analysis with statistics
        """
        available = self.get_available_results()[:limit]

        if len(available) < 2:
            return {"error": "Insufficient data for trend analysis"}

        trend_data = {
            "component": component,
            "runs_analyzed": len(available),
            "data_points": [],
            "statistics": {},
        }

        # Collect data points
        for results_file in reversed(available):  # Oldest to newest
            results = self.load_results(results_file)
            timestamp = results.get("timestamp")

            if component:
                # Specific component
                comp_data = results.get("components", {}).get(component)
                if comp_data:
                    value = comp_data.get("elapsed_seconds", 0)
                    trend_data["data_points"].append(
                        {
                            "timestamp": timestamp,
                            "value": value,
                        }
                    )
            else:
                # Overall (average of all components)
                components = results.get("components", {})
                if components:
                    avg_time = sum(
                        c.get("elapsed_seconds", 0) for c in components.values()
                    ) / len(components)
                    trend_data["data_points"].append(
                        {
                            "timestamp": timestamp,
                            "value": avg_time,
                        }
                    )

        # Calculate statistics
        if trend_data["data_points"]:
            values = [dp["value"] for dp in trend_data["data_points"]]

            trend_data["statistics"] = {
                "min": min(values),
                "max": max(values),
                "mean": sum(values) / len(values),
                "first": values[0],
                "last": values[-1],
                "change": values[-1] - values[0],
                "change_percent": (
                    ((values[-1] - values[0]) / values[0] * 100) if values[0] > 0 else 0
                ),
                "trend": (
                    "improving"
                    if values[-1] < values[0]
                    else "degrading" if values[-1] > values[0] else "stable"
                ),
            }

        return trend_data


def compare_with_baseline(current_file: Path, baseline_file: Path = None) -> int:
    """
    Convenience function to compare current results with baseline.

    Args:
        current_file: Path to current results
        baseline_file: Path to baseline (None = use previous run)

    Returns:
        Exit code: 0 if no regressions, 1 if regressions found
    """
    comparator = BenchmarkComparator()

    if baseline_file is None:
        # Use previous run as baseline
        available = comparator.get_available_results()
        if len(available) < 2:
            print("⚠️  No baseline available for comparison")
            return 0

        # Find current file in list and use next one as baseline
        try:
            current_idx = available.index(current_file)
            if current_idx + 1 < len(available):
                baseline_file = available[current_idx + 1]
            else:
                print("⚠️  No older results available for comparison")
                return 0
        except ValueError:
            # Current file not in list, use most recent as baseline
            baseline_file = available[0]

    # Perform comparison
    comparison = comparator.compare_two_runs(current_file, baseline_file)
    comparator.print_comparison(comparison)

    # Generate detailed report
    comparator.generate_comparison_report(current_file, baseline_file)

    # Return exit code based on regressions
    if comparison["regressions"]:
        critical_regressions = [
            r for r in comparison["regressions"] if r["severity"] == "critical"
        ]
        if critical_regressions:
            print(
                f"🔴 CRITICAL: {len(critical_regressions)} critical performance regressions detected!"
            )
        return 1

    return 0
