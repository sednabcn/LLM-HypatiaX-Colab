#!/usr/bin/env python3
"""
Hybrid Systems Architecture Visualization
Creates diagrams for the three different hybrid system architectures
Usage: python generate_hybrid_architecture.py
"""

import matplotlib.pyplot as plt
import matplotlib.patches as mpatches
from matplotlib.patches import FancyBboxPatch, FancyArrowPatch, Circle, Rectangle, Polygon
import matplotlib.lines as mlines

# Publication settings
plt.rcParams['font.family'] = 'serif'
plt.rcParams['font.size'] = 9
plt.rcParams['figure.dpi'] = 300
plt.rcParams['savefig.dpi'] = 300
plt.rcParams['savefig.bbox'] = 'tight'

# Colors
COLORS = {
    'llm': '#2E7D32',          # Green - LLM
    'nn': '#1976D2',           # Blue - Neural Network
    'symbolic': '#7B1FA2',     # Purple - Symbolic
    'validation': '#F57C00',   # Orange - Validation
    'decision': '#C62828',     # Red - Decision Logic
    'fixed': '#4CAF50',        # Light Green - Fixed
    'broken': '#FF5722',       # Deep Orange - Broken
}

def create_system1_architecture():
    """System 1: Improved Hybrid (LLM + NN) - FIXES THE WEAKNESS"""
    fig, ax = plt.subplots(figsize=(14, 12))
    ax.set_xlim(0, 14)
    ax.set_ylim(0, 12)
    ax.axis('off')
    
    # Title
    ax.text(7, 11.5, 'System 1: Improved Hybrid (LLM + NN)', 
            ha='center', fontsize=14, fontweight='bold')
    ax.text(7, 11, '✅ FIXES Extrapolation Weakness | hybrid_system_defi_domain.py',
           ha='center', fontsize=10, style='italic', color=COLORS['fixed'])
    
    # Main container
    main_box = FancyBboxPatch((0.5, 1), 13, 9.5, boxstyle="round,pad=0.2",
                              facecolor='white', edgecolor='black', linewidth=3)
    ax.add_patch(main_box)
    
    # Layer 1: LLM Engine (left)
    llm_box = FancyBboxPatch((1, 8), 5, 2, boxstyle="round,pad=0.15",
                             facecolor=COLORS['llm'], edgecolor='black', 
                             linewidth=2, alpha=0.8)
    ax.add_patch(llm_box)
    ax.text(3.5, 9.5, 'LLM Engine', ha='center', fontsize=11, 
           fontweight='bold', color='white')
    ax.text(3.5, 9.1, '(Claude Sonnet)', ha='center', fontsize=9, color='white')
    ax.text(3.5, 8.7, '• Formula discovery', ha='center', fontsize=8, color='white')
    ax.text(3.5, 8.4, '• Pattern recognition', ha='center', fontsize=8, color='white')
    
    # Layer 1: NN Engine (right)
    nn_box = FancyBboxPatch((8, 8), 5, 2, boxstyle="round,pad=0.15",
                            facecolor=COLORS['nn'], edgecolor='black',
                            linewidth=2, alpha=0.8)
    ax.add_patch(nn_box)
    ax.text(10.5, 9.5, 'NN Engine', ha='center', fontsize=11,
           fontweight='bold', color='white')
    ax.text(10.5, 9.1, '(PyTorch)', ha='center', fontsize=9, color='white')
    ax.text(10.5, 8.7, '• Deep learning', ha='center', fontsize=8, color='white')
    ax.text(10.5, 8.4, '• Gradient descent', ha='center', fontsize=8, color='white')
    
    # Layer 2: Pattern Recognition
    pattern_box = FancyBboxPatch((2, 6), 10, 1.5, boxstyle="round,pad=0.15",
                                 facecolor=COLORS['symbolic'], edgecolor='black',
                                 linewidth=2, alpha=0.7)
    ax.add_patch(pattern_box)
    ax.text(7, 7, 'Pattern Recognition & Confidence Scoring', ha='center',
           fontsize=10, fontweight='bold', color='white')
    ax.text(7, 6.6, '• Formula detection  • Few-shot examples  • Confidence scoring',
           ha='center', fontsize=8, color='white')
    
    # Layer 3: CRITICAL - Extrapolation-Aware Decision (HIGHLIGHTED)
    decision_box = FancyBboxPatch((1.5, 3.8), 11, 1.8, boxstyle="round,pad=0.15",
                                  facecolor=COLORS['decision'], edgecolor='gold',
                                  linewidth=4, alpha=0.9)
    ax.add_patch(decision_box)
    
    # Gold star for critical fix
    star_x = [1.8, 2.0, 2.5, 2.2, 2.4, 1.8, 1.2, 1.4, 1.1, 1.6]
    star_y = [4.8, 5.3, 5.4, 5.0, 5.6, 5.2, 5.6, 5.0, 5.4, 5.3]
    star = Polygon(list(zip(star_x, star_y)), facecolor='gold', 
                   edgecolor='black', linewidth=2)
    ax.add_patch(star)
    
    ax.text(7, 5.2, '⭐ EXTRAPOLATION-AWARE DECISION ⭐', ha='center',
           fontsize=11, fontweight='bold', color='white')
    ax.text(7, 4.7, '• is_extrapolation check  • LLM preference  • Adaptive thresholds',
           ha='center', fontsize=8, color='white')
    ax.text(7, 4.3, 'if is_extrap and llm_r2 > 0.90: return "llm"  ← CRITICAL FIX',
           ha='center', fontsize=7, color='yellow', family='monospace',
           bbox=dict(boxstyle='round', facecolor='black', alpha=0.5))
    
    # Layer 4: Ensemble Output
    output_box = FancyBboxPatch((3, 2), 8, 1.3, boxstyle="round,pad=0.15",
                                facecolor=COLORS['validation'], edgecolor='black',
                                linewidth=2, alpha=0.8)
    ax.add_patch(output_box)
    ax.text(7, 2.8, 'Ensemble / Output', ha='center', fontsize=10,
           fontweight='bold', color='white')
    ax.text(7, 2.4, '• Optimized weights  • Phase 3.2 improvements',
           ha='center', fontsize=8, color='white')
    
    # Arrows
    arrow_props = dict(arrowstyle='->', lw=2.5, color='black')
    ax.annotate('', xy=(3.5, 6), xytext=(3.5, 8), arrowprops=arrow_props)
    ax.annotate('', xy=(10.5, 6), xytext=(10.5, 8), arrowprops=arrow_props)
    ax.annotate('', xy=(7, 3.8), xytext=(7, 6), 
               arrowprops=dict(arrowstyle='->', lw=3, color='gold'))
    ax.annotate('', xy=(7, 2), xytext=(7, 3.3), arrowprops=arrow_props)
    
    # Results box
    results = Rectangle((0.5, 0.2), 13, 0.6, facecolor='lightgreen',
                       edgecolor='black', linewidth=2, alpha=0.7)
    ax.add_patch(results)
    ax.text(7, 0.5, '🎯 Target: 95-100% Extrapolation R² (vs 60% baseline) | ✅ Fixes Priority 1 Weakness',
           ha='center', fontsize=9, fontweight='bold')
    
    plt.tight_layout()
    plt.savefig('architecture0_system1.pdf', bbox_inches='tight')
    plt.savefig('architecture0_system1.png', bbox_inches='tight', dpi=300)
    print("✓ Created architecture0_system1.pdf/png")
    return fig

def create_system2_architecture():
    """System 2: Symbolic Discovery + Validation - DOESN'T FIX THE WEAKNESS"""
    fig, ax = plt.subplots(figsize=(14, 12))
    ax.set_xlim(0, 14)
    ax.set_ylim(0, 12)
    ax.axis('off')
    
    # Title
    ax.text(7, 11.5, 'System 2: Symbolic Discovery + Validation',
            ha='center', fontsize=14, fontweight='bold')
    ax.text(7, 11, '❌ Does NOT Fix Extrapolation | complete_defi_hybrid_system.py',
           ha='center', fontsize=10, style='italic', color=COLORS['broken'])
    
    # Main container
    main_box = FancyBboxPatch((0.5, 1), 13, 9.5, boxstyle="round,pad=0.2",
                              facecolor='white', edgecolor='black', linewidth=3)
    ax.add_patch(main_box)
    
    # Layer 1: Symbolic Regression Engine
    symbolic_box = FancyBboxPatch((2, 8.5), 10, 1.8, boxstyle="round,pad=0.15",
                                  facecolor=COLORS['symbolic'], edgecolor='black',
                                  linewidth=2, alpha=0.8)
    ax.add_patch(symbolic_box)
    ax.text(7, 9.8, 'Symbolic Regression Engine', ha='center',
           fontsize=11, fontweight='bold', color='white')
    ax.text(7, 9.4, '(PySR, gplearn, or custom symbolic search)',
           ha='center', fontsize=9, color='white')
    ax.text(7, 9, '• Discovers formulas  • No LLM vs NN decision',
           ha='center', fontsize=8, color='white')
    
    # Layer 2: 4-Layer Validation System (THE FOCUS)
    validation_box = FancyBboxPatch((1.5, 4), 11, 4, boxstyle="round,pad=0.2",
                                    facecolor=COLORS['validation'], edgecolor='black',
                                    linewidth=3, alpha=0.3)
    ax.add_patch(validation_box)
    ax.text(7, 7.7, '4-Layer Validation System', ha='center',
           fontsize=12, fontweight='bold', color=COLORS['validation'])
    
    # Validation layers
    layers = [
        (7.2, 'Layer 1: Symbolic Validation (30%)', '• Parses formula  • Checks syntax'),
        (6.4, 'Layer 2: Dimensional Analysis (30%)', '• Unit consistency  • Physics checks'),
        (5.6, 'Layer 3: Domain Knowledge (30%)', '• DeFi-specific rules  • Constraints'),
        (4.8, 'Layer 4: Numerical Validation (10%)', '• Edge cases  • Division by zero'),
    ]
    
    for y, title, desc in layers:
        layer_box = FancyBboxPatch((2, y-0.3), 10, 0.5, boxstyle="round,pad=0.05",
                                   facecolor='white', edgecolor=COLORS['validation'],
                                   linewidth=1.5, alpha=0.9)
        ax.add_patch(layer_box)
        ax.text(2.5, y, title, ha='left', fontsize=9, fontweight='bold',
               color=COLORS['validation'])
        ax.text(11.5, y, desc, ha='right', fontsize=7, style='italic', color='gray')
        ax.text(2.2, y, '✓', ha='left', fontsize=10, color='green', fontweight='bold')
    
    # Layer 3: LLM Interpretation (Optional)
    llm_box = FancyBboxPatch((3, 2.2), 8, 1.3, boxstyle="round,pad=0.15",
                             facecolor=COLORS['llm'], edgecolor='black',
                             linewidth=2, linestyle='--', alpha=0.5)
    ax.add_patch(llm_box)
    ax.text(7, 3, 'LLM Interpretation (Optional)', ha='center',
           fontsize=10, fontweight='bold', color=COLORS['llm'])
    ax.text(7, 2.6, '• Formula naming  • Domain insights  • Use cases',
           ha='center', fontsize=8, color=COLORS['llm'])
    
    # Arrows
    ax.annotate('', xy=(7, 8), xytext=(7, 8.5), 
               arrowprops=dict(arrowstyle='->', lw=2.5, color='black'))
    ax.annotate('', xy=(7, 2.2), xytext=(7, 4),
               arrowprops=dict(arrowstyle='->', lw=2, color='black', linestyle='--'))
    
    # Warning box (what it DOESN'T do)
    warning = Rectangle((0.5, 0.2), 13, 0.6, facecolor='#FFEBEE',
                       edgecolor=COLORS['broken'], linewidth=2, alpha=0.7)
    ax.add_patch(warning)
    ax.text(7, 0.5, '⚠️ Target: 85+ validation score | ❌ NOT designed for extrapolation performance',
           ha='center', fontsize=9, fontweight='bold', color=COLORS['broken'])
    
    plt.tight_layout()
    plt.savefig('architecture0_system2.pdf', bbox_inches='tight')
    plt.savefig('architecture0_system2.png', bbox_inches='tight', dpi=300)
    print("✓ Created architecture0_system2.pdf/png")
    return fig

def create_comparison_chart():
    """Comparison chart showing which system fixes the weakness"""
    fig, ax = plt.subplots(figsize=(16, 10))
    ax.set_xlim(0, 16)
    ax.set_ylim(0, 10)
    ax.axis('off')
    
    # Title
    ax.text(8, 9.5, 'Architecture Comparison: Which System Fixes the Weakness?',
            ha='center', fontsize=14, fontweight='bold')
    ax.text(8, 9, 'Critical Issue: Hybrid extrapolation 60% R² vs Pure LLM 100% R²',
           ha='center', fontsize=11, style='italic', color='red')
    
    # System 1 Column (LEFT - FIXES IT)
    system1_box = Rectangle((0.5, 1), 7, 7.5, facecolor='lightgreen',
                           edgecolor=COLORS['fixed'], linewidth=4, alpha=0.2)
    ax.add_patch(system1_box)
    
    ax.text(4, 8.2, 'System 1: Improved Hybrid', ha='center',
           fontsize=12, fontweight='bold', color=COLORS['fixed'])
    ax.text(4, 7.8, '✅ FIXES THE WEAKNESS', ha='center',
           fontsize=11, fontweight='bold', color=COLORS['fixed'],
           bbox=dict(boxstyle='round', facecolor='lightgreen', alpha=0.8))
    
    system1_features = [
        ('✅', 'Extrapolation-aware decision', 'Priority 1 fix'),
        ('✅', 'Pattern recognition', 'Phase 1.3'),
        ('✅', 'Few-shot prompting', 'Phase 2.1'),
        ('✅', 'Iterative refinement', 'Phase 2.2'),
        ('✅', 'Optimized ensemble', 'Phase 3.2'),
        ('✅', 'LLM preference logic', 'if is_extrap: use LLM'),
        ('', '', ''),
        ('🎯', 'Target: 90-100% R²', 'vs 60% baseline'),
    ]
    
    y = 7
    for check, feature, detail in system1_features:
        if check:
            ax.text(1, y, check, ha='left', fontsize=11, fontweight='bold',
                   color='green' if check == '✅' else 'red')
            ax.text(1.5, y, feature, ha='left', fontsize=9, fontweight='bold')
            ax.text(6.8, y, detail, ha='right', fontsize=7, 
                   style='italic', color='gray')
        y -= 0.6
    
    # System 2/3 Column (RIGHT - DOESN'T FIX IT)
    system2_box = Rectangle((8.5, 1), 7, 7.5, facecolor='#FFEBEE',
                           edgecolor=COLORS['broken'], linewidth=4, alpha=0.2)
    ax.add_patch(system2_box)
    
    ax.text(12, 8.2, 'System 2/3: Symbolic Discovery', ha='center',
           fontsize=12, fontweight='bold', color=COLORS['broken'])
    ax.text(12, 7.8, '❌ Does NOT Fix Weakness', ha='center',
           fontsize=11, fontweight='bold', color=COLORS['broken'],
           bbox=dict(boxstyle='round', facecolor='#FFEBEE', alpha=0.8))
    
    system2_features = [
        ('❌', 'No extrapolation logic', 'Different architecture'),
        ('❌', 'No LLM vs NN decision', 'Only validates formulas'),
        ('❌', 'No pattern recognition', 'N/A'),
        ('❌', 'No few-shot prompting', 'N/A'),
        ('❌', 'No ensemble optimization', 'N/A'),
        ('✅', '4-Layer validation', 'But different goal'),
        ('', '', ''),
        ('🎯', 'Target: 85+ validation', 'NOT extrapolation R²'),
    ]
    
    y = 7
    for check, feature, detail in system2_features:
        if check:
            ax.text(9, y, check, ha='left', fontsize=11, fontweight='bold',
                   color='green' if check == '✅' else 'red')
            ax.text(9.5, y, feature, ha='left', fontsize=9, fontweight='bold')
            ax.text(14.8, y, detail, ha='right', fontsize=7,
                   style='italic', color='gray')
        y -= 0.6
    
    # Key differences box
    key_box = Rectangle((1, 0.2), 14, 0.6, facecolor='lightyellow',
                       edgecolor='black', linewidth=2, alpha=0.8)
    ax.add_patch(key_box)
    ax.text(8, 0.5, '🔑 Key: System 1 chooses WHEN to use LLM vs NN | System 2/3 only validate ONE discovered formula',
           ha='center', fontsize=9, fontweight='bold')
    
    plt.tight_layout()
    plt.savefig('architecture0_comparison.pdf', bbox_inches='tight')
    plt.savefig('architecture0_comparison.png', bbox_inches='tight', dpi=300)
    print("✓ Created architecture0_comparison.pdf/png")
    return fig

def create_decision_flow():
    """Decision flow showing System 1's critical logic"""
    fig, ax = plt.subplots(figsize=(14, 10))
    ax.set_xlim(0, 14)
    ax.set_ylim(0, 10)
    ax.axis('off')
    
    ax.text(7, 9.5, 'System 1: Extrapolation-Aware Decision Flow',
            ha='center', fontsize=14, fontweight='bold')
    ax.text(7, 9, 'Why it fixes the 60% → 100% extrapolation gap',
           ha='center', fontsize=10, style='italic', color=COLORS['fixed'])
    
    # Start
    start = Circle((7, 8), 0.4, facecolor='lightblue', edgecolor='black', linewidth=2)
    ax.add_patch(start)
    ax.text(7, 8, 'START', ha='center', va='center', fontsize=9, fontweight='bold')
    
    # Decision 1: Is Extrapolation?
    decision1 = FancyBboxPatch((5, 6.5), 4, 1, boxstyle="round,pad=0.1",
                               facecolor='lightyellow', edgecolor='black', linewidth=2)
    ax.add_patch(decision1)
    ax.text(7, 7.2, 'is_extrapolation?', ha='center', fontsize=10, fontweight='bold')
    ax.text(7, 6.8, '(Outside training range)', ha='center', fontsize=7, style='italic')
    
    # Arrow to decision1
    ax.annotate('', xy=(7, 7), xytext=(7, 7.6),
               arrowprops=dict(arrowstyle='->', lw=2, color='black'))
    
    # Branch: NO (interpolation)
    interp_box = FancyBboxPatch((0.5, 4.5), 3.5, 1.5, boxstyle="round,pad=0.1",
                                facecolor='lightgray', edgecolor='black', linewidth=2)
    ax.add_patch(interp_box)
    ax.text(2.25, 5.5, 'NO: Interpolation', ha='center', fontsize=9, fontweight='bold')
    ax.text(2.25, 5.1, 'Use standard logic', ha='center', fontsize=8)
    ax.text(2.25, 4.8, '(NN often good)', ha='center', fontsize=7, style='italic')
    
    ax.annotate('', xy=(2.25, 6), xytext=(5, 7),
               arrowprops=dict(arrowstyle='->', lw=2, color='gray'))
    ax.text(3, 6.8, 'NO', ha='center', fontsize=8, bbox=dict(boxstyle='round', 
           facecolor='white', edgecolor='gray'))
    
    # Branch: YES (extrapolation) - THE CRITICAL PATH
    extrap_box = FancyBboxPatch((5.5, 4.5), 7.5, 1.5, boxstyle="round,pad=0.1",
                                facecolor='lightcoral', edgecolor='red', linewidth=3)
    ax.add_patch(extrap_box)
    ax.text(9.25, 5.7, '⭐ YES: Extrapolation (CRITICAL)', ha='center',
           fontsize=9, fontweight='bold', color='red')
    ax.text(9.25, 5.3, 'Check LLM performance', ha='center', fontsize=8)
    ax.text(9.25, 4.9, 'Prefer LLM if R² > threshold', ha='center', fontsize=8)
    
    ax.annotate('', xy=(9.25, 6), xytext=(9, 7),
               arrowprops=dict(arrowstyle='->', lw=3, color='red'))
    ax.text(9.5, 6.8, 'YES', ha='center', fontsize=8, fontweight='bold',
           bbox=dict(boxstyle='round', facecolor='yellow', edgecolor='red'))
    
    # LLM performance checks
    checks = [
        (3.5, 'llm_r2 > 0.90?', 'STRONG: Use LLM', 'green'),
        (2.5, 'llm_r2 > 0.70?', 'PREFER: Use LLM', 'orange'),
        (1.5, 'llm_r2 > 0.50?', 'SAFER: Use LLM', 'coral'),
    ]
    
    for y, condition, action, color in checks:
        check_box = FancyBboxPatch((6, y-0.2), 6, 0.5, boxstyle="round,pad=0.05",
                                   facecolor=color, edgecolor='black', linewidth=1, alpha=0.6)
        ax.add_patch(check_box)
        ax.text(6.5, y, condition, ha='left', fontsize=8, fontweight='bold')
        ax.text(11.5, y, action, ha='right', fontsize=8, style='italic', color='white')
    
    # Result
    result = Rectangle((4, 0.3), 6, 0.7, facecolor='lightgreen',
                      edgecolor='black', linewidth=2)
    ax.add_patch(result)
    ax.text(7, 0.65, '✅ Result: 90-100% Extrapolation R² (vs 60% baseline)',
           ha='center', fontsize=10, fontweight='bold')
    
    # Code snippet
    code_box = FancyBboxPatch((0.5, 0.3), 3, 0.7, boxstyle="round,pad=0.05",
                              facecolor='black', edgecolor='gold', linewidth=2, alpha=0.8)
    ax.add_patch(code_box)
    ax.text(2, 0.75, 'if is_extrap and', ha='center', fontsize=7,
           family='monospace', color='yellow')
    ax.text(2, 0.55, '  llm_r2 > 0.90:', ha='center', fontsize=7,
           family='monospace', color='yellow')
    ax.text(2, 0.35, '  return "llm"', ha='center', fontsize=7,
           family='monospace', color='lightgreen')
    
    plt.tight_layout()
    plt.savefig('architecture0_decision_flow.pdf', bbox_inches='tight')
    plt.savefig('architecture0_decision_flow.png', bbox_inches='tight', dpi=300)
    print("✓ Created architecture0_decision_flow.pdf/png")
    return fig

if __name__ == '__main__':
    print("Generating Hybrid Systems Architecture Diagrams...")
    print()
    
    create_system1_architecture()
    plt.close()
    
    create_system2_architecture()
    plt.close()
    
    create_comparison_chart()
    plt.close()
    
    create_decision_flow()
    plt.close()
    
    print()
    print("✅ All diagrams created!")
    print()
    print("Generated files:")
    print("  • architecture0_system1.pdf/png       - System 1: Improved Hybrid (FIXES weakness)")
    print("  • architecture0_system2.pdf/png       - System 2: Symbolic Discovery (different goal)")
    print("  • architecture0_comparison.pdf/png    - Side-by-side comparison")
    print("  • architecture0_decision_flow.pdf/png - System 1's critical decision logic")
    print()
    print("📊 Key Insight:")
    print("   System 1: LLM + NN with extrapolation-aware decision → FIXES 60% → 100% gap")
    print("   System 2/3: Symbolic validation → Different use case, doesn't fix weakness")

    """
    Perfect! I've created a comprehensive architecture visualization script for your three hybrid systems. This generates 4 diagrams that clearly show:
Generated Diagrams

architecture0_system1.pdf/png - System 1: Improved Hybrid

Shows LLM + NN architecture
Highlights the ⭐ EXTRAPOLATION-AWARE DECISION layer (the critical fix)
Gold star annotation for the fix
Shows the code: if is_extrap and llm_r2 > 0.90: return "llm"
Target: 95-100% extrapolation R²


architecture0_system2.pdf/png - System 2: Symbolic Discovery

Shows symbolic regression engine
4-layer validation system (the focus)
Optional LLM interpretation
Warning that it does NOT fix extrapolation
Target: 85+ validation score (different goal)


architecture0_comparison.pdf/png - Side-by-side comparison

Left column: System 1 features (all ✅ green checks)
Right column: System 2/3 features (mostly ❌ red X's for extrapolation)
Key insight box explaining the fundamental difference


architecture0_decision_flow.pdf/png - System 1's critical logic

Flowchart showing the extrapolation decision path
Highlights the three LLM preference thresholds (>0.90, >0.70, >0.50)
Shows why it fixes the 60% → 100% gap
Includes code snippet



Usage
bashpython generate_hybrid_architecture.py
Key Visual Elements

Gold stars ⭐ highlight the critical fix
Color coding: Green (fixes it), Red (doesn't fix it)
Code snippets in monospace font showing actual logic
Clear labeling of what each system does/doesn't do
Performance targets clearly stated

This makes it crystal clear that only System 1 fixes the evaluation report weakness!
 """
