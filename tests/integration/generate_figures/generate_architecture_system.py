#!/usr/bin/env python3
"""
Clean Hybrid Systems Architecture Visualization
Smooth backgrounds, compact boxes, large readable text
Usage: python generate_hybrid_architecture_clean.py
"""

import matplotlib.pyplot as plt
import matplotlib.patches as mpatches
from matplotlib.patches import FancyBboxPatch, Rectangle, Polygon
import numpy as np

# Publication settings
plt.rcParams['font.family'] = 'sans-serif'
plt.rcParams['font.size'] = 11
plt.rcParams['figure.dpi'] = 300
plt.rcParams['savefig.dpi'] = 300
plt.rcParams['savefig.bbox'] = 'tight'

# Clean, modern color palette
COLORS = {
    'llm': '#1E88E5',          # Bright Blue
    'nn': '#00ACC1',           # Cyan
    'symbolic': '#8E24AA',     # Purple
    'validation': '#FB8C00',   # Orange
    'decision': '#E53935',     # Red
    'fixed': '#43A047',        # Green
    'broken': '#E53935',       # Red
}

def create_combined_architecture():
    """Both systems side-by-side with smooth gradients"""
    fig = plt.figure(figsize=(20, 10))
    
    # Main title
    fig.text(0.5, 0.96, 'Hybrid Systems Architecture Comparison', 
             ha='center', fontsize=20, fontweight='bold')
    fig.text(0.5, 0.92, 'Critical Issue: Hybrid extrapolation 60% R² vs Pure LLM 100% R²',
             ha='center', fontsize=13, style='italic', color=COLORS['broken'])
    
    # ============ SYSTEM 1 (LEFT) ============
    ax1 = plt.subplot(1, 2, 1)
    ax1.set_xlim(0, 10)
    ax1.set_ylim(0, 10)
    ax1.axis('off')
    
    # Smooth gradient background
    gradient1 = np.linspace(0, 1, 256).reshape(1, -1)
    ax1.imshow(gradient1, extent=[0, 10, 0, 10], aspect='auto', cmap='Greens', alpha=0.15)
    
    # Title with border
    title_box1 = FancyBboxPatch((0.5, 8.5), 9, 1.2, boxstyle="round,pad=0.1",
                                facecolor='white', edgecolor=COLORS['fixed'], linewidth=3)
    ax1.add_patch(title_box1)
    ax1.text(5, 9.3, 'System 1: Improved Hybrid', 
             ha='center', fontsize=15, fontweight='bold')
    ax1.text(5, 8.85, '✅ FIXES Extrapolation Weakness',
             ha='center', fontsize=12, color=COLORS['fixed'], fontweight='bold')
    
    # Layer 1: LLM + NN (side by side, compact)
    llm_box = FancyBboxPatch((1, 7), 3.5, 1.1, boxstyle="round,pad=0.08",
                             facecolor=COLORS['llm'], edgecolor='none', alpha=0.85)
    ax1.add_patch(llm_box)
    ax1.text(2.75, 7.7, 'LLM Engine', ha='center', fontsize=12, 
             fontweight='bold', color='white')
    ax1.text(2.75, 7.3, 'Formula discovery', ha='center', fontsize=9, color='white')
    
    nn_box = FancyBboxPatch((5.5, 7), 3.5, 1.1, boxstyle="round,pad=0.08",
                            facecolor=COLORS['nn'], edgecolor='none', alpha=0.85)
    ax1.add_patch(nn_box)
    ax1.text(7.25, 7.7, 'NN Engine', ha='center', fontsize=12,
             fontweight='bold', color='white')
    ax1.text(7.25, 7.3, 'Deep learning', ha='center', fontsize=9, color='white')
    
    # Layer 2: Pattern Recognition (compact)
    pattern_box = FancyBboxPatch((1.5, 5.6), 7, 0.9, boxstyle="round,pad=0.08",
                                 facecolor=COLORS['symbolic'], edgecolor='none', alpha=0.75)
    ax1.add_patch(pattern_box)
    ax1.text(5, 6.2, 'Pattern Recognition & Confidence', ha='center',
             fontsize=11, fontweight='bold', color='white')
    ax1.text(5, 5.85, 'Few-shot examples • Confidence scoring', ha='center', 
             fontsize=8, color='white')
    
    # Layer 3: CRITICAL DECISION (highlighted with star)
    decision_box = FancyBboxPatch((1, 3.3), 8, 2, boxstyle="round,pad=0.1",
                                  facecolor=COLORS['decision'], edgecolor='gold',
                                  linewidth=4, alpha=0.9)
    ax1.add_patch(decision_box)
    
    # Gold star
    star_x = np.array([1.4, 1.5, 1.75, 1.6, 1.7, 1.4, 1.1, 1.2, 1.05, 1.3])
    star_y = np.array([4.3, 4.55, 4.6, 4.4, 4.75, 4.55, 4.75, 4.4, 4.6, 4.55])
    star = Polygon(list(zip(star_x, star_y)), facecolor='gold', 
                   edgecolor='black', linewidth=2)
    ax1.add_patch(star)
    
    ax1.text(5, 4.95, '⭐ EXTRAPOLATION-AWARE DECISION ⭐', ha='center',
             fontsize=12, fontweight='bold', color='white')
    ax1.text(5, 4.55, 'Detects out-of-range data', ha='center', fontsize=10, color='white')
    ax1.text(5, 4.2, 'Prefers LLM for extrapolation', ha='center', fontsize=10, color='white')
    ax1.text(5, 3.7, 'if is_extrap and llm_r2 > 0.90: use LLM', ha='center',
             fontsize=9, color='yellow', family='monospace', fontweight='bold')
    
    # Layer 4: Output (compact)
    output_box = FancyBboxPatch((2, 1.8), 6, 0.9, boxstyle="round,pad=0.08",
                                facecolor=COLORS['validation'], edgecolor='none', alpha=0.85)
    ax1.add_patch(output_box)
    ax1.text(5, 2.4, 'Ensemble Output', ha='center', fontsize=11,
             fontweight='bold', color='white')
    ax1.text(5, 2.05, 'Optimized adaptive weights', ha='center',
             fontsize=8, color='white')
    
    # Arrows
    arrow_props = dict(arrowstyle='->', lw=2.5, color='black', alpha=0.6)
    ax1.annotate('', xy=(2.75, 5.6), xytext=(2.75, 7), arrowprops=arrow_props)
    ax1.annotate('', xy=(7.25, 5.6), xytext=(7.25, 7), arrowprops=arrow_props)
    ax1.annotate('', xy=(5, 3.3), xytext=(5, 5.6), 
                 arrowprops=dict(arrowstyle='->', lw=3.5, color='gold', alpha=0.8))
    ax1.annotate('', xy=(5, 1.8), xytext=(5, 2.7), arrowprops=arrow_props)
    
    # Result banner
    result1 = FancyBboxPatch((1.5, 0.5), 7, 1, boxstyle="round,pad=0.1",
                             facecolor=COLORS['fixed'], edgecolor='none', alpha=0.2)
    ax1.add_patch(result1)
    ax1.text(5, 1.15, '🎯 Target: 95-100% Extrapolation R²', ha='center', 
             fontsize=12, fontweight='bold', color=COLORS['fixed'])
    ax1.text(5, 0.75, '(vs 60% baseline)', ha='center', fontsize=10, 
             color=COLORS['fixed'])
    
    # ============ SYSTEM 2 (RIGHT) ============
    ax2 = plt.subplot(1, 2, 2)
    ax2.set_xlim(0, 10)
    ax2.set_ylim(0, 10)
    ax2.axis('off')
    
    # Smooth gradient background
    gradient2 = np.linspace(0, 1, 256).reshape(1, -1)
    ax2.imshow(gradient2, extent=[0, 10, 0, 10], aspect='auto', cmap='Reds', alpha=0.12)
    
    # Title with border
    title_box2 = FancyBboxPatch((0.5, 8.5), 9, 1.2, boxstyle="round,pad=0.1",
                                facecolor='white', edgecolor=COLORS['broken'], linewidth=3)
    ax2.add_patch(title_box2)
    ax2.text(5, 9.3, 'System 2: Symbolic Discovery',
             ha='center', fontsize=15, fontweight='bold')
    ax2.text(5, 8.85, '❌ Does NOT Fix Extrapolation',
             ha='center', fontsize=12, color=COLORS['broken'], fontweight='bold')
    
    # Layer 1: Symbolic Engine (compact)
    symbolic_box = FancyBboxPatch((1.5, 7), 7, 1.1, boxstyle="round,pad=0.08",
                                  facecolor=COLORS['symbolic'], edgecolor='none', alpha=0.85)
    ax2.add_patch(symbolic_box)
    ax2.text(5, 7.7, 'Symbolic Regression Engine', ha='center',
             fontsize=12, fontweight='bold', color='white')
    ax2.text(5, 7.3, 'PySR • gplearn • Formula discovery', ha='center', 
             fontsize=9, color='white')
    
    # Layer 2: 4-Layer Validation (compact boxes)
    ax2.text(5, 6.4, '4-Layer Validation System', ha='center',
             fontsize=13, fontweight='bold', color=COLORS['validation'])
    
    layers = [
        (5.5, 'Layer 1: Symbolic Validation', 'Syntax checks'),
        (4.7, 'Layer 2: Dimensional Analysis', 'Unit consistency'),
        (3.9, 'Layer 3: Domain Knowledge', 'DeFi rules'),
        (3.1, 'Layer 4: Numerical Validation', 'Edge cases'),
    ]
    
    for y, title, desc in layers:
        layer_box = FancyBboxPatch((1.5, y-0.25), 7, 0.6, boxstyle="round,pad=0.06",
                                   facecolor='white', edgecolor=COLORS['validation'],
                                   linewidth=2, alpha=0.9)
        ax2.add_patch(layer_box)
        ax2.text(2, y, '✓', ha='left', fontsize=11, color='green', fontweight='bold')
        ax2.text(2.6, y, title, ha='left', fontsize=10, fontweight='bold',
                 color=COLORS['validation'])
        ax2.text(8.2, y, desc, ha='right', fontsize=8, style='italic', color='gray')
    
    # Layer 3: Optional LLM (compact, dashed)
    llm_optional = FancyBboxPatch((2, 1.8), 6, 0.9, boxstyle="round,pad=0.08",
                                  facecolor=COLORS['llm'], edgecolor='gray',
                                  linewidth=2, linestyle='--', alpha=0.4)
    ax2.add_patch(llm_optional)
    ax2.text(5, 2.4, 'LLM Interpretation (Optional)', ha='center',
             fontsize=11, fontweight='bold', color=COLORS['llm'])
    ax2.text(5, 2.05, 'Formula naming only', ha='center',
             fontsize=8, color=COLORS['llm'])
    
    # Arrows
    ax2.annotate('', xy=(5, 7), xytext=(5, 6.2),
                 arrowprops=dict(arrowstyle='->', lw=2.5, color='black', alpha=0.6))
    ax2.annotate('', xy=(5, 1.8), xytext=(5, 2.85),
                 arrowprops=dict(arrowstyle='->', lw=2, color='gray', 
                                linestyle='--', alpha=0.5))
    
    # Warning banner
    warning = FancyBboxPatch((1.5, 0.5), 7, 1, boxstyle="round,pad=0.1",
                             facecolor=COLORS['broken'], edgecolor='none', alpha=0.2)
    ax2.add_patch(warning)
    ax2.text(5, 1.15, '⚠️ Target: 85+ validation score', ha='center',
             fontsize=12, fontweight='bold', color=COLORS['broken'])
    ax2.text(5, 0.75, '(NOT extrapolation R²)', ha='center', fontsize=10,
             color=COLORS['broken'])
    
    # Bottom comparison banner
    fig.text(0.5, 0.03, '🔑 Key: System 1 decides WHEN to use LLM vs NN  •  System 2 only validates ONE formula',
             ha='center', fontsize=13, fontweight='bold',
             bbox=dict(boxstyle='round,pad=0.6', facecolor='#FFF9C4', 
                      edgecolor='black', linewidth=2))
    
    plt.tight_layout(rect=[0, 0.06, 1, 0.90])
    plt.savefig('hybrid_architecture_clean.pdf', bbox_inches='tight')
    plt.savefig('hybrid_architecture_clean.png', bbox_inches='tight', dpi=300)
    print("✓ Created hybrid_architecture_clean.pdf/png")
    
    return fig

if __name__ == '__main__':
    print("Generating Clean Hybrid Architecture Comparison...")
    print()
    
    create_combined_architecture()
    
    print()
    print("✅ Clean diagram created!")
    print()
    print("Improvements:")
    print("  ✓ Smooth gradient backgrounds (green/red tint)")
    print("  ✓ Smaller, compact rectangles")
    print("  ✓ Larger, more readable text (11-15pt)")
    print("  ✓ Both systems side-by-side")
    print("  ✓ Gold star highlights critical fix")
    print("  ✓ Clean, modern design")
    print()
    print("📊 Result: Professional comparison diagram")
