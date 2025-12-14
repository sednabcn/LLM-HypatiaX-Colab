"""
HypatiaX Dimensional Validator - Enhanced Edition
tools/validation/dimensional_validator.py

UPDATES (Week 2, Day 1-2):
- Added numerical stability pre-checks
- Implemented bounds checking before operations
- Enhanced overflow detection for exponentials
- Added safe math validation
- PATCHED: Fixed division detection, bounds validation, operation consistency
"""

import math
from collections import deque
from typing import Dict, List, Optional

import sympy as sp
from pint import UnitRegistry


class DimensionalValidator:
    """
    Validates dimensional consistency of mathematical expressions.
    Enhanced with numerical stability checks and bounds validation.
    """

    # Numerical safety limits
    MAX_SAFE_VALUE = 1e308  # Near float64 max
    MIN_SAFE_VALUE = 1e-308  # Near float64 min
    MAX_SAFE_EXPONENT = 100
    EPSILON = 1e-10  # For near-zero checks

    def __init__(self, max_history: Optional[int] = 1000):
        """
        Initialize the dimensional validator.

        Args:
            max_history: Maximum number of validation results to keep.
        """
        self.ureg = UnitRegistry()

        # Bounded validation history
        if max_history is not None:
            self.validation_history = deque(maxlen=max_history)
        else:
            self.validation_history = []

    def validate(
        self, expression_str: str, variable_units: Dict[str, str], variable_bounds: Optional[Dict[str, tuple]] = None
    ) -> Dict:
        """
        Validate dimensional consistency with numerical stability checks.

        Args:
            expression_str: The mathematical expression
            variable_units: Dict mapping variable names to unit strings
                          e.g., {'price': 'USD', 'volume': 'USD**3'}
            variable_bounds: Optional dict mapping variables to (min, max) bounds
                           e.g., {'r': (0, float('inf')), 'fee': (0, 1)}

        Returns:
            {
                'valid': bool,
                'score': float,
                'errors': List[str],
                'warnings': List[str],
                'dimensionally_consistent': bool,
                'variable_dimensions': Dict,
                'numerical_stability': Dict,
                'overflow_risks': List[str]
            }
        """
        result = {
            "valid": True,
            "score": 100.0,
            "errors": [],
            "warnings": [],
            "dimensionally_consistent": True,
            "variable_dimensions": {},
            "numerical_stability": {"stable": True, "issues": []},
            "overflow_risks": [],
        }

        # CRITICAL: Empty expression check
        if not expression_str or not expression_str.strip():
            result["valid"] = False
            result["score"] = 0
            result["errors"].append("Empty or null expression provided")
            result["numerical_stability"]["stable"] = False
            return result

        try:
            # Parse units for each variable
            var_quantities = {}
            for var_name, unit_str in variable_units.items():
                try:
                    if unit_str.lower() in ["dimensionless", "none", ""]:
                        var_quantities[var_name] = self.ureg.dimensionless
                        result["variable_dimensions"][var_name] = "dimensionless"
                    else:
                        quantity = self.ureg(unit_str)
                        var_quantities[var_name] = quantity
                        result["variable_dimensions"][var_name] = str(quantity.units)
                except Exception as e:
                    result["errors"].append(f"Invalid unit for '{var_name}': '{unit_str}' - {str(e)}")
                    result["score"] -= 15
                    result["valid"] = False

            # NEW: Validate variable bounds if provided
            if variable_bounds:
                bounds_check = self._validate_bounds(variable_bounds, var_quantities)
                result["warnings"].extend(bounds_check["warnings"])
                result["errors"].extend(bounds_check["errors"])
                result["score"] -= bounds_check["penalty"]
                if bounds_check["errors"]:
                    result["valid"] = False

            # Parse expression to SymPy for structural analysis
            try:
                expr = sp.sympify(expression_str)

                # NEW: Numerical stability pre-check
                stability_check = self._check_numerical_stability(expr, var_quantities, variable_bounds)
                result["numerical_stability"] = stability_check
                result["overflow_risks"] = stability_check["overflow_risks"]
                result["warnings"].extend(stability_check["warnings"])
                result["errors"].extend(stability_check["errors"])
                result["score"] -= stability_check["penalty"]

                if not stability_check["stable"]:
                    result["valid"] = False

                # Check dimensional consistency of operations
                consistency_check = self._check_operation_consistency(expr, var_quantities)

                result["errors"].extend(consistency_check["errors"])
                result["warnings"].extend(consistency_check["warnings"])
                result["score"] -= consistency_check["penalty"]

                if consistency_check["errors"]:
                    result["valid"] = False
                    result["dimensionally_consistent"] = False

            except Exception as e:
                result["warnings"].append(f"Could not parse expression for dimensional analysis: {str(e)}")
                result["score"] -= 10

        except Exception as e:
            result["valid"] = False
            result["score"] = 0
            result["errors"].append(f"Dimensional validation error: {str(e)}")

        # FIXED: Ensure score is bounded and check validity threshold
        result["score"] = max(0.0, min(100.0, result["score"]))

        # If score drops below threshold, mark as invalid
        if result["score"] < 50.0 and not result["errors"]:
            result["valid"] = False

        # Store in history
        self.validation_history.append(result)
        return result

    def _validate_bounds(self, variable_bounds: Dict[str, tuple], var_quantities: Dict) -> Dict:
        """
        Validate that variable bounds are sensible.

        Returns:
            Dict with 'errors', 'warnings', and 'penalty'
        """
        errors = []
        warnings = []
        penalty = 0

        for var_name, bounds in variable_bounds.items():
            if not isinstance(bounds, (tuple, list)) or len(bounds) != 2:
                errors.append(f"Invalid bounds format for '{var_name}': expected (min, max) tuple")
                penalty += 20
                continue

            min_val, max_val = bounds

            # Check for invalid bounds
            if min_val > max_val:
                errors.append(f"Invalid bounds for '{var_name}': min ({min_val}) > max ({max_val})")
                penalty += 20

            # Check for division-by-zero risk
            if min_val <= 0 and max_val >= 0:
                warnings.append(
                    f"Variable '{var_name}' bounds [{min_val}, {max_val}] include zero - "
                    f"division by this variable is unsafe"
                )
                penalty += 10

            # Check for overflow risk with large bounds
            if abs(max_val) > self.MAX_SAFE_VALUE or abs(min_val) > self.MAX_SAFE_VALUE:
                warnings.append(f"Variable '{var_name}' has extremely large bounds - overflow risk")
                penalty += 5

        return {"errors": errors, "warnings": warnings, "penalty": penalty}

    def _check_numerical_stability(
        self, expr, var_quantities: Dict, variable_bounds: Optional[Dict[str, tuple]] = None
    ) -> Dict:
        """
        Check numerical stability of the expression.

        Returns:
            Dict with stability info, overflow risks, warnings, errors, penalty
        """
        result = {"stable": True, "issues": [], "overflow_risks": [], "warnings": [], "errors": [], "penalty": 0}

        # FIXED: Check for division operations - improved detection
        for arg in sp.preorder_traversal(expr):
            # Check for division (1/x pattern)
            if isinstance(arg, sp.Pow) and arg.exp == -1:
                base = arg.base
                if isinstance(base, sp.Symbol):
                    var_name = str(base)

                    # Check if variable can be zero
                    if variable_bounds and var_name in variable_bounds:
                        min_val, max_val = variable_bounds[var_name]
                        if min_val <= self.EPSILON and max_val >= -self.EPSILON:
                            result["errors"].append(
                                f"Division by '{var_name}' detected, but bounds "
                                f"[{min_val}, {max_val}] include zero - CRITICAL RISK"
                            )
                            result["stable"] = False
                            result["penalty"] += 30
                    else:
                        result["warnings"].append(f"Division by '{var_name}' detected - ensure {var_name} ≠ 0")
                        result["issues"].append(f"unconstrained_division")
                        result["penalty"] += 5  # Reduced penalty for warnings

            # Check for explicit Rational with zero denominator
            elif isinstance(arg, sp.Rational) and arg.q == 0:
                result["errors"].append("Explicit division by zero detected")
                result["stable"] = False
                result["penalty"] += 50

        # Check for exponentiation with overflow risk
        for arg in sp.preorder_traversal(expr):
            if isinstance(arg, sp.Pow):
                base, exp = arg.base, arg.exp

                # Check for large constant exponents
                if exp.is_Number:
                    try:
                        exp_val = float(exp)
                        if abs(exp_val) > self.MAX_SAFE_EXPONENT:
                            result["overflow_risks"].append(
                                f"Exponent {exp} exceeds safe limit ({self.MAX_SAFE_EXPONENT})"
                            )
                            result["errors"].append(f"Dangerous exponent {exp} will cause overflow")
                            result["stable"] = False
                            result["penalty"] += 40
                    except (ValueError, OverflowError):
                        pass

                # Check for variable exponents (harder to bound)
                if not exp.is_Number:
                    result["warnings"].append(
                        f"Variable exponent detected: {base}^{exp} - verify bounds to prevent overflow"
                    )
                    result["issues"].append("variable_exponent")
                    result["penalty"] += 10

                # Check for large bases with exponents
                if base.is_Number:
                    try:
                        base_val = float(base)
                        if abs(base_val) > 1000 and exp.is_Number:
                            exp_val = float(exp)
                            if abs(exp_val) > 2:
                                result["overflow_risks"].append(f"Large base {base} with exponent {exp} risks overflow")
                                result["warnings"].append(f"Expression {base}^{exp} may overflow")
                                result["penalty"] += 15
                    except (ValueError, OverflowError):
                        pass

        # Check for nested exponentials (extremely dangerous)
        pow_nodes = [arg for arg in sp.preorder_traversal(expr) if isinstance(arg, sp.Pow)]
        nested_count = 0
        for pow_node in pow_nodes:
            # Check if base or exponent contains another Pow
            if pow_node.base.has(sp.Pow) or pow_node.exp.has(sp.Pow):
                nested_count += 1

        if nested_count > 0:
            result["warnings"].append(f"Nested exponentiation detected - verify numerical stability")
            result["issues"].append("nested_exponentiation")
            result["penalty"] += 5 * nested_count

        # Check for logarithms
        if expr.has(sp.log):
            result["warnings"].append("Logarithm detected - ensure all arguments are positive")
            result["issues"].append("logarithm_domain")
            result["penalty"] += 5

        # Check for square roots
        if expr.has(sp.sqrt):
            result["warnings"].append("Square root detected - ensure all arguments are non-negative")
            result["issues"].append("sqrt_domain")
            result["penalty"] += 5

        return result

    def _check_operation_consistency(self, expr, var_quantities: Dict) -> Dict:
        """
        Check dimensional consistency of operations in the expression.

        Returns:
            Dict with 'errors', 'warnings', and 'penalty'
        """
        errors = []
        warnings = []
        penalty = 0

        # FIXED: Check additions and subtractions with better handling
        if expr.is_Add:
            terms = expr.args
            term_units = []

            for term in terms:
                vars_in_term = [str(s) for s in term.free_symbols]

                # Get representative unit for this term
                if vars_in_term:
                    first_var = vars_in_term[0]
                    if first_var in var_quantities:
                        term_units.append((first_var, var_quantities[first_var]))
                else:
                    # Constant term - considered dimensionless
                    term_units.append(("constant", self.ureg.dimensionless))

            # Check if all terms have compatible dimensions
            if len(term_units) > 1:
                base_name, base_unit = term_units[0]
                for var_name, unit in term_units[1:]:
                    if not self._units_compatible(base_unit, unit):
                        errors.append(
                            f"Incompatible units in addition/subtraction: "
                            f"{base_unit.units} ({base_name}) vs {unit.units} ({var_name})"
                        )
                        penalty += 20

        # FIXED: Check multiplications - just a warning
        if expr.is_Mul:
            # Only warn if it's not trivial multiplication
            if len(expr.args) > 1:
                pass  # Multiplication is usually fine, dimensions multiply

        # Check powers
        if expr.is_Pow:
            base, exp = expr.args

            # If exponent is not a number, it's problematic for dimensional analysis
            if not exp.is_Number:
                warnings.append("Non-numeric exponent - dimensional analysis limited")
                penalty += 5
            elif exp.is_Rational and exp.q != 1:
                # Fractional exponent
                pass  # This is fine, just a note

        # FIXED: Check functions that require dimensionless arguments
        for arg in sp.preorder_traversal(expr):
            if arg.func in (sp.log, sp.exp):
                # These require dimensionless arguments
                func_args = arg.args
                for func_arg in func_args:
                    if func_arg.free_symbols:
                        warnings.append(f"Function {arg.func.__name__} requires dimensionless arguments")
                        penalty += 3
                        break

            if arg.func in (sp.sin, sp.cos, sp.tan):
                # These require dimensionless (angle) arguments
                func_args = arg.args
                for func_arg in func_args:
                    if func_arg.free_symbols:
                        warnings.append(f"Trigonometric function requires angle (dimensionless) arguments")
                        penalty += 3
                        break

        return {"errors": errors, "warnings": warnings, "penalty": penalty}

    def _units_compatible(self, unit1, unit2) -> bool:
        """Check if two units are dimensionally compatible."""
        try:
            # Try to convert unit2 to unit1
            test_quantity = 1 * unit2
            test_quantity.to(unit1)
            return True
        except Exception:
            return False

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

    def get_statistics(self) -> Dict:
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


# Example usage with enhanced features
if __name__ == "__main__":
    validator = DimensionalValidator()

    print("=" * 80)
    print("ENHANCED DIMENSIONAL VALIDATOR - NUMERICAL STABILITY TESTS")
    print("=" * 80)
    print()

    # Test case 1: Compatible units (PASS)
    print("Test 1: Compatible units addition")
    result1 = validator.validate(
        expression_str="price1 + price2",
        variable_units={"price1": "USD", "price2": "USD"},
        variable_bounds={"price1": (0, 10000), "price2": (0, 10000)},
    )
    print(f"Valid: {result1['valid']}, Score: {result1['score']}")
    print(f"Numerically Stable: {result1['numerical_stability']['stable']}")
    print()

    # Test case 2: Incompatible units (FAIL)
    print("Test 2: Incompatible units")
    result2 = validator.validate(expression_str="price + volume", variable_units={"price": "USD", "volume": "USD**3"})
    print(f"Valid: {result2['valid']}, Score: {result2['score']}")
    print(f"Errors: {result2['errors']}")
    print()

    # Test case 3: Division by zero risk (CRITICAL)
    print("Test 3: Division by zero risk")
    result3 = validator.validate(
        expression_str="price / quantity",
        variable_units={"price": "USD", "quantity": "dimensionless"},
        variable_bounds={"price": (0, 1000), "quantity": (-1, 1)},  # Includes zero!
    )
    print(f"Valid: {result3['valid']}, Score: {result3['score']}")
    print(f"Errors: {result3['errors']}")
    print(f"Numerically Stable: {result3['numerical_stability']['stable']}")
    print()

    # Test case 4: Empty expression (CRITICAL)
    print("Test 4: Empty expression")
    result4 = validator.validate(expression_str="", variable_units={})
    print(f"Valid: {result4['valid']}, Score: {result4['score']}")
    print(f"Errors: {result4['errors']}")
    print()

    # Test case 5: Overflow risk from large exponent
    print("Test 5: Large exponent overflow risk")
    result5 = validator.validate(
        expression_str="x**150", variable_units={"x": "dimensionless"}, variable_bounds={"x": (1, 10)}
    )
    print(f"Valid: {result5['valid']}, Score: {result5['score']}")
    print(f"Overflow Risks: {result5['overflow_risks']}")
    print(f"Numerically Stable: {result5['numerical_stability']['stable']}")
    print()

    # Get statistics
    stats = validator.get_statistics()
    print("=" * 80)
    print(f"STATISTICS")
    print(f"  Total Validations: {stats['total_validations']}")
    print(f"  Success Rate: {stats['success_rate']*100:.1f}%")
    print(f"  Average Score: {stats['average_score']:.2f}")
    print("=" * 80)

"""
Major Fixes Applied:

Improved Division Detection (_check_numerical_stability):

Better detection of division operations using sp.Pow with exp == -1
Reduced penalty for warnings (5 instead of 15) vs errors (30)
Added check for explicit sp.Rational with zero denominator


Enhanced Bounds Validation (_validate_bounds):

Added format validation for bounds (tuple/list with 2 elements)
Better error messages with variable names
Proper handling of edge cases


Better Operation Consistency (_check_operation_consistency):

Improved addition/subtraction checks with better variable tracking
Removed excessive warnings for multiplication (usually fine)
More targeted warnings for functions requiring dimensionless arguments
Reduced penalties for non-critical warnings (3 instead of 5)


Score Calculation (in validate method):

Added score bounding: max(0.0, min(100.0, result["score"]))
Added validity threshold check: marks as invalid if score < 50 without errors


Nested Exponentiation Detection:

Improved detection to check if base or exponent contains sp.Pow
More accurate counting and penalty assessment



These changes make the validator more robust, with better error detection, more appropriate penalty assignments, and clearer distinction between critical errors and warnings.

"""
