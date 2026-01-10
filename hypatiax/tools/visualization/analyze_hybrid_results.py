#!/usr/bin/env python3
"""
DOMAIN-AWARE HYBRID SYSTEMS ANALYZER
====================================
Comprehensive analysis tool for domain-organized comparison results.

Features:
  - Domain-specific analysis (defi, lending, trading, physics)
  - Cross-domain comparison
  - Publication-quality visualizations
  - Statistical tables and reports
  - Auto-detection of latest results per domain

Directory Structure:
  hypatiax/data/results/
    ├── comparison_results/
    │   ├── all_domains/
    │   ├── defi/
    │   ├── lending/
    │   ├── trading/
    │   └── physics/
    └── analysis_outputs/
        ├── all_domains/
        ├── defi/
        ├── lending/
        ├── trading/
        └── physics/

Author: HypatiaX Evaluation Team
Version: 2.0 - Domain-Aware Production
"""

import json
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
from pathlib import Path
from typing import Dict, List, Optional, Tuple
from datetime import datetime
import sys
import argparse

# Configure plotting style
plt.style.use("seaborn-v0_8-darkgrid")
sns.set_palette("husl")
plt.rcParams["figure.figsize"] = (12, 8)
plt.rcParams["font.size"] = 10


# ============================================================================
# DOMAIN CONFIGURATION
# ============================================================================

VALID_DOMAINS = ["all_domains", "defi", "lending", "trading", "physics"]
BASE_RESULTS_DIR = "hypatiax/data/results"


# ============================================================================
# UTILITY FUNCTIONS
# ============================================================================


def find_latest_result(domain: str, base_dir: str = BASE_RESULTS_DIR) -> Optional[Path]:
    """Find latest result file for a domain"""
    results_dir = Path(base_dir) / "comparison_results" / domain

    if not results_dir.exists():
        return None

    # Try symlink first
    latest_link = results_dir / "comparison_results_latest.json"
    if latest_link.exists():
        return latest_link

    # Fallback to newest timestamped file
    result_files = sorted(results_dir.glob("comparison_results_*.json"))
    return result_files[-1] if result_files else None


def get_output_dir(
    input_file: Path, domain: str, base_dir: str = BASE_RESULTS_DIR
) -> Path:
    """Generate output directory for analysis based on input file timestamp"""
    # Extract timestamp from input filename
    if "latest" in input_file.name:
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    else:
        # Extract: comparison_results_20241227_143022.json -> 20241227_143022
        parts = input_file.stem.split("_")
        if len(parts) >= 3:
            timestamp = f"{parts[-2]}_{parts[-1]}"
        else:
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")

    return Path(base_dir) / "analysis_outputs" / domain / timestamp


def create_latest_symlink(output_dir: Path):
    """Create 'latest' symlink pointing to this analysis"""
    analysis_base = output_dir.parent  # e.g., analysis_outputs/defi/
    latest_link = analysis_base / "latest"

    if latest_link.exists() or latest_link.is_symlink():
        latest_link.unlink()

    # Create relative symlink
    latest_link.symlink_to(output_dir.name)
    print(f"🔗 Latest analysis: {latest_link}")


def infer_domain_from_path(filepath: Path) -> str:
    """Infer domain from file path"""
    parts = filepath.parts
    for domain in VALID_DOMAINS:
        if domain in parts:
            return domain
    return "all_domains"


# ============================================================================
# MAIN ANALYZER CLASS
# ============================================================================


class RealHybridSystemAnalyzer:
    """
    Analyze real execution results from hybrid system comparisons.
    Domain-aware version with enhanced organization.
    """

    def __init__(self, results_file: str, domain: str = "all_domains"):
        """
        Load results from JSON file

        Args:
            results_file: Path to comparison results JSON
            domain: Domain name for context (used in titles/reports)
        """
        self.results_file = Path(results_file)
        self.domain = domain

        print(f"📂 Loading results from: {results_file}")
        print(f"🏷️  Domain: {domain}")

        with open(results_file, "r") as f:
            self.raw_data = json.load(f)

        # Convert to DataFrames
        self.df_system1 = self._process_system_results("system1")
        self.df_system2 = self._process_system_results("system2")
        self.df_combined = self._create_combined_df()

        print(f"✅ Loaded {len(self.df_system1)} System 1 results")
        print(f"✅ Loaded {len(self.df_system2)} System 2 results")

    def _process_system_results(self, system: str) -> pd.DataFrame:
        """Convert system results to DataFrame"""
        results = self.raw_data.get(system, [])

        processed = []
        for r in results:
            if not r.get("success", False):
                continue

            row = {
                "system": system,
                "test": r.get("description", "Unknown")[:40],
                "domain": r.get("domain", "unknown"),
                "r2": r.get("r2", -999),
                "rmse": r.get("rmse", 999),
                "runtime": r.get("runtime_seconds", 0),
                "extrapolation": r.get("is_extrapolation", False),
            }

            # System-specific fields
            if system == "system1":
                row["decision"] = r.get("decision", "unknown")
                row["llm_r2"] = r.get("llm_r2", 0)
                row["nn_r2"] = r.get("nn_r2", 0)
                row["has_validation"] = False
                row["validation_score"] = 0
            else:  # system2
                row["decision"] = "symbolic"
                row["validation_score"] = r.get("validation_score", 0)
                row["has_validation"] = r.get("has_validation", True)
                row["validation_valid"] = r.get("validation_valid", False)

            processed.append(row)

        return pd.DataFrame(processed)

    def _create_combined_df(self) -> pd.DataFrame:
        """Create combined DataFrame for side-by-side comparison"""
        combined = []

        for _, row1 in self.df_system1.iterrows():
            test_name = row1["test"]
            domain = row1["domain"]

            # Find matching test in system2
            row2 = self.df_system2[
                (self.df_system2["test"] == test_name)
                & (self.df_system2["domain"] == domain)
            ]

            if not row2.empty:
                row2 = row2.iloc[0]
                combined.append(
                    {
                        "test": test_name,
                        "domain": domain,
                        "extrapolation": row1["extrapolation"],
                        "s1_r2": row1["r2"],
                        "s2_r2": row2["r2"],
                        "s1_rmse": row1["rmse"],
                        "s2_rmse": row2["rmse"],
                        "s1_runtime": row1["runtime"],
                        "s2_runtime": row2["runtime"],
                        "s1_decision": row1["decision"],
                        "s2_validation": row2["validation_score"],
                        "s2_valid": row2.get("validation_valid", False),
                        "winner_r2": "s1" if row1["r2"] > row2["r2"] else "s2",
                        "r2_diff": abs(row1["r2"] - row2["r2"]),
                    }
                )

        return pd.DataFrame(combined)

    # ========================================================================
    # STATISTICAL TABLES
    # ========================================================================

    def print_summary_statistics(self):
        """Print comprehensive summary statistics"""
        print("\n" + "=" * 80)
        title = f"SUMMARY STATISTICS - {self.domain.upper()}"
        print(title.center(80))
        print("=" * 80)

        print("\n📊 OVERALL PERFORMANCE")
        print("-" * 80)

        # System 1 stats
        if len(self.df_system1) > 0:
            s1_stats = self.df_system1["r2"].describe()
            print(f"\nSystem 1 (Improved Hybrid):")
            print(f"  Tests:      {len(self.df_system1)}")
            print(f"  Mean R²:    {s1_stats['mean']:.6f}")
            print(f"  Median R²:  {s1_stats['50%']:.6f}")
            print(f"  Std Dev:    {s1_stats['std']:.6f}")
            print(f"  Min R²:     {s1_stats['min']:.6f}")
            print(f"  Max R²:     {s1_stats['max']:.6f}")
        else:
            print("\nSystem 1: No results")

        # System 2 stats
        if len(self.df_system2) > 0:
            s2_stats = self.df_system2["r2"].describe()
            print(f"\nSystem 2 (Symbolic + Validation):")
            print(f"  Tests:      {len(self.df_system2)}")
            print(f"  Mean R²:    {s2_stats['mean']:.6f}")
            print(f"  Median R²:  {s2_stats['50%']:.6f}")
            print(f"  Std Dev:    {s2_stats['std']:.6f}")
            print(f"  Min R²:     {s2_stats['min']:.6f}")
            print(f"  Max R²:     {s2_stats['max']:.6f}")
        else:
            print("\nSystem 2: No results")

        # Runtime comparison
        if len(self.df_system1) > 0 and len(self.df_system2) > 0:
            print("\n⏱️  RUNTIME COMPARISON")
            print("-" * 80)
            print(f"System 1 Mean Runtime: {self.df_system1['runtime'].mean():.2f}s")
            print(f"System 2 Mean Runtime: {self.df_system2['runtime'].mean():.2f}s")
            speedup = (
                self.df_system2["runtime"].mean() / self.df_system1["runtime"].mean()
            )
            print(f"Speedup Factor: {speedup:.2f}x")

        # Head-to-head
        if len(self.df_combined) > 0:
            print("\n🎯 HEAD-TO-HEAD COMPARISON")
            print("-" * 80)
            s1_wins = (self.df_combined["winner_r2"] == "s1").sum()
            s2_wins = (self.df_combined["winner_r2"] == "s2").sum()
            total = len(self.df_combined)

            print(f"System 1 Wins: {s1_wins}/{total} ({s1_wins / total * 100:.1f}%)")
            print(f"System 2 Wins: {s2_wins}/{total} ({s2_wins / total * 100:.1f}%)")

    def create_domain_comparison_table(self) -> Optional[pd.DataFrame]:
        """Create domain-wise comparison table (only for all_domains)"""
        if self.domain != "all_domains" or len(self.df_combined) == 0:
            return None

        print("\n📋 DOMAIN-WISE PERFORMANCE")
        print("-" * 80)

        domain_stats = []

        for domain in self.df_combined["domain"].unique():
            domain_data = self.df_combined[self.df_combined["domain"] == domain]

            s1_wins = (domain_data["winner_r2"] == "s1").sum()
            s2_wins = (domain_data["winner_r2"] == "s2").sum()

            domain_stats.append(
                {
                    "Domain": domain.upper(),
                    "Tests": len(domain_data),
                    "S1 Mean R²": domain_data["s1_r2"].mean(),
                    "S2 Mean R²": domain_data["s2_r2"].mean(),
                    "S1 Wins": s1_wins,
                    "S2 Wins": s2_wins,
                    "S1 Win %": (s1_wins / len(domain_data) * 100),
                }
            )

        df_domain = pd.DataFrame(domain_stats)
        print(df_domain.to_string(index=False))

        return df_domain

    def create_extrapolation_table(self) -> Optional[pd.DataFrame]:
        """Create extrapolation performance table"""
        if len(self.df_combined) == 0:
            return None

        print("\n🔴 EXTRAPOLATION PERFORMANCE")
        print("-" * 80)

        extrap_data = self.df_combined[self.df_combined["extrapolation"]]
        interp_data = self.df_combined[~self.df_combined["extrapolation"]]

        if len(extrap_data) == 0:
            print("No extrapolation tests in this domain.")
            return None

        comparison = pd.DataFrame(
            {
                "Test Type": ["Interpolation", "Extrapolation"],
                "Count": [len(interp_data), len(extrap_data)],
                "S1 Mean R²": [
                    interp_data["s1_r2"].mean() if len(interp_data) > 0 else 0,
                    extrap_data["s1_r2"].mean(),
                ],
                "S2 Mean R²": [
                    interp_data["s2_r2"].mean() if len(interp_data) > 0 else 0,
                    extrap_data["s2_r2"].mean(),
                ],
                "S1 Drop": [
                    0,
                    (interp_data["s1_r2"].mean() - extrap_data["s1_r2"].mean())
                    if len(interp_data) > 0
                    else 0,
                ],
                "S2 Drop": [
                    0,
                    (interp_data["s2_r2"].mean() - extrap_data["s2_r2"].mean())
                    if len(interp_data) > 0
                    else 0,
                ],
            }
        )

        print(comparison.to_string(index=False))

        return comparison

    def create_decision_breakdown_table(self) -> Optional[pd.DataFrame]:
        """Create System 1 decision breakdown table"""
        if len(self.df_system1) == 0:
            return None

        print("\n🎯 SYSTEM 1 DECISION BREAKDOWN")
        print("-" * 80)

        decision_stats = []

        for decision in self.df_system1["decision"].unique():
            decision_data = self.df_system1[self.df_system1["decision"] == decision]

            decision_stats.append(
                {
                    "Decision": decision.upper(),
                    "Count": len(decision_data),
                    "Percentage": len(decision_data) / len(self.df_system1) * 100,
                    "Mean R²": decision_data["r2"].mean(),
                    "Median R²": decision_data["r2"].median(),
                    "Success Rate (R²>0.95)": (decision_data["r2"] > 0.95).mean() * 100,
                }
            )

        df_decision = pd.DataFrame(decision_stats)
        print(df_decision.to_string(index=False))

        return df_decision

    # ========================================================================
    # VISUALIZATIONS
    # ========================================================================

    def plot_r2_distribution(self, output_dir: Path):
        """Plot R² score distributions"""
        if len(self.df_system1) == 0 and len(self.df_system2) == 0:
            return

        fig, axes = plt.subplots(2, 2, figsize=(15, 12))
        fig.suptitle(f"R² Score Analysis - {self.domain.upper()}", fontsize=16)

        # 1. Histogram comparison
        ax = axes[0, 0]
        if len(self.df_system1) > 0:
            ax.hist(
                self.df_system1["r2"],
                bins=30,
                alpha=0.6,
                label="System 1",
                color="blue",
            )
        if len(self.df_system2) > 0:
            ax.hist(
                self.df_system2["r2"],
                bins=30,
                alpha=0.6,
                label="System 2",
                color="orange",
            )
        ax.set_xlabel("R² Score")
        ax.set_ylabel("Frequency")
        ax.set_title("R² Score Distribution")
        ax.legend()
        ax.grid(True, alpha=0.3)

        # 2. Box plot comparison
        ax = axes[0, 1]
        data_to_plot = []
        labels = []
        if len(self.df_system1) > 0:
            data_to_plot.append(self.df_system1["r2"])
            labels.append("System 1")
        if len(self.df_system2) > 0:
            data_to_plot.append(self.df_system2["r2"])
            labels.append("System 2")

        if data_to_plot:
            box = ax.boxplot(data_to_plot, labels=labels, patch_artist=True)
            for i, patch in enumerate(box["boxes"]):
                patch.set_facecolor(["lightblue", "lightsalmon"][i])
        ax.set_ylabel("R² Score")
        ax.set_title("R² Score Box Plot Comparison")
        ax.grid(True, alpha=0.3)

        # 3. Scatter plot (head-to-head)
        ax = axes[1, 0]
        if len(self.df_combined) > 0:
            ax.scatter(
                self.df_combined["s1_r2"],
                self.df_combined["s2_r2"],
                alpha=0.6,
                s=100,
                c="purple",
            )
            ax.plot([0, 1], [0, 1], "r--", label="y=x (tie line)")
            ax.set_xlabel("System 1 R²")
            ax.set_ylabel("System 2 R²")
            ax.set_title("Head-to-Head R² Comparison")
            ax.legend()
            ax.grid(True, alpha=0.3)
        else:
            ax.text(
                0.5,
                0.5,
                "No paired comparisons",
                ha="center",
                va="center",
                transform=ax.transAxes,
            )

        # 4. Violin plot
        ax = axes[1, 1]
        if len(self.df_system1) > 0 or len(self.df_system2) > 0:
            combined_data = []
            if len(self.df_system1) > 0:
                combined_data.append(self.df_system1[["r2"]].assign(system="System 1"))
            if len(self.df_system2) > 0:
                combined_data.append(self.df_system2[["r2"]].assign(system="System 2"))

            if combined_data:
                combined_df = pd.concat(combined_data)
                sns.violinplot(data=combined_df, x="system", y="r2", ax=ax)
                ax.set_title("R² Score Violin Plot")
                ax.set_ylabel("R² Score")
                ax.grid(True, alpha=0.3)

        plt.tight_layout()
        filepath = output_dir / "r2_distribution_analysis.png"
        plt.savefig(filepath, dpi=300, bbox_inches="tight")
        print(f"✅ Saved: {filepath.name}")
        plt.close()

    def plot_domain_performance(self, output_dir: Path):
        """Plot performance by domain (only for all_domains)"""
        if self.domain != "all_domains" or len(self.df_combined) == 0:
            return

        fig, axes = plt.subplots(2, 1, figsize=(15, 10))
        fig.suptitle("Performance Across Domains", fontsize=16)

        # 1. Mean R² by domain
        ax = axes[0]
        domain_means = self.df_combined.groupby("domain")[["s1_r2", "s2_r2"]].mean()
        x = np.arange(len(domain_means))
        width = 0.35

        ax.bar(
            x - width / 2,
            domain_means["s1_r2"],
            width,
            label="System 1",
            color="skyblue",
        )
        ax.bar(
            x + width / 2,
            domain_means["s2_r2"],
            width,
            label="System 2",
            color="salmon",
        )
        ax.set_xlabel("Domain")
        ax.set_ylabel("Mean R² Score")
        ax.set_title("Mean R² Score by Domain")
        ax.set_xticks(x)
        ax.set_xticklabels(domain_means.index, rotation=45)
        ax.legend()
        ax.grid(True, alpha=0.3, axis="y")

        # 2. Win rate by domain
        ax = axes[1]
        win_rates = []
        domains = []

        for domain in self.df_combined["domain"].unique():
            domain_data = self.df_combined[self.df_combined["domain"] == domain]
            s1_wins = (domain_data["winner_r2"] == "s1").sum()
            win_rate = s1_wins / len(domain_data) * 100
            win_rates.append(win_rate)
            domains.append(domain)

        colors = ["green" if wr > 50 else "red" for wr in win_rates]
        ax.barh(domains, win_rates, color=colors, alpha=0.7)
        ax.axvline(50, color="black", linestyle="--", label="50% (tie)")
        ax.set_xlabel("System 1 Win Rate (%)")
        ax.set_title("System 1 Win Rate by Domain")
        ax.legend()
        ax.grid(True, alpha=0.3, axis="x")

        plt.tight_layout()
        filepath = output_dir / "domain_performance.png"
        plt.savefig(filepath, dpi=300, bbox_inches="tight")
        print(f"✅ Saved: {filepath.name}")
        plt.close()

    def plot_extrapolation_analysis(self, output_dir: Path):
        """Plot extrapolation vs interpolation performance"""
        if len(self.df_combined) == 0:
            return

        extrap_data = self.df_combined[self.df_combined["extrapolation"]]
        interp_data = self.df_combined[~self.df_combined["extrapolation"]]

        if len(extrap_data) == 0:
            print("⚠️  No extrapolation tests, skipping extrapolation plot")
            return

        fig, axes = plt.subplots(2, 2, figsize=(15, 12))
        fig.suptitle(f"Extrapolation Analysis - {self.domain.upper()}", fontsize=16)

        # 1. R² comparison - System 1
        ax = axes[0, 0]
        data_to_plot = []
        labels = []
        if len(interp_data) > 0:
            data_to_plot.append(interp_data["s1_r2"])
            labels.append("Interpolation")
        if len(extrap_data) > 0:
            data_to_plot.append(extrap_data["s1_r2"])
            labels.append("Extrapolation")

        if data_to_plot:
            ax.boxplot(data_to_plot, labels=labels, patch_artist=True)
        ax.set_ylabel("R² Score")
        ax.set_title("System 1: Interpolation vs Extrapolation")
        ax.grid(True, alpha=0.3)

        # 2. R² comparison - System 2
        ax = axes[0, 1]
        data_to_plot = []
        labels = []
        if len(interp_data) > 0:
            data_to_plot.append(interp_data["s2_r2"])
            labels.append("Interpolation")
        if len(extrap_data) > 0:
            data_to_plot.append(extrap_data["s2_r2"])
            labels.append("Extrapolation")

        if data_to_plot:
            ax.boxplot(data_to_plot, labels=labels, patch_artist=True)
        ax.set_ylabel("R² Score")
        ax.set_title("System 2: Interpolation vs Extrapolation")
        ax.grid(True, alpha=0.3)

        # 3. Performance drop comparison
        ax = axes[1, 0]
        if len(interp_data) > 0 and len(extrap_data) > 0:
            s1_drop = interp_data["s1_r2"].mean() - extrap_data["s1_r2"].mean()
            s2_drop = interp_data["s2_r2"].mean() - extrap_data["s2_r2"].mean()

            ax.bar(
                ["System 1", "System 2"],
                [s1_drop, s2_drop],
                color=["blue", "orange"],
                alpha=0.7,
            )
            ax.set_ylabel("R² Drop (Interpolation - Extrapolation)")
            ax.set_title("Extrapolation Performance Drop")
            ax.grid(True, alpha=0.3, axis="y")

        # 4. Scatter: extrapolation performance comparison
        ax = axes[1, 1]
        if len(extrap_data) > 0:
            ax.scatter(
                extrap_data["s1_r2"], extrap_data["s2_r2"], s=100, alpha=0.6, c="red"
            )
            ax.plot([0, 1], [0, 1], "k--", label="y=x")
            ax.set_xlabel("System 1 R² (Extrapolation)")
            ax.set_ylabel("System 2 R² (Extrapolation)")
            ax.set_title("Extrapolation: Head-to-Head")
            ax.legend()
            ax.grid(True, alpha=0.3)

        plt.tight_layout()
        filepath = output_dir / "extrapolation_analysis.png"
        plt.savefig(filepath, dpi=300, bbox_inches="tight")
        print(f"✅ Saved: {filepath.name}")
        plt.close()

    def plot_runtime_comparison(self, output_dir: Path):
        """Plot runtime comparison"""
        if len(self.df_system1) == 0 and len(self.df_system2) == 0:
            return

        fig, axes = plt.subplots(2, 2, figsize=(15, 12))
        fig.suptitle(f"Runtime Analysis - {self.domain.upper()}", fontsize=16)

        # 1. Runtime distribution
        ax = axes[0, 0]
        if len(self.df_system1) > 0:
            ax.hist(
                self.df_system1["runtime"],
                bins=20,
                alpha=0.6,
                label="System 1",
                color="blue",
            )
        if len(self.df_system2) > 0:
            ax.hist(
                self.df_system2["runtime"],
                bins=20,
                alpha=0.6,
                label="System 2",
                color="orange",
            )
        ax.set_xlabel("Runtime (seconds)")
        ax.set_ylabel("Frequency")
        ax.set_title("Runtime Distribution")
        ax.legend()
        ax.grid(True, alpha=0.3)

        # 2. Runtime box plot
        ax = axes[0, 1]
        data_to_plot = []
        labels = []
        if len(self.df_system1) > 0:
            data_to_plot.append(self.df_system1["runtime"])
            labels.append("System 1")
        if len(self.df_system2) > 0:
            data_to_plot.append(self.df_system2["runtime"])
            labels.append("System 2")

        if data_to_plot:
            box = ax.boxplot(data_to_plot, labels=labels, patch_artist=True)
            for i, patch in enumerate(box["boxes"]):
                patch.set_facecolor(["lightblue", "lightsalmon"][i])
        ax.set_ylabel("Runtime (seconds)")
        ax.set_title("Runtime Box Plot Comparison")
        ax.grid(True, alpha=0.3)

        # 3. Runtime vs R² - System 1
        ax = axes[1, 0]
        if len(self.df_system1) > 0:
            ax.scatter(
                self.df_system1["runtime"],
                self.df_system1["r2"],
                alpha=0.6,
                s=100,
                c="blue",
            )
            ax.set_xlabel("Runtime (seconds)")
            ax.set_ylabel("R² Score")
            ax.set_title("System 1: Runtime vs R²")
            ax.grid(True, alpha=0.3)

        # 4. Runtime vs R² - System 2
        ax = axes[1, 1]
        if len(self.df_system2) > 0:
            ax.scatter(
                self.df_system2["runtime"],
                self.df_system2["r2"],
                alpha=0.6,
                s=100,
                c="orange",
            )
            ax.set_xlabel("Runtime (seconds)")
            ax.set_ylabel("R² Score")
            ax.set_title("System 2: Runtime vs R²")
            ax.grid(True, alpha=0.3)

        plt.tight_layout()
        filepath = output_dir / "runtime_comparison.png"
        plt.savefig(filepath, dpi=300, bbox_inches="tight")
        print(f"✅ Saved: {filepath.name}")
        plt.close()

    def plot_validation_analysis(self, output_dir: Path):
        """Plot System 2 validation analysis"""
        if (
            "validation_score" not in self.df_system2.columns
            or len(self.df_system2) == 0
        ):
            return

        fig, axes = plt.subplots(2, 2, figsize=(15, 12))
        fig.suptitle(f"Validation Analysis - {self.domain.upper()}", fontsize=16)

        # 1. Validation score distribution
        ax = axes[0, 0]
        ax.hist(self.df_system2["validation_score"], bins=20, color="green", alpha=0.7)
        ax.axvline(85, color="red", linestyle="--", label="Threshold (85)")
        ax.set_xlabel("Validation Score")
        ax.set_ylabel("Frequency")
        ax.set_title("System 2: Validation Score Distribution")
        ax.legend()
        ax.grid(True, alpha=0.3)

        # 2. Validation score vs R²
        ax = axes[0, 1]
        ax.scatter(
            self.df_system2["validation_score"],
            self.df_system2["r2"],
            s=100,
            alpha=0.6,
            c="purple",
        )
        ax.set_xlabel("Validation Score")
        ax.set_ylabel("R² Score")
        ax.set_title("Validation Score vs R² Performance")
        ax.grid(True, alpha=0.3)

        # 3. Pass/Fail breakdown
        ax = axes[1, 0]
        passed = (self.df_system2["validation_score"] >= 85).sum()
        failed = (self.df_system2["validation_score"] < 85).sum()

        if passed + failed > 0:
            ax.pie(
                [passed, failed],
                labels=["Pass (≥85)", "Fail (<85)"],
                autopct="%1.1f%%",
                colors=["lightgreen", "lightcoral"],
                startangle=90,
            )
            ax.set_title("System 2: Validation Pass Rate")

        # 4. R² by validation status
        ax = axes[1, 1]
        passed_data = self.df_system2[self.df_system2["validation_score"] >= 85]
        failed_data = self.df_system2[self.df_system2["validation_score"] < 85]

        if len(passed_data) > 0 and len(failed_data) > 0:
            ax.boxplot(
                [passed_data["r2"], failed_data["r2"]],
                labels=["Passed", "Failed"],
                patch_artist=True,
            )
            ax.set_ylabel("R² Score")
            ax.set_title("R² by Validation Status")
            ax.grid(True, alpha=0.3)

        plt.tight_layout()
        filepath = output_dir / "validation_analysis.png"
        plt.savefig(filepath, dpi=300, bbox_inches="tight")
        print(f"✅ Saved: {filepath.name}")
        plt.close()

    def plot_decision_breakdown(self, output_dir: Path):
        """Plot System 1 decision breakdown"""
        if len(self.df_system1) == 0:
            return

        fig, axes = plt.subplots(2, 2, figsize=(15, 12))
        fig.suptitle(f"Decision Analysis - {self.domain.upper()}", fontsize=16)

        # 1. Decision distribution (pie chart)
        ax = axes[0, 0]
        decision_counts = self.df_system1["decision"].value_counts()
        ax.pie(
            decision_counts.values,
            labels=decision_counts.index,
            autopct="%1.1f%%",
            startangle=90,
        )
        ax.set_title("System 1: Decision Distribution")

        # 2. R² by decision type
        ax = axes[0, 1]
        decisions = self.df_system1["decision"].unique()
        r2_by_decision = [
            self.df_system1[self.df_system1["decision"] == d]["r2"].values
            for d in decisions
        ]
        if r2_by_decision:
            ax.boxplot(r2_by_decision, labels=decisions, patch_artist=True)
            ax.set_ylabel("R² Score")
            ax.set_title("R² Score by Decision Type")
            ax.grid(True, alpha=0.3)

        # 3. Decision frequency by domain (only for all_domains)
        ax = axes[1, 0]
        if self.domain == "all_domains" and len(self.df_system1["domain"].unique()) > 1:
            decision_domain = pd.crosstab(
                self.df_system1["domain"], self.df_system1["decision"]
            )
            decision_domain.plot(kind="bar", stacked=True, ax=ax)
            ax.set_xlabel("Domain")
            ax.set_ylabel("Count")
            ax.set_title("Decision Types by Domain")
            ax.legend(title="Decision")
            plt.setp(ax.xaxis.get_majorticklabels(), rotation=45)
        else:
            decision_counts = self.df_system1["decision"].value_counts()
            ax.bar(
                decision_counts.index,
                decision_counts.values,
                color=["skyblue", "lightcoral", "lightgreen"],
            )
            ax.set_ylabel("Count")
            ax.set_title("Decision Frequency")
            ax.grid(True, alpha=0.3, axis="y")

        # 4. Success rate by decision
        ax = axes[1, 1]
        success_rates = []
        labels = []
        for decision in decisions:
            decision_data = self.df_system1[self.df_system1["decision"] == decision]
            success_rate = (decision_data["r2"] > 0.95).mean() * 100
            success_rates.append(success_rate)
            labels.append(decision)

        colors = ["skyblue"] * len(labels)
        ax.bar(labels, success_rates, color=colors, alpha=0.7)
        ax.set_ylabel("Success Rate (%)")
        ax.set_title("Success Rate (R²>0.95) by Decision")
        ax.grid(True, alpha=0.3, axis="y")

        plt.tight_layout()
        filepath = output_dir / "decision_breakdown.png"
        plt.savefig(filepath, dpi=300, bbox_inches="tight")
        print(f"✅ Saved: {filepath.name}")
        plt.close()

    # ========================================================================
    # COMPREHENSIVE ANALYSIS
    # ========================================================================

    def generate_full_analysis(self, output_dir: str):
        """Generate complete analysis with all tables and plots"""
        output_path = Path(output_dir)
        output_path.mkdir(parents=True, exist_ok=True)

        print("\n" + "=" * 80)
        print(f"COMPREHENSIVE ANALYSIS - {self.domain.upper()}".center(80))
        print("=" * 80)

        # Generate tables
        self.print_summary_statistics()
        domain_table = self.create_domain_comparison_table()
        extrap_table = self.create_extrapolation_table()
        decision_table = self.create_decision_breakdown_table()

        # Export tables to CSV
        if domain_table is not None:
            domain_table.to_csv(output_path / "domain_comparison.csv", index=False)
        if extrap_table is not None:
            extrap_table.to_csv(
                output_path / "extrapolation_comparison.csv", index=False
            )
        if decision_table is not None:
            decision_table.to_csv(output_path / "decision_breakdown.csv", index=False)

        print(f"\n✅ Tables exported to {output_path}")

        # Generate all plots
        print("\n📊 Generating visualizations...")
        self.plot_r2_distribution(output_path)
        self.plot_domain_performance(output_path)
        self.plot_extrapolation_analysis(output_path)
        self.plot_runtime_comparison(output_path)
        self.plot_validation_analysis(output_path)
        self.plot_decision_breakdown(output_path)

        print("\n" + "=" * 80)
        print(f"✅ ANALYSIS COMPLETE - Results saved to: {output_path.absolute()}")
        print("=" * 80)

        # Generate summary report
        self._generate_summary_report(output_path)

    def _generate_summary_report(self, output_dir: Path):
        """Generate text summary report"""
        report_path = output_dir / "summary_report.txt"

        with open(report_path, "w") as f:
            f.write("=" * 80 + "\n")
            f.write(f"HYBRID SYSTEMS COMPARISON - {self.domain.upper()}\n")
            f.write("=" * 80 + "\n\n")

            f.write(f"Generated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")
            f.write(f"Results File: {self.results_file}\n\n")

            # Overall stats
            f.write("OVERALL PERFORMANCE:\n")
            f.write("-" * 80 + "\n")

            if len(self.df_system1) > 0:
                f.write(f"System 1 Tests: {len(self.df_system1)}\n")
                f.write(f"System 1 Mean R²: {self.df_system1['r2'].mean():.6f}\n")
                f.write(
                    f"System 1 Mean Runtime: {self.df_system1['runtime'].mean():.2f}s\n\n"
                )

            if len(self.df_system2) > 0:
                f.write(f"System 2 Tests: {len(self.df_system2)}\n")
                f.write(f"System 2 Mean R²: {self.df_system2['r2'].mean():.6f}\n")
                f.write(
                    f"System 2 Mean Runtime: {self.df_system2['runtime'].mean():.2f}s\n\n"
                )

            # Head-to-head
            if len(self.df_combined) > 0:
                s1_wins = (self.df_combined["winner_r2"] == "s1").sum()
                s2_wins = (self.df_combined["winner_r2"] == "s2").sum()
                total = len(self.df_combined)

                f.write("HEAD-TO-HEAD:\n")
                f.write("-" * 80 + "\n")
                f.write(
                    f"System 1 Wins: {s1_wins}/{total} ({s1_wins / total * 100:.1f}%)\n"
                )
                f.write(
                    f"System 2 Wins: {s2_wins}/{total} ({s2_wins / total * 100:.1f}%)\n\n"
                )

            # Extrapolation
            extrap_data = (
                self.df_combined[self.df_combined["extrapolation"]]
                if len(self.df_combined) > 0
                else pd.DataFrame()
            )
            if len(extrap_data) > 0:
                f.write("EXTRAPOLATION PERFORMANCE:\n")
                f.write("-" * 80 + "\n")
                f.write(f"System 1: {extrap_data['s1_r2'].mean():.6f}\n")
                f.write(f"System 2: {extrap_data['s2_r2'].mean():.6f}\n\n")

            # Recommendations
            f.write("RECOMMENDATIONS:\n")
            f.write("-" * 80 + "\n")

            if len(self.df_system1) > 0 and len(self.df_system2) > 0:
                if self.df_system1["r2"].mean() > self.df_system2["r2"].mean():
                    f.write(
                        "✅ System 1 (Improved Hybrid) shows better overall performance\n"
                    )
                else:
                    f.write(
                        "✅ System 2 (Symbolic + Validation) shows better overall performance\n"
                    )

                if len(extrap_data) > 0:
                    if extrap_data["s1_r2"].mean() > extrap_data["s2_r2"].mean():
                        f.write("✅ System 1 excels at extrapolation tasks\n")
                    else:
                        f.write("✅ System 2 excels at extrapolation tasks\n")

                if (
                    self.df_system1["runtime"].mean()
                    < self.df_system2["runtime"].mean()
                ):
                    f.write("✅ System 1 is faster (lower runtime)\n")
                else:
                    f.write("✅ System 2 is faster (lower runtime)\n")

        print(f"✅ Summary report: {report_path.name}")


# ============================================================================
# CROSS-DOMAIN COMPARISON
# ============================================================================


def compare_all_domains(base_dir: str = BASE_RESULTS_DIR):
    """Generate cross-domain comparison analysis"""
    print("\n" + "=" * 80)
    print("CROSS-DOMAIN PERFORMANCE COMPARISON")
    print("=" * 80)

    comparison_data = []

    for domain in VALID_DOMAINS:
        if domain == "all_domains":
            continue

        latest_file = find_latest_result(domain, base_dir)
        if not latest_file or not latest_file.exists():
            print(f"⚠️  No results for {domain}")
            continue

        with open(latest_file) as f:
            data = json.load(f)

        s1_r2 = [r["r2"] for r in data.get("system1", []) if r.get("success")]
        s2_r2 = [r["r2"] for r in data.get("system2", []) if r.get("success")]

        if s1_r2 or s2_r2:
            comparison_data.append(
                {
                    "Domain": domain.upper(),
                    "S1 Tests": len(s1_r2),
                    "S2 Tests": len(s2_r2),
                    "S1 Mean R²": sum(s1_r2) / len(s1_r2) if s1_r2 else 0,
                    "S2 Mean R²": sum(s2_r2) / len(s2_r2) if s2_r2 else 0,
                    "Winner": "S1"
                    if (sum(s1_r2) / len(s1_r2) if s1_r2 else 0)
                    > (sum(s2_r2) / len(s2_r2) if s2_r2 else 0)
                    else "S2",
                }
            )

    if not comparison_data:
        print("❌ No domain results found for comparison")
        return

    df = pd.DataFrame(comparison_data)

    # Print table
    print("\n" + df.to_string(index=False))

    # Save CSV
    output_dir = Path(base_dir) / "analysis_outputs"
    output_dir.mkdir(parents=True, exist_ok=True)
    csv_path = output_dir / "cross_domain_comparison.csv"
    df.to_csv(csv_path, index=False)
    print(f"\n✅ Saved: {csv_path}")

    # Generate plot
    fig, axes = plt.subplots(2, 1, figsize=(12, 10))
    fig.suptitle("Cross-Domain Performance Comparison", fontsize=16)

    # 1. Bar chart comparison
    ax = axes[0]
    x = range(len(df))
    width = 0.35

    ax.bar(
        [i - width / 2 for i in x],
        df["S1 Mean R²"],
        width,
        label="System 1",
        color="skyblue",
    )
    ax.bar(
        [i + width / 2 for i in x],
        df["S2 Mean R²"],
        width,
        label="System 2",
        color="salmon",
    )

    ax.set_xlabel("Domain")
    ax.set_ylabel("Mean R² Score")
    ax.set_title("Mean R² Score by Domain")
    ax.set_xticks(x)
    ax.set_xticklabels(df["Domain"], rotation=45)
    ax.legend()
    ax.grid(True, alpha=0.3, axis="y")

    # 2. Winner distribution
    ax = axes[1]
    winner_counts = df["Winner"].value_counts()
    colors = ["skyblue" if w == "S1" else "salmon" for w in winner_counts.index]
    ax.bar(winner_counts.index, winner_counts.values, color=colors, alpha=0.7)
    ax.set_ylabel("Number of Domains Won")
    ax.set_title("Domain Wins by System")
    ax.grid(True, alpha=0.3, axis="y")

    plt.tight_layout()
    plot_path = output_dir / "cross_domain_comparison.png"
    plt.savefig(plot_path, dpi=300, bbox_inches="tight")
    print(f"✅ Saved: {plot_path}")
    plt.close()


# ============================================================================
# CLI INTERFACE
# ============================================================================


def main():
    parser = argparse.ArgumentParser(
        description="Domain-aware hybrid system comparison analyzer",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  # Analyze latest all_domains results
  python analyze_hybrid_results.py
  
  # Analyze specific domain
  python analyze_hybrid_results.py --domain defi
  
  # Analyze all domains sequentially
  python analyze_hybrid_results.py --all-domains
  
  # Cross-domain comparison
  python analyze_hybrid_results.py --cross-domain
  
  # Specific input file
  python analyze_hybrid_results.py --input hypatiax/data/results/comparison_results/defi/comparison_results_20241227_143022.json
  
  # Custom output directory
  python analyze_hybrid_results.py --domain lending --output my_analysis
        """,
    )

    parser.add_argument(
        "--domain",
        type=str,
        default="all_domains",
        choices=VALID_DOMAINS,
        help="Domain to analyze (default: all_domains)",
    )
    parser.add_argument(
        "--input", type=str, help="Path to specific comparison results JSON file"
    )
    parser.add_argument(
        "--output", type=str, help="Custom output directory (overrides auto-generation)"
    )
    parser.add_argument(
        "--all-domains", action="store_true", help="Analyze all domains sequentially"
    )
    parser.add_argument(
        "--cross-domain",
        action="store_true",
        help="Generate cross-domain comparison only",
    )
    parser.add_argument(
        "--base-dir",
        type=str,
        default=BASE_RESULTS_DIR,
        help=f"Base results directory (default: {BASE_RESULTS_DIR})",
    )

    args = parser.parse_args()

    # Cross-domain comparison only
    if args.cross_domain:
        compare_all_domains(args.base_dir)
        return

    # Analyze all domains
    if args.all_domains:
        print("🔄 Analyzing all domains...")
        success_count = 0

        for domain in VALID_DOMAINS:
            input_file = find_latest_result(domain, args.base_dir)
            if not input_file:
                print(f"⚠️  No results found for {domain}, skipping...")
                continue

            print(f"\n{'=' * 80}")
            print(f"Analyzing: {domain.upper()}")
            print(f"{'=' * 80}")

            output_dir = get_output_dir(input_file, domain, args.base_dir)

            try:
                analyzer = RealHybridSystemAnalyzer(str(input_file), domain)
                analyzer.generate_full_analysis(output_dir=str(output_dir))
                create_latest_symlink(output_dir)
                success_count += 1
            except Exception as e:
                print(f"❌ Failed to analyze {domain}: {e}")
                continue

        print(
            f"\n🎉 Successfully analyzed {success_count}/{len(VALID_DOMAINS)} domains!"
        )

        # Also generate cross-domain comparison
        if success_count > 1:
            print("\n" + "=" * 80)
            print("Generating cross-domain comparison...")
            compare_all_domains(args.base_dir)

        return

    # Single domain analysis
    if args.input:
        input_file = Path(args.input)
        domain = (
            infer_domain_from_path(input_file)
            if args.domain == "all_domains"
            else args.domain
        )
    else:
        input_file = find_latest_result(args.domain, args.base_dir)
        domain = args.domain

    if not input_file or not input_file.exists():
        print(f"❌ No results found for domain: {args.domain}")
        print(
            f"   Looked in: {Path(args.base_dir) / 'comparison_results' / args.domain}"
        )
        sys.exit(1)

    print(f"📂 Input: {input_file}")
    print(f"🏷️  Domain: {domain}")

    # Generate output directory
    if args.output:
        output_dir = Path(args.output)
    else:
        output_dir = get_output_dir(input_file, domain, args.base_dir)

    # Run analysis
    try:
        analyzer = RealHybridSystemAnalyzer(str(input_file), domain)
        analyzer.generate_full_analysis(output_dir=str(output_dir))
        create_latest_symlink(output_dir)

        print(f"\n✅ Analysis complete for {domain}!")
        print(f"📊 Results: {output_dir}")

    except Exception as e:
        print(f"\n❌ Analysis failed: {str(e)}")
        import traceback

        traceback.print_exc()
        sys.exit(1)


if __name__ == "__main__":
    main()

"""
# 1. Run comparison (generates timestamped results)
python test_real_hybrid_systems_comparison.py --mode quick

# 2. Analyze latest results (auto-detects and organizes)
python analyze_hybrid_results.py --auto
# Output: hypatiax/data/results/analysis_outputs/20241227_143022/

# 3. Use 'latest' symlink (always points to most recent)
python analyze_hybrid_results.py
# Uses: hypatiax/data/results/comparison_results/comparison_results_latest.json

# 4. Analyze specific run
python analyze_hybrid_results.py \
    --input hypatiax/data/results/comparison_results/comparison_results_20241227_143022.json

# 5. Custom output location
python analyze_hybrid_results.py --auto --output custom_analysis
```

## 📝 .gitignore Updates

Add to your `.gitignore`:
```
# Results and analysis outputs
hypatiax/data/results/comparison_results/*.json
hypatiax/data/results/analysis_outputs/*/
hypatiax/data/results/archived/

# Keep directory structure
!hypatiax/data/results/.gitkeep
!hypatiax/data/results/comparison_results/.gitkeep
!hypatiax/data/results/analysis_outputs/.gitkeep

# Allow example/template files
hypatiax/data/results/comparison_results/example_results.json
"""
