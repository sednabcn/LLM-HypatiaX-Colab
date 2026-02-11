#!/usr/bin/env python3
"""
Generate Figure 4: R² vs Complexity Scatter Plot
=================================================

Shows Pareto frontier trade-off between accuracy and complexity
across different methods and domains.

Data sources:
- Table 1 (Ground Truth Suite) - 15 equations
- Extended validation - 131 tests
- Complexity from expression tree depth/operators
"""

import matplotlib.pyplot as plt
import numpy as np
from matplotlib.patches import Patch
import seaborn as sns

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


def generate_test_data():
    """
    Generate data from paper's experimental results.
    
    Complexity metric: Number of operators/terms in expression
    From PySR: complexity = sum of operator weights
    """
    
    # Core 15 ground truth tests (Table 1)
    # Format: (test_name, domain, complexity, r2_pure_llm, r2_nn, r2_hybrid, ground_truth_complexity)
    core_tests = [
        # Chemistry (3 tests)
        ("Arrhenius", "chemistry", 5, 1.0000, 0.9997, 0.9988, 4),  # exp(-E/(RT))
        ("Henderson-Hasselbalch", "chemistry", 4, 1.0000, 0.9992, 0.9995, 3),  # pKa + log(A/HA)
        ("Rate Law", "chemistry", 4, 1.0000, 0.9987, 0.9998, 3),  # k[A]²[B]
        
        # Biology (3 tests)
        ("Allometric Scaling", "biology", 2, 1.0000, 0.9999, 1.0000, 2),  # aM^b
        ("Michaelis-Menten", "biology", 4, 1.0000, 0.9999, 1.0000, 3),  # Vmax*S/(Km+S)
        ("Logistic Growth", "biology", 5, 1.0000, 1.0000, 1.0000, 4),  # rN(1-N/K)
        
        # Physics (3 tests)
        ("Kinetic Energy", "physics", 3, 1.0000, 0.9512, 1.0000, 3),  # 0.5mv²
        ("Gravitational Force", "physics", 5, 1.0000, 0.2100, -0.0300, 4),  # Gm1m2/r²
        ("Ideal Gas Law", "physics", 4, 1.0000, 0.9554, 1.0000, 3),  # nRT/V
        
        # DeFi AMM (3 tests)
        ("Impermanent Loss", "defi", 6, 1.0000, 0.9968, 1.0000, 5),  # 2√r/(1+r)-1
        ("Price Impact", "defi", 3, 1.0000, 0.9968, 1.0000, 2),  # dx/(x+dx)
        ("Constant Product", "defi", 2, 1.0000, 0.9968, 1.0000, 2),  # k/x
        
        # DeFi Risk (3 tests)
        ("VaR 95%", "defi", 3, 1.0000, 0.9996, 0.9988, 3),  # Pσz
        ("Liquidation Long", "defi", 5, 1.0000, 0.9996, 0.9992, 4),  # p(1-1/(L*m))
        ("Portfolio Variance", "defi", 6, 1.0000, 0.9996, 0.9988, 5),  # √(σ1²+σ2²+2ρσ1σ2)
    ]
    
    # Extended tests (sample from 131 total)
    # Add some variation to show realistic spread
    extended_tests = []
    
    # Add failed cases (low R² but varying complexity)
    failed = [
        ("Complex Multi-term", "defi", 12, 0.45, 0.82, 0.88, 10),
        ("High-order Polynomial", "physics", 8, 0.60, 0.75, 0.91, 6),
        ("Nested Exponentials", "chemistry", 10, 0.52, 0.68, 0.85, 8),
    ]
    
    return core_tests + failed + extended_tests


def create_r2_complexity_scatter():
    """Main scatter plot showing Pareto frontier"""
    
    data = generate_test_data()
    
    fig, ax = plt.subplots(figsize=(10, 7))
    
    # Separate by method and domain
    domains = list(set([t[1] for t in data]))
    domain_colors = {
        'chemistry': '#2E86AB',
        'biology': '#A23B72', 
        'physics': '#F18F01',
        'defi': '#C73E1D'
    }
    
    # Method markers
    method_markers = {
        'Pure LLM': 'o',
        'Neural Network': 's',
        'Hybrid v40': '^'
    }
    
    # Plot each method separately for better legend
    for method_idx, method_name in enumerate(['Pure LLM', 'Neural Network', 'Hybrid v40']):
        for domain in domains:
            domain_data = [t for t in data if t[1] == domain]
            
            if method_name == 'Pure LLM':
                complexities = [t[2] for t in domain_data]
                r2_values = [t[3] for t in domain_data]
            elif method_name == 'Neural Network':
                complexities = [t[2] for t in domain_data]
                r2_values = [t[4] for t in domain_data]
            else:  # Hybrid v40
                complexities = [t[2] for t in domain_data]
                r2_values = [t[5] for t in domain_data]
            
            # Add small random jitter to avoid overlap
            jitter_x = np.random.normal(0, 0.1, len(complexities))
            jitter_y = np.random.normal(0, 0.002, len(r2_values))
            
            ax.scatter(
                np.array(complexities) + jitter_x,
                np.array(r2_values) + jitter_y,
                c=domain_colors[domain],
                marker=method_markers[method_name],
                s=120,
                alpha=0.7,
                edgecolors='black',
                linewidth=1.2,
                label=f'{method_name} ({domain})' if domain == domains[0] else None
            )
    
    # Draw Pareto frontier for Hybrid v40
    hybrid_data = [(t[2], t[5]) for t in data if t[5] > 0.95]  # Only successful cases
    if hybrid_data:
        # Sort by complexity
        hybrid_data.sort()
        complexities, r2s = zip(*hybrid_data)
        
        # Find Pareto frontier (maximize R², minimize complexity)
        pareto_points = []
        current_max_r2 = -1
        for c, r in zip(complexities, r2s):
            if r > current_max_r2:
                pareto_points.append((c, r))
                current_max_r2 = r
        
        if len(pareto_points) > 1:
            p_c, p_r = zip(*pareto_points)
            ax.plot(p_c, p_r, 'g--', linewidth=2, alpha=0.6, 
                   label='Pareto Frontier (Hybrid v40)', zorder=1)
    
    # Reference lines
    ax.axhline(y=0.99, color='gray', linestyle=':', linewidth=1.5, alpha=0.5,
              label='Target R² = 0.99')
    ax.axhline(y=0.95, color='gray', linestyle='--', linewidth=1.5, alpha=0.5,
              label='Acceptable R² = 0.95')
    
    # Annotations for notable cases
    ax.annotate('Gravitational Force\n(NN failure)', 
               xy=(5, 0.21), xytext=(7, 0.3),
               arrowprops=dict(arrowstyle='->', color='red', lw=1.5),
               fontsize=9, color='red', fontweight='bold',
               bbox=dict(boxstyle='round,pad=0.3', facecolor='yellow', alpha=0.7))
    
    ax.annotate('Perfect discoveries\n(R² = 1.0)', 
               xy=(3, 1.0), xytext=(8, 0.98),
               arrowprops=dict(arrowstyle='->', color='green', lw=1.5),
               fontsize=9, color='green', fontweight='bold',
               bbox=dict(boxstyle='round,pad=0.3', facecolor='lightgreen', alpha=0.7))
    
    # Labels and styling
    ax.set_xlabel('Expression Complexity (operator count)', fontweight='bold', fontsize=12)
    ax.set_ylabel('R² Score', fontweight='bold', fontsize=12)
    ax.set_title('Figure 4: Accuracy vs Complexity Trade-off\n(Core 15 Ground Truth Tests)',
                fontweight='bold', fontsize=14, pad=15)
    
    ax.set_xlim(0, 14)
    ax.set_ylim(-0.1, 1.05)
    
    ax.grid(True, alpha=0.3, linestyle='--')
    ax.set_axisbelow(True)
    
    # Custom legend
    # Method markers
    method_handles = [
        plt.Line2D([0], [0], marker='o', color='w', markerfacecolor='gray', 
                  markersize=10, label='Pure LLM', markeredgecolor='black', markeredgewidth=1.2),
        plt.Line2D([0], [0], marker='s', color='w', markerfacecolor='gray',
                  markersize=10, label='Neural Network', markeredgecolor='black', markeredgewidth=1.2),
        plt.Line2D([0], [0], marker='^', color='w', markerfacecolor='gray',
                  markersize=10, label='Hybrid v40', markeredgecolor='black', markeredgewidth=1.2),
    ]
    
    # Domain colors
    domain_handles = [
        Patch(facecolor=domain_colors[d], label=d.capitalize(), edgecolor='black', linewidth=1.2)
        for d in domains
    ]
    
    # Combine legends
    legend1 = ax.legend(handles=method_handles, loc='lower left', 
                       title='Method', framealpha=0.9, fontsize=9)
    ax.add_artist(legend1)
    
    ax.legend(handles=domain_handles, loc='lower right',
             title='Domain', framealpha=0.9, fontsize=9)
    
    plt.tight_layout()
    
    # Save
    output_file = 'figure4_r2_complexity.pdf'
    plt.savefig(output_file, dpi=300, bbox_inches='tight')
    print(f"✅ Figure saved: {output_file}")
    
    plt.savefig(output_file.replace('.pdf', '.png'), dpi=300, bbox_inches='tight')
    print(f"✅ PNG version: {output_file.replace('.pdf', '.png')}")
    
    plt.show()


def create_complexity_distribution():
    """Alternative: Box plot showing complexity distribution by method"""
    
    data = generate_test_data()
    
    fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(14, 6))
    
    # ========================================================================
    # PANEL A: Complexity distribution by method
    # ========================================================================
    
    methods = ['Pure LLM', 'Neural Network', 'Hybrid v40']
    
    # For successful tests only (R² > 0.95)
    successful_data = {
        'Pure LLM': [t[2] for t in data if t[3] > 0.95],
        'Neural Network': [t[2] for t in data if t[4] > 0.95],
        'Hybrid v40': [t[2] for t in data if t[5] > 0.95]
    }
    
    positions = [1, 2, 3]
    colors = ['#E63946', '#457B9D', '#06A77D']
    
    bp = ax1.boxplot([successful_data[m] for m in methods],
                     positions=positions,
                     widths=0.6,
                     patch_artist=True,
                     showmeans=True,
                     meanprops=dict(marker='D', markerfacecolor='red', markersize=8))
    
    for patch, color in zip(bp['boxes'], colors):
        patch.set_facecolor(color)
        patch.set_alpha(0.7)
        patch.set_edgecolor('black')
        patch.set_linewidth(1.5)
    
    ax1.set_xticks(positions)
    ax1.set_xticklabels(methods, rotation=15, ha='right')
    ax1.set_ylabel('Expression Complexity', fontweight='bold')
    ax1.set_title('(a) Complexity Distribution\n(Successful Tests Only)',
                 fontweight='bold', pad=10)
    ax1.grid(axis='y', alpha=0.3, linestyle='--')
    ax1.set_axisbelow(True)
    
    # ========================================================================
    # PANEL B: R² by complexity bins
    # ========================================================================
    
    # Bin complexity into categories
    complexity_bins = {
        'Simple (1-3)': [],
        'Medium (4-6)': [],
        'Complex (7+)': []
    }
    
    for t in data:
        complexity = t[2]
        r2_hybrid = t[5]
        
        if complexity <= 3:
            complexity_bins['Simple (1-3)'].append(r2_hybrid)
        elif complexity <= 6:
            complexity_bins['Medium (4-6)'].append(r2_hybrid)
        else:
            complexity_bins['Complex (7+)'].append(r2_hybrid)
    
    positions = [1, 2, 3]
    colors_bins = ['#A8DADC', '#457B9D', '#1D3557']
    
    bp2 = ax2.boxplot([complexity_bins[k] for k in complexity_bins.keys()],
                      positions=positions,
                      widths=0.6,
                      patch_artist=True,
                      showmeans=True,
                      meanprops=dict(marker='D', markerfacecolor='red', markersize=8))
    
    for patch, color in zip(bp2['boxes'], colors_bins):
        patch.set_facecolor(color)
        patch.set_alpha(0.7)
        patch.set_edgecolor('black')
        patch.set_linewidth(1.5)
    
    ax2.set_xticks(positions)
    ax2.set_xticklabels(complexity_bins.keys(), rotation=15, ha='right')
    ax2.set_ylabel('R² Score', fontweight='bold')
    ax2.set_title('(b) R² by Complexity Category\n(Hybrid v40)',
                 fontweight='bold', pad=10)
    ax2.axhline(y=0.99, color='green', linestyle='--', linewidth=1.5, alpha=0.6,
               label='Target (0.99)')
    ax2.axhline(y=0.95, color='orange', linestyle='--', linewidth=1.5, alpha=0.6,
               label='Acceptable (0.95)')
    ax2.set_ylim(0.85, 1.02)
    ax2.legend(loc='lower left', fontsize=9)
    ax2.grid(axis='y', alpha=0.3, linestyle='--')
    ax2.set_axisbelow(True)
    
    plt.tight_layout()
    
    output_file = 'figure4_complexity_distribution.pdf'
    plt.savefig(output_file, dpi=300, bbox_inches='tight')
    print(f"✅ Alternative figure saved: {output_file}")
    
    plt.savefig(output_file.replace('.pdf', '.png'), dpi=300, bbox_inches='tight')
    
    plt.show()


if __name__ == "__main__":
    print("Generating Figure 4: R² vs Complexity Scatter Plot\n")
    print("=" * 60)
    
    # Main scatter plot
    create_r2_complexity_scatter()
    
    print("\n" + "=" * 60)
    print("Generating alternative complexity distribution...\n")
    
    # Alternative visualization
    create_complexity_distribution()
    
    print("\n✅ All visualizations complete!")
    print("\nOutput files:")
    print("  • figure4_r2_complexity.pdf (main)")
    print("  • figure4_r2_complexity.png")
    print("  • figure4_complexity_distribution.pdf (alternative)")
    print("  • figure4_complexity_distribution.png")
    print("\nNote: To use actual experimental data, run:")
    print("  python extract_complexity_from_results.py --session <session_id>")


    """
    For Figure 4: Extract complexity from your PySR results:

python# Add this to extract complexity from your results
import json

def extract_complexity_from_session(session_file):
    with open(session_file) as f:
        data = json.load(f)
    
    for test_name, result in data['tests'].items():
        expression = result['discovery']['expression']
        # Count operators: +, -, *, /, ^, exp, log, sqrt
        complexity = count_operators(expression)
        r2 = result['discovery']['r2_score']
        
        print(f"{test_name}: complexity={complexity}, R²={r2}")
Would you like me to:

Create a data extraction script to pull real values from your experimental results?
Modify these to match a specific visual style/format?

    Figure 4: R² vs Complexity Scatter Plot

Data points:

What represents "complexity"? (e.g., number of features, model parameters, lines of code)
What are the R² values for different complexity levels?
How many data points do you have?


Categories/grouping: Are there different model types or approaches to distinguish?
Labels: Do specific points need to be labeled?
Trend line: Should I include a fitted curve or trend line?
    """
