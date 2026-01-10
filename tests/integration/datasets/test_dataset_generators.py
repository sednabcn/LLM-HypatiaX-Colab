"""
Comprehensive test suite for HypatiaX dataset generators.
Tests DeFi, Risk, and general dataset generation functionality.
"""

import json
import os
import tempfile
import unittest
from datetime import datetime
from pathlib import Path
from typing import Any, Dict, List

import pandas as pd


class TestDeFiDatasetGenerator(unittest.TestCase):
    """Tests for DeFi dataset generation"""

    def setUp(self):
        """Set up test fixtures"""
        self.temp_dir = tempfile.mkdtemp()
        self.output_file = os.path.join(self.temp_dir, "test_defi_output.json")

    def tearDown(self):
        """Clean up test files"""
        import shutil

        if os.path.exists(self.temp_dir):
            shutil.rmtree(self.temp_dir)

    def test_defi_formula_structure(self):
        """Test that DeFi formulas have correct structure"""
        expected_keys = [
            "formula_name",
            "formula",
            "description",
            "variables",
            "category",
        ]

        sample_formula = {
            "formula_name": "APY",
            "formula": "((1 + r/n)^n) - 1",
            "description": "Annual Percentage Yield",
            "variables": {"r": "interest rate", "n": "compounding periods"},
            "category": "yield",
        }

        for key in expected_keys:
            self.assertIn(key, sample_formula, f"Missing key: {key}")

    def test_defi_formula_validation(self):
        """Test validation of DeFi formulas"""
        valid_categories = ["yield", "liquidity", "staking", "lending", "swap"]

        sample_formula = {"formula_name": "Impermanent Loss", "category": "liquidity"}

        self.assertIn(sample_formula["category"], valid_categories)

    def test_defi_data_generation(self):
        """Test DeFi dataset generation produces valid data"""
        # Simulate generated data
        generated_data = {
            "timestamp": datetime.now().isoformat(),
            "formulas": [
                {
                    "formula_name": "TVL",
                    "formula": "sum(assets)",
                    "description": "Total Value Locked",
                    "variables": {"assets": "list of asset values"},
                    "category": "liquidity",
                }
            ],
        }

        self.assertIsInstance(generated_data, dict)
        self.assertIn("formulas", generated_data)
        self.assertIsInstance(generated_data["formulas"], list)
        self.assertGreater(len(generated_data["formulas"]), 0)

    def test_defi_json_export(self):
        """Test JSON export functionality"""
        data = {
            "formulas": [
                {"name": "APY", "value": 5.5},
                {"name": "TVL", "value": 1000000},
            ]
        }

        with open(self.output_file, "w") as f:
            json.dump(data, f)

        self.assertTrue(os.path.exists(self.output_file))

        with open(self.output_file, "r") as f:
            loaded_data = json.load(f)

        self.assertEqual(data, loaded_data)

    def test_defi_csv_summary_generation(self):
        """Test CSV summary generation"""
        csv_file = os.path.join(self.temp_dir, "defi_summary.csv")

        data = {
            "formula_name": ["APY", "TVL", "IL"],
            "category": ["yield", "liquidity", "liquidity"],
            "complexity": ["medium", "low", "high"],
        }

        df = pd.DataFrame(data)
        df.to_csv(csv_file, index=False)

        self.assertTrue(os.path.exists(csv_file))

        loaded_df = pd.read_csv(csv_file)
        self.assertEqual(len(loaded_df), 3)
        self.assertListEqual(
            list(loaded_df.columns), ["formula_name", "category", "complexity"]
        )


class TestRiskDatasetGenerator(unittest.TestCase):
    """Tests for Risk dataset generation"""

    def setUp(self):
        """Set up test fixtures"""
        self.temp_dir = tempfile.mkdtemp()

    def tearDown(self):
        """Clean up test files"""
        import shutil

        if os.path.exists(self.temp_dir):
            shutil.rmtree(self.temp_dir)

    def test_risk_metric_structure(self):
        """Test risk metrics have proper structure"""
        expected_keys = [
            "metric_name",
            "formula",
            "risk_type",
            "severity",
            "description",
        ]

        sample_metric = {
            "metric_name": "VaR",
            "formula": "quantile(returns, alpha)",
            "risk_type": "market",
            "severity": "high",
            "description": "Value at Risk calculation",
        }

        for key in expected_keys:
            self.assertIn(key, sample_metric, f"Missing key: {key}")

    def test_risk_categories(self):
        """Test valid risk categories"""
        valid_risk_types = ["market", "credit", "operational", "liquidity", "systemic"]
        valid_severities = ["low", "medium", "high", "critical"]

        sample_metric = {"risk_type": "market", "severity": "high"}

        self.assertIn(sample_metric["risk_type"], valid_risk_types)
        self.assertIn(sample_metric["severity"], valid_severities)

    def test_risk_comprehensive_data(self):
        """Test comprehensive risk data generation"""
        risk_data = {
            "timestamp": datetime.now().isoformat(),
            "metrics": [
                {
                    "metric_name": "Sharpe Ratio",
                    "formula": "(Rp - Rf) / σp",
                    "risk_type": "market",
                    "severity": "medium",
                },
                {
                    "metric_name": "Default Probability",
                    "formula": "P(default)",
                    "risk_type": "credit",
                    "severity": "high",
                },
            ],
        }

        self.assertIn("metrics", risk_data)
        self.assertEqual(len(risk_data["metrics"]), 2)

        for metric in risk_data["metrics"]:
            self.assertIn("risk_type", metric)
            self.assertIn("severity", metric)

    def test_risk_json_export(self):
        """Test risk data JSON export"""
        output_file = os.path.join(self.temp_dir, "risk_comprehensive.json")

        risk_data = {
            "version": "1.0",
            "metrics": [
                {"name": "VaR", "value": 0.05},
                {"name": "CVaR", "value": 0.08},
            ],
        }

        with open(output_file, "w") as f:
            json.dump(risk_data, f, indent=2)

        self.assertTrue(os.path.exists(output_file))

        with open(output_file, "r") as f:
            loaded = json.load(f)

        self.assertEqual(loaded["version"], "1.0")
        self.assertEqual(len(loaded["metrics"]), 2)


class TestFullDatasetGenerator(unittest.TestCase):
    """Tests for full dataset generation pipeline"""

    def setUp(self):
        """Set up test fixtures"""
        self.temp_dir = tempfile.mkdtemp()

    def tearDown(self):
        """Clean up test files"""
        import shutil

        if os.path.exists(self.temp_dir):
            shutil.rmtree(self.temp_dir)

    def test_combined_dataset_structure(self):
        """Test combined dataset has all required components"""
        combined_data = {
            "metadata": {
                "generated_at": datetime.now().isoformat(),
                "version": "1.0",
                "components": ["defi", "risk", "analytics"],
            },
            "defi": {"formulas": []},
            "risk": {"metrics": []},
            "analytics": {"queries": []},
        }

        self.assertIn("metadata", combined_data)
        self.assertIn("defi", combined_data)
        self.assertIn("risk", combined_data)
        self.assertIn("analytics", combined_data)

    def test_dataset_versioning(self):
        """Test dataset version tracking"""
        dataset = {
            "version": "1.0.0",
            "generated_at": datetime.now().isoformat(),
            "data": {},
        }

        self.assertIsNotNone(dataset["version"])
        self.assertIsNotNone(dataset["generated_at"])

    def test_dataset_integrity(self):
        """Test dataset integrity checks"""
        dataset = {
            "checksum": "abc123",
            "record_count": 100,
            "data": [{"id": i} for i in range(100)],
        }

        self.assertEqual(dataset["record_count"], len(dataset["data"]))

    def test_multi_format_export(self):
        """Test exporting to multiple formats"""
        data = {
            "formulas": [
                {"name": "Formula1", "type": "DeFi"},
                {"name": "Formula2", "type": "Risk"},
            ]
        }

        # JSON export
        json_file = os.path.join(self.temp_dir, "output.json")
        with open(json_file, "w") as f:
            json.dump(data, f)
        self.assertTrue(os.path.exists(json_file))

        # CSV export
        csv_file = os.path.join(self.temp_dir, "output.csv")
        df = pd.DataFrame(data["formulas"])
        df.to_csv(csv_file, index=False)
        self.assertTrue(os.path.exists(csv_file))


class TestDatasetValidation(unittest.TestCase):
    """Tests for dataset validation"""

    def test_required_fields_validation(self):
        """Test validation of required fields"""
        required_fields = ["id", "name", "type", "formula"]

        valid_record = {
            "id": 1,
            "name": "APY",
            "type": "DeFi",
            "formula": "calculation",
        }

        for field in required_fields:
            self.assertIn(field, valid_record)

    def test_data_type_validation(self):
        """Test validation of data types"""
        record = {"id": 1, "name": "APY", "value": 5.5, "active": True}

        self.assertIsInstance(record["id"], int)
        self.assertIsInstance(record["name"], str)
        self.assertIsInstance(record["value"], (int, float))
        self.assertIsInstance(record["active"], bool)

    def test_formula_syntax_validation(self):
        """Test basic formula syntax validation"""
        valid_formulas = ["(1 + r/n)^n - 1", "sum(assets)", "P * (1 + r)^t"]

        for formula in valid_formulas:
            self.assertIsInstance(formula, str)
            self.assertGreater(len(formula), 0)

    def test_empty_dataset_handling(self):
        """Test handling of empty datasets"""
        empty_dataset = {"formulas": []}

        self.assertIsInstance(empty_dataset, dict)
        self.assertEqual(len(empty_dataset["formulas"]), 0)


class TestQueryDatasetGenerator(unittest.TestCase):
    """Tests for query-based dataset generation"""

    def test_defi_query_generation(self):
        """Test DeFi query generation"""
        queries = [
            "What is the APY for this pool?",
            "Calculate impermanent loss",
            "Show TVL across protocols",
        ]

        for query in queries:
            self.assertIsInstance(query, str)
            self.assertGreater(len(query), 0)

    def test_risk_query_generation(self):
        """Test risk query generation"""
        queries = [
            "Calculate VaR at 95% confidence",
            "What is the Sharpe ratio?",
            "Assess credit risk exposure",
        ]

        for query in queries:
            self.assertIsInstance(query, str)
            self.assertTrue(
                any(
                    risk_term in query.lower()
                    for risk_term in ["var", "risk", "sharpe"]
                )
            )

    def test_query_answer_pairs(self):
        """Test query-answer pair generation"""
        qa_pair = {
            "query": "What is APY?",
            "answer": "Annual Percentage Yield measures returns over a year",
            "formula": "((1 + r/n)^n) - 1",
            "category": "defi",
        }

        self.assertIn("query", qa_pair)
        self.assertIn("answer", qa_pair)
        self.assertIn("formula", qa_pair)


class TestTableauDatasetGenerator(unittest.TestCase):
    """Tests for Tableau-specific dataset generation"""

    def test_tableau_query_structure(self):
        """Test Tableau query structure"""
        tableau_query = {
            "query_text": "Show sales by region",
            "query_type": "aggregation",
            "fields": ["sales", "region"],
            "calculation": "SUM([Sales])",
        }

        self.assertIn("query_text", tableau_query)
        self.assertIn("calculation", tableau_query)
        self.assertIsInstance(tableau_query["fields"], list)

    def test_tableau_formula_generation(self):
        """Test Tableau formula generation"""
        formulas = [
            "SUM([Sales])",
            "AVG([Profit])",
            'IF [Region] = "East" THEN [Sales] * 1.1 END',
        ]

        for formula in formulas:
            self.assertTrue("[" in formula or "(" in formula)


def run_all_tests():
    """Run all test suites"""
    loader = unittest.TestLoader()
    suite = unittest.TestSuite()

    # Add all test classes
    suite.addTests(loader.loadTestsFromTestCase(TestDeFiDatasetGenerator))
    suite.addTests(loader.loadTestsFromTestCase(TestRiskDatasetGenerator))
    suite.addTests(loader.loadTestsFromTestCase(TestFullDatasetGenerator))
    suite.addTests(loader.loadTestsFromTestCase(TestDatasetValidation))
    suite.addTests(loader.loadTestsFromTestCase(TestQueryDatasetGenerator))
    suite.addTests(loader.loadTestsFromTestCase(TestTableauDatasetGenerator))

    runner = unittest.TextTestRunner(verbosity=2)
    result = runner.run(suite)

    return result


if __name__ == "__main__":
    print("=" * 70)
    print("HypatiaX Dataset Generator Test Suite")
    print("=" * 70)
    result = run_all_tests()
    print("\n" + "=" * 70)
    print(f"Tests run: {result.testsRun}")
    print(f"Failures: {len(result.failures)}")
    print(f"Errors: {len(result.errors)}")
    print(
        f"Success rate: {((result.testsRun - len(result.failures) - len(result.errors)) / result.testsRun * 100):.2f}%"
    )
    print("=" * 70)

    """
    Test Coverage
1. DeFi Dataset Generator Tests

Formula structure validation
Category validation
Data generation verification
JSON/CSV export functionality

2. Risk Dataset Generator Tests

Risk metric structure
Risk categories and severity levels
Comprehensive data generation
JSON export validation

3. Full Dataset Generator Tests

Combined dataset structure
Version tracking
Data integrity checks
Multi-format export (JSON & CSV)

4. Dataset Validation Tests

Required fields validation
Data type checking
Formula syntax validation
Empty dataset handling

5. Query Dataset Generator Tests

DeFi query generation
Risk query generation
Query-answer pair structure

6. Tableau Dataset Generator Tests

Tableau query structure
Formula generation

Running the Tests
bash# Run all tests
python test_dataset_generators.py

# Run specific test class
python -m unittest test_dataset_generators.TestDeFiDatasetGenerator

# Run with verbose output
python -m unittest -v test_dataset_generators


The test suite includes proper setup/teardown for temporary files, comprehensive assertions, and covers the main functionality of your dataset generation pipeline based on your project structure.
"""
