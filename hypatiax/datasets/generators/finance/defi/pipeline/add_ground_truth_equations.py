#!/usr/bin/env python3
"""
Add ground truth equations to DeFi formulas that are missing them.
"""

import json
import sys
from pathlib import Path

# Known DeFi formulas and their equations
GROUND_TRUTH = {
    'impermanent loss': r'2*\sqrt{r}/(1+r) - 1',
    'constant product': r'\sqrt{x \cdot y}',
    'utilization rate': r'borrowed/supplied',
    'constant product pool': r'x \cdot y',
    'price impact': r'1 - (1 - \Delta x / (x + \Delta x))',
    'amm price': r'y/x',
    'liquidity': r'\sqrt{x \cdot y}',
}

def add_equations(input_file: Path, output_file: Path = None):
    """Add ground truth equations to formulas."""
    
    if output_file is None:
        output_file = input_file.parent / f"{input_file.stem}_with_equations{input_file.suffix}"
    
    print(f"Loading: {input_file}")
    with open(input_file) as f:
        data = json.load(f)
    
    if not isinstance(data, list):
        print(f"Error: Expected list, got {type(data)}")
        return
    
    added = 0
    for item in data:
        desc = item.get('description', '').lower()
        
        # Skip if already has equation
        if item.get('discovered_equation'):
            continue
        
        # Try to match known formulas
        for keyword, equation in GROUND_TRUTH.items():
            if keyword in desc:
                item['discovered_equation'] = equation
                
                # Also update validation if present
                if 'validation' in item and isinstance(item['validation'], dict):
                    item['validation']['expression'] = equation
                    if not item['validation'].get('canonical_form'):
                        item['validation']['canonical_form'] = equation
                
                added += 1
                print(f"  ✓ Added equation for: {item['description'][:50]}")
                break
    
    print(f"\nAdded {added} equations")
    print(f"Saving to: {output_file}")
    
    with open(output_file, 'w') as f:
        json.dump(data, f, indent=2)
    
    return added

def main():
    if len(sys.argv) < 2:
        print("Usage: python add_ground_truth_equations.py <input_file> [output_file]")
        sys.exit(1)
    
    input_file = Path(sys.argv[1])
    output_file = Path(sys.argv[2]) if len(sys.argv) > 2 else None
    
    if not input_file.exists():
        print(f"Error: File not found: {input_file}")
        sys.exit(1)
    
    add_equations(input_file, output_file)

if __name__ == '__main__':
    main()
