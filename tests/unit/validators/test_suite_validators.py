#!/usr/bin/env python3
"""
Comprehensive Validator Test Suite
Tests all validators: Ensemble, Domain, Dimensional, and their integration

This suite tests:
1. Individual validator functionality
2. Cross-validator integration
3. Edge cases and error handling
4. Performance and memory management
5. Domain-specific validation rules
"""

import json
import sys
import time
from datetime import datetime
from pathlib import Path
from typing import Any, Dict, List, Tuple

import numpy as np

# Add project root to path
project_root = Path(__file__).parent.parent.parent
sys.path.insert(0, str(project_root))

# Try importing validators, provide mocks if not available
try:
    from tools.validation.dimensional_validator import DimensionalValidator
    from tools.validation.domain_validator import DomainValidator
    from tools.validation.ensemble_validator import EnsembleValidator

    VALIDATORS_AVAILABLE = True
except ImportError as e:
    print(f"⚠️  Import warning: {e}")
    print("Creating mock validators for testing...")
    VALIDATORS_AVAILABLE = False

    # Mock implementations (simplified)
    class DimensionalValidator:
        def __init__(self, max_history=1000):
            self.validation_history = []

        def validate(self, expression_str, variable_units):
            score = 100.0
            errors = []
            warnings = []

            if "+" in expression_str or "-" in expression_str:
                units = list(set(variable_units.values()))
                if len(units) > 1:
                    errors.append("Incompatible units in addition/subtraction")
                    score -= 20

            return {
                "valid": len(errors) == 0,
                "score": max(0, score),
                "errors": errors,
                "warnings": warnings,
                "dimensionally_consistent": len(errors) == 0,
                "variable_dimensions": variable_units,
            }

        def clear_history(self):
            self.validation_history = []

        def get_statistics(self):
            return {"total_validations": len(self.validation_history)}

    class DomainValidator:
        def __init__(self, domain, max_history=1000):
            self.domain = domain
            self.validation_history = []

        def validate(self, expression_str, variable_definitions, test_data=None):
            score = 100.0
            errors = []
            warnings = []

            if test_data:
                for var, values in test_data.items():
                    if "reserve" in var or "price" in var or "liquidity" in var:
                        if np.any(values < 0):
                            errors.append(f"{var} must be positive")
                            score -= 20

            return {
                "valid": len(errors) == 0,
                "score": max(0, score),
                "errors": errors,
                "warnings": warnings,
                "domain": self.domain,
                "constraints_checked": [],
            }

        def clear_history(self):
            self.validation_history = []

        def get_statistics(self):
            return {"total_validations": len(self.validation_history)}

    class EnsembleValidator:
        def __init__(self, domain="defi", max_history=1000, weights=None):
            self.domain = domain
            self.dimensional_validator = DimensionalValidator(max_history)
            self.domain_validator = DomainValidator(domain, max_history)
            self.validation_history = []
            self.weights = weights or {
                "symbolic": 0.35,
                "dimensional": 0.25,
                "domain": 0.30,
                "numerical": 0.10,
            }

        def validate_complete(
            self,
            expression_str,
            variable_definitions,
            variable_units,
            test_data=None,
            from_latex=False,
        ):
            dim_result = self.dimensional_validator.validate(
                expression_str, variable_units
            )
            dom_result = self.domain_validator.validate(
                expression_str, variable_definitions, test_data
            )

            total_score = (
                self.weights["dimensional"] * dim_result["score"]
                + self.weights["domain"] * dom_result["score"]
                + self.weights["symbolic"] * 100.0
                + self.weights["numerical"] * 100.0
            )

            result = {
                "valid": dim_result["valid"] and dom_result["valid"],
                "total_score": total_score,
                "layer_scores": {
                    "symbolic": 100.0,
                    "dimensional": dim_result["score"],
                    "domain": dom_result["score"],
                    "numerical": 100.0,
                },
                "layer_results": {
                    "symbolic": {
                        "valid": True,
                        "score": 100.0,
                        "errors": [],
                        "warnings": [],
                    },
                    "dimensional": dim_result,
                    "domain": dom_result,
                    "numerical": {"score": 100.0, "errors": [], "warnings": []},
                },
                "errors": dim_result["errors"] + dom_result["errors"],
                "warnings": dim_result["warnings"] + dom_result["warnings"],
                "recommendations": [],
                "expression": expression_str,
                "domain": self.domain,
            }

            self.validation_history.append(result)
            return result

        def clear_history(self):
            self.validation_history = []
            self.dimensional_validator.clear_history()
            self.domain_validator.clear_history()

        def get_statistics(self):
            if not self.validation_history:
                return {
                    "total_validations": 0,
                    "success_rate": 0.0,
                    "average_total_score": 0.0,
                }
            total = len(self.validation_history)
            valid = sum(1 for v in self.validation_history if v["valid"])
            avg_score = sum(v["total_score"] for v in self.validation_history) / total
            return {
                "total_validations": total,
                "success_rate": valid / total,
                "average_total_score": avg_score,
            }

        def get_weakest_layer(self):
            if not self.validation_history:
                return None
            return "dimensional"


class ComprehensiveTestSuite:
    """Complete test suite for all validators"""

    def __init__(self):
        self.results = {
            "dimensional": [],
            "domain": [],
            "ensemble": [],
            "integration": [],
            "edge_cases": [],
            "performance": [],
        }
        self.start_time = None
        self.test_data = self._generate_test_data()

    def _generate_test_data(self) -> Dict[str, Any]:
        """Generate comprehensive test data"""
        return {
            "defi_expressions": [
                {
                    "name": "Basic Constant Product",
                    "expression": "reserve0 * reserve1",
                    "variables": {
                        "reserve0": "Token 0 reserve amount",
                        "reserve1": "Token 1 reserve amount",
                    },
                    "units": {"reserve0": "USD", "reserve1": "USD"},
                    "test_data": {
                        "reserve0": np.array([100.0, 200.0, 300.0, 400.0, 500.0]),
                        "reserve1": np.array([50.0, 100.0, 150.0, 200.0, 250.0]),
                    },
                    "expected_valid": True,
                    "expected_min_score": 85,
                },
                {
                    "name": "Price Ratio",
                    "expression": "reserve1 / reserve0",
                    "variables": {
                        "reserve0": "Token 0 reserve",
                        "reserve1": "Token 1 reserve",
                    },
                    "units": {"reserve0": "USD", "reserve1": "USD"},
                    "test_data": {
                        "reserve0": np.array([100.0, 200.0, 300.0]),
                        "reserve1": np.array([50.0, 100.0, 150.0]),
                    },
                    "expected_valid": True,
                    "expected_min_score": 90,
                },
                {
                    "name": "Impermanent Loss (Square Root)",
                    "expression": "sqrt(reserve0 * reserve1) / liquidity",
                    "variables": {
                        "reserve0": "Reserve 0",
                        "reserve1": "Reserve 1",
                        "liquidity": "Pool liquidity",
                    },
                    "units": {"reserve0": "USD", "reserve1": "USD", "liquidity": "USD"},
                    "test_data": {
                        "reserve0": np.array([100.0, 200.0, 300.0]),
                        "reserve1": np.array([100.0, 200.0, 300.0]),
                        "liquidity": np.array([100.0, 200.0, 300.0]),
                    },
                    "expected_valid": True,
                    "expected_min_score": 85,
                },
                {
                    "name": "INVALID: Negative Reserves",
                    "expression": "reserve0 + reserve1",
                    "variables": {"reserve0": "Reserve 0", "reserve1": "Reserve 1"},
                    "units": {"reserve0": "USD", "reserve1": "USD"},
                    "test_data": {
                        "reserve0": np.array([-100.0, 200.0, 300.0]),
                        "reserve1": np.array([50.0, 100.0, 150.0]),
                    },
                    "expected_valid": False,
                    "expected_max_score": 85,
                },
                {
                    "name": "INVALID: Dimensional Mismatch",
                    "expression": "price + volume",
                    "variables": {"price": "Token price", "volume": "Trading volume"},
                    "units": {"price": "USD", "volume": "USD**3"},
                    "test_data": {
                        "price": np.array([100.0, 200.0, 300.0]),
                        "volume": np.array([1000.0, 2000.0, 3000.0]),
                    },
                    "expected_valid": False,
                    "expected_max_score": 80,
                },
            ],
            "finance_expressions": [
                {
                    "name": "Portfolio Return",
                    "expression": "weight1 * return1 + weight2 * return2",
                    "variables": {
                        "weight1": "Asset 1 weight",
                        "weight2": "Asset 2 weight",
                        "return1": "Asset 1 return",
                        "return2": "Asset 2 return",
                    },
                    "units": {
                        "weight1": "dimensionless",
                        "weight2": "dimensionless",
                        "return1": "dimensionless",
                        "return2": "dimensionless",
                    },
                    "test_data": {
                        "weight1": np.array([0.6, 0.5, 0.7]),
                        "weight2": np.array([0.4, 0.5, 0.3]),
                        "return1": np.array([0.05, 0.10, -0.02]),
                        "return2": np.array([0.03, 0.08, 0.01]),
                    },
                    "expected_valid": True,
                    "expected_min_score": 80,
                }
            ],
            "risk_expressions": [
                {
                    "name": "Value at Risk",
                    "expression": "portfolio_value * volatility * confidence",
                    "variables": {
                        "portfolio_value": "Portfolio value",
                        "volatility": "Volatility measure",
                        "confidence": "Confidence level",
                    },
                    "units": {
                        "portfolio_value": "USD",
                        "volatility": "dimensionless",
                        "confidence": "dimensionless",
                    },
                    "test_data": {
                        "portfolio_value": np.array([10000.0, 20000.0, 30000.0]),
                        "volatility": np.array([0.15, 0.20, 0.25]),
                        "confidence": np.array([0.95, 0.95, 0.95]),
                    },
                    "expected_valid": True,
                    "expected_min_score": 85,
                }
            ],
        }

    def run_all_tests(self) -> Dict[str, Any]:
        """Run complete test suite"""
        self.start_time = time.time()

        print("=" * 80)
        print("COMPREHENSIVE VALIDATOR TEST SUITE")
        print("=" * 80)
        print(f"Testing: Ensemble, Domain, and Dimensional Validators")
        print(f"Mock Mode: {not VALIDATORS_AVAILABLE}")
        print("=" * 80)
        print()

        self._test_dimensional_validator()
        self._test_domain_validator()
        self._test_ensemble_validator()
        self._test_integration()
        self._test_edge_cases()
        self._test_performance()

        summary = self._generate_summary()
        self._save_results(summary)

        return summary

    def _test_dimensional_validator(self):
        """Test dimensional validator"""
        print("\n" + "=" * 80)
        print("TEST SUITE 1: DIMENSIONAL VALIDATOR")
        print("=" * 80)

        validator = DimensionalValidator(max_history=100)

        test_cases = [
            {
                "name": "Valid: Same Units Addition",
                "expr": "price1 + price2",
                "units": {"price1": "USD", "price2": "USD"},
                "should_pass": True,
            },
            {
                "name": "Invalid: Different Units Addition",
                "expr": "price + volume",
                "units": {"price": "USD", "volume": "USD**3"},
                "should_pass": False,
            },
            {
                "name": "Valid: Multiplication",
                "expr": "price * quantity",
                "units": {"price": "USD", "quantity": "dimensionless"},
                "should_pass": True,
            },
            {
                "name": "Valid: Division",
                "expr": "reserve0 / reserve1",
                "units": {"reserve0": "USD", "reserve1": "USD"},
                "should_pass": True,
            },
        ]

        passed = 0

        for idx, test in enumerate(test_cases, 1):
            print(f"\nTest {idx}/{len(test_cases)}: {test['name']}")
            print("-" * 80)

            result = validator.validate(
                expression_str=test["expr"], variable_units=test["units"]
            )

            test_passed = result["valid"] == test["should_pass"]

            print(f"Expression: {test['expr']}")
            print(f"Units: {test['units']}")
            print(f"Valid: {result['valid']} (Expected: {test['should_pass']})")
            print(f"Score: {result['score']:.2f}/100")

            if result["errors"]:
                print(f"Errors: {result['errors']}")
            if result["warnings"]:
                print(f"Warnings: {result['warnings']}")

            print("✅ TEST PASSED" if test_passed else "❌ TEST FAILED")
            if test_passed:
                passed += 1

            self.results["dimensional"].append(
                {"test": test["name"], "passed": test_passed, "result": result}
            )

        print(f"\n{'=' * 80}")
        print(f"Dimensional Validator: {passed}/{len(test_cases)} passed")
        print(f"{'=' * 80}")

        stats = validator.get_statistics()
        print(f"\nValidator Statistics:")
        print(f"  Total Validations: {stats.get('total_validations', 0)}")

    def _test_domain_validator(self):
        """Test domain validators for each domain"""
        print("\n" + "=" * 80)
        print("TEST SUITE 2: DOMAIN VALIDATOR")
        print("=" * 80)

        domains = ["defi", "risk", "finance"]

        for domain in domains:
            print(f"\n--- Testing {domain.upper()} Domain ---")

            validator = DomainValidator(domain=domain, max_history=100)

            if domain == "defi":
                test_cases = self.test_data["defi_expressions"][:3]
            elif domain == "finance":
                test_cases = self.test_data["finance_expressions"]
            elif domain == "risk":
                test_cases = self.test_data["risk_expressions"]
            else:
                continue

            for test in test_cases:
                result = validator.validate(
                    expression_str=test["expression"],
                    variable_definitions=test["variables"],
                    test_data=test.get("test_data"),
                )

                print(f"\n{test['name']}")
                print(f"  Valid: {result['valid']}")
                print(f"  Score: {result['score']:.2f}/100")
                if result["errors"]:
                    print(f"  Errors: {len(result['errors'])}")

                self.results["domain"].append(
                    {"domain": domain, "test": test["name"], "result": result}
                )

    def _test_ensemble_validator(self):
        """Test ensemble validator"""
        print("\n" + "=" * 80)
        print("TEST SUITE 3: ENSEMBLE VALIDATOR")
        print("=" * 80)

        validator = EnsembleValidator(domain="defi", max_history=100)

        passed = 0

        for idx, test in enumerate(self.test_data["defi_expressions"], 1):
            print(
                f"\nTest {idx}/{len(self.test_data['defi_expressions'])}: {test['name']}"
            )
            print("-" * 80)

            result = validator.validate_complete(
                expression_str=test["expression"],
                variable_definitions=test["variables"],
                variable_units=test["units"],
                test_data=test.get("test_data"),
            )

            valid_ok = result["valid"] == test.get("expected_valid", True)

            if test.get("expected_min_score"):
                score_ok = result["total_score"] >= test["expected_min_score"]
            elif test.get("expected_max_score"):
                score_ok = result["total_score"] <= test["expected_max_score"]
            else:
                score_ok = True

            test_passed = valid_ok and score_ok

            print(f"Expression: {test['expression']}")
            print(f"Overall Valid: {result['valid']}")
            print(f"Total Score: {result['total_score']:.2f}/100")
            print(f"\nLayer Scores:")
            for layer, score in result["layer_scores"].items():
                print(f"  {layer:12s}: {score:6.2f}/100")

            if result["errors"]:
                print(f"\nErrors: {len(result['errors'])}")
                for error in result["errors"][:2]:
                    print(f"  • {error}")

            print("✅ TEST PASSED" if test_passed else "❌ TEST FAILED")
            if test_passed:
                passed += 1

            self.results["ensemble"].append(
                {"test": test["name"], "passed": test_passed, "result": result}
            )

        print(f"\n{'=' * 80}")
        print(
            f"Ensemble Validator: {passed}/{len(self.test_data['defi_expressions'])} passed"
        )
        print(f"{'=' * 80}")

        stats = validator.get_statistics()
        print(f"\nEnsemble Statistics:")
        print(f"  Total Validations: {stats.get('total_validations', 0)}")
        print(f"  Success Rate: {stats.get('success_rate', 0):.1%}")
        print(f"  Average Score: {stats.get('average_total_score', 0):.2f}/100")

    def _test_integration(self):
        """Test integration between validators"""
        print("\n" + "=" * 80)
        print("TEST SUITE 4: VALIDATOR INTEGRATION")
        print("=" * 80)

        ensemble = EnsembleValidator(domain="defi")

        test_expr = "reserve0 * reserve1 / liquidity"
        test_vars = {
            "reserve0": "Reserve 0",
            "reserve1": "Reserve 1",
            "liquidity": "Liquidity",
        }
        test_units = {"reserve0": "USD", "reserve1": "USD", "liquidity": "USD"}
        test_data = {
            "reserve0": np.array([100.0, 200.0, 300.0]),
            "reserve1": np.array([100.0, 200.0, 300.0]),
            "liquidity": np.array([100.0, 200.0, 300.0]),
        }

        print("\n--- Test: Coordinated Validation ---")
        result = ensemble.validate_complete(
            expression_str=test_expr,
            variable_definitions=test_vars,
            variable_units=test_units,
            test_data=test_data,
        )

        print(f"Expression: {test_expr}")
        print(f"Total Score: {result['total_score']:.2f}")

        layers_ran = all(
            layer in result["layer_results"]
            for layer in ["symbolic", "dimensional", "domain", "numerical"]
        )

        print(
            "✅ All validation layers executed" if layers_ran else "❌ Missing layers"
        )

        self.results["integration"].append(
            {"test": "Coordinated Validation", "passed": layers_ran, "result": result}
        )

        print("\n--- Test: History Management ---")
        ensemble.clear_history()

        for i in range(5):
            ensemble.validate_complete(
                expression_str=test_expr,
                variable_definitions=test_vars,
                variable_units=test_units,
                test_data=test_data,
            )

        stats = ensemble.get_statistics()
        history_ok = stats["total_validations"] == 5
        print(f"History tracking: {stats['total_validations']} validations recorded")
        print(
            "✅ History management working"
            if history_ok
            else "❌ History management issue"
        )

        self.results["integration"].append(
            {"test": "History Management", "passed": history_ok, "stats": stats}
        )

    def _test_edge_cases(self):
        """Test edge cases and error handling"""
        print("\n" + "=" * 80)
        print("TEST SUITE 5: EDGE CASES")
        print("=" * 80)

        ensemble = EnsembleValidator(domain="defi")

        edge_cases = [
            {
                "name": "Empty Expression",
                "expr": "",
                "vars": {},
                "units": {},
                "should_error": True,
            },
            {
                "name": "Division by Zero Risk",
                "expr": "numerator / denominator",
                "vars": {"numerator": "Top", "denominator": "Bottom"},
                "units": {"numerator": "USD", "denominator": "USD"},
                "test_data": {
                    "numerator": np.array([100.0, 200.0]),
                    "denominator": np.array([0.0, 50.0]),
                },
                "should_warn": True,
            },
            {
                "name": "Very Large Numbers",
                "expr": "x * y",
                "vars": {"x": "X", "y": "Y"},
                "units": {"x": "USD", "y": "dimensionless"},
                "test_data": {
                    "x": np.array([1e15, 1e16, 1e17]),
                    "y": np.array([1e15, 1e16, 1e17]),
                },
                "should_warn": True,
            },
        ]

        for idx, test in enumerate(edge_cases, 1):
            print(f"\nEdge Case {idx}/{len(edge_cases)}: {test['name']}")
            print("-" * 80)

            try:
                result = ensemble.validate_complete(
                    expression_str=test["expr"],
                    variable_definitions=test["vars"],
                    variable_units=test["units"],
                    test_data=test.get("test_data"),
                )

                has_errors = len(result["errors"]) > 0
                has_warnings = len(result["warnings"]) > 0

                print(f"Validation completed without crash")
                print(f"Errors: {len(result['errors'])}")
                print(f"Warnings: {len(result['warnings'])}")

                test_passed = True
                if test.get("should_error"):
                    test_passed = has_errors or not result["valid"]
                elif test.get("should_warn"):
                    test_passed = has_warnings

                print(
                    "✅ Edge case handled correctly"
                    if test_passed
                    else "❌ Unexpected behavior"
                )

                self.results["edge_cases"].append(
                    {"test": test["name"], "passed": test_passed, "result": result}
                )

            except Exception as e:
                print(f"❌ Exception raised: {type(e).__name__}: {e}")
                self.results["edge_cases"].append(
                    {"test": test["name"], "passed": False, "error": str(e)}
                )

    def _test_performance(self):
        """Test performance and memory usage"""
        print("\n" + "=" * 80)
        print("TEST SUITE 6: PERFORMANCE")
        print("=" * 80)

        print("\n--- Test: Validation Speed ---")
        ensemble = EnsembleValidator(domain="defi")

        test_expr = "sqrt(reserve0 * reserve1) / liquidity"
        test_vars = {"reserve0": "R0", "reserve1": "R1", "liquidity": "L"}
        test_units = {"reserve0": "USD", "reserve1": "USD", "liquidity": "USD"}
        test_data = {
            "reserve0": np.random.rand(100) * 1000,
            "reserve1": np.random.rand(100) * 1000,
            "liquidity": np.random.rand(100) * 1000,
        }

        n_iterations = 100
        start = time.time()

        for i in range(n_iterations):
            result = ensemble.validate_complete(
                expression_str=test_expr,
                variable_definitions=test_vars,
                variable_units=test_units,
                test_data=test_data,
            )

        elapsed = time.time() - start
        avg_time = (elapsed / n_iterations) * 1000

        print(f"Total time for {n_iterations} validations: {elapsed:.3f}s")
        print(f"Average time per validation: {avg_time:.2f}ms")

        perf_ok = avg_time < 100  # Expect under 100ms
        print("✅ Performance acceptable" if perf_ok else "⚠️  Performance slow")

        self.results["performance"].append(
            {
                "test": "Validation Speed",
                "iterations": n_iterations,
                "total_time": elapsed,
                "avg_time_ms": avg_time,
                "passed": perf_ok,
            }
        )

    def _generate_summary(self) -> Dict[str, Any]:
        """Generate test summary"""
        total_tests = sum(len(v) for v in self.results.values())
        passed_tests = sum(
            sum(1 for t in tests if t.get("passed", False))
            for tests in self.results.values()
        )

        elapsed = time.time() - self.start_time

        return {
            "timestamp": datetime.now().isoformat(),
            "total_tests": total_tests,
            "passed_tests": passed_tests,
            "failed_tests": total_tests - passed_tests,
            "pass_rate": passed_tests / total_tests if total_tests > 0 else 0,
            "elapsed_seconds": elapsed,
            "mock_mode": not VALIDATORS_AVAILABLE,
            "results_by_category": self.results,
        }

    def _save_results(self, summary: Dict[str, Any]):
        """Save test results to file"""
        output_file = Path("validator_test_results.json")

        with open(output_file, "w") as f:
            json.dump(summary, f, indent=2, default=str)

        print(f"\n✅ Results saved to {output_file}")
        print(f"\nSummary:")
        print(f"  Total Tests: {summary['total_tests']}")
        print(f"  Passed: {summary['passed_tests']}")
        print(f"  Failed: {summary['failed_tests']}")
        print(f"  Pass Rate: {summary['pass_rate']:.1%}")
        print(f"  Time Elapsed: {summary['elapsed_seconds']:.2f}s")


if __name__ == "__main__":
    suite = ComprehensiveTestSuite()
    suite.run_all_tests()
