#!/usr/bin/env python3
"""
Generate all figures for HypatiaX manuscript from CSV data
"""

import pandas as pd
import matplotlib.pyplot as plt
import numpy as np
import seaborn as sns
from pathlib import Path

# Set publication-quality style
plt.style.use('seaborn-v0_8-paper')
sns.set_palette("colorblind")
plt.rcParams.update({
    'font.size': 10,
    'font.family': 'serif',
    'font.serif': ['Times New Roman'],
    'text.usetex': False,
    'figure.figsize': (6, 4),
    'figure.dpi': 300,
    'axes.labelsize': 10,
    'axes.titlesize': 11,
    'xtick.labelsize': 9,
    'ytick.labelsize': 9,
    'legend.fontsize': 9,
})

# Create output directory
output_dir = Path('figures')
output_dir.mkdir(exist_ok=True)

def figure1_arrhenius_extrapolation():
    """Figure 1: Arrhenius equation extrapolation comparison"""
    df = pd.read_csv('figure1_arrhenius_extrapolation.csv')
    
    fig, ax = plt.subplots(figsize=(7, 5))
    
    # Plot training data
    train_data = df[df['training_data'] == True]
    extrap_data = df[df['training_data'] == False]
    
    # Ground truth
    ax.plot(df['temperature_K'], df['ground_truth_k'], 'k-', 
            linewidth=2, label='Ground Truth', zorder=3)
    
    # Neural network
    ax.plot(df['temperature_K'], df['neural_network_k'], 'r--', 
            linewidth=2, label='Neural Network', zorder=2)
    
    # HypatiaX
    ax.plot(df['temperature_K'], df['hybrid_v40_k'], 'b:', 
            linewidth=2, label='HypatiaX', zorder=1)
    
    # Shade training region
    ax.axvspan(train_data['temperature_K'].min(), 
               train_data['temperature_K'].max(), 
               alpha=0.1, color='green', label='Training Region')
    
    ax.set_xlabel('Temperature (K)')
    ax.set_ylabel('Rate Constant k')
    ax.set_title('Arrhenius Equation: Catastrophic Neural Extrapolation Failure')
    ax.legend(loc='upper left')
    ax.set_yscale('log')
    ax.grid(True, alpha=0.3)
    
    plt.tight_layout()
    plt.savefig(output_dir / 'figure1_arrhenius.pdf', bbox_inches='tight')
    plt.savefig(output_dir / 'figure1_arrhenius.png', bbox_inches='tight', dpi=300)
    plt.close()
    
    print("✓ Figure 1: Arrhenius extrapolation")

def figure2_domain_comparison():
    """Figure 2: Domain-wise performance comparison"""
    df = pd.read_csv('figure2_domain_comparison.csv')
    
    fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(10, 4))
    
    # Success rates
    x = np.arange(len(df))
    width = 0.35
    
    ax1.bar(x - width/2, df['pure_llm_success_rate'], width, 
            label='Pure LLM', color='orange', alpha=0.8)
    ax1.bar(x + width/2, df['hybrid_v40_success_rate'], width, 
            label='HypatiaX', color='blue', alpha=0.8)
    
    ax1.set_xlabel('Domain')
    ax1.set_ylabel('Success Rate (%)')
    ax1.set_title('Success Rate by Domain')
    ax1.set_xticks(x)
    ax1.set_xticklabels(df['domain'], rotation=45, ha='right')
    ax1.legend()
    ax1.set_ylim([0, 105])
    ax1.grid(True, alpha=0.3, axis='y')
    
    # R² scores
    ax2.bar(x - width/2, df['pure_llm_mean_r2'], width, 
            label='Pure LLM', color='orange', alpha=0.8)
    ax2.bar(x + width/2, df['hybrid_v40_mean_r2'], width, 
            label='HypatiaX', color='blue', alpha=0.8)
    
    ax2.set_xlabel('Domain')
    ax2.set_ylabel('Mean R²')
    ax2.set_title('Prediction Accuracy by Domain')
    ax2.set_xticks(x)
    ax2.set_xticklabels(df['domain'], rotation=45, ha='right')
    ax2.legend()
    ax2.set_ylim([0, 1.05])
    ax2.grid(True, alpha=0.3, axis='y')
    
    plt.tight_layout()
    plt.savefig(output_dir / 'figure2_domain_comparison.pdf', bbox_inches='tight')
    plt.savefig(output_dir / 'figure2_domain_comparison.png', bbox_inches='tight', dpi=300)
    plt.close()
    
    print("✓ Figure 2: Domain comparison")

def figure3_validation_breakdown():
    """Figure 3: Multi-layer validation breakdown"""
    df = pd.read_csv('figure3_validation_breakdown.csv')
    
    fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(10, 4))
    
    # Waterfall chart - individual layer contributions
    colors = ['#1f77b4', '#ff7f0e', '#2ca02c', '#d62728']
    ax1.bar(df['layer_name'], df['percentage'], color=colors, alpha=0.8)
    ax1.set_xlabel('Validation Layer')
    ax1.set_ylabel('Errors Caught (%)')
    ax1.set_title('Error Detection by Validation Layer')
    ax1.set_xticklabels(df['layer_name'], rotation=45, ha='right')
    ax1.grid(True, alpha=0.3, axis='y')
    
    # Add percentage labels on bars
    for i, (layer, pct) in enumerate(zip(df['layer_name'], df['percentage'])):
        ax1.text(i, pct + 1, f'{pct:.1f}%', ha='center', va='bottom', fontsize=8)
    
    # Cumulative detection
    ax2.plot(df['layer'], df['cumulative_percentage'], 'o-', 
             linewidth=2, markersize=8, color='#1f77b4')
    ax2.fill_between(df['layer'], 0, df['cumulative_percentage'], alpha=0.3)
    ax2.set_xlabel('Validation Layer')
    ax2.set_ylabel('Cumulative Errors Caught (%)')
    ax2.set_title('Cumulative Error Detection (100% Coverage)')
    ax2.set_xticks(df['layer'])
    ax2.set_xticklabels([f"L{i}" for i in df['layer']])
    ax2.set_ylim([0, 105])
    ax2.grid(True, alpha=0.3)
    ax2.axhline(y=100, color='red', linestyle='--', linewidth=1, alpha=0.5, label='100% Coverage')
    ax2.legend()
    
    plt.tight_layout()
    plt.savefig(output_dir / 'figure3_validation.pdf', bbox_inches='tight')
    plt.savefig(output_dir / 'figure3_validation.png', bbox_inches='tight', dpi=300)
    plt.close()
    
    print("✓ Figure 3: Validation breakdown")

def figure4_extrapolation_error_heatmap():
    """Figure 4: Extrapolation error heatmap across equations and ranges"""
    df = pd.read_csv('figure_5systems_comparison.csv')
    
    # Prepare data for heatmap
    nn_data = df[df['method'] == 'Neural Network']
    hybrid_data = df[df['method'] == 'Hybrid v40']
    
    # Get common equations (present in both datasets)
    nn_equations = set(nn_data['equation'].unique())
    hybrid_equations = set(hybrid_data['equation'].unique())
    equations = list(nn_equations & hybrid_equations)  # Intersection
    
    ranges = ['Near (1.5×)', 'Medium (2×)', 'Far (3×)']
    
    # Create error matrices
    nn_errors = np.zeros((len(equations), 3))
    hybrid_errors = np.zeros((len(equations), 3))
    
    for i, eq in enumerate(equations):
        nn_row = nn_data[nn_data['equation'] == eq].iloc[0]
        hybrid_row = hybrid_data[hybrid_data['equation'] == eq].iloc[0]
        
        nn_errors[i] = [nn_row['extrap_near_error'], 
                        nn_row['extrap_medium_error'], 
                        nn_row['extrap_far_error']]
        hybrid_errors[i] = [hybrid_row['extrap_near_error'], 
                           hybrid_row['extrap_medium_error'], 
                           hybrid_row['extrap_far_error']]
    
    # Plot heatmaps
    fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(12, 6))
    
    # Neural Network errors (log scale for visibility)
    im1 = ax1.imshow(np.log10(nn_errors + 1), cmap='YlOrRd', aspect='auto')
    ax1.set_xticks(np.arange(len(ranges)))
    ax1.set_yticks(np.arange(len(equations)))
    ax1.set_xticklabels(ranges)
    ax1.set_yticklabels(equations, fontsize=8)
    ax1.set_title('Neural Network Extrapolation Error (log₁₀ scale)')
    plt.colorbar(im1, ax=ax1, label='log₁₀(Error %)')
    
    # HypatiaX errors (should be all zeros)
    im2 = ax2.imshow(hybrid_errors, cmap='Greens_r', aspect='auto', vmin=0, vmax=1)
    ax2.set_xticks(np.arange(len(ranges)))
    ax2.set_yticks(np.arange(len(equations)))
    ax2.set_xticklabels(ranges)
    ax2.set_yticklabels(equations, fontsize=8)
    ax2.set_title('HypatiaX Extrapolation Error (0% across all ranges)')
    plt.colorbar(im2, ax=ax2, label='Error %')
    
    plt.tight_layout()
    plt.savefig(output_dir / 'figure4_extrapolation_heatmap.pdf', bbox_inches='tight')
    plt.savefig(output_dir / 'figure4_extrapolation_heatmap.png', bbox_inches='tight', dpi=300)
    plt.close()
    
    print("✓ Figure 4: Extrapolation error heatmap")

def figure5_method_comparison():
    """Figure 5: Overall method comparison (success vs time)"""
    df = pd.read_csv('figure5_method_comparison.csv')
    
    fig, ax = plt.subplots(figsize=(8, 6))
    
    # Scatter plot with different markers
    markers = ['o', 's', '^', 'D', '*']
    colors = ['orange', 'red', 'green', 'purple', 'blue']
    
    for i, (idx, row) in enumerate(df.iterrows()):
        ax.scatter(row['mean_time_sec'], row['success_rate'], 
                  s=200, marker=markers[i], color=colors[i], 
                  alpha=0.7, edgecolors='black', linewidth=1.5,
                  label=row['method'])
    
    # Add text labels
    for idx, row in df.iterrows():
        offset_x = 50 if row['method'] != 'Pure PySR' else -200
        offset_y = 3 if row['method'] != 'Neural Network' else -5
        ax.annotate(row['method'], 
                   xy=(row['mean_time_sec'], row['success_rate']),
                   xytext=(offset_x, offset_y), 
                   textcoords='offset points',
                   fontsize=9, ha='left')
    
    ax.set_xlabel('Mean Discovery Time (seconds)', fontsize=11)
    ax.set_ylabel('Success Rate (%)', fontsize=11)
    ax.set_title('Method Comparison: Success Rate vs. Discovery Time', fontsize=12)
    ax.set_xscale('log')
    ax.grid(True, alpha=0.3, which='both')
    ax.set_xlim([5, 3000])
    ax.set_ylim([55, 105])
    
    # Add Pareto frontier annotation
    ax.axhline(y=95, color='green', linestyle='--', alpha=0.3, linewidth=1)
    ax.axvline(x=400, color='green', linestyle='--', alpha=0.3, linewidth=1)
    ax.text(400, 97, 'HypatiaX: Optimal\nbalance', fontsize=8, 
            ha='center', bbox=dict(boxstyle='round', facecolor='wheat', alpha=0.5))
    
    plt.tight_layout()
    plt.savefig(output_dir / 'figure5_method_comparison.pdf', bbox_inches='tight')
    plt.savefig(output_dir / 'figure5_method_comparison.png', bbox_inches='tight', dpi=300)
    plt.close()
    
    print("✓ Figure 5: Method comparison")

def figure6_timing_comparison():
    """Figure 6: Detailed timing comparison with speedup factors"""
    df = pd.read_csv('figure_timing_comparison.csv')
    
    fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(11, 4))
    
    # Timing comparison
    methods = df['method']
    times = df['mean_time_sec']
    colors_timing = ['orange', 'red', 'green', 'blue', 'purple']
    
    bars1 = ax1.barh(methods, times, color=colors_timing, alpha=0.8, edgecolor='black')
    ax1.set_xlabel('Mean Time (seconds, log scale)')
    ax1.set_title('Discovery Time by Method')
    ax1.set_xscale('log')
    ax1.grid(True, alpha=0.3, axis='x')
    
    # Add time labels
    for i, (method, time) in enumerate(zip(methods, times)):
        ax1.text(time * 1.2, i, f'{time:.0f}s', va='center', fontsize=9)
    
    # Speedup vs HypatiaX
    speedups = pd.to_numeric(df['speedup_vs_hybrid'].str.replace('x', ''), errors='coerce')
    colors_speedup = ['lightcoral' if x < 1 else 'lightgreen' for x in speedups]
    
    bars2 = ax2.barh(methods, speedups, color=colors_speedup, alpha=0.8, edgecolor='black')
    ax2.set_xlabel('Speedup vs. HypatiaX')
    ax2.set_title('Relative Speed (>1 = faster, <1 = slower)')
    ax2.axvline(x=1, color='black', linestyle='--', linewidth=2, label='HypatiaX baseline')
    ax2.grid(True, alpha=0.3, axis='x')
    ax2.legend()
    
    # Add speedup labels
    for i, (method, speedup) in enumerate(zip(methods, speedups)):
        label = f'{speedup:.1f}×' if speedup >= 1 else f'{speedup:.2f}×'
        offset = speedup * 0.1 if speedup >= 1 else speedup * 1.5
        ax2.text(speedup + offset, i, label, va='center', fontsize=9)
    
    plt.tight_layout()
    plt.savefig(output_dir / 'figure6_timing.pdf', bbox_inches='tight')
    plt.savefig(output_dir / 'figure6_timing.png', bbox_inches='tight', dpi=300)
    plt.close()
    
    print("✓ Figure 6: Timing comparison")

def figure7_architecture_diagram():
    """Figure 7: HypatiaX architecture diagram (to be created with TikZ in LaTeX)"""
    print("✓ Figure 7: Architecture diagram (created in LaTeX)")
    # This will be created as a TikZ diagram in the LaTeX document

def table1_extrapolation_summary():
    """Table 1: Extrapolation error summary"""
    df = pd.read_csv('figure_5systems_comparison.csv')
    
    # Get common equations
    nn_equations = set(df[df['method'] == 'Neural Network']['equation'].unique())
    hybrid_equations = set(df[df['method'] == 'Hybrid v40']['equation'].unique())
    common_equations = list(nn_equations & hybrid_equations)
    
    # Create summary table
    summary = []
    for equation in common_equations:
        nn_row = df[(df['equation'] == equation) & (df['method'] == 'Neural Network')].iloc[0]
        hybrid_row = df[(df['equation'] == equation) & (df['method'] == 'Hybrid v40')].iloc[0]
        
        summary.append({
            'Equation': equation.replace('_', ' ').title(),
            'NN Train R²': f"{nn_row['training_r2']:.3f}",
            'NN Extrap Error (%)': f"{nn_row['mean_extrap_error']:.1f}",
            'HypatiaX Train R²': f"{hybrid_row['training_r2']:.3f}",
            'HypatiaX Extrap Error (%)': f"{hybrid_row['mean_extrap_error']:.1f}",
        })
    
    summary_df = pd.DataFrame(summary)
    
    # Save as CSV for LaTeX import
    summary_df.to_csv(output_dir / 'table1_extrapolation_summary.csv', index=False)
    print("✓ Table 1: Extrapolation summary saved")

def main():
    """Generate all figures and tables"""
    print("Generating HypatiaX manuscript figures...\n")
    
    figure1_arrhenius_extrapolation()
    figure2_domain_comparison()
    figure3_validation_breakdown()
    figure4_extrapolation_error_heatmap()
    figure5_method_comparison()
    figure6_timing_comparison()
    figure7_architecture_diagram()
    table1_extrapolation_summary()
    
    print(f"\n✓ All figures saved to {output_dir}/")
    print("\nNext steps:")
    print("1. Compile LaTeX document: pdflatex hypatiax_manuscript.tex")
    print("2. Run bibtex: bibtex hypatiax_manuscript")
    print("3. Compile again: pdflatex hypatiax_manuscript.tex (twice)")

if __name__ == '__main__':
    main()
