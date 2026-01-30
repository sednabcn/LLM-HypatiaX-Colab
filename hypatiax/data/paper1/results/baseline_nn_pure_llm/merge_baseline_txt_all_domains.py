"""
Merge ALL domain baseline results for comprehensive comparison
"""

import json
from pathlib import Path
from collections import defaultdict

def load_json(filepath):
    """Load JSON file."""
    with open(filepath, 'r') as f:
        return json.load(f)

def main():
    results_dir = Path('results')
    
    # Define file patterns for each domain set
    file_mapping = {
        'llm': {
            'defi': 'baseline_llm_FIXED_20251220_235258.json',  # Has defi domains
            'physics': 'baseline_pure_llm_20251220_152604.json'  # Has physics domains
        },
        'nn': {
            'defi': 'baseline_nn_defi_20251220_162650.json',  # Has defi domains  
            'physics': 'baseline_neural_network_20251220_144434.json'  # Has physics domains
        }
    }
    
    print("="*80)
    print("MERGING ALL DOMAIN BASELINES FOR COMPREHENSIVE COMPARISON")
    print("="*80)
    
    # Merge LLM results
    print("\n📊 Merging LLM results...")
    all_llm = []
    llm_domains = set()
    
    for domain_type, filename in file_mapping['llm'].items():
        filepath = results_dir / filename
        if filepath.exists():
            print(f"  Loading {filename}...")
            data = load_json(filepath)
            if isinstance(data, list):
                all_llm.extend(data)
                domains = set(item.get('domain', 'unknown') for item in data)
                llm_domains.update(domains)
                print(f"    ✅ Added {len(data)} cases from {domain_type}: {sorted(domains)}")
        else:
            print(f"    ⚠️  File not found: {filename}")
    
    # Merge NN results
    print("\n📊 Merging NN results...")
    all_nn = []
    nn_domains = set()
    
    for domain_type, filename in file_mapping['nn'].items():
        filepath = results_dir / filename
        if filepath.exists():
            print(f"  Loading {filename}...")
            data = load_json(filepath)
            if isinstance(data, list):
                all_nn.extend(data)
                domains = set(item.get('domain', 'unknown') for item in data)
                nn_domains.update(domains)
                print(f"    ✅ Added {len(data)} cases from {domain_type}: {sorted(domains)}")
        else:
            print(f"    ⚠️  File not found: {filename}")
    
    # Find common domains
    common_domains = llm_domains & nn_domains
    llm_only = llm_domains - nn_domains
    nn_only = nn_domains - llm_domains
    
    print("\n" + "="*80)
    print("DOMAIN ANALYSIS")
    print("="*80)
    print(f"\n✅ Common domains ({len(common_domains)}): {sorted(common_domains)}")
    if llm_only:
        print(f"⚠️  LLM-only domains: {sorted(llm_only)}")
    if nn_only:
        print(f"⚠️  NN-only domains: {sorted(nn_only)}")
    
    # Filter to common domains only
    llm_filtered = [item for item in all_llm if item.get('domain') in common_domains]
    nn_filtered = [item for item in all_nn if item.get('domain') in common_domains]
    
    # Get counts per domain
    llm_counts = defaultdict(int)
    for item in llm_filtered:
        llm_counts[item.get('domain', 'unknown')] += 1
    
    nn_counts = defaultdict(int)
    for item in nn_filtered:
        nn_counts[item.get('domain', 'unknown')] += 1
    
    print("\n" + "="*80)
    print("TEST CASE COUNTS PER DOMAIN")
    print("="*80)
    print(f"{'Domain':<25} {'LLM Cases':>15} {'NN Cases':>15}")
    print("-"*80)
    
    total_llm = 0
    total_nn = 0
    for domain in sorted(common_domains):
        llm_count = llm_counts[domain]
        nn_count = nn_counts[domain]
        total_llm += llm_count
        total_nn += nn_count
        print(f"{domain:<25} {llm_count:>15} {nn_count:>15}")
    
    print("-"*80)
    print(f"{'TOTAL':<25} {total_llm:>15} {total_nn:>15}")
    
    # Save merged files
    output_llm = results_dir / 'baseline_llm_ALL_DOMAINS.json'
    output_nn = results_dir / 'baseline_nn_ALL_DOMAINS.json'
    
    with open(output_llm, 'w') as f:
        json.dump(llm_filtered, f, indent=2)
    
    with open(output_nn, 'w') as f:
        json.dump(nn_filtered, f, indent=2)
    
    print("\n" + "="*80)
    print("FILES SAVED")
    print("="*80)
    print(f"✅ {output_llm}")
    print(f"   {len(llm_filtered)} test cases across {len(common_domains)} domains")
    print(f"\n✅ {output_nn}")
    print(f"   {len(nn_filtered)} test cases across {len(common_domains)} domains")
    
    print("\n" + "="*80)
    print("READY FOR COMPARISON")
    print("="*80)
    print("\nRun comparison with:")
    print(f"  python comparison_analysis_improved.py {output_llm.name} {output_nn.name}")
    print("\nOr from the results directory:")
    print(f"  cd results && python ../comparison_analysis_improved.py {output_llm.name} {output_nn.name}")

if __name__ == "__main__":
    main()
