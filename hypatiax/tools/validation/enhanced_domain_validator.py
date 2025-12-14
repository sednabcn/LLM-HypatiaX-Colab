#!/usr/bin/env python3
"""
HypatiaX Enhanced Domain Validator - FIXED VERSION
tools/validation/enhanced_domain_validator.py

FIXES APPLIED:
1. Better syntax validation before sympify (catches "x + + y")
2. Reduced penalties for valid data (score goes from 57 to 75+)
3. Fixed Sharpe ratio denominator detection
4. Improved scoring logic to not over-penalize suggestions
5. Robust sympify: pass explicit symbol locals derived from variable_definitions to avoid parsing
   ambiguities (fixes "Symbol' and 'FunctionClass'" parse errors for names like "rf").
"""

import re
from collections import deque
from enum import Enum
from typing import Any, Dict, List, Optional, Set, Tuple

import numpy as np
import sympy as sp


class ConstraintType(Enum):
    """Types of variable constraints"""

    POSITIVE = "positive"
    NON_NEGATIVE = "non_negative"
    STRICTLY_POSITIVE = "strictly_positive"
    BOUNDED = "bounded"
    PERCENTAGE = "percentage"
    PERCENTAGE_STRICT = "percentage_strict"
    PROBABILITY = "probability"
    INTEGER = "integer"
    RATIO = "ratio"


class EnhancedDomainValidator:
    """Production-grade domain validator with comprehensive edge case handling."""

    def __init__(self, domain: str = "defi", max_history: Optional[int] = 1000):
        """Initialize enhanced domain validator."""
        self.domain = domain.lower()
        self.constraints = self._load_enhanced_constraints()
        self.formula_patterns = self._load_formula_patterns()

        if max_history is not None:
            self.validation_history = deque(maxlen=max_history)
        else:
            self.validation_history = deque()

    def _load_enhanced_constraints(self) -> Dict:
        """Load comprehensive domain-specific constraints."""
        constraints = {
            "defi": {
                "strictly_positive": {
                    "reserves": [
                        "x",
                        "y",
                        "reserve_x",
                        "reserve_y",
                        "x0",
                        "y0",
                        "x_0",
                        "y_0",
                        "reserve0",
                        "reserve1",
                        "L",
                        "liquidity",
                    ],
                    "prices": [
                        "price",
                        "p",
                        "P",
                        "p_t",
                        "p_0",
                        "p0",
                        "pt",
                        "p1",
                        "p2",
                        "price_current",
                        "price_initial",
                        "spot_price",
                    ],
                    "ratios": ["r", "ratio", "price_ratio", "reserve_ratio"],
                    "amounts": ["amount", "dx", "dy", "amount_in", "amount_out"],
                },
                "bounded_strict": {
                    "fee": (0, 1, "strict"),
                    "phi": (0, 1, "strict"),
                    "gamma": (0, 1, "strict"),
                    "slippage": (0, 1, "inclusive"),
                    "utilization": (0, 1, "inclusive"),
                },
                "edge_cases": {
                    "il_ratio": {
                        "variable": "r",
                        "constraint": "r > 0",
                        "reason": "Impermanent Loss formula: (1+r) in denominator",
                        "critical": True,
                    },
                    "constant_product": {
                        "constraint": "x * y = k",
                        "reason": "AMM invariant must be preserved",
                        "critical": True,
                    },
                    "fee_at_100": {
                        "constraint": "fee < 1.0",
                        "reason": "Fee at 100% breaks (1-fee) multiplier",
                        "critical": True,
                    },
                    "zero_reserve": {
                        "constraint": "reserves > 0",
                        "reason": "Empty pool breaks all calculations",
                        "critical": True,
                    },
                },
                "special_checks": [
                    "constant_product",
                    "no_negative_slippage",
                    "ratio_positivity",
                    "price_positivity",
                    "division_protection",
                    "epsilon_guards",
                    "il_constraints",
                    "amm_invariants",
                ],
            },
            "finance": {
                "strictly_positive": {
                    "prices": ["price", "P", "S", "spot", "strike", "K"],
                    "volatility": ["sigma", "vol", "volatility", "std"],
                    "time": ["t", "T", "time", "maturity", "tau"],
                },
                "bounded_strict": {
                    "return": (-1, None, "lower_inclusive"),
                    "weight": (0, 1, "inclusive"),
                    "allocation": (0, 1, "inclusive"),
                    "correlation": (-1, 1, "inclusive"),
                },
                "edge_cases": {
                    "sharpe_denominator": {
                        "constraint": "sigma > 0",
                        "reason": "Sharpe ratio: divide by volatility",
                        "critical": True,
                    },
                    "option_moneyness": {
                        "constraint": "S > 0, K > 0",
                        "reason": "Option pricing requires positive prices",
                        "critical": True,
                    },
                },
                "special_checks": [
                    "weights_sum_to_one",
                    "sharpe_denominator",
                    "positive_volatility",
                    "correlation_bounds",
                ],
            },
            "risk": {
                "strictly_positive": {
                    "var": ["VaR", "var", "value_at_risk"],
                    "es": ["ES", "CVaR", "expected_shortfall"],
                    "volatility": ["sigma", "vol", "volatility"],
                },
                "bounded_strict": {
                    "confidence": (0, 1, "exclusive"),
                    "alpha": (0, 1, "exclusive"),
                    "probability": (0, 1, "inclusive"),
                },
                "edge_cases": {
                    "var_confidence": {
                        "constraint": "0 < alpha < 1",
                        "reason": "Confidence level must be in (0,1) exclusive",
                        "critical": True,
                    }
                },
                "special_checks": ["var_positive", "confidence_valid", "probability_sum"],
            },
            "esg": {
                "bounded_strict": {
                    "score": (0, 100, "inclusive"),
                    "rating": (0, 10, "inclusive"),
                    "weight": (0, 1, "inclusive"),
                },
                "non_negative": ["impact", "emissions", "carbon", "footprint"],
                "special_checks": ["score_range", "weights_sum_to_one", "non_negative_impact"],
            },
        }
        return constraints.get(self.domain, {})

    def _load_formula_patterns(self) -> Dict:
        """Load formula-specific validation patterns."""
        patterns = {
            "defi": {
                "impermanent_loss": {
                    "pattern": r"(sqrt|√).*\(.*r.*\).*/(.*1.*\+.*r.*)",
                    "variables": {"r": ConstraintType.RATIO},
                    "critical_constraints": ["r > 0"],
                    "edge_cases": ["r close to 0", "r → ∞"],
                },
                "constant_product": {
                    "pattern": r"(x.*\*.*y|y.*\*.*x)",
                    "variables": {"x": ConstraintType.POSITIVE, "y": ConstraintType.POSITIVE},
                    "invariant": "x * y = k",
                    "edge_cases": ["x or y → 0"],
                },
                "swap_output": {
                    "pattern": r"(dy|amount_out|output).*=.*(dx|amount_in).*\(1.*-.*fee\)",
                    "variables": {"fee": ConstraintType.PERCENTAGE_STRICT},
                    "critical_constraints": ["fee < 1", "reserves > 0"],
                    "edge_cases": ["fee = 1", "low liquidity"],
                },
            },
            "finance": {
                "sharpe_ratio": {
                    "pattern": r"(return.*-.*rf|r.*-.*rf).*/.*sigma",
                    "variables": {"sigma": ConstraintType.POSITIVE},
                    "critical_constraints": ["sigma > 0"],
                    "edge_cases": ["sigma → 0"],
                }
            },
        }
        return patterns.get(self.domain, {})

    def validate(
        self,
        expression_str: str,
        variable_definitions: Dict[str, str],
        variable_constraints: Optional[Dict[str, Dict[str, Any]]] = None,
        test_data: Optional[Dict[str, np.ndarray]] = None,
        formula_type: Optional[str] = None,
    ) -> Dict[str, Any]:
        """Comprehensive domain validation with constraint checking."""
        result = {
            "valid": True,
            "score": 100.0,
            "errors": [],
            "warnings": [],
            "info": [],
            "domain": self.domain,
            "formula_type": formula_type,
            "constraints_checked": [],
            "constraint_violations": [],
            "edge_cases_detected": [],
            "suggested_constraints": [],
            "remediation_steps": [],
        }

        # Validate basic syntax
        if not expression_str or not expression_str.strip():
            result["errors"].append("Empty expression provided")
            result["valid"] = False
            result["score"] = 0
            self.validation_history.append(result)
            return result

        # FIX 1: Enhanced syntax validation before sympify
        invalid_patterns = [
            (r"\+\s*\+", "consecutive plus operators (++)"),
            (r"-\s*-(?![0-9])", "consecutive minus operators (--)"),
            (r"\*\s*\*\s*-", "invalid power operator (**-)"),
            (r"(?<![*])\*\s*\+", "multiplication followed by plus (*+)"),
            (r"/\s*\+", "division followed by plus (/+)"),
        ]

        for pattern, description in invalid_patterns:
            if re.search(pattern, expression_str):
                result["errors"].append(f"Invalid syntax: {description} detected")
                result["valid"] = False
                result["score"] = 0
                self.validation_history.append(result)
                return result

        # Robust sympify: if variable_definitions provided, create explicit symbols to avoid parsing ambiguities
        sympy_locals = {}
        try:
            if variable_definitions:
                for name in variable_definitions.keys():
                    # Create a SymPy symbol for each variable name (safe even with underscores/numbers)
                    try:
                        sympy_locals[name] = sp.symbols(name)
                    except Exception:
                        # Defensive: fallback to a generic symbol name if direct creation fails
                        sympy_locals[name] = sp.Symbol(name)
            # Always include common functions in locals to avoid them being treated as unknown classes
            sympy_locals.update({"sqrt": sp.sqrt, "sin": sp.sin, "cos": sp.cos, "log": sp.log, "exp": sp.exp})
            expr = sp.sympify(expression_str, locals=sympy_locals)
            result["info"].append(f"Parsed expression: {expr}")
        except Exception as e:
            result["errors"].append(f"Cannot parse expression: {str(e)}")
            result["valid"] = False
            result["score"] = 0
            self.validation_history.append(result)
            return result

        # Auto-detect formula type
        if not formula_type:
            formula_type = self._detect_formula_type(expression_str)
            if formula_type:
                result["formula_type"] = formula_type
                result["info"].append(f"Detected formula type: {formula_type}")

        # Validation steps
        result = self._check_strictly_positive_variables(expression_str, expr, test_data, result)
        result = self._check_bounded_variables_strict(expression_str, expr, test_data, result)

        if variable_constraints:
            result = self._validate_explicit_constraints(expr, variable_constraints, test_data, result)

        result = self._check_defi_edge_cases(expression_str, expr, formula_type, test_data, result)
        result = self._check_special_rules(expression_str, expr, variable_definitions, test_data, result)

        if formula_type:
            result = self._validate_formula_specific(expression_str, expr, formula_type, test_data, result)

        result = self._check_epsilon_protection(expression_str, expr, result)

        # Final validity
        if result["errors"]:
            result["valid"] = False

        result["score"] = max(0.0, min(100.0, result["score"]))
        self.validation_history.append(result)
        return result

    def _detect_formula_type(self, expr_str: str) -> Optional[str]:
        """Auto-detect formula type from pattern matching."""
        expr_clean = expr_str.replace(" ", "").lower()
        for formula_type, pattern_info in self.formula_patterns.items():
            pattern = pattern_info.get("pattern", "")
            if re.search(pattern, expr_clean, re.IGNORECASE):
                return formula_type
        return None

    def _check_strictly_positive_variables(
        self, expr_str: str, expr: sp.Expr, test_data: Optional[Dict], result: Dict
    ) -> Dict:
        """FIX 2: Don't penalize when test data is provided and valid."""
        strictly_positive = self.constraints.get("strictly_positive", {})

        for category, var_list in strictly_positive.items():
            for var in var_list:
                if self._variable_in_expression(var, expr_str, expr):
                    result["constraints_checked"].append(f"{var}_strictly_positive")

                    if test_data and var in test_data:
                        values = test_data[var]
                        min_val = np.min(values)

                        if np.any(values <= 0):
                            result["errors"].append(
                                f"CRITICAL: '{var}' ({category}) must be strictly positive (> 0), "
                                f"found minimum: {min_val:.6e}. "
                                f"Remediation: Add input validation: assert {var} > 0"
                            )
                            result["constraint_violations"].append(
                                {
                                    "variable": var,
                                    "constraint": f"{var} > 0",
                                    "actual": float(min_val),
                                    "severity": "critical",
                                }
                            )
                            result["remediation_steps"].append(f"Add constraint validation: assert {var} > 0")
                            result["score"] -= 25
                        elif np.any(values < 1e-8):
                            result["warnings"].append(
                                f"'{var}' has very small values (< 1e-8), numerical instability risk"
                            )
                            result["score"] -= 5
                        # REMOVED: Don't warn/penalize for valid data
                    else:
                        result["suggested_constraints"].append(
                            f"Add constraint: {var} > 0  # {category} must be strictly positive"
                        )
                        result["info"].append(f"Note: '{var}' ({category}) should be validated as strictly positive")
                        result["score"] -= 5  # Reduced from -8

        return result

    def _check_bounded_variables_strict(
        self, expr_str: str, expr: sp.Expr, test_data: Optional[Dict], result: Dict
    ) -> Dict:
        """Check bounded variables with strict/inclusive enforcement."""
        bounded_vars = self.constraints.get("bounded_strict", {})

        for var, bounds_info in bounded_vars.items():
            if not self._variable_in_expression(var, expr_str, expr):
                continue

            lower, upper, bound_type = bounds_info
            result["constraints_checked"].append(f"{var}_bounded")

            if test_data and var in test_data:
                values = test_data[var]
                min_val = np.min(values)
                max_val = np.max(values)
                violations = []

                if lower is not None:
                    if bound_type in ["strict", "exclusive"]:
                        if np.any(values <= lower):
                            violations.append(f"{var} must be > {lower} (strict), found {min_val:.6f}")
                    else:
                        if np.any(values < lower):
                            violations.append(f"{var} must be >= {lower}, found {min_val:.6f}")

                if upper is not None:
                    if bound_type in ["strict", "exclusive"]:
                        if np.any(values >= upper):
                            violations.append(f"{var} must be < {upper} (strict), found {max_val:.6f}")
                    else:
                        if np.any(values > upper):
                            violations.append(f"{var} must be <= {upper}, found {max_val:.6f}")

                if violations:
                    for violation in violations:
                        result["errors"].append(f"Bound violation: {violation}")
                        result["constraint_violations"].append(
                            {"variable": var, "violation": violation, "severity": "high"}
                        )
                    result["score"] -= 15 * len(violations)

                    if lower is not None and upper is not None:
                        bound_str = (
                            f"{lower} < {var} < {upper}" if bound_type == "strict" else f"{lower} <= {var} <= {upper}"
                        )
                    elif lower is not None:
                        bound_str = f"{var} > {lower}" if bound_type == "strict" else f"{var} >= {lower}"
                    else:
                        bound_str = f"{var} < {upper}" if bound_type == "strict" else f"{var} <= {upper}"
                    result["remediation_steps"].append(f"Add constraint: {bound_str}")
            else:
                if lower is not None and upper is not None:
                    bound_str = (
                        f"{lower} < {var} < {upper}" if bound_type == "strict" else f"{lower} <= {var} <= {upper}"
                    )
                elif lower is not None:
                    bound_str = f"{var} > {lower}" if bound_type == "strict" else f"{var} >= {lower}"
                else:
                    bound_str = f"{var} < {upper}" if bound_type == "strict" else f"{var} <= {upper}"
                result["suggested_constraints"].append(f"Add constraint: {bound_str}")
                result["score"] -= 5

        return result

    def _validate_explicit_constraints(
        self, expr: sp.Expr, variable_constraints: Dict[str, Dict[str, Any]], test_data: Optional[Dict], result: Dict
    ) -> Dict:
        """Validate explicitly provided variable constraints."""
        for var, constraint_spec in variable_constraints.items():
            constraint_type = constraint_spec.get("type")
            min_val = constraint_spec.get("min")
            max_val = constraint_spec.get("max")
            reason = constraint_spec.get("reason", "")

            result["constraints_checked"].append(f"{var}_explicit")

            if test_data and var in test_data:
                values = test_data[var]
                actual_min = np.min(values)
                actual_max = np.max(values)

                if constraint_type == "strictly_positive":
                    if np.any(values <= 0):
                        result["errors"].append(
                            f"CRITICAL: '{var}' violates constraint > 0 (min: {actual_min:.6e}). Reason: {reason}"
                        )
                        result["score"] -= 30

                elif constraint_type == "non_negative":
                    if np.any(values < 0):
                        result["errors"].append(f"'{var}' violates constraint >= 0 (min: {actual_min:.6f})")
                        result["score"] -= 20

                elif constraint_type == "percentage_strict":
                    if np.any(values <= 0) or np.any(values >= 1):
                        result["errors"].append(
                            f"'{var}' violates 0 < {var} < 1 (range: [{actual_min:.6f}, {actual_max:.6f}])"
                        )
                        result["score"] -= 25

                if min_val is not None and actual_min < min_val:
                    result["errors"].append(f"'{var}' below minimum {min_val} (actual: {actual_min:.6f})")
                    result["score"] -= 15

                if max_val is not None and actual_max > max_val:
                    result["errors"].append(f"'{var}' above maximum {max_val} (actual: {actual_max:.6f})")
                    result["score"] -= 15

        return result

    def _check_defi_edge_cases(
        self, expr_str: str, expr: sp.Expr, formula_type: Optional[str], test_data: Optional[Dict], result: Dict
    ) -> Dict:
        """Check DeFi-specific edge cases."""
        if self.domain != "defi":
            return result

        edge_cases = self.constraints.get("edge_cases", {})

        # IL ratio constraint
        if "il_ratio" in edge_cases or formula_type == "impermanent_loss":
            if "r" in expr_str or any(var.name == "r" for var in expr.free_symbols):
                result["edge_cases_detected"].append("il_ratio_constraint")

                expr_clean = expr_str.replace(" ", "")
                if "(1+r)" in expr_clean or "/(1+r)" in expr_clean:
                    if test_data and "r" in test_data:
                        r_values = test_data["r"]
                        if np.any(r_values <= 0):
                            result["errors"].append(
                                f"CRITICAL DeFi EDGE CASE: Variable 'r' must be positive. "
                                f"Found min r = {np.min(r_values):.6f}. "
                                f"Remediation: Add constraint 'if r <= 0: raise ValueError'"
                            )
                            result["constraint_violations"].append(
                                {
                                    "edge_case": "il_ratio",
                                    "constraint": "r > 0",
                                    "reason": "Prevents (1+r) = 0",
                                    "severity": "critical",
                                }
                            )
                            result["remediation_steps"].append(
                                "Add input validation: if r <= 0: raise ValueError('r must be positive')"
                            )
                            result["score"] -= 35

        # Fee at 100%
        if "fee_at_100" in edge_cases:
            fee_vars = ["fee", "phi", "gamma"]
            for fee_var in fee_vars:
                if self._variable_in_expression(fee_var, expr_str, expr):
                    result["edge_cases_detected"].append("fee_at_100_percent")

                    if f"(1-{fee_var})" in expr_str.replace(" ", "") or f"(1 - {fee_var})" in expr_str:
                        result["warnings"].append(
                            f"Edge case: '{fee_var}' in (1-{fee_var}) term. "
                            f"Ensure {fee_var} < 1.0 (not <=) to prevent zero multiplier"
                        )
                        result["suggested_constraints"].append(f"Add constraint: {fee_var} < 1.0  # Strict inequality")
                        result["score"] -= 10

                    if test_data and fee_var in test_data:
                        fee_values = test_data[fee_var]
                        if np.any(fee_values >= 1.0):
                            result["errors"].append(
                                f"CRITICAL: Fee '{fee_var}' at or above 100% "
                                f"(max: {np.max(fee_values):.6f}). Breaks (1-fee) multiplier."
                            )
                            result["score"] -= 30

        # Zero reserves
        if "zero_reserve" in edge_cases:
            reserve_vars = ["x", "y", "reserve_x", "reserve_y", "x0", "y0", "L", "liquidity"]
            for reserve_var in reserve_vars:
                if self._variable_in_expression(reserve_var, expr_str, expr):
                    result["edge_cases_detected"].append("zero_reserve_check")

                    if test_data and reserve_var in test_data:
                        reserve_values = test_data[reserve_var]
                        if np.any(reserve_values <= 0):
                            result["errors"].append(
                                f"CRITICAL: Reserve '{reserve_var}' at or below zero "
                                f"(min: {np.min(reserve_values):.6f}). Empty pool!"
                            )
                            result["score"] -= 35

        return result

    def _check_special_rules(
        self, expr_str: str, expr: sp.Expr, var_defs: Dict, test_data: Optional[Dict], result: Dict
    ) -> Dict:
        """Check domain-specific special rules."""
        special_checks = self.constraints.get("special_checks", [])

        for check in special_checks:
            if check == "ratio_positivity":
                result = self._check_ratio_positivity(expr_str, expr, test_data, result)
            elif check == "price_positivity":
                result = self._check_price_positivity(expr_str, expr, test_data, result)
            elif check == "no_negative_slippage":
                result = self._check_no_negative_slippage(expr_str, test_data, result)
            elif check == "weights_sum_to_one":
                result = self._check_weights_sum(var_defs, result)
            elif check == "var_positive":
                result = self._check_var_positive(expr_str, test_data, result)
            elif check == "sharpe_denominator":
                result = self._check_sharpe_denominator(expr_str, expr, test_data, result)

        return result

    def _check_epsilon_protection(self, expr_str: str, expr: sp.Expr, result: Dict) -> Dict:
        """FIX 2: Reduced penalty for epsilon protection."""
        denominators = []
        for atom in sp.preorder_traversal(expr):
            if atom.is_Pow and atom.exp == -1:
                denominators.append(atom.base)

        if denominators:
            has_epsilon = any(pattern in expr_str.lower() for pattern in ["epsilon", "eps", "ε", "1e-", "0.000"])

            if not has_epsilon:
                result["warnings"].append(
                    f"Found {len(denominators)} division(s). "
                    f"Consider epsilon protection: (denominator + ε) where ε = 1e-10"
                )
                result["suggested_constraints"].append("Consider adding: denominator + 1e-10 for numerical stability")
                result["score"] -= 3  # REDUCED from -8
            else:
                result["info"].append("Epsilon protection detected - verify value is appropriate")

        return result

    def _validate_formula_specific(
        self, expr_str: str, expr: sp.Expr, formula_type: str, test_data: Optional[Dict], result: Dict
    ) -> Dict:
        """Formula-type specific validation."""
        if formula_type in self.formula_patterns:
            pattern_info = self.formula_patterns[formula_type]

            required_vars = pattern_info.get("variables", {})
            for var, constraint_type in required_vars.items():
                if not self._variable_in_expression(var, expr_str, expr):
                    result["warnings"].append(f"Formula type '{formula_type}' typically includes variable '{var}'")

            critical_constraints = pattern_info.get("critical_constraints", [])
            for constraint in critical_constraints:
                result["info"].append(f"Critical constraint for {formula_type}: {constraint}")

            edge_cases = pattern_info.get("edge_cases", [])
            if edge_cases:
                result["info"].append(f"Edge cases for {formula_type}: {', '.join(edge_cases)}")

        return result

    def _variable_in_expression(self, var: str, expr_str: str, expr: sp.Expr) -> bool:
        """Check if variable appears in expression."""
        if var in expr_str:
            return True
        free_symbols = {str(sym) for sym in expr.free_symbols}
        return var in free_symbols

    def _check_ratio_positivity(self, expr_str: str, expr: sp.Expr, test_data: Optional[Dict], result: Dict) -> Dict:
        """Check that ratio variables are positive."""
        ratio_vars = ["r", "ratio", "price_ratio", "reserve_ratio"]
        for var in ratio_vars:
            if self._variable_in_expression(var, expr_str, expr):
                if test_data and var in test_data:
                    values = test_data[var]
                    if np.any(values <= 0):
                        result["errors"].append(
                            f"Ratio variable '{var}' must be positive, found min: {np.min(values):.6f}"
                        )
                        result["score"] -= 20
        return result

    def _check_price_positivity(self, expr_str: str, expr: sp.Expr, test_data: Optional[Dict], result: Dict) -> Dict:
        """Check that price variables are positive."""
        price_vars = ["price", "p", "P", "p_t", "p_0", "p0", "pt", "price_current", "price_initial", "spot_price"]
        for var in price_vars:
            if self._variable_in_expression(var, expr_str, expr):
                if test_data and var in test_data:
                    values = test_data[var]
                    if np.any(values <= 0):
                        result["errors"].append(
                            f"Price variable '{var}' must be positive, found min: {np.min(values):.6f}"
                        )
                        result["score"] -= 20
        return result

    def _check_no_negative_slippage(self, expr_str: str, test_data: Optional[Dict], result: Dict) -> Dict:
        """Check that slippage is non-negative."""
        if "slippage" in expr_str:
            if test_data and "slippage" in test_data:
                values = test_data["slippage"]
                if np.any(values < 0):
                    result["errors"].append(f"Slippage cannot be negative, found min: {np.min(values):.6f}")
                    result["score"] -= 15
                elif np.any(values > 1):
                    result["warnings"].append(f"Slippage > 100% detected (max: {np.max(values):.2%})")
                    result["score"] -= 5
        return result

    def _check_weights_sum(self, var_defs: Dict, result: Dict) -> Dict:
        """Check if weight variables should sum to one."""
        weight_vars = [var for var in var_defs.keys() if "weight" in var.lower() or "allocation" in var.lower()]
        if len(weight_vars) > 1:
            result["info"].append(f"Multiple weight variables detected: {weight_vars}. Verify they sum to 1.0")
            result["suggested_constraints"].append(f"Add constraint: sum({', '.join(weight_vars)}) = 1.0")
        return result

    def _check_var_positive(self, expr_str: str, test_data: Optional[Dict], result: Dict) -> Dict:
        """Check that VaR is positive (represents loss magnitude)."""
        var_vars = ["VaR", "var", "value_at_risk"]
        for var in var_vars:
            if var in expr_str:
                if test_data and var in test_data:
                    values = test_data[var]
                    if np.any(values < 0):
                        result["warnings"].append(
                            f"VaR typically represents loss magnitude (positive). "
                            f"Found negative values: min = {np.min(values):.6f}"
                        )
                        result["score"] -= 5
        return result

    def _check_sharpe_denominator(self, expr_str: str, expr: sp.Expr, test_data: Optional[Dict], result: Dict) -> Dict:
        """Improved Sharpe ratio denominator checking with robust detection."""
        expr_clean = expr_str.replace(" ", "").lower()

        # Recognize sigma-like variable names
        sigma_vars = ["sigma", "volatility", "vol"]

        # Heuristic 1: string-based detection of '/sigma' patterns
        has_sigma_division = any(f"/{v}" in expr_clean for v in sigma_vars)

        # Heuristic 2: symbolic detection - check for Pow(..., -1) with sigma base or Mul with sigma**-1
        sigma_in_denominator = False
        detected_sigma_var = None

        for atom in sp.preorder_traversal(expr):
            try:
                # Pow with negative exponent indicates denominator
                if getattr(atom, "is_Pow", False) and getattr(atom, "exp", None) == -1:
                    base_str = str(atom.base).lower()
                    for var in sigma_vars:
                        if var == base_str or var in base_str:
                            sigma_in_denominator = True
                            detected_sigma_var = var
                            break
                # Mul nodes may include a power argument that is negative (i.e., division)
                elif getattr(atom, "is_Mul", False):
                    for arg in getattr(atom, "args", ()):
                        if getattr(arg, "is_Pow", False) and getattr(arg, "exp", None) == -1:
                            base_str = str(arg.base).lower()
                            for var in sigma_vars:
                                if var == base_str or var in base_str:
                                    sigma_in_denominator = True
                                    detected_sigma_var = var
                                    break
                        if sigma_in_denominator:
                            break
                if sigma_in_denominator:
                    break
            except Exception:
                # Be defensive: if sympy objects behave unexpectedly, fall back to string heuristics
                continue

        if not (has_sigma_division or sigma_in_denominator):
            return result

        result["info"].append("Sharpe ratio detected: verify sigma > 0 to avoid division by zero")

        # Determine which sigma variable(s) to check
        if detected_sigma_var:
            vars_to_check = [detected_sigma_var]
        else:
            # pick sigma-like variables that actually appear in the expression
            vars_to_check = [v for v in sigma_vars if self._variable_in_expression(v, expr_str, expr)]

        # If none identified by name, conservatively check all sigma-like names if present in test_data
        if not vars_to_check and test_data:
            vars_to_check = [v for v in sigma_vars if v in (test_data or {})]

        # Validate the sigma variable(s)
        for var in vars_to_check:
            if not self._variable_in_expression(var, expr_str, expr):
                continue
            if test_data and var in test_data:
                values = test_data[var]
                # Zero or negative volatility is critical
                if np.any(values <= 0):
                    result["errors"].append(
                        f"CRITICAL: Sharpe denominator '{var}' must be positive, " f"found min: {np.min(values):.6f}"
                    )
                    result["constraint_violations"].append(
                        {
                            "variable": var,
                            "constraint": f"{var} > 0",
                            "reason": "Division by zero in Sharpe ratio",
                            "severity": "critical",
                        }
                    )
                    result["score"] -= 30

                elif np.any(values < 1e-6):
                    result["warnings"].append(f"Very small volatility (< 1e-6) may cause numerical instability")
                    result["score"] -= 5
            else:
                # No test data available - suggest constraints but don't over-penalize
                result["suggested_constraints"].append(f"Add constraint: {var} > 0  # Required for Sharpe ratio")
                result["score"] -= 3

        return result

    def get_validation_summary(self) -> Dict[str, Any]:
        """Get summary statistics across validation history."""
        if not self.validation_history:
            return {"total_validations": 0}

        total = len(self.validation_history)
        valid_count = sum(1 for v in self.validation_history if v["valid"])
        all_errors = [err for v in self.validation_history for err in v["errors"]]
        all_warnings = [warn for v in self.validation_history for warn in v["warnings"]]
        avg_score = np.mean([v["score"] for v in self.validation_history])

        violation_types = {}
        for v in self.validation_history:
            for violation in v.get("constraint_violations", []):
                vtype = violation.get("variable", "unknown")
                violation_types[vtype] = violation_types.get(vtype, 0) + 1

        return {
            "total_validations": total,
            "valid_count": valid_count,
            "invalid_count": total - valid_count,
            "validity_rate": valid_count / total if total > 0 else 0,
            "average_score": avg_score,
            "total_errors": len(all_errors),
            "total_warnings": len(all_warnings),
            "most_common_violations": sorted(violation_types.items(), key=lambda x: x[1], reverse=True)[:5],
            "domains_validated": list(set(v["domain"] for v in self.validation_history)),
        }

    def export_validation_report(self, filepath: str) -> None:
        """Export validation history to JSON file."""
        import json

        report = {"summary": self.get_validation_summary(), "history": list(self.validation_history)}
        with open(filepath, "w") as f:
            json.dump(report, f, indent=2)

    def clear_history(self) -> None:
        """Clear validation history."""
        self.validation_history.clear()
