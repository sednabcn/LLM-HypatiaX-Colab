#!/usr/bin/env python3
"""
Complete Hybrid Systems Architecture Visualization
Three systems side-by-side with smooth backgrounds
Usage: python generate_hybrid_architecture_complete.py
"""

import matplotlib.pyplot as plt
import matplotlib.patches as mpatches
from matplotlib.patches import FancyBboxPatch, Rectangle, Polygon
import numpy as np

# Publication settings
plt.rcParams['font.family'] = 'sans-serif'
plt.rcParams['font.size'] = 10
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
    'hybrid3': '#F57C00',      # Deep Orange
}

def create_three_systems():
    """All three systems side-by-side"""
    fig = plt.figure(figsize=(20, 9))
    
    # Main title
    fig.text(0.5, 0.97, 'Complete Hybrid Systems Architecture Comparison', 
             ha='center', fontsize=18, fontweight='bold')
    fig.text(0.5, 0.935, 'Critical Issue: Hybrid extrapolation 60% R² vs Pure LLM 100% R²',
             ha='center', fontsize=12, style='italic', color=COLORS['broken'])
    
    # ============ SYSTEM 1 (LEFT) ============
    ax1 = plt.subplot(1, 3, 1)
    ax1.set_xlim(0, 10)
    ax1.set_ylim(0, 10)
    ax1.axis('off')
    
    # Smooth gradient background
    gradient1 = np.linspace(0, 1, 256).reshape(1, -1)
    ax1.imshow(gradient1, extent=[0, 10, 0, 10], aspect='auto', cmap='Greens', alpha=0.15)
    
    # Title with border
    title_box1 = FancyBboxPatch((0.3, 8.6), 9.4, 1.1, boxstyle="round,pad=0.1",
                                facecolor='white', edgecolor=COLORS['fixed'], linewidth=3)
    ax1.add_patch(title_box1)
    ax1.text(5, 9.25, 'System 1: Improved Hybrid', 
             ha='center', fontsize=12, fontweight='bold')
    ax1.text(5, 8.85, '✅ FIXES Extrapolation',
             ha='center', fontsize=10, color=COLORS['fixed'], fontweight='bold')
    
    # Layer 1: NN + LLM (SWAPPED - NN left, LLM right)
    nn_box = FancyBboxPatch((0.8, 7), 3.8, 1.1, boxstyle="round,pad=0.08",
                            facecolor=COLORS['nn'], edgecolor='none', alpha=0.85)
    ax1.add_patch(nn_box)
    ax1.text(2.7, 7.7, 'NN Engine', ha='center', fontsize=11,
             fontweight='bold', color='white')
    ax1.text(2.7, 7.3, 'Deep learning', ha='center', fontsize=8, color='white')
    
    llm_box = FancyBboxPatch((5.4, 7), 3.8, 1.1, boxstyle="round,pad=0.08",
                             facecolor=COLORS['llm'], edgecolor='none', alpha=0.85)
    ax1.add_patch(llm_box)
    ax1.text(7.3, 7.7, 'LLM Engine', ha='center', fontsize=11, 
             fontweight='bold', color='white')
    ax1.text(7.3, 7.3, 'Formula discovery', ha='center', fontsize=8, color='white')
    
    # Layer 2: Pattern Recognition
    pattern_box = FancyBboxPatch((1.3, 5.6), 7.4, 0.9, boxstyle="round,pad=0.08",
                                 facecolor=COLORS['symbolic'], edgecolor='none', alpha=0.75)
    ax1.add_patch(pattern_box)
    ax1.text(5, 6.15, 'Pattern Recognition', ha='center',
             fontsize=10, fontweight='bold', color='white')
    ax1.text(5, 5.85, 'Confidence scoring', ha='center', 
             fontsize=7, color='white')
    
    # Layer 3: CRITICAL DECISION
    decision_box = FancyBboxPatch((0.8, 3.3), 8.4, 2, boxstyle="round,pad=0.1",
                                  facecolor=COLORS['decision'], edgecolor='gold',
                                  linewidth=4, alpha=0.9)
    ax1.add_patch(decision_box)
    
    # Gold star
    star_x = np.array([1.2, 1.3, 1.6, 1.4, 1.5, 1.2, 0.9, 1.0, 0.85, 1.1])
    star_y = np.array([4.3, 4.55, 4.6, 4.4, 4.75, 4.55, 4.75, 4.4, 4.6, 4.55])
    star = Polygon(list(zip(star_x, star_y)), facecolor='gold', 
                   edgecolor='black', linewidth=2)
    ax1.add_patch(star)
    
    ax1.text(5, 4.9, '⭐ EXTRAPOLATION-AWARE', ha='center',
             fontsize=11, fontweight='bold', color='white')
    ax1.text(5, 4.55, 'Detects out-of-range', ha='center', fontsize=9, color='white')
    ax1.text(5, 4.2, 'Prefers LLM for extrap', ha='center', fontsize=9, color='white')
    ax1.text(5, 3.7, 'if is_extrap: use LLM', ha='center',
             fontsize=8, color='yellow', family='monospace', fontweight='bold')
    
    # Layer 4: Output
    output_box = FancyBboxPatch((2, 1.8), 6, 0.9, boxstyle="round,pad=0.08",
                                facecolor=COLORS['validation'], edgecolor='none', alpha=0.85)
    ax1.add_patch(output_box)
    ax1.text(5, 2.35, 'Ensemble Output', ha='center', fontsize=10,
             fontweight='bold', color='white')
    ax1.text(5, 2.05, 'Adaptive weights', ha='center',
             fontsize=7, color='white')
    
    # Arrows
    arrow_props = dict(arrowstyle='->', lw=2.5, color='black', alpha=0.6)
    ax1.annotate('', xy=(2.7, 5.6), xytext=(2.7, 7), arrowprops=arrow_props)
    ax1.annotate('', xy=(7.3, 5.6), xytext=(7.3, 7), arrowprops=arrow_props)
    ax1.annotate('', xy=(5, 3.3), xytext=(5, 5.6), 
                 arrowprops=dict(arrowstyle='->', lw=3.5, color='gold', alpha=0.8))
    ax1.annotate('', xy=(5, 1.8), xytext=(5, 2.7), arrowprops=arrow_props)
    
    # Result banner
    result1 = FancyBboxPatch((1.3, 0.5), 7.4, 1, boxstyle="round,pad=0.1",
                             facecolor=COLORS['fixed'], edgecolor='none', alpha=0.2)
    ax1.add_patch(result1)
    ax1.text(5, 1.1, '🎯 Target: 95-100% R²', ha='center', 
             fontsize=11, fontweight='bold', color=COLORS['fixed'])
    ax1.text(5, 0.75, '(vs 60% baseline)', ha='center', fontsize=9, 
             color=COLORS['fixed'])
    
    # ============ SYSTEM 3 (MIDDLE) ============
    ax3 = plt.subplot(1, 3, 2)
    ax3.set_xlim(0, 10)
    ax3.set_ylim(0, 10)
    ax3.axis('off')
    
    # Smooth gradient background
    gradient3 = np.linspace(0, 1, 256).reshape(1, -1)
    ax3.imshow(gradient3, extent=[0, 10, 0, 10], aspect='auto', cmap='Oranges', alpha=0.12)
    
    # Title with border
    title_box3 = FancyBboxPatch((0.3, 8.6), 9.4, 1.1, boxstyle="round,pad=0.1",
                                facecolor='white', edgecolor=COLORS['hybrid3'], linewidth=3)
    ax3.add_patch(title_box3)
    ax3.text(5, 9.25, 'System 3: LLM + Symbolic',
             ha='center', fontsize=12, fontweight='bold')
    ax3.text(5, 8.85, '🔄 Fallback Architecture',
             ha='center', fontsize=10, color=COLORS['hybrid3'], fontweight='bold')
    
    # Layer 1: LLM Engine (primary)
    llm_primary = FancyBboxPatch((1.5, 7), 7, 1.1, boxstyle="round,pad=0.08",
                                 facecolor=COLORS['llm'], edgecolor='none', alpha=0.85)
    ax3.add_patch(llm_primary)
    ax3.text(5, 7.7, 'LLM Engine (Primary)', ha='center',
             fontsize=11, fontweight='bold', color='white')
    ax3.text(5, 7.3, 'Formula discovery & reasoning', ha='center', 
             fontsize=8, color='white')
    
    # Linking arrow (thick, showing connection)
    link_arrow = dict(arrowstyle='->', lw=4, color=COLORS['hybrid3'], alpha=0.8)
    ax3.annotate('', xy=(5, 5.6), xytext=(5, 7),
                 arrowprops=link_arrow)
    ax3.text(6.2, 6.3, 'Links to ↓', ha='left', fontsize=9, 
             color=COLORS['hybrid3'], fontweight='bold', style='italic')
    
    # Layer 2: Symbolic Regression (fallback)
    symbolic_fallback = FancyBboxPatch((1.5, 4.2), 7, 1.3, boxstyle="round,pad=0.08",
                                       facecolor=COLORS['symbolic'], edgecolor='none', alpha=0.85)
    ax3.add_patch(symbolic_fallback)
    ax3.text(5, 5.15, 'Symbolic Regression (Fallback)', ha='center',
             fontsize=11, fontweight='bold', color='white')
    ax3.text(5, 4.8, 'PySR • gplearn', ha='center', fontsize=8, color='white')
    ax3.text(5, 4.5, 'Used when LLM confidence low', ha='center', 
             fontsize=7, color='white', style='italic')
    
    # Layer 3: Decision Logic
    decision3 = FancyBboxPatch((1.5, 2.6), 7, 1.3, boxstyle="round,pad=0.08",
                               facecolor=COLORS['decision'], edgecolor='none', alpha=0.75)
    ax3.add_patch(decision3)
    ax3.text(5, 3.5, 'Fallback Decision', ha='center',
             fontsize=10, fontweight='bold', color='white')
    ax3.text(5, 3.15, 'if llm_confidence < threshold:', ha='center',
             fontsize=8, color='yellow', family='monospace')
    ax3.text(5, 2.85, '    use symbolic_regression', ha='center',
             fontsize=8, color='lightgreen', family='monospace')
    
    # Layer 4: Output
    output3 = FancyBboxPatch((2, 1.3), 6, 0.9, boxstyle="round,pad=0.08",
                             facecolor=COLORS['validation'], edgecolor='none', alpha=0.85)
    ax3.add_patch(output3)
    ax3.text(5, 1.85, 'Hybrid Output', ha='center', fontsize=10,
             fontweight='bold', color='white')
    ax3.text(5, 1.55, 'LLM or Symbolic', ha='center',
             fontsize=7, color='white')
    
    # Arrows
    ax3.annotate('', xy=(5, 4.2), xytext=(5, 5.5),
                 arrowprops=dict(arrowstyle='->', lw=2.5, color='black', alpha=0.6))
    ax3.annotate('', xy=(5, 2.6), xytext=(5, 3.9),
                 arrowprops=dict(arrowstyle='->', lw=2.5, color='black', alpha=0.6))
    ax3.annotate('', xy=(5, 1.3), xytext=(5, 2.2),
                 arrowprops=dict(arrowstyle='->', lw=2.5, color='black', alpha=0.6))
    
    # Result banner
    result3 = FancyBboxPatch((1.5, 0.5), 7, 1, boxstyle="round,pad=0.1",
                             facecolor=COLORS['hybrid3'], edgecolor='none', alpha=0.2)
    ax3.add_patch(result3)
    ax3.text(5, 1.1, '🎯 Target: Robust hybrid', ha='center',
             fontsize=11, fontweight='bold', color=COLORS['hybrid3'])
    ax3.text(5, 0.75, 'LLM first, symbolic backup', ha='center', fontsize=9,
             color=COLORS['hybrid3'])
    
    # ============ SYSTEM 2 (RIGHT) ============
    ax2 = plt.subplot(1, 3, 3)
    ax2.set_xlim(0, 10)
    ax2.set_ylim(0, 10)
    ax2.axis('off')
    
    # Smooth gradient background
    gradient2 = np.linspace(0, 1, 256).reshape(1, -1)
    ax2.imshow(gradient2, extent=[0, 10, 0, 10], aspect='auto', cmap='Reds', alpha=0.12)
    
    # Title with border
    title_box2 = FancyBboxPatch((0.3, 8.6), 9.4, 1.1, boxstyle="round,pad=0.1",
                                facecolor='white', edgecolor=COLORS['broken'], linewidth=3)
    ax2.add_patch(title_box2)
    ax2.text(5, 9.25, 'System 2: Symbolic Only',
             ha='center', fontsize=12, fontweight='bold')
    ax2.text(5, 8.85, '❌ No Extrapolation Fix',
             ha='center', fontsize=10, color=COLORS['broken'], fontweight='bold')
    
    # Layer 1: Symbolic Engine
    symbolic_box = FancyBboxPatch((1.5, 7), 7, 1.1, boxstyle="round,pad=0.08",
                                  facecolor=COLORS['symbolic'], edgecolor='none', alpha=0.85)
    ax2.add_patch(symbolic_box)
    ax2.text(5, 7.7, 'Symbolic Regression', ha='center',
             fontsize=11, fontweight='bold', color='white')
    ax2.text(5, 7.3, 'PySR • gplearn • Formula discovery', ha='center', 
             fontsize=8, color='white')
    
    # Layer 2: 4-Layer Validation
    ax2.text(5, 6.3, '4-Layer Validation', ha='center',
             fontsize=12, fontweight='bold', color=COLORS['validation'])
    
    layers = [
        (5.5, 'Layer 1: Symbolic', 'Syntax'),
        (4.8, 'Layer 2: Dimensional', 'Units'),
        (4.1, 'Layer 3: Domain', 'Rules'),
        (3.4, 'Layer 4: Numerical', 'Edge cases'),
    ]
    
    for y, title, desc in layers:
        layer_box = FancyBboxPatch((1.5, y-0.22), 7, 0.55, boxstyle="round,pad=0.06",
                                   facecolor='white', edgecolor=COLORS['validation'],
                                   linewidth=2, alpha=0.9)
        ax2.add_patch(layer_box)
        ax2.text(1.9, y, '✓', ha='left', fontsize=10, color='green', fontweight='bold')
        ax2.text(2.4, y, title, ha='left', fontsize=9, fontweight='bold',
                 color=COLORS['validation'])
        ax2.text(8.2, y, desc, ha='right', fontsize=7, style='italic', color='gray')
    
    # Layer 3: Optional LLM
    llm_optional = FancyBboxPatch((2, 1.8), 6, 0.9, boxstyle="round,pad=0.08",
                                  facecolor=COLORS['llm'], edgecolor='gray',
                                  linewidth=2, linestyle='--', alpha=0.4)
    ax2.add_patch(llm_optional)
    ax2.text(5, 2.35, 'LLM Interpretation (Optional)', ha='center',
             fontsize=10, fontweight='bold', color=COLORS['llm'])
    ax2.text(5, 2.05, 'Naming only', ha='center',
             fontsize=7, color=COLORS['llm'])
    
    # Arrows
    ax2.annotate('', xy=(5, 7), xytext=(5, 6.1),
                 arrowprops=dict(arrowstyle='->', lw=2.5, color='black', alpha=0.6))
    ax2.annotate('', xy=(5, 1.8), xytext=(5, 3.15),
                 arrowprops=dict(arrowstyle='->', lw=2, color='gray', 
                                linestyle='--', alpha=0.5))
    
    # Warning banner
    warning = FancyBboxPatch((1.5, 0.5), 7, 1, boxstyle="round,pad=0.1",
                             facecolor=COLORS['broken'], edgecolor='none', alpha=0.2)
    ax2.add_patch(warning)
    ax2.text(5, 1.1, '⚠️ Target: Validation only', ha='center',
             fontsize=11, fontweight='bold', color=COLORS['broken'])
    ax2.text(5, 0.75, '(NOT extrapolation R²)', ha='center', fontsize=9,
             color=COLORS['broken'])
    
    # Bottom comparison banner
    fig.text(0.5, 0.02, '🔑 System 1: NN+LLM choice  •  System 3: LLM→Symbolic fallback  •  System 2: Symbolic validation only',
             ha='center', fontsize=11, fontweight='bold',
             bbox=dict(boxstyle='round,pad=0.5', facecolor='#FFF9C4', 
                      edgecolor='black', linewidth=2))
    
    plt.tight_layout(rect=[0, 0.05, 1, 0.915])
    plt.savefig('hybrid_architecture_three_systems.pdf', bbox_inches='tight')
    plt.savefig('hybrid_architecture_three_systems.png', bbox_inches='tight', dpi=300)
    print("✓ Created hybrid_architecture_three_systems.pdf/png")
    
    return fig

if __name__ == '__main__':
    print("Generating Complete Three-System Architecture Comparison...")
    print()
    
    create_three_systems()
    
    print()
    print("✅ Complete diagram created!")
    print()
    print("Three Systems:")
    print("  LEFT (System 1):   NN + LLM with extrapolation-aware decision ✅")
    print("  MIDDLE (System 3): LLM → Symbolic (fallback architecture) 🔄")
    print("  RIGHT (System 2):  Symbolic validation only ❌")
    print()
    print("Key features:")
    print("  ✓ NN/LLM swapped positions (NN left, LLM right)")
    print("  ✓ System 3 shows LLM linking to Symbolic as fallback")
    print("  ✓ Smooth gradient backgrounds")
    print("  ✓ Larger text, smaller rectangles")
    print("  ✓ Professional design")
    print()
    print("📊 Result: Complete architecture comparison")
