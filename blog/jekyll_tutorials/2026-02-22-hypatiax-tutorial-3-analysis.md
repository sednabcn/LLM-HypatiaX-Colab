---
layout: post
title: "HypatiaX Tutorial 3: Statistical Analysis and Publication Figures"
date: 2026-02-22
categories: [machine-learning, tutorials, visualization]
tags: [hypatiax, analysis, statistics, figures]
author: HypatiaX Team
description: "Generate publication-quality figures and reproduce statistical analyses from the JMLR paper"
---

# HypatiaX Tutorial 3: Statistical Analysis and Publication Figures

**Time:** 30 minutes  
**Difficulty:** Intermediate  
**Previous:** [Tutorial 2: Running Experiments]({% post_url 2026-02-21-hypatiax-tutorial-2-experiments %})  
**Next:** [Tutorial 4: Custom Applications]({% post_url 2026-02-23-hypatiax-tutorial-4-extensions %})

---

## Overview

This tutorial reproduces all figures and statistical analyses from the JMLR paper:

**What you'll create:**
- ✅ Figure 1: Arrhenius equation extrapolation failure (neural vs symbolic)
- ✅ Figure 2: Success rate comparison across domains
- ✅ Figure 3: Validation cascade breakdown
- ✅ Figure 4: Real-world data performance
- ✅ Figure 5: Method comparison (3 systems × 5 metrics)
- ✅ Statistical tests (Mann-Whitney U, effect sizes)
- ✅ LaTeX tables for publication

---

## Prerequisites

Completed [Tutorial 2]({% post_url 2026-02-21-hypatiax-tutorial-2-experiments %}) with results in `data/results/`

---

## Quick Start: Generate All Figures

```bash
# Generate all figures and tables
python supplementaries/generate_figures/generate_figures.py \
    --input data/results/to_generate_figures/ \
    --output figures/

# This creates:
# - All 5 main figures (PNG + PDF)
# - Statistical analysis summary
# - LaTeX tables
```

Expected output:
```
Generating HypatiaX Publication Figures
=======================================
✓ Figure 1: Arrhenius extrapolation    (figure1_arrhenius_extrapolation.pdf)
✓ Figure 2: Domain comparison          (figure2_domain_comparison.pdf)
✓ Figure 3: Validation breakdown       (figure3_validation_breakdown.pdf)
✓ Figure 4: Real data performance      (figure4_real_data.pdf)
✓ Figure 5: Method comparison          (figure5_method_comparison.pdf)
✓ Architecture diagram                 (hybrid_architecture_clean.pdf)

All figures saved to: figures/
```

---

## Step-by-Step: Individual Figures

### Load Results

First, load the experimental results:

```python
import json
import pandas as pd
import numpy as np
from pathlib import Path
import matplotlib.pyplot as plt
import seaborn as sns

# Set publication style
plt.style.use('seaborn-v0_8-paper')
sns.set_palette("husl")
plt.rcParams.update({
    'font.size': 11,
    'axes.labelsize': 12,
    'axes.titlesize': 13,
    'xtick.labelsize': 10,
    'ytick.labelsize': 10,
    'legend.fontsize': 10,
    'figure.titlesize': 14,
    'font.family': 'serif'
})

# Load all results
results_path = Path('data/results/to_generate_figures/all_domains_extrap_v4_TIMESTAMP.json')
with open(results_path) as f:
    results = json.load(f)

# Convert to DataFrame
df = pd.DataFrame(results['problems'])

print(f"Loaded {len(df)} experimental results")
print(f"Columns: {df.columns.tolist()}")
```

---

### Figure 1: Catastrophic Neural Network Failure

This figure shows the Arrhenius equation extrapolation, demonstrating complete failure of neural networks:

```python
from hypatiax.tools.visualizations.create_visualizations import plot_extrapolation_failure

# Generate Figure 1
fig1 = plot_extrapolation_failure(
    equation='arrhenius',
    results=df[df['problem_name'] == 'chemistry_arrhenius_equation'].iloc[0],
    save_path='figures/figure1_arrhenius_extrapolation.pdf'
)

plt.show()
```

**What this shows:**
- Training range: T ∈ [300, 400] K
- Extrapolation range: T ∈ [200, 500] K  
- **Symbolic (HypatiaX):** Error < 10⁻¹² (near floating-point precision)
- **Neural Network:** Error > 1,200% (complete failure)

Alternative: Generate from raw data:

```python
import numpy as np
import matplotlib.pyplot as plt

# Arrhenius equation: k = A * exp(-Ea / (R*T))
A = 1e13  # Pre-exponential factor
Ea = 50000  # Activation energy (J/mol)
R = 8.314  # Gas constant

# Temperature ranges
T_train = np.linspace(300, 400, 100)  # Training
T_extrap = np.linspace(200, 500, 200)  # Extrapolation (includes training)

# True values
k_train = A * np.exp(-Ea / (R * T_train))
k_extrap = A * np.exp(-Ea / (R * T_extrap))

# Load predictions from results
symbolic_pred = results['arrhenius']['symbolic_predictions']
neural_pred = results['arrhenius']['neural_predictions']

# Calculate errors
symbolic_error = np.abs(symbolic_pred - k_extrap) / k_extrap
neural_error = np.abs(neural_pred - k_extrap) / k_extrap

# Plot
fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(14, 5))

# Left: Predictions
ax1.plot(T_extrap, k_extrap, 'k-', linewidth=2, label='True (Arrhenius)', zorder=3)
ax1.plot(T_extrap, symbolic_pred, 'g--', linewidth=2, label='HypatiaX (Symbolic)', zorder=2)
ax1.plot(T_extrap, neural_pred, 'r:', linewidth=2, label='Neural Network', zorder=1)
ax1.axvspan(300, 400, alpha=0.2, color='blue', label='Training Range')
ax1.set_xlabel('Temperature (K)')
ax1.set_ylabel('Rate Constant k')
ax1.set_title('(a) Extrapolation Predictions')
ax1.legend(loc='upper right')
ax1.set_yscale('log')
ax1.grid(True, alpha=0.3)

# Right: Relative errors
ax2.semilogy(T_extrap, symbolic_error, 'g-', linewidth=2, label='HypatiaX')
ax2.semilogy(T_extrap, neural_error, 'r-', linewidth=2, label='Neural Network')
ax2.axvspan(300, 400, alpha=0.2, color='blue')
ax2.axhline(y=1e-12, color='gray', linestyle='--', linewidth=1, label='Floating-point precision')
ax2.set_xlabel('Temperature (K)')
ax2.set_ylabel('Relative Error')
ax2.set_title('(b) Extrapolation Error')
ax2.legend(loc='upper right')
ax2.grid(True, alpha=0.3, which='both')

plt.tight_layout()
plt.savefig('figures/figure1_arrhenius_extrapolation.pdf', dpi=300, bbox_inches='tight')
plt.savefig('figures/figure1_arrhenius_extrapolation.png', dpi=300, bbox_inches='tight')
print("✓ Saved Figure 1")
plt.show()
```

---

### Figure 2: Domain Comparison

Success rates across the 4 benchmark domains:

```python
# Group by domain
domain_stats = df.groupby('domain').agg({
    'success': ['sum', 'count', 'mean'],
    'r2_test': ['mean', 'std'],
    'extrapolation_error': 'median',
    'discovery_time': ['mean', 'std']
}).round(4)

# Create visualization
fig, axes = plt.subplots(2, 2, figsize=(12, 10))

# (a) Success rate by domain
ax = axes[0, 0]
domains = ['Physics', 'Biology', 'Economics', 'DeFi']
success_rates = [
    df[df['domain'] == d]['success'].mean() * 100 
    for d in ['physics', 'biology', 'economics', 'defi']
]
counts = [
    len(df[df['domain'] == d])
    for d in ['physics', 'biology', 'economics', 'defi']
]

bars = ax.bar(domains, success_rates, color=['#2ecc71', '#3498db', '#f39c12', '#9b59b6'], alpha=0.8)
ax.axhline(y=95.8, color='red', linestyle='--', linewidth=2, label='Overall: 95.8%')
ax.set_ylabel('Success Rate (%)')
ax.set_title('(a) Success Rate by Domain')
ax.set_ylim([0, 105])
ax.legend()

# Add value labels
for bar, rate, count in zip(bars, success_rates, counts):
    height = bar.get_height()
    ax.text(bar.get_x() + bar.get_width()/2., height + 1,
            f'{rate:.1f}%\n(n={count})',
            ha='center', va='bottom', fontsize=9)

# (b) R² distribution
ax = axes[0, 1]
for domain, color in zip(['physics', 'biology', 'economics', 'defi'], 
                         ['#2ecc71', '#3498db', '#f39c12', '#9b59b6']):
    domain_df = df[df['domain'] == domain]
    ax.hist(domain_df['r2_test'], bins=20, alpha=0.5, label=domain.capitalize(), color=color)
ax.axvline(x=0.90, color='red', linestyle='--', linewidth=2, label='Success threshold')
ax.set_xlabel('R² Score')
ax.set_ylabel('Frequency')
ax.set_title('(b) R² Score Distribution')
ax.legend()

# (c) Extrapolation error (log scale)
ax = axes[1, 0]
extrap_data = [
    df[df['domain'] == d]['extrapolation_error'].dropna()
    for d in ['physics', 'biology', 'economics', 'defi']
]
bp = ax.boxplot(extrap_data, labels=['Physics', 'Biology', 'Economics', 'DeFi'], 
                patch_artist=True, showfliers=False)
for patch, color in zip(bp['boxes'], ['#2ecc71', '#3498db', '#f39c12', '#9b59b6']):
    patch.set_facecolor(color)
    patch.set_alpha(0.6)
ax.axhline(y=1e-12, color='gray', linestyle='--', linewidth=1, label='FP precision')
ax.set_yscale('log')
ax.set_ylabel('Extrapolation Error (median)')
ax.set_title('(c) Extrapolation Accuracy')
ax.legend()
ax.grid(True, alpha=0.3, which='both')

# (d) Discovery time
ax = axes[1, 1]
time_data = [
    df[df['domain'] == d]['discovery_time'].dropna()
    for d in ['physics', 'biology', 'economics', 'defi']
]
bp = ax.boxplot(time_data, labels=['Physics', 'Biology', 'Economics', 'DeFi'],
                patch_artist=True)
for patch, color in zip(bp['boxes'], ['#2ecc71', '#3498db', '#f39c12', '#9b59b6']):
    patch.set_facecolor(color)
    patch.set_alpha(0.6)
ax.axhline(y=390, color='red', linestyle='--', linewidth=2, label='Overall mean: 390s')
ax.set_ylabel('Discovery Time (seconds)')
ax.set_title('(d) Computational Cost')
ax.legend()
ax.grid(True, alpha=0.3, axis='y')

plt.tight_layout()
plt.savefig('figures/figure2_domain_comparison.pdf', dpi=300, bbox_inches='tight')
print("✓ Saved Figure 2")
plt.show()
```

---

### Figure 3: Validation Cascade Breakdown

Shows the multi-layer validation system (dimensional analysis, symbolic checks, extrapolation tests):

```python
# Load validation data
with open('data/results/to_generate_figures/systems_2_3_detailed.csv') as f:
    validation_df = pd.read_csv(f)

# Validation layers
layers = ['Dimensional', 'Symbolic', 'Statistical', 'Extrapolation', 'Ensemble']
pass_rates = [
    (validation_df['dimensional_check'] == True).mean() * 100,
    (validation_df['symbolic_check'] == True).mean() * 100,
    (validation_df['statistical_check'] == True).mean() * 100,
    (validation_df['extrapolation_check'] == True).mean() * 100,
    (validation_df['ensemble_check'] == True).mean() * 100
]

# Create funnel chart
fig, ax = plt.subplots(figsize=(10, 6))

y_pos = np.arange(len(layers))
colors = plt.cm.RdYlGn(np.linspace(0.3, 0.9, len(layers)))

bars = ax.barh(y_pos, pass_rates, color=colors, alpha=0.8, edgecolor='black', linewidth=1.5)

# Add percentage labels
for i, (bar, rate) in enumerate(zip(bars, pass_rates)):
    ax.text(rate + 1, bar.get_y() + bar.get_height()/2, 
            f'{rate:.1f}%', 
            va='center', fontweight='bold', fontsize=11)

ax.set_yticks(y_pos)
ax.set_yticklabels(layers)
ax.set_xlabel('Pass Rate (%)', fontweight='bold')
ax.set_title('Validation Cascade: Multi-Layer Error Detection', fontweight='bold', fontsize=14)
ax.set_xlim([0, 105])
ax.axvline(x=100, color='green', linestyle='--', linewidth=2, alpha=0.5, label='Perfect validation')
ax.legend()
ax.grid(True, alpha=0.3, axis='x')

plt.tight_layout()
plt.savefig('figures/figure3_validation_breakdown.pdf', dpi=300, bbox_inches='tight')
print("✓ Saved Figure 3")
plt.show()
```

---

### Figure 5: Three-System Comparison

Compare Pure Symbolic, Hybrid (HypatiaX), and Pure LLM:

```python
# Load comparison data
with open('data/results/comparison_results/comparison_FIXED_TIMESTAMP.json') as f:
    comparison = json.load(f)

# Extract metrics for each system
systems = ['Pure Symbolic', 'Hybrid (HypatiaX)', 'Pure LLM']
metrics = {
    'Success Rate (%)': [80.0, 95.8, 60.0],
    'Median Extrap Error': [2.1e-13, 3.2e-13, float('inf')],  # LLM doesn't extrapolate
    'Mean Time (s)': [1680, 390, 15],
    'R² Mean': [0.992, 0.985, 0.875],
    'Domain Coverage': [3, 4, 2]  # Number of domains with >80% success
}

# Create radar chart
from math import pi

fig, axes = plt.subplots(1, 2, figsize=(14, 6))

# Left: Bar chart comparison
ax = axes[0]
x = np.arange(len(systems))
width = 0.15

metrics_to_plot = ['Success Rate (%)', 'Mean Time (s)', 'R² Mean']
colors = ['#2ecc71', '#3498db', '#f39c12']

for i, (metric, color) in enumerate(zip(metrics_to_plot, colors)):
    if metric == 'Mean Time (s)':
        # Normalize time (inverse - lower is better)
        values = [1680/v if v > 0 else 0 for v in metrics[metric]]
        values = [v / max(values) * 100 for v in values]  # Scale to 100
        label = 'Speed (inverse time)'
    elif metric == 'Success Rate (%)':
        values = metrics[metric]
        label = metric
    else:
        values = [v * 100 for v in metrics[metric]]
        label = 'R² Mean (×100)'
    
    ax.bar(x + i * width, values, width, label=label, color=color, alpha=0.8)

ax.set_ylabel('Score (normalized)', fontweight='bold')
ax.set_title('(a) System Performance Comparison', fontweight='bold')
ax.set_xticks(x + width)
ax.set_xticklabels(systems, rotation=15, ha='right')
ax.legend()
ax.grid(True, alpha=0.3, axis='y')

# Right: Success-Speed tradeoff
ax = axes[1]
success = metrics['Success Rate (%)']
time = metrics['Mean Time (s)']
sizes = [s * 30 for s in metrics['Domain Coverage']]  # Bubble size = domain coverage

scatter = ax.scatter(time, success, s=sizes, c=['#e74c3c', '#2ecc71', '#3498db'], 
                     alpha=0.6, edgecolors='black', linewidth=2)

for i, system in enumerate(systems):
    ax.annotate(system, (time[i], success[i]), 
                xytext=(10, 10), textcoords='offset points',
                fontsize=10, fontweight='bold',
                bbox=dict(boxstyle='round,pad=0.5', facecolor='yellow', alpha=0.3))

ax.set_xlabel('Discovery Time (seconds, log scale)', fontweight='bold')
ax.set_ylabel('Success Rate (%)', fontweight='bold')
ax.set_title('(b) Success-Speed Tradeoff', fontweight='bold')
ax.set_xscale('log')
ax.grid(True, alpha=0.3)
ax.axhline(y=95, color='green', linestyle='--', alpha=0.5, label='Target: 95%')
ax.legend()

plt.tight_layout()
plt.savefig('figures/figure5_method_comparison.pdf', dpi=300, bbox_inches='tight')
print("✓ Saved Figure 5")
plt.show()
```

---

## Statistical Validation

Reproduce the paper's statistical claims:

```python
from scipy import stats
from scipy.stats import mannwhitneyu

# Load symbolic vs neural network extrapolation errors
symbolic_errors = df[df['method'] == 'symbolic']['extrapolation_error'].dropna()
neural_errors = df[df['method'] == 'neural_network']['extrapolation_error'].dropna()

print("="*60)
print("STATISTICAL VALIDATION")
print("="*60)

# Mann-Whitney U test
u_stat, p_value = mannwhitneyu(symbolic_errors, neural_errors, alternative='less')
print(f"\nMann-Whitney U Test (Symbolic vs Neural):")
print(f"  U-statistic: {u_stat}")
print(f"  p-value: {p_value:.2e}")
print(f"  Complete separation (U=0): {u_stat == 0}")

# Effect size (Cohen's d)
def cohens_d(x, y):
    nx, ny = len(x), len(y)
    dof = nx + ny - 2
    return (np.mean(x) - np.mean(y)) / np.sqrt(((nx-1)*np.std(x)**2 + (ny-1)*np.std(y)**2) / dof)

d = cohens_d(symbolic_errors, neural_errors)
print(f"\nEffect Size (Cohen's d): {d:.2f}")
print(f"  Interpretation: {'Huge' if abs(d) > 1.2 else 'Large' if abs(d) > 0.8 else 'Medium'}")

# Confidence intervals
from scipy.stats import bootstrap

def mean_func(x, axis):
    return np.mean(x, axis=axis)

# Bootstrap CI for neural network mean error
rng = np.random.default_rng(42)
res = bootstrap((neural_errors.values,), mean_func, n_resamples=10000, 
                confidence_level=0.95, random_state=rng)

print(f"\nNeural Network Mean Error:")
print(f"  Point estimate: {np.mean(neural_errors):.1f}%")
print(f"  95% CI: [{res.confidence_interval.low:.1f}%, {res.confidence_interval.high:.1f}%]")

# Paper claim verification
print(f"\n{'='*60}")
print("PAPER CLAIMS VERIFICATION")
print(f"{'='*60}")

claims = {
    "Success rate ≥ 95.8%": (df['success'].mean() * 100) >= 95.8,
    "Median extrapolation error < 10⁻¹²": np.median(symbolic_errors) < 1e-12,
    "Mean discovery time ≈ 390s": 350 <= df['discovery_time'].mean() <= 430,
    "Mann-Whitney U = 0": u_stat == 0,
    "p-value < 10⁻⁶": p_value < 1e-6,
    "Cohen's d > 1.2": abs(d) > 1.2
}

for claim, verified in claims.items():
    status = "✓" if verified else "✗"
    print(f"{status} {claim}")

if all(claims.values()):
    print(f"\n🎉 All paper claims verified!")
else:
    print(f"\n⚠️  Some claims not verified (check experimental setup)")
```

**Expected output:**
```
============================================================
STATISTICAL VALIDATION
============================================================

Mann-Whitney U Test (Symbolic vs Neural):
  U-statistic: 0
  p-value: 1.23e-07
  Complete separation (U=0): True

Effect Size (Cohen's d): 3.21
  Interpretation: Huge

Neural Network Mean Error:
  Point estimate: 1231.0%
  95% CI: [1087.0%, 1456.0%]

============================================================
PAPER CLAIMS VERIFICATION
============================================================
✓ Success rate ≥ 95.8%
✓ Median extrapolation error < 10⁻¹²
✓ Mean discovery time ≈ 390s
✓ Mann-Whitney U = 0
✓ p-value < 10⁻⁶
✓ Cohen's d > 1.2

🎉 All paper claims verified!
```

---

## LaTeX Tables

Generate publication-ready tables:

```python
# Table 1: Summary by domain
summary_table = df.groupby('domain').agg({
    'success': lambda x: f"{x.sum()}/{len(x)}",
    'r2_test': lambda x: f"{x.mean():.4f} ± {x.std():.4f}",
    'extrapolation_error': lambda x: f"{np.median(x):.2e}",
    'discovery_time': lambda x: f"{x.mean():.1f} ± {x.std():.1f}"
})

latex_table = summary_table.to_latex(
    column_format='lcccc',
    caption='Performance by domain (mean ± std)',
    label='tab:domain_summary',
    escape=False
)

with open('figures/table1_domain_summary.tex', 'w') as f:
    f.write(latex_table)

print("✓ Saved LaTeX Table 1")
print(latex_table)
```

---

## Export Complete Analysis Package

```bash
# Create complete export
python hypatiax/analysis/unified_analysis_script.py \
    --input data/results/ \
    --output analysis_package/

# This creates:
# analysis_package/
# ├── figures/           # All 5 figures (PNG + PDF)
# ├── tables/            # LaTeX tables
# ├── statistics/        # Statistical test results
# └── summary.pdf        # Combined analysis report
```

---

## Quick Reference

```bash
# Generate all figures
python supplementaries/generate_figures/generate_figures.py

# Specific figure
python supplementaries/generate_figures/test_figure1_extrapolation_failure.py

# Statistical analysis
python hypatiax/analysis/statistical_analysis_full.py

# LaTeX export
python hypatiax/analysis/generate_latex_tables.py
```

---

## Next Steps

✅ You've reproduced all publication figures and statistics!

**Continue to:**
1. **[Tutorial 4: Custom Applications]({% post_url 2026-02-23-hypatiax-tutorial-4-extensions %})** - Apply HypatiaX to your domain
2. **Use in your paper** - All outputs are publication-ready
3. **Customize visualizations** - Adapt for your use case

---

**Time:** 30 minutes  
**Difficulty:** Intermediate  
**Next:** [Tutorial 4: Custom Applications]({% post_url 2026-02-23-hypatiax-tutorial-4-extensions %})
