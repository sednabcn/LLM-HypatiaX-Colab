# test_suite.py
"""
Unified test suite for all 3 prototypes
"""

TEST_QUERIES = [
    # Known formulas (should work in all)
    ("Calculate impermanent loss for 50/50 AMM pool", "defi"),
    ("Value at Risk at 95% confidence", "risk"),
    ("Sharpe ratio for portfolio", "risk"),
    ("Uniswap V2 swap output with 0.3% fee", "defi"),
    
    # Slight variations (test flexibility)
    ("Impermanent loss but with 80/20 weights", "defi"),
    ("VaR but at 99% confidence instead", "risk"),
    
    # Novel combinations (test discovery)
    ("Optimal LP fee for volatile market", "defi"),
    ("Risk-adjusted return with drawdown penalty", "risk"),
    ("Liquidation price with time decay", "defi"),
    
    # Edge cases
    ("Something that doesn't make sense", "defi"),
    ("", "defi"),  # Empty query
    ("Calculate the meaning of life", "defi"),  # Nonsense
    
    # Complex multi-variable
    ("Portfolio variance with 3 assets and correlations", "risk"),
    ("Concentrated liquidity value in Uniswap V3", "defi"),
]

def evaluate_prototype(prototype_name: str, api_instance):
    """Test a prototype and collect metrics."""
    results = {
        'prototype': prototype_name,
        'success_count': 0,
        'validation_pass_count': 0,
        'total_time_ms': 0,
        'errors': [],
        'details': []
    }
    
    for query, domain in TEST_QUERIES:
        import time
        start = time.time()
        
        try:
            response = api_instance.generate_formula(query, domain)
            elapsed_ms = (time.time() - start) * 1000
            
            results['total_time_ms'] += elapsed_ms
            
            if response['status'] == 'success':
                results['success_count'] += 1
                
                if response['validation']['passed']:
                    results['validation_pass_count'] += 1
            
            results['details'].append({
                'query': query,
                'status': response['status'],
                'time_ms': elapsed_ms,
                'validation_score': response.get('validation', {}).get('score', 0)
            })
        
        except Exception as e:
            results['errors'].append({
                'query': query,
                'error': str(e)
            })
    
    # Calculate metrics
    total_queries = len(TEST_QUERIES)
    results['success_rate'] = results['success_count'] / total_queries
    results['validation_rate'] = results['validation_pass_count'] / total_queries
    results['avg_time_ms'] = results['total_time_ms'] / total_queries
    
    return results

# Run comparison
if __name__ == "__main__":
    from prototype_a_lookup import SmartLookupAPI
    from prototype_b_llm import LLMGeneratorAPI
    from prototype_c_discovery import HybridDiscoveryAPI
    
    print("Testing all 3 prototypes...\n")
    
    # Test A
    print("Testing Prototype A: Smart Lookup...")
    api_a = SmartLookupAPI()
    results_a = evaluate_prototype("Smart Lookup", api_a)
    
    # Test B
    print("\nTesting Prototype B: LLM Generator...")
    api_b = LLMGeneratorAPI()
    results_b = evaluate_prototype("LLM Generator", api_b)
    
    # Test C
    print("\nTesting Prototype C: Hybrid Discovery...")
    api_c = HybridDiscoveryAPI()
    results_c = evaluate_prototype("Hybrid Discovery", api_c)
    
    # Compare
    print("\n" + "="*80)
    print("COMPARISON RESULTS")
    print("="*80)
    
    comparison = pd.DataFrame([
        {
            'Prototype': r['prototype'],
            'Success Rate': f"{r['success_rate']*100:.1f}%",
            'Validation Rate': f"{r['validation_rate']*100:.1f}%",
            'Avg Time (ms)': f"{r['avg_time_ms']:.0f}",
            'Errors': len(r['errors'])
        }
        for r in [results_a, results_b, results_c]
    ])
    
    print(comparison.to_string(index=False))
    
    # Recommendation
    print("\n" + "="*80)
    print("RECOMMENDATION")
    print("="*80)
    
    # Decision logic
    if results_a['validation_rate'] > 0.8 and results_a['avg_time_ms'] < 500:
        print("→ Prototype A (Smart Lookup): Fast + reliable for known formulas")
    elif results_b['validation_rate'] > 0.7 and results_b['avg_time_ms'] < 5000:
        print("→ Prototype B (LLM Generator): Good balance of speed + flexibility")
    elif results_c['validation_rate'] > 0.85:
        print("→ Prototype C (Hybrid Discovery): Highest quality, worth the wait")
    else:
        print("→ Hybrid approach: A for known queries, C for novel discoveries")
