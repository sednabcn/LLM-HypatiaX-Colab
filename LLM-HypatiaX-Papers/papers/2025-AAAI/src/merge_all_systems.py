#!/usr/bin/env python3
"""
Merge results from all systems into unified format
Based on your existing merge scripts
"""

import json
import sys
from pathlib import Path

def merge_system_results():
    """Merge all system results"""
    
    # Paths to different system results
    results_dir = Path(__file__).parent.parent.parent.parent / "shared" / "results"
    
    systems = {
        'llm': results_dir / 'baseline_nn_pure_llm',
        'nn': results_dir / 'baseline_nn_pure_llm',
        'hybrid_llm_nn': results_dir / 'hybrid_llm_nn',
        'llm_guided': results_dir / 'llm_guided',
        'pysr': results_dir / 'hybrid_pysr'
    }
    
    merged = {}
    
    # Your merging logic here
    # This should match your existing merge_all_systems.py
    
    # Save merged results
    output_path = Path(__file__).parent.parent / "data" / "all_systems_merged.json"
    with open(output_path, 'w') as f:
        json.dump(merged, f, indent=2)
    
    print(f"✓ Merged data saved to: {output_path}")

if __name__ == '__main__':
    merge_system_results()
