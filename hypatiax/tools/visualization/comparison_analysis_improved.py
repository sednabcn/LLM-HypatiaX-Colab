#!/usr/bin/env python3
"""
DOMAIN-AWARE COMPARISON ANALYSIS: Pure LLM vs Neural Network
============================================================
Comprehensive comparison analysis for formula discovery across domains.
Integrates with HypatiaX domain-organized results structure.

Directory Structure:
  hypatiax/data/results/
    ├── llm_results/
    │   ├── all_domains/
    │   ├── defi/
    │   ├── lending/
    │   ├── trading/
    │   └── physics/
    ├── nn_results/
    │   ├── all_domains/
    │   ├── defi/
    │   ├── lending/
    │   ├── trading/
    │   └── physics/
    └── llm_nn_comparison/
        ├── all_domains/
        ├── defi/
        ├── lending/
        ├── trading/
        └── physics/

Author: HypatiaX Evaluation Team
Version: 2.0 - Domain-Aware
"""

import json
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
from pathlib import Path
from typing import Dict, List, Optional, Tuple
import pandas as pd
import argparse
import sys
from datetime import datetime

# Set style for better-looking plots
plt.style.use("seaborn-v0_8-darkgrid")
sns.set_palette("husl")

# Configuration
VALID_DOMAINS = ["all_domains", "defi", "lending", "trading", "physics"]
BASE_RESULTS_DIR = "hypatiax/data/results"


# ============================================================================
# UTILITY FUNCTIONS
# ============================================================================


def find_latest_result(
    method: str, domain: str, base_dir: str = BASE_RESULTS_DIR
) -> Optional[Path]:
    """
    Find latest result file for a method and domain

    Args:
        method: 'llm' or 'nn'
        domain: Domain name
        base_dir: Base results directory
    """
    results_dir = Path(base_dir) / f"{method}_results" / domain

    if not results_dir.exists():
        return None

    # Try symlink first
    latest_link = results_dir / f"{method}_results_latest.json"
    if latest_link.exists():
        return latest_link

    # Fallback to newest timestamped file
    result_files = sorted(results_dir.glob(f"{method}_results_*.json"))
    return result_files[-1] if result_files else None


def infer_domain_from_path(filepath: Path) -> str:
    """Infer domain from file path"""
    parts = filepath.parts
    for domain in VALID_DOMAINS:
        if domain in parts:
            return domain
    return "all_domains"


def get_output_dir(domain: str, base_dir: str = BASE_RESULTS_DIR) -> Path:
    """Generate output directory for comparison analysis"""
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    return Path(base_dir) / "llm_nn_comparison" / domain / timestamp


def create_latest_symlink(output_dir: Path):
    """Create 'latest' symlink pointing to this analysis"""
    analysis_base = output_dir.parent
    latest_link = analysis_base / "latest"

    if latest_link.exists() or latest_link.is_symlink():
        latest_link.unlink()

    latest_link.symlink_to(output_dir.name)
    print(f"🔗 Latest comparison: {latest_link}")


# ============================================================================
# DATA LOADING
# ============================================================================


def load_results(llm_file: str, nn_file: str) -> Tuple[List, List]:
    """Load both result files."""
    try:
        with open(llm_file, "r") as f:
            llm_results = json.load(f)
        print(f"✅ Loaded LLM results from: {llm_file}")

        with open(nn_file, "r") as f:
            nn_results = json.load(f)
        print(f"✅ Loaded NN results from: {nn_file}")

        # Handle different JSON structures
        if isinstance(llm_results, dict):
            llm_list = extract_results_from_dict(llm_results)
        else:
            llm_list = llm_results

        if isinstance(nn_results, dict):
            nn_list = extract_results_from_dict(nn_results)
        else:
            nn_list = nn_results

        return llm_list, nn_list

    except FileNotFoundError as e:
        print(f"❌ Error: File not found - {e}")
        raise
    except json.JSONDecodeError as e:
        print(f"❌ Error: Invalid JSON format - {e}")
        raise


def extract_results_from_dict(results_dict: dict) -> List:
    """Extract results list from various dict structures"""
    # Try common keys
    for key in ["results", "test_results", "cases", "experiments"]:
        if key in results_dict:
            return results_dict[key]

    # If dict itself looks like a single result, wrap it
    if "description" in results_dict or "evaluation" in results_dict:
        return [results_dict]

    return []


# ============================================================================
# COMPARISON ANALYSIS
# ============================================================================


def create_comparison_tables(
    llm_results: List, nn_results: List, domain: str
) -> pd.DataFrame:
    """Create comprehensive comparison tables using pandas."""

    if len(llm_results) != len(nn_results):
        print(
            f"⚠️  Warning: Different number of results (LLM: {len(llm_results)}, NN: {len(nn_results)})"
        )

    # Build main comparison dataframe
    data = []
    for i, (llm_r, nn_r) in enumerate(zip(llm_results, nn_results)):
        row = extract_comparison_row(llm_r, nn_r, i)
        data.append(row)

    df = pd.DataFrame(data)

    # Calculate winner
    df["Winner"] = df.apply(determine_winner, axis=1)

    # Calculate R² difference
    df["R² Difference"] = df.apply(calc_r2_diff, axis=1)

    return df


def extract_comparison_row(llm_r: dict, nn_r: dict, index: int) -> dict:
    """Extract comparison data from a single test case pair"""

    # Description
    desc = llm_r.get("description", f"Test case {index + 1}")[:50]

    # Domain
    domain = llm_r.get("domain", llm_r.get("metadata", {}).get("domain", "unknown"))

    # Formula type
    formula_type = llm_r.get("metadata", {}).get(
        "formula_type", llm_r.get("formula_type", "unknown")
    )

    # Evaluation metrics
    llm_eval = llm_r.get("evaluation", {})
    nn_eval = nn_r.get("evaluation", {})

    llm_r2 = llm_eval.get("r2")
    nn_r2 = nn_eval.get("r2")
    llm_rmse = llm_eval.get("rmse")
    nn_rmse = nn_eval.get("rmse")

    # Extrapolation flag
    extrap = llm_r.get("metadata", {}).get(
        "extrapolation_test", llm_r.get("extrapolation_test", False)
    )

    return {
        "Description": desc,
        "Domain": domain,
        "Formula Type": formula_type,
        "LLM R²": llm_r2,
        "NN R²": nn_r2,
        "LLM RMSE": llm_rmse,
        "NN RMSE": nn_rmse,
        "Extrapolation": extrap,
    }


def determine_winner(row) -> str:
    """Determine winner for a test case"""
    llm_r2 = row["LLM R²"]
    nn_r2 = row["NN R²"]

    if llm_r2 is None or nn_r2 is None:
        return "N/A"
    if pd.isna(llm_r2) or pd.isna(nn_r2):
        return "N/A"

    diff = abs(llm_r2 - nn_r2)
    if diff < 0.001:  # Essentially tied
        return "Tie"
    elif llm_r2 > nn_r2:
        return "LLM"
    else:
        return "NN"


def calc_r2_diff(row) -> float:
    """Calculate R² difference (LLM - NN)"""
    llm = row["LLM R²"]
    nn = row["NN R²"]
    if llm is None or nn is None or pd.isna(llm) or pd.isna(nn):
        return np.nan
    return llm - nn


# ============================================================================
# VISUALIZATIONS
# ============================================================================


def plot_overall_comparison(df: pd.DataFrame, domain: str, output_dir: Path):
    """Create overall comparison visualizations."""

    fig, axes = plt.subplots(2, 2, figsize=(16, 12))
    fig.suptitle(
        f"Pure LLM vs Neural Network: {domain.upper()}", fontsize=16, fontweight="bold"
    )

    # 1. R² Distribution comparison
    ax1 = axes[0, 0]
    llm_r2 = df["LLM R²"].dropna()
    nn_r2 = df["NN R²"].dropna()

    if len(llm_r2) > 0:
        ax1.hist(
            llm_r2, bins=20, alpha=0.6, label="LLM", color="blue", edgecolor="black"
        )
        ax1.axvline(
            llm_r2.mean(),
            color="blue",
            linestyle="--",
            linewidth=2,
            label=f"LLM Mean: {llm_r2.mean():.3f}",
        )

    if len(nn_r2) > 0:
        ax1.hist(nn_r2, bins=20, alpha=0.6, label="NN", color="red", edgecolor="black")
        ax1.axvline(
            nn_r2.mean(),
            color="red",
            linestyle="--",
            linewidth=2,
            label=f"NN Mean: {nn_r2.mean():.3f}",
        )

    ax1.set_xlabel("R² Score", fontsize=12)
    ax1.set_ylabel("Frequency", fontsize=12)
    ax1.set_title("R² Distribution", fontsize=14, fontweight="bold")
    ax1.legend()
    ax1.grid(True, alpha=0.3)

    # 2. Head-to-head scatter plot
    ax2 = axes[0, 1]
    valid_data = df.dropna(subset=["LLM R²", "NN R²"])

    if len(valid_data) > 0:
        ax2.scatter(
            valid_data["LLM R²"],
            valid_data["NN R²"],
            alpha=0.6,
            s=100,
            edgecolors="black",
            linewidth=1,
        )

        min_val = min(valid_data["LLM R²"].min(), valid_data["NN R²"].min())
        max_val = max(valid_data["LLM R²"].max(), valid_data["NN R²"].max())
        ax2.plot(
            [min_val, max_val],
            [min_val, max_val],
            "k--",
            alpha=0.5,
            linewidth=2,
            label="Equal Performance",
        )

        ax2.set_xlabel("LLM R²", fontsize=12)
        ax2.set_ylabel("NN R²", fontsize=12)
        ax2.set_title("Head-to-Head R² Comparison", fontsize=14, fontweight="bold")
        ax2.legend()
        ax2.grid(True, alpha=0.3)

    # 3. Win rate pie chart
    ax3 = axes[1, 0]
    winner_counts = df["Winner"].value_counts()
    colors = {"LLM": "blue", "NN": "red", "Tie": "gray", "N/A": "lightgray"}
    pie_colors = [colors.get(w, "gray") for w in winner_counts.index]

    wedges, texts, autotexts = ax3.pie(
        winner_counts.values,
        labels=winner_counts.index,
        autopct="%1.1f%%",
        colors=pie_colors,
        startangle=90,
        textprops={"fontsize": 12, "fontweight": "bold"},
    )
    ax3.set_title("Win Rate Distribution", fontsize=14, fontweight="bold")

    # 4. Performance quality distribution
    ax4 = axes[1, 1]

    llm_excellent = (df["LLM R²"] > 0.95).sum()
    llm_good = ((df["LLM R²"] > 0.80) & (df["LLM R²"] <= 0.95)).sum()
    llm_poor = (df["LLM R²"] <= 0.80).sum()

    nn_excellent = (df["NN R²"] > 0.95).sum()
    nn_good = ((df["NN R²"] > 0.80) & (df["NN R²"] <= 0.95)).sum()
    nn_poor = (df["NN R²"] <= 0.80).sum()

    categories = [
        "Excellent\n(R² > 0.95)",
        "Good\n(0.80 < R² ≤ 0.95)",
        "Poor\n(R² ≤ 0.80)",
    ]
    llm_values = [llm_excellent, llm_good, llm_poor]
    nn_values = [nn_excellent, nn_good, nn_poor]

    x = np.arange(len(categories))
    width = 0.35

    bars1 = ax4.bar(
        x - width / 2,
        llm_values,
        width,
        label="LLM",
        color="blue",
        alpha=0.7,
        edgecolor="black",
    )
    bars2 = ax4.bar(
        x + width / 2,
        nn_values,
        width,
        label="NN",
        color="red",
        alpha=0.7,
        edgecolor="black",
    )

    ax4.set_ylabel("Number of Cases", fontsize=12)
    ax4.set_title("Performance Quality Distribution", fontsize=14, fontweight="bold")
    ax4.set_xticks(x)
    ax4.set_xticklabels(categories)
    ax4.legend()
    ax4.grid(True, alpha=0.3, axis="y")

    # Add value labels
    for bars in [bars1, bars2]:
        for bar in bars:
            height = bar.get_height()
            ax4.text(
                bar.get_x() + bar.get_width() / 2.0,
                height,
                f"{int(height)}",
                ha="center",
                va="bottom",
                fontweight="bold",
            )

    plt.tight_layout()
    filepath = output_dir / "overall_comparison.png"
    plt.savefig(filepath, dpi=300, bbox_inches="tight")
    print(f"✅ Saved: {filepath.name}")
    plt.close()


def plot_extrapolation_analysis(df: pd.DataFrame, domain: str, output_dir: Path):
    """Analyze extrapolation performance."""

    extrap_df = df[df["Extrapolation"] == True].copy()

    if len(extrap_df) == 0:
        print("⚠️  No extrapolation test cases found")
        return

    fig, axes = plt.subplots(1, 2, figsize=(16, 6))
    fig.suptitle(
        f"Extrapolation Analysis - {domain.upper()}", fontsize=16, fontweight="bold"
    )

    # 1. Extrapolation vs non-extrapolation
    ax1 = axes[0]

    non_extrap_df = df[df["Extrapolation"] == False]

    categories = ["Extrapolation\nTests", "Standard\nTests"]
    llm_values = [
        extrap_df["LLM R²"].mean() if len(extrap_df) > 0 else 0,
        non_extrap_df["LLM R²"].mean() if len(non_extrap_df) > 0 else 0,
    ]
    nn_values = [
        extrap_df["NN R²"].mean() if len(extrap_df) > 0 else 0,
        non_extrap_df["NN R²"].mean() if len(non_extrap_df) > 0 else 0,
    ]

    x = np.arange(len(categories))
    width = 0.35

    bars1 = ax1.bar(
        x - width / 2,
        llm_values,
        width,
        label="LLM",
        color="blue",
        alpha=0.7,
        edgecolor="black",
        linewidth=1.5,
    )
    bars2 = ax1.bar(
        x + width / 2,
        nn_values,
        width,
        label="NN",
        color="red",
        alpha=0.7,
        edgecolor="black",
        linewidth=1.5,
    )

    ax1.set_ylabel("Mean R² Score", fontsize=12)
    ax1.set_title(
        "Extrapolation vs Standard Test Performance", fontsize=14, fontweight="bold"
    )
    ax1.set_xticks(x)
    ax1.set_xticklabels(categories)
    ax1.legend()
    ax1.grid(True, alpha=0.3, axis="y")
    ax1.axhline(y=0.95, color="green", linestyle="--", alpha=0.5, linewidth=2)

    # Add value labels
    for bars in [bars1, bars2]:
        for bar in bars:
            height = bar.get_height()
            if height > 0:
                ax1.text(
                    bar.get_x() + bar.get_width() / 2.0,
                    height,
                    f"{height:.3f}",
                    ha="center",
                    va="bottom",
                    fontsize=11,
                    fontweight="bold",
                )

    # 2. Individual extrapolation cases
    ax2 = axes[1]

    if len(extrap_df) > 0:
        case_names = [desc[:25] for desc in extrap_df["Description"]]
        y_pos = np.arange(len(case_names))

        ax2.barh(
            y_pos - 0.2,
            extrap_df["LLM R²"],
            0.4,
            label="LLM",
            color="blue",
            alpha=0.7,
            edgecolor="black",
            linewidth=1.5,
        )
        ax2.barh(
            y_pos + 0.2,
            extrap_df["NN R²"],
            0.4,
            label="NN",
            color="red",
            alpha=0.7,
            edgecolor="black",
            linewidth=1.5,
        )

        ax2.set_yticks(y_pos)
        ax2.set_yticklabels(case_names, fontsize=9)
        ax2.set_xlabel("R² Score", fontsize=12)
        ax2.set_title(
            "Individual Extrapolation Test Cases", fontsize=14, fontweight="bold"
        )
        ax2.legend()
        ax2.grid(True, alpha=0.3, axis="x")
        ax2.axvline(x=0.95, color="green", linestyle="--", alpha=0.5, linewidth=2)

    plt.tight_layout()
    filepath = output_dir / "extrapolation_analysis.png"
    plt.savefig(filepath, dpi=300, bbox_inches="tight")
    print(f"✅ Saved: {filepath.name}")
    plt.close()


# ============================================================================
# SUMMARY REPORTS
# ============================================================================


def create_summary_report(df: pd.DataFrame, domain: str, output_dir: Path):
    """Create comprehensive summary report"""

    report_path = output_dir / "comparison_summary.txt"

    with open(report_path, "w") as f:
        f.write("=" * 100 + "\n")
        f.write(f"LLM VS NN COMPARISON - {domain.upper()}\n")
        f.write("=" * 100 + "\n\n")

        f.write(f"Generated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n\n")

        # Overall statistics
        llm_r2 = df["LLM R²"].dropna()
        nn_r2 = df["NN R²"].dropna()

        f.write("OVERALL PERFORMANCE:\n")
        f.write("-" * 100 + "\n")
        f.write(f"{'Metric':<40} {'LLM':>25} {'NN':>25}\n")
        f.write("-" * 100 + "\n")

        if len(llm_r2) > 0 and len(nn_r2) > 0:
            f.write(f"{'Total Cases':<40} {len(llm_r2):>25} {len(nn_r2):>25}\n")
            f.write(f"{'Mean R²':<40} {llm_r2.mean():>25.4f} {nn_r2.mean():>25.4f}\n")
            f.write(
                f"{'Median R²':<40} {llm_r2.median():>25.4f} {nn_r2.median():>25.4f}\n"
            )
            f.write(f"{'Std Dev R²':<40} {llm_r2.std():>25.4f} {nn_r2.std():>25.4f}\n")
            f.write(f"{'Min R²':<40} {llm_r2.min():>25.4f} {nn_r2.min():>25.4f}\n")
            f.write(f"{'Max R²':<40} {llm_r2.max():>25.4f} {nn_r2.max():>25.4f}\n")
            f.write(
                f"{'Excellent (R² > 0.99)':<40} {(llm_r2 > 0.99).sum():>25} {(nn_r2 > 0.99).sum():>25}\n"
            )
            f.write(
                f"{'Good (R² > 0.95)':<40} {(llm_r2 > 0.95).sum():>25} {(nn_r2 > 0.95).sum():>25}\n"
            )

        # Win rates
        f.write("\nHEAD-TO-HEAD RESULTS:\n")
        f.write("-" * 100 + "\n")
        winner_counts = df["Winner"].value_counts()
        total = len(df)
        f.write(
            f"{'LLM Wins:':<40} {winner_counts.get('LLM', 0)} ({winner_counts.get('LLM', 0) / total * 100:.1f}%)\n"
        )
        f.write(
            f"{'NN Wins:':<40} {winner_counts.get('NN', 0)} ({winner_counts.get('NN', 0) / total * 100:.1f}%)\n"
        )
        f.write(
            f"{'Ties:':<40} {winner_counts.get('Tie', 0)} ({winner_counts.get('Tie', 0) / total * 100:.1f}%)\n"
        )

        # Recommendations
        f.write("\nRECOMMENDATIONS:\n")
        f.write("-" * 100 + "\n")

        if len(llm_r2) > 0 and len(nn_r2) > 0:
            if llm_r2.mean() > nn_r2.mean() + 0.1:
                f.write("✅ PREFER LLM APPROACH for this domain\n")
                f.write(f"   Advantage: +{(llm_r2.mean() - nn_r2.mean()):.4f} R²\n")
            elif nn_r2.mean() > llm_r2.mean() + 0.1:
                f.write("✅ PREFER NN APPROACH for this domain\n")
                f.write(f"   Advantage: +{(nn_r2.mean() - llm_r2.mean()):.4f} R²\n")
            else:
                f.write("⚖️  METHODS ARE COMPARABLE for this domain\n")

    print(f"✅ Saved: {report_path.name}")


# ============================================================================
# MAIN EXECUTION
# ============================================================================


def generate_comparison_report(
    llm_file: str, nn_file: str, domain: str, output_dir: Optional[Path] = None
):
    """Generate comprehensive comparison report"""

    print("=" * 100)
    print(f"LLM vs NN COMPARISON ANALYSIS - {domain.upper()}".center(100))
    print("=" * 100)

    # Load results
    llm_results, nn_results = load_results(llm_file, nn_file)

    # Create output directory
    if output_dir is None:
        output_dir = get_output_dir(domain)
    output_dir.mkdir(parents=True, exist_ok=True)

    print(f"\n📂 Output directory: {output_dir}")

    # Create comparison dataframe
    print("\n📊 Creating comparison tables...")
    df = create_comparison_tables(llm_results, nn_results, domain)

    # Save raw dataframe
    csv_path = output_dir / "detailed_comparison.csv"
    df.to_csv(csv_path, index=False)
    print(f"✅ Saved: {csv_path.name}")

    # Generate visualizations
    print("\n📈 Generating visualizations...")
    plot_overall_comparison(df, domain, output_dir)
    plot_extrapolation_analysis(df, domain, output_dir)

    # Create summary report
    print("\n📝 Creating summary report...")
    create_summary_report(df, domain, output_dir)

    # Create latest symlink
    create_latest_symlink(output_dir)

    # Print console summary
    print_console_summary(df, domain)

    print("\n" + "=" * 100)
    print(f"✅ All results saved to: {output_dir}")
    print("=" * 100)


def print_console_summary(df: pd.DataFrame, domain: str):
    """Print summary to console"""

    print("\n" + "=" * 100)
    print(f"SUMMARY - {domain.upper()}".center(100))
    print("=" * 100)

    llm_r2 = df["LLM R²"].dropna()
    nn_r2 = df["NN R²"].dropna()

    if len(llm_r2) > 0 and len(nn_r2) > 0:
        print(f"\nOverall Performance:")
        print(f"  LLM Mean R²: {llm_r2.mean():.4f} (±{llm_r2.std():.4f})")
        print(f"  NN Mean R²:  {nn_r2.mean():.4f} (±{nn_r2.std():.4f})")
        print(f"  Advantage:   {llm_r2.mean() - nn_r2.mean():+.4f}")

        winner_counts = df["Winner"].value_counts()
        total = len(df)
        print(f"\nWin Rates:")
        print(
            f"  LLM: {winner_counts.get('LLM', 0)}/{total} ({winner_counts.get('LLM', 0) / total * 100:.1f}%)"
        )
        print(
            f"  NN:  {winner_counts.get('NN', 0)}/{total} ({winner_counts.get('NN', 0) / total * 100:.1f}%)"
        )
        print(
            f"  Tie: {winner_counts.get('Tie', 0)}/{total} ({winner_counts.get('Tie', 0) / total * 100:.1f}%)"
        )


# ============================================================================
# CLI INTERFACE
# ============================================================================


def main():
    parser = argparse.ArgumentParser(
        description="Domain-aware LLM vs NN comparison analyzer",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  # Auto-detect latest results for a domain
  python comparison_analysis_improved.py --domain defi
  
  # Specify input files
  python comparison_analysis_improved.py --llm llm_results.json --nn nn_results.json --domain defi
  
  # Compare all domains
  python comparison_analysis_improved.py --all-domains
  
  # Custom output directory
  python comparison_analysis_improved.py --domain lending --output my_comparison
        """,
    )

    parser.add_argument(
        "--domain",
        type=str,
        default="all_domains",
        choices=VALID_DOMAINS,
        help="Domain to analyze",
    )
    parser.add_argument("--llm", type=str, help="Path to LLM results JSON file")
    parser.add_argument("--nn", type=str, help="Path to NN results JSON file")
    parser.add_argument("--output", type=str, help="Custom output directory")
    parser.add_argument(
        "--all-domains", action="store_true", help="Compare all domains sequentially"
    )
    parser.add_argument(
        "--base-dir",
        type=str,
        default=BASE_RESULTS_DIR,
        help=f"Base results directory (default: {BASE_RESULTS_DIR})",
    )

    args = parser.parse_args()

    # Compare all domains
    if args.all_domains:
        print("🔄 Comparing all domains...")
        success_count = 0

        for domain in VALID_DOMAINS:
            llm_file = find_latest_result("llm", domain, args.base_dir)
            nn_file = find_latest_result("nn", domain, args.base_dir)

            if not llm_file or not nn_file:
                print(f"⚠️  Missing results for {domain}, skipping...")
                continue

            print(f"\n{'=' * 100}")
            print(f"Comparing: {domain.upper()}")
            print(f"{'=' * 100}")

            try:
                generate_comparison_report(str(llm_file), str(nn_file), domain)
                success_count += 1
            except Exception as e:
                print(f"❌ Failed to compare {domain}: {e}")
                continue

        print(
            f"\n🎉 Successfully compared {success_count}/{len(VALID_DOMAINS)} domains!"
        )
        return

    # Single domain comparison
    if args.llm and args.nn:
        llm_file = Path(args.llm)
        nn_file = Path(args.nn)
        domain = args.domain
    else:
        # Auto-detect latest results
        llm_file = find_latest_result("llm", args.domain, args.base_dir)
        nn_file = find_latest_result("nn", args.domain, args.base_dir)
        domain = args.domain

    if not llm_file or not llm_file.exists():
        print(f"❌ LLM results not found for domain: {args.domain}")
        print(f"   Looked in: {Path(args.base_dir) / 'llm_results' / args.domain}")
        sys.exit(1)

    if not nn_file or not nn_file.exists():
        print(f"❌ NN results not found for domain: {args.domain}")
        print(f"   Looked in: {Path(args.base_dir) / 'nn_results' / args.domain}")
        sys.exit(1)

    print(f"📂 LLM results: {llm_file}")
    print(f"📂 NN results: {nn_file}")
    print(f"🏷️  Domain: {domain}")

    # Generate output directory
    output_dir = Path(args.output) if args.output else None

    # Run comparison
    try:
        generate_comparison_report(str(llm_file), str(nn_file), domain, output_dir)
        print(f"\n✅ Comparison complete for {domain}!")

    except Exception as e:
        print(f"\n❌ Comparison failed: {str(e)}")
        import traceback

        traceback.print_exc()
        sys.exit(1)


if __name__ == "__main__":
    main()

"""
Perfect! Now let me create a comprehensive guide showing how all three analysis scripts work together:
📊 Complete Analysis Workflow Guide
Three Analysis Scripts Overview
1. analyze_hybrid_results.py
   Purpose: Compare System 1 (Hybrid) vs System 2 (Symbolic+Validation)
   Input: Hybrid system comparison results
   
2. comparison_analysis_improved.py  
   Purpose: Compare Pure LLM vs Pure Neural Network
   Input: LLM and NN baseline results
   
3. (Optional) cross_comparison.py
   Purpose: Compare ALL methods (System1, System2, LLM, NN)
   Input: All result types
Directory Structure
hypatiax/data/results/
├── comparison_results/          # System1 vs System2 (Hybrid comparisons)
│   ├── all_domains/
│   │   ├── comparison_results_20241227_143022.json
│   │   └── comparison_results_latest.json
│   ├── defi/
│   ├── lending/
│   ├── trading/
│   └── physics/
│
├── llm_results/                 # Pure LLM baseline results
│   ├── all_domains/
│   │   ├── llm_results_20241227_143022.json
│   │   └── llm_results_latest.json
│   ├── defi/
│   ├── lending/
│   ├── trading/
│   └── physics/
│
├── nn_results/                  # Pure NN baseline results
│   ├── all_domains/
│   │   ├── nn_results_20241227_143022.json
│   │   └── nn_results_latest.json
│   ├── defi/
│   ├── lending/
│   ├── trading/
│   └── physics/
│
├── analysis_outputs/            # Hybrid comparison analysis
│   ├── all_domains/
│   │   ├── 20241227_143022/
│   │   │   ├── summary_report.txt
│   │   │   ├── *.csv
│   │   │   └── *.png
│   │   └── latest/
│   ├── defi/
│   ├── lending/
│   ├── trading/
│   └── physics/
│
└── llm_nn_comparison/           # LLM vs NN analysis
    ├── all_domains/
    │   ├── 20241227_150000/
    │   │   ├── comparison_summary.txt
    │   │   ├── detailed_comparison.csv
    │   │   └── *.png
    │   └── latest/
    ├── defi/
    ├── lending/
    ├── trading/
    └── physics/
Complete Workflow
bash# ============================================================================
# STEP 1: Run All Experiments
# ============================================================================

# A. Run hybrid system comparison (System 1 vs System 2)
python test_real_hybrid_systems_comparison.py --mode full --split-domains

# B. Run pure LLM baseline
python run_llm_baseline.py --mode full --split-domains

# C. Run pure NN baseline
python run_nn_baseline.py --mode full --split-domains


# ============================================================================
# STEP 2: Analyze Hybrid Systems (System 1 vs System 2)
# ============================================================================

# Analyze all domains
python analyze_hybrid_results.py --all-domains

# Or analyze specific domain
python analyze_hybrid_results.py --domain defi

# Generate cross-domain comparison
python analyze_hybrid_results.py --cross-domain


# ============================================================================
# STEP 3: Analyze LLM vs NN Baselines
# ============================================================================

# Compare all domains
python comparison_analysis_improved.py --all-domains

# Or compare specific domain
python comparison_analysis_improved.py --domain lending

# With specific files
python comparison_analysis_improved.py \
    --llm hypatiax/data/results/llm_results/defi/llm_results_latest.json \
    --nn hypatiax/data/results/nn_results/defi/nn_results_latest.json \
    --domain defi


# ============================================================================
# STEP 4: View Results
# ============================================================================

# View latest hybrid comparison for DeFi
ls hypatiax/data/results/analysis_outputs/defi/latest/

# View latest LLM vs NN comparison for DeFi
ls hypatiax/data/results/llm_nn_comparison/defi/latest/

# Quick summary
cat hypatiax/data/results/analysis_outputs/defi/latest/summary_report.txt
cat hypatiax/data/results/llm_nn_comparison/defi/latest/comparison_summary.txt
Key Differences Between Scripts
Featureanalyze_hybrid_results.pycomparison_analysis_improved.pyPurposeCompare improved hybrid approachesCompare baseline methodsSystem 1Hybrid (LLM+NN+Ensemble)Pure LLMSystem 2Symbolic + ValidationPure NNInputSingle JSON (both systems)Two separate JSON filesFocusDecision logic, validationRaw capability comparisonOutput Diranalysis_outputs/llm_nn_comparison/
Quick Reference Commands
bash# ============== HYBRID ANALYSIS ==============

# Quick analysis of latest results
python analyze_hybrid_results.py --domain defi

# Analyze all domains
python analyze_hybrid_results.py --all-domains

# Cross-domain summary
python analyze_hybrid_results.py --cross-domain


# ============== LLM vs NN ANALYSIS ==============

# Quick comparison of latest results  
python comparison_analysis_improved.py --domain defi

# Compare all domains
python comparison_analysis_improved.py --all-domains

# Custom files
python comparison_analysis_improved.py \
    --llm path/to/llm.json \
    --nn path/to/nn.json \
    --domain trading


# ============== VIEW RESULTS ==============

# Latest hybrid analysis
open hypatiax/data/results/analysis_outputs/defi/latest/r2_distribution_analysis.png

# Latest LLM vs NN
open hypatiax/data/results/llm_nn_comparison/defi/latest/overall_comparison.png

# Compare outputs
diff \
    hypatiax/data/results/analysis_outputs/defi/latest/summary_report.txt \
    hypatiax/data/results/llm_nn_comparison/defi/latest/comparison_summary.txt
This gives you a complete, domain-organized analysis pipeline! 🎯
"""
