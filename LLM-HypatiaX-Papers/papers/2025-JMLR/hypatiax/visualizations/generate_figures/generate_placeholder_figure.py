#!/usr/bin/env python3
"""
Generate a placeholder PDF for the missing hybrid_v40_detailed_flow figure.
This creates a simple flowchart diagram that can be replaced with the actual figure later.
"""

import matplotlib.pyplot as plt
import matplotlib.patches as mpatches
from matplotlib.patches import FancyBboxPatch, FancyArrowPatch
import os

def create_architecture_diagram():
    """Create a placeholder architecture diagram for Hybrid v40."""
    
    fig, ax = plt.subplots(figsize=(12, 10))
    ax.set_xlim(0, 10)
    ax.set_ylim(0, 12)
    ax.axis('off')
    
    # Title
    ax.text(5, 11.5, 'HypatiaX Hybrid v40 Architecture', 
            fontsize=16, fontweight='bold', ha='center')
    
    # Define colors
    colors = {
        'input': '#E3F2FD',
        'process': '#FFF3E0',
        'core': '#F3E5F5',
        'validation': '#E8F5E9',
        'output': '#FCE4EC'
    }
    
    # Layer 1: Multimodal Data Sources
    layer1_y = 9.5
    box1 = FancyBboxPatch((0.5, layer1_y), 9, 1.2, 
                          boxstyle="round,pad=0.1", 
                          edgecolor='black', facecolor=colors['input'],
                          linewidth=2)
    ax.add_patch(box1)
    ax.text(5, layer1_y + 0.9, 'Layer 1: Multimodal Data Sources', 
            fontsize=12, fontweight='bold', ha='center')
    ax.text(5, layer1_y + 0.4, 'Images • Time-Series • Text • Tabular Data', 
            fontsize=9, ha='center', style='italic')
    
    # Arrow
    arrow1 = FancyArrowPatch((5, layer1_y), (5, layer1_y - 0.5),
                            arrowstyle='->', mutation_scale=20, 
                            linewidth=2, color='black')
    ax.add_patch(arrow1)
    
    # Layer 2: Preprocessing
    layer2_y = 7.5
    box2 = FancyBboxPatch((0.5, layer2_y), 9, 1.2,
                          boxstyle="round,pad=0.1",
                          edgecolor='black', facecolor=colors['process'],
                          linewidth=2)
    ax.add_patch(box2)
    ax.text(5, layer2_y + 0.9, 'Layer 2: Preprocessing Layer', 
            fontsize=12, fontweight='bold', ha='center')
    ax.text(5, layer2_y + 0.4, 'Feature Extraction • Normalization • Variable Identification', 
            fontsize=9, ha='center', style='italic')
    
    # Arrow
    arrow2 = FancyArrowPatch((5, layer2_y), (5, layer2_y - 0.5),
                            arrowstyle='->', mutation_scale=20,
                            linewidth=2, color='black')
    ax.add_patch(arrow2)
    
    # Layer 3: Symbolic Discovery Core (PySR)
    layer3_y = 5.5
    box3 = FancyBboxPatch((0.5, layer3_y), 9, 1.2,
                          boxstyle="round,pad=0.1",
                          edgecolor='black', facecolor=colors['core'],
                          linewidth=2)
    ax.add_patch(box3)
    ax.text(5, layer3_y + 0.9, 'Layer 3: Symbolic Discovery Core (PySR)', 
            fontsize=12, fontweight='bold', ha='center')
    ax.text(5, layer3_y + 0.4, 'Multi-Objective Evolution • Physics-Informed Operators • Pareto Optimization', 
            fontsize=9, ha='center', style='italic')
    
    # Arrow
    arrow3 = FancyArrowPatch((5, layer3_y), (5, layer3_y - 0.5),
                            arrowstyle='->', mutation_scale=20,
                            linewidth=2, color='black')
    ax.add_patch(arrow3)
    
    # Layer 4: Validation Framework
    layer4_y = 3.5
    box4 = FancyBboxPatch((0.5, layer4_y), 9, 1.2,
                          boxstyle="round,pad=0.1",
                          edgecolor='black', facecolor=colors['validation'],
                          linewidth=2)
    ax.add_patch(box4)
    ax.text(5, layer4_y + 0.9, 'Layer 4: Validation Framework', 
            fontsize=12, fontweight='bold', ha='center')
    ax.text(5, layer4_y + 0.4, 'Dimensional Analysis • Domain Constraints • Stability • Extrapolation', 
            fontsize=9, ha='center', style='italic')
    
    # Arrow
    arrow4 = FancyArrowPatch((5, layer4_y), (5, layer4_y - 0.5),
                            arrowstyle='->', mutation_scale=20,
                            linewidth=2, color='black')
    ax.add_patch(arrow4)
    
    # Layer 5: LLM Interpretation (Optional)
    layer5_y = 1.5
    box5 = FancyBboxPatch((0.5, layer5_y), 9, 1.2,
                          boxstyle="round,pad=0.1",
                          edgecolor='black', facecolor=colors['output'],
                          linewidth=2, linestyle='--')
    ax.add_patch(box5)
    ax.text(5, layer5_y + 0.9, 'Layer 5: LLM Interpretation Layer (Optional)', 
            fontsize=12, fontweight='bold', ha='center')
    ax.text(5, layer5_y + 0.4, 'Physical Explanation • Literature Context • Natural Language Reporting', 
            fontsize=9, ha='center', style='italic')
    
    # Add note about placeholder
    ax.text(5, 0.3, 'PLACEHOLDER FIGURE - Replace with actual architecture diagram', 
            fontsize=8, ha='center', style='italic', color='red')
    
    plt.tight_layout()
    return fig

if __name__ == '__main__':
    # Create figures directory if it doesn't exist
    os.makedirs('figures', exist_ok=True)
    
    # Generate the figure
    fig = create_architecture_diagram()
    
    # Save as PDF
    output_path = 'figures/hybrid_v40_detailed_flow.pdf'
    fig.savefig(output_path, format='pdf', bbox_inches='tight', dpi=300)
    print(f"Placeholder figure saved to: {output_path}")
    
    plt.close()
