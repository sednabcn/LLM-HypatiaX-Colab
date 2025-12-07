"""
HypatiaX Hybrid Discovery System with Validation
Combines symbolic regression, validation, and LLM interpretation
"""

import json
from collections import deque
from datetime import datetime
from typing import Dict, List, Optional

import numpy as np

from hypatiax.tools.llm_providers.llm_interpreter import InterpretationConfig, LLMInterpreter
from hypatiax.tools.symbolic.symbolic_engine import DiscoveryConfig, SymbolicEngine
from hypatiax.tools.validation.ensemble_validator import EnsembleValidator


class HybridDiscoverySystem:
    """
    Integrated system for discovering, validating, and interpreting mathematical formulas.

    Workflow:
    1. Discover symbolic expression from data (SymbolicEngine)
    2. Validate expression across multiple layers (EnsembleValidator)
    3. Interpret meaning using LLM (LLMInterpreter)
    """

    def __init__(
        self,
        domain: str = "defi",
        discovery_config: Optional[DiscoveryConfig] = None,
        interpretation_config: Optional[InterpretationConfig] = None,
        max_results: Optional[int] = 100,
        validation_weights: Optional[Dict[str, float]] = None,
        use_rich_output: bool = True,
    ):
        """
        Initialize the hybrid discovery system.

        Args:
            domain: Domain context ('defi', 'risk', 'finance', 'esg')
            discovery_config: Configuration for symbolic regression
            interpretation_config: Configuration for LLM interpretation
            max_results: Maximum number of results to keep in memory
            validation_weights: Custom weights for validation layers
            use_rich_output: Enable rich formatted output
        """
        self.domain = domain

        # Initialize components
        self.symbolic_engine = SymbolicEngine(discovery_config or DiscoveryConfig())
        self.llm_interpreter = LLMInterpreter(interpretation_config or InterpretationConfig())
        self.validator = EnsembleValidator(domain=domain, max_history=max_results, weights=validation_weights)

        # Bounded results storage
        self.max_results = max_results
        if max_results is not None:
            self.results = deque(maxlen=max_results)
        else:
            self.results = []

        # Add formatter
        self.use_rich_output = use_rich_output
        if use_rich_output:
            try:
                from hypatiax.tools.formatters.hybrid_formatter import HybridFormatter

                self.formatter = HybridFormatter()
            except ImportError:
                print("⚠ Warning: 'rich' not installed. Install with: pip install rich")
                self.formatter = None
        else:
            self.formatter = None

    def discover_validate_interpret(
        self,
        X: np.ndarray,
        y: np.ndarray,
        variable_names: List[str],
        variable_descriptions: Dict[str, str],
        variable_units: Dict[str, str],
        description: Optional[str] = None,
        validate_first: bool = True,
        show_formatted: bool = True,
    ) -> Dict:
        """
        Complete discovery workflow with validation and interpretation.

        Args:
            X: Input features (n_samples, n_features)
            y: Target values (n_samples,)
            variable_names: Names of variables
            variable_descriptions: Descriptions of what each variable represents
            variable_units: Unit strings for each variable
            description: Optional description of this discovery run
            validate_first: If True, skip interpretation if validation fails
            show_formatted: If True, display formatted output (requires rich)

        Returns:
            Complete result dictionary with discovery, validation, and interpretation
        """
        print(f"\n{'='*70}")
        print(f"WORKFLOW: {description or 'Unnamed Discovery'}")
        print(f"Domain: {self.domain.upper()}")
        print(f"{'='*70}")

        # STAGE 1: DISCOVER
        print(f"\n[1/3] 🔍 Discovering symbolic expression from {len(X)} samples...")
        discovery_result = self.symbolic_engine.discover(X, y, variable_names)

        print(f"✓ Found: {discovery_result['expression']}")
        print(f"  R² Score: {discovery_result['r2_score']:.4f}")
        print(f"  Complexity: {discovery_result['complexity']}")

        # STAGE 2: VALIDATE
        print(f"\n[2/3] ✓ Validating expression across {len(self.validator.weights)} layers...")

        # Prepare test data from input features
        test_data = {name: X[:, i] for i, name in enumerate(variable_names)}

        validation_result = self.validator.validate_complete(
            expression_str=discovery_result["expression"],
            variable_definitions=variable_descriptions,
            variable_units=variable_units,
            test_data=test_data,
        )

        # Display validation results
        valid_symbol = "✓" if validation_result["valid"] else "✗"
        print(f"{valid_symbol} Overall Score: {validation_result['total_score']:.1f}/100")
        print(f"  Layer Scores:")
        for layer, score in validation_result["layer_scores"].items():
            layer_symbol = "✓" if score >= 70 else "⚠" if score >= 50 else "✗"
            print(f"    {layer_symbol} {layer.capitalize()}: {score:.1f}")

        # Show errors if any
        if validation_result["errors"]:
            print(f"\n  ⚠ Errors ({len(validation_result['errors'])}):")
            for error in validation_result["errors"][:3]:
                print(f"    - {error}")
            if len(validation_result["errors"]) > 3:
                print(f"    ... and {len(validation_result['errors']) - 3} more")

        # Show warnings if any
        if validation_result["warnings"]:
            print(f"\n  ℹ Warnings ({len(validation_result['warnings'])}):")
            for warning in validation_result["warnings"][:3]:
                print(f"    - {warning}")
            if len(validation_result["warnings"]) > 3:
                print(f"    ... and {len(validation_result['warnings']) - 3} more")

        # STAGE 3: INTERPRET
        interpretation = None

        if validation_result["valid"] or not validate_first:
            print(f"\n[3/3] 🤖 Interpreting with LLM...")
            try:
                interpretation = self.llm_interpreter.interpret(
                    expression=discovery_result["expression"],
                    domain=self.domain,
                    variables=variable_descriptions,
                    r2=discovery_result["r2_score"],
                )
                print(f"✓ Interpretation complete")

                # Show interpretation summary if available
                if isinstance(interpretation, dict) and "interpretation" in interpretation:
                    interp_text = interpretation["interpretation"]
                    if len(interp_text) > 150:
                        print(f"  Summary: {interp_text[:150]}...")
                    else:
                        print(f"  Summary: {interp_text}")

            except Exception as e:
                print(f"✗ Interpretation failed: {str(e)}")
                interpretation = {"error": str(e)}
        else:
            print(f"\n[3/3] ⊗ Interpretation skipped (validation failed)")
            print(f"  Recommendations:")
            for rec in validation_result["recommendations"][:3]:
                print(f"    • {rec}")

        # Compile complete result
        complete_result = {
            "timestamp": datetime.now().isoformat(),
            "description": description,
            "domain": self.domain,
            "discovery": discovery_result,
            "validation": validation_result,
            "interpretation": interpretation,
            "metadata": {"n_samples": len(X), "n_features": X.shape[1], "variable_names": variable_names},
        }

        # Store result
        self.results.append(complete_result)

        print(f"\n{'='*70}")
        print(f"Workflow complete. Result stored ({len(self.results)}/{self.max_results or '∞'})")
        print(f"{'='*70}\n")

        # Display formatted output if requested
        if show_formatted and self.formatter:
            print("\n")
            self.formatter.format_result(complete_result)

        return complete_result

    def display_result(self, result: Dict, format: str = "rich"):
        """
        Display a result in various formats.

        Args:
            result: Result dictionary
            format: Display format ('rich', 'json', 'summary')
        """
        if format == "rich" and self.formatter:
            self.formatter.format_result(result)
        elif format == "summary" and self.formatter:
            self.formatter.format_result(result, show_full=False)
        elif format == "json":
            print(json.dumps(result, indent=2, ensure_ascii=False))
        else:
            # Fallback to basic print
            print(f"Expression: {result.get('discovery', {}).get('expression')}")
            print(f"R²: {result.get('discovery', {}).get('r2_score'):.4f}")
            print(f"Validation: {result.get('validation', {}).get('total_score'):.1f}/100")

    def compare_all_results(self, top_n: int = 10):
        """Display comparison table of all stored results."""
        if self.formatter:
            self.formatter.compare_results(list(self.results), top_n)
        else:
            print(f"Stored {len(self.results)} results")
            for i, result in enumerate(list(self.results)[-top_n:], 1):
                expr = result.get("discovery", {}).get("expression", "N/A")
                r2 = result.get("discovery", {}).get("r2_score", 0)
                print(f"{i}. {expr[:50]}... | R²={r2:.4f}")

    def export_formatted(self, result: Dict, filepath: str, format: str = "html"):
        """
        Export result with formatting.

        Args:
            result: Result dictionary
            filepath: Output file path
            format: Export format ('html', 'markdown', 'json')
        """
        if self.formatter and format in ["html", "markdown"]:
            if format == "html":
                self.formatter.export_html(result, filepath)
            else:
                self.formatter.export_markdown(result, filepath)
        elif format == "json":
            self._export_json_single(result, filepath)
        else:
            raise ValueError(f"Unsupported format: {format}")

    def _export_json_single(self, result: Dict, filepath: str):
        """Export single result to JSON."""
        serializable = self._make_serializable(result)
        with open(filepath, "w", encoding="utf-8") as f:
            json.dump(serializable, f, indent=2, ensure_ascii=False)
        print(f"✓ Exported to {filepath}")

    def clear_results(self):
        """Clear all stored results."""
        if isinstance(self.results, deque):
            self.results.clear()
        else:
            self.results = []
        print("✓ Results cleared")

    def get_results(self, limit: Optional[int] = None) -> List[Dict]:
        """Get stored results."""
        results_list = list(self.results)
        if limit is not None:
            return results_list[-limit:]
        return results_list

    def get_best_result(self, metric: str = "r2_score", require_valid: bool = True) -> Optional[Dict]:
        """Get the best result based on a metric."""
        if not self.results:
            return None

        candidates = list(self.results)
        if require_valid:
            candidates = [r for r in candidates if "validation" in r and r["validation"].get("valid", False)]

        if not candidates:
            return None

        if metric == "r2_score":
            return max(candidates, key=lambda x: x["discovery"].get("r2_score", float("-inf")))
        elif metric == "validation_score":
            return max(candidates, key=lambda x: x.get("validation", {}).get("total_score", float("-inf")))
        elif metric == "complexity":
            return min(candidates, key=lambda x: x["discovery"].get("complexity", float("inf")))
        else:
            return max(candidates, key=lambda x: x.get(metric, float("-inf")))

    def export_results(self, filepath: str, format: str = "json"):
        """Export results to a file."""
        if format.lower() == "json":
            self._export_json(filepath)
        elif format.lower() == "csv":
            self._export_csv(filepath)
        else:
            raise ValueError(f"Unsupported format: {format}")

    def _export_json(self, filepath: str):
        """Export results to JSON file."""
        results_list = []
        for result in self.results:
            serializable_result = self._make_serializable(result)
            results_list.append(serializable_result)

        with open(filepath, "w") as f:
            json.dump(results_list, f, indent=2, default=str)

        print(f"✓ Exported {len(results_list)} results to {filepath}")

    def _export_csv(self, filepath: str):
        """Export summary results to CSV file."""
        import csv

        with open(filepath, "w", newline="") as f:
            writer = csv.writer(f)
            writer.writerow(
                [
                    "Timestamp",
                    "Description",
                    "Domain",
                    "Expression",
                    "R2_Score",
                    "Validation_Score",
                    "Valid",
                    "Complexity",
                ]
            )

            for result in self.results:
                writer.writerow(
                    [
                        result.get("timestamp", ""),
                        result.get("description", ""),
                        result.get("domain", ""),
                        result.get("discovery", {}).get("expression", ""),
                        result.get("discovery", {}).get("r2_score", ""),
                        result.get("validation", {}).get("total_score", ""),
                        result.get("validation", {}).get("valid", ""),
                        result.get("discovery", {}).get("complexity", ""),
                    ]
                )

        print(f"✓ Exported {len(self.results)} results to {filepath}")

    def _make_serializable(self, obj):
        """Convert objects to JSON-serializable format."""
        if isinstance(obj, dict):
            return {k: self._make_serializable(v) for k, v in obj.items()}
        elif isinstance(obj, list):
            return [self._make_serializable(v) for v in obj]
        elif isinstance(obj, np.ndarray):
            return obj.tolist()
        elif hasattr(obj, "__dict__"):
            return str(obj)
        else:
            return obj

    def get_statistics(self) -> Dict:
        """Get statistics about discovery runs."""
        if not self.results:
            return {"total_runs": 0, "valid_count": 0, "average_r2": 0.0, "average_validation_score": 0.0}

        total = len(self.results)
        valid_count = sum(1 for r in self.results if "validation" in r and r["validation"].get("valid", False))

        r2_scores = [r["discovery"]["r2_score"] for r in self.results if "discovery" in r]
        avg_r2 = sum(r2_scores) / len(r2_scores) if r2_scores else 0.0

        val_scores = [r["validation"]["total_score"] for r in self.results if "validation" in r]
        avg_val = sum(val_scores) / len(val_scores) if val_scores else 0.0

        return {
            "total_runs": total,
            "valid_count": valid_count,
            "invalid_count": total - valid_count,
            "success_rate": valid_count / total if total > 0 else 0.0,
            "average_r2": avg_r2,
            "average_validation_score": avg_val,
            "domain": self.domain,
        }


if __name__ == "__main__":
    # Initialize with rich formatting (will gracefully degrade if not available)
    system = HybridDiscoverySystem(domain="defi", max_results=50, use_rich_output=True)

    # Generate sample data
    np.random.seed(42)
    X = np.random.uniform(10, 1000, (100, 2))
    y = np.sqrt(X[:, 0] * X[:, 1]) + np.random.normal(0, 5, 100)

    # Run discovery (automatically shows formatted output if available)
    result = system.discover_validate_interpret(
        X=X,
        y=y,
        variable_names=["reserve0", "reserve1"],
        variable_descriptions={"reserve0": "Token 0 reserves in pool", "reserve1": "Token 1 reserves in pool"},
        variable_units={"reserve0": "dimensionless", "reserve1": "dimensionless"},
        description="AMM Constant Product Formula Discovery",
        show_formatted=True,
    )

    # Get statistics
    stats = system.get_statistics()
    print(f"\nSystem Statistics:")
    print(f"  Total runs: {stats['total_runs']}")
    print(f"  Success rate: {stats['success_rate']:.1%}")
    print(f"  Average R²: {stats['average_r2']:.4f}")
    print(f"  Average validation score: {stats['average_validation_score']:.1f}")

    # Export results
    system.export_results("discovery_results.json", format="json")
    system.export_results("discovery_results.csv", format="csv")
