#!/usr/bin/env python3
"""
Hybrid System Comparison - Domain-Aware Visualization & Statistical Testing
===========================================================================
Comprehensive visualization and statistical analysis for comparing hybrid
discovery architectures across different domains.

Author: HypatiaX Team
Version: 2.0

Place in: hypatiax/tools/visualization/hypatiax_hybrid_system_visualization.py
"""

import argparse
import json
from pathlib import Path
from typing import Dict, List, Optional

import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
import seaborn as sns
from scipy import stats

# Set publication-quality style
plt.style.use("seaborn-v0_8-darkgrid")
sns.set_palette("husl")


# ============================================================================
# DOMAIN-AWARE DATA LOADER
# ============================================================================


class DomainDataLoader:
    """Load and organize results by domain."""

    DOMAINS = ["all_domains", "defi", "lending", "trading", "physics"]

    def __init__(self, results_dir: str = "hypatiax/data/results"):
        self.results_dir = Path(results_dir)
        self.comparison_dir = self.results_dir / "comparison_results"

    def load_domain_results(self, domain: str) -> Optional[pd.DataFrame]:
        """Load results for a specific domain."""
        domain_dir = self.comparison_dir / domain

        if not domain_dir.exists():
            print(f"⚠️  Domain directory not found: {domain_dir}")
            return None

        # Check for latest link
        latest_link = domain_dir / "comparison_results_latest.json"
        if latest_link.exists():
            data_file = latest_link
        else:
            # Find most recent file
            files = sorted(domain_dir.glob("comparison_results_*.json"))
            if not files:
                print(f"⚠️  No results found for domain: {domain}")
                return None
            data_file = files[-1]

        print(f"📂 Loading {domain}: {data_file.name}")

        try:
            with open(data_file, "r") as f:
                data = json.load(f)

            # Convert to DataFrame
            if isinstance(data, dict) and "results" in data:
                df = pd.DataFrame(data["results"])
            elif isinstance(data, list):
                df = pd.DataFrame(data)
            else:
                df = pd.DataFrame([data])

            # Add domain column
            df["domain"] = domain

            return df

        except Exception as e:
            print(f"❌ Error loading {domain}: {e}")
            return None

    def load_all_available_domains(self):
        """Load all domains that have results."""
        all_dfs = []
        loaded_domains = []

        for domain in self.DOMAINS:
            df = self.load_domain_results(domain)
            if df is not None:
                all_dfs.append(df)
                loaded_domains.append(domain)

        if not all_dfs:
            raise ValueError("No domain results found!")

        combined_df = pd.concat(all_dfs, ignore_index=True)

        print(f"\n✅ Loaded {len(loaded_domains)} domains: {', '.join(loaded_domains)}")
        print(f"   Total results: {len(combined_df)}")

        return combined_df, loaded_domains


# ============================================================================
# DOMAIN-AWARE VISUALIZATION
# ============================================================================


class DomainAwareVisualizer:
    """Generate publication-quality visualizations with domain breakdown."""

    def __init__(self, output_dir: str = "figures"):
        self.output_dir = Path(output_dir)
        self.output_dir.mkdir(exist_ok=True, parents=True)
        print(f"📊 Visualizer initialized - saving to: {self.output_dir}")

    def plot_cross_domain_comparison(
        self, results_df: pd.DataFrame, metric: str = "r2_score", save: bool = True
    ):
        """Compare performance across domains."""
        fig, ax = plt.subplots(figsize=(12, 6))

        # Group by domain and architecture
        grouped = (
            results_df.groupby(["domain", "architecture"])[metric].mean().unstack()
        )

        # Handle missing columns
        if "llm_nn" not in grouped.columns:
            grouped["llm_nn"] = np.nan
        if "llm_symbolic_validation" not in grouped.columns:
            grouped["llm_symbolic_validation"] = np.nan

        # Rename for readability
        grouped.columns = ["LLM+NN", "LLM+Symbolic+Val"]

        # Plot grouped bars
        grouped.plot(
            kind="bar",
            ax=ax,
            color=["#3498db", "#e74c3c"],
            alpha=0.8,
            edgecolor="black",
            linewidth=1.2,
        )

        ax.set_xlabel("Domain", fontsize=12, fontweight="bold")
        ax.set_ylabel(metric.replace("_", " ").title(), fontsize=12, fontweight="bold")
        ax.set_title(
            f"{metric.replace('_', ' ').title()} Across Domains",
            fontsize=14,
            fontweight="bold",
        )
        ax.legend(title="Architecture", fontsize=10)
        ax.grid(axis="y", alpha=0.3)
        plt.xticks(rotation=45, ha="right")

        plt.tight_layout()

        if save:
            filepath = self.output_dir / f"cross_domain_{metric}.png"
            plt.savefig(filepath, dpi=300, bbox_inches="tight")
            print(f"✅ Saved: {filepath}")

        plt.close()
        return fig

    def plot_domain_specific_breakdown(
        self, results_df: pd.DataFrame, domain: str, save: bool = True
    ):
        """Create detailed breakdown for a specific domain."""
        # Filter to domain
        domain_df = results_df[results_df["domain"] == domain]

        if len(domain_df) == 0:
            print(f"⚠️  No results for domain: {domain}")
            return None

        fig, axes = plt.subplots(2, 2, figsize=(14, 10))
        fig.suptitle(
            f"Domain Analysis: {domain.upper()}", fontsize=16, fontweight="bold"
        )

        # 1. R² Score comparison
        ax = axes[0, 0]
        r2_data = domain_df.groupby("architecture")["r2_score"].mean()
        bars = ax.bar(
            range(len(r2_data)),
            r2_data.values,
            color=["#3498db", "#e74c3c"],
            alpha=0.8,
            edgecolor="black",
        )
        ax.set_xticks(range(len(r2_data)))
        ax.set_xticklabels(["LLM+NN", "LLM+Sym+Val"], rotation=45, ha="right")
        ax.set_ylabel("R² Score", fontweight="bold")
        ax.set_title("Discovery Quality")
        ax.grid(axis="y", alpha=0.3)

        for bar in bars:
            height = bar.get_height()
            ax.text(
                bar.get_x() + bar.get_width() / 2.0,
                height,
                f"{height:.3f}",
                ha="center",
                va="bottom",
                fontweight="bold",
            )

        # 2. Validation Score (Architecture B only)
        ax = axes[0, 1]
        arch_b = domain_df[domain_df["architecture"] == "llm_symbolic_validation"]
        if len(arch_b) > 0 and "validation_score" in arch_b.columns:
            val_score = arch_b["validation_score"].mean()
            ax.bar([0], [val_score], color="#2ecc71", alpha=0.8, edgecolor="black")
            ax.set_xticks([0])
            ax.set_xticklabels(["Arch B"])
            ax.set_ylabel("Validation Score", fontweight="bold")
            ax.set_title("Validation Quality")
            ax.set_ylim(0, 100)
            ax.axhline(y=85, color="red", linestyle="--", label="Threshold")
            ax.text(
                0, val_score + 2, f"{val_score:.1f}", ha="center", fontweight="bold"
            )
            ax.legend()
        else:
            ax.text(0.5, 0.5, "N/A", ha="center", va="center", fontsize=20)
            ax.set_xticks([])
        ax.grid(axis="y", alpha=0.3)

        # 3. Discovery Time
        ax = axes[1, 0]
        time_data = domain_df.groupby("architecture")["discovery_time"].mean()
        bars = ax.bar(
            range(len(time_data)),
            time_data.values,
            color=["#3498db", "#e74c3c"],
            alpha=0.8,
            edgecolor="black",
        )
        ax.set_xticks(range(len(time_data)))
        ax.set_xticklabels(["LLM+NN", "LLM+Sym+Val"], rotation=45, ha="right")
        ax.set_ylabel("Time (seconds)", fontweight="bold")
        ax.set_title("Discovery Efficiency")
        ax.grid(axis="y", alpha=0.3)

        for bar in bars:
            height = bar.get_height()
            ax.text(
                bar.get_x() + bar.get_width() / 2.0,
                height,
                f"{height:.2f}s",
                ha="center",
                va="bottom",
                fontweight="bold",
            )

        # 4. Production Ready percentage
        ax = axes[1, 1]
        prod_data = domain_df.groupby("architecture")["production_ready"].mean() * 100
        bars = ax.bar(
            range(len(prod_data)),
            prod_data.values,
            color=["#3498db", "#e74c3c"],
            alpha=0.8,
            edgecolor="black",
        )
        ax.set_xticks(range(len(prod_data)))
        ax.set_xticklabels(["LLM+NN", "LLM+Sym+Val"], rotation=45, ha="right")
        ax.set_ylabel("Production Ready (%)", fontweight="bold")
        ax.set_title("Deployment Readiness")
        ax.set_ylim(0, 110)
        ax.grid(axis="y", alpha=0.3)

        for bar in bars:
            height = bar.get_height()
            ax.text(
                bar.get_x() + bar.get_width() / 2.0,
                height,
                f"{height:.1f}%",
                ha="center",
                va="bottom",
                fontweight="bold",
            )

        plt.tight_layout()

        if save:
            filepath = self.output_dir / f"domain_breakdown_{domain}.png"
            plt.savefig(filepath, dpi=300, bbox_inches="tight")
            print(f"✅ Saved: {filepath}")

        plt.close()
        return fig

    def plot_domain_heatmap(
        self, results_df: pd.DataFrame, metric: str = "r2_score", save: bool = True
    ):
        """Create heatmap showing metric across domains and architectures."""
        fig, ax = plt.subplots(figsize=(10, 6))

        # Pivot table
        pivot = results_df.pivot_table(
            values=metric, index="domain", columns="architecture", aggfunc="mean"
        )

        # Rename columns
        pivot.columns = ["LLM+NN", "LLM+Symbolic+Val"]

        # Heatmap
        sns.heatmap(
            pivot,
            annot=True,
            fmt=".3f",
            cmap="RdYlGn",
            center=0.9 if metric == "r2_score" else 85,
            ax=ax,
            cbar_kws={"label": metric.replace("_", " ").title()},
            linewidths=1,
            linecolor="black",
        )

        ax.set_title(
            f"{metric.replace('_', ' ').title()} Heatmap",
            fontsize=14,
            fontweight="bold",
        )
        ax.set_xlabel("Architecture", fontsize=12, fontweight="bold")
        ax.set_ylabel("Domain", fontsize=12, fontweight="bold")

        plt.tight_layout()

        if save:
            filepath = self.output_dir / f"domain_heatmap_{metric}.png"
            plt.savefig(filepath, dpi=300, bbox_inches="tight")
            print(f"✅ Saved: {filepath}")

        plt.close()
        return fig

    def generate_all_visualizations(self, results_df: pd.DataFrame, domains: List[str]):
        """Generate all standard visualizations."""
        print("\n" + "=" * 80)
        print("GENERATING DOMAIN-AWARE VISUALIZATIONS")
        print("=" * 80 + "\n")

        # Cross-domain comparisons
        print("Creating cross-domain plots...")
        self.plot_cross_domain_comparison(results_df, "r2_score")
        self.plot_cross_domain_comparison(results_df, "discovery_time")
        self.plot_domain_heatmap(results_df, "r2_score")

        # Domain-specific breakdowns
        print("\nCreating domain-specific plots...")
        for domain in domains:
            self.plot_domain_specific_breakdown(results_df, domain)

        print(f"\n✅ All visualizations saved to: {self.output_dir}")


# ============================================================================
# STATISTICAL ANALYSIS
# ============================================================================


class StatisticalAnalyzer:
    """Perform statistical significance testing with domain awareness."""

    def __init__(self, alpha: float = 0.05):
        self.alpha = alpha
        print(f"📊 Statistical Analyzer initialized (α={alpha})")

    def paired_t_test(
        self,
        results_df: pd.DataFrame,
        metric: str = "r2_score",
        domain: Optional[str] = None,
    ) -> Dict:
        """Perform paired t-test, optionally for specific domain."""
        if domain:
            results_df = results_df[results_df["domain"] == domain]

        arch_a = results_df[results_df["architecture"] == "llm_nn"].set_index(
            "test_case"
        )[metric]
        arch_b = results_df[
            results_df["architecture"] == "llm_symbolic_validation"
        ].set_index("test_case")[metric]

        common_tests = arch_a.index.intersection(arch_b.index)

        if len(common_tests) < 2:
            return {
                "test": "paired_t_test",
                "metric": metric,
                "domain": domain,
                "error": "Insufficient paired samples",
                "n_pairs": len(common_tests),
            }

        a_values = arch_a.loc[common_tests].values
        b_values = arch_b.loc[common_tests].values

        mask = ~(np.isnan(a_values) | np.isnan(b_values))
        a_values = a_values[mask]
        b_values = b_values[mask]

        statistic, pvalue = stats.ttest_rel(a_values, b_values)

        diff = a_values - b_values
        cohen_d = (
            np.mean(diff) / np.std(diff, ddof=1) if np.std(diff, ddof=1) > 0 else 0
        )

        significant = pvalue < self.alpha

        if significant:
            winner = (
                "Architecture A (LLM+NN)"
                if np.mean(a_values) > np.mean(b_values)
                else "Architecture B (LLM+Symbolic+Val)"
            )
        else:
            winner = "No significant difference"

        return {
            "test": "paired_t_test",
            "metric": metric,
            "domain": domain or "all",
            "n_pairs": len(a_values),
            "mean_a": float(np.mean(a_values)),
            "mean_b": float(np.mean(b_values)),
            "std_a": float(np.std(a_values, ddof=1)),
            "std_b": float(np.std(b_values, ddof=1)),
            "t_statistic": float(statistic),
            "p_value": float(pvalue),
            "significant": significant,
            "alpha": self.alpha,
            "cohen_d": float(cohen_d),
            "effect_size": self._interpret_effect_size(cohen_d),
            "winner": winner,
        }

    def comprehensive_domain_analysis(
        self, results_df: pd.DataFrame, domains: List[str], metrics: List[str] = None
    ) -> Dict:
        """Perform comprehensive analysis across domains."""
        if metrics is None:
            metrics = ["r2_score", "validation_score", "discovery_time"]

        print("\n" + "=" * 80)
        print("COMPREHENSIVE DOMAIN-AWARE STATISTICAL ANALYSIS")
        print("=" * 80 + "\n")

        analysis = {"overall": {}, "by_domain": {}}

        # Overall analysis
        print("OVERALL ANALYSIS (All Domains)")
        print("-" * 40)
        for metric in metrics:
            result = self.paired_t_test(results_df, metric)
            analysis["overall"][metric] = result

            if "error" not in result:
                print(f"\n{metric}:")
                print(f"  Mean A: {result['mean_a']:.4f}")
                print(f"  Mean B: {result['mean_b']:.4f}")
                print(f"  p-value: {result['p_value']:.4f}")
                print(f"  Significant: {'Yes' if result['significant'] else 'No'}")
                print(f"  Winner: {result['winner']}")

        # Domain-specific analysis
        for domain in domains:
            print(f"\n{'=' * 80}")
            print(f"DOMAIN: {domain.upper()}")
            print("-" * 40)

            analysis["by_domain"][domain] = {}

            for metric in metrics:
                result = self.paired_t_test(results_df, metric, domain=domain)
                analysis["by_domain"][domain][metric] = result

                if "error" not in result:
                    print(f"\n{metric}:")
                    print(f"  Mean A: {result['mean_a']:.4f}")
                    print(f"  Mean B: {result['mean_b']:.4f}")
                    print(f"  p-value: {result['p_value']:.4f}")
                    print(f"  Winner: {result['winner']}")

        return analysis

    def _interpret_effect_size(self, cohen_d: float) -> str:
        """Interpret Cohen's d effect size."""
        abs_d = abs(cohen_d)
        if abs_d < 0.2:
            return "negligible"
        elif abs_d < 0.5:
            return "small"
        elif abs_d < 0.8:
            return "medium"
        else:
            return "large"

    def export_statistical_report(
        self, analysis: Dict, filepath: str = "statistical_analysis.json"
    ):
        """Export statistical analysis to JSON."""
        with open(filepath, "w") as f:
            json.dump(analysis, f, indent=2, default=str)
        print(f"\n✅ Statistical analysis exported to: {filepath}")


# ============================================================================
# CLI INTERFACE
# ============================================================================


def main():
    parser = argparse.ArgumentParser(
        description="Domain-Aware Visualization & Statistical Testing"
    )

    parser.add_argument(
        "--input", type=str, help="Path to specific comparison results file"
    )
    parser.add_argument("--domain", type=str, choices=DomainDataLoader.DOMAINS)
    parser.add_argument("--results-dir", type=str, default="hypatiax/data/results")
    parser.add_argument("--output-dir", type=str, default="figures")
    parser.add_argument("--alpha", type=float, default=0.05)
    parser.add_argument(
        "--metrics",
        nargs="+",
        default=["r2_score", "validation_score", "discovery_time"],
    )
    parser.add_argument("--visualize", action="store_true")
    parser.add_argument("--statistics", action="store_true")
    parser.add_argument("--all", action="store_true")
    parser.add_argument("--verbose", action="store_true")

    args = parser.parse_args()

    # Load data
    print(f"📂 Loading data...")

    if args.input:
        print(f"   From file: {args.input}")
        with open(args.input, "r") as f:
            data = json.load(f)

        if isinstance(data, dict) and "results" in data:
            results_df = pd.DataFrame(data["results"])
        elif isinstance(data, list):
            results_df = pd.DataFrame(data)
        else:
            results_df = pd.DataFrame([data])

        domains = (
            results_df["domain"].unique().tolist()
            if "domain" in results_df.columns
            else ["unknown"]
        )

    else:
        loader = DomainDataLoader(results_dir=args.results_dir)

        if args.domain:
            results_df = loader.load_domain_results(args.domain)
            if results_df is None:
                print(f"❌ No results found for domain: {args.domain}")
                return
            domains = [args.domain]
        else:
            results_df, domains = loader.load_all_available_domains()

    print(f"✅ Loaded {len(results_df)} results from {len(domains)} domain(s)")
    print(f"   Domains: {', '.join(domains)}")

    # Perform requested operations
    if args.all or args.visualize:
        visualizer = DomainAwareVisualizer(output_dir=args.output_dir)
        visualizer.generate_all_visualizations(results_df, domains)

    if args.all or args.statistics:
        analyzer = StatisticalAnalyzer(alpha=args.alpha)
        analysis = analyzer.comprehensive_domain_analysis(
            results_df, domains, metrics=args.metrics
        )

        output_path = Path(args.output_dir) / "statistical_analysis.json"
        analyzer.export_statistical_report(analysis, filepath=str(output_path))

    print("\n" + "=" * 80)
    print("✅ ANALYSIS COMPLETE")
    print("=" * 80)
    print(f"\nResults saved to: {args.output_dir}/")


if __name__ == "__main__":
    main()
