# =====================================================================
# FILE 2: testing/test_suite.py
# =====================================================================
"""
Test suite for Formula Generator Multiverse.
"""

import logging
from typing import List, Tuple

import pandas as pd


class TestSuite:
    """Comprehensive test suite."""

    @staticmethod
    def get_test_queries() -> List[Tuple[str, str]]:
        """Standard test queries."""
        return [
            # Known formulas
            ("Calculate impermanent loss for 50/50 AMM pool", "defi"),
            ("Value at Risk at 95% confidence", "risk"),
            ("Sharpe ratio for portfolio", "risk"),
            ("Uniswap V2 swap output with 0.3% fee", "defi"),
            ("Constant product invariant k equals x times y", "defi"),
            # Variations
            ("Impermanent loss for 80/20 weighted pool", "defi"),
            ("VaR at 99% confidence level", "risk"),
            ("Sharpe ratio with 5% risk-free rate", "risk"),
            # Novel
            ("Optimal LP fee for high volatility market", "defi"),
            ("Risk-adjusted return with maximum drawdown penalty", "risk"),
            ("Sortino ratio using downside deviation only", "risk"),
            # Complex
            ("Portfolio variance with 3 correlated assets", "risk"),
            ("Concentrated liquidity value in Uniswap V3 range", "defi"),
            ("Expected Shortfall CVaR at 95%", "risk"),
            # Edge cases
            ("Something nonsensical", "defi"),
            ("Calculate the meaning of life", "defi"),
        ]

    @staticmethod
    def get_quick_test_queries() -> List[Tuple[str, str]]:
        """Quick test (5 queries only)."""
        return TestSuite.get_test_queries()[:5]

    @staticmethod
    def run_comprehensive_test(multiverse, quick_mode: bool = False) -> pd.DataFrame:
        """
        Run complete test suite.

        Args:
            multiverse: FormulaGeneratorMultiverse instance
            quick_mode: If True, run subset of tests

        Returns:
            Analytics DataFrame
        """
        logging.info("\n" + "=" * 80)
        logging.info("COMPREHENSIVE TEST SUITE - STARTING")
        logging.info("=" * 80 + "\n")

        test_queries = (
            TestSuite.get_quick_test_queries()
            if quick_mode
            else TestSuite.get_test_queries()
        )

        mode_label = "Quick" if quick_mode else "Full"
        logging.info(f"{mode_label} mode: Testing {len(test_queries)} queries\n")

        for i, (query, domain) in enumerate(test_queries, 1):
            logging.info(f"\n{'='*80}")
            logging.info(f"TEST {i}/{len(test_queries)}")
            logging.info(f"{'='*80}")

            multiverse.generate_all_strategies(query, domain)

        analytics = multiverse.generate_analytics()

        logging.info("\n" + "=" * 80)
        logging.info("TEST SUITE COMPLETE")
        logging.info("=" * 80 + "\n")

        return analytics
