"""
HypatiaX Ensemble Validator (RECALIBRATED - Week 2, Day 3)
tools/validation/ensemble_validator.py

Combines multiple validators for comprehensive validation.

CRITICAL UPDATES:
- Recalibrated scoring thresholds (94.0 → 85.0 alignment)
- Rebalanced validation layer weights for better dimensional coverage
- Enhanced penalty system with graduated severity levels
- Improved edge case detection and handling
- Documented clear acceptance criteria with justification
"""

from collections import deque
from typing import Dict, List, Optional

import numpy as np

from hypatiax.tools.validation.dimensional_validator import DimensionalValidator
from hypatiax.tools.validation.domain_validator import DomainValidator
from hypatiax.tools.validation.symbolic_validator import SymbolicValidator


class EnsembleValidator:
    """
    Ensemble validator that combines multiple validation layers:
    1. Symbolic validation (mathematical correctness)
    2. Dimensional validation (unit consistency)
    3. Domain validation (domain-specific rules)
    4. Numerical validation (stability with test data)

    ACCEPTANCE CRITERIA (Recalibrated Week 2, Day 3):
    - Overall score >= 85.0 (recalibrated from 94.0)
    - All critical validators must pass (symbolic, dimensional)
    - Domain-specific rules must be satisfied
    - No critical edge cases (division by zero, overflow, NaN)

    SCORING PHILOSOPHY:
    - 85.0 threshold represents "production ready" quality
    - Balances strictness with practical usability
    - Allows minor warnings while blocking critical issues
    """

    # RECALIBRATED: Clear threshold documentation with justification
    VALIDATION_THRESHOLDS = {
        "minimum_total_score": 85.0,  # Production-ready threshold (was 94.0)
        "minimum_layer_score": 65.0,  # Individual layer minimum (lowered from 70.0)
        "critical_failure_threshold": 40.0,  # Below this = automatic failure (was 50.0)
        "edge_case_penalty_critical": 20.0,  # CRITICAL edge cases (increased from 15.0)
        "edge_case_penalty_major": 12.0,  # MAJOR issues (new tier)
        "edge_case_penalty_warning": 5.0,  # WARNING level (existing)
        "dimensional_inconsistency_penalty": 25.0,  # Increased from 20.0
        "domain_constraint_penalty": 15.0,  # Domain violations (increased from 10.0)
    }

    def __init__(
        self,
        domain: str = "defi",
        max_history: Optional[int] = 1000,
        weights: Optional[Dict[str, float]] = None,
        strict_mode: bool = False,
    ):
        """
        Initialize the ensemble validator.

        Args:
            domain: Domain context ('defi', 'risk', 'finance', 'esg')
            max_history: Maximum number of validation results to keep
            weights: Custom weights for each validation layer
            strict_mode: If True, apply stricter validation criteria
        """
        self.domain = domain
        self.strict_mode = strict_mode

        # Initialize validators
        self.symbolic_validator = SymbolicValidator(max_history=max_history)
        self.dimensional_validator = DimensionalValidator(max_history=max_history)
        self.domain_validator = DomainValidator(domain, max_history=max_history)

        # RECALIBRATED: Optimized validation weights for dimensional coverage
        # Key changes:
        # - Increased dimensional weight (0.25 → 0.35) - dimensional issues are critical
        # - Balanced symbolic weight (0.35 → 0.30) - still important but not dominant
        # - Maintained domain weight (0.30) - domain rules remain critical
        # - Reduced numerical weight (0.10 → 0.05) - supplementary check only
        self.weights = weights or {
            "symbolic": 0.30,  # Mathematical correctness (was 0.35)
            "dimensional": 0.35,  # Unit consistency - INCREASED (was 0.25, then 0.30)
            "domain": 0.30,  # Domain-specific rules (maintained)
            "numerical": 0.05,  # Numerical stability - DECREASED (was 0.10)
        }

        # Validate weights
        weight_sum = sum(self.weights.values())
        if not np.isclose(weight_sum, 1.0):
            raise ValueError(f"Weights must sum to 1.0, got {weight_sum}")

        # Bounded validation history
        if max_history is not None:
            self.validation_history = deque(maxlen=max_history)
        else:
            self.validation_history = []

    def validate_complete(
        self,
        expression_str: str,
        variable_definitions: Dict[str, str],
        variable_units: Dict[str, str],
        test_data: Optional[Dict[str, np.ndarray]] = None,
        from_latex: bool = False,
    ) -> Dict:
        """
        Perform comprehensive validation across all layers.

        RECALIBRATED: Applies new threshold (85.0) with enhanced penalty system.

        Args:
            expression_str: The mathematical expression
            variable_definitions: Variable name to description mapping
            variable_units: Variable name to unit string mapping
            test_data: Optional test data for numerical validation
            from_latex: Whether expression is in LaTeX format

        Returns:
            {
                'valid': bool,
                'total_score': float (0-100, >= 85.0 to pass),
                'base_score': float (score before penalties),
                'layer_scores': Dict[str, float],
                'layer_results': Dict[str, Dict],
                'errors': List[str],
                'warnings': List[str],
                'recommendations': List[str],
                'edge_cases_detected': List[str],
                'acceptance_criteria': Dict,
                'penalties_applied': Dict
            }
        """
        # 1. Symbolic validation
        symbolic_result = self.symbolic_validator.validate(
            expression=expression_str,
            variable_definitions=variable_definitions,
            domain=self.domain,
            from_latex=from_latex,
        )

        # 2. Dimensional validation
        dimensional_result = self.dimensional_validator.validate(
            expression_str=expression_str, variable_units=variable_units
        )

        # 3. Domain validation
        domain_result = self.domain_validator.validate(
            expression_str=expression_str, variable_definitions=variable_definitions, test_data=test_data
        )

        # 4. Numerical validation (if test data provided)
        numerical_result = (
            self._numerical_validation(expression_str, test_data, symbolic_result.get("sympy_expr"))
            if test_data
            else {"score": 100.0, "errors": [], "warnings": []}
        )

        # ENHANCED: Comprehensive edge case detection
        edge_cases = self._detect_edge_cases(symbolic_result, dimensional_result, domain_result, numerical_result)

        # Calculate base weighted score
        base_score = (
            self.weights["symbolic"] * symbolic_result["score"]
            + self.weights["dimensional"] * dimensional_result["score"]
            + self.weights["domain"] * domain_result["score"]
            + self.weights["numerical"] * numerical_result["score"]
        )

        # RECALIBRATED: Apply graduated penalty system
        total_score, penalties_applied = self._apply_penalties(
            base_score, edge_cases, dimensional_result, domain_result
        )

        # Aggregate all errors and warnings
        all_errors = (
            symbolic_result.get("errors", [])
            + dimensional_result.get("errors", [])
            + domain_result.get("errors", [])
            + numerical_result.get("errors", [])
        )

        all_warnings = (
            symbolic_result.get("warnings", [])
            + dimensional_result.get("warnings", [])
            + domain_result.get("warnings", [])
            + numerical_result.get("warnings", [])
        )

        # RECALIBRATED: Determine overall validity with new criteria
        overall_valid = self._check_acceptance_criteria(
            total_score, symbolic_result, dimensional_result, domain_result, edge_cases
        )

        # Generate recommendations
        recommendations = self._generate_recommendations(
            symbolic_result, dimensional_result, domain_result, numerical_result, edge_cases, total_score
        )

        # ENHANCED: Document acceptance criteria evaluation
        acceptance_criteria = {
            "minimum_score_met": total_score >= self.VALIDATION_THRESHOLDS["minimum_total_score"],
            "symbolic_valid": symbolic_result["valid"],
            "dimensional_valid": dimensional_result["valid"],
            "domain_valid": domain_result["valid"],
            "no_critical_edge_cases": len([e for e in edge_cases if "CRITICAL" in e]) == 0,
            "no_major_edge_cases": len([e for e in edge_cases if "MAJOR" in e]) == 0,
            "threshold_used": self.VALIDATION_THRESHOLDS["minimum_total_score"],
            "all_layers_above_minimum": all(
                score >= self.VALIDATION_THRESHOLDS["minimum_layer_score"]
                for score in [
                    symbolic_result["score"],
                    dimensional_result["score"],
                    domain_result["score"],
                    numerical_result["score"],
                ]
            ),
        }

        # Compile complete result
        complete_result = {
            "valid": overall_valid,
            "total_score": total_score,
            "base_score": base_score,
            "penalties_applied": penalties_applied,
            "layer_scores": {
                "symbolic": symbolic_result["score"],
                "dimensional": dimensional_result["score"],
                "domain": domain_result["score"],
                "numerical": numerical_result["score"],
            },
            "layer_results": {
                "symbolic": symbolic_result,
                "dimensional": dimensional_result,
                "domain": domain_result,
                "numerical": numerical_result,
            },
            "errors": all_errors,
            "warnings": all_warnings,
            "recommendations": recommendations,
            "edge_cases_detected": edge_cases,
            "acceptance_criteria": acceptance_criteria,
            "expression": expression_str,
            "canonical_form": symbolic_result.get("canonical_form"),
            "domain": self.domain,
            "strict_mode": self.strict_mode,
            "weights_used": self.weights,
        }

        # Store in history
        self.validation_history.append(complete_result)

        return complete_result

    def _detect_edge_cases(self, symbolic: Dict, dimensional: Dict, domain: Dict, numerical: Dict) -> List[str]:
        """
        ENHANCED: Comprehensive edge case detection with severity classification.

        Severity Levels:
        - CRITICAL: Fatal issues (div/0, empty expr, NaN/Inf)
        - MAJOR: Serious issues (dimensional mismatch, constraint violations)
        - WARNING: Potential issues (overflow risk, numerical instability)

        Detects:
        - Division by zero risks
        - Numerical overflow/underflow
        - Empty expressions
        - Invalid mathematical operations
        - Dimensional inconsistencies
        - Domain constraint violations
        """
        edge_cases = []

        # CRITICAL: Symbolic issues
        symbolic_errors = str(symbolic.get("errors", [])).lower()

        if "division by zero" in symbolic_errors or "divide by zero" in symbolic_errors:
            edge_cases.append("CRITICAL: Division by zero detected")

        if "empty" in symbolic_errors or "blank" in symbolic_errors:
            edge_cases.append("CRITICAL: Empty or blank expression")

        if "undefined" in symbolic_errors:
            edge_cases.append("CRITICAL: Undefined mathematical operation")

        # CRITICAL: Numerical issues
        numerical_errors = str(numerical.get("errors", [])).lower()

        if "nan" in numerical_errors:
            edge_cases.append("CRITICAL: Expression produces NaN values")

        if "inf" in numerical_errors or "infinite" in numerical_errors:
            edge_cases.append("CRITICAL: Expression produces infinite values")

        # MAJOR: Dimensional inconsistencies (upgraded severity)
        if dimensional.get("errors"):
            for error in dimensional.get("errors", []):
                error_lower = error.lower()
                if "inconsistent" in error_lower or "mismatch" in error_lower:
                    edge_cases.append(f"MAJOR: Dimensional inconsistency - {error}")
                elif "invalid" in error_lower or "incompatible" in error_lower:
                    edge_cases.append(f"MAJOR: Dimensional incompatibility - {error}")

        # MAJOR: Domain constraint violations
        if domain.get("errors"):
            for error in domain.get("errors", []):
                if "constraint violation" in error.lower():
                    edge_cases.append(f"MAJOR: Domain constraint violation - {error}")
                elif "invalid range" in error.lower():
                    edge_cases.append(f"MAJOR: Invalid value range - {error}")

        # WARNING: Numerical stability issues
        numerical_warnings = str(numerical.get("warnings", [])).lower()

        if "overflow" in numerical_warnings:
            edge_cases.append("WARNING: Potential numerical overflow detected")

        if "underflow" in numerical_warnings:
            edge_cases.append("WARNING: Potential numerical underflow detected")

        if "very large" in numerical_warnings:
            edge_cases.append("WARNING: Very large output values may cause instability")

        if "very small" in numerical_warnings:
            edge_cases.append("WARNING: Very small output values may cause precision loss")

        # WARNING: Dimensional warnings
        if dimensional.get("warnings"):
            for warning in dimensional.get("warnings")[:2]:  # Limit to first 2
                edge_cases.append(f"WARNING: Dimensional - {warning}")

        return edge_cases

    def _apply_penalties(
        self, base_score: float, edge_cases: List[str], dimensional_result: Dict, domain_result: Dict
    ) -> tuple[float, Dict]:
        """
        RECALIBRATED: Apply graduated penalty system with tracking.

        Penalty Structure (Updated):
        - CRITICAL edge cases: -20 points each (increased from 15)
        - MAJOR edge cases: -12 points each (new tier)
        - WARNING edge cases: -5 points each
        - Dimensional errors: -25 points each (increased from 20)
        - Domain violations: -15 points each (increased from 10)

        Returns:
            (final_score, penalties_dict)
        """
        score = base_score
        penalties = {"critical_count": 0, "major_count": 0, "warning_count": 0, "total_deducted": 0.0, "breakdown": []}

        # Apply edge case penalties
        for edge_case in edge_cases:
            deduction = 0.0

            if "CRITICAL" in edge_case:
                deduction = self.VALIDATION_THRESHOLDS["edge_case_penalty_critical"]
                penalties["critical_count"] += 1
                penalties["breakdown"].append(f"Critical edge case: -{deduction}")

            elif "MAJOR" in edge_case:
                deduction = self.VALIDATION_THRESHOLDS["edge_case_penalty_major"]
                penalties["major_count"] += 1
                penalties["breakdown"].append(f"Major issue: -{deduction}")

            elif "WARNING" in edge_case:
                deduction = self.VALIDATION_THRESHOLDS["edge_case_penalty_warning"]
                penalties["warning_count"] += 1
                penalties["breakdown"].append(f"Warning: -{deduction}")

            score -= deduction
            penalties["total_deducted"] += deduction

        # Additional penalty for dimensional errors (beyond edge cases)
        if not dimensional_result.get("valid", True) and dimensional_result.get("errors"):
            # Count errors not already captured in edge cases
            uncaptured_errors = len(
                [e for e in dimensional_result.get("errors", []) if not any(str(e) in ec for ec in edge_cases)]
            )
            if uncaptured_errors > 0:
                deduction = self.VALIDATION_THRESHOLDS["dimensional_inconsistency_penalty"]
                score -= deduction
                penalties["total_deducted"] += deduction
                penalties["breakdown"].append(f"Dimensional errors: -{deduction}")

        # Additional penalty for domain violations (beyond edge cases)
        if not domain_result.get("valid", True) and domain_result.get("errors"):
            uncaptured_errors = len(
                [e for e in domain_result.get("errors", []) if not any(str(e) in ec for ec in edge_cases)]
            )
            if uncaptured_errors > 0:
                deduction = self.VALIDATION_THRESHOLDS["domain_constraint_penalty"]
                score -= deduction
                penalties["total_deducted"] += deduction
                penalties["breakdown"].append(f"Domain violations: -{deduction}")

        # Ensure score doesn't go below 0
        final_score = max(0.0, score)

        return final_score, penalties

    def _check_acceptance_criteria(
        self, total_score: float, symbolic: Dict, dimensional: Dict, domain: Dict, edge_cases: List[str]
    ) -> bool:
        """
        RECALIBRATED: Check if expression meets acceptance criteria.

        Requirements (all must be met):
        1. Total score >= 85.0 (recalibrated threshold)
        2. Symbolic validation must pass
        3. Dimensional validation must pass
        4. No critical edge cases allowed
        5. No major edge cases allowed (new requirement)
        6. All layers >= 65.0 minimum score
        7. In strict mode: domain validation must also pass
        """
        # Check minimum score threshold
        if total_score < self.VALIDATION_THRESHOLDS["minimum_total_score"]:
            return False

        # Critical validators must pass
        if not symbolic["valid"] or not dimensional["valid"]:
            return False

        # No critical edge cases allowed
        critical_edge_cases = [e for e in edge_cases if "CRITICAL" in e]
        if critical_edge_cases:
            return False

        # UPDATED: No major edge cases allowed either
        major_edge_cases = [e for e in edge_cases if "MAJOR" in e]
        if major_edge_cases:
            return False

        # Check minimum layer scores
        if symbolic["score"] < self.VALIDATION_THRESHOLDS["minimum_layer_score"]:
            return False
        if dimensional["score"] < self.VALIDATION_THRESHOLDS["minimum_layer_score"]:
            return False
        if domain["score"] < self.VALIDATION_THRESHOLDS["minimum_layer_score"]:
            return False

        # In strict mode, domain validation must also pass
        if self.strict_mode and not domain["valid"]:
            return False

        # Check for critical failure in any layer
        for score in [symbolic["score"], dimensional["score"], domain["score"]]:
            if score < self.VALIDATION_THRESHOLDS["critical_failure_threshold"]:
                return False

        return True

    def _numerical_validation(self, expression_str: str, test_data: Dict[str, np.ndarray], sympy_expr) -> Dict:
        """
        Validate numerical stability using test data.

        Checks:
        - No NaN or Inf in outputs
        - Reasonable output ranges
        - Numerical stability across test cases
        """
        result = {"score": 100.0, "errors": [], "warnings": []}

        if not test_data or sympy_expr is None:
            return result

        try:
            import sympy as sp

            # Convert test data to evaluation
            free_vars = list(sympy_expr.free_symbols)

            # Check if we have all required variables
            missing_vars = [str(v) for v in free_vars if str(v) not in test_data]
            if missing_vars:
                result["warnings"].append(f"Missing test data for variables: {missing_vars}")
                result["score"] -= 10
                return result

            # Evaluate expression with test data
            n_samples = len(next(iter(test_data.values())))
            outputs = []

            for i in range(n_samples):
                substitutions = {str(var): float(test_data[str(var)][i]) for var in free_vars if str(var) in test_data}

                try:
                    value = float(sympy_expr.subs(substitutions))
                    outputs.append(value)
                except Exception as e:
                    result["errors"].append(f"Evaluation error at sample {i}: {str(e)}")
                    result["score"] -= 10

            if outputs:
                outputs = np.array(outputs)

                # Check for NaN
                nan_count = np.sum(np.isnan(outputs))
                if nan_count > 0:
                    result["errors"].append(f"Expression produces NaN values " f"({nan_count}/{len(outputs)} samples)")
                    result["score"] -= 30

                # Check for Inf
                inf_count = np.sum(np.isinf(outputs))
                if inf_count > 0:
                    result["errors"].append(
                        f"Expression produces infinite values " f"({inf_count}/{len(outputs)} samples)"
                    )
                    result["score"] -= 30

                # Check for extreme values (potential overflow)
                valid_outputs = outputs[np.isfinite(outputs)]
                if len(valid_outputs) > 0:
                    max_abs = np.max(np.abs(valid_outputs))
                    if max_abs > 1e10:
                        result["warnings"].append(f"Very large output values detected (max: {max_abs:.2e})")
                        result["score"] -= 10

                    # Check for very small values (potential underflow)
                    nonzero_valid = valid_outputs[valid_outputs != 0]
                    if len(nonzero_valid) > 0:
                        min_abs = np.min(np.abs(nonzero_valid))
                        if min_abs < 1e-10:
                            result["warnings"].append(f"Very small output values detected (min: {min_abs:.2e})")
                            result["score"] -= 5

        except Exception as e:
            result["warnings"].append(f"Numerical validation error: {str(e)}")
            result["score"] -= 15

        return result

    def _generate_recommendations(
        self,
        symbolic: Dict,
        dimensional: Dict,
        domain: Dict,
        numerical: Dict,
        edge_cases: List[str],
        total_score: float,
    ) -> List[str]:
        """
        ENHANCED: Generate actionable recommendations with priority ordering.
        """
        recommendations = []

        # Calculate score gap
        score_gap = self.VALIDATION_THRESHOLDS["minimum_total_score"] - total_score

        # Priority 1: Critical edge cases (blocking issues)
        critical_cases = [e for e in edge_cases if "CRITICAL" in e]
        if critical_cases:
            recommendations.append(f"🔴 FIX CRITICAL ({len(critical_cases)}): Blocking issues that prevent validation")
            for case in critical_cases[:3]:  # Show first 3
                recommendations.append(f"   • {case.replace('CRITICAL: ', '')}")
            if len(critical_cases) > 3:
                recommendations.append(f"   • ... and {len(critical_cases) - 3} more critical issue(s)")

        # Priority 2: Major edge cases (serious issues)
        major_cases = [e for e in edge_cases if "MAJOR" in e]
        if major_cases:
            recommendations.append(f"🟠 FIX MAJOR ({len(major_cases)}): Serious issues requiring attention")
            for case in major_cases[:2]:  # Show first 2
                recommendations.append(f"   • {case.replace('MAJOR: ', '')}")

        # Priority 3: Symbolic validation
        if not symbolic["valid"]:
            recommendations.append("🔴 FIX: Resolve symbolic/mathematical errors (required for validation)")
        elif symbolic["score"] < 90:
            if symbolic.get("canonical_form"):
                recommendations.append(f"🟡 OPTIMIZE: Simplify expression to canonical form")

        # Priority 4: Dimensional validation (increased importance)
        if not dimensional["valid"]:
            recommendations.append("🔴 FIX: Resolve dimensional inconsistencies (critical for correctness)")
            if dimensional.get("errors"):
                for error in dimensional.get("errors", [])[:2]:
                    recommendations.append(f"   • {error}")
        elif dimensional["score"] < 85:
            recommendations.append("🟡 IMPROVE: Address dimensional analysis warnings")

        # Priority 5: Domain validation
        if not domain["valid"]:
            recommendations.append(f"🔴 FIX: Violates {self.domain} domain constraints")
        elif domain["score"] < 85:
            recommendations.append(f"🟡 REVIEW: Address domain-specific warnings for {self.domain}")

        # Priority 6: Numerical stability
        if numerical["errors"]:
            recommendations.append("🟠 FIX: Resolve numerical stability issues")
        elif numerical["warnings"]:
            recommendations.append("🟡 OPTIMIZE: Improve numerical stability for production use")

        # Score guidance
        if score_gap > 0 and recommendations:
            recommendations.insert(0, f"📊 SCORE GAP: {score_gap:.1f} points below threshold ({total_score:.1f}/85.0)")

        # Success message
        if not recommendations or (total_score >= 85.0 and not critical_cases and not major_cases):
            recommendations.append("✅ Expression passes all validation checks!")

        return recommendations

    # History management methods

    def clear_history(self):
        """Clear all validation history."""
        if isinstance(self.validation_history, deque):
            self.validation_history.clear()
        else:
            self.validation_history = []

        # Also clear sub-validator histories
        self.symbolic_validator.clear_history()
        self.dimensional_validator.clear_history()
        self.domain_validator.clear_history()

    def get_history(self, limit: Optional[int] = None) -> List[Dict]:
        """Get validation history."""
        history_list = list(self.validation_history)
        if limit is not None:
            return history_list[-limit:]
        return history_list

    def get_statistics(self) -> Dict:
        """Get comprehensive statistics about validation history."""
        if not self.validation_history:
            return {
                "total_validations": 0,
                "success_rate": 0.0,
                "average_total_score": 0.0,
                "average_layer_scores": {},
                "threshold_used": self.VALIDATION_THRESHOLDS["minimum_total_score"],
                "weights_used": self.weights,
            }

        total = len(self.validation_history)
        valid_count = sum(1 for v in self.validation_history if v["valid"])

        avg_total_score = sum(v["total_score"] for v in self.validation_history) / total

        # Calculate average scores per layer
        avg_layer_scores = {}
        for layer in ["symbolic", "dimensional", "domain", "numerical"]:
            scores = [v["layer_scores"][layer] for v in self.validation_history]
            avg_layer_scores[layer] = sum(scores) / len(scores)

        # Calculate average penalties
        avg_penalties = (
            sum(v.get("penalties_applied", {}).get("total_deducted", 0.0) for v in self.validation_history) / total
        )

        return {
            "total_validations": total,
            "success_rate": valid_count / total,
            "average_total_score": avg_total_score,
            "average_base_score": sum(v["base_score"] for v in self.validation_history) / total,
            "average_penalties": avg_penalties,
            "average_layer_scores": avg_layer_scores,
            "valid_count": valid_count,
            "invalid_count": total - valid_count,
            "domain": self.domain,
            "threshold_used": self.VALIDATION_THRESHOLDS["minimum_total_score"],
            "weights_used": self.weights,
        }

    def get_weakest_layer(self) -> Optional[str]:
        """Identify which validation layer has the lowest average score."""
        stats = self.get_statistics()
        if not stats["average_layer_scores"]:
            return None

        return min(stats["average_layer_scores"].items(), key=lambda x: x[1])[0]

    def get_penalty_summary(self) -> Dict:
        """Get summary of penalties applied across validation history."""
        if not self.validation_history:
            return {"total_penalties": 0.0, "critical_count": 0, "major_count": 0, "warning_count": 0}

        total_penalties = sum(
            v.get("penalties_applied", {}).get("total_deducted", 0.0) for v in self.validation_history
        )

        critical_count = sum(v.get("penalties_applied", {}).get("critical_count", 0) for v in self.validation_history)

        major_count = sum(v.get("penalties_applied", {}).get("major_count", 0) for v in self.validation_history)

        warning_count = sum(v.get("penalties_applied", {}).get("warning_count", 0) for v in self.validation_history)

        return {
            "total_penalties": total_penalties,
            "critical_count": critical_count,
            "major_count": major_count,
            "warning_count": warning_count,
            "average_per_validation": (
                total_penalties / len(self.validation_history) if self.validation_history else 0.0
            ),
        }


# Example usage
if __name__ == "__main__":
    # Initialize ensemble validator with recalibrated settings
    validator = EnsembleValidator(domain="defi")

    # Test expression
    result = validator.validate_complete(
        expression_str="sqrt(reserve0 * reserve1) / liquidity",
        variable_definitions={
            "reserve0": "Token 0 reserves",
            "reserve1": "Token 1 reserves",
            "liquidity": "Total pool liquidity",
        },
        variable_units={"reserve0": "USD", "reserve1": "USD", "liquidity": "USD"},
        test_data={
            "reserve0": np.array([100, 200, 300]),
            "reserve1": np.array([50, 100, 150]),
            "liquidity": np.array([1000, 2000, 3000]),
        },
    )

    print("=" * 70)
    print("VALIDATION RESULTS (Recalibrated Thresholds)")
    print("=" * 70)
    print(f"\nOverall Valid: {result['valid']}")
    print(f"Total Score: {result['total_score']:.2f} / 85.0 (threshold)")
    print(f"Base Score: {result['base_score']:.2f} (before penalties)")

    print(f"\n--- Acceptance Criteria ---")
    for key, value in result["acceptance_criteria"].items():
        status = "✅" if value else "❌"
        print(f"  {status} {key}: {value}")

    print(f"\n--- Layer Scores (Weights: {validator.weights}) ---")
    for layer, score in result["layer_scores"].items():
        weight = validator.weights[layer]
        print(f"  {layer:12s}: {score:5.2f} (weight: {weight:.2f})")

    print(f"\n--- Penalties Applied ---")
    penalties = result["penalties_applied"]
    print(f"  Total Deducted: {penalties['total_deducted']:.2f} points")
    print(f"  Critical Issues: {penalties['critical_count']}")
    print(f"  Major Issues: {penalties['major_count']}")
    print(f"  Warnings: {penalties['warning_count']}")
    if penalties["breakdown"]:
        print(f"  Breakdown:")
        for item in penalties["breakdown"]:
            print(f"    • {item}")

    print(f"\n--- Edge Cases Detected ---")
    if result["edge_cases_detected"]:
        for edge_case in result["edge_cases_detected"]:
            print(f"  • {edge_case}")
    else:
        print(f"  ✅ No edge cases detected")

    print(f"\n--- Recommendations ---")
    for rec in result["recommendations"]:
        print(f"  {rec}")

    # Get statistics
    print(f"\n{'=' * 70}")
    print("VALIDATION STATISTICS")
    print("=" * 70)
    stats = validator.get_statistics()
    print(f"Total Validations: {stats['total_validations']}")
    print(f"Success Rate: {stats['success_rate']:.1%}")
    print(f"Average Total Score: {stats['average_total_score']:.2f}")
    print(f"Average Base Score: {stats['average_base_score']:.2f}")
    print(f"Average Penalties: {stats['average_penalties']:.2f}")
    print(f"Weakest Layer: {validator.get_weakest_layer()}")

    # Get penalty summary
    penalty_summary = validator.get_penalty_summary()
    print(f"\n--- Penalty Summary ---")
    print(f"Total Penalties: {penalty_summary['total_penalties']:.2f}")
    print(f"Critical Count: {penalty_summary['critical_count']}")
    print(f"Major Count: {penalty_summary['major_count']}")
    print(f"Warning Count: {penalty_summary['warning_count']}")
    print(f"Average per Validation: {penalty_summary['average_per_validation']:.2f}")


# Complete Feature Set:
# ✅ Recalibrated thresholds - 85.0 minimum score (down from 94.0)
# ✅ Rebalanced weights - Dimensional validation now 35% (up from 25%)
# ✅ 3-tier penalty system - CRITICAL (-20), MAJOR (-12), WARNING (-5)
# ✅ Enhanced edge case detection - Better classification and tracking
# ✅ Comprehensive reporting - Penalties breakdown, acceptance criteria, statistics
# ✅ Example usage - Full demonstration with formatted output


# Key Changes Implemented:
# 1. Recalibrated Scoring Thresholds (85.0 alignment)

# minimum_total_score: 85.0 (production-ready threshold)
# minimum_layer_score: 65.0 (lowered from 70.0)
# critical_failure_threshold: 40.0 (lowered from 50.0)

# 2. Rebalanced Validation Layer Weights
#'symbolic': 0.30      # ↓ from 0.35
#'dimensional': 0.35   # ↑ from 0.25 (increased focus on dimensional issues)
#'domain': 0.30        # maintained
#'numerical': 0.05     # ↓ from 0.10 (supplementary only)

"""
The validator now properly prioritizes dimensional consistency issues while maintaining a practical 85.0 threshold for production-ready expressions. The graduated penalty system ensures critical issues block validation while allowing minor warnings in otherwise valid expressions.
"""
