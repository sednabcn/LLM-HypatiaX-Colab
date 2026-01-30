#!/usr/bin/env python3
import json
from pathlib import Path
from datetime import datetime
from typing import Optional
import os

class DomainAwareResultsSaver:
    """Save results organized by domain"""
    
    DOMAINS = ['all_domains', 'defi', 'lending', 'trading', 'physics']
    
    def __init__(self, base_dir: str = 'hypatiax/data/results'):
        self.base_dir = Path(base_dir)
    
    def save_results(self, results: dict, domain: str = 'all_domains') -> Path:
        """
        Save results to domain-specific directory
        
        Args:
            results: Comparison results dictionary
            domain: Domain name (all_domains, defi, lending, trading, physics)
        """
        if domain not in self.DOMAINS:
            raise ValueError(f"Invalid domain: {domain}. Must be one of {self.DOMAINS}")
        
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        
        # Create domain-specific directory
        results_dir = self.base_dir / 'comparison_results' / domain
        results_dir.mkdir(parents=True, exist_ok=True)
        
        # Save timestamped file
        filepath = results_dir / f'comparison_results_{timestamp}.json'
        with open(filepath, 'w') as f:
            json.dump(results, f, indent=2)
        
        # Update 'latest' symlink
        latest_link = results_dir / 'comparison_results_latest.json'
        if latest_link.exists() or latest_link.is_symlink():
            latest_link.unlink()
        
        # Create relative symlink
        latest_link.symlink_to(filepath.name)
        
        print(f"✅ Saved [{domain}]: {filepath}")
        print(f"🔗 Updated [{domain}]: {latest_link}")
        
        return filepath
    
    def save_by_domains(self, results: dict) -> dict:
        """
        Save results split by domain
        
        Args:
            results: Full comparison results
            
        Returns:
            Dictionary mapping domain -> filepath
        """
        saved_files = {}
        
        # Save all_domains (full results)
        saved_files['all_domains'] = self.save_results(results, 'all_domains')
        
        # Split and save by domain
        domain_results = self._split_by_domain(results)
        
        for domain, domain_data in domain_results.items():
            if domain_data['system1'] or domain_data['system2']:
                saved_files[domain] = self.save_results(domain_data, domain)
        
        return saved_files
    
    def _split_by_domain(self, results: dict) -> dict:
        """Split results by domain"""
        domain_data = {domain: {'system1': [], 'system2': [], 'metadata': results.get('metadata', {})} 
                      for domain in self.DOMAINS if domain != 'all_domains'}
        
        # Split system1 results
        for result in results.get('system1', []):
            domain = result.get('domain', 'unknown')
            if domain in domain_data:
                domain_data[domain]['system1'].append(result)
        
        # Split system2 results
        for result in results.get('system2', []):
            domain = result.get('domain', 'unknown')
            if domain in domain_data:
                domain_data[domain]['system2'].append(result)
        
        return domain_data


# Update your main test function
def main():
    parser = argparse.ArgumentParser(...)
    
    parser.add_argument(
        '--domain',
        type=str,
        default='all_domains',
        choices=['all_domains', 'defi', 'lending', 'trading', 'physics'],
        help='Domain to test (or all_domains for everything)'
    )
    parser.add_argument(
        '--split-domains',
        action='store_true',
        help='Save results split by domain in addition to all_domains'
    )
    
    args = parser.parse_args()
    
    # Run your comparison
    results = run_comparison(args)
    
    # Save results
    saver = DomainAwareResultsSaver()
    
    if args.split_domains:
        # Save to all domain subdirectories
        saved_files = saver.save_by_domains(results)
        print(f"\n✅ Results saved to {len(saved_files)} domain directories")
    else:
        # Save to single domain directory
        filepath = saver.save_results(results, args.domain)
        print(f"\n✅ Results saved: {filepath}")

"""
# USAGE #====================================
# ========================================
# RUNNING COMPARISONS
# ========================================

# 1. Run all domains (saves to all_domains + split by domain)
python test_real_hybrid_systems_comparison.py --mode quick --split-domains

# 2. Run specific domain only
python test_real_hybrid_systems_comparison.py --mode quick --domain defi

# 3. Run specific domain (save to that domain only)
python test_real_hybrid_systems_comparison.py --mode quick --domain lending


# ========================================
# ANALYZING RESULTS
# ========================================

# 1. Analyze latest all_domains
python analyze_hybrid_results.py

# 2. Analyze specific domain
python analyze_hybrid_results.py --domain defi

# 3. Analyze ALL domains automatically
python analyze_hybrid_results.py --all-domains

# 4. Analyze specific file
python analyze_hybrid_results.py --input hypatiax/data/results/comparison_results/trading/comparison_results_20241227_143022.json

# 5. Custom output
python analyze_hybrid_results.py --domain defi --output my_defi_analysis


# ========================================
# QUICK ACCESS VIA SYMLINKS
# ========================================

# View latest results for any domain
cat hypatiax/data/results/comparison_results/defi/comparison_results_latest.json
cat hypatiax/data/results/comparison_results/lending/comparison_results_latest.json

# View latest analysis for any domain
ls hypatiax/data/results/analysis_outputs/defi/latest/
ls hypatiax/data/results/analysis_outputs/trading/latest/

"""
"""
📋 Role of test_real_hybrid_systems_comparison.py
This is the execution engine that runs the actual hybrid system comparisons. Here's what it does:
🎯 Core Purpose
It's a test runner that executes both System 1 and System 2 on the same test cases and records performance metrics.
🔧 Key Responsibilities
1. Test Execution
python# Runs real tests on actual hybrid systems
- System 1: Improved Hybrid (LLM + NN + Ensemble decision logic)
- System 2: Symbolic + Validation (Pure symbolic with validation checks)
2. Data Collection
python# For each test, it records:
{
    "description": "Test name",
    "domain": "defi/lending/trading/physics",
    "r2": 0.998,                    # R² score
    "rmse": 0.0123,                 # Root mean squared error
    "runtime_seconds": 2.45,         # Execution time
    "is_extrapolation": False,       # Test type
    "decision": "ensemble",          # System 1: which model won
    "validation_score": 92.5,        # System 2: validation quality
    "success": True
}
3. Test Organization
python# Organizes tests by domain:
- all_domains: Run all tests across domains
- defi: DeFi-specific tests only
- lending: Lending protocol tests
- trading: Trading strategy tests
- physics: Physics simulation tests
4. Results Output
python# Saves structured JSON with both systems' results:
{
    "metadata": {
        "timestamp": "2024-12-27T14:30:22",
        "mode": "quick",
        "domain": "defi"
    },
    "system1": [test_result1, test_result2, ...],
    "system2": [test_result1, test_result2, ...]
}
🚀 Typical Workflow
bash# Step 1: Run comparison tests
python test_real_hybrid_systems_comparison.py --mode quick --domain defi

# This generates:
# hypatiax/data/results/comparison_results/defi/comparison_results_20241227_143022.json

# Step 2: Analyze results
python analyze_hybrid_results.py --domain defi

# This generates:
# hypatiax/data/results/analysis_outputs/defi/20241227_143022/
#   ├── summary_report.txt
#   ├── *.csv (tables)
#   └── *.png (visualizations)
```

### 📊 **Relationship Between Scripts**
```
test_real_hybrid_systems_comparison.py (RUNNER)
    ↓
    Executes tests on both systems
    Measures performance (R², RMSE, runtime)
    ↓
    Saves results to JSON
    ↓
comparison_results/domain/comparison_results_TIMESTAMP.json (RAW DATA)
    ↓
    Input to analyzer
    ↓
analyze_hybrid_results.py (ANALYZER)
    ↓
    Loads JSON data
    Generates statistics
    Creates visualizations
    ↓
analysis_outputs/domain/TIMESTAMP/ (ANALYSIS)
    ├── Tables (CSV)
    ├── Plots (PNG)
    └── Report (TXT)
🎮 Example Usage Scenarios
Scenario 1: Quick DeFi Test
bash# Run quick tests on DeFi domain
python test_real_hybrid_systems_comparison.py --mode quick --domain defi

# Analyze results immediately
python analyze_hybrid_results.py --domain defi
Scenario 2: Comprehensive All-Domain Evaluation
bash# Run full test suite across all domains
python test_real_hybrid_systems_comparison.py --mode full --split-domains

# Analyze each domain
python analyze_hybrid_results.py --all-domains

# Generate cross-domain comparison
python analyze_hybrid_results.py --cross-domain
Scenario 3: Focus on Extrapolation
bash# Run only extrapolation tests
python test_real_hybrid_systems_comparison.py --mode quick --extrapolation-only --domain physics

# Analyze extrapolation performance
python analyze_hybrid_results.py --domain physics
🔑 Key Differences
ScriptPurposeInputOutputtest_real_*Execute comparisonsTest definitionsRaw results (JSON)analyze_*Analyze resultsResults JSONReports, plots, tables
The test script is the data generator, while the analyzer is the insight extractor! 🎯

"""

