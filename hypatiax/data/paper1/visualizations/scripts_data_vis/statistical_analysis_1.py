#!/usr/bin/env python3
"""
BULLETPROOF Statistical Analysis - Handles Any JSON Structure
"""

import json
import numpy as np
import pandas as pd
from scipy.stats import mannwhitneyu
import matplotlib.pyplot as plt
import seaborn as sns
from pathlib import Path

# Set publication-quality defaults
plt.rcParams['figure.dpi'] = 300
plt.rcParams['savefig.dpi'] = 300
plt.rcParams['font.size'] = 10
plt.rcParams['font.family'] = 'serif'
plt.rcParams['figure.figsize'] = (14, 8)
plt.rcParams['savefig.bbox'] = 'tight'
plt.rcParams['pdf.compression'] = 6
sns.set_style("whitegrid")


def safe_get(data, key, default=None):
    """Safely get value from dict."""
    return data.get(key, default) if isinstance(data, dict) else default


def main():
    """Main analysis function."""
    print("=" * 80)
    print("BULLETPROOF STATISTICAL ANALYSIS")
    print("=" * 80)
    print()
    
    current_dir = Path.cwd()
    output_dir = current_dir / "figures"
    output_dir.mkdir(exist_ok=True)
    
    # Try to load all available files
    files_to_try = {
        'extrapolation': [
            "all_domains_extrap_v4_20260124_131545.json",
            "all_domains_extrap_v4_20260120_223747.json"
        ],
        'interpolation': [
            "results_20260125_031224.json",
            "all_systems_merged.json",
            "standalone_real_methods_20260116_003311.json"
        ],
        'systems': [
            "systems_2_3_2_data.json",
            "systems_2_3_data.json"
        ]
    }
    
    loaded_data = {}
    
    print("Loading data files...")
    print("-" * 80)
    
    for category, filenames in files_to_try.items():
        for filename in filenames:
            filepath = current_dir / filename
            if filepath.exists():
                try:
                    with open(filepath, 'r') as f:
                        data = json.load(f)
                    loaded_data[category] = data
                    print(f"✅ {category:15s}: {filename}")
                    break
                except Exception as e:
                    print(f"⚠️  {category:15s}: {filename} - {e}")
        
        if category not in loaded_data:
            print(f"❌ {category:15s}: No valid file found")
    
    print()
    
    if not loaded_data:
        print("❌ ERROR: No data files could be loaded!")
        return
    
    # Extract results
    print("Extracting data...")
    print("-" * 80)
    
    results = {
        "Hybrid_v40": {"r2": [], "extrap": []},
        "Neural_Network": {"r2": [], "extrap": []},
        "Pure_LLM": {"r2": [], "extrap": []},
        "System_3": {"r2": [], "extrap": []},
        "System_2": {"r2": [], "extrap": []}
    }
    
    method_mappings = {
        "Hybrid System v40": "Hybrid_v40",
        "Hybrid_v40": "Hybrid_v40",
        "Neural Network": "Neural_Network",
        "Neural_Network": "Neural_Network",
        "Pure LLM": "Pure_LLM",
        "Pure_LLM": "Pure_LLM",
        "System 3 LLM+Fallback": "System_3",
        "System_3": "System_3",
        "System 2 Symbolic": "System_2",
        "System_2": "System_2"
    }
    
    # Process each loaded data file
    for category, data in loaded_data.items():
        print(f"\nProcessing {category} data...")
        
        # Handle different JSON structures
        tests = []
        
        # Structure 1: data['tests'] is an array
        if 'tests' in data and isinstance(data['tests'], list):
            tests = data['tests']
        
        # Structure 2: data itself is an array
        elif isinstance(data, list):
            tests = data
        
        # Structure 3: data has a 'results' key
        elif 'results' in data:
            if isinstance(data['results'], dict):
                # Convert dict to list of tests
                for test_name, test_data in data['results'].items():
                    tests.append({
                        'test_name': test_name,
                        'results': test_data if isinstance(test_data, dict) else {}
                    })
            elif isinstance(data['results'], list):
                tests = data['results']
        
        print(f"  Found {len(tests)} test entries")
        
        # Extract data from each test
        for test in tests:
            if not isinstance(test, dict):
                continue
            
            # Get test results (different possible structures)
            test_results = safe_get(test, 'results', {})
            
            # If test itself contains method data directly
            if not test_results:
                test_results = {k: v for k, v in test.items() 
                              if isinstance(v, dict) and 'r2' in v or 'medium_2x' in v}
            
            # Process each method in the test
            for method_name, result_data in test_results.items():
                if not isinstance(result_data, dict):
                    continue
                
                # Map to our standard names
                standard_name = method_mappings.get(method_name)
                if not standard_name:
                    continue
                
                # Extract R² score (try multiple possible keys)
                r2 = (result_data.get('r2') or 
                      result_data.get('r2_score') or 
                      result_data.get('train_r2'))
                
                if r2 is not None and r2 != float('inf') and not np.isnan(r2):
                    results[standard_name]['r2'].append(float(r2))
                
                # Extract extrapolation error (try multiple possible keys)
                extrap = (result_data.get('medium_2x') or 
                         result_data.get('extrapolation_error') or
                         result_data.get('extrap_error'))
                
                if extrap is not None and extrap != float('inf') and not np.isnan(extrap):
                    results[standard_name]['extrap'].append(float(extrap))
    
    # Print summary
    print()
    print("=" * 80)
    print("DATA SUMMARY")
    print("=" * 80)
    print()
    
    for system, data in results.items():
        if data['r2'] or data['extrap']:
            print(f"{system}:")
            if data['r2']:
                print(f"  R² scores: {len(data['r2'])} values (mean: {np.mean(data['r2']):.4f})")
            if data['extrap']:
                print(f"  Extrapolation errors: {len(data['extrap'])} values (mean: {np.mean(data['extrap']):.2f}%)")
    
    print()
    print("=" * 80)
    print("GENERATING FIGURE")
    print("=" * 80)
    print()
    
    # Create the figure
    fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(14, 6))
    
    # LEFT PANEL: Extrapolation Performance
    extrap_data_plot = []
    extrap_labels = []
    extrap_colors = []
    
    if results['Hybrid_v40']['extrap']:
        extrap_data_plot.append(results['Hybrid_v40']['extrap'])
        extrap_labels.append('Hybrid v40')
        extrap_colors.append('blue')
    
    if results['Neural_Network']['extrap']:
        extrap_data_plot.append(results['Neural_Network']['extrap'])
        extrap_labels.append('Neural\nNetwork')
        extrap_colors.append('red')
    
    if extrap_data_plot:
        positions = list(range(1, len(extrap_data_plot) + 1))
        bp1 = ax1.boxplot(extrap_data_plot, positions=positions, widths=0.5,
                          patch_artist=True, labels=extrap_labels)
        
        for patch, color in zip(bp1['boxes'], extrap_colors):
            patch.set_facecolor(color)
            patch.set_alpha(0.7)
        
        ax1.set_ylabel('Extrapolation Error (%)', fontsize=11)
        ax1.set_title('Extrapolation Performance\n(2× training range)', 
                     fontsize=12, fontweight='bold')
        ax1.set_yscale('log')
        ax1.grid(True, alpha=0.3, axis='y')
        
        # Add statistics if we have 2 groups
        if len(extrap_data_plot) == 2:
            try:
                U, p = mannwhitneyu(extrap_data_plot[0], extrap_data_plot[1], 
                                   alternative='less')
                ax1.text(0.5, 0.95, f'Mann-Whitney U = {U:.0f}, p = {p:.2e}',
                        transform=ax1.transAxes, fontsize=9,
                        verticalalignment='top', bbox=dict(boxstyle='round', 
                        facecolor='wheat', alpha=0.5))
            except:
                pass
    else:
        ax1.text(0.5, 0.5, 'No extrapolation data available',
                ha='center', va='center', transform=ax1.transAxes, fontsize=12)
        ax1.set_xlim(0, 2)
        ax1.set_ylim(0, 1)
    
    # RIGHT PANEL: Interpolation Performance (R²)
    interp_data_plot = []
    interp_labels = []
    interp_colors = []
    
    systems_to_plot = [
        ('Hybrid_v40', 'Hybrid v40', 'blue'),
        ('System_3', 'System 3\nLLM+Fallback', 'purple'),
        ('Neural_Network', 'Neural\nNetwork', 'red'),
        ('Pure_LLM', 'Pure LLM', 'green')
    ]
    
    for key, label, color in systems_to_plot:
        if results[key]['r2']:
            interp_data_plot.append(results[key]['r2'])
            interp_labels.append(label)
            interp_colors.append(color)
    
    if interp_data_plot:
        positions2 = list(range(1, len(interp_data_plot) + 1))
        bp2 = ax2.boxplot(interp_data_plot, positions=positions2, widths=0.5,
                          patch_artist=True, labels=interp_labels)
        
        for patch, color in zip(bp2['boxes'], interp_colors):
            patch.set_facecolor(color)
            patch.set_alpha(0.7)
        
        ax2.set_ylabel('R² Score', fontsize=11)
        ax2.set_title('Interpolation Performance', 
                     fontsize=12, fontweight='bold')
        
        # Set y-axis limits based on data
        all_r2 = [val for sublist in interp_data_plot for val in sublist]
        min_r2 = min(all_r2)
        y_min = max(0.0, min_r2 - 0.1)
        ax2.set_ylim([y_min, 1.01])
        ax2.grid(True, alpha=0.3, axis='y')
    else:
        ax2.text(0.5, 0.5, 'No interpolation data available',
                ha='center', va='center', transform=ax2.transAxes, fontsize=12)
        ax2.set_xlim(0, 2)
        ax2.set_ylim(0, 1)
    
    plt.tight_layout()
    
    # Save the figure
    pdf_file = output_dir / "figure_5systems_comparison.pdf"
    png_file = output_dir / "figure_5systems_comparison.png"
    
    print("Saving figures...")
    plt.savefig(pdf_file, format='pdf', bbox_inches='tight', 
                dpi=300, metadata={'Creator': 'Matplotlib', 'Title': 'Five Systems Comparison'})
    plt.savefig(png_file, format='png', bbox_inches='tight', dpi=300)
    plt.close()
    
    print(f"✅ Saved: {pdf_file}")
    print(f"✅ Saved: {png_file}")
    
    # Verify files
    print()
    print("Verifying output files:")
    print(f"  PDF size: {pdf_file.stat().st_size / 1024:.1f} KB")
    print(f"  PNG size: {png_file.stat().st_size / 1024:.1f} KB")
    
    print()
    print("=" * 80)
    print("✅ ANALYSIS COMPLETE")
    print("=" * 80)
    print()
    print("Next steps:")
    print("1. Verify PDF: pdfinfo figures/figure_5systems_comparison.pdf")
    print("2. View figure: evince figures/figure_5systems_comparison.pdf &")
    print("3. Compile paper: cd ~/Downloads/GITHUB/LLM-HypatiaX-Colab/paper && make clean && make")
    print()


if __name__ == '__main__':
    try:
        main()
    except Exception as e:
        print(f"\n❌ Error: {e}")
        import traceback
        traceback.print_exc()
        exit(1)
