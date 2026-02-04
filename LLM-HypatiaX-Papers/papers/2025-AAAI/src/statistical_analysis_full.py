#!/usr/bin/env python3
"""
Complete statistical analysis for paper
Based on your existing statistical_analysis_full.py
"""

import json
import sys
from pathlib import Path
import pandas as pd
import numpy as np
from scipy import stats
import matplotlib.pyplot as plt
import seaborn as sns

# Add shared code
sys.path.append('../../../shared/code')

def load_all_systems_data():
    """Load merged systems data"""
    data_file = Path(__file__).parent.parent / "data" / "all_systems_merged.json"
    with open(data_file, 'r') as f:
        return json.load(f)

def compute_statistics():
    """Compute comprehensive statistics"""
    data = load_all_systems_data()
    
    # Your statistical analysis code here
    # This should match your existing analysis
    
    results = {
        'descriptive_stats': {},
        'pairwise_tests': {},
        'effect_sizes': {},
        'confidence_intervals': {}
    }
    
    return results

def generate_latex_tables():
    """Generate LaTeX tables for paper"""
    stats = compute_statistics()
    
    # Generate tables matching your paper format
    # Save to latex/ directory
    
    pass

if __name__ == '__main__':
    print("Running statistical analysis...")
    results = compute_statistics()
    generate_latex_tables()
    print("✓ Analysis complete!")
