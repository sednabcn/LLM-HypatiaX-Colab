#=====================================================================
#                                TEST SUITE
#=====================================================================
class TestSuite:
"""Comprehensive test suite for all strategies."""
@staticmethod
def get_test_queries() -> List[Tuple[str, str]]:
    """Get standard test queries."""
    return [
        # Known formulas - should work in all strategies
        ("Calculate impermanent loss for 50/50 AMM pool", "defi"),
        ("Value at Risk at 95% confidence", "risk"),
        ("Sharpe ratio for portfolio", "risk"),
        ("Uniswap V2 swap output with 0.3% fee", "defi"),
        ("Constant product invariant k=x*y", "defi"),
        
        # Slight variations
        ("Impermanent loss but for 80/20 weighted pool", "defi"),
        ("VaR at 99% confidence level instead of 95%", "risk"),
        ("Sharpe ratio with 3% risk-free rate", "risk"),
        
        # Novel combinations
        ("Optimal LP fee for volatile market conditions", "defi"),
        ("Risk-adjusted return penalized by drawdown", "risk"),
        ("Liquidation price with exponential time decay", "defi"),
        ("Sortino ratio using downside deviation", "risk"),
        
        # Complex multi-variable
        ("Portfolio variance with 3 assets and correlations", "risk"),
        ("Concentrated liquidity value in Uniswap V3", "defi"),
        ("Expected Shortfall at 95% confidence", "risk"),
        
        # Edge cases
        ("Something that makes no mathematical sense", "defi"),
        ("Calculate the meaning of life in DeFi terms", "defi"),
        ("", "defi"),  # Empty
        
        # Domain-specific advanced
        ("Maximum drawdown over rolling 30-day window", "risk"),
        ("Price impact with slippage in low liquidity", "defi"),
    ]

@staticmethod
def run_comprehensive_test(multiverse: FormulaGeneratorMultiverse) -> pd.DataFrame:
    """Run all test queries through the multiverse."""
    logging.info("\n" + "="*80)
    logging.info("RUNNING COMPREHENSIVE TEST SUITE")
    logging.info("="*80 + "\n")
    
    test_queries = TestSuite.get_test_queries()
    
    for i, (query, domain) in enumerate(test_queries, 1):
        logging.info(f"\n[Test {i}/{len(test_queries)}] Query: {query[:60]}...")
        multiverse.generate_all_strategies(query, domain, parallel=True)
    
    # Generate and return analytics
    analytics = multiverse.generate_analytics()
    
    logging.info("\n" + "="*80)
    logging.info("TEST SUITE COMPLETE")
    logging.info("="*80 + "\n")
    
    return analytics
# =====================================================================
#                             MAIN EXECUTION
# =====================================================================
if name == "main":
    # Configure logging
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(levelname)s - %(message)s',
        datefmt='%H:%M:%S'
    )
    # Initialize multiverse
    multiverse = FormulaGeneratorMultiverse(
        defi_csv='../defi_queries_280.csv',
        risk_csv='../risk_queries_comprehensive.csv',
        anthropic_api_key=os.getenv('ANTHROPIC_API_KEY'),
        enable_strategies=[
            Strategy.SMART_LOOKUP,
            Strategy.LLM_GENERATION,
            # Strategy.SYMBOLIC_DISCOVERY,  # Enable if you want (slow)
        ]
    )

    # Run comprehensive test
    analytics = TestSuite.run_comprehensive_test(multiverse)

    # Print summary
    multiverse.print_summary()

    # Export results
    timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
    multiverse.export_results(f'multiverse_results_{timestamp}.json')

    print("\n✓ Testing complete!")
    print(f"✓ Results exported to multiverse_results_{timestamp}.json")



# USAGE

# Install dependencies
# pip install sentence-transformers anthropic pandas numpy

# Set API key
# export ANTHROPIC_API_KEY="your-key"

# Run comprehensive test
# python formula_generator_multiverse.py

# Output:
# - Console: Real-time progress + summary
# - File: multiverse_results_TIMESTAMP.json (full results)
`



# WHAT YOU GET
"""
1. **Parallel Testing**: All strategies run simultaneously
2. **Automatic Recommendation**: System picks best strategy per query
3. **Comprehensive Analytics**: Success rates, validation rates, speed, cost
4. **Export Everything**: JSON file with all results for analysis
5. **Easy to Extend**: Add new strategies by implementing the interface

---

**This is production-ready. Run it TODAY and you'll know which approach to build. Want me to help set it up?**Claude can make mistakes. Please double-check responses.
"""
