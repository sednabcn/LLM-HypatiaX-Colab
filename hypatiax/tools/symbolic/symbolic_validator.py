from typing import Dict, Optional, Tuple

import sympy as sp
from sympy.parsing.latex import parse_latex


class IntervalArithmetic:
    """
    Compute the range (min, max) of symbolic expressions given variable constraints.

    This enables the validator to understand that:
    - r ∈ [0.001, 100]  →  r + 1 ∈ [1.001, 101]  (never zero!)
    - x ∈ [5, 10]       →  x * 2 ∈ [10, 20]
    - etc.
    """

    EPSILON = 1e-10  # Safety threshold for division

    @staticmethod
    def compute_range(expr: sp.Expr, constraints: Dict[str, Dict[str, float]]) -> Tuple[float, float]:
        """
        Compute the min and max values an expression can take.

        Args:
            expr: SymPy expression (e.g., r + 1, x * y, etc.)
            constraints: {"var": {"min": value, "max": value}, ...}

        Returns:
            (min_value, max_value) tuple

        Examples:
            >>> constraints = {"r": {"min": 0.001, "max": 100}}
            >>> IntervalArithmetic.compute_range(sp.Symbol('r') + 1, constraints)
            (1.001, 101.0)
        """
        try:
            # If it's just a number, return it
            if expr.is_Number:
                val = float(expr)
                return (val, val)

            # If it's a single variable
            if expr.is_Symbol:
                var_name = str(expr)
                if var_name in constraints:
                    return (constraints[var_name]["min"], constraints[var_name]["max"])
                else:
                    # Unknown variable - can't determine range
                    return (-float("inf"), float("inf"))

            # Addition: [a_min, a_max] + [b_min, b_max] = [a_min+b_min, a_max+b_max]
            if isinstance(expr, sp.Add):
                min_sum = 0.0
                max_sum = 0.0
                for arg in expr.args:
                    arg_min, arg_max = IntervalArithmetic.compute_range(arg, constraints)
                    min_sum += arg_min
                    max_sum += arg_max
                return (min_sum, max_sum)

            # Multiplication: more complex due to sign changes
            if isinstance(expr, sp.Mul):
                # Start with first argument
                result_min, result_max = IntervalArithmetic.compute_range(expr.args[0], constraints)

                # Multiply by each subsequent argument
                for arg in expr.args[1:]:
                    arg_min, arg_max = IntervalArithmetic.compute_range(arg, constraints)

                    # Four possible products (consider sign changes)
                    products = [result_min * arg_min, result_min * arg_max, result_max * arg_min, result_max * arg_max]

                    result_min = min(products)
                    result_max = max(products)

                return (result_min, result_max)

            # Power: x^n
            if isinstance(expr, sp.Pow):
                base = expr.args[0]
                exponent = expr.args[1]

                base_min, base_max = IntervalArithmetic.compute_range(base, constraints)

                # If exponent is a constant
                if exponent.is_Number:
                    exp_val = float(exponent)

                    # Even exponent: always positive, take abs
                    if exp_val % 2 == 0:
                        if base_min >= 0:
                            return (base_min**exp_val, base_max**exp_val)
                        elif base_max <= 0:
                            return (abs(base_max) ** exp_val, abs(base_min) ** exp_val)
                        else:
                            # Crosses zero - minimum is 0
                            return (0, max(abs(base_min), abs(base_max)) ** exp_val)

                    # Odd exponent: preserves sign
                    else:
                        return (base_min**exp_val, base_max**exp_val)

            # Division: a/b
            if isinstance(expr, sp.Mul):
                # Check if any argument is 1/something
                numerator_min, numerator_max = (1.0, 1.0)
                denominator_min, denominator_max = (1.0, 1.0)

                for arg in expr.args:
                    if isinstance(arg, sp.Pow) and arg.args[1] == -1:
                        # This is 1/x
                        base = arg.args[0]
                        base_min, base_max = IntervalArithmetic.compute_range(base, constraints)
                        denominator_min *= base_min
                        denominator_max *= base_max
                    else:
                        arg_min, arg_max = IntervalArithmetic.compute_range(arg, constraints)
                        numerator_min *= arg_min
                        numerator_max *= arg_max

                # Compute division range (handle sign changes)
                if denominator_min > 0 or denominator_max < 0:
                    divisions = [
                        numerator_min / denominator_min,
                        numerator_min / denominator_max,
                        numerator_max / denominator_min,
                        numerator_max / denominator_max,
                    ]
                    return (min(divisions), max(divisions))

            # For other expressions, we can't determine range precisely
            # Return conservative estimate
            return (-float("inf"), float("inf"))

        except Exception as e:
            # If anything goes wrong, be conservative
            return (-float("inf"), float("inf"))

    @staticmethod
    def is_always_nonzero(expr: sp.Expr, constraints: Dict[str, Dict[str, float]]) -> bool:
        """
        Check if an expression is guaranteed to be non-zero.

        Returns True if:
        - min_value > EPSILON (always positive)
        - max_value < -EPSILON (always negative)

        Examples:
            >>> constraints = {"r": {"min": 0.001, "max": 100}}
            >>> IntervalArithmetic.is_always_nonzero(sp.Symbol('r') + 1, constraints)
            True  # Because r+1 ∈ [1.001, 101], never zero
        """
        min_val, max_val = IntervalArithmetic.compute_range(expr, constraints)

        # Check if always positive OR always negative
        return min_val > IntervalArithmetic.EPSILON or max_val < -IntervalArithmetic.EPSILON

    @staticmethod
    def has_epsilon_guard(expr: sp.Expr) -> bool:
        """
        Check if expression already contains an epsilon guard (e.g., 1e-10).

        Returns True if any term is a very small number like 1e-10, 1e-8, etc.
        """
        if isinstance(expr, sp.Add):
            for term in expr.args:
                if term.is_Number:
                    abs_val = abs(float(term))
                    # Check if it's a small epsilon-like value
                    if 1e-15 < abs_val < 1e-5:
                        return True
        return False


class FormulaValidator:
    """
    Validate generated formulas mathematically
    THIS IS WHERE YOUR PhD MATTERS
    """

    def __init__(self):
        self.domain_rules = {"finance": self._financial_rules, "defi": self._defi_rules, "esg": self._esg_rules}
        self.interval_arithmetic = IntervalArithmetic()
        self.errors = []
        self.warnings = []

    def validate(self, formula_latex, domain="finance", constraints=None):
        """
        Comprehensive validation

        Args:
            formula_latex: LaTeX formula string
            domain: Domain type ("finance", "defi", "esg")
            constraints: Dict of variable constraints {"var": {"min": x, "max": y}}
        """
        if constraints is None:
            constraints = {}

        results = {
            "syntactically_valid": False,
            "dimensionally_consistent": False,
            "domain_valid": False,
            "numerically_stable": False,
            "errors": [],
            "warnings": [],
        }

        # Reset instance error/warning lists
        self.errors = []
        self.warnings = []

        try:
            # 1. Parse LaTeX to SymPy
            expr = parse_latex(formula_latex)
            results["syntactically_valid"] = True

            # 2. Check dimensional consistency
            if self._check_dimensions(expr):
                results["dimensionally_consistent"] = True
            else:
                self.errors.append("Dimensional mismatch")

            # 3. Domain-specific rules
            domain_check = self.domain_rules[domain](expr)
            results["domain_valid"] = domain_check["valid"]
            self.errors.extend(domain_check["errors"])

            # 4. Numerical stability analysis with interval arithmetic
            self._check_division_by_zero(expr, constraints)
            stability = self._check_numerical_stability(expr)
            results["numerically_stable"] = len(self.errors) == 0
            self.warnings.extend(stability["warnings"])

        except Exception as e:
            self.errors.append(f"Parse error: {str(e)}")

        results["errors"] = self.errors
        results["warnings"] = self.warnings

        return results

    def _check_dimensions(self, expr):
        """
        Dimensional analysis
        Like checking units in physics
        """
        # Your implementation here
        # Check: price * price ≠ return
        # Check: volatility has correct units
        return True

    def _check_division_by_zero(self, expr: sp.Expr, constraints: Dict[str, Dict[str, float]]) -> None:
        """
        Enhanced division by zero detection using interval arithmetic.

        Now detects:
        1. Direct division by zero: 1/0
        2. Variables that could be zero: x/y where y ∈ [-1, 1]
        3. BUT ACCEPTS safe cases: r/(r+1) where r > 0
        4. Recognizes epsilon guards: x/(y + 1e-10)
        """
        # Find all division operations
        for sub_expr in sp.preorder_traversal(expr):
            if isinstance(sub_expr, sp.Mul):
                # Check each factor for negative exponents (division)
                for arg in sub_expr.args:
                    if isinstance(arg, sp.Pow) and arg.args[1] == -1:
                        # Found division: 1/denominator
                        denominator = arg.args[0]

                        # CASE 1: Direct division by zero
                        if denominator.is_Number and float(denominator) == 0:
                            self.errors.append(f"CRITICAL: Direct division by zero detected")
                            continue

                        # CASE 2: Check if denominator has epsilon guard
                        if self.interval_arithmetic.has_epsilon_guard(denominator):
                            # Has epsilon guard - safe!
                            self.warnings.append(f"Division by zero risk mitigated: {denominator}")
                            continue

                        # CASE 3: Use interval arithmetic to check if denominator can be zero
                        if self.interval_arithmetic.is_always_nonzero(denominator, constraints):
                            # Denominator is provably non-zero - safe!
                            # No warning needed
                            continue

                        # CASE 4: Denominator COULD be zero - flag it
                        self.errors.append(
                            f"CRITICAL: Unprotected division by zero risk: {denominator}. "
                            f"Add epsilon guard: (denominator + ε)"
                        )

    def _check_numerical_stability(self, expr):
        """
        YOUR COMPUTATIONAL MECHANICS EXPERTISE!

        Check:
        - Division by zero risks (now handled by _check_division_by_zero)
        - Overflow/underflow potential
        - Precision loss in operations
        - Conditioning of the problem
        """
        warnings = []

        # Check for subtractive cancellation
        # (a - b) where a ≈ b loses precision
        subtractions = self._find_subtractions(expr)
        for sub in subtractions:
            warnings.append(f"Potential precision loss: {sub}")

        # Check for exponentials (overflow risk)
        if expr.has(sp.exp):
            warnings.append("Exponential functions may overflow")

        return {"stable": len(warnings) == 0, "warnings": warnings}

    def _extract_denominators(self, expr):
        """Extract all denominators from an expression"""
        denominators = []
        for sub_expr in sp.preorder_traversal(expr):
            if isinstance(sub_expr, sp.Pow) and sub_expr.args[1] == -1:
                denominators.append(sub_expr.args[0])
        return denominators

    def _find_subtractions(self, expr):
        """Find all subtraction operations"""
        subtractions = []
        for sub_expr in sp.preorder_traversal(expr):
            if isinstance(sub_expr, sp.Add):
                # Check for negative terms (subtractions)
                for arg in sub_expr.args:
                    if isinstance(arg, sp.Mul) and any(
                        term.is_Number and float(term) < 0 for term in arg.args if term.is_Number
                    ):
                        subtractions.append(sub_expr)
                        break
        return subtractions

    def _financial_rules(self, expr):
        """
        Financial domain constraints
        """
        errors = []

        # Check: Risk metrics should be non-negative
        # Check: Returns should be percentage or decimal
        # Check: Probabilities sum to 1
        # Check: Weights in portfolio sum to 1

        return {"valid": len(errors) == 0, "errors": errors}

    def _defi_rules(self, expr):
        """
        DeFi-specific constraints
        """
        errors = []

        # Check: x*y = k invariant preservation
        # Check: Price impact must be positive
        # Check: Liquidity must be positive
        # Check: No arbitrage opportunities

        return {"valid": len(errors) == 0, "errors": errors}

    def _esg_rules(self, expr):
        """
        ESG scoring constraints
        """
        errors = []

        # Check: Scores in valid range (0-100 typical)
        # Check: Components properly weighted
        # Check: No negative environmental impact as positive

        return {"valid": len(errors) == 0, "errors": errors}
