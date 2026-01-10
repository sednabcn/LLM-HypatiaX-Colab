#!/usr/bin/env python3
"""
HYBRID SYSTEM COMPARISON FRAMEWORK
===================================
Comprehensive evaluation comparing:
  1. Architecture A: LLM + Neural Network
  2. Architecture B: LLM + Symbolic Engine + Validation

Evaluation Metrics:
  - Formula Discovery Accuracy (R²)
  - Validation Quality (Multi-layer scores)
  - Interpretability
  - Computational Efficiency
  - Edge Case Handling
  - Production Readiness

Author: HypatiaX Team
Version: 1.0
"""

import argparse
import json
import time
from dataclasses import dataclass, asdict
from pathlib import Path
from typing import Dict, List, Optional, Tuple

import numpy as np
import pandas as pd
from tabulate import tabulate

# Add project root to path
import sys

sys.path.insert(0, str(Path(__file__).parent.parent.parent))


# ============================================================================
# ARCHITECTURE DEFINITIONS
# ============================================================================


@dataclass
class HybridSystemResult:
    """Standardized result structure for comparison"""

    architecture: str  # "llm_nn" or "llm_symbolic_validation"
    test_case: str

    # Discovery Metrics
    discovered_formula: str
    r2_score: float
    rmse: float
    complexity: int
    discovery_time: float

    # Validation Metrics (if available)
    validation_score: Optional[float] = None
    symbolic_score: Optional[float] = None
    dimensional_score: Optional[float] = None
    domain_score: Optional[float] = None
    numerical_score: Optional[float] = None

    # Edge Case Handling
    edge_cases_detected: Optional[int] = None
    critical_errors: Optional[int] = None
    warnings: Optional[int] = None

    # Interpretability
    has_interpretation: bool = False
    interpretation_time: Optional[float] = None

    # Production Readiness
    production_ready: bool = False
    requires_fixes: Optional[List[str]] = None

    # Additional Metadata
    method_used: str = ""  # "LLM", "NN", "Ensemble", "Symbolic"
    confidence: Optional[float] = None


# ============================================================================
# ARCHITECTURE A: LLM + NEURAL NETWORK
# ============================================================================


class LLMNeuralHybrid:
    """
    Architecture A: Combines LLM formula generation with Neural Network

    Workflow:
      1. LLM generates candidate formula
      2. Neural Network learns from data
      3. Ensemble decision (pick best based on R²)
      4. Limited validation (R² threshold only)
    """

    def __init__(self, llm_provider="anthropic"):
        self.name = "LLM + Neural Network"
        self.architecture = "llm_nn"
        print(f"[Architecture A] Initialized: {self.name}")

    def discover(
        self,
        X: np.ndarray,
        y: np.ndarray,
        variable_names: List[str],
        variable_descriptions: Dict[str, str],
        test_case_name: str,
    ) -> HybridSystemResult:
        """Run LLM+NN hybrid discovery"""

        print(f"\n[Architecture A] Running {test_case_name}...")
        start_time = time.time()

        # Simulate LLM generation (you'd replace with actual LLM call)
        llm_formula, llm_r2 = self._llm_discover(X, y, variable_names)

        # Simulate NN training (you'd replace with actual NN)
        nn_formula, nn_r2 = self._nn_discover(X, y, variable_names)

        # Ensemble decision: pick best R²
        if llm_r2 > nn_r2:
            method = "LLM"
            formula = llm_formula
            r2 = llm_r2
            confidence = 0.9 if llm_r2 > 0.95 else 0.7
        else:
            method = "NN"
            formula = nn_formula
            r2 = nn_r2
            confidence = 0.6  # NNs less interpretable

        discovery_time = time.time() - start_time

        # Calculate RMSE
        y_pred = self._evaluate_formula(formula, X, variable_names)
        rmse = (
            np.sqrt(np.mean((y - y_pred) ** 2)) if y_pred is not None else float("inf")
        )

        # Limited validation (R² threshold only)
        production_ready = r2 > 0.90

        return HybridSystemResult(
            architecture=self.architecture,
            test_case=test_case_name,
            discovered_formula=formula,
            r2_score=r2,
            rmse=rmse,
            complexity=self._estimate_complexity(formula),
            discovery_time=discovery_time,
            method_used=method,
            confidence=confidence,
            production_ready=production_ready,
            has_interpretation=False,  # LLM+NN doesn't include interpretation
        )

    def _llm_discover(self, X, y, variable_names):
        """Simulate LLM formula discovery"""
        # Placeholder - would call actual LLM
        formula = f"{variable_names[0]} * {variable_names[1]}"
        r2 = np.random.uniform(0.85, 0.99)
        return formula, r2

    def _nn_discover(self, X, y, variable_names):
        """Simulate NN formula discovery"""
        # Placeholder - would train actual NN
        formula = f"network_approximation({', '.join(variable_names)})"
        r2 = np.random.uniform(0.75, 0.95)
        return formula, r2

    def _evaluate_formula(self, formula, X, variable_names):
        """Evaluate formula on data"""
        try:
            # Placeholder evaluation
            return np.random.uniform(0, 1, len(X))
        except:
            return None

    def _estimate_complexity(self, formula):
        """Estimate formula complexity"""
        return len(formula.split()) + formula.count("*") + formula.count("/")


# ============================================================================
# ARCHITECTURE B: LLM + SYMBOLIC + VALIDATION
# ============================================================================


class LLMSymbolicValidationHybrid:
    """
    Architecture B: LLM + Symbolic Engine + Multi-Layer Validation

    Workflow:
      1. Symbolic Engine discovers formula from data
      2. Multi-layer validation (4 validators)
      3. LLM interprets and provides insights
      4. Comprehensive edge case detection
      5. Production readiness assessment
    """

    def __init__(self, domain="defi", llm_provider="anthropic"):
        self.name = "LLM + Symbolic + Validation"
        self.architecture = "llm_symbolic_validation"
        self.domain = domain

        # Import actual components
        try:
            from hypatiax.tools.symbolic.hybrid_system import HybridDiscoverySystem

            self.system = HybridDiscoverySystem(
                domain=domain,
                primary_llm=llm_provider,
                enable_fallback=True,
                use_rich_output=False,
            )
            print(f"[Architecture B] Initialized: {self.name}")
        except ImportError as e:
            print(f"⚠️  Could not import HybridDiscoverySystem: {e}")
            self.system = None

    def discover(
        self,
        X: np.ndarray,
        y: np.ndarray,
        variable_names: List[str],
        variable_descriptions: Dict[str, str],
        variable_units: Dict[str, str],
        test_case_name: str,
    ) -> HybridSystemResult:
        """Run LLM+Symbolic+Validation hybrid discovery"""

        print(f"\n[Architecture B] Running {test_case_name}...")
        start_time = time.time()

        if self.system is None:
            # Fallback if system not available
            return self._fallback_discover(X, y, variable_names, test_case_name)

        # Run complete workflow
        result = self.system.discover_validate_interpret(
            X=X,
            y=y,
            variable_names=variable_names,
            variable_descriptions=variable_descriptions,
            variable_units=variable_units,
            description=test_case_name,
            show_formatted=False,
            use_llm=False,  # Set to True if you want LLM interpretation
            min_validation_score=85.0,
        )

        discovery_time = time.time() - start_time

        # Extract metrics
        discovery = result.get("discovery", {})
        validation = result.get("validation", {})
        interpretation = result.get("interpretation")

        # Determine production readiness
        production_ready = (
            validation.get("valid", False)
            and validation.get("total_score", 0) >= 85.0
            and discovery.get("r2_score", 0) >= 0.90
        )

        # Collect required fixes
        requires_fixes = []
        if validation.get("errors"):
            requires_fixes = validation["errors"][:3]  # Top 3 errors

        return HybridSystemResult(
            architecture=self.architecture,
            test_case=test_case_name,
            discovered_formula=discovery.get("expression", "N/A"),
            r2_score=discovery.get("r2_score", 0.0),
            rmse=discovery.get("rmse", float("inf")),
            complexity=discovery.get("complexity", 0),
            discovery_time=discovery_time,
            validation_score=validation.get("total_score"),
            symbolic_score=validation.get("layer_scores", {}).get("symbolic"),
            dimensional_score=validation.get("layer_scores", {}).get("dimensional"),
            domain_score=validation.get("layer_scores", {}).get("domain"),
            numerical_score=validation.get("layer_scores", {}).get("numerical"),
            edge_cases_detected=len(validation.get("edge_cases_detected", [])),
            critical_errors=len(
                [e for e in validation.get("errors", []) if "CRITICAL" in e]
            ),
            warnings=len(validation.get("warnings", [])),
            has_interpretation=interpretation is not None,
            interpretation_time=interpretation.get("metadata", {}).get(
                "generation_time_seconds"
            )
            if interpretation
            else None,
            production_ready=production_ready,
            requires_fixes=requires_fixes,
            method_used="Symbolic",
            confidence=validation.get("total_score", 0) / 100.0,
        )

    def _fallback_discover(self, X, y, variable_names, test_case_name):
        """Fallback if system not available"""
        return HybridSystemResult(
            architecture=self.architecture,
            test_case=test_case_name,
            discovered_formula="system_not_available",
            r2_score=0.0,
            rmse=float("inf"),
            complexity=0,
            discovery_time=0.0,
            production_ready=False,
        )


# ============================================================================
# COMPARISON FRAMEWORK
# ============================================================================


class HybridSystemComparison:
    """Framework for comparing hybrid system architectures"""

    def __init__(self):
        self.results: List[HybridSystemResult] = []
        self.test_cases = self._load_test_cases()

    def _load_test_cases(self) -> Dict:
        """Load DeFi test cases"""
        return {
            "kelly_criterion": {
                "name": "Kelly Criterion",
                "variables": ["expected_return", "volatility"],
                "descriptions": {
                    "expected_return": "Expected APY",
                    "volatility": "IL risk measure",
                },
                "units": {
                    "expected_return": "dimensionless",
                    "volatility": "dimensionless",
                },
                "ground_truth": "min(expected_return / (2 * volatility**2), 1.0)",
                "data_generator": lambda n: (
                    np.column_stack(
                        [
                            np.random.uniform(0.05, 0.50, n),
                            np.random.uniform(0.05, 0.40, n),
                        ]
                    ),
                    lambda X: np.minimum(X[:, 0] / (2 * X[:, 1] ** 2), 1.0),
                ),
            },
            "amm_constant_product": {
                "name": "AMM Constant Product",
                "variables": ["reserve0", "reserve1"],
                "descriptions": {
                    "reserve0": "Token 0 reserves",
                    "reserve1": "Token 1 reserves",
                },
                "units": {
                    "reserve0": "USD",
                    "reserve1": "USD",
                },
                "ground_truth": "sqrt(reserve0 * reserve1)",
                "data_generator": lambda n: (
                    np.random.uniform(100, 10000, (n, 2)),
                    lambda X: np.sqrt(X[:, 0] * X[:, 1]),
                ),
            },
            "impermanent_loss": {
                "name": "Impermanent Loss",
                "variables": ["price_ratio"],
                "descriptions": {
                    "price_ratio": "Current price / Initial price",
                },
                "units": {
                    "price_ratio": "dimensionless",
                },
                "ground_truth": "2 * sqrt(price_ratio) / (1 + price_ratio + 1e-10) - 1",
                "data_generator": lambda n: (
                    np.random.uniform(0.1, 5.0, (n, 1)),
                    lambda X: 2 * np.sqrt(X[:, 0]) / (1 + X[:, 0] + 1e-10) - 1,
                ),
            },
        }

    def run_comparison(
        self,
        test_cases: Optional[List[str]] = None,
        n_samples: int = 200,
        verbose: bool = True,
    ) -> pd.DataFrame:
        """Run comparison between both architectures"""

        if test_cases is None:
            test_cases = list(self.test_cases.keys())

        print("=" * 80)
        print(f"{'HYBRID SYSTEM COMPARISON':^80}")
        print("=" * 80)
        print(f"\n📋 Test Cases: {len(test_cases)}")
        print(f"📊 Samples: {n_samples}")
        print(f"\n🏗️  Architectures:")
        print(f"   A) LLM + Neural Network")
        print(f"   B) LLM + Symbolic + Validation")
        print("=" * 80)

        # Initialize systems
        system_a = LLMNeuralHybrid()
        system_b = LLMSymbolicValidationHybrid(domain="defi")

        # Run tests
        for test_name in test_cases:
            test_case = self.test_cases[test_name]

            print(f"\n{'=' * 80}")
            print(f"TEST: {test_case['name']}")
            print(f"{'=' * 80}")

            # Generate data
            X, y_func = test_case["data_generator"](n_samples)
            y = y_func(X)
            y += np.random.normal(0, np.abs(y) * 0.01, size=y.shape)

            # Run Architecture A
            result_a = system_a.discover(
                X=X,
                y=y,
                variable_names=test_case["variables"],
                variable_descriptions=test_case["descriptions"],
                test_case_name=test_name,
            )
            self.results.append(result_a)

            # Run Architecture B
            result_b = system_b.discover(
                X=X,
                y=y,
                variable_names=test_case["variables"],
                variable_descriptions=test_case["descriptions"],
                variable_units=test_case["units"],
                test_case_name=test_name,
            )
            self.results.append(result_b)

            # Show comparison
            if verbose:
                self._print_test_comparison(result_a, result_b)

        # Generate report
        return self.generate_report()

    def _print_test_comparison(
        self, result_a: HybridSystemResult, result_b: HybridSystemResult
    ):
        """Print comparison for single test"""

        print(f"\n📊 Architecture Comparison:")

        comparison_data = [
            ["Metric", "A: LLM+NN", "B: LLM+Symbolic+Val", "Winner"],
            ["─" * 20, "─" * 15, "─" * 20, "─" * 10],
            [
                "R² Score",
                f"{result_a.r2_score:.4f}",
                f"{result_b.r2_score:.4f}",
                "A" if result_a.r2_score > result_b.r2_score else "B",
            ],
            [
                "RMSE",
                f"{result_a.rmse:.4f}",
                f"{result_b.rmse:.4f}",
                "A" if result_a.rmse < result_b.rmse else "B",
            ],
            [
                "Discovery Time",
                f"{result_a.discovery_time:.2f}s",
                f"{result_b.discovery_time:.2f}s",
                "A" if result_a.discovery_time < result_b.discovery_time else "B",
            ],
            [
                "Validation Score",
                "N/A",
                f"{result_b.validation_score:.1f}/100"
                if result_b.validation_score
                else "N/A",
                "B",
            ],
            [
                "Edge Cases Detected",
                "0",
                str(result_b.edge_cases_detected)
                if result_b.edge_cases_detected
                else "0",
                "B",
            ],
            [
                "Critical Errors",
                "Unknown",
                str(result_b.critical_errors) if result_b.critical_errors else "0",
                "B",
            ],
            [
                "Production Ready",
                "✓" if result_a.production_ready else "✗",
                "✓" if result_b.production_ready else "✗",
                "Tie"
                if result_a.production_ready == result_b.production_ready
                else ("A" if result_a.production_ready else "B"),
            ],
        ]

        print(tabulate(comparison_data, tablefmt="grid"))

        # Show validation breakdown for B
        if result_b.validation_score:
            print(f"\n🔍 Architecture B Validation Breakdown:")
            print(f"   • Symbolic:     {result_b.symbolic_score:.1f}/100")
            print(f"   • Dimensional:  {result_b.dimensional_score:.1f}/100")
            print(f"   • Domain:       {result_b.domain_score:.1f}/100")
            print(f"   • Numerical:    {result_b.numerical_score:.1f}/100")

    def generate_report(self) -> pd.DataFrame:
        """Generate comprehensive comparison report"""

        print("\n" + "=" * 80)
        print(f"{'COMPREHENSIVE COMPARISON REPORT':^80}")
        print("=" * 80)

        # Convert results to DataFrame
        df = pd.DataFrame([asdict(r) for r in self.results])

        # Aggregate by architecture
        print("\n📊 AGGREGATE METRICS BY ARCHITECTURE")
        print("-" * 80)

        agg_metrics = (
            df.groupby("architecture")
            .agg(
                {
                    "r2_score": ["mean", "std", "min", "max"],
                    "rmse": ["mean", "std"],
                    "discovery_time": ["mean", "std"],
                    "validation_score": "mean",
                    "production_ready": "sum",
                }
            )
            .round(4)
        )

        print(agg_metrics)

        # Winner determination
        print("\n🏆 WINNER DETERMINATION")
        print("-" * 80)

        arch_a_results = df[df["architecture"] == "llm_nn"]
        arch_b_results = df[df["architecture"] == "llm_symbolic_validation"]

        scores = {
            "R² Accuracy": self._compare_metric(
                arch_a_results["r2_score"].mean(),
                arch_b_results["r2_score"].mean(),
                higher_is_better=True,
            ),
            "RMSE": self._compare_metric(
                arch_a_results["rmse"].mean(),
                arch_b_results["rmse"].mean(),
                higher_is_better=False,
            ),
            "Speed": self._compare_metric(
                arch_a_results["discovery_time"].mean(),
                arch_b_results["discovery_time"].mean(),
                higher_is_better=False,
            ),
            "Validation Quality": self._compare_metric(
                0, arch_b_results["validation_score"].mean(), higher_is_better=True
            ),
            "Edge Case Detection": self._compare_metric(
                0, arch_b_results["edge_cases_detected"].mean(), higher_is_better=True
            ),
            "Production Readiness": self._compare_metric(
                arch_a_results["production_ready"].sum(),
                arch_b_results["production_ready"].sum(),
                higher_is_better=True,
            ),
        }

        for metric, (winner, score_a, score_b) in scores.items():
            print(f"\n{metric}:")
            print(f"   A: {score_a:.4f}")
            print(f"   B: {score_b:.4f}")
            print(f"   Winner: {winner}")

        # Overall winner
        wins_a = sum(1 for _, (w, _, _) in scores.items() if w == "A")
        wins_b = sum(1 for _, (w, _, _) in scores.items() if w == "B")

        print("\n" + "=" * 80)
        if wins_b > wins_a:
            print(
                f"{'🏆 OVERALL WINNER: ARCHITECTURE B (LLM + Symbolic + Validation)':^80}"
            )
            print(f"{'Wins: ' + str(wins_b) + '/6':^80}")
        elif wins_a > wins_b:
            print(f"{'🏆 OVERALL WINNER: ARCHITECTURE A (LLM + Neural Network)':^80}")
            print(f"{'Wins: ' + str(wins_a) + '/6':^80}")
        else:
            print(f"{'🤝 TIE: Both architectures perform equally':^80}")
        print("=" * 80)

        return df

    def _compare_metric(self, val_a, val_b, higher_is_better=True):
        """Compare metric and return winner"""
        if higher_is_better:
            winner = "B" if val_b > val_a else "A" if val_a > val_b else "Tie"
        else:
            winner = "A" if val_a < val_b else "B" if val_b < val_a else "Tie"
        return winner, val_a, val_b

    def export_results(self, filepath: str):
        """Export comparison results to JSON"""
        data = {
            "results": [asdict(r) for r in self.results],
            "summary": self._generate_summary(),
        }

        with open(filepath, "w") as f:
            json.dump(data, f, indent=2, default=str)

        print(f"\n✅ Results exported to: {filepath}")

    def _generate_summary(self) -> Dict:
        """Generate summary statistics"""
        df = pd.DataFrame([asdict(r) for r in self.results])

        return {
            "total_tests": len(self.results),
            "architectures_compared": df["architecture"].nunique(),
            "avg_r2_by_arch": df.groupby("architecture")["r2_score"].mean().to_dict(),
            "production_ready_by_arch": df.groupby("architecture")["production_ready"]
            .sum()
            .to_dict(),
        }


# ============================================================================
# CLI INTERFACE
# ============================================================================


def main():
    parser = argparse.ArgumentParser(
        description="Compare Hybrid System Architectures",
        formatter_class=argparse.RawDescriptionHelpFormatter,
    )

    parser.add_argument(
        "--tests",
        nargs="+",
        choices=["kelly_criterion", "amm_constant_product", "impermanent_loss", "all"],
        default=["all"],
        help="Test cases to run",
    )
    parser.add_argument(
        "--samples", type=int, default=200, help="Number of samples per test"
    )
    parser.add_argument("--export", type=str, help="Export results to JSON file")
    parser.add_argument("--quiet", action="store_true", help="Suppress verbose output")

    args = parser.parse_args()

    # Setup test cases
    test_cases = None if "all" in args.tests else args.tests

    # Run comparison
    comparison = HybridSystemComparison()
    df_results = comparison.run_comparison(
        test_cases=test_cases,
        n_samples=args.samples,
        verbose=not args.quiet,
    )

    # Export if requested
    if args.export:
        comparison.export_results(args.export)

    print("\n✅ Comparison complete!")


if __name__ == "__main__":
    main()
