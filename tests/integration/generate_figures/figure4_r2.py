#!/usr/bin/env python3
"""
Figure 4: R² vs Complexity Scatter Plot - ACTUAL EXPERIMENTAL DATA
===================================================================

Uses real results from:
- standalone_real_methods_20260116_003311.json (15 core tests)
- all_domains_extrap_v4_20260120_223747.json (extrapolation data)

Complexity metric: Expression tree depth/operator count
"""

import matplotlib.pyplot as plt
import numpy as np
from matplotlib.patches import Patch
import re

# Publication-quality settings
plt.rcParams.update({
    'font.family': 'serif',
    'font.size': 11,
    'axes.labelsize': 12,
    'axes.titlesize': 13,
    'xtick.labelsize': 10,
    'ytick.labelsize': 10,
    'legend.fontsize': 9,
    'figure.titlesize': 14,
    'text.usetex': False,
})


def estimate_complexity(formula_str):
    """
    Estimate formula complexity from string representation.
    
    Complexity = number of operators + nesting depth
    """
    if not formula_str or formula_str == "Neural Network" or "Black box" in formula_str:
        return 0  # NN is black box
    
    if formula_str == "DISCOVERY_FAILED":
        return 0
    
    # Count operators
    operators = ['+', '-', '*', '/', '**', 'exp', 'log', 'sqrt', 'log10']
    complexity = 0
    
    for op in operators:
        complexity += formula_str.count(op)
    
    # Add penalty for nesting (count parentheses)
    complexity += formula_str.count('(') * 0.5
    
    return max(1, int(complexity))


def load_actual_data():
    """Load data from actual experimental results"""
    
    # REAL DATA FROM: standalone_real_methods_20260116_003311.json
    tests_data = [
        # Format: (name, domain, r2_llm, r2_nn, r2_hybrid, formula_llm, formula_hybrid)
        
        # Chemistry
        ("Arrhenius", "chemistry", 1.0000, 0.9996, 0.9989, 
         "k = A × exp(-Ea/(R × T))", 
         "(((((T + -331.33148) * (T + -286.26013)) * ((T + -616.7621) + T)) * 5.900765e-8)"),
        
        ("Henderson-Hasselbalch", "chemistry", 1.0000, 0.9985, 0.9989,
         "pH = pKa + log₁₀([A⁻]/[HA])",
         "((38.588684 + ((7.5455556 / (HA + 1.1689923)) + ((0.17864262 / HA) + A_minus)))"),
        
        ("Rate Law", "chemistry", 1.0000, 0.9994, 1.0000,
         "rate = k × [A]^m × [B]^n",
         "(B_conc * 0.5) * (A_conc * A_conc)"),
        
        # Biology
        ("Allometric Scaling", "biology", 1.0000, 0.9999, 1.0000,
         "Y = a × M^b",
         "(((M * -0.9110226) / (M + 60.027668)) * M) + ((M * 1.6206156) - (-5.7254066"),
        
        ("Michaelis-Menten", "biology", 1.0000, 0.9997, 0.0000,
         "v = (Vmax × [S]) / (Km + [S])",
         "DISCOVERY_FAILED"),
        
        ("Logistic Growth", "biology", 1.0000, 0.9999, 0.0000,
         "dN/dt = r*N*(1-N/K)",
         "DISCOVERY_FAILED"),
        
        # Physics
        ("Kinetic Energy", "physics", 1.0000, 0.9998, 1.0000,
         "KE = 0.5 × m × v²",
         "v * ((m * v) * 0.5)"),
        
        ("Gravitational Force", "physics", 1.0000, 0.2448, -0.0257,
         "F = G × m₁ × m₂ / r²",
         "-0.22981945"),
        
        ("Ideal Gas Law", "physics", 1.0000, 0.7905, 1.0000,
         "P = nRT/V",
         "((T - -2.145704e-5) * (8.313999 / V)) * n"),
        
        # DeFi AMM
        ("Impermanent Loss", "defi", 1.0000, 0.9965, 0.9992,
         "IL = 2*sqrt(price_ratio)/(1+price_ratio) - 1",
         "((((-0.10139638 - (price_ratio * (price_ratio + price_ratio))) / price_ratio)"),
        
        ("Price Impact", "defi", 1.0000, 0.9991, 1.0000,
         "impact = swap / (reserve + swap)",
         "swap / (swap + reserve)"),
        
        ("Constant Product", "defi", 1.0000, 0.9964, 1.0000,
         "y = k/x where k = 1,000,000",
         "480.95236 / (x / 2079.208)"),
        
        # DeFi Risk
        ("VaR 95%", "defi", 1.0000, 0.9999, 1.0000,
         "VaR = portfolio × volatility × 1.645",
         "portfolio * (volatility * 1.645)"),
        
        ("Liquidation Long", "defi", 1.0000, 0.9999, 1.0000,
         "liquidation_price = entry_price × (1 - 1/(leverage × 0.8))",
         "entry_price - (entry_price * (1.25 / leverage))"),
        
        ("Portfolio VaR", "defi", 1.0000, 0.9990, 0.9949,
         "Portfolio VaR = √(var1² + var2² + 2ρ·var1·var2)",
         "(((((rho * var1) + 18891.637) * (var2 / (var1 + 15128.247))) + var1) * 1.0489613"),
    ]
    
    results = []
    for name, domain, r2_llm, r2_nn, r2_hybrid, formula_llm, formula_hybrid in tests_data:
        complexity_llm = estimate_complexity(formula_llm)
        complexity_hybrid = estimate_complexity(formula_hybrid) if r2_hybrid > 0 else 0
        
        results.append({
            'name': name,
            'domain': domain,
            'r2_llm': r2_llm,
            'r2_nn': r2_nn,
            'r2_hybrid': r2_hybrid if r2_hybrid > 0 else None,
            'complexity_llm': complexity_llm,
            'complexity_hybrid': complexity_hybrid,
            'formula_llm': formula_llm,
            'formula_hybrid': formula_hybrid
        })
    
    return results


def create_main_scatter():
    """Main scatter plot with actual experimental data"""
    
    data = load_actual_data()
    
    fig, ax = plt.subplots(figsize=(12, 8))
    
    # Domain colors
    domain_colors = {
        'chemistry': '#2E86AB',
        'biology': '#A23B72', 
        'physics': '#F18F01',
        'defi': '#C73E1D'
    }
    
    # Plot Pure LLM (circles)
    for item in data:
        color = domain_colors[item['domain']]
        ax.scatter(item['complexity_llm'], item['r2_llm'],
                  marker='o', s=150, c=color, alpha=0.8,
                  edgecolors='black', linewidth=1.5, zorder=3)
    
    # Plot Neural Network (squares)
    for item in data:
        color = domain_colors[item['domain']]
        # NN has fixed complexity of 0 (black box)
        ax.scatter(0, item['r2_nn'],
                  marker='s', s=150, c=color, alpha=0.8,
                  edgecolors='black', linewidth=1.5, zorder=3)
    
    # Plot Hybrid v40 (triangles)
    for item in data:
        if item['r2_hybrid'] is not None:
            color = domain_colors[item['domain']]
            ax.scatter(item['complexity_hybrid'], item['r2_hybrid'],
                      marker='^', s=150, c=color, alpha=0.8,
                      edgecolors='black', linewidth=1.5, zorder=3)
    
    # Annotate notable failures
    for item in data:
        if item['name'] == "Gravitational Force":
            # NN failure
            ax.annotate('NN Failure\n(Grav. Force)', 
                       xy=(0, item['r2_nn']), xytext=(3, 0.35),
                       arrowprops=dict(arrowstyle='->', color='red', lw=2),
                       fontsize=10, color='red', fontweight='bold',
                       bbox=dict(boxstyle='round,pad=0.4', facecolor='yellow', alpha=0.8))
            
            # Hybrid failure
            if item['r2_hybrid'] is not None and item['r2_hybrid'] < 0:
                ax.annotate('Hybrid Failure', 
                           xy=(item['complexity_hybrid'], item['r2_hybrid']), 
                           xytext=(5, -0.05),
                           arrowprops=dict(arrowstyle='->', color='red', lw=2),
                           fontsize=9, color='red', fontweight='bold')
        
        if item['name'] == "Michaelis-Menten" and item['r2_hybrid'] is None:
            ax.annotate('Hybrid Failed\n(M-M, Log. Growth)', 
                       xy=(7, 0.05), xytext=(9, 0.15),
                       fontsize=9, color='orange', fontweight='bold',
                       bbox=dict(boxstyle='round,pad=0.3', facecolor='lightyellow', alpha=0.8))
    
    # Reference lines
    ax.axhline(y=0.99, color='green', linestyle='--', linewidth=2, alpha=0.6,
              label='Excellent (R² ≥ 0.99)', zorder=1)
    ax.axhline(y=0.95, color='orange', linestyle='--', linewidth=2, alpha=0.6,
              label='Good (R² ≥ 0.95)', zorder=1)
    
    # Pareto frontier for Pure LLM (all perfect at varying complexity)
    llm_points = [(item['complexity_llm'], item['r2_llm']) for item in data]
    llm_points.sort()
    if llm_points:
        x_vals, y_vals = zip(*llm_points)
        ax.plot(x_vals, y_vals, 'go--', linewidth=2, alpha=0.5, 
               label='LLM Pareto (all R²=1.0)', zorder=2)
    
    # Labels and styling
    ax.set_xlabel('Formula Complexity (operator count + nesting)', 
                 fontweight='bold', fontsize=13)
    ax.set_ylabel('R² Score', fontweight='bold', fontsize=13)
    ax.set_title('Figure 4: Accuracy vs Complexity Trade-off\n' + 
                'Real Experimental Results (15 Ground Truth Tests)',
                fontweight='bold', fontsize=15, pad=20)
    
    ax.set_xlim(-1, 20)
    ax.set_ylim(-0.15, 1.05)
    
    ax.grid(True, alpha=0.3, linestyle='--', zorder=0)
    ax.set_axisbelow(True)
    
    # Create custom legend
    # Method markers
    method_handles = [
        plt.Line2D([0], [0], marker='o', color='w', markerfacecolor='gray', 
                  markersize=12, label='Pure LLM (Symbolic)', 
                  markeredgecolor='black', markeredgewidth=1.5),
        plt.Line2D([0], [0], marker='s', color='w', markerfacecolor='gray',
                  markersize=12, label='Neural Network (Black Box)', 
                  markeredgecolor='black', markeredgewidth=1.5),
        plt.Line2D([0], [0], marker='^', color='w', markerfacecolor='gray',
                  markersize=12, label='Hybrid v40 (SR)', 
                  markeredgecolor='black', markeredgewidth=1.5),
    ]
    
    # Domain colors
    domain_handles = [
        Patch(facecolor=domain_colors[d], label=d.capitalize(), 
              edgecolor='black', linewidth=1.2)
        for d in sorted(domain_colors.keys())
    ]
    
    # Add reference lines to method legend
    method_handles.append(plt.Line2D([0], [0], color='green', linestyle='--', 
                                    linewidth=2, label='Excellent (R² ≥ 0.99)'))
    method_handles.append(plt.Line2D([0], [0], color='orange', linestyle='--', 
                                    linewidth=2, label='Good (R² ≥ 0.95)'))
    
    # Two legends
    legend1 = ax.legend(handles=method_handles, loc='lower left', 
                       title='Method & Thresholds', framealpha=0.95, 
                       fontsize=10, title_fontsize=11)
    ax.add_artist(legend1)
    
    ax.legend(handles=domain_handles, loc='lower right',
             title='Domain', framealpha=0.95, fontsize=10, title_fontsize=11)
    
    # Add text box with key insights
    textstr = 'Key Findings:\n' + \
              '• Pure LLM: 100% R²=1.0, varying complexity\n' + \
              '• Neural Net: 86.7% R²≥0.95, black box\n' + \
              '• Hybrid v40: 80% R²≥0.95, symbolic\n' + \
              '• Physics: Most challenging domain'
    
    props = dict(boxstyle='round', facecolor='wheat', alpha=0.8)
    ax.text(0.02, 0.65, textstr, transform=ax.transAxes, fontsize=9,
           verticalalignment='top', bbox=props)
    
    plt.tight_layout()
    
    # Save
    plt.savefig('figure4_real_data.pdf', dpi=300, bbox_inches='tight')
    plt.savefig('figure4_real_data.png', dpi=300, bbox_inches='tight')
    print("✅ Figure 4 saved: figure4_real_data.pdf/.png")
    
    plt.show()


def create_domain_breakdown():
    """Domain-specific analysis panels"""
    
    data = load_actual_data()
    
    fig, axes = plt.subplots(2, 2, figsize=(14, 10))
    axes = axes.flatten()
    
    domains = ['chemistry', 'biology', 'physics', 'defi']
    domain_colors = {
        'chemistry': '#2E86AB',
        'biology': '#A23B72', 
        'physics': '#F18F01',
        'defi': '#C73E1D'
    }
    
    for idx, domain in enumerate(domains):
        ax = axes[idx]
        domain_data = [d for d in data if d['domain'] == domain]
        
        # Prepare data for grouped bar chart
        test_names = [d['name'].replace(' ', '\n') for d in domain_data]
        r2_llm = [d['r2_llm'] for d in domain_data]
        r2_nn = [d['r2_nn'] for d in domain_data]
        r2_hybrid = [d['r2_hybrid'] if d['r2_hybrid'] is not None else 0 
                     for d in domain_data]
        
        x = np.arange(len(test_names))
        width = 0.25
        
        ax.bar(x - width, r2_llm, width, label='Pure LLM', 
              color='#06A77D', alpha=0.8, edgecolor='black', linewidth=1.2)
        ax.bar(x, r2_nn, width, label='Neural Net', 
              color='#457B9D', alpha=0.8, edgecolor='black', linewidth=1.2)
        ax.bar(x + width, r2_hybrid, width, label='Hybrid v40', 
              color='#E63946', alpha=0.8, edgecolor='black', linewidth=1.2)
        
        ax.axhline(y=0.99, color='green', linestyle='--', linewidth=1.5, alpha=0.5)
        ax.axhline(y=0.95, color='orange', linestyle='--', linewidth=1.5, alpha=0.5)
        
        ax.set_ylabel('R² Score', fontweight='bold')
        ax.set_title(f'{domain.capitalize()}', fontweight='bold', 
                    color=domain_colors[domain], fontsize=13)
        ax.set_xticks(x)
        ax.set_xticklabels(test_names, fontsize=8)
        ax.set_ylim(-0.1, 1.05)
        ax.grid(axis='y', alpha=0.3, linestyle='--')
        ax.set_axisbelow(True)
        
        if idx == 0:
            ax.legend(loc='lower right', fontsize=9)
    
    plt.suptitle('Figure 4B: Domain-Specific Performance Breakdown', 
                fontweight='bold', fontsize=15, y=1.00)
    plt.tight_layout()
    
    plt.savefig('figure4b_domain_breakdown.pdf', dpi=300, bbox_inches='tight')
    plt.savefig('figure4b_domain_breakdown.png', dpi=300, bbox_inches='tight')
    print("✅ Figure 4B saved: figure4b_domain_breakdown.pdf/.png")
    
    plt.show()


def print_summary_statistics():
    """Print summary table of results"""
    
    data = load_actual_data()
    
    print("\n" + "="*80)
    print("SUMMARY STATISTICS - ACTUAL EXPERIMENTAL DATA")
    print("="*80)
    
    methods = ['Pure LLM', 'Neural Network', 'Hybrid v40']
    
    for method in methods:
        print(f"\n{method}:")
        print("-" * 60)
        
        if method == 'Pure LLM':
            r2_values = [d['r2_llm'] for d in data]
            complexities = [d['complexity_llm'] for d in data]
        elif method == 'Neural Network':
            r2_values = [d['r2_nn'] for d in data]
            complexities = [0] * len(data)  # Black box
        else:  # Hybrid v40
            r2_values = [d['r2_hybrid'] for d in data if d['r2_hybrid'] is not None]
            complexities = [d['complexity_hybrid'] for d in data 
                          if d['r2_hybrid'] is not None and d['r2_hybrid'] > 0]
        
        successful = [r for r in r2_values if r >= 0.95]
        excellent = [r for r in r2_values if r >= 0.99]
        
        print(f"  Success Rate (R² ≥ 0.95): {len(successful)}/{len(r2_values)} " + 
              f"({100*len(successful)/len(r2_values):.1f}%)")
        print(f"  Excellent Rate (R² ≥ 0.99): {len(excellent)}/{len(r2_values)} " + 
              f"({100*len(excellent)/len(r2_values):.1f}%)")
        print(f"  Mean R²: {np.mean(r2_values):.4f}")
        print(f"  Median R²: {np.median(r2_values):.4f}")
        print(f"  Min R²: {np.min(r2_values):.4f}")
        
        if method != 'Neural Network':
            print(f"  Mean Complexity: {np.mean(complexities):.1f}")
            print(f"  Complexity Range: {np.min(complexities):.0f} - {np.max(complexities):.0f}")
    
    print("\n" + "="*80)


if __name__ == "__main__":
    print("Generating Figure 4 with ACTUAL EXPERIMENTAL DATA\n")
    
    # Print summary stats
    print_summary_statistics()
    
    # Generate figures
    print("\nGenerating scatter plot...")
    create_main_scatter()
    
    print("\nGenerating domain breakdown...")
    create_domain_breakdown()
    
    print("\n✅ All figures generated successfully!")
    print("\nOutput files:")
    print("  • figure4_real_data.pdf (main scatter)")
    print("  • figure4_real_data.png")
    print("  • figure4b_domain_breakdown.pdf (domain analysis)")
    print("  • figure4b_domain_breakdown.png")
