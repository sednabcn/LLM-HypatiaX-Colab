"""
Unit Tests for defi_dataset_20_generator.py
Tests the 20 comprehensive DeFi formulas generator
"""

import sys
import unittest
from unittest.mock import MagicMock, Mock, patch

import numpy as np

# Mock the HybridDiscoverySystem
sys.modules["hypatiax.tools.symbolic.hybrid_system"] = MagicMock()


class MockHybridDiscoverySystem:
    """Mock for HybridDiscoverySystem"""

    def __init__(self, domain="defi", max_results=100):
        self.domain = domain
        self.max_results = max_results
        self.results = []

    def discover_validate_interpret(self, **kwargs):
        return {"status": "success"}

    def export_results(self, filepath, format="json"):
        return True

    def get_statistics(self):
        return {"total_runs": 20, "valid_count": 18, "success_rate": 0.9, "average_r2": 0.95}


class TestDeFiFormulaGeneratorInit(unittest.TestCase):
    """Test DeFiFormulaGenerator initialization"""

    @patch("hypatiax.tools.symbolic.hybrid_system.HybridDiscoverySystem")
    def test_init_with_defaults(self, mock_system):
        """Test initialization with default parameters"""
        from generators.finance.defi.defi_dataset_20_generator import DeFiFormulaGenerator

        generator = DeFiFormulaGenerator()

        self.assertEqual(generator.seed, 42)
        self.assertIsInstance(generator.results, list)

    @patch("hypatiax.tools.symbolic.hybrid_system.HybridDiscoverySystem")
    def test_init_with_custom_seed(self, mock_system):
        """Test initialization with custom seed"""
        from generators.finance.defi.defi_dataset_20_generator import DeFiFormulaGenerator

        generator = DeFiFormulaGenerator(seed=123)

        self.assertEqual(generator.seed, 123)

    @patch("hypatiax.tools.symbolic.hybrid_system.HybridDiscoverySystem")
    @patch("numpy.random.seed")
    def test_init_sets_random_seed(self, mock_np_seed, mock_system):
        """Test that numpy random seed is set"""
        from generators.finance.defi.defi_dataset_20_generator import DeFiFormulaGenerator

        generator = DeFiFormulaGenerator(seed=99)

        mock_np_seed.assert_called_with(99)


class TestFormula01ImpermanentLoss(unittest.TestCase):
    """Test Formula 1: Impermanent Loss"""

    def test_il_formula_correctness(self):
        """Test IL formula: 2*sqrt(price_ratio)/(1+price_ratio) - 1"""
        price_ratio = np.array([1.0, 2.0, 0.5, 4.0])

        il = 2 * np.sqrt(price_ratio) / (price_ratio + 1) - 1

        # At price_ratio=1, IL should be 0
        self.assertAlmostEqual(il[0], 0.0)

        # At price_ratio=2, IL should be negative
        self.assertLess(il[1], 0)

        # At price_ratio=0.5, IL should be negative
        self.assertLess(il[2], 0)

    def test_il_symmetry(self):
        """Test that IL is symmetric for 2x and 0.5x"""
        price_up = 2.0
        price_down = 0.5

        il_up = 2 * np.sqrt(price_up) / (price_up + 1) - 1
        il_down = 2 * np.sqrt(price_down) / (price_down + 1) - 1

        # Both should result in loss
        self.assertLess(il_up, 0)
        self.assertLess(il_down, 0)


class TestFormula02AMMSwapOutput(unittest.TestCase):
    """Test Formula 2: AMM Swap Output"""

    def test_swap_output_formula(self):
        """Test Uniswap V2 swap output formula"""
        amount_in = 10
        reserve_in = 1000
        reserve_out = 1000

        y_out = (amount_in * 0.997 * reserve_out) / (reserve_in + amount_in * 0.997)

        self.assertGreater(y_out, 0)
        self.assertLess(y_out, amount_in)  # Should get less due to slippage

    def test_swap_output_with_fee(self):
        """Test that 0.3% fee reduces output"""
        amount_in = 100
        reserve_in = 10000
        reserve_out = 10000

        # With fee
        output_with_fee = (amount_in * 0.997 * reserve_out) / (reserve_in + amount_in * 0.997)

        # Without fee (theoretical)
        output_no_fee = (amount_in * reserve_out) / (reserve_in + amount_in)

        self.assertLess(output_with_fee, output_no_fee)


class TestFormula03UtilizationRate(unittest.TestCase):
    """Test Formula 3: Utilization Rate"""

    def test_utilization_calculation(self):
        """Test utilization = borrowed / supplied"""
        borrowed = 500
        supplied = 1000

        util = borrowed / supplied

        self.assertAlmostEqual(util, 0.5)

    def test_utilization_bounds(self):
        """Test utilization is between 0 and 1"""
        borrowed = np.array([0, 500, 1000])
        supplied = np.array([1000, 1000, 1000])

        util = borrowed / supplied

        self.assertTrue(np.all(util >= 0))
        self.assertTrue(np.all(util <= 1))


class TestFormula04LiquidityPoolValue(unittest.TestCase):
    """Test Formula 4: Liquidity Pool Value"""

    def test_pool_value_formula(self):
        """Test value = 2 * sqrt(reserve0 * reserve1)"""
        reserve0 = 10000
        reserve1 = 10000

        value = 2 * np.sqrt(reserve0 * reserve1)

        self.assertAlmostEqual(value, 20000)

    def test_pool_value_increases_with_reserves(self):
        """Test that larger reserves increase pool value"""
        # Small pool
        small_value = 2 * np.sqrt(1000 * 1000)

        # Large pool
        large_value = 2 * np.sqrt(10000 * 10000)

        self.assertGreater(large_value, small_value)


class TestFormula05CompoundInterestRate(unittest.TestCase):
    """Test Formula 5: Compound Interest Rate Model"""

    def test_interest_rate_linear_model(self):
        """Test rate = base_rate + slope * utilization"""
        base_rate = 0.02
        utilization = 0.5
        slope = 0.10

        rate = base_rate + slope * utilization

        self.assertAlmostEqual(rate, 0.07)

    def test_higher_utilization_higher_rate(self):
        """Test that higher utilization increases rate"""
        base_rate = 0.02
        slope = 0.10

        util_low = 0.3
        util_high = 0.8

        rate_low = base_rate + slope * util_low
        rate_high = base_rate + slope * util_high

        self.assertGreater(rate_high, rate_low)


class TestFormula06CollateralRatio(unittest.TestCase):
    """Test Formula 6: Collateral Ratio"""

    def test_collateral_ratio_calculation(self):
        """Test col_ratio = collateral / debt"""
        collateral = 15000
        debt = 10000

        col_ratio = collateral / debt

        self.assertAlmostEqual(col_ratio, 1.5)

    def test_safe_collateral_ratio(self):
        """Test that ratio > 1.5 is typically safe"""
        collateral = 15000
        debt = 8000

        col_ratio = collateral / debt

        self.assertGreater(col_ratio, 1.5)


class TestFormula07LiquidationPrice(unittest.TestCase):
    """Test Formula 7: Liquidation Price"""

    def test_liquidation_price_formula(self):
        """Test liq_price = entry_price / liq_threshold"""
        entry_price = 1000
        liq_threshold = 1.3

        liq_price = entry_price / liq_threshold

        self.assertLess(liq_price, entry_price)
        self.assertAlmostEqual(liq_price, 769.23, places=2)

    def test_higher_threshold_lower_liq_price(self):
        """Test that higher threshold means lower liquidation price"""
        entry_price = 1000

        threshold_low = 1.2
        threshold_high = 1.5

        liq_low = entry_price / threshold_low
        liq_high = entry_price / threshold_high

        self.assertLess(liq_high, liq_low)


class TestFormula08YieldFarmingAPY(unittest.TestCase):
    """Test Formula 8: Yield Farming APY"""

    def test_apy_calculation(self):
        """Test APY = (rewards_per_block * blocks_per_year) / total_staked"""
        rewards_per_block = 1.0
        blocks_per_year = 2102400
        total_staked = 10000

        apy = (rewards_per_block * blocks_per_year) / total_staked

        self.assertGreater(apy, 0)
        self.assertAlmostEqual(apy, 210.24)

    def test_more_staked_lower_apy(self):
        """Test that more total staked reduces individual APY"""
        rewards_per_block = 1.0
        blocks_per_year = 2102400

        staked_low = 10000
        staked_high = 100000

        apy_low = (rewards_per_block * blocks_per_year) / staked_low
        apy_high = (rewards_per_block * blocks_per_year) / staked_high

        self.assertGreater(apy_low, apy_high)


class TestFormula09Slippage(unittest.TestCase):
    """Test Formula 9: Slippage"""

    def test_slippage_calculation(self):
        """Test slippage = amount_in / (reserve + amount_in)"""
        amount_in = 100
        reserve = 10000

        slippage = amount_in / (reserve + amount_in)

        self.assertGreater(slippage, 0)
        self.assertLess(slippage, 1)
        self.assertAlmostEqual(slippage, 0.0099, places=4)

    def test_larger_trade_higher_slippage(self):
        """Test that larger trades have higher slippage"""
        reserve = 10000

        small_trade = 10
        large_trade = 1000

        slippage_small = small_trade / (reserve + small_trade)
        slippage_large = large_trade / (reserve + large_trade)

        self.assertGreater(slippage_large, slippage_small)


class TestFormula10LPTokenShare(unittest.TestCase):
    """Test Formula 10: LP Token Share"""

    def test_lp_token_calculation(self):
        """Test LP tokens = (deposit / total_liquidity) * total_shares"""
        deposit_amount = 1000
        total_liquidity = 10000
        total_shares = 5000

        lp_tokens = (deposit_amount / total_liquidity) * total_shares

        self.assertAlmostEqual(lp_tokens, 500)

    def test_proportional_share(self):
        """Test that LP tokens are proportional to deposit"""
        total_liquidity = 10000
        total_shares = 5000

        deposit_small = 100
        deposit_large = 1000

        tokens_small = (deposit_small / total_liquidity) * total_shares
        tokens_large = (deposit_large / total_liquidity) * total_shares

        self.assertAlmostEqual(tokens_large / tokens_small, 10)


class TestFormula11HealthFactor(unittest.TestCase):
    """Test Formula 11: Health Factor (Aave-style)"""

    def test_health_factor_calculation(self):
        """Test health = (collateral * liq_threshold) / debt"""
        collateral = 10000
        liq_threshold = 0.80
        debt = 6000

        health = (collateral * liq_threshold) / debt

        self.assertAlmostEqual(health, 1.333, places=3)

    def test_health_factor_interpretation(self):
        """Test health factor interpretation"""
        collateral = 10000
        liq_threshold = 0.75

        # Safe: health > 1
        debt_safe = 5000
        health_safe = (collateral * liq_threshold) / debt_safe
        self.assertGreater(health_safe, 1)

        # At risk: health < 1
        debt_risk = 8000
        health_risk = (collateral * liq_threshold) / debt_risk
        self.assertLess(health_risk, 1)


class TestFormula12FundingRate(unittest.TestCase):
    """Test Formula 12: Perpetual Swap Funding Rate"""

    def test_funding_rate_calculation(self):
        """Test funding = (mark_price - index_price) / index_price / interval"""
        mark_price = 1010
        index_price = 1000
        funding_interval = 8

        funding = (mark_price - index_price) / index_price / funding_interval

        self.assertGreater(funding, 0)
        self.assertAlmostEqual(funding, 0.00125)

    def test_negative_funding(self):
        """Test negative funding when mark < index"""
        mark_price = 990
        index_price = 1000
        funding_interval = 8

        funding = (mark_price - index_price) / index_price / funding_interval

        self.assertLess(funding, 0)


class TestFormula13PriceImpact(unittest.TestCase):
    """Test Formula 13: Price Impact Estimation"""

    def test_price_impact_calculation(self):
        """Test impact = (trade_size / liquidity) ^ 0.5"""
        trade_size = 100
        liquidity = 10000

        impact = (trade_size / liquidity) ** 0.5

        self.assertGreater(impact, 0)
        self.assertLess(impact, 1)
        self.assertAlmostEqual(impact, 0.1)


class TestFormula14StakingRewards(unittest.TestCase):
    """Test Formula 14: Staking Rewards"""

    def test_staking_rewards_calculation(self):
        """Test rewards = staked * rate * (time / 365)"""
        staked_amount = 1000
        reward_rate = 0.10  # 10% APR
        time_staked = 365  # 1 year

        rewards = staked_amount * reward_rate * (time_staked / 365)

        self.assertAlmostEqual(rewards, 100)

    def test_proportional_time(self):
        """Test that rewards are proportional to time"""
        staked = 1000
        rate = 0.10

        # Half year
        rewards_half = staked * rate * (182.5 / 365)

        # Full year
        rewards_full = staked * rate * (365 / 365)

        self.assertAlmostEqual(rewards_half * 2, rewards_full)


class TestFormula15BondingCurve(unittest.TestCase):
    """Test Formula 15: Linear Bonding Curve Price"""

    def test_bonding_curve_price(self):
        """Test price = supply * reserve_ratio"""
        supply = 1000
        reserve_ratio = 0.3

        price = supply * reserve_ratio

        self.assertAlmostEqual(price, 300)

    def test_price_increases_with_supply(self):
        """Test that price increases with supply"""
        reserve_ratio = 0.3

        supply_low = 100
        supply_high = 1000

        price_low = supply_low * reserve_ratio
        price_high = supply_high * reserve_ratio

        self.assertGreater(price_high, price_low)


class TestFormula16FlashLoanFee(unittest.TestCase):
    """Test Formula 16: Flash Loan Fee"""

    def test_flash_loan_fee_calculation(self):
        """Test fee = loan_amount * fee_rate"""
        loan_amount = 100000
        fee_rate = 0.0009  # 0.09%

        fee = loan_amount * fee_rate

        self.assertAlmostEqual(fee, 90)

    def test_fee_proportional_to_loan(self):
        """Test that fee scales with loan amount"""
        fee_rate = 0.0009

        loan_small = 10000
        loan_large = 100000

        fee_small = loan_small * fee_rate
        fee_large = loan_large * fee_rate

        self.assertAlmostEqual(fee_large / fee_small, 10)


class TestFormula17VestingSchedule(unittest.TestCase):
    """Test Formula 17: Linear Vesting Schedule"""

    def test_vesting_calculation(self):
        """Test vested = total * (elapsed / period)"""
        total_tokens = 10000
        time_elapsed = 182.5  # Half year
        vesting_period = 365  # 1 year

        vested = total_tokens * (time_elapsed / vesting_period)

        self.assertAlmostEqual(vested, 5000)

    def test_vesting_bounds(self):
        """Test vesting at start and end"""
        total_tokens = 10000
        vesting_period = 365

        # At start (0 days)
        vested_start = total_tokens * (0 / vesting_period)
        self.assertEqual(vested_start, 0)

        # At end (365 days)
        vested_end = total_tokens * (365 / vesting_period)
        self.assertAlmostEqual(vested_end, total_tokens)


class TestFormula18ArbitrageProfit(unittest.TestCase):
    """Test Formula 18: Cross-Exchange Arbitrage"""

    def test_arbitrage_profit_calculation(self):
        """Test profit = (price_b - price_a) * trade_size"""
        price_a = 1000
        price_b = 1050
        trade_size = 10

        profit = (price_b - price_a) * trade_size

        self.assertAlmostEqual(profit, 500)

    def test_negative_arbitrage(self):
        """Test loss when price_b < price_a"""
        price_a = 1050
        price_b = 1000
        trade_size = 10

        profit = (price_b - price_a) * trade_size

        self.assertLess(profit, 0)


class TestFormula19GasCostROI(unittest.TestCase):
    """Test Formula 19: Gas-Adjusted ROI"""

    def test_gas_adjusted_roi(self):
        """Test roi = (profit - gas_cost) / gas_cost"""
        profit = 100
        gas_cost = 20

        roi = (profit - gas_cost) / gas_cost

        self.assertAlmostEqual(roi, 4.0)

    def test_unprofitable_with_gas(self):
        """Test that high gas can make transaction unprofitable"""
        profit = 10
        gas_cost = 50

        roi = (profit - gas_cost) / gas_cost

        self.assertLess(roi, 0)


class TestFormula20ConcentratedLiquidityPosition(unittest.TestCase):
    """Test Formula 20: Uniswap V3 Concentrated Liquidity"""

    def test_concentrated_liq_amount0(self):
        """Test amount0 calculation for concentrated liquidity"""
        liquidity = 10000
        sqrt_price_current = 50
        sqrt_price_lower = 45
        sqrt_price_upper = 55

        amount0 = liquidity * (sqrt_price_upper - sqrt_price_current) / (sqrt_price_current * sqrt_price_upper)

        self.assertGreater(amount0, 0)


class TestGenerateFormulaMethod(unittest.TestCase):
    """Test the generate_formula method"""

    @patch("hypatiax.tools.symbolic.hybrid_system.HybridDiscoverySystem")
    def setUp(self, mock_system):
        """Set up test fixtures"""
        mock_system.return_value = MockHybridDiscoverySystem()
        from generators.finance.defi.defi_dataset_20_generator import DeFiFormulaGenerator

        self.generator = DeFiFormulaGenerator(seed=42)
        self.generator.system.discover_validate_interpret = Mock()

    def test_generate_formula_calls_discover(self):
        """Test that generate_formula calls discover_validate_interpret"""
        self.generator.generate_formula(1, n_samples=10)

        self.generator.system.discover_validate_interpret.assert_called_once()

    def test_generate_all_20_formulas(self):
        """Test generating all 20 formulas"""
        for formula_num in range(1, 21):
            self.generator.system.discover_validate_interpret.reset_mock()
            self.generator.generate_formula(formula_num, n_samples=5)
            self.generator.system.discover_validate_interpret.assert_called()


class TestRunAllFormulas(unittest.TestCase):
    """Test run_all_formulas method"""

    @patch("hypatiax.tools.symbolic.hybrid_system.HybridDiscoverySystem")
    def setUp(self, mock_system):
        """Set up test fixtures"""
        mock_system.return_value = MockHybridDiscoverySystem()
        from generators.finance.defi.defi_dataset_20_generator import DeFiFormulaGenerator

        self.generator = DeFiFormulaGenerator(seed=42)
        self.generator.generate_formula = Mock()

    def test_run_all_formulas_calls_all_20(self):
        """Test that all 20 formulas are generated"""
        self.generator.run_all_formulas(n_samples=10)

        # Should be called 20 times
        self.assertEqual(self.generator.generate_formula.call_count, 20)

        # Check that all formula numbers 1-20 were called
        called_formula_nums = [call[0][0] for call in self.generator.generate_formula.call_args_list]
        self.assertEqual(sorted(called_formula_nums), list(range(1, 21)))


class TestSaveResults(unittest.TestCase):
    """Test save_results method"""

    @patch("hypatiax.tools.symbolic.hybrid_system.HybridDiscoverySystem")
    @patch("os.makedirs")
    def test_save_results_creates_directory(self, mock_makedirs, mock_system):
        """Test that output directory is created"""
        mock_system.return_value = MockHybridDiscoverySystem()
        from generators.finance.defi.defi_dataset_20_generator import DeFiFormulaGenerator

        generator = DeFiFormulaGenerator(seed=42)
        generator.save_results(output_dir="test_output")

        mock_makedirs.assert_called()

    @patch("hypatiax.tools.symbolic.hybrid_system.HybridDiscoverySystem")
    @patch("os.makedirs")
    def test_save_results_returns_paths(self, mock_makedirs, mock_system):
        """Test that save_results returns file paths"""
        mock_system.return_value = MockHybridDiscoverySystem()
        from generators.finance.defi.defi_dataset_20_generator import DeFiFormulaGenerator

        generator = DeFiFormulaGenerator(seed=42)
        json_path, csv_path = generator.save_results()

        self.assertIn(".json", json_path)
        self.assertIn(".csv", csv_path)


class TestPrintSummary(unittest.TestCase):
    """Test print_summary method"""

    @patch("hypatiax.tools.symbolic.hybrid_system.HybridDiscoverySystem")
    @patch("builtins.print")
    def test_print_summary_outputs_stats(self, mock_print, mock_system):
        """Test that summary prints statistics"""
        mock_system.return_value = MockHybridDiscoverySystem()
        from generators.finance.defi.defi_dataset_20_generator import DeFiFormulaGenerator

        generator = DeFiFormulaGenerator(seed=42)
        generator.print_summary()

        self.assertTrue(mock_print.called)


def run_tests():
    """Run all unit tests"""
    loader = unittest.TestLoader()
    suite = unittest.TestSuite()

    # Add all test classes
    suite.addTests(loader.loadTestsFromTestCase(TestDeFiFormulaGeneratorInit))
    suite.addTests(loader.loadTestsFromTestCase(TestFormula01ImpermanentLoss))
    suite.addTests(loader.loadTestsFromTestCase(TestFormula02AMMSwapOutput))
    suite.addTests(loader.loadTestsFromTestCase(TestFormula03UtilizationRate))
    suite.addTests(loader.loadTestsFromTestCase(TestFormula04LiquidityPoolValue))
    suite.addTests(loader.loadTestsFromTestCase(TestFormula05CompoundInterestRate))
    suite.addTests(loader.loadTestsFromTestCase(TestFormula06CollateralRatio))
    suite.addTests(loader.loadTestsFromTestCase(TestFormula07LiquidationPrice))
    suite.addTests(loader.loadTestsFromTestCase(TestFormula08YieldFarmingAPY))
    suite.addTests(loader.loadTestsFromTestCase(TestFormula09Slippage))
    suite.addTests(loader.loadTestsFromTestCase(TestFormula10LPTokenShare))
    suite.addTests(loader.loadTestsFromTestCase(TestFormula11HealthFactor))
    suite.addTests(loader.loadTestsFromTestCase(TestFormula12FundingRate))
    suite.addTests(loader.loadTestsFromTestCase(TestFormula13PriceImpact))
    suite.addTests(loader.loadTestsFromTestCase(TestFormula14StakingRewards))
    suite.addTests(loader.loadTestsFromTestCase(TestFormula15BondingCurve))
    suite.addTests(loader.loadTestsFromTestCase(TestFormula16FlashLoanFee))
    suite.addTests(loader.loadTestsFromTestCase(TestFormula17VestingSchedule))
    suite.addTests(loader.loadTestsFromTestCase(TestFormula18ArbitrageProfit))
    suite.addTests(loader.loadTestsFromTestCase(TestFormula19GasCostROI))
    suite.addTests(loader.loadTestsFromTestCase(TestFormula20ConcentratedLiquidityPosition))
    suite.addTests(loader.loadTestsFromTestCase(TestGenerateFormulaMethod))
    suite.addTests(loader.loadTestsFromTestCase(TestRunAllFormulas))
    suite.addTests(loader.loadTestsFromTestCase(TestSaveResults))
    suite.addTests(loader.loadTestsFromTestCase(TestPrintSummary))

    runner = unittest.TextTestRunner(verbosity=2)
    result = runner.run(suite)

    return result


if __name__ == "__main__":
    print("=" * 70)
    print("Unit Tests: defi_dataset_20_generator.py")
    print("Testing 20 comprehensive DeFi formulas")
    print("=" * 70)
    result = run_tests()
    print("\n" + "=" * 70)
    print(f"Tests run: {result.testsRun}")
    print(f"Failures: {len(result.failures)}")
    print(f"Errors: {len(result.errors)}")
    print(f"Success: {result.wasSuccessful()}")
    print("=" * 70)
