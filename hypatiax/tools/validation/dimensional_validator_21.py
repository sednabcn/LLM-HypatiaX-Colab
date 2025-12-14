"""
HypatiaX Dimensional Validator - COMPLETE FIX
tools/validation/dimensional_validator.py

ALL FIXES APPLIED:
1. USD unit registration
2. Division detection with variable name tracking
3. Nested exponentiation detection
4. sqrt/log domain warnings
5. Large base detection (multiple strategies) - FIXED for 1000**5
6. Multiplication penalty reduced to 5
7. Better duplicate detection for overflow risks
8. Only warn for division by variables, not constants
9. Conservative large base thresholds - UPDATED
10. Contextual zero-in-bounds warnings (only for division variables) - NEW
"""

import math
import re
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
    MAX_SAFE_VALUE = 1e308
    MIN_SAFE_VALUE = 1e-308
    MAX_SAFE_EXPONENT = 100
    EPSILON = 1e-10

    def __init__(self, max_history: Optional[int] = 1000):
        """Initialize the dimensional validator."""
        self.ureg = UnitRegistry()

        try:
            self.ureg.define("USD = [currency]")
        except:
            pass

        if max_history is not None:
            self.validation_history = deque(maxlen=max_history)
        else:
            self.validation_history = []

    def validate(
        self, expression_str: str, variable_units: Dict[str, str], variable_bounds: Optional[Dict[str, tuple]] = None
    ) -> Dict:
        """Validate dimensional consistency with numerical stability checks."""
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

        if not expression_str or not expression_str.strip():
            result["valid"] = False
            result["score"] = 0
            result["errors"].append("Empty or null expression provided")
            result["numerical_stability"]["stable"] = False
            self.validation_history.append(result)
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

            # Validate variable bounds if provided
            if variable_bounds:
                bounds_check = self._validate_bounds(variable_bounds, var_quantities)
                result["warnings"].extend(bounds_check["warnings"])
                result["errors"].extend(bounds_check["errors"])
                result["score"] -= bounds_check["penalty"]
                if bounds_check["errors"]:
                    result["valid"] = False

            try:
                # PRE-PARSE: Check for large base patterns in raw string
                # FIXED: Changed from \d{5,} to \d{3,} and threshold to catch 1000**5
                patterns = [
                    r"(\d{3,})\s*\*\*\s*(\d+)",
                    r"(\d{3,})\s*\^\s*(\d+)",
                    r"pow\s*\(\s*(\d{3,})\s*,\s*(\d+)\s*\)",
                ]

                for pattern in patterns:
                    match = re.search(pattern, expression_str, re.IGNORECASE)
                    if match:
                        try:
                            base_val = int(match.group(1))
                            exp_val = int(match.group(2))
                            # FIXED: Changed from base_val > 10000 to base_val >= 100
                            # and exp_val > 2 to exp_val >= 3
                            if base_val >= 100 and exp_val >= 3:
                                result["overflow_risks"].append(
                                    f"Large base {base_val} with exponent {exp_val} risks overflow"
                                )
                                result["warnings"].append(f"Expression {base_val}^{exp_val} may overflow")
                                result["score"] -= 10
                                break
                        except (ValueError, IndexError):
                            pass

                # Check for extremely large numbers
                large_num_pattern = r"\b(\d{13,})\b"
                large_nums = re.findall(large_num_pattern, expression_str)
                if large_nums and len(result["overflow_risks"]) == 0:  # Only if not already detected
                    for num_str in large_nums:
                        try:
                            num_val = int(num_str)
                            if num_val > 1e12:
                                result["overflow_risks"].append(
                                    f"Extremely large number {num_val} detected - overflow risk"
                                )
                                result["warnings"].append(f"Large number {num_val} may cause overflow")
                                result["score"] -= 10
                                break
                        except ValueError:
                            pass

                expr = sp.sympify(expression_str, evaluate=False)

                # Numerical stability check
                stability_check = self._check_numerical_stability(expr, var_quantities, variable_bounds)
                result["numerical_stability"] = stability_check
                result["overflow_risks"].extend(stability_check["overflow_risks"])
                result["warnings"].extend(stability_check["warnings"])
                result["errors"].extend(stability_check["errors"])
                result["score"] -= stability_check["penalty"]

                if not stability_check["stable"]:
                    result["valid"] = False

                # Dimensional consistency check
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

        result["score"] = max(0.0, min(100.0, result["score"]))

        if result["score"] < 30.0 and not result["errors"]:
            result["valid"] = False

        try:
            if isinstance(self.validation_history, deque):
                self.validation_history.append(result)
            else:
                self.validation_history.append(result)
        except Exception:
            pass

        return result

    def _validate_bounds(self, variable_bounds: Dict[str, tuple], var_quantities: Dict) -> Dict:
        """Validate that variable bounds are sensible."""
        errors = []
        warnings = []
        penalty = 0

        for var_name, bounds in variable_bounds.items():
            if not isinstance(bounds, (tuple, list)) or len(bounds) != 2:
                errors.append(f"Invalid bounds format for '{var_name}': expected (min, max) tuple")
                penalty += 20
                continue

            min_val, max_val = bounds

            if min_val > max_val:
                errors.append(f"Invalid bounds for '{var_name}': min ({min_val}) > max ({max_val})")
                penalty += 20

            # FIXED: Commented out blanket zero-in-bounds warning
            # Only warn about zero in bounds if there might be division involved
            # We'll check this contextually in numerical stability instead
            # if min_val <= 0 and max_val >= 0:
            #     warnings.append(
            #         f"Variable '{var_name}' bounds [{min_val}, {max_val}] include zero - "
            #         f"division by this variable is unsafe"
            #     )
            #     penalty += 5

            if abs(max_val) > self.MAX_SAFE_VALUE or abs(min_val) > self.MAX_SAFE_VALUE:
                warnings.append(f"Variable '{var_name}' has extremely large bounds - overflow risk")
                penalty += 5

        return {"errors": errors, "warnings": warnings, "penalty": penalty}

    def _check_numerical_stability(
        self, expr, var_quantities: Dict, variable_bounds: Optional[Dict[str, tuple]] = None
    ) -> Dict:
        """Check numerical stability of the expression."""
        result = {"stable": True, "issues": [], "overflow_risks": [], "warnings": [], "errors": [], "penalty": 0}

        # Check for multiplication of 2+ distinct variables
        multiplication_checked = False
        for arg in sp.preorder_traversal(expr):
            if isinstance(arg, sp.Mul) and not multiplication_checked:
                symbols_set = set()
                for factor in arg.args:
                    if isinstance(factor, sp.Symbol):
                        symbols_set.add(str(factor))

                if len(symbols_set) >= 2:
                    result["warnings"].append(f"Multiplication of variables detected - verify dimensional consistency")
                    result["penalty"] += 5
                    multiplication_checked = True
                    break

        # FIXED: Check for division by variables only - now tracks division variables
        division_variables = set()
        for arg in sp.preorder_traversal(expr):
            if isinstance(arg, sp.Pow) and arg.exp == -1:
                base = arg.base
                if isinstance(base, sp.Symbol):
                    var_name = str(base)
                    division_variables.add(var_name)

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
                        result["issues"].append(f"unconstrained_division_{var_name}")
                        result["penalty"] += 3

            elif isinstance(arg, sp.Rational) and arg.q == 0:
                result["errors"].append("Explicit division by zero detected")
                result["stable"] = False
                result["penalty"] += 50

        # NEW: Warn about zero in bounds only for variables that appear in division
        if variable_bounds and division_variables:
            for var_name in division_variables:
                if var_name in variable_bounds:
                    min_val, max_val = variable_bounds[var_name]
                    if (
                        min_val <= 0
                        and max_val >= 0
                        and not any(f"Division by '{var_name}'" in err for err in result["errors"])
                    ):
                        result["warnings"].append(
                            f"Variable '{var_name}' used in division has bounds [{min_val}, {max_val}] including zero"
                        )
                        result["penalty"] += 5

        try:
            if hasattr(expr, "as_numer_denom"):
                numer, denom = expr.as_numer_denom()
                if denom.is_Number and denom == 0:
                    result["errors"].append("Explicit division by zero (x/0) detected")
                    result["stable"] = False
                    result["penalty"] += 50
        except:
            pass

        # Check for exponentiation risks
        for arg in sp.preorder_traversal(expr):
            if isinstance(arg, sp.Pow):
                base, exp = arg.base, arg.exp

                if exp.is_Number:
                    try:
                        exp_val = float(exp)
                        if abs(exp_val) > self.MAX_SAFE_EXPONENT:
                            result["overflow_risks"].append(
                                f"Exponent {exp} exceeds safe limit ({self.MAX_SAFE_EXPONENT})"
                            )
                            result["errors"].append(f"Dangerous exponent {exp} will cause overflow")
                            result["stable"] = False
                            result["penalty"] += 41
                        elif abs(exp_val) > 50:
                            result["warnings"].append(f"Large exponent {exp} detected - verify bounds")
                            result["penalty"] += 5
                    except (ValueError, OverflowError):
                        pass

                if not exp.is_Number:
                    result["warnings"].append(
                        f"Variable exponent detected: {base}^{exp} - verify bounds to prevent overflow"
                    )
                    result["issues"].append("variable_exponent")
                    result["penalty"] += 5

                # Large base detection in parsed expression
                if base.is_Number:
                    try:
                        base_val = float(base)
                        if abs(base_val) > 10000 and exp.is_Number:
                            exp_val = float(exp)
                            if abs(exp_val) > 2:
                                risk_msg = f"Large base {int(base_val)} with exponent {int(exp_val)} risks overflow"
                                if risk_msg not in result["overflow_risks"]:
                                    result["overflow_risks"].append(risk_msg)
                                    result["warnings"].append(f"Expression {int(base_val)}^{int(exp_val)} may overflow")
                                    result["penalty"] += 10
                    except (ValueError, OverflowError, TypeError):
                        pass

        # Nested exponentiation detection
        for arg in sp.preorder_traversal(expr):
            if isinstance(arg, sp.Pow):
                if isinstance(arg.base, sp.Pow):
                    result["warnings"].append("Nested exponentiation detected - verify numerical stability")
                    result["issues"].append("nested_exponentiation")
                    result["penalty"] += 5
                    break
                if isinstance(arg.exp, sp.Pow):
                    result["warnings"].append("Nested exponentiation detected - verify numerical stability")
                    result["issues"].append("nested_exponentiation")
                    result["penalty"] += 5
                    break

        # Square root detection
        sqrt_found = False
        for arg in sp.preorder_traversal(expr):
            if arg.func == sp.sqrt or (isinstance(arg, sp.Pow) and arg.exp == sp.Rational(1, 2)):
                sqrt_found = True
                break

        if sqrt_found:
            result["warnings"].append("Square root detected - ensure all arguments are non-negative")
            result["issues"].append("sqrt_domain")
            result["penalty"] += 3

        # Logarithm detection
        log_found = False
        for arg in sp.preorder_traversal(expr):
            if arg.func in (sp.log, sp.ln):
                log_found = True
                break

        if log_found:
            result["warnings"].append("Logarithm detected - ensure all arguments are positive")
            result["issues"].append("logarithm_domain")
            result["penalty"] += 3

        return result

    def _check_operation_consistency(self, expr, var_quantities: Dict) -> Dict:
        """Check dimensional consistency of operations in the expression."""
        errors = []
        warnings = []
        penalty = 0

        if expr.is_Add:
            terms = expr.args
            term_units = []

            for term in terms:
                vars_in_term = [str(s) for s in term.free_symbols]

                if vars_in_term:
                    first_var = vars_in_term[0]
                    if first_var in var_quantities:
                        term_units.append((first_var, var_quantities[first_var]))
                else:
                    term_units.append(("constant", self.ureg.dimensionless))

            if len(term_units) > 1 and any(name != "constant" for name, _ in term_units):
                base_name, base_unit = term_units[0]
                for var_name, unit in term_units[1:]:
                    if not self._units_compatible(base_unit, unit):
                        if (
                            base_unit.dimensionality == self.ureg.dimensionless.dimensionality
                            and unit.dimensionality == self.ureg.dimensionless.dimensionality
                        ):
                            continue
                        errors.append(
                            f"Incompatible units in addition/subtraction: "
                            f"{base_unit.units} ({base_name}) vs {unit.units} ({var_name})"
                        )
                        penalty += 20

        if expr.is_Pow:
            base, exp = expr.args

            if not exp.is_Number:
                warnings.append("Non-numeric exponent - dimensional analysis limited")
                penalty += 3
            elif exp.is_Rational and exp.q != 1:
                warnings.append(f"Fractional exponent ({exp}) detected - verify dimensional correctness")
                penalty += 2

        for arg in sp.preorder_traversal(expr):
            if arg.func in (sp.log, sp.exp):
                func_args = arg.args
                for func_arg in func_args:
                    if func_arg.free_symbols:
                        warnings.append(f"Function {arg.func.__name__} requires dimensionless arguments")
                        penalty += 2
                        break

            if arg.func in (sp.sin, sp.cos, sp.tan):
                func_args = arg.args
                for func_arg in func_args:
                    if func_arg.free_symbols:
                        warnings.append(f"Trigonometric function requires angle (dimensionless) arguments")
                        penalty += 2
                        break

        return {"errors": errors, "warnings": warnings, "penalty": penalty}

    def _units_compatible(self, unit1, unit2) -> bool:
        """Check if two units are dimensionally compatible."""
        try:
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
        """Get validation history."""
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
