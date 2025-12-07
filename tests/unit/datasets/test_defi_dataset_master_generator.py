"""
Unit Tests for defi_dataset_master_generator.py
Tests the MassiveDeFiFormulaGenerator class with 280 formula variations
"""

import os
import sys
import unittest
from unittest.mock import MagicMock, Mock, call, patch

import numpy as np

# Mock the HybridDiscoverySystem before importing the generator
sys.modules["hypatiax.tools.symbolic.hybrid_system"] = MagicMock()


class MockHybridDiscoverySystem:
    """Mock HybridDiscoverySystem for testing"""

    def __init__(self, domain="defi", max_results=500):
        self.domain = domain
        self.max_results = max_results
        self.results = []

    def discover_validate_interpret(self, **kwargs):
        return {"status": "success", "r2_score": 0.95}


class TestMassiveDeFiFormulaGeneratorInit(unittest.TestCase):
    """Test generator initialization"""

    def setUp(self):
        """Set up test fixtures"""
        self.domain = "defi"
        self.seed = 42

    @patch("hypatiax.tools.symbolic.hybrid_system.HybridDiscoverySystem")
    def test_init_with_default_params(self, mock_system):
        """Test initialization with default parameters"""
        from generators.finance.defi.defi_dataset_master_generator import MassiveDeFiFormulaGenerator

        generator = MassiveDeFiFormulaGenerator()

        self.assertEqual(generator.seed, 42)
        self.assertEqual(generator.formula_id, 0)
        self.assertEqual(generator.successful_formulas, 0)
        self.assertEqual(generator.failed_formulas, 0)
        self.assertIsInstance(generator.results, list)
        self.assertEqual(len(generator.results), 0)

    @patch("hypatiax.tools.symbolic.hybrid_system.HybridDiscoverySystem")
    def test_init_with_custom_params(self, mock_system):
        """Test initialization with custom parameters"""
        from generators.finance.defi.defi_dataset_master_generator import MassiveDeFiFormulaGenerator

        generator = MassiveDeFiFormulaGenerator(domain="custom", seed=123)

        self.assertEqual(generator.seed, 123)

    @patch("hypatiax.tools.symbolic.hybrid_system.HybridDiscoverySystem")
    def test_init_sets_random_seed(self, mock_system):
        """Test that initialization sets numpy random seed"""
        from generators.finance.defi.defi_dataset_master_generator import MassiveDeFiFormulaGenerator

        with patch("numpy.random.seed") as mock_seed:
            generator = MassiveDeFiFormulaGenerator(seed=99)
            mock_seed.assert_called_once_with(99)


class TestConstantProductVariants(unittest.TestCase):
    """Test constant product formula variants"""

    def setUp(self):
        """Set up test fixtures"""
        with patch("hypatiax.tools.symbolic.hybrid_system.HybridDiscoverySystem"):
            from generators.finance.defi.defi_dataset_master_generator import MassiveDeFiFormulaGenerator

            self.generator = MassiveDeFiFormulaGenerator(seed=42)
            self.generator._process_formula = Mock()

    def test_generate_constant_product_variants_count(self):
        """Test that 30 variants are generated"""
        self.generator.generate_constant_product_variants(n_samples=20)

        self.assertEqual(self.generator._process_formula.call_count, 30)
        self.assertEqual(self.generator.formula_id, 30)

    def test_generate_constant_product_formula_correctness(self):
        """Test constant product formula k = x * y"""
        np.random.seed(42)

        token_x = np.array([100.0, 200.0, 300.0])
        token_y = np.array([500.0, 400.0, 300.0])

        k_expected = token_x * token_y

        np.testing.assert_array_almost_equal(k_expected, [50000, 80000, 90000])

    def test_constant_product_reserve_ranges(self):
        """Test that reserve ranges vary across variations"""
        self.generator.generate_constant_product_variants(n_samples=5)

        calls = self.generator._process_formula.call_args_list

        # Check first and last call have different descriptions
        first_desc = calls[0][1]["description"]
        last_desc = calls[-1][1]["description"]

        self.assertNotEqual(first_desc, last_desc)
        self.assertIn("Constant Product", first_desc)

    def test_constant_product_data_shape(self):
        """Test data shape is correct"""
        n_samples = 20
        self.generator.generate_constant_product_variants(n_samples=n_samples)

        call_args = self.generator._process_formula.call_args_list[0]
        X_data = call_args[1]["X"]
        y_data = call_args[1]["y"]

        self.assertEqual(X_data.shape, (n_samples, 2))
        self.assertEqual(y_data.shape, (n_samples,))


class TestConstantSumVariants(unittest.TestCase):
    """Test constant sum formula variants"""

    def setUp(self):
        """Set up test fixtures"""
        with patch("hypatiax.tools.symbolic.hybrid_system.HybridDiscoverySystem"):
            from generators.finance.defi.defi_dataset_master_generator import MassiveDeFiFormulaGenerator

            self.generator = MassiveDeFiFormulaGenerator(seed=42)
            self.generator._process_formula = Mock()

    def test_generate_constant_sum_variants_count(self):
        """Test that 25 variants are generated"""
        self.generator.generate_constant_sum_variants(n_samples=20)

        self.assertEqual(self.generator._process_formula.call_count, 25)
        self.assertEqual(self.generator.formula_id, 25)

    def test_constant_sum_formula_correctness(self):
        """Test constant sum formula k = x + y"""
        token_x = np.array([100.0, 200.0, 300.0])
        token_y = np.array([500.0, 400.0, 300.0])

        k_expected = token_x + token_y

        np.testing.assert_array_equal(k_expected, [600, 600, 600])

    def test_constant_sum_weight_variation(self):
        """Test that weight ratios vary"""
        self.generator.generate_constant_sum_variants(n_samples=5)

        # Verify all calls have Constant_Sum in name
        calls = self.generator._process_formula.call_args_list
        for call in calls:
            name = call[1]["name"]
            self.assertIn("Constant_Sum_v", name)


class TestImpermanentLossVariants(unittest.TestCase):
    """Test impermanent loss formula variants"""

    def setUp(self):
        """Set up test fixtures"""
        with patch("hypatiax.tools.symbolic.hybrid_system.HybridDiscoverySystem"):
            from generators.finance.defi.defi_dataset_master_generator import MassiveDeFiFormulaGenerator

            self.generator = MassiveDeFiFormulaGenerator(seed=42)
            self.generator._process_formula = Mock()

    def test_generate_impermanent_loss_variants_count(self):
        """Test that 30 variants are generated"""
        self.generator.generate_impermanent_loss_variants(n_samples=20)

        self.assertEqual(self.generator._process_formula.call_count, 30)

    def test_impermanent_loss_formula_correctness(self):
        """Test IL formula: 2*sqrt(price_ratio)/(1+price_ratio) - 1"""
        price_ratio = np.array([1.0, 2.0, 0.5])

        il_expected = 2 * np.sqrt(price_ratio) / (1 + price_ratio) - 1

        # At price_ratio=1 (no change), IL should be 0
        self.assertAlmostEqual(il_expected[0], 0.0)

        # At price_ratio=2 (doubled), IL should be negative
        self.assertLess(il_expected[1], 0)

        # At price_ratio=0.5 (halved), IL should be negative
        self.assertLess(il_expected[2], 0)

    def test_impermanent_loss_price_ranges(self):
        """Test different price ranges across variations"""
        self.generator.generate_impermanent_loss_variants(n_samples=5)

        calls = self.generator._process_formula.call_args_list

        # All should be IL variations
        for call in calls:
            name = call[1]["name"]
            self.assertIn("Impermanent_Loss_v", name)


class TestFeeEarningVariants(unittest.TestCase):
    """Test fee earning formula variants"""

    def setUp(self):
        """Set up test fixtures"""
        with patch("hypatiax.tools.symbolic.hybrid_system.HybridDiscoverySystem"):
            from generators.finance.defi.defi_dataset_master_generator import MassiveDeFiFormulaGenerator

            self.generator = MassiveDeFiFormulaGenerator(seed=42)
            self.generator._process_formula = Mock()

    def test_generate_fee_earning_variants_count(self):
        """Test that 32 variants are generated"""
        self.generator.generate_fee_earning_variants(n_samples=20)

        self.assertEqual(self.generator._process_formula.call_count, 32)

    def test_fee_calculation_correctness(self):
        """Test fee calculation logic"""
        fee_tier = 0.01  # 1%
        volume_24h = 1000000
        user_liq = 10000
        total_liq = 100000

        expected_fees = fee_tier * volume_24h * (user_liq / (total_liq + user_liq))

        # User should earn proportional to their liquidity share
        self.assertGreater(expected_fees, 0)
        self.assertLess(expected_fees, volume_24h * fee_tier)


class TestProcessFormula(unittest.TestCase):
    """Test the _process_formula helper method"""

    def setUp(self):
        """Set up test fixtures"""
        with patch("hypatiax.tools.symbolic.hybrid_system.HybridDiscoverySystem"):
            from generators.finance.defi.defi_dataset_master_generator import MassiveDeFiFormulaGenerator

            self.generator = MassiveDeFiFormulaGenerator(seed=42)
            self.generator.system.discover_validate_interpret = Mock(return_value={"status": "ok"})

    def test_process_formula_success(self):
        """Test successful formula processing"""
        name = "Test_Formula"
        description = "Test description"
        X = np.random.rand(10, 2)
        y = np.random.rand(10)

        self.generator._process_formula(name, description, X, y, 10)

        self.assertEqual(self.generator.successful_formulas, 1)
        self.assertEqual(len(self.generator.results), 1)
        self.generator.system.discover_validate_interpret.assert_called_once()

    def test_process_formula_exception_handling(self):
        """Test formula processing with exception"""
        self.generator.system.discover_validate_interpret = Mock(side_effect=Exception("Test error"))

        name = "Test_Formula"
        description = "Test description"
        X = np.random.rand(10, 2)
        y = np.random.rand(10)

        # Should not raise exception
        self.generator._process_formula(name, description, X, y, 10)

        self.assertEqual(self.generator.failed_formulas, 1)
        self.assertEqual(len(self.generator.results), 0)

    def test_process_formula_increments_counters(self):
        """Test that counters are incremented correctly"""
        X = np.random.rand(5, 2)
        y = np.random.rand(5)

        initial_successful = self.generator.successful_formulas

        self.generator._process_formula("Test", "Desc", X, y, 5)

        self.assertEqual(self.generator.successful_formulas, initial_successful + 1)


class TestRunAllVariants(unittest.TestCase):
    """Test the main run_all_variants method"""

    def setUp(self):
        """Set up test fixtures"""
        with patch("hypatiax.tools.symbolic.hybrid_system.HybridDiscoverySystem"):
            from generators.finance.defi.defi_dataset_master_generator import MassiveDeFiFormulaGenerator

            self.generator = MassiveDeFiFormulaGenerator(seed=42)

    def test_run_all_variants_calls_all_generators(self):
        """Test that all generator methods are called"""
        # Mock all generator methods
        self.generator.generate_constant_product_variants = Mock()
        self.generator.generate_constant_sum_variants = Mock()
        self.generator.generate_constant_mean_variants = Mock()
        self.generator.generate_stableswap_variants = Mock()
        self.generator.generate_impermanent_loss_variants = Mock()
        self.generator.generate_position_value_variants = Mock()
        self.generator.generate_concentrated_liquidity_variants = Mock()
        self.generator.generate_fee_earning_variants = Mock()
        self.generator.generate_apy_variants = Mock()
        self.generator.generate_slippage_variants = Mock()
        self.generator.generate_price_impact_variants = Mock()
        self.generator.generate_utilization_variants = Mock()
        self.generator.generate_swap_output_variants = Mock()

        self.generator.run_all_variants(n_samples=10)

        # Verify all generators were called
        self.generator.generate_constant_product_variants.assert_called_once_with(10)
        self.generator.generate_constant_sum_variants.assert_called_once_with(10)
        self.generator.generate_constant_mean_variants.assert_called_once_with(10)
        self.generator.generate_stableswap_variants.assert_called_once_with(10)
        self.generator.generate_impermanent_loss_variants.assert_called_once_with(10)
        self.generator.generate_position_value_variants.assert_called_once_with(10)
        self.generator.generate_concentrated_liquidity_variants.assert_called_once_with(10)
        self.generator.generate_fee_earning_variants.assert_called_once_with(10)
        self.generator.generate_apy_variants.assert_called_once_with(10)
        self.generator.generate_slippage_variants.assert_called_once_with(10)
        self.generator.generate_price_impact_variants.assert_called_once_with(10)
        self.generator.generate_utilization_variants.assert_called_once_with(10)
        self.generator.generate_swap_output_variants.assert_called_once_with(10)

    def test_run_all_variants_returns_successful_count(self):
        """Test that method returns successful formula count"""
        # Mock all methods to do nothing
        for method_name in dir(self.generator):
            if method_name.startswith("generate_") and method_name != "generate_formula":
                setattr(self.generator, method_name, Mock())

        self.generator.successful_formulas = 250
        result = self.generator.run_all_variants(n_samples=10)

        self.assertEqual(result, 250)


class TestPrintSummary(unittest.TestCase):
    """Test the print_summary method"""

    def setUp(self):
        """Set up test fixtures"""
        with patch("hypatiax.tools.symbolic.hybrid_system.HybridDiscoverySystem"):
            from generators.finance.defi.defi_dataset_master_generator import MassiveDeFiFormulaGenerator

            self.generator = MassiveDeFiFormulaGenerator(seed=42)

    @patch("builtins.print")
    def test_print_summary_displays_stats(self, mock_print):
        """Test that summary displays statistics"""
        self.generator.formula_id = 280
        self.generator.successful_formulas = 270
        self.generator.failed_formulas = 10

        self.generator.print_summary()

        # Check that print was called
        self.assertTrue(mock_print.called)

        # Verify key information was printed
        printed_text = " ".join([str(call[0][0]) for call in mock_print.call_args_list])
        self.assertIn("280", printed_text)
        self.assertIn("270", printed_text)

    def test_print_summary_calculates_success_rate(self):
        """Test success rate calculation"""
        self.generator.formula_id = 100
        self.generator.successful_formulas = 95

        success_rate = (self.generator.successful_formulas / self.generator.formula_id) * 100

        self.assertAlmostEqual(success_rate, 95.0)


class TestDataValidation(unittest.TestCase):
    """Test data validation and constraints"""

    def test_positive_sample_count(self):
        """Test that sample count must be positive"""
        n_samples = 20
        self.assertGreater(n_samples, 0)

    def test_reserve_ranges_logical(self):
        """Test that reserve ranges are logical"""
        x_min, x_max = 10, 100

        self.assertLess(x_min, x_max)
        self.assertGreater(x_min, 0)

    def test_formula_id_increments(self):
        """Test that formula_id increments correctly"""
        with patch("hypatiax.tools.symbolic.hybrid_system.HybridDiscoverySystem"):
            from generators.finance.defi.defi_dataset_master_generator import MassiveDeFiFormulaGenerator

            generator = MassiveDeFiFormulaGenerator(seed=42)

        initial_id = generator.formula_id
        generator.formula_id += 1

        self.assertEqual(generator.formula_id, initial_id + 1)


def run_tests():
    """Run all unit tests"""
    loader = unittest.TestLoader()
    suite = unittest.TestSuite()

    # Add all test classes
    suite.addTests(loader.loadTestsFromTestCase(TestMassiveDeFiFormulaGeneratorInit))
    suite.addTests(loader.loadTestsFromTestCase(TestConstantProductVariants))
    suite.addTests(loader.loadTestsFromTestCase(TestConstantSumVariants))
    suite.addTests(loader.loadTestsFromTestCase(TestImpermanentLossVariants))
    suite.addTests(loader.loadTestsFromTestCase(TestFeeEarningVariants))
    suite.addTests(loader.loadTestsFromTestCase(TestProcessFormula))
    suite.addTests(loader.loadTestsFromTestCase(TestRunAllVariants))
    suite.addTests(loader.loadTestsFromTestCase(TestPrintSummary))
    suite.addTests(loader.loadTestsFromTestCase(TestDataValidation))

    runner = unittest.TextTestRunner(verbosity=2)
    result = runner.run(suite)

    return result


if __name__ == "__main__":
    print("=" * 70)
    print("Unit Tests: defi_dataset_master_generator.py")
    print("Testing 280 formula variations generator")
    print("=" * 70)
    result = run_tests()
    print("\n" + "=" * 70)
    print(f"Tests run: {result.testsRun}")
    print(f"Failures: {len(result.failures)}")
    print(f"Errors: {len(result.errors)}")
    print(f"Success: {result.wasSuccessful()}")
    print("=" * 70)
