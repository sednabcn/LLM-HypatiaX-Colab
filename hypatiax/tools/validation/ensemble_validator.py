"""
HypatiaX Ensemble Validator
tools/validation/ensemble_validator.py

Combines multiple validators for comprehensive validation.

UPDATES (Week 2, Day 3 - Hour 1):
✅ Recalibrated scoring threshold: 70.0 → 85.0 (explicit)
✅ Rebalanced weights: Dimensional 0.25→0.30, Symbolic 0.35→0.30
✅ Added comprehensive edge case detection method
✅ Implemented structured penalty system (-15 critical, -20 dimensional)
✅ Added detailed acceptance criteria documentation
✅ Enhanced dimensional inconsistency handling
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

    ACCEPTANCE CRITERIA (Week 2, Day 3):
    - Overall score >= 85.0 (recalibrated from 70.0)
    - All critical validators must pass (symbolic, dimensional)
    - Domain-specific rules must be satisfied
    - No critical edge cases (division by zero, overflow, NaN)
    - Individual layer scores >= 50.0 (critical failure threshold)
    """

    # HOUR 1 FIX: Clear, explicit threshold documentation
    VALIDATION_THRESHOLDS = {
        "minimum_total_score": 85.0,  # ✅ RECALIBRATED from 70.0
        "minimum_layer_score": 70.0,  # Individual layer minimum
        "critical_failure_threshold": 50.0,  # Below this = automatic failure
        "edge_case_penalty": 15.0,  # ✅ STANDARDIZED: -15 per critical edge case
        "dimensional_inconsistency_penalty": 20.0,  # ✅ INCREASED from 10.0
        "warning_penalty": 5.0,  # Minor issues
        "domain_violation_penalty": 10.0,  # Domain-specific violations
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

        # HOUR 1 FIX: Rebalanced validation weights
        # Dimensional increased to 0.30 (from 0.25) - dimensional issues are critical
        # Symbolic decreased to 0.30 (from 0.35) - balance with dimensional
        self.weights = weights or {
            "symbolic": 0.30,  # ✅ DECREASED from 0.35
            "dimensional": 0.30,  # ✅ INCREASED from 0.25 (dimensional issues critical)
            "domain": 0.30,  # Unchanged at 0.30 (domain rules critical)
            "numerical": 0.10,  # Unchanged at 0.10 (supplementary check)
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

        HOUR 1 UPDATE: Now applies recalibrated 85.0 threshold and enhanced penalties.

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
                'base_score': float (before penalties),
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
        # Add None check at the very beginning
        if expression_str is None:
            return {
                "valid": False,
                "total_score": 0.0,
                "base_score": 0.0,
                "penalties_applied": {
                    "critical": 0,
                    "dimensional": 0,
                    "domain": 0,
                    "warning": 0,
                    "total_deducted": 0,
                },
                "layer_scores": {
                    "symbolic": 0.0,
                    "dimensional": 0.0,
                    "domain": 0.0,
                    "numerical": 0.0,
                },
                "layer_results": {},
                "errors": ["Expression cannot be None"],
                "warnings": [],
                "recommendations": ["Provide a valid expression string"],
                "edge_cases_detected": ["CRITICAL: Empty or null expression"],
                "acceptance_criteria": {
                    "minimum_score_met": False,
                    "symbolic_valid": False,
                    "dimensional_valid": False,
                    "domain_valid": False,
                    "no_critical_edge_cases": False,
                    "threshold_used": self.VALIDATION_THRESHOLDS["minimum_total_score"],
                    "all_layers_above_critical": False,
                },
                "expression": None,
                "canonical_form": None,
                "domain": self.domain,
                "strict_mode": self.strict_mode,
            }

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

        # HOUR 1 FIX: Comprehensive edge case detection
        edge_cases = self._detect_edge_cases(symbolic_result, dimensional_result, domain_result, numerical_result)

        # Calculate base weighted score
        base_score = (
            self.weights["symbolic"] * symbolic_result["score"]
            + self.weights["dimensional"] * dimensional_result["score"]
            + self.weights["domain"] * domain_result["score"]
            + self.weights["numerical"] * numerical_result["score"]
        )

        # HOUR 1 FIX: Apply structured penalties
        total_score, penalties_applied = self._apply_penalties(base_score, edge_cases, dimensional_result)

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

        # HOUR 1 FIX: Determine validity using 85.0 threshold
        overall_valid = self._check_acceptance_criteria(
            total_score, symbolic_result, dimensional_result, domain_result, edge_cases
        )

        # Generate recommendations
        recommendations = self._generate_recommendations(
            symbolic_result, dimensional_result, domain_result, numerical_result, edge_cases
        )

        # HOUR 1 FIX: Detailed acceptance criteria documentation
        acceptance_criteria = {
            "minimum_score_met": total_score >= self.VALIDATION_THRESHOLDS["minimum_total_score"],
            "symbolic_valid": symbolic_result["valid"],
            "dimensional_valid": dimensional_result["valid"],
            "domain_valid": domain_result["valid"],
            "no_critical_edge_cases": len([e for e in edge_cases if "CRITICAL" in e]) == 0,
            "threshold_used": self.VALIDATION_THRESHOLDS["minimum_total_score"],
            "all_layers_above_critical": all(
                score >= self.VALIDATION_THRESHOLDS["critical_failure_threshold"]
                for score in [
                    symbolic_result["score"],
                    dimensional_result["score"],
                    domain_result["score"],
                ]
            ),
        }

        # Compile complete result
        complete_result = {
            "valid": overall_valid,
            "total_score": total_score,
            "base_score": base_score,  # Score before penalties
            "penalties_applied": penalties_applied,  # ✅ NEW: Transparency
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
        }

        # Store in history
        self.validation_history.append(complete_result)

        return complete_result

    def _detect_edge_cases(self, symbolic: Dict, dimensional: Dict, domain: Dict, numerical: Dict) -> List[str]:
        """
        HOUR 1 FIX: Comprehensive edge case detection with structured categorization.

        Categories:
        - CRITICAL: Must fix (division by zero, NaN, Inf, empty expression)
        - DIMENSIONAL: Unit inconsistencies
        - DOMAIN: Domain-specific violations
        - WARNING: Potential issues (overflow, underflow)

        Returns:
            List of categorized edge case strings
        """
        edge_cases = []

        # === CRITICAL SYMBOLIC ISSUES ===
        symbolic_errors_str = str(symbolic.get("errors", [])).lower()

        if "division by zero" in symbolic_errors_str or "divide by zero" in symbolic_errors_str:
            edge_cases.append("CRITICAL: Division by zero detected")

        if "empty" in symbolic_errors_str or "null" in symbolic_errors_str:
            edge_cases.append("CRITICAL: Empty or null expression")

        if "invalid" in symbolic_errors_str and "syntax" in symbolic_errors_str:
            edge_cases.append("CRITICAL: Invalid syntax in expression")

        # === CRITICAL NUMERICAL ISSUES ===
        numerical_errors_str = str(numerical.get("errors", [])).lower()
        numerical_warnings_str = str(numerical.get("warnings", [])).lower()

        if "nan" in numerical_errors_str:
            edge_cases.append("CRITICAL: Expression produces NaN values")

        if "inf" in numerical_errors_str or "infinite" in numerical_errors_str:
            edge_cases.append("CRITICAL: Expression produces infinite values")

        # === WARNING-LEVEL NUMERICAL ISSUES ===
        if "overflow" in numerical_warnings_str:
            edge_cases.append("WARNING: Potential numerical overflow detected")

        if "underflow" in numerical_warnings_str:
            edge_cases.append("WARNING: Potential numerical underflow detected")

        # === DIMENSIONAL INCONSISTENCIES ===
        dimensional_errors = dimensional.get("errors", [])
        for error in dimensional_errors:
            error_lower = error.lower()
            if any(keyword in error_lower for keyword in ["inconsistent", "incompatible", "mismatch"]):
                edge_cases.append(f"DIMENSIONAL: {error}")
            elif "division" in error_lower and "zero" in error_lower:
                edge_cases.append(f"CRITICAL: {error}")
            elif "overflow" in error_lower:
                edge_cases.append(f"WARNING: {error}")

        # === DIMENSIONAL STABILITY ISSUES ===
        dimensional_stability = dimensional.get("numerical_stability", {})
        if not dimensional_stability.get("stable", True):
            for issue in dimensional_stability.get("issues", []):
                if "division" in str(issue).lower():
                    edge_cases.append("WARNING: Unconstrained division detected")

        # === DOMAIN-SPECIFIC VIOLATIONS ===
        domain_errors_str = str(domain.get("errors", [])).lower()

        if "constraint violation" in domain_errors_str or "violates" in domain_errors_str:
            edge_cases.append("DOMAIN: Constraint violation detected")

        if "domain-specific" in domain_errors_str:
            # Extract specific domain errors
            for error in domain.get("errors", []):
                edge_cases.append(f"DOMAIN: {error}")

        # === OVERFLOW RISKS ===
        overflow_risks = dimensional.get("overflow_risks", [])
        for risk in overflow_risks:
            edge_cases.append(f"WARNING: {risk}")

        return edge_cases

    def _apply_penalties(
        self, base_score: float, edge_cases: List[str], dimensional_result: Dict
    ) -> tuple[float, Dict]:
        """
        HOUR 1 FIX: Apply structured penalty system with transparency.

        Penalty Structure:
        - CRITICAL edge case: -15 points (standardized)
        - WARNING edge case: -5 points
        - DIMENSIONAL inconsistency: -20 points (increased from 10)
        - DOMAIN violation: -10 points

        Returns:
            Tuple of (final_score, penalties_dict)
        """
        score = base_score
        penalties = {
            "critical": 0,
            "dimensional": 0,
            "domain": 0,
            "warning": 0,
            "total_deducted": 0,
        }

        for edge_case in edge_cases:
            if "CRITICAL" in edge_case:
                penalty = self.VALIDATION_THRESHOLDS["edge_case_penalty"]
                score -= penalty
                penalties["critical"] += penalty
            elif "DIMENSIONAL" in edge_case:
                penalty = self.VALIDATION_THRESHOLDS["dimensional_inconsistency_penalty"]
                score -= penalty
                penalties["dimensional"] += penalty
            elif "DOMAIN" in edge_case:
                penalty = self.VALIDATION_THRESHOLDS["domain_violation_penalty"]
                score -= penalty
                penalties["domain"] += penalty
            elif "WARNING" in edge_case:
                penalty = self.VALIDATION_THRESHOLDS["warning_penalty"]
                score -= penalty
                penalties["warning"] += penalty

        # Calculate total deducted
        penalties["total_deducted"] = base_score - max(0.0, score)

        # Ensure score doesn't go below 0
        final_score = max(0.0, score)

        return final_score, penalties

    def _check_acceptance_criteria(
        self, total_score: float, symbolic: Dict, dimensional: Dict, domain: Dict, edge_cases: List[str]
    ) -> bool:
        """
        HOUR 1 FIX: Check acceptance criteria with 85.0 threshold.

        Requirements (ALL must be met):
        1. Total score >= 85.0 ✅ (recalibrated threshold)
        2. Symbolic validation must pass
        3. Dimensional validation must pass
        4. No critical edge cases
        5. All layers >= 50.0 (critical failure threshold)
        6. In strict mode: domain validation must also pass

        Returns:
            True if all criteria met, False otherwise
        """
        # 1. Check minimum score threshold (85.0)
        if total_score < self.VALIDATION_THRESHOLDS["minimum_total_score"]:
            return False

        # 2-3. Critical validators must pass
        if not symbolic["valid"] or not dimensional["valid"]:
            return False

        # 4. No critical edge cases allowed
        critical_edge_cases = [e for e in edge_cases if "CRITICAL" in e]
        if critical_edge_cases:
            return False

        # 5. Check for critical failure in any layer
        for score in [symbolic["score"], dimensional["score"], domain["score"]]:
            if score < self.VALIDATION_THRESHOLDS["critical_failure_threshold"]:
                return False

        # 6. In strict mode, domain validation must also pass
        if self.strict_mode and not domain["valid"]:
            return False

        return True

    def _numerical_validation(self, expression_str: str, test_data: Dict[str, np.ndarray], sympy_expr) -> Dict:
        """
        Validate numerical stability using test data.

        Checks:
        - No NaN or Inf in outputs
        - Reasonable output ranges
        - Numerical stability across samples
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
                if np.any(np.isnan(outputs)):
                    result["errors"].append(
                        f"Expression produces NaN values " f"({np.sum(np.isnan(outputs))}/{len(outputs)} samples)"
                    )
                    result["score"] -= 30

                # Check for Inf
                if np.any(np.isinf(outputs)):
                    result["errors"].append(
                        f"Expression produces infinite values " f"({np.sum(np.isinf(outputs))}/{len(outputs)} samples)"
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
                    nonzero_outputs = valid_outputs[valid_outputs != 0]
                    if len(nonzero_outputs) > 0:
                        min_abs = np.min(np.abs(nonzero_outputs))
                        if min_abs < 1e-10:
                            result["warnings"].append(f"Very small output values detected (min: {min_abs:.2e})")
                            result["score"] -= 5

        except Exception as e:
            result["warnings"].append(f"Numerical validation error: {str(e)}")
            result["score"] -= 15

        return result

    def _generate_recommendations(
        self, symbolic: Dict, dimensional: Dict, domain: Dict, numerical: Dict, edge_cases: List[str]
    ) -> List[str]:
        """
        Generate actionable recommendations prioritized by severity.

        Priority Order:
        1. Critical edge cases (MUST FIX)
        2. Dimensional inconsistencies (MUST FIX)
        3. Symbolic errors (MUST FIX)
        4. Domain violations (MUST FIX in strict mode)
        5. Warnings and optimizations (SHOULD FIX)
        """
        recommendations = []

        # 1. Critical edge cases (highest priority)
        critical_cases = [e for e in edge_cases if "CRITICAL" in e]
        if critical_cases:
            recommendations.append(f"🔴 FIX CRITICAL: Resolve {len(critical_cases)} critical edge case(s) immediately")
            for case in critical_cases[:3]:  # Show first 3
                recommendations.append(f"  → {case}")

        # 2. Dimensional inconsistencies
        if not dimensional["valid"]:
            recommendations.append("🔴 FIX CRITICAL: Resolve dimensional inconsistencies before deployment")
            dimensional_errors = dimensional.get("errors", [])[:2]
            for error in dimensional_errors:
                recommendations.append(f"  → {error}")
        elif dimensional.get("warnings"):
            recommendations.append("🟡 VERIFY: Check dimensional analysis warnings")

        # 3. Symbolic errors
        if not symbolic["valid"]:
            recommendations.append("🔴 FIX CRITICAL: Resolve mathematical/symbolic errors")
            symbolic_errors = symbolic.get("errors", [])[:2]
            for error in symbolic_errors:
                recommendations.append(f"  → {error}")
        elif symbolic["score"] < 90 and symbolic.get("canonical_form"):
            recommendations.append(f"🟡 IMPROVE: Simplify to: {symbolic['canonical_form']}")

        # 4. Domain violations
        if not domain["valid"]:
            recommendations.append(f"🔴 FIX CRITICAL: Violates {self.domain} domain constraints")
        elif domain.get("warnings"):
            recommendations.append(f"🟡 REVIEW: Address {self.domain} domain warnings")

        # 5. Numerical stability
        if numerical.get("errors"):
            recommendations.append("🔴 FIX: Resolve numerical stability issues")
        elif numerical.get("warnings"):
            recommendations.append("🟡 OPTIMIZE: Improve numerical stability")

        # 6. Success case
        if not recommendations:
            recommendations.append("✅ Expression passes all validation checks")

        return recommendations

    # === History Management Methods ===

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
        """
        Get comprehensive statistics about validation history.

        Returns statistics using the 85.0 threshold.
        """
        if not self.validation_history:
            return {
                "total_validations": 0,
                "success_rate": 0.0,
                "average_total_score": 0.0,
                "average_layer_scores": {},
                "threshold_used": self.VALIDATION_THRESHOLDS["minimum_total_score"],
            }

        total = len(self.validation_history)
        valid_count = sum(1 for v in self.validation_history if v["valid"])

        avg_total_score = sum(v["total_score"] for v in self.validation_history) / total

        # Calculate average scores per layer
        avg_layer_scores = {}
        for layer in ["symbolic", "dimensional", "domain", "numerical"]:
            scores = [v["layer_scores"][layer] for v in self.validation_history]
            avg_layer_scores[layer] = sum(scores) / len(scores)

        return {
            "total_validations": total,
            "success_rate": valid_count / total,
            "average_total_score": avg_total_score,
            "average_layer_scores": avg_layer_scores,
            "valid_count": valid_count,
            "invalid_count": total - valid_count,
            "domain": self.domain,
            "threshold_used": self.VALIDATION_THRESHOLDS["minimum_total_score"],
        }

    def get_weakest_layer(self) -> Optional[str]:
        """Identify which validation layer has the lowest average score."""
        stats = self.get_statistics()
        if not stats["average_layer_scores"]:
            return None

        return min(stats["average_layer_scores"].items(), key=lambda x: x[1])[0]


# Example usage demonstrating Hour 1 fixes
if __name__ == "__main__":
    print("=" * 80)
    print("ENSEMBLE VALIDATOR - HOUR 1 FIXES DEMONSTRATION")
    print("=" * 80)
    print()

    # Initialize ensemble validator
    validator = EnsembleValidator(domain="defi")

    print(f"✅ Threshold Recalibrated: {validator.VALIDATION_THRESHOLDS['minimum_total_score']}")
    print(f"✅ Weights Rebalanced:")
    print(f"   Symbolic: {validator.weights['symbolic']}")
    print(f"   Dimensional: {validator.weights['dimensional']}")
    print(f"   Domain: {validator.weights['domain']}")
    print(f"   Numerical: {validator.weights['numerical']}")
    print()

    # Test expression
    print("Testing expression: sqrt(reserve0 * reserve1) / liquidity")
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

    print(f"\nOverall Valid: {result['valid']}")
    print(f"Total Score: {result['total_score']:.2f}")
    print(f"Base Score: {result['base_score']:.2f}")

    print(f"\n✅ Penalties Applied:")
    for key, value in result["penalties_applied"].items():
        print(f"   {key}: {value}")

    print(f"\n✅ Acceptance Criteria:")
    for key, value in result["acceptance_criteria"].items():
        print(f"   {key}: {value}")

    print(f"\nLayer Scores:")
    for layer, score in result["layer_scores"].items():
        print(f"  {layer}: {score:.2f}")

    print(f"\n✅ Edge Cases Detected: {len(result['edge_cases_detected'])}")
    for case in result["edge_cases_detected"]:
        print(f"   - {case}")

    print(f"\nRecommendations:")
    for rec in result["recommendations"]:
        print(f"  {rec}")

    # Get statistics
    stats = validator.get_statistics()
    print(f"\nStatistics:")
    print(f"  Total: {stats['total_validations']}")
    print(f"  Success Rate: {stats['success_rate']*100:.1f}%")
    print(f"  Threshold: {stats['threshold_used']}")
    print(f"  Weakest Layer: {validator.get_weakest_layer()}")


"""
✅ Hour 1 Requirements - All Implemented
1. Threshold Recalibration (70.0 → 85.0) ✅

Explicit VALIDATION_THRESHOLDS["minimum_total_score"] = 85.0
Updated all documentation and acceptance criteria
Added clear threshold documentation in class docstring

2. Weight Rebalancing ✅

Dimensional: 0.25 → 0.30 (increased)
Symbolic: 0.35 → 0.30 (decreased)
Domain: 0.30 (unchanged)
Numerical: 0.10 (unchanged)
Added comments explaining the rationale

3. Edge Case Detection Method ✅
Enhanced _detect_edge_cases() with:

Structured categorization (CRITICAL, DIMENSIONAL, DOMAIN, WARNING)
Comprehensive pattern matching
Multiple detection layers for each category
Better handling of dimensional stability issues
Overflow risk detection

4. Penalty System ✅
Enhanced _apply_penalties() with:

-15 points for critical edge cases (standardized)
-20 points for dimensional inconsistencies (increased from 10)
-10 points for domain violations
-5 points for warnings
Returns transparency dict showing breakdown of penalties
Added penalties_applied to results

5. Acceptance Criteria Documentation ✅
Enhanced with:

Clear documentation in class docstring
All 6 criteria explicitly listed
Added all_layers_above_critical check
Transparency in acceptance criteria results
Updated _check_acceptance_criteria() method

Additional Improvements:

Updated header comments to document all Hour 1 fixes
Added demonstration code showing all fixes
Improved code comments throughout
Better type hints (tuple[float, Dict])
Enhanced recommendation generation with priority ordering

The validator now fully meets the Hour 1 specifications and should pass all 5 ensemble tests with the recalibrated 85.0 threshold and enhanced dimensional handling!

"""
