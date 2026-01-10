import glob
import json
import os

import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
import seaborn as sns
from scipy import stats


def load_all_results():
    """Load all formula results from data directory."""
    all_files = glob.glob("data/*.json")
    all_results = []

    print(f"Found {len(all_files)} data files:")
    for filepath in all_files:
        print(f"  - {filepath}")
        try:
            with open(filepath, "r") as f:
                data = json.load(f)
                if isinstance(data, list):
                    all_results.extend(data)
                else:
                    all_results.append(data)
        except Exception as e:
            print(f"    Error loading {filepath}: {e}")

    print(f"\nLoaded {len(all_results)} total formulas\n")
    return all_results


def extract_metrics(all_results):
    """Extract metrics from results into DataFrame."""
    df_data = []

    for result in all_results:
        try:
            # Handle different result structures
            validation = result.get("validation", {})
            discovery = result.get("discovery", {})

            df_data.append(
                {
                    "domain": result.get("domain", "unknown"),
                    "valid": validation.get("valid", False),
                    "total_score": validation.get("total_score", 0),
                    "symbolic_score": validation.get("layer_scores", {}).get(
                        "symbolic", 0
                    ),
                    "dimensional_score": validation.get("layer_scores", {}).get(
                        "dimensional", 0
                    ),
                    "domain_score": validation.get("layer_scores", {}).get("domain", 0),
                    "r2_score": discovery.get("r2_score", 0),
                    "complexity": discovery.get("complexity", 0),
                    "expression": discovery.get("expression", ""),
                    "description": result.get("description", ""),
                }
            )
        except Exception as e:
            print(f"Warning: Error extracting metrics from result: {e}")
            continue

    return pd.DataFrame(df_data)


def compute_statistics(df):
    """Compute comprehensive statistics."""
    stats_dict = {
        "overall": {
            "total_formulas": len(df),
            "valid_formulas": int(df["valid"].sum()),
            "success_rate": float(df["valid"].mean()),
            "avg_total_score": float(df["total_score"].mean()),
            "median_total_score": float(df["total_score"].median()),
            "std_total_score": float(df["total_score"].std()),
            "avg_r2_score": float(df["r2_score"].mean()),
            "avg_complexity": float(df["complexity"].mean()),
        }
    }

    # By domain
    for domain in df["domain"].unique():
        domain_df = df[df["domain"] == domain]
        stats_dict[domain] = {
            "count": len(domain_df),
            "valid": int(domain_df["valid"].sum()),
            "success_rate": float(domain_df["valid"].mean()),
            "avg_score": float(domain_df["total_score"].mean()),
            "avg_r2": float(domain_df["r2_score"].mean()),
        }

    # Score statistics
    stats_dict["scores"] = {
        "total_score": {
            "mean": float(df["total_score"].mean()),
            "median": float(df["total_score"].median()),
            "std": float(df["total_score"].std()),
            "min": float(df["total_score"].min()),
            "max": float(df["total_score"].max()),
            "q25": float(df["total_score"].quantile(0.25)),
            "q75": float(df["total_score"].quantile(0.75)),
        },
        "symbolic_score": {
            "mean": float(df["symbolic_score"].mean()),
            "median": float(df["symbolic_score"].median()),
        },
        "dimensional_score": {
            "mean": float(df["dimensional_score"].mean()),
            "median": float(df["dimensional_score"].median()),
        },
        "domain_score": {
            "mean": float(df["domain_score"].mean()),
            "median": float(df["domain_score"].median()),
        },
    }

    return stats_dict


def perform_statistical_tests(df):
    """Perform statistical hypothesis tests."""
    tests = {}

    # Test 1: DeFi vs Risk domain comparison
    if "defi" in df["domain"].values and "risk" in df["domain"].values:
        defi_scores = df[df["domain"] == "defi"]["total_score"]
        risk_scores = df[df["domain"] == "risk"]["total_score"]

        if len(defi_scores) > 0 and len(risk_scores) > 0:
            t_stat, p_value = stats.ttest_ind(defi_scores, risk_scores)

            tests["domain_comparison"] = {
                "test": "Independent t-test",
                "null_hypothesis": "No difference in scores between domains",
                "defi_mean": float(defi_scores.mean()),
                "defi_std": float(defi_scores.std()),
                "risk_mean": float(risk_scores.mean()),
                "risk_std": float(risk_scores.std()),
                "t_statistic": float(t_stat),
                "p_value": float(p_value),
                "significant_at_0.05": bool(p_value < 0.05),
                "effect_size_cohen_d": float(
                    (defi_scores.mean() - risk_scores.mean())
                    / np.sqrt((defi_scores.std() ** 2 + risk_scores.std() ** 2) / 2)
                ),
            }

    # Test 2: Correlation between R² and validation score
    if len(df) > 2:
        corr, p_val = stats.pearsonr(df["r2_score"], df["total_score"])
        tests["r2_validation_correlation"] = {
            "test": "Pearson correlation",
            "correlation": float(corr),
            "p_value": float(p_val),
            "significant_at_0.05": bool(p_val < 0.05),
        }

    # Test 3: Complexity vs validity
    if len(df) > 2:
        valid_complexity = df[df["valid"]]["complexity"].mean()
        invalid_complexity = df[~df["valid"]]["complexity"].mean()

        if not np.isnan(valid_complexity) and not np.isnan(invalid_complexity):
            tests["complexity_validity"] = {
                "valid_mean_complexity": float(valid_complexity),
                "invalid_mean_complexity": float(invalid_complexity),
                "difference": float(valid_complexity - invalid_complexity),
            }

    return tests


def create_visualizations(df):
    """Create statistical visualizations."""
    os.makedirs("results", exist_ok=True)

    # Set style
    sns.set_style("whitegrid")
    sns.set_palette("husl")

    # 1. Score distribution
    fig, axes = plt.subplots(2, 2, figsize=(14, 10))

    # Total score histogram
    axes[0, 0].hist(df["total_score"], bins=20, edgecolor="black", alpha=0.7)
    axes[0, 0].axvline(
        df["total_score"].mean(),
        color="red",
        linestyle="--",
        label=f"Mean: {df['total_score'].mean():.1f}",
    )
    axes[0, 0].set_xlabel("Total Validation Score")
    axes[0, 0].set_ylabel("Frequency")
    axes[0, 0].set_title("Distribution of Validation Scores")
    axes[0, 0].legend()
    axes[0, 0].grid(True, alpha=0.3)

    # R² score histogram
    axes[0, 1].hist(
        df["r2_score"], bins=20, edgecolor="black", alpha=0.7, color="green"
    )
    axes[0, 1].axvline(
        df["r2_score"].mean(),
        color="red",
        linestyle="--",
        label=f"Mean: {df['r2_score'].mean():.3f}",
    )
    axes[0, 1].set_xlabel("R² Score")
    axes[0, 1].set_ylabel("Frequency")
    axes[0, 1].set_title("Distribution of R² Scores")
    axes[0, 1].legend()
    axes[0, 1].grid(True, alpha=0.3)

    # Domain comparison boxplot
    if len(df["domain"].unique()) > 1:
        df.boxplot(column="total_score", by="domain", ax=axes[1, 0])
        axes[1, 0].set_xlabel("Domain")
        axes[1, 0].set_ylabel("Total Score")
        axes[1, 0].set_title("Score Distribution by Domain")
        axes[1, 0].get_figure().suptitle("")  # Remove default title

    # Complexity vs R² scatter
    axes[1, 1].scatter(df["complexity"], df["r2_score"], alpha=0.5)
    axes[1, 1].set_xlabel("Formula Complexity")
    axes[1, 1].set_ylabel("R² Score")
    axes[1, 1].set_title("Complexity vs Fit Quality")
    axes[1, 1].grid(True, alpha=0.3)

    plt.tight_layout()
    plt.savefig("results/statistical_analysis.png", dpi=300, bbox_inches="tight")
    plt.close()

    # 2. Layer scores breakdown
    fig, ax = plt.subplots(figsize=(10, 6))
    layer_means = [
        df["symbolic_score"].mean(),
        df["dimensional_score"].mean(),
        df["domain_score"].mean(),
    ]
    layers = ["Symbolic", "Dimensional", "Domain"]

    bars = ax.bar(
        layers,
        layer_means,
        color=["skyblue", "lightcoral", "lightgreen"],
        edgecolor="black",
        alpha=0.7,
    )
    ax.set_ylabel("Average Score")
    ax.set_title("Average Scores by Validation Layer")
    ax.set_ylim([0, 100])
    ax.grid(True, alpha=0.3, axis="y")

    # Add value labels on bars
    for bar in bars:
        height = bar.get_height()
        ax.text(
            bar.get_x() + bar.get_width() / 2.0,
            height,
            f"{height:.1f}",
            ha="center",
            va="bottom",
            fontsize=12,
            fontweight="bold",
        )

    plt.tight_layout()
    plt.savefig("results/layer_scores.png", dpi=300, bbox_inches="tight")
    plt.close()

    print("✓ Visualizations saved:")
    print("  - results/statistical_analysis.png")
    print("  - results/layer_scores.png")


def analyze_dataset():
    """Comprehensive statistical analysis of all formulas."""

    print("\n" + "=" * 80)
    print("STATISTICAL ANALYSIS OF FORMULA DATASET")
    print("=" * 80 + "\n")

    # Load data
    all_results = load_all_results()

    if not all_results:
        print("No results found. Please generate formulas first.")
        return None, None

    # Extract metrics
    df = extract_metrics(all_results)

    if df.empty:
        print("No valid data extracted.")
        return None, None

    # Compute statistics
    print("=" * 80)
    print("OVERALL STATISTICS")
    print("=" * 80)

    stats_dict = compute_statistics(df)

    print(f"\nTotal formulas: {stats_dict['overall']['total_formulas']}")
    print(
        f"Valid formulas: {stats_dict['overall']['valid_formulas']} "
        f"({stats_dict['overall']['success_rate'] * 100:.1f}%)"
    )

    print(f"\nValidation Scores:")
    print(f"  Mean:   {stats_dict['scores']['total_score']['mean']:.1f}")
    print(f"  Median: {stats_dict['scores']['total_score']['median']:.1f}")
    print(f"  Std:    {stats_dict['scores']['total_score']['std']:.1f}")
    print(f"  Min:    {stats_dict['scores']['total_score']['min']:.1f}")
    print(f"  Max:    {stats_dict['scores']['total_score']['max']:.1f}")

    print(f"\nBy Domain:")
    domain_df = (
        df.groupby("domain")
        .agg({"valid": ["count", "sum"], "total_score": "mean", "r2_score": "mean"})
        .round(2)
    )
    print(domain_df)

    # Statistical tests
    print("\n" + "=" * 80)
    print("STATISTICAL TESTS")
    print("=" * 80)

    tests = perform_statistical_tests(df)

    if "domain_comparison" in tests:
        dc = tests["domain_comparison"]
        print(f"\nDomain Comparison (Independent t-test):")
        print(f"  DeFi mean: {dc['defi_mean']:.1f} (±{dc['defi_std']:.1f})")
        print(f"  Risk mean: {dc['risk_mean']:.1f} (±{dc['risk_std']:.1f})")
        print(f"  t-statistic: {dc['t_statistic']:.3f}")
        print(f"  p-value: {dc['p_value']:.4f}")
        print(
            f"  Significant at α=0.05: {'Yes' if dc['significant_at_0.05'] else 'No'}"
        )
        print(f"  Effect size (Cohen's d): {dc['effect_size_cohen_d']:.3f}")

    if "r2_validation_correlation" in tests:
        rc = tests["r2_validation_correlation"]
        print(f"\nR² vs Validation Score Correlation:")
        print(f"  Pearson r: {rc['correlation']:.3f}")
        print(f"  p-value: {rc['p_value']:.4f}")
        print(f"  Significant: {'Yes' if rc['significant_at_0.05'] else 'No'}")

    # Create visualizations
    print("\n" + "=" * 80)
    print("GENERATING VISUALIZATIONS")
    print("=" * 80 + "\n")
    create_visualizations(df)

    # Save results
    os.makedirs("results", exist_ok=True)

    summary = {"statistics": stats_dict, "tests": tests}

    with open("results/dataset_summary.json", "w") as f:
        json.dump(summary, f, indent=2)

    print("\n✓ Summary saved to results/dataset_summary.json")

    print("\n" + "=" * 80)
    print("ANALYSIS COMPLETE")
    print("=" * 80 + "\n")

    return df, summary


if __name__ == "__main__":
    df, summary = analyze_dataset()
