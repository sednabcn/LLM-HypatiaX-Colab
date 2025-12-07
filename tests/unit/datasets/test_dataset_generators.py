"""
Pure Unit Tests for HypatiaX Dataset Generators.
Each test focuses on a single function/method in isolation with mocked dependencies.
"""

import json
import unittest
from datetime import datetime
from unittest.mock import MagicMock, Mock, mock_open, patch

import pandas as pd


# Mock Classes (representing your actual generator classes)
class DeFiDatasetGenerator:
    """Mock DeFi dataset generator"""

    def validate_formula(self, formula_dict):
        """Validate a single formula structure"""
        required_keys = ["formula_name", "formula", "description", "variables", "category"]
        return all(key in formula_dict for key in required_keys)

    def validate_category(self, category):
        """Validate formula category"""
        valid_categories = ["yield", "liquidity", "staking", "lending", "swap"]
        return category in valid_categories

    def calculate_apy(self, rate, periods):
        """Calculate APY"""
        if periods <= 0:
            raise ValueError("Periods must be positive")
        return ((1 + rate / periods) ** periods) - 1

    def format_formula_name(self, name):
        """Format formula name"""
        return name.strip().upper()


class RiskDatasetGenerator:
    """Mock Risk dataset generator"""

    def validate_risk_metric(self, metric_dict):
        """Validate risk metric structure"""
        required_keys = ["metric_name", "formula", "risk_type", "severity"]
        return all(key in metric_dict for key in required_keys)

    def validate_severity(self, severity):
        """Validate severity level"""
        valid_severities = ["low", "medium", "high", "critical"]
        return severity in valid_severities

    def calculate_sharpe_ratio(self, returns, risk_free_rate, std_dev):
        """Calculate Sharpe ratio"""
        if std_dev == 0:
            raise ValueError("Standard deviation cannot be zero")
        return (returns - risk_free_rate) / std_dev


class DatasetExporter:
    """Mock dataset exporter"""

    def to_json(self, data, filepath):
        """Export to JSON"""
        with open(filepath, "w") as f:
            json.dump(data, f)
        return True

    def to_csv(self, data, filepath):
        """Export to CSV"""
        df = pd.DataFrame(data)
        df.to_csv(filepath, index=False)
        return True

    def generate_timestamp(self):
        """Generate ISO timestamp"""
        return datetime.now().isoformat()


# Unit Tests
class TestDeFiDatasetGeneratorUnit(unittest.TestCase):
    """Pure unit tests for DeFi generator methods"""

    def setUp(self):
        """Set up test instance"""
        self.generator = DeFiDatasetGenerator()

    def test_validate_formula_with_valid_data(self):
        """Test formula validation with valid input"""
        valid_formula = {
            "formula_name": "APY",
            "formula": "((1 + r/n)^n) - 1",
            "description": "Annual Percentage Yield",
            "variables": {"r": "rate", "n": "periods"},
            "category": "yield",
        }
        self.assertTrue(self.generator.validate_formula(valid_formula))

    def test_validate_formula_with_missing_keys(self):
        """Test formula validation with missing keys"""
        invalid_formula = {
            "formula_name": "APY",
            "formula": "((1 + r/n)^n) - 1",
            # Missing: description, variables, category
        }
        self.assertFalse(self.generator.validate_formula(invalid_formula))

    def test_validate_formula_with_empty_dict(self):
        """Test formula validation with empty dictionary"""
        self.assertFalse(self.generator.validate_formula({}))

    def test_validate_category_with_valid_input(self):
        """Test category validation with valid category"""
        self.assertTrue(self.generator.validate_category("yield"))
        self.assertTrue(self.generator.validate_category("liquidity"))
        self.assertTrue(self.generator.validate_category("staking"))

    def test_validate_category_with_invalid_input(self):
        """Test category validation with invalid category"""
        self.assertFalse(self.generator.validate_category("invalid"))
        self.assertFalse(self.generator.validate_category(""))
        self.assertFalse(self.generator.validate_category("YIELD"))

    def test_calculate_apy_with_valid_inputs(self):
        """Test APY calculation with valid inputs"""
        result = self.generator.calculate_apy(0.05, 12)
        self.assertAlmostEqual(result, 0.05116, places=5)

    def test_calculate_apy_with_zero_periods(self):
        """Test APY calculation with zero periods raises error"""
        with self.assertRaises(ValueError):
            self.generator.calculate_apy(0.05, 0)

    def test_calculate_apy_with_negative_periods(self):
        """Test APY calculation with negative periods raises error"""
        with self.assertRaises(ValueError):
            self.generator.calculate_apy(0.05, -1)

    def test_format_formula_name_removes_whitespace(self):
        """Test formula name formatting removes whitespace"""
        result = self.generator.format_formula_name("  apy  ")
        self.assertEqual(result, "APY")

    def test_format_formula_name_converts_to_uppercase(self):
        """Test formula name formatting converts to uppercase"""
        result = self.generator.format_formula_name("tvl")
        self.assertEqual(result, "TVL")


class TestRiskDatasetGeneratorUnit(unittest.TestCase):
    """Pure unit tests for Risk generator methods"""

    def setUp(self):
        """Set up test instance"""
        self.generator = RiskDatasetGenerator()

    def test_validate_risk_metric_with_valid_data(self):
        """Test risk metric validation with valid input"""
        valid_metric = {
            "metric_name": "VaR",
            "formula": "quantile(returns, 0.05)",
            "risk_type": "market",
            "severity": "high",
        }
        self.assertTrue(self.generator.validate_risk_metric(valid_metric))

    def test_validate_risk_metric_with_missing_keys(self):
        """Test risk metric validation with missing keys"""
        invalid_metric = {
            "metric_name": "VaR",
            "formula": "quantile(returns, 0.05)",
            # Missing: risk_type, severity
        }
        self.assertFalse(self.generator.validate_risk_metric(invalid_metric))

    def test_validate_severity_with_valid_levels(self):
        """Test severity validation with valid levels"""
        self.assertTrue(self.generator.validate_severity("low"))
        self.assertTrue(self.generator.validate_severity("medium"))
        self.assertTrue(self.generator.validate_severity("high"))
        self.assertTrue(self.generator.validate_severity("critical"))

    def test_validate_severity_with_invalid_levels(self):
        """Test severity validation with invalid levels"""
        self.assertFalse(self.generator.validate_severity("extreme"))
        self.assertFalse(self.generator.validate_severity(""))
        self.assertFalse(self.generator.validate_severity("HIGH"))

    def test_calculate_sharpe_ratio_with_valid_inputs(self):
        """Test Sharpe ratio calculation with valid inputs"""
        result = self.generator.calculate_sharpe_ratio(0.12, 0.02, 0.15)
        self.assertAlmostEqual(result, 0.6667, places=4)

    def test_calculate_sharpe_ratio_with_zero_std_dev(self):
        """Test Sharpe ratio calculation with zero std dev raises error"""
        with self.assertRaises(ValueError):
            self.generator.calculate_sharpe_ratio(0.12, 0.02, 0)

    def test_calculate_sharpe_ratio_with_negative_returns(self):
        """Test Sharpe ratio calculation with negative returns"""
        result = self.generator.calculate_sharpe_ratio(-0.05, 0.02, 0.15)
        self.assertAlmostEqual(result, -0.4667, places=4)


class TestDatasetExporterUnit(unittest.TestCase):
    """Pure unit tests for DatasetExporter methods"""

    def setUp(self):
        """Set up test instance"""
        self.exporter = DatasetExporter()

    @patch("builtins.open", new_callable=mock_open)
    @patch("json.dump")
    def test_to_json_calls_json_dump(self, mock_json_dump, mock_file):
        """Test JSON export calls json.dump"""
        data = {"test": "data"}
        filepath = "/tmp/test.json"

        result = self.exporter.to_json(data, filepath)

        self.assertTrue(result)
        mock_file.assert_called_once_with(filepath, "w")
        mock_json_dump.assert_called_once()

    @patch("pandas.DataFrame.to_csv")
    @patch("pandas.DataFrame")
    def test_to_csv_calls_dataframe_to_csv(self, mock_df_class, mock_to_csv):
        """Test CSV export calls DataFrame.to_csv"""
        data = [{"a": 1}, {"a": 2}]
        filepath = "/tmp/test.csv"

        mock_df_instance = MagicMock()
        mock_df_class.return_value = mock_df_instance

        result = self.exporter.to_csv(data, filepath)

        self.assertTrue(result)
        mock_df_class.assert_called_once_with(data)

    def test_generate_timestamp_returns_string(self):
        """Test timestamp generation returns string"""
        timestamp = self.exporter.generate_timestamp()
        self.assertIsInstance(timestamp, str)

    def test_generate_timestamp_is_iso_format(self):
        """Test timestamp is in ISO format"""
        timestamp = self.exporter.generate_timestamp()
        # Should be parseable by datetime
        parsed = datetime.fromisoformat(timestamp)
        self.assertIsInstance(parsed, datetime)


class TestFormulaValidationUnit(unittest.TestCase):
    """Unit tests for formula validation functions"""

    def test_is_valid_formula_structure(self):
        """Test formula structure validation"""

        def is_valid_structure(formula):
            return isinstance(formula, str) and len(formula) > 0

        self.assertTrue(is_valid_structure("x + y"))
        self.assertFalse(is_valid_structure(""))
        self.assertFalse(is_valid_structure(123))

    def test_has_balanced_parentheses(self):
        """Test parentheses balancing check"""

        def has_balanced_parens(formula):
            count = 0
            for char in formula:
                if char == "(":
                    count += 1
                elif char == ")":
                    count -= 1
                if count < 0:
                    return False
            return count == 0

        self.assertTrue(has_balanced_parens("(a + b) * c"))
        self.assertTrue(has_balanced_parens("((a + b) * (c + d))"))
        self.assertFalse(has_balanced_parens("(a + b"))
        self.assertFalse(has_balanced_parens("a + b)"))
        self.assertFalse(has_balanced_parens(")("))


class TestDataNormalizationUnit(unittest.TestCase):
    """Unit tests for data normalization functions"""

    def test_normalize_string(self):
        """Test string normalization"""

        def normalize_string(s):
            return s.strip().lower()

        self.assertEqual(normalize_string("  APY  "), "apy")
        self.assertEqual(normalize_string("TVL"), "tvl")
        self.assertEqual(normalize_string(""), "")

    def test_normalize_numeric_value(self):
        """Test numeric value normalization"""

        def normalize_numeric(value, decimals=2):
            return round(float(value), decimals)

        self.assertEqual(normalize_numeric(5.12345, 2), 5.12)
        self.assertEqual(normalize_numeric("3.7", 1), 3.7)
        self.assertEqual(normalize_numeric(10, 2), 10.0)

    def test_sanitize_field_name(self):
        """Test field name sanitization"""

        def sanitize_field_name(name):
            return name.replace(" ", "_").replace("-", "_").lower()

        self.assertEqual(sanitize_field_name("Formula Name"), "formula_name")
        self.assertEqual(sanitize_field_name("Risk-Type"), "risk_type")
        self.assertEqual(sanitize_field_name("APY"), "apy")


class TestQueryGenerationUnit(unittest.TestCase):
    """Unit tests for query generation functions"""

    def test_generate_defi_query(self):
        """Test DeFi query generation"""

        def generate_query(formula_name, action="calculate"):
            return f"{action.capitalize()} {formula_name}"

        self.assertEqual(generate_query("APY"), "Calculate APY")
        self.assertEqual(generate_query("TVL", "show"), "Show TVL")

    def test_generate_query_with_params(self):
        """Test query generation with parameters"""

        def generate_query_with_params(formula, params):
            param_str = ", ".join(f"{k}={v}" for k, v in params.items())
            return f"Calculate {formula} with {param_str}"

        result = generate_query_with_params("APY", {"rate": 0.05, "periods": 12})
        self.assertIn("APY", result)
        self.assertIn("rate=0.05", result)
        self.assertIn("periods=12", result)


class TestErrorHandlingUnit(unittest.TestCase):
    """Unit tests for error handling"""

    def test_handle_missing_field(self):
        """Test handling of missing required field"""

        def check_required_fields(data, required):
            missing = [field for field in required if field not in data]
            if missing:
                raise KeyError(f"Missing fields: {missing}")
            return True

        with self.assertRaises(KeyError):
            check_required_fields({"a": 1}, ["a", "b", "c"])

    def test_handle_invalid_type(self):
        """Test handling of invalid data type"""

        def validate_type(value, expected_type):
            if not isinstance(value, expected_type):
                raise TypeError(f"Expected {expected_type}, got {type(value)}")
            return True

        self.assertTrue(validate_type(5, int))
        with self.assertRaises(TypeError):
            validate_type("5", int)


def run_unit_tests():
    """Run all unit tests"""
    loader = unittest.TestLoader()
    suite = unittest.TestSuite()

    # Add all unit test classes
    suite.addTests(loader.loadTestsFromTestCase(TestDeFiDatasetGeneratorUnit))
    suite.addTests(loader.loadTestsFromTestCase(TestRiskDatasetGeneratorUnit))
    suite.addTests(loader.loadTestsFromTestCase(TestDatasetExporterUnit))
    suite.addTests(loader.loadTestsFromTestCase(TestFormulaValidationUnit))
    suite.addTests(loader.loadTestsFromTestCase(TestDataNormalizationUnit))
    suite.addTests(loader.loadTestsFromTestCase(TestQueryGenerationUnit))
    suite.addTests(loader.loadTestsFromTestCase(TestErrorHandlingUnit))

    runner = unittest.TextTestRunner(verbosity=2)
    result = runner.run(suite)

    return result


if __name__ == "__main__":
    print("=" * 70)
    print("HypatiaX Dataset Generator - UNIT TESTS")
    print("Testing individual functions in isolation with mocked dependencies")
    print("=" * 70)
    result = run_unit_tests()
    print("\n" + "=" * 70)
    print(f"Tests run: {result.testsRun}")
    print(f"Failures: {len(result.failures)}")
    print(f"Errors: {len(result.errors)}")
    print(
        f"Success rate: {((result.testsRun - len(result.failures) - len(result.errors)) / result.testsRun * 100):.2f}%"
    )
    print("=" * 70)

    """

What Makes These True Unit Tests:
✅ Isolated Testing

Each test focuses on one function/method only
No dependencies on external systems (files, databases, APIs)

✅ Mocked Dependencies

Uses @patch and mock_open to mock file I/O
Uses MagicMock for pandas DataFrame operations
Tests behavior without actually writing files

✅ Fast Execution

No I/O operations = runs in milliseconds
No setup/teardown of temp directories

✅ Single Responsibility

Each test validates ONE behavior
Clear test names describe exactly what's being tested

✅ Independent Tests

Tests don't depend on each other
Can run in any order

Test Categories:

Validation Tests - Test validation logic only
Calculation Tests - Test mathematical functions
Formatting Tests - Test string manipulation
Error Handling Tests - Test exception raising
Export Tests - Test with mocked I/O

The previous version was mixing unit tests with integration tests (testing file operations, CSV generation, etc.)

 """
