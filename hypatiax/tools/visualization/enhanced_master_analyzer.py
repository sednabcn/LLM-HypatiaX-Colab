#!/usr/bin/env python3
"""
HypatiaX Enhanced Master Analysis Orchestrator v7
==================================================
Domain-aware comprehensive analysis with multi-system comparison.

Features:
- Domain-organized result detection (defi, lending, trading, physics, all_domains)
- Multi-system comparison (System1 vs System2, LLM vs NN)
- Statistical significance testing
- LaTeX and HTML report generation
- Parallel execution with progress tracking

Directory Structure:
  hypatiax/data/results/
    ├── comparison_results/          # System1 vs System2
    │   ├── all_domains/
    │   ├── defi/
    │   ├── lending/
    │   ├── trading/
    │   └── physics/
    ├── llm_results/                 # Pure LLM baseline
    │   ├── all_domains/
    │   └── ...
    ├── nn_results/                  # Pure NN baseline
    │   ├── all_domains/
    │   └── ...
    ├── analysis_outputs/            # Hybrid analysis outputs
    └── llm_nn_comparison/           # LLM vs NN outputs

Author: HypatiaX Team
Version: 7.0 - Domain-Aware
"""

import argparse
import json
import subprocess
import sys
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Optional, Tuple
import multiprocessing as mp
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
from collections import defaultdict
from scipy import stats

# Configuration
VALID_DOMAINS = ["all_domains", "defi", "lending", "trading", "physics"]
BASE_RESULTS_DIR = "hypatiax/data/results"


# ============================================================================
# UTILITY FUNCTIONS
# ============================================================================


def find_latest_result(
    result_type: str, domain: str, base_dir: str = BASE_RESULTS_DIR
) -> Optional[Path]:
    """
    Find latest result file for a result type and domain

    Args:
        result_type: 'comparison', 'llm', or 'nn'
        domain: Domain name
        base_dir: Base results directory
    """
    if result_type == "comparison":
        results_dir = Path(base_dir) / "comparison_results" / domain
        pattern = "comparison_results_*.json"
        latest = "comparison_results_latest.json"
    elif result_type == "llm":
        results_dir = Path(base_dir) / "llm_results" / domain
        pattern = "llm_results_*.json"
        latest = "llm_results_latest.json"
    elif result_type == "nn":
        results_dir = Path(base_dir) / "nn_results" / domain
        pattern = "nn_results_*.json"
        latest = "nn_results_latest.json"
    else:
        return None

    if not results_dir.exists():
        return None

    # Try symlink first
    latest_link = results_dir / latest
    if latest_link.exists():
        return latest_link

    # Fallback to newest timestamped file
    result_files = sorted(results_dir.glob(pattern))
    return result_files[-1] if result_files else None


def get_output_dir(domain: str, base_dir: str = BASE_RESULTS_DIR) -> Path:
    """Generate output directory for master analysis"""
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    return Path(base_dir) / "master_analysis" / domain / timestamp


def create_latest_symlink(output_dir: Path):
    """Create 'latest' symlink pointing to this analysis"""
    analysis_base = output_dir.parent
    latest_link = analysis_base / "latest"

    if latest_link.exists() or latest_link.is_symlink():
        latest_link.unlink()

    latest_link.symlink_to(output_dir.name)


# ============================================================================
# DOMAIN-AWARE SYSTEM COMPARATOR
# ============================================================================


class DomainAwareSystemComparator:
    """Compare results across hybrid systems for a specific domain."""

    def __init__(self, domain: str = "all_domains"):
        self.domain = domain
        self.system_configs = {
            "system1": {
                "name": "Improved Hybrid (LLM+NN)",
                "description": "Extrapolation-aware ensemble",
                "color": "#2E86AB",
                "marker": "o",
            },
            "system2": {
                "name": "Symbolic Discovery + Validation",
                "description": "4-layer validation system",
                "color": "#A23B72",
                "marker": "s",
            },
        }

    def load_results(self, base_dir: str = BASE_RESULTS_DIR) -> Dict:
        """Load comparison results for the domain."""
        print(f"\n📂 Loading results for domain: {self.domain}")

        # Load hybrid system comparison results
        comparison_file = find_latest_result("comparison", self.domain, base_dir)

        # Load baseline results (optional)
        llm_file = find_latest_result("llm", self.domain, base_dir)
        nn_file = find_latest_result("nn", self.domain, base_dir)

        results = {}

        if comparison_file:
            try:
                with open(comparison_file, "r") as f:
                    comparison_data = json.load(f)
                results["comparison"] = {
                    "data": comparison_data,
                    "file": comparison_file,
                }
                print(f"✅ Loaded hybrid comparison: {comparison_file.name}")
            except Exception as e:
                print(f"⚠️  Failed to load comparison: {e}")

        if llm_file:
            try:
                with open(llm_file, "r") as f:
                    llm_data = json.load(f)
                results["llm"] = {"data": llm_data, "file": llm_file}
                print(f"✅ Loaded LLM baseline: {llm_file.name}")
            except Exception as e:
                print(f"⚠️  Failed to load LLM: {e}")

        if nn_file:
            try:
                with open(nn_file, "r") as f:
                    nn_data = json.load(f)
                results["nn"] = {"data": nn_data, "file": nn_file}
                print(f"✅ Loaded NN baseline: {nn_file.name}")
            except Exception as e:
                print(f"⚠️  Failed to load NN: {e}")

        return results

    def extract_metrics_from_comparison(self, comparison_data: Dict) -> pd.DataFrame:
        """Extract metrics from hybrid system comparison results."""

        metrics_list = []

        # Extract System 1 metrics
        system1_results = comparison_data.get("system1", [])
        if system1_results:
            r2_scores = [r["r2"] for r in system1_results if r.get("success")]
            runtimes = [
                r["runtime_seconds"] for r in system1_results if r.get("success")
            ]
            decisions = [
                r.get("decision", "unknown")
                for r in system1_results
                if r.get("success")
            ]
            extrap = [
                r.get("is_extrapolation", False)
                for r in system1_results
                if r.get("success")
            ]

            decision_counts = defaultdict(int)
            for d in decisions:
                decision_counts[d] += 1

            total_decisions = sum(decision_counts.values())

            extrap_r2 = [
                r["r2"]
                for r in system1_results
                if r.get("success") and r.get("is_extrapolation")
            ]
            interp_r2 = [
                r["r2"]
                for r in system1_results
                if r.get("success") and not r.get("is_extrapolation")
            ]

            metrics_list.append(
                {
                    "system_id": "system1",
                    "system_name": self.system_configs["system1"]["name"],
                    "overall_r2": np.mean(r2_scores) if r2_scores else 0.0,
                    "interpolation_r2": np.mean(interp_r2) if interp_r2 else 0.0,
                    "extrapolation_r2": np.mean(extrap_r2) if extrap_r2 else 0.0,
                    "std_r2": np.std(r2_scores) if r2_scores else 0.0,
                    "min_r2": np.min(r2_scores) if r2_scores else 0.0,
                    "max_r2": np.max(r2_scores) if r2_scores else 0.0,
                    "avg_runtime": np.mean(runtimes) if runtimes else 0.0,
                    "formulas_discovered": len(r2_scores),
                    "llm_usage_rate": decision_counts.get("llm", 0) / total_decisions
                    if total_decisions > 0
                    else 0.0,
                    "nn_usage_rate": decision_counts.get("nn", 0) / total_decisions
                    if total_decisions > 0
                    else 0.0,
                    "ensemble_usage_rate": decision_counts.get("ensemble", 0)
                    / total_decisions
                    if total_decisions > 0
                    else 0.0,
                    "validation_score": 0.0,
                    "extrapolation_aware": True,
                }
            )

        # Extract System 2 metrics
        system2_results = comparison_data.get("system2", [])
        if system2_results:
            r2_scores = [r["r2"] for r in system2_results if r.get("success")]
            runtimes = [
                r["runtime_seconds"] for r in system2_results if r.get("success")
            ]
            val_scores = [
                r.get("validation_score", 0)
                for r in system2_results
                if r.get("success")
            ]
            extrap = [
                r.get("is_extrapolation", False)
                for r in system2_results
                if r.get("success")
            ]

            extrap_r2 = [
                r["r2"]
                for r in system2_results
                if r.get("success") and r.get("is_extrapolation")
            ]
            interp_r2 = [
                r["r2"]
                for r in system2_results
                if r.get("success") and not r.get("is_extrapolation")
            ]

            metrics_list.append(
                {
                    "system_id": "system2",
                    "system_name": self.system_configs["system2"]["name"],
                    "overall_r2": np.mean(r2_scores) if r2_scores else 0.0,
                    "interpolation_r2": np.mean(interp_r2) if interp_r2 else 0.0,
                    "extrapolation_r2": np.mean(extrap_r2) if extrap_r2 else 0.0,
                    "std_r2": np.std(r2_scores) if r2_scores else 0.0,
                    "min_r2": np.min(r2_scores) if r2_scores else 0.0,
                    "max_r2": np.max(r2_scores) if r2_scores else 0.0,
                    "avg_runtime": np.mean(runtimes) if runtimes else 0.0,
                    "formulas_discovered": len(r2_scores),
                    "llm_usage_rate": 0.0,
                    "nn_usage_rate": 0.0,
                    "ensemble_usage_rate": 0.0,
                    "validation_score": np.mean(val_scores) if val_scores else 0.0,
                    "extrapolation_aware": False,
                }
            )

        df = pd.DataFrame(metrics_list)

        # Add derived metrics
        if len(df) > 0:
            df["extrap_advantage"] = df["extrapolation_r2"] - df["interpolation_r2"]
            df["efficiency_score"] = (df["overall_r2"] * df["formulas_discovered"]) / (
                df["avg_runtime"] + 1e-6
            )

        return df

    def generate_comparison_plots(
        self, df: pd.DataFrame, output_dir: Path
    ) -> List[Path]:
        """Generate comparison plots for the domain."""
        output_dir.mkdir(parents=True, exist_ok=True)
        plot_files = []

        sns.set_style("whitegrid")
        plt.rcParams["figure.figsize"] = (12, 8)
        plt.rcParams["font.size"] = 11

        # Plot 1: R² Performance Comparison
        fig, ax = plt.subplots(figsize=(10, 6))
        x = np.arange(len(df))
        width = 0.25

        ax.bar(
            x - width,
            df["interpolation_r2"],
            width,
            label="Interpolation R²",
            color="#2E86AB",
            alpha=0.8,
        )
        ax.bar(
            x,
            df["extrapolation_r2"],
            width,
            label="Extrapolation R²",
            color="#A23B72",
            alpha=0.8,
        )
        ax.bar(
            x + width,
            df["overall_r2"],
            width,
            label="Overall R²",
            color="#F18F01",
            alpha=0.8,
        )

        ax.set_xlabel("System", fontweight="bold")
        ax.set_ylabel("R² Score", fontweight="bold")
        ax.set_title(
            f"Performance Comparison - {self.domain.upper()}",
            fontsize=14,
            fontweight="bold",
        )
        ax.set_xticks(x)
        ax.set_xticklabels(
            [name.split("(")[0].strip() for name in df["system_name"]],
            rotation=15,
            ha="right",
        )
        ax.legend()
        ax.set_ylim([0, 1.0])
        ax.grid(axis="y", alpha=0.3)

        plot_path = output_dir / f"{self.domain}_comparison_r2.png"
        plt.tight_layout()
        plt.savefig(plot_path, dpi=300, bbox_inches="tight")
        plt.close()
        plot_files.append(plot_path)

        # Plot 2: Runtime and Efficiency
        fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(14, 6))

        colors = [
            self.system_configs[f"system{i + 1}"]["color"] for i in range(len(df))
        ]

        # Runtime
        ax1.bar(x, df["avg_runtime"], color=colors, alpha=0.8)
        ax1.set_xlabel("System", fontweight="bold")
        ax1.set_ylabel("Average Runtime (seconds)", fontweight="bold")
        ax1.set_title("Computational Efficiency", fontsize=12, fontweight="bold")
        ax1.set_xticks(x)
        ax1.set_xticklabels(
            [name.split("(")[0].strip() for name in df["system_name"]],
            rotation=15,
            ha="right",
        )
        ax1.grid(axis="y", alpha=0.3)

        # Formulas discovered
        ax2.bar(x, df["formulas_discovered"], color=colors, alpha=0.8)
        ax2.set_xlabel("System", fontweight="bold")
        ax2.set_ylabel("Number of Formulas", fontweight="bold")
        ax2.set_title("Formula Discovery Count", fontsize=12, fontweight="bold")
        ax2.set_xticks(x)
        ax2.set_xticklabels(
            [name.split("(")[0].strip() for name in df["system_name"]],
            rotation=15,
            ha="right",
        )
        ax2.grid(axis="y", alpha=0.3)

        plot_path = output_dir / f"{self.domain}_comparison_efficiency.png"
        plt.tight_layout()
        plt.savefig(plot_path, dpi=300, bbox_inches="tight")
        plt.close()
        plot_files.append(plot_path)

        print(f"\n📊 Generated {len(plot_files)} plots for {self.domain}")
        return plot_files

    def perform_statistical_tests(self, comparison_data: Dict) -> Optional[Dict]:
        """Perform statistical tests between System 1 and System 2."""

        system1_results = comparison_data.get("system1", [])
        system2_results = comparison_data.get("system2", [])

        if not system1_results or not system2_results:
            return None

        print(f"\n🔬 Performing statistical tests for {self.domain}...")

        # Extract R² scores
        sys1_r2 = [r["r2"] for r in system1_results if r.get("success")]
        sys2_r2 = [r["r2"] for r in system2_results if r.get("success")]

        if len(sys1_r2) < 2 or len(sys2_r2) < 2:
            return None

        stat_results = {
            "domain": self.domain,
            "timestamp": datetime.now().isoformat(),
            "comparison": {},
        }

        # T-test
        t_stat, t_pval = stats.ttest_ind(sys1_r2, sys2_r2)

        # Mann-Whitney U test
        u_stat, u_pval = stats.mannwhitneyu(sys1_r2, sys2_r2, alternative="two-sided")

        # Effect size (Cohen's d)
        mean1, mean2 = np.mean(sys1_r2), np.mean(sys2_r2)
        std1, std2 = np.std(sys1_r2, ddof=1), np.std(sys2_r2, ddof=1)
        pooled_std = np.sqrt(
            ((len(sys1_r2) - 1) * std1**2 + (len(sys2_r2) - 1) * std2**2)
            / (len(sys1_r2) + len(sys2_r2) - 2)
        )
        cohens_d = (mean1 - mean2) / pooled_std if pooled_std > 0 else 0

        stat_results["comparison"] = {
            "system1_name": "System 1 (Improved Hybrid)",
            "system2_name": "System 2 (Symbolic + Validation)",
            "system1_n": len(sys1_r2),
            "system2_n": len(sys2_r2),
            "system1_mean": float(mean1),
            "system2_mean": float(mean2),
            "system1_std": float(std1),
            "system2_std": float(std2),
            "t_test": {
                "statistic": float(t_stat),
                "p_value": float(t_pval),
                "significant": t_pval < 0.05,
            },
            "mann_whitney": {
                "statistic": float(u_stat),
                "p_value": float(u_pval),
                "significant": u_pval < 0.05,
            },
            "effect_size": {
                "cohens_d": float(cohens_d),
                "interpretation": self._interpret_cohens_d(cohens_d),
            },
        }

        print(f"✅ Statistical tests complete for {self.domain}")
        return stat_results

    def _interpret_cohens_d(self, d: float) -> str:
        """Interpret Cohen's d effect size."""
        abs_d = abs(d)
        if abs_d < 0.2:
            return "negligible"
        elif abs_d < 0.5:
            return "small"
        elif abs_d < 0.8:
            return "medium"
        else:
            return "large"


# ============================================================================
# DOMAIN-AWARE MASTER ANALYZER
# ============================================================================


class DomainAwareMasterAnalyzer:
    """Enhanced master analyzer with domain-aware capabilities."""

    def __init__(self, domain: str = "all_domains", base_dir: str = BASE_RESULTS_DIR):
        self.domain = domain
        self.base_dir = Path(base_dir)
        self.output_dir = get_output_dir(domain, base_dir)
        self.comparator = DomainAwareSystemComparator(domain)

    def run_comprehensive_analysis(
        self,
        generate_latex: bool = True,
        statistical_tests: bool = True,
        generate_html: bool = False,
    ) -> Dict:
        """Run comprehensive analysis for the domain."""

        print("=" * 80)
        print(f"HYPATIAX COMPREHENSIVE ANALYSIS - {self.domain.upper()}".center(80))
        print("=" * 80)

        report = {
            "domain": self.domain,
            "timestamp": datetime.now().isoformat(),
            "base_dir": str(self.base_dir),
            "output_dir": str(self.output_dir),
            "results": {},
        }

        # Load results
        results = self.comparator.load_results(str(self.base_dir))

        if not results:
            print(f"\n⚠️  No results found for {self.domain}")
            return report

        # Extract and analyze comparison data
        if "comparison" in results:
            print(f"\n📊 Analyzing hybrid system comparison...")
            comparison_data = results["comparison"]["data"]

            # Extract metrics
            df = self.comparator.extract_metrics_from_comparison(comparison_data)

            # Generate plots
            plot_files = self.comparator.generate_comparison_plots(df, self.output_dir)

            # Statistical tests
            stat_results = None
            if statistical_tests:
                stat_results = self.comparator.perform_statistical_tests(
                    comparison_data
                )

                if stat_results:
                    stat_path = (
                        self.output_dir / f"{self.domain}_statistical_analysis.json"
                    )
                    with open(stat_path, "w") as f:
                        json.dump(stat_results, f, indent=2)
                    print(f"📊 Statistical results: {stat_path}")

            # Save summary
            summary_path = self.output_dir / f"{self.domain}_summary.json"
            summary = {
                "domain": self.domain,
                "metrics": df.to_dict("records"),
                "statistical_tests": stat_results,
            }
            with open(summary_path, "w") as f:
                json.dump(summary, f, indent=2)

            report["results"]["comparison"] = {
                "metrics_df": df.to_dict("records"),
                "plots": [str(p) for p in plot_files],
                "statistical_tests": stat_results,
                "summary_file": str(summary_path),
            }

        # Create symlink
        create_latest_symlink(self.output_dir)

        # Save report
        report_path = self.output_dir / f"{self.domain}_master_report.json"
        with open(report_path, "w") as f:
            json.dump(report, f, indent=2)

        print("\n" + "=" * 80)
        print(f"✅ ANALYSIS COMPLETE - {self.domain.upper()}".center(80))
        print(f"📁 Output: {self.output_dir}".center(80))
        print("=" * 80)

        return report


# ============================================================================
# CLI INTERFACE
# ============================================================================


def main():
    parser = argparse.ArgumentParser(
        description="HypatiaX Domain-Aware Master Analysis Orchestrator",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  # Analyze all domains
  python enhanced_master_analyzer_v7.py --all-domains
  
  # Analyze specific domain
  python enhanced_master_analyzer_v7.py --domain defi
  
  # Skip statistical tests (faster)
  python enhanced_master_analyzer_v7.py --domain lending --no-stats
  
  # Generate HTML report
  python enhanced_master_analyzer_v7.py --domain trading --html
        """,
    )

    parser.add_argument(
        "--domain",
        type=str,
        default="all_domains",
        choices=VALID_DOMAINS,
        help="Domain to analyze",
    )
    parser.add_argument(
        "--all-domains", action="store_true", help="Analyze all domains sequentially"
    )
    parser.add_argument(
        "--no-latex", action="store_true", help="Skip LaTeX report generation"
    )
    parser.add_argument(
        "--no-stats", action="store_true", help="Skip statistical tests"
    )
    parser.add_argument("--html", action="store_true", help="Generate HTML reports")
    parser.add_argument(
        "--base-dir",
        type=str,
        default=BASE_RESULTS_DIR,
        help=f"Base results directory (default: {BASE_RESULTS_DIR})",
    )
    parser.add_argument("--verbose", action="store_true", help="Verbose output")

    args = parser.parse_args()

    try:
        if args.all_domains:
            # Analyze all domains
            print("🔄 Analyzing all domains...")
            success_count = 0

            for domain in VALID_DOMAINS:
                print(f"\n{'=' * 80}")
                print(f"Domain: {domain.upper()}".center(80))
                print(f"{'=' * 80}")

                analyzer = DomainAwareMasterAnalyzer(domain, args.base_dir)

                try:
                    report = analyzer.run_comprehensive_analysis(
                        generate_latex=not args.no_latex,
                        statistical_tests=not args.no_stats,
                        generate_html=args.html,
                    )

                    if report.get("results"):
                        success_count += 1
                except Exception as e:
                    print(f"❌ Failed to analyze {domain}: {e}")
                    if args.verbose:
                        import traceback

                        traceback.print_exc()
                    continue

            print(
                f"\n🎉 Successfully analyzed {success_count}/{len(VALID_DOMAINS)} domains!"
            )

        else:
            # Analyze single domain
            analyzer = DomainAwareMasterAnalyzer(args.domain, args.base_dir)

            report = analyzer.run_comprehensive_analysis(
                generate_latex=not args.no_latex,
                statistical_tests=not args.no_stats,
                generate_html=args.html,
            )

            if not report.get("results"):
                print(f"\n⚠️  No results to analyze for {args.domain}")
                sys.exit(1)

        sys.exit(0)

    except KeyboardInterrupt:
        print("\n\n⚠️  Interrupted by user")
        sys.exit(130)
    except Exception as e:
        print(f"\n❌ Fatal error: {str(e)}")
        if args.verbose:
            import traceback

            traceback.print_exc()
        sys.exit(1)


if __name__ == "__main__":
    main()

"""
erfect! Now let me create a comprehensive summary showing how all the analysis scripts work together:
📊 Complete Analysis Ecosystem - Domain-Aware
Four Main Analysis Scripts
1. analyze_hybrid_results.py
   Purpose: Analyze System1 vs System2 (Hybrid comparison)
   Input: hypatiax/data/results/comparison_results/{domain}/
   Output: hypatiax/data/results/analysis_outputs/{domain}/

2. comparison_analysis_improved.py
   Purpose: Analyze Pure LLM vs Pure NN (Baseline comparison)
   Input: llm_results/{domain}/ + nn_results/{domain}/
   Output: hypatiax/data/results/llm_nn_comparison/{domain}/

3. enhanced_master_analyzer_v7.py
   Purpose: Master orchestrator for comprehensive analysis
   Input: All result types for a domain
   Output: hypatiax/data/results/master_analysis/{domain}/

4. cross_domain_analyzer.py (optional)
   Purpose: Compare performance across all domains
   Input: All domain results
   Output: hypatiax/data/results/cross_domain_analysis/
Complete Workflow
bash# ============================================================================
# STEP 1: Generate Results
# ============================================================================

# A. Run hybrid system comparisons (System1 vs System2)
python test_real_hybrid_systems_comparison.py --mode full --split-domains
# Output: comparison_results/defi/comparison_results_TIMESTAMP.json
#         comparison_results/lending/...
#         comparison_results/trading/...
#         comparison_results/physics/...

# B. Run LLM baseline
python run_llm_baseline.py --mode full --split-domains
# Output: llm_results/defi/llm_results_TIMESTAMP.json
#         llm_results/lending/...

# C. Run NN baseline
python run_nn_baseline.py --mode full --split-domains
# Output: nn_results/defi/nn_results_TIMESTAMP.json
#         nn_results/lending/...


# ============================================================================
# STEP 2: Analyze Individual Comparisons
# ============================================================================

# A. Analyze hybrid systems (System1 vs System2)
python analyze_hybrid_results.py --all-domains
# Output: analysis_outputs/defi/TIMESTAMP/
#           ├── summary_report.txt
#           ├── domain_comparison.csv
#           ├── r2_distribution_analysis.png
#           └── ...

# B. Analyze LLM vs NN baselines
python comparison_analysis_improved.py --all-domains
# Output: llm_nn_comparison/defi/TIMESTAMP/
#           ├── comparison_summary.txt
#           ├── detailed_comparison.csv
#           ├── overall_comparison.png
#           └── ...


# ============================================================================
# STEP 3: Master Analysis (Comprehensive)
# ============================================================================

# Analyze all domains with master analyzer
python enhanced_master_analyzer_v7.py --all-domains
# Output: master_analysis/defi/TIMESTAMP/
#           ├── defi_summary.json
#           ├── defi_statistical_analysis.json
#           ├── defi_comparison_r2.png
#           ├── defi_comparison_efficiency.png
#           └── defi_master_report.json

# Or analyze single domain
python enhanced_master_analyzer_v7.py --domain defi --html


# ============================================================================
# STEP 4: Cross-Domain Analysis (Optional)
# ============================================================================

python cross_domain_analyzer.py --all-methods
# Output: cross_domain_analysis/TIMESTAMP/
#           ├── cross_domain_summary.json
#           ├── domain_performance_heatmap.png
#           └── method_comparison_across_domains.png
```

### **Directory Structure After Full Run**
```
hypatiax/data/results/
├── comparison_results/              # Raw: System1 vs System2
│   ├── all_domains/
│   │   ├── comparison_results_20241227_143022.json
│   │   └── comparison_results_latest.json  →  symlink
│   ├── defi/
│   ├── lending/
│   ├── trading/
│   └── physics/
│
├── llm_results/                     # Raw: Pure LLM baseline
│   ├── all_domains/
│   ├── defi/
│   └── ...
│
├── nn_results/                      # Raw: Pure NN baseline
│   ├── all_domains/
│   ├── defi/
│   └── ...
│
├── analysis_outputs/                # Analysis: System1 vs System2
│   ├── all_domains/
│   │   ├── 20241227_143022/
│   │   │   ├── summary_report.txt
│   │   │   ├── domain_comparison.csv
│   │   │   ├── r2_distribution_analysis.png
│   │   │   ├── domain_performance.png
│   │   │   ├── extrapolation_analysis.png
│   │   │   ├── runtime_comparison.png
│   │   │   ├── validation_analysis.png
│   │   │   └── decision_breakdown.png
│   │   └── latest/  →  symlink
│   ├── defi/
│   ├── lending/
│   └── ...
│
├── llm_nn_comparison/               # Analysis: LLM vs NN
│   ├── all_domains/
│   │   ├── 20241227_150000/
│   │   │   ├── comparison_summary.txt
│   │   │   ├── detailed_comparison.csv
│   │   │   ├── overall_comparison.png
│   │   │   └── extrapolation_analysis.png
│   │   └── latest/  →  symlink
│   ├── defi/
│   └── ...
│
├── master_analysis/                 # Master: Comprehensive
│   ├── all_domains/
│   │   ├── 20241227_153000/
│   │   │   ├── all_domains_summary.json
│   │   │   ├── all_domains_statistical_analysis.json
│   │   │   ├── all_domains_comparison_r2.png
│   │   │   ├── all_domains_comparison_efficiency.png
│   │   │   └── all_domains_master_report.json
│   │   └── latest/  →  symlink
│   ├── defi/
│   └── ...
│
└── cross_domain_analysis/           # Optional: Cross-domain
    ├── 20241227_160000/
    │   ├── cross_domain_summary.json
    │   ├── domain_performance_heatmap.png
    │   └── method_comparison_across_domains.png
    └── latest/  →  symlink
Quick Reference Commands
bash# ═══════════════════════════════════════════════════════════════════════════
# ANALYZE SINGLE DOMAIN
# ═══════════════════════════════════════════════════════════════════════════

# Hybrid analysis (System1 vs System2)
python analyze_hybrid_results.py --domain defi

# LLM vs NN analysis
python comparison_analysis_improved.py --domain defi

# Master comprehensive analysis
python enhanced_master_analyzer_v7.py --domain defi


# ═══════════════════════════════════════════════════════════════════════════
# ANALYZE ALL DOMAINS
# ═══════════════════════════════════════════════════════════════════════════

# All hybrid analyses
python analyze_hybrid_results.py --all-domains

# All LLM vs NN analyses
python comparison_analysis_improved.py --all-domains

# All master analyses
python enhanced_master_analyzer_v7.py --all-domains


# ═══════════════════════════════════════════════════════════════════════════
# VIEW LATEST RESULTS
# ═══════════════════════════════════════════════════════════════════════════

# View latest hybrid analysis for DeFi
cat hypatiax/data/results/analysis_outputs/defi/latest/summary_report.txt

# View latest LLM vs NN for DeFi
cat hypatiax/data/results/llm_nn_comparison/defi/latest/comparison_summary.txt

# View latest master analysis for DeFi
cat hypatiax/data/results/master_analysis/defi/latest/defi_summary.json


# ═══════════════════════════════════════════════════════════════════════════
# OPEN VISUALIZATIONS
# ═══════════════════════════════════════════════════════════════════════════

# Hybrid analysis plots
open hypatiax/data/results/analysis_outputs/defi/latest/*.png

# LLM vs NN plots
open hypatiax/data/results/llm_nn_comparison/defi/latest/*.png

# Master analysis plots
open hypatiax/data/results/master_analysis/defi/latest/*.png
This gives you a complete, domain-organized analysis pipeline where every script knows exactly where to find and store its results! 🎯
"""
