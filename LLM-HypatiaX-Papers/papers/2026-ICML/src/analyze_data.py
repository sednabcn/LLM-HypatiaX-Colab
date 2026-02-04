#!/usr/bin/env python3
"""
Data analysis for the paper
"""

import json
from pathlib import Path

DATA_DIR = Path(__file__).parent.parent / "data"

def analyze():
    """Run statistical analysis"""
    data_file = DATA_DIR / "all_systems_merged.json"
    
    if not data_file.exists():
        print(f"Data file not found: {data_file}")
        print("Please link the shared data first:")
        print(f"  cd {DATA_DIR} && ln -s ../../../shared/data/all_systems_merged.json .")
        return
    
    with open(data_file, 'r') as f:
        data = json.load(f)
    
    print(f"Loaded data with {len(data)} items")
    # Add your analysis here

if __name__ == '__main__':
    analyze()
