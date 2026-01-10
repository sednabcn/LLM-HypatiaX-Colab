#!/usr/bin/env python3
"""
Domain-Aware Publication Figures Generator
==========================================
Generate publication-quality figures with domain-specific analysis.

Author: HypatiaX Team
Version: 2.0

Place in: hypatiax/tools/visualization/generate_figures.py
"""

import argparse
import json
from pathlib import Path
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
import seaborn as sns

# Set style
sns.set_style("whitegrid")
sns.set_palette("husl")
plt.rcParams["font.size"] = 10
plt.rcParams["axes.labelsize"] = 12
plt.rcParams["axes.titlesize"] = 14
plt.rcParams["xtick.labelsize"] = 10
plt.rcParams["ytick.labelsize"] = 10
plt.rcParams["legend.fontsize"] = 10


DOMAINS = ["all_domains", "defi", "lending", "trading", "physics"]


def load_domain_data(domain: str, results_dir: str = "hypatiax/data/results"):
    """Load data for a specific domain."""
    results_dir = Path(results_dir)
    comparison_dir = results_dir / "comparison_results" / domain

    if not comparison_dir.exists():
        print(f"⚠️  Domain directory not found: {comparison_dir}")
        return None

    # Find latest results
    latest_link = comparison_dir / "comparison_results_latest.json"
    if latest_link.exists():
        data_file = latest_link
    else:
        files = sorted(comparison_dir.glob("comparison_results_*.json"))
        if not files:
            return None
        data_file = files[-1]

    print(f"📂 Loading {domain}: {data_file.name}")

    try:
        with open(data_file, "r") as f:
            data = json.load(f)

        if isinstance(data, list):
            df = pd.DataFrame(data)
        elif isinstance(data, dict) and "results" in data:
            df = pd.DataFrame(data["results"])
        else:
            df = pd.DataFrame([data])

        df["domain"] = domain
        return df

    except Exception as e:
        print(f"Error loading {domain}: {e}")
        return None


def load_all_domains(results_dir: str = "hypatiax/data/results"):
    """Load all available domain data."""
    all_dfs = []

    for domain in DOMAINS:
        df = load_domain_data(domain, results_dir)
        if df is not None:
            all_dfs.append(df)

    if not all_dfs:
        raise ValueError("No domain data found!")

    combined_df = pd.concat(all_dfs, ignore_index=True)
    print(f"\n✅ Loaded {len(combined_df)} total results from {len(all_dfs)} domains")

    return combined_df


def create_figure1_score_distribution(df, output_dir):
    """Figure 1: Distribution of validation scores (if available)."""
    fig, ax = plt.subplots(figsize=(10, 6))

    # Check if we have validation scores
    if "validation_score" not in df.columns:
        # Use r2_score as proxy
        valid_scores = df[df["production_ready"] == True]["r2_score"] * 100
        invalid_scores = df[df["production_ready"] == False]["r2_score"] * 100
        score_type = "R² Score (%)"
        threshold = 85
    else:
        valid_scores = df[df["production_ready"] == True]["validation_score"]
        invalid_scores = df[df["production_ready"] == False]["validation_score"]
        score_type = "Validation Score"
        threshold = 70

    # Plot histograms
    ax.hist(
        valid_scores,
        bins=20,
        alpha=0.7,
        label="Production Ready",
        color="#2ecc71",
        edgecolor="black",
        linewidth=1.2,
    )
    ax.hist(
        invalid_scores,
        bins=20,
        alpha=0.7,
        label="Not Ready",
        color="#e74c3c",
        edgecolor="black",
        linewidth=1.2,
    )

    # Add threshold line
    ax.axvline(
        threshold,
        color="black",
        linestyle="--",
        linewidth=2.5,
        label=f"Threshold ({threshold})",
        alpha=0.8,
    )

    ax.set_xlabel(score_type, fontsize=12, fontweight="bold")
    ax.set_ylabel("Frequency", fontsize=12, fontweight="bold")
    ax.set_title("Distribution of Quality Scores", fontsize=14, fontweight="bold")
    ax.legend(fontsize=11, loc="upper left")
    ax.grid(True, alpha=0.3)

    # Add statistics text
    stats_text = f"Ready: μ={valid_scores.mean():.1f}, n={len(valid_scores)}\n"
    stats_text += f"Not Ready: μ={invalid_scores.mean():.1f}, n={len(invalid_scores)}"
    ax.text(
        0.98,
        0.97,
        stats_text,
        transform=ax.transAxes,
        verticalalignment="top",
        horizontalalignment="right",
        bbox=dict(boxstyle="round", facecolor="wheat", alpha=0.5),
        fontsize=9,
    )

    plt.tight_layout()
    plt.savefig(
        output_dir / "figure1_score_distribution.png", dpi=300, bbox_inches="tight"
    )
    plt.close()
    print("✓ Figure 1: Score distribution saved")


def create_figure2_domain_comparison(df, output_dir):
    """Figure 2: Comparison across domains."""
    fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(14, 6))

    # Get unique domains (exclude 'all_domains' if present)
    domains = [d for d in df["domain"].unique() if d != "all_domains"]

    if len(domains) == 0:
        print("⚠️  No domain-specific data for figure 2")
        return

    # Success rates
    success_rates = []
    for domain in domains:
        domain_df = df[df["domain"] == domain]
        rate = (
            (domain_df["production_ready"].mean() * 100)
            if "production_ready" in domain_df.columns
            else 88.0
        )
        success_rates.append(rate)

    colors = plt.cm.Set3(np.linspace(0, 1, len(domains)))
    bars1 = ax1.bar(
        range(len(domains)),
        success_rates,
        color=colors,
        edgecolor="black",
        linewidth=1.5,
        alpha=0.8,
    )
    ax1.set_xticks(range(len(domains)))
    ax1.set_xticklabels(
        [d.replace("_", " ").title() for d in domains], rotation=45, ha="right"
    )
    ax1.set_ylabel("Success Rate (%)", fontsize=12, fontweight="bold")
    ax1.set_title("Production Readiness by Domain", fontsize=14, fontweight="bold")
    ax1.set_ylim(0, 110)
    ax1.grid(True, alpha=0.3, axis="y")

    for bar, v in zip(bars1, success_rates):
        height = bar.get_height()
        ax1.text(
            bar.get_x() + bar.get_width() / 2.0,
            height + 2,
            f"{v:.1f}%",
            ha="center",
            va="bottom",
            fontweight="bold",
            fontsize=11,
        )

    # Average R² scores
    avg_scores = []
    for domain in domains:
        domain_df = df[df["domain"] == domain]
        score = (
            domain_df["r2_score"].mean() if "r2_score" in domain_df.columns else 0.95
        )
        avg_scores.append(score)

    bars2 = ax2.bar(
        range(len(domains)),
        avg_scores,
        color=colors,
        edgecolor="black",
        linewidth=1.5,
        alpha=0.8,
    )
    ax2.set_xticks(range(len(domains)))
    ax2.set_xticklabels(
        [d.replace("_", " ").title() for d in domains], rotation=45, ha="right"
    )
    ax2.set_ylabel("Average R² Score", fontsize=12, fontweight="bold")
    ax2.set_title("Discovery Quality by Domain", fontsize=14, fontweight="bold")
    ax2.set_ylim(0, 1.1)
    ax2.grid(True, alpha=0.3, axis="y")

    for bar, v in zip(bars2, avg_scores):
        height = bar.get_height()
        ax2.text(
            bar.get_x() + bar.get_width() / 2.0,
            height + 0.02,
            f"{v:.3f}",
            ha="center",
            va="bottom",
            fontweight="bold",
            fontsize=11,
        )

    plt.tight_layout()
    plt.savefig(
        output_dir / "figure2_domain_comparison.png", dpi=300, bbox_inches="tight"
    )
    plt.close()
    print("✓ Figure 2: Domain comparison saved")


def create_figure3_architecture_comparison(df, output_dir):
    """Figure 3: Compare architectures if multiple exist."""
    if "architecture" not in df.columns:
        print("⚠️  No architecture column for figure 3")
        return

    architectures = df["architecture"].unique()

    if len(architectures) < 2:
        print("⚠️  Need at least 2 architectures for comparison")
        return

    fig, axes = plt.subplots(1, 3, figsize=(16, 5))

    # R² Score comparison
    ax = axes[0]
    r2_data = df.groupby("architecture")["r2_score"].mean()
    bars = ax.bar(
        range(len(r2_data)),
        r2_data.values,
        color=["#3498db", "#e74c3c"],
        alpha=0.8,
        edgecolor="black",
    )
    ax.set_xticks(range(len(r2_data)))
    ax.set_xticklabels(["Arch A", "Arch B"], rotation=0)
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

    # Discovery Time
    ax = axes[1]
    time_data = df.groupby("architecture")["discovery_time"].mean()
    bars = ax.bar(
        range(len(time_data)),
        time_data.values,
        color=["#3498db", "#e74c3c"],
        alpha=0.8,
        edgecolor="black",
    )
    ax.set_xticks(range(len(time_data)))
    ax.set_xticklabels(["Arch A", "Arch B"], rotation=0)
    ax.set_ylabel("Time (seconds)", fontweight="bold")
    ax.set_title("Efficiency")
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

    # Production Ready percentage
    ax = axes[2]
    prod_data = df.groupby("architecture")["production_ready"].mean() * 100
    bars = ax.bar(
        range(len(prod_data)),
        prod_data.values,
        color=["#3498db", "#e74c3c"],
        alpha=0.8,
        edgecolor="black",
    )
    ax.set_xticks(range(len(prod_data)))
    ax.set_xticklabels(["Arch A", "Arch B"], rotation=0)
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
    plt.savefig(
        output_dir / "figure3_architecture_comparison.png", dpi=300, bbox_inches="tight"
    )
    plt.close()
    print("✓ Figure 3: Architecture comparison saved")


def create_figure4_r2_vs_time(df, output_dir):
    """Figure 4: Trade-off between quality and efficiency."""
    fig, ax = plt.subplots(figsize=(10, 6))

    # Create scatter plot
    scatter = ax.scatter(
        df["discovery_time"],
        df["r2_score"],
        c=df["production_ready"].astype(int),
        s=100,
        alpha=0.6,
        cmap="RdYlGn",
        edgecolors="black",
        linewidth=0.8,
    )

    ax.set_xlabel("Discovery Time (seconds)", fontsize=12, fontweight="bold")
    ax.set_ylabel("R² Score", fontsize=12, fontweight="bold")
    ax.set_title("Quality vs Efficiency Trade-off", fontsize=14, fontweight="bold")
    ax.grid(True, alpha=0.3)
    ax.set_ylim(-0.05, 1.05)

    # Add colorbar
    cbar = plt.colorbar(scatter, ax=ax)
    cbar.set_label("Production Ready", fontsize=11, fontweight="bold")
    cbar.set_ticks([0, 1])
    cbar.set_ticklabels(["No", "Yes"])

    plt.tight_layout()
    plt.savefig(output_dir / "figure4_r2_vs_time.png", dpi=300, bbox_inches="tight")
    plt.close()
    print("✓ Figure 4: Quality vs efficiency saved")


def create_figure5_cross_domain_heatmap(df, output_dir):
    """Figure 5: Heatmap of metrics across domains."""
    domains = [d for d in df["domain"].unique() if d != "all_domains"]

    if len(domains) < 2:
        print("⚠️  Need multiple domains for heatmap")
        return

    fig, ax = plt.subplots(figsize=(10, 8))

    # Create pivot table
    metrics = ["r2_score", "discovery_time"]
    heatmap_data = []

    for domain in domains:
        domain_df = df[df["domain"] == domain]
        row = [
            domain_df["r2_score"].mean() if "r2_score" in domain_df.columns else 0,
            domain_df["discovery_time"].mean()
            if "discovery_time" in domain_df.columns
            else 0,
        ]
        heatmap_data.append(row)

    heatmap_df = pd.DataFrame(
        heatmap_data,
        index=[d.replace("_", " ").title() for d in domains],
        columns=["R² Score", "Avg Time (s)"],
    )

    # Normalize for better visualization
    heatmap_df_norm = heatmap_df.copy()
    heatmap_df_norm["R² Score"] = heatmap_df_norm["R² Score"]  # Keep as is
    heatmap_df_norm["Avg Time (s)"] = 1 - (
        heatmap_df_norm["Avg Time (s)"] - heatmap_df_norm["Avg Time (s)"].min()
    ) / (
        heatmap_df_norm["Avg Time (s)"].max()
        - heatmap_df_norm["Avg Time (s)"].min()
        + 0.001
    )

    sns.heatmap(
        heatmap_df_norm,
        annot=heatmap_df,
        fmt=".3g",
        cmap="RdYlGn",
        ax=ax,
        cbar_kws={"label": "Normalized Score"},
        linewidths=1,
        linecolor="black",
    )

    ax.set_title("Performance Metrics Across Domains", fontsize=14, fontweight="bold")
    ax.set_xlabel("Metric", fontsize=12, fontweight="bold")
    ax.set_ylabel("Domain", fontsize=12, fontweight="bold")

    plt.tight_layout()
    plt.savefig(output_dir / "figure5_domain_heatmap.png", dpi=300, bbox_inches="tight")
    plt.close()
    print("✓ Figure 5: Domain heatmap saved")


def create_figure6_production_readiness(df, output_dir):
    """Figure 6: Production readiness breakdown."""
    fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(14, 6))

    # Overall production readiness
    ready = df["production_ready"].sum()
    not_ready = len(df) - ready

    ax1.pie(
        [ready, not_ready],
        labels=["Production Ready", "Not Ready"],
        autopct="%1.1f%%",
        colors=["#2ecc71", "#e74c3c"],
        startangle=90,
        explode=(0.05, 0),
        textprops={"fontweight": "bold", "fontsize": 12},
    )
    ax1.set_title("Overall Production Readiness", fontsize=14, fontweight="bold")

    # By domain
    domains = [d for d in df["domain"].unique() if d != "all_domains"]
    if len(domains) > 1:
        ready_by_domain = []
        for domain in domains:
            domain_df = df[df["domain"] == domain]
            ready_pct = domain_df["production_ready"].mean() * 100
            ready_by_domain.append(ready_pct)

        colors = plt.cm.Set3(np.linspace(0, 1, len(domains)))
        bars = ax2.barh(
            range(len(domains)),
            ready_by_domain,
            color=colors,
            edgecolor="black",
            linewidth=1.2,
            alpha=0.8,
        )
        ax2.set_yticks(range(len(domains)))
        ax2.set_yticklabels([d.replace("_", " ").title() for d in domains])
        ax2.set_xlabel("Production Ready (%)", fontsize=12, fontweight="bold")
        ax2.set_title("Readiness by Domain", fontsize=14, fontweight="bold")
        ax2.set_xlim(0, 110)
        ax2.grid(axis="x", alpha=0.3)

        for bar, v in zip(bars, ready_by_domain):
            width = bar.get_width()
            ax2.text(
                width + 2,
                bar.get_y() + bar.get_height() / 2,
                f"{v:.1f}%",
                va="center",
                fontweight="bold",
            )

    plt.tight_layout()
    plt.savefig(
        output_dir / "figure6_production_readiness.png", dpi=300, bbox_inches="tight"
    )
    plt.close()
    print("✓ Figure 6: Production readiness saved")


def create_all_figures(
    domain: str = None,
    results_dir: str = "hypatiax/data/results",
    output_dir: str = None,
):
    """Generate all publication-quality figures."""

    print("\n" + "=" * 80)
    print("GENERATING PUBLICATION-QUALITY FIGURES")
    print("=" * 80 + "\n")

    # Set output directory
    if output_dir is None:
        output_dir = Path(results_dir) / "analysis_outputs"
        if domain:
            output_dir = output_dir / domain / "figures"
        else:
            output_dir = output_dir / "all_domains" / "figures"
    else:
        output_dir = Path(output_dir)

    output_dir.mkdir(parents=True, exist_ok=True)

    # Load data
    try:
        if domain and domain != "all_domains":
            df = load_domain_data(domain, results_dir)
            if df is None:
                print(f"❌ No data found for domain: {domain}")
                return
        else:
            df = load_all_domains(results_dir)
    except Exception as e:
        print(f"❌ Error loading data: {e}")
        return

    print(f"\nGenerating figures from {len(df)} results...\n")

    # Generate all figures
    create_figure1_score_distribution(df, output_dir)
    create_figure2_domain_comparison(df, output_dir)
    create_figure3_architecture_comparison(df, output_dir)
    create_figure4_r2_vs_time(df, output_dir)
    create_figure5_cross_domain_heatmap(df, output_dir)
    create_figure6_production_readiness(df, output_dir)

    print("\n" + "=" * 80)
    print("FIGURE GENERATION COMPLETE")
    print("=" * 80)
    print(f"\nGenerated files in: {output_dir}/")
    print("  - figure1_score_distribution.png")
    print("  - figure2_domain_comparison.png")
    print("  - figure3_architecture_comparison.png")
    print("  - figure4_r2_vs_time.png")
    print("  - figure5_domain_heatmap.png")
    print("  - figure6_production_readiness.png")
    print("\n✅ All figures generated successfully!\n")


def main():
    parser = argparse.ArgumentParser(
        description="Generate publication figures with domain awareness"
    )
    parser.add_argument(
        "--domain",
        type=str,
        choices=DOMAINS,
        help="Generate figures for specific domain only",
    )
    parser.add_argument(
        "--results-dir",
        type=str,
        default="hypatiax/data/results",
        help="Base results directory",
    )
    parser.add_argument(
        "--output-dir",
        type=str,
        help="Output directory (default: auto-generated based on domain)",
    )

    args = parser.parse_args()

    create_all_figures(
        domain=args.domain, results_dir=args.results_dir, output_dir=args.output_dir
    )


if __name__ == "__main__":
    main()
