#!/usr/bin/env python3
"""
Hybrid System Comparison - Visualization & Statistical Testing
===============================================================
Provides comprehensive visualization and statistical analysis for
comparing hybrid discovery architectures.

Features:
  - Comparative visualizations (bar charts, radar plots, heatmaps)
  - Statistical significance testing (t-tests, Wilcoxon, effect sizes)
  - Performance profiling
  - Publication-ready figures

Author: HypatiaX Team
Version: 1.0
"""

import json
from pathlib import Path
from typing import Dict, List, Optional, Tuple

import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
import seaborn as sns
from scipy import stats


# Set publication-quality style
plt.style.use("seaborn-v0_8-darkgrid")
sns.set_palette("husl")


# ============================================================================
# VISUALIZATION FUNCTIONS
# ============================================================================


class ComparisonVisualizer:
    """Generate publication-quality comparison visualizations"""

    def __init__(self, output_dir: str = "figures"):
        self.output_dir = Path(output_dir)
        self.output_dir.mkdir(exist_ok=True)
        print(f"📊 Visualizer initialized - saving to: {self.output_dir}")

    def plot_architecture_comparison(
        self,
        results_df: pd.DataFrame,
        metrics: List[str] = None,
        save: bool = True,
    ) -> plt.Figure:
        """
        Create bar chart comparing architectures across metrics.

        Args:
            results_df: DataFrame with results
            metrics: List of metrics to compare (default: key metrics)
            save: Whether to save figure

        Returns:
            matplotlib Figure object
        """
        if metrics is None:
            metrics = [
                "r2_score",
                "validation_score",
                "discovery_time",
                "edge_cases_detected",
                "critical_errors",
            ]

        # Aggregate by architecture
        agg_data = results_df.groupby("architecture").agg(
            {
                "r2_score": "mean",
                "validation_score": "mean",
                "discovery_time": "mean",
                "edge_cases_detected": "mean",
                "critical_errors": "mean",
            }
        )

        # Create subplots
        n_metrics = len(metrics)
        fig, axes = plt.subplots(1, n_metrics, figsize=(5 * n_metrics, 5))

        if n_metrics == 1:
            axes = [axes]

        for ax, metric in zip(axes, metrics):
            if metric not in agg_data.columns:
                ax.text(0.5, 0.5, f"{metric}\nN/A", ha="center", va="center")
                ax.set_xticks([])
                ax.set_yticks([])
                continue

            data = agg_data[metric]

            # Bar chart
            bars = ax.bar(range(len(data)), data.values, color=["#3498db", "#e74c3c"])

            # Labels
            ax.set_xticks(range(len(data)))
            ax.set_xticklabels(["LLM+NN", "LLM+Symbolic+Val"], rotation=45, ha="right")
            ax.set_ylabel(metric.replace("_", " ").title())
            ax.set_title(f"{metric.replace('_', ' ').title()}\n(Mean)")

            # Add value labels on bars
            for i, bar in enumerate(bars):
                height = bar.get_height()
                ax.text(
                    bar.get_x() + bar.get_width() / 2.0,
                    height,
                    f"{height:.3f}",
                    ha="center",
                    va="bottom",
                    fontsize=10,
                )

            # Grid
            ax.grid(axis="y", alpha=0.3)

        plt.tight_layout()

        if save:
            filepath = self.output_dir / "architecture_comparison.png"
            plt.savefig(filepath, dpi=300, bbox_inches="tight")
            print(f"✅ Saved: {filepath}")

        return fig

    def plot_validation_radar(
        self,
        results_df: pd.DataFrame,
        test_case: Optional[str] = None,
        save: bool = True,
    ) -> plt.Figure:
        """
        Create radar plot showing validation layer scores.

        Args:
            results_df: DataFrame with results
            test_case: Specific test case to plot (None for average)
            save: Whether to save figure

        Returns:
            matplotlib Figure object
        """
        # Filter to Architecture B only (has validation scores)
        arch_b = results_df[results_df["architecture"] == "llm_symbolic_validation"]

        if len(arch_b) == 0:
            print("⚠️  No Architecture B results found for radar plot")
            return None

        # Define layer metrics
        layers = [
            "symbolic_score",
            "dimensional_score",
            "domain_score",
            "numerical_score",
        ]
        layer_labels = ["Symbolic", "Dimensional", "Domain", "Numerical"]

        # Get data
        if test_case:
            data = arch_b[arch_b["test_case"] == test_case][layers].iloc[0]
        else:
            data = arch_b[layers].mean()

        # Radar plot setup
        angles = np.linspace(0, 2 * np.pi, len(layers), endpoint=False).tolist()
        values = data.values.tolist()

        # Close the plot
        angles += angles[:1]
        values += values[:1]

        # Create figure
        fig, ax = plt.subplots(figsize=(8, 8), subplot_kw=dict(projection="polar"))

        # Plot
        ax.plot(angles, values, "o-", linewidth=2, label="Architecture B")
        ax.fill(angles, values, alpha=0.25)

        # Set labels
        ax.set_xticks(angles[:-1])
        ax.set_xticklabels(layer_labels)
        ax.set_ylim(0, 100)
        ax.set_yticks([20, 40, 60, 80, 100])
        ax.set_yticklabels(["20", "40", "60", "80", "100"])
        ax.grid(True)

        # Title
        title = "Validation Layer Scores"
        if test_case:
            title += f"\n{test_case}"
        else:
            title += "\n(Average across all tests)"
        ax.set_title(title, size=14, pad=20)

        # Add threshold line
        threshold = [85] * len(angles)
        ax.plot(angles, threshold, "r--", linewidth=1, label="Threshold (85)")
        ax.legend(loc="upper right", bbox_to_anchor=(1.3, 1.1))

        if save:
            filepath = (
                self.output_dir
                / f"validation_radar{'_' + test_case if test_case else ''}.png"
            )
            plt.savefig(filepath, dpi=300, bbox_inches="tight")
            print(f"✅ Saved: {filepath}")

        return fig

    def plot_performance_heatmap(
        self,
        results_df: pd.DataFrame,
        save: bool = True,
    ) -> plt.Figure:
        """
        Create heatmap showing performance across test cases and architectures.

        Args:
            results_df: DataFrame with results
            save: Whether to save figure

        Returns:
            matplotlib Figure object
        """
        # Pivot table: test_case x architecture for key metrics
        metrics_to_plot = ["r2_score", "validation_score", "production_ready"]

        fig, axes = plt.subplots(1, 3, figsize=(18, 6))

        for ax, metric in zip(axes, metrics_to_plot):
            if metric == "production_ready":
                # Convert boolean to int
                data = results_df.copy()
                data["production_ready"] = data["production_ready"].astype(int)
                pivot = data.pivot_table(
                    values=metric,
                    index="test_case",
                    columns="architecture",
                    aggfunc="sum",
                )
            else:
                pivot = results_df.pivot_table(
                    values=metric,
                    index="test_case",
                    columns="architecture",
                    aggfunc="mean",
                )

            # Handle missing columns
            if "llm_nn" not in pivot.columns:
                pivot["llm_nn"] = np.nan
            if "llm_symbolic_validation" not in pivot.columns:
                pivot["llm_symbolic_validation"] = np.nan

            # Rename columns for readability
            pivot.columns = ["LLM+NN", "LLM+Symbolic+Val"]

            # Heatmap
            sns.heatmap(
                pivot,
                annot=True,
                fmt=".2f" if metric != "production_ready" else ".0f",
                cmap="RdYlGn",
                center=0.85
                if metric == "r2_score"
                else (85 if metric == "validation_score" else 0.5),
                ax=ax,
                cbar_kws={"label": metric.replace("_", " ").title()},
            )

            ax.set_title(f"{metric.replace('_', ' ').title()}")
            ax.set_xlabel("Architecture")
            ax.set_ylabel("Test Case")

        plt.tight_layout()

        if save:
            filepath = self.output_dir / "performance_heatmap.png"
            plt.savefig(filepath, dpi=300, bbox_inches="tight")
            print(f"✅ Saved: {filepath}")

        return fig

    def plot_error_distribution(
        self,
        results_df: pd.DataFrame,
        save: bool = True,
    ) -> plt.Figure:
        """
        Plot distribution of errors and warnings across architectures.

        Args:
            results_df: DataFrame with results
            save: Whether to save figure

        Returns:
            matplotlib Figure object
        """
        fig, axes = plt.subplots(1, 2, figsize=(14, 6))

        # Filter to Architecture B (only one with error tracking)
        arch_b = results_df[results_df["architecture"] == "llm_symbolic_validation"]

        if len(arch_b) == 0:
            print("⚠️  No error data available for Architecture B")
            return None

        # Critical errors
        ax = axes[0]
        test_cases = arch_b["test_case"].values
        critical = arch_b["critical_errors"].fillna(0).values

        bars = ax.barh(range(len(test_cases)), critical, color="#e74c3c")
        ax.set_yticks(range(len(test_cases)))
        ax.set_yticklabels(test_cases)
        ax.set_xlabel("Number of Critical Errors")
        ax.set_title("Critical Errors by Test Case\n(Architecture B)")
        ax.grid(axis="x", alpha=0.3)

        # Add value labels
        for i, bar in enumerate(bars):
            width = bar.get_width()
            if width > 0:
                ax.text(
                    width,
                    bar.get_y() + bar.get_height() / 2,
                    f"{int(width)}",
                    ha="left",
                    va="center",
                    fontsize=9,
                )

        # Warnings
        ax = axes[1]
        warnings = arch_b["warnings"].fillna(0).values

        bars = ax.barh(range(len(test_cases)), warnings, color="#f39c12")
        ax.set_yticks(range(len(test_cases)))
        ax.set_yticklabels(test_cases)
        ax.set_xlabel("Number of Warnings")
        ax.set_title("Warnings by Test Case\n(Architecture B)")
        ax.grid(axis="x", alpha=0.3)

        # Add value labels
        for i, bar in enumerate(bars):
            width = bar.get_width()
            if width > 0:
                ax.text(
                    width,
                    bar.get_y() + bar.get_height() / 2,
                    f"{int(width)}",
                    ha="left",
                    va="center",
                    fontsize=9,
                )

        plt.tight_layout()

        if save:
            filepath = self.output_dir / "error_distribution.png"
            plt.savefig(filepath, dpi=300, bbox_inches="tight")
            print(f"✅ Saved: {filepath}")

        return fig

    def plot_time_efficiency(
        self,
        results_df: pd.DataFrame,
        save: bool = True,
    ) -> plt.Figure:
        """
        Compare discovery time efficiency between architectures.

        Args:
            results_df: DataFrame with results
            save: Whether to save figure

        Returns:
            matplotlib Figure object
        """
        fig, ax = plt.subplots(figsize=(10, 6))

        # Group by architecture and test case
        grouped = (
            results_df.groupby(["architecture", "test_case"])["discovery_time"]
            .mean()
            .reset_index()
        )

        # Pivot for easier plotting
        pivot = grouped.pivot(
            index="test_case", columns="architecture", values="discovery_time"
        )

        # Handle missing columns
        if "llm_nn" not in pivot.columns:
            pivot["llm_nn"] = 0
        if "llm_symbolic_validation" not in pivot.columns:
            pivot["llm_symbolic_validation"] = 0

        # Plot grouped bars
        x = np.arange(len(pivot.index))
        width = 0.35

        bars1 = ax.bar(
            x - width / 2, pivot["llm_nn"], width, label="LLM+NN", color="#3498db"
        )
        bars2 = ax.bar(
            x + width / 2,
            pivot["llm_symbolic_validation"],
            width,
            label="LLM+Symbolic+Val",
            color="#e74c3c",
        )

        ax.set_xlabel("Test Case")
        ax.set_ylabel("Discovery Time (seconds)")
        ax.set_title("Discovery Time Comparison by Test Case")
        ax.set_xticks(x)
        ax.set_xticklabels(pivot.index, rotation=45, ha="right")
        ax.legend()
        ax.grid(axis="y", alpha=0.3)

        # Add value labels
        def add_labels(bars):
            for bar in bars:
                height = bar.get_height()
                if height > 0:
                    ax.text(
                        bar.get_x() + bar.get_width() / 2.0,
                        height,
                        f"{height:.2f}s",
                        ha="center",
                        va="bottom",
                        fontsize=8,
                    )

        add_labels(bars1)
        add_labels(bars2)

        plt.tight_layout()

        if save:
            filepath = self.output_dir / "time_efficiency.png"
            plt.savefig(filepath, dpi=300, bbox_inches="tight")
            print(f"✅ Saved: {filepath}")

        return fig

    def generate_all_visualizations(self, results_df: pd.DataFrame) -> None:
        """Generate all standard visualizations."""
        print("\n" + "=" * 80)
        print("GENERATING ALL VISUALIZATIONS")
        print("=" * 80 + "\n")

        self.plot_architecture_comparison(results_df)
        self.plot_validation_radar(results_df)
        self.plot_performance_heatmap(results_df)
        self.plot_error_distribution(results_df)
        self.plot_time_efficiency(results_df)

        print(f"\n✅ All visualizations saved to: {self.output_dir}")


# ============================================================================
# STATISTICAL TESTING
# ============================================================================


class StatisticalAnalyzer:
    """Perform statistical significance testing on comparison results"""

    def __init__(self, alpha: float = 0.05):
        """
        Initialize statistical analyzer.

        Args:
            alpha: Significance level (default: 0.05 for 95% confidence)
        """
        self.alpha = alpha
        print(f"📊 Statistical Analyzer initialized (α={alpha})")

    def paired_t_test(
        self,
        results_df: pd.DataFrame,
        metric: str = "r2_score",
    ) -> Dict:
        """
        Perform paired t-test comparing architectures.

        Args:
            results_df: DataFrame with results from both architectures
            metric: Metric to compare

        Returns:
            Dictionary with test results
        """
        # Get paired samples (same test case)
        arch_a = results_df[results_df["architecture"] == "llm_nn"].set_index(
            "test_case"
        )[metric]
        arch_b = results_df[
            results_df["architecture"] == "llm_symbolic_validation"
        ].set_index("test_case")[metric]

        # Align on test cases
        common_tests = arch_a.index.intersection(arch_b.index)

        if len(common_tests) < 2:
            return {
                "test": "paired_t_test",
                "metric": metric,
                "error": "Insufficient paired samples",
                "n_pairs": len(common_tests),
            }

        a_values = arch_a.loc[common_tests].values
        b_values = arch_b.loc[common_tests].values

        # Remove NaN values
        mask = ~(np.isnan(a_values) | np.isnan(b_values))
        a_values = a_values[mask]
        b_values = b_values[mask]

        # Perform paired t-test
        statistic, pvalue = stats.ttest_rel(a_values, b_values)

        # Effect size (Cohen's d)
        diff = a_values - b_values
        cohen_d = np.mean(diff) / np.std(diff, ddof=1)

        # Interpret
        significant = pvalue < self.alpha

        if significant:
            if np.mean(a_values) > np.mean(b_values):
                winner = "Architecture A (LLM+NN)"
            else:
                winner = "Architecture B (LLM+Symbolic+Val)"
        else:
            winner = "No significant difference"

        return {
            "test": "paired_t_test",
            "metric": metric,
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

    def wilcoxon_signed_rank_test(
        self,
        results_df: pd.DataFrame,
        metric: str = "r2_score",
    ) -> Dict:
        """
        Perform Wilcoxon signed-rank test (non-parametric alternative to t-test).

        Args:
            results_df: DataFrame with results
            metric: Metric to compare

        Returns:
            Dictionary with test results
        """
        # Get paired samples
        arch_a = results_df[results_df["architecture"] == "llm_nn"].set_index(
            "test_case"
        )[metric]
        arch_b = results_df[
            results_df["architecture"] == "llm_symbolic_validation"
        ].set_index("test_case")[metric]

        common_tests = arch_a.index.intersection(arch_b.index)

        if len(common_tests) < 2:
            return {
                "test": "wilcoxon_signed_rank",
                "metric": metric,
                "error": "Insufficient paired samples",
            }

        a_values = arch_a.loc[common_tests].values
        b_values = arch_b.loc[common_tests].values

        # Remove NaN values
        mask = ~(np.isnan(a_values) | np.isnan(b_values))
        a_values = a_values[mask]
        b_values = b_values[mask]

        # Perform test
        statistic, pvalue = stats.wilcoxon(a_values, b_values)

        significant = pvalue < self.alpha

        if significant:
            if np.median(a_values) > np.median(b_values):
                winner = "Architecture A (LLM+NN)"
            else:
                winner = "Architecture B (LLM+Symbolic+Val)"
        else:
            winner = "No significant difference"

        return {
            "test": "wilcoxon_signed_rank",
            "metric": metric,
            "n_pairs": len(a_values),
            "median_a": float(np.median(a_values)),
            "median_b": float(np.median(b_values)),
            "statistic": float(statistic),
            "p_value": float(pvalue),
            "significant": significant,
            "alpha": self.alpha,
            "winner": winner,
        }

    def mann_whitney_u_test(
        self,
        results_df: pd.DataFrame,
        metric: str = "r2_score",
    ) -> Dict:
        """
        Perform Mann-Whitney U test (independent samples).

        Args:
            results_df: DataFrame with results
            metric: Metric to compare

        Returns:
            Dictionary with test results
        """
        arch_a = (
            results_df[results_df["architecture"] == "llm_nn"][metric].dropna().values
        )
        arch_b = (
            results_df[results_df["architecture"] == "llm_symbolic_validation"][metric]
            .dropna()
            .values
        )

        if len(arch_a) < 2 or len(arch_b) < 2:
            return {
                "test": "mann_whitney_u",
                "metric": metric,
                "error": "Insufficient samples",
            }

        statistic, pvalue = stats.mannwhitneyu(arch_a, arch_b, alternative="two-sided")

        significant = pvalue < self.alpha

        if significant:
            if np.median(arch_a) > np.median(arch_b):
                winner = "Architecture A (LLM+NN)"
            else:
                winner = "Architecture B (LLM+Symbolic+Val)"
        else:
            winner = "No significant difference"

        return {
            "test": "mann_whitney_u",
            "metric": metric,
            "n_a": len(arch_a),
            "n_b": len(arch_b),
            "median_a": float(np.median(arch_a)),
            "median_b": float(np.median(arch_b)),
            "statistic": float(statistic),
            "p_value": float(pvalue),
            "significant": significant,
            "alpha": self.alpha,
            "winner": winner,
        }

    def effect_size_analysis(
        self,
        results_df: pd.DataFrame,
        metrics: List[str] = None,
    ) -> pd.DataFrame:
        """
        Calculate effect sizes for multiple metrics.

        Args:
            results_df: DataFrame with results
            metrics: List of metrics to analyze

        Returns:
            DataFrame with effect size analysis
        """
        if metrics is None:
            metrics = ["r2_score", "rmse", "discovery_time", "validation_score"]

        effect_sizes = []

        for metric in metrics:
            arch_a = (
                results_df[results_df["architecture"] == "llm_nn"][metric]
                .dropna()
                .values
            )
            arch_b = (
                results_df[results_df["architecture"] == "llm_symbolic_validation"][
                    metric
                ]
                .dropna()
                .values
            )

            if len(arch_a) == 0 or len(arch_b) == 0:
                continue

            # Cohen's d
            mean_diff = np.mean(arch_b) - np.mean(arch_a)
            pooled_std = np.sqrt((np.var(arch_a, ddof=1) + np.var(arch_b, ddof=1)) / 2)
            cohen_d = mean_diff / pooled_std if pooled_std > 0 else 0

            effect_sizes.append(
                {
                    "metric": metric,
                    "mean_a": np.mean(arch_a),
                    "mean_b": np.mean(arch_b),
                    "difference": mean_diff,
                    "cohen_d": cohen_d,
                    "effect_size": self._interpret_effect_size(cohen_d),
                }
            )

        return pd.DataFrame(effect_sizes)

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

    def comprehensive_analysis(
        self,
        results_df: pd.DataFrame,
        metrics: List[str] = None,
    ) -> Dict:
        """
        Perform comprehensive statistical analysis.

        Args:
            results_df: DataFrame with results
            metrics: List of metrics to analyze

        Returns:
            Dictionary with all test results
        """
        if metrics is None:
            metrics = ["r2_score", "validation_score", "discovery_time"]

        print("\n" + "=" * 80)
        print("COMPREHENSIVE STATISTICAL ANALYSIS")
        print("=" * 80 + "\n")

        analysis = {
            "paired_t_tests": {},
            "wilcoxon_tests": {},
            "mann_whitney_tests": {},
            "effect_sizes": None,
        }

        for metric in metrics:
            print(f"\nAnalyzing: {metric}")
            print("-" * 40)

            # Paired t-test
            t_result = self.paired_t_test(results_df, metric)
            analysis["paired_t_tests"][metric] = t_result

            if "error" not in t_result:
                print(f"Paired t-test:")
                print(f"  Mean A: {t_result['mean_a']:.4f}")
                print(f"  Mean B: {t_result['mean_b']:.4f}")
                print(f"  p-value: {t_result['p_value']:.4f}")
                print(f"  Significant: {'Yes' if t_result['significant'] else 'No'}")
                print(
                    f"  Effect size: {t_result['effect_size']} (d={t_result['cohen_d']:.3f})"
                )
                print(f"  Winner: {t_result['winner']}")

            # Wilcoxon
            w_result = self.wilcoxon_signed_rank_test(results_df, metric)
            analysis["wilcoxon_tests"][metric] = w_result

            if "error" not in w_result:
                print(f"\nWilcoxon signed-rank test:")
                print(f"  Median A: {w_result['median_a']:.4f}")
                print(f"  Median B: {w_result['median_b']:.4f}")
                print(f"  p-value: {w_result['p_value']:.4f}")
                print(f"  Significant: {'Yes' if w_result['significant'] else 'No'}")

            # Mann-Whitney
            mw_result = self.mann_whitney_u_test(results_df, metric)
            analysis["mann_whitney_tests"][metric] = mw_result

        # Effect sizes
        print(f"\n{'=' * 80}")
        print("EFFECT SIZE ANALYSIS")
        print("=" * 80)
        effect_df = self.effect_size_analysis(results_df, metrics)
        analysis["effect_sizes"] = effect_df.to_dict("records")
        print(effect_df.to_string(index=False))

        return analysis

    def export_statistical_report(
        self,
        analysis: Dict,
        filepath: str = "statistical_analysis.json",
    ) -> None:
        """Export statistical analysis to JSON."""
        with open(filepath, "w") as f:
            json.dump(analysis, f, indent=2, default=str)
        print(f"\n✅ Statistical analysis exported to: {filepath}")


# ============================================================================
# CLI INTERFACE
# ============================================================================


def main():
    import argparse

    parser = argparse.ArgumentParser(
        description="Visualization & Statistical Testing for Hybrid System Comparison"
    )

    parser.add_argument(
        "--input",
        type=str,
        required=True,
        help="Path to comparison results JSON or CSV",
    )
    parser.add_argument(
        "--output-dir", type=str, default="figures", help="Output directory for figures"
    )
    parser.add_argument(
        "--alpha",
        type=float,
        default=0.05,
        help="Significance level for statistical tests",
    )
    parser.add_argument(
        "--metrics",
        nargs="+",
        default=["r2_score", "validation_score", "discovery_time"],
        help="Metrics to analyze",
    )
    parser.add_argument(
        "--visualize", action="store_true", help="Generate visualizations"
    )
    parser.add_argument(
        "--statistics", action="store_true", help="Perform statistical tests"
    )
    parser.add_argument(
        "--all",
        action="store_true",
        help="Generate all visualizations and perform all tests",
    )

    args = parser.parse_args()

    # Load data
    print(f"📂 Loading data from: {args.input}")

    if args.input.endswith(".json"):
        with open(args.input, "r") as f:
            data = json.load(f)

        # Convert to DataFrame
        if isinstance(data, dict) and "results" in data:
            results_df = pd.DataFrame(data["results"])
        elif isinstance(data, list):
            results_df = pd.DataFrame(data)
        else:
            results_df = pd.DataFrame([data])

    elif args.input.endswith(".csv"):
        results_df = pd.read_csv(args.input)

    else:
        raise ValueError(f"Unsupported file format: {args.input}")

    print(f"✅ Loaded {len(results_df)} results")
    print(f"   Architectures: {results_df['architecture'].unique().tolist()}")
    print(f"   Test cases: {results_df['test_case'].nunique()}")

    # Perform requested operations
    if args.all or args.visualize:
        visualizer = ComparisonVisualizer(output_dir=args.output_dir)
        visualizer.generate_all_visualizations(results_df)

    if args.all or args.statistics:
        analyzer = StatisticalAnalyzer(alpha=args.alpha)
        analysis = analyzer.comprehensive_analysis(results_df, metrics=args.metrics)

        # Export results
        output_path = Path(args.output_dir) / "statistical_analysis.json"
        analyzer.export_statistical_report(analysis, filepath=str(output_path))

    print("\n" + "=" * 80)
    print("✅ ANALYSIS COMPLETE")
    print("=" * 80)
    print(f"\nResults saved to: {args.output_dir}/")


if __name__ == "__main__":
    main()

"""
The script can now be run from the command line with various options:

--input to specify the data file
--output-dir for where to save results
--visualize for generating plots
--statistics for statistical tests
--all for comprehensive analysis
"""
