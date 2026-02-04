#!/usr/bin/env python3
"""
Symbolic Validation for Generated Formulas
Uses SymPy for mathematical validation
Part of HypatiaX tools/validation/

WEEK 2 UPDATES:
- Added biology/ biochemistry domain
- Added empty expression validation (Issue #1)
- Enhanced division-by-zero detection (Issue #1)
- Added overflow risk detection (Issue #1)
- Improved numerical stability checks
- Added explicit constraint validation for DeFi formulas

CRITICAL FIX:
- Fixed all variable_units -> variable_definitions references
- Fixed expression_str -> expression references
"""

import re
from collections import deque
from typing import Any, Dict, List, Optional

import sympy as sp
from sympy import simplify, sympify
from sympy.parsing.latex import parse_latex


def safe_sympify(expression_str: str, variable_names: Optional[List[str]] = None):
    """Safely sympify with Pint isolation."""
    if not isinstance(expression_str, str):
        expression_str = str(expression_str)

    local_dict = {}
    if variable_names:
        for var in variable_names:
            local_dict[var] = sp.Symbol(var, real=True)

    local_dict.update(
        {
            "exp": sp.exp,
            "log": sp.log,
            "ln": sp.log,
            "sqrt": sp.sqrt,
            "sin": sp.sin,
            "cos": sp.cos,
            "tan": sp.tan,
        }
    )

    try:
        return sp.sympify(expression_str, locals=local_dict, evaluate=False)
    except:
        try:
            return sp.sympify(expression_str, locals=local_dict, evaluate=True)
        except Exception as e:
            raise ValueError(f"Could not parse: {e}")


class SymbolicValidator:
    """
    Validates generated formulas mathematically

    Uses:
        - SymPy for symbolic mathematics
        - Numerical stability analysis
        - Dimensional consistency
        - Domain-specific constraints
    """

    def __init__(self, max_history: Optional[int] = 1000):
        """
        Initialize the validator.

        Args:
            max_history: Maximum number of validation results to keep in history.
                        If None, no limit. Defaults to 1000.
        """
        self.domain_rules = {
            "defi": self._defi_rules,
            "finance": self._finance_rules,
            "esg": self._esg_rules,
            "risk": self._risk_rules,
            "biology": self._biology_rules,  # ADD THIS
            "biochemistry": self._biology_rules,  # ADD THIS
        }

        # Bounded validation history
        if max_history is not None:
            self.validation_history = deque(maxlen=max_history)
        else:
            self.validation_history = []

    def validate(
        self,
        expression: str,
        variable_definitions: Dict[str, str],
        domain: str = "defi",
        from_latex: bool = False,
    ) -> Dict[str, Any]:
        """
        Comprehensive validation of a mathematical expression.

        Args:
            expression: The mathematical expression (string or LaTeX)
            variable_definitions: Dict mapping variable names to descriptions
            domain: Domain context ('defi', 'finance', 'esg', 'risk')
            from_latex: Whether the expression is in LaTeX format

        Returns:
            {
                'valid': bool,
                'syntactically_valid': bool,
                'dimensionally_consistent': bool,
                'domain_valid': bool,
                'numerically_stable': bool,
                'sympy_expr': SymPy expression object,
                'canonical_form': str (simplified form),
                'errors': [list of error messages],
                'warnings': [list of warnings],
                'score': 0-100
            }
        """
        results = {
            "valid": True,
            "syntactically_valid": False,
            "dimensionally_consistent": False,
            "domain_valid": False,
            "numerically_stable": False,
            "errors": [],
            "warnings": [],
            "sympy_expr": None,
            "canonical_form": None,
        }

        # WEEK 2 FIX: Edge Case #1 - Empty expression validation
        if not expression or not expression.strip():
            results["errors"].append("Empty expression not allowed")
            results["valid"] = False
            return self._finalize_results(results)

        # WEEK 2 FIX: Edge Case #2 - Check for whitespace-only expressions
        if expression.strip() == "":
            results["errors"].append("Expression contains only whitespace")
            results["valid"] = False
            return self._finalize_results(results)

        try:
            # 1. Parse expression
            if from_latex:
                expr = self._safe_parse_latex(expression)
            else:
                expr = safe_sympify(expression, list(variable_definitions.keys()))

            if expr is None:
                results["errors"].append("Cannot parse expression")
                results["valid"] = False
                return self._finalize_results(results)

            results["syntactically_valid"] = True
            results["sympy_expr"] = expr

            # 2. Check for undefined variables
            free_vars = expr.free_symbols
            undefined_vars = [
                str(v) for v in free_vars if str(v) not in variable_definitions
            ]
            if undefined_vars:
                results["errors"].append(f"Undefined variables: {undefined_vars}")
                results["valid"] = False

            # 3. Check for mathematical issues
            if expr.has(sp.zoo):  # Complex infinity
                results["errors"].append("Contains complex infinity")
                results["valid"] = False

            if expr.has(sp.oo):  # Infinity
                results["warnings"].append("Contains infinity - verify limits")

            if expr.has(sp.nan):  # Not a number
                results["errors"].append("Contains NaN (not a number)")
                results["valid"] = False

            # 4. Simplification
            try:
                simplified = simplify(expr)
                results["canonical_form"] = str(simplified)

                if expr != simplified:
                    results["warnings"].append(f"Can be simplified to: {simplified}")
            except Exception as e:
                results["warnings"].append(f"Simplification failed: {str(e)}")
                results["canonical_form"] = str(expr)

            # 5. Dimensional consistency
            if self._check_dimensions(expr, variable_definitions):
                results["dimensionally_consistent"] = True
            else:
                results["errors"].append("Dimensional inconsistency detected")
                results["valid"] = False

            # 6. Domain-specific rules
            domain_check = self.domain_rules.get(domain, self._default_rules)(
                expr, variable_definitions
            )

            results["domain_valid"] = domain_check["valid"]
            results["errors"].extend(domain_check["errors"])
            results["warnings"].extend(domain_check.get("warnings", []))

            if not domain_check["valid"]:
                results["valid"] = False

            # 7. Numerical stability analysis (ENHANCED IN WEEK 2)
            stability = self._check_numerical_stability(expr)
            results["numerically_stable"] = stability["stable"]
            results["warnings"].extend(stability["warnings"])
            results["errors"].extend(stability.get("errors", []))

            # WEEK 2 FIX: Fail validation if critical stability errors found
            if stability.get("errors"):
                results["valid"] = False

        except Exception as e:
            results["errors"].append(f"Validation error: {str(e)}")
            results["valid"] = False

        return self._finalize_results(results)

    def _finalize_results(self, results: Dict[str, Any]) -> Dict[str, Any]:
        """Calculate score and store in history."""
        results["score"] = self._calculate_score(results)
        self.validation_history.append(results)
        return results

    def _safe_parse_latex(self, latex_str: str):
        """Safely parse LaTeX, handling common issues."""
        try:
            # Clean LaTeX string
            latex_str = latex_str.strip()
            latex_str = re.sub(r"\\text\{([^}]+)\}", r"\1", latex_str)

            return parse_latex(latex_str)
        except Exception:
            # Try alternative parsing
            try:
                return sympify(latex_str)
            except Exception:
                return None

    def _check_dimensions(self, expr, variable_definitions: Dict[str, str]) -> bool:
        """
        Dimensional analysis - basic implementation.

        This is a simplified check. For production, implement detailed
        dimensional analysis based on variable types.
        """
        # TODO: Implement proper dimensional analysis
        # For now, just check that operations make sense

        # Check for operations that mix incompatible types
        # e.g., price * price should not equal return

        return True  # Placeholder

    def _check_numerical_stability(self, expr) -> Dict[str, Any]:
        """
        ENHANCED WEEK 2: Numerical stability analysis.

        Checks:
        1. Division by zero risks (ENHANCED)
        2. Overflow/underflow potential (ENHANCED)
        3. Precision loss in operations
        4. Subtractive cancellation
        5. Large number handling (NEW)
        """
        warnings = []
        errors = []  # NEW: Critical stability issues

        # 1. ENHANCED: Find all denominators and flag unprotected divisions
        denominators = self._extract_denominators(expr)
        for denom in denominators:
            if self._could_be_zero(denom):
                # Check if epsilon protection exists
                if not self._has_epsilon_protection(denom):
                    errors.append(
                        f"CRITICAL: Unprotected division by zero risk: {denom}. "
                        f"Add epsilon guard: (denominator + ε)"
                    )
                else:
                    warnings.append(f"Division by zero risk mitigated: {denom}")

        # 2. Check for subtractive cancellation
        subtractions = self._find_subtractions(expr)
        if len(subtractions) > 2:
            warnings.append("Multiple subtractions may cause precision loss")

        # 3. ENHANCED: Check for exponentials with overflow detection
        if expr.has(sp.exp):
            exp_args = self._extract_exp_arguments(expr)
            for arg in exp_args:
                # Check if exponent could be very large
                if self._could_overflow_exp(arg):
                    warnings.append(
                        f"Exponential overflow risk: exp({arg}). "
                        f"Recommend capping argument or using safe_exp"
                    )

        # 4. ENHANCED: Check for products with overflow detection
        if expr.has(sp.Mul):
            mul_terms = self._extract_multiplication_chains(expr)
            if len(mul_terms) > 3:
                warnings.append(
                    f"Multiple multiplications ({len(mul_terms)} terms) - "
                    f"check for overflow. Consider: {' * '.join(map(str, mul_terms[:3]))}..."
                )

        # 5. Check sqrt of potentially negative values
        if expr.has(sp.sqrt):
            sqrt_args = self._extract_sqrt_arguments(expr)
            for arg in sqrt_args:
                if not self._guaranteed_positive(arg):
                    warnings.append(
                        f"Square root of potentially negative value: sqrt({arg}). "
                        f"Add validation or use abs()"
                    )

        # 6. Check for logarithms (domain issues)
        if expr.has(sp.log):
            log_args = self._extract_log_arguments(expr)
            for arg in log_args:
                if not self._guaranteed_positive(arg):
                    warnings.append(
                        f"Logarithm of non-positive value risk: log({arg}). "
                        f"Ensure {arg} > 0"
                    )

        # 7. Check for trigonometric functions (range issues)
        if any(expr.has(func) for func in [sp.sin, sp.cos, sp.tan]):
            warnings.append("Trigonometric functions - verify input ranges")

        # 8. NEW WEEK 2: Check for power operations with large exponents
        if expr.has(sp.Pow):
            power_terms = self._extract_power_terms(expr)
            for base, exp_val in power_terms:
                if self._could_overflow_power(base, exp_val):
                    warnings.append(
                        f"Power overflow risk: ({base})^({exp_val}). "
                        f"Verify bounds on base and exponent"
                    )

        return {
            "stable": len(warnings) == 0 and len(errors) == 0,
            "warnings": warnings,
            "errors": errors,
        }

    # NEW WEEK 2: Helper methods for enhanced stability checks

    def _has_epsilon_protection(self, expr) -> bool:
        """Check if expression has epsilon protection for division."""
        expr_str = str(expr).lower()
        # Look for common epsilon patterns
        epsilon_patterns = ["epsilon", "eps", "ε", "+ 1e-", "+ 0.000"]
        return any(pattern in expr_str for pattern in epsilon_patterns)

    def _extract_exp_arguments(self, expr) -> List:
        """Extract arguments to exponential functions."""
        args = []
        if expr.func == sp.exp:
            args.append(expr.args[0])
        if hasattr(expr, "args"):
            for arg in expr.args:
                args.extend(self._extract_exp_arguments(arg))
        return args

    def _could_overflow_exp(self, arg) -> bool:
        """Check if exponential argument could cause overflow."""
        # Conservative: if arg contains multiplication or powers, flag it
        arg_str = str(arg)
        if "*" in arg_str or "**" in arg_str or "^" in arg_str:
            return True
        # If arg is a symbol without bounds, flag it
        if arg.free_symbols and not arg.is_Number:
            return True
        return False

    def _extract_multiplication_chains(self, expr) -> List:
        """Extract terms in multiplication chains."""
        terms = []
        if expr.is_Mul:
            terms.extend(expr.args)
        if hasattr(expr, "args"):
            for arg in expr.args:
                if arg.is_Mul:
                    terms.extend(arg.args)
        return terms

    def _extract_sqrt_arguments(self, expr) -> List:
        """Extract arguments to square root functions."""
        args = []
        if expr.func == sp.sqrt:
            args.append(expr.args[0])
        if hasattr(expr, "args"):
            for arg in expr.args:
                args.extend(self._extract_sqrt_arguments(arg))
        return args

    def _extract_log_arguments(self, expr) -> List:
        """Extract arguments to logarithm functions."""
        args = []
        if expr.func == sp.log:
            args.append(expr.args[0])
        if hasattr(expr, "args"):
            for arg in expr.args:
                args.extend(self._extract_log_arguments(arg))
        return args

    def _extract_power_terms(self, expr) -> List[tuple]:
        """Extract (base, exponent) pairs from power operations."""
        terms = []
        if expr.is_Pow:
            terms.append((expr.args[0], expr.args[1]))
        if hasattr(expr, "args"):
            for arg in expr.args:
                terms.extend(self._extract_power_terms(arg))
        return terms

    def _could_overflow_power(self, base, exponent) -> bool:
        """Check if power operation could overflow."""
        # If exponent is > 10 or contains variables, flag it
        if exponent.is_Number:
            try:
                exp_val = float(exponent)
                if abs(exp_val) > 10:
                    return True
            except:
                pass
        # If exponent contains free symbols, flag it
        if exponent.free_symbols:
            return True
        return False

    def _guaranteed_positive(self, expr) -> bool:
        """Check if expression is guaranteed to be positive."""
        # If it's a positive number
        if expr.is_Number:
            try:
                return float(expr) > 0
            except:
                return False

        # If it's an absolute value
        if expr.func == sp.Abs:
            return True

        # If it's a square
        if expr.is_Pow and expr.args[1] == 2:
            return True

        # If it's wrapped in abs() or sqrt(x^2)
        expr_str = str(expr).lower()
        if "abs(" in expr_str:
            return True

        return False

    # Original helper methods (kept for compatibility)

    def _extract_denominators(self, expr) -> List:
        """Extract all denominators from expression."""
        denominators = []

        if expr.is_Mul:
            for arg in expr.args:
                if arg.is_Pow and arg.exp.is_negative:
                    denominators.append(arg.base)

        if expr.is_Add:
            for arg in expr.args:
                denominators.extend(self._extract_denominators(arg))

        if hasattr(expr, "args"):
            for arg in expr.args:
                denominators.extend(self._extract_denominators(arg))

        return denominators

    def _could_be_zero(self, expr) -> bool:
        """
        Check if expression could evaluate to zero.

        Enhanced: Recognize domain-specific safe patterns.
        """
        if expr.is_Number:
            return abs(float(expr)) < 1e-10

        # Check for sum of positive-only variables
        if expr.is_Add:
            # If all terms are known-positive variables, sum can't be zero
            all_positive = True
            has_variables = False

            for term in expr.args:
                if term.is_Symbol:
                    has_variables = True
                    var_name = str(term).lower()
                    # Known positive variable patterns
                    is_positive_var = any(
                        pattern in var_name
                        for pattern in [
                            "km",
                            "vmax",
                            "kcat",  # Biochemistry constants
                            "concentration",
                            "conc",  # Concentrations (≥0)
                            "price",
                            "liquidity",  # Finance (>0)
                            "amount",
                            "volume",  # Generally positive
                        ]
                    )
                    if not is_positive_var:
                        all_positive = False
                        break
                    elif term.is_Number and float(term) > 0:
                        has_variables = True
                        continue
                    elif not (term.is_Mul and any(arg.is_Symbol for arg in term.args)):
                        all_positive = False
                        break

            # If we have variables and all are known positive, sum can't be zero
            if has_variables and all_positive:
                return False

            # Otherwise, conservative: additions could cancel
            return True

        # Check for (1 + r) patterns where r could be -1
        expr_str = str(expr)
        if "+ r" in expr_str or "+ ratio" in expr_str:
            return True

        return False

    def _find_subtractions(self, expr) -> List:
        """Find all subtraction operations."""
        subs = []

        if expr.is_Add:
            neg_terms = [arg for arg in expr.args if arg.could_extract_minus_sign()]
            if len(neg_terms) > 0:
                subs.append(expr)

        if hasattr(expr, "args"):
            for arg in expr.args:
                subs.extend(self._find_subtractions(arg))

        return subs

    # Domain-specific validation rules (ENHANCED IN WEEK 2)

    def _defi_rules(self, expr, variable_definitions: Dict[str, str]) -> Dict[str, Any]:
        """
        ENHANCED WEEK 2: DeFi-specific validation rules.

        New checks:
        - Impermanent Loss ratio constraints (r > 0)
        - Price positivity requirements
        - Fee bounds (0 ≤ φ < 1)
        """
        errors = []
        warnings = []

        # WEEK 2 FIX: Check for IL formula with ratio variable
        expr_str = str(expr).lower()
        free_vars = [str(s).lower() for s in expr.free_symbols]

        # Check 1: Impermanent Loss ratio constraint
        if ("r" in free_vars or "ratio" in free_vars) and "sqrt" in expr_str:
            # Look for (1+r) in denominator - IL formula pattern
            if "1 + r" in expr_str or "(1+r)" in expr_str:
                errors.append(
                    "CRITICAL: Impermanent Loss formula requires r > 0. "
                    "Add constraint: if r ≤ 0, reject or use abs(r)"
                )

        # Check 2: Price positivity
        price_vars = [
            v for v in free_vars if "price" in v or "p_" in v or "p0" in v or "pt" in v
        ]
        if price_vars:
            warnings.append(
                f"Price variables {price_vars} must be positive. "
                f"Add validation: assert all(p > 0 for p in prices)"
            )

        # Check 3: Fee bounds
        if "fee" in free_vars or "phi" in free_vars or "φ" in expr_str:
            warnings.append(
                "Fee variable must satisfy 0 ≤ fee < 1. "
                "Add validation: assert 0 <= fee < 1"
            )

        # Check 4: Liquidity must be positive
        if "liquidity" in free_vars:
            warnings.append("Ensure liquidity is always positive")

        # Check 5: Price impact should be bounded
        if "price" in expr_str:
            warnings.append("Verify price bounds and slippage limits")

        # Check 6: x*y = k invariant considerations
        if expr.has(sp.Mul) and expr.has(sp.Pow):
            warnings.append("Check AMM constant product invariant preservation")

        return {"valid": len(errors) == 0, "errors": errors, "warnings": warnings}

    def _finance_rules(
        self, expr, variable_definitions: Dict[str, str]
    ) -> Dict[str, Any]:
        """Finance-specific validation rules."""
        errors = []
        warnings = []

        # Check for negative risk metrics
        if "risk" in str(expr).lower() or "var" in str(expr).lower():
            warnings.append("Risk metrics should be non-negative")

        # Check for return calculations
        if "return" in str(expr).lower():
            warnings.append("Verify return calculation methodology")

        # Check for probability constraints
        if "prob" in str(expr).lower():
            warnings.append("Ensure probabilities are in [0, 1]")

        return {"valid": len(errors) == 0, "errors": errors, "warnings": warnings}

    def _esg_rules(self, expr, variable_definitions: Dict[str, str]) -> Dict[str, Any]:
        """ESG-specific validation rules."""
        errors = []
        warnings = []

        # Check score ranges
        if "score" in str(expr).lower():
            warnings.append("Verify scores are in valid range (typically 0-100)")

        # Check weighting
        if expr.has(sp.Add):
            warnings.append("Ensure component weights sum appropriately")

        return {"valid": len(errors) == 0, "errors": errors, "warnings": warnings}

    def _risk_rules(self, expr, variable_definitions: Dict[str, str]) -> Dict[str, Any]:
        """Risk management validation rules."""
        errors = []
        warnings = []

        # Check VaR properties
        if "var" in str(expr).lower():
            warnings.append("VaR should be positive and bounded")

        # Check confidence levels
        if "confidence" in str(expr).lower():
            warnings.append("Confidence levels must be in (0, 1)")

        # Check for unbounded risk
        if expr.has(sp.oo):
            errors.append("Risk metric appears unbounded")

        return {"valid": len(errors) == 0, "errors": errors, "warnings": warnings}

    def _biology_rules(
        self, expr, variable_definitions: Dict[str, str]
    ) -> Dict[str, Any]:
        """
        Biology/biochemistry-specific validation rules.

        Known safe patterns:
        - Michaelis-Menten: Km + S is always positive (Km > 0, S ≥ 0)
        - Hill equation: Similar guarantees
        """
        errors = []
        warnings = []

        expr_str = str(expr).lower()
        free_vars = [str(s).lower() for s in expr.free_symbols]

        # Check for Michaelis-Menten pattern
        if ("km" in free_vars or "michaelis" in expr_str) and "s" in free_vars:
            # This is likely Michaelis-Menten kinetics
            # Km + S is ALWAYS positive (Km > 0 by definition, S ≥ 0)
            warnings.append(
                "Michaelis-Menten pattern detected. "
                "Ensure Km > 0 and S ≥ 0 (standard biochemistry constraints)"
            )

        # Check for concentration variables (must be non-negative)
        concentration_vars = [
            v
            for v in free_vars
            if any(term in v for term in ["concentration", "conc", "_c"])
        ]
        if concentration_vars:
            warnings.append(
                f"Concentration variables {concentration_vars} must be non-negative. "
                f"Validate input data: all concentrations ≥ 0"
            )

        # Check for rate constants (must be positive)
        rate_vars = [
            v
            for v in free_vars
            if any(term in v for term in ["vmax", "kcat", "kd", "ki", "rate"])
        ]
        if rate_vars:
            warnings.append(
                f"Rate/equilibrium constants {rate_vars} must be positive. "
                f"Validate input data: all constants > 0"
            )

        return {"valid": len(errors) == 0, "errors": errors, "warnings": warnings}

    def _default_rules(
        self, expr, variable_definitions: Dict[str, str]
    ) -> Dict[str, Any]:
        """Default validation rules."""
        return {"valid": True, "errors": [], "warnings": []}

    def _calculate_score(self, results: Dict[str, Any]) -> int:
        """Calculate overall validation score (0-100)."""
        score = 0

        # Base scores for passing each check
        if results["syntactically_valid"]:
            score += 25
        if results["dimensionally_consistent"]:
            score += 25
        if results["domain_valid"]:
            score += 25
        if results["numerically_stable"]:
            score += 25

        # WEEK 2 ENHANCEMENT: Harsher penalties for critical errors
        score -= len(results["errors"]) * 15  # Increased from 10
        score -= len(results.get("warnings", [])) * 2

        return max(0, min(100, score))

    # Utility methods for history management

    def clear_history(self):
        """Clear validation history."""
        if isinstance(self.validation_history, deque):
            self.validation_history.clear()
        else:
            self.validation_history = []

    def get_history(self, limit: Optional[int] = None) -> List[Dict]:
        """
        Get validation history.

        Args:
            limit: Maximum number of most recent validations to return

        Returns:
            List of validation result dictionaries
        """
        history_list = list(self.validation_history)
        if limit is not None:
            return history_list[-limit:]
        return history_list

    def get_statistics(self) -> Dict[str, Any]:
        """Get statistics about validation history."""
        if not self.validation_history:
            return {"total_validations": 0, "success_rate": 0.0, "average_score": 0.0}

        total = len(self.validation_history)
        valid_count = sum(1 for v in self.validation_history if v["valid"])
        avg_score = sum(v["score"] for v in self.validation_history) / total

        return {
            "total_validations": total,
            "success_rate": valid_count / total,
            "average_score": avg_score,
            "valid_count": valid_count,
            "invalid_count": total - valid_count,
        }


# Example usage
if __name__ == "__main__":
    validator = SymbolicValidator()

    print("=" * 80)
    print("WEEK 2 ENHANCED VALIDATION TESTS")
    print("=" * 80)

    # Test case 1: Empty expression (NEW WEEK 2)
    print("\n[TEST 1] Empty expression detection:")
    result1 = validator.validate(
        expression="", variable_definitions={}, domain="finance"
    )
    print(f"Valid: {result1['valid']}, Score: {result1['score']}")
    print(f"Errors: {result1['errors']}")

    # Test case 2: Division by zero without protection
    print("\n[TEST 2] Unprotected division by zero:")
    result2 = validator.validate(
        expression="sqrt(2*sqrt(r)/(1+r)) - 1",
        variable_definitions={"r": "Price ratio"},
        domain="defi",
    )
    print(f"Valid: {result2['valid']}, Score: {result2['score']}")
    print(f"Errors: {result2['errors']}")

    # Test case 3: Price without positivity constraint
    print("\n[TEST 3] Price positivity check:")
    result3 = validator.validate(
        expression="sqrt(abs(P_t - P_0))",
        variable_definitions={"P_t": "Current price", "P_0": "Initial price"},
        domain="defi",
    )
    print(f"Valid: {result3['valid']}, Score: {result3['score']}")
    print(f"Warnings: {result3['warnings']}")

    # Test case 4: Overflow risk detection
    print("\n[TEST 4] Overflow risk in exponential:")
    result4 = validator.validate(
        expression="exp(lambda_val * sigma**2)",
        variable_definitions={"lambda_val": "Sensitivity", "sigma": "Volatility"},
        domain="risk",
    )
    print(f"Valid: {result4['valid']}, Score: {result4['score']}")
    print(f"Warnings: {result4['warnings']}")

    # Get statistics
    print("\n" + "=" * 80)
    stats = validator.get_statistics()
    print(f"Validation statistics: {stats}")
    print("=" * 80)
