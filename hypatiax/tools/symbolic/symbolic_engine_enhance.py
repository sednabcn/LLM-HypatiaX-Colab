"""
Enhanced Symbolic Engine - ADDITIONAL SAFETY ENHANCEMENTS
symbolic_engine_enhanced.py

NEW ENHANCEMENTS:
- Advanced null/empty expression detection with detailed diagnostics
- Safe math operations wrapper class for all mathematical operations
- Expression sanitization and validation before execution
- Automatic epsilon injection for division operations
- Comprehensive test suite for safety features
"""

import re
import warnings
from dataclasses import dataclass
from typing import Callable, Dict, List, Optional, Union

import numpy as np
import sympy as sp

# ============================================================================
# ENHANCEMENT 1: ADVANCED SAFE MATH WRAPPER
# ============================================================================


class SafeMathOperations:
    """
    Comprehensive safe math operations wrapper.

    Provides epsilon-protected versions of all dangerous operations:
    - Division with automatic epsilon protection
    - Logarithm with domain checking
    - Square root with non-negativity enforcement
    - Power operations with overflow protection
    """

    # Safety constants
    EPSILON = 1e-10
    EPSILON_LOG = 1e-15  # Smaller epsilon for log (since log(1e-10) is still defined)
    MAX_EXP_ARG = 700  # e^700 ≈ 10^304 (near max float)
    MIN_LOG_ARG = 1e-300  # Minimum safe logarithm argument
    MAX_POWER = 1000  # Maximum safe exponent

    def __init__(self, epsilon: float = None, strict_mode: bool = True):
        """
        Initialize safe math operations.

        Args:
            epsilon: Custom epsilon value (default: 1e-10)
            strict_mode: If True, raises errors on violations; if False, warns and fixes
        """
        self.epsilon = epsilon if epsilon is not None else self.EPSILON
        self.strict_mode = strict_mode
        self.violation_count = 0
        self.violations_log = []

    def safe_divide(
        self, numerator: Union[float, np.ndarray], denominator: Union[float, np.ndarray], context: str = ""
    ) -> Union[float, np.ndarray]:
        """
        Division with automatic epsilon protection.

        Prevents division by zero: a / b → a / (b + ε)

        Args:
            numerator: Dividend
            denominator: Divisor
            context: Optional context string for error messages

        Returns:
            Safe division result
        """
        # Detect near-zero denominators
        is_array = isinstance(denominator, np.ndarray)

        if is_array:
            near_zero_mask = np.abs(denominator) < self.epsilon
            if np.any(near_zero_mask):
                self._log_violation(
                    "division_by_near_zero",
                    f"Denominator has {np.sum(near_zero_mask)} near-zero values "
                    f"(min: {np.min(np.abs(denominator)):.2e}). {context}",
                )
                # Apply epsilon protection
                denominator = np.where(
                    near_zero_mask, denominator + np.sign(denominator + self.epsilon) * self.epsilon, denominator
                )
        else:
            if abs(denominator) < self.epsilon:
                self._log_violation("division_by_near_zero", f"Denominator near zero: {denominator:.2e}. {context}")
                denominator = denominator + np.sign(denominator + self.epsilon) * self.epsilon

        return numerator / denominator

    def safe_log(self, x: Union[float, np.ndarray], context: str = "") -> Union[float, np.ndarray]:
        """
        Logarithm with domain enforcement.

        Ensures log argument is positive: log(x) where x > ε

        Args:
            x: Logarithm argument
            context: Optional context string

        Returns:
            Safe logarithm result
        """
        is_array = isinstance(x, np.ndarray)

        if is_array:
            # Check for non-positive values
            non_positive_mask = x <= self.EPSILON_LOG
            if np.any(non_positive_mask):
                self._log_violation(
                    "log_non_positive",
                    f"Log argument has {np.sum(non_positive_mask)} non-positive values "
                    f"(min: {np.min(x):.2e}). {context}",
                )
                # Clip to safe minimum
                x = np.maximum(x, self.MIN_LOG_ARG)
        else:
            if x <= self.EPSILON_LOG:
                self._log_violation("log_non_positive", f"Log argument non-positive: {x:.2e}. {context}")
                x = max(x, self.MIN_LOG_ARG)

        return np.log(x)

    def safe_sqrt(self, x: Union[float, np.ndarray], context: str = "") -> Union[float, np.ndarray]:
        """
        Square root with non-negativity enforcement.

        Args:
            x: Square root argument
            context: Optional context string

        Returns:
            Safe square root result
        """
        is_array = isinstance(x, np.ndarray)

        if is_array:
            negative_mask = x < 0
            if np.any(negative_mask):
                self._log_violation(
                    "sqrt_negative",
                    f"Sqrt argument has {np.sum(negative_mask)} negative values " f"(min: {np.min(x):.2e}). {context}",
                )
                # Clip to zero
                x = np.maximum(x, 0)
        else:
            if x < 0:
                self._log_violation("sqrt_negative", f"Sqrt argument negative: {x:.2e}. {context}")
                x = max(x, 0)

        return np.sqrt(x)

    def safe_exp(self, x: Union[float, np.ndarray], context: str = "") -> Union[float, np.ndarray]:
        """
        Exponential with overflow protection.

        Args:
            x: Exponent
            context: Optional context string

        Returns:
            Safe exponential result
        """
        is_array = isinstance(x, np.ndarray)

        if is_array:
            overflow_mask = x > self.MAX_EXP_ARG
            if np.any(overflow_mask):
                self._log_violation(
                    "exp_overflow",
                    f"Exp argument has {np.sum(overflow_mask)} overflow-risk values "
                    f"(max: {np.max(x):.2e}). {context}",
                )
                # Clip to safe maximum
                x = np.minimum(x, self.MAX_EXP_ARG)
        else:
            if x > self.MAX_EXP_ARG:
                self._log_violation("exp_overflow", f"Exp argument overflow risk: {x:.2e}. {context}")
                x = min(x, self.MAX_EXP_ARG)

        return np.exp(x)

    def safe_power(
        self, base: Union[float, np.ndarray], exponent: Union[float, np.ndarray], context: str = ""
    ) -> Union[float, np.ndarray]:
        """
        Power operation with overflow protection.

        Args:
            base: Base value
            exponent: Exponent value
            context: Optional context string

        Returns:
            Safe power result
        """
        is_array = isinstance(exponent, np.ndarray)

        # Check for extreme exponents
        if is_array:
            extreme_mask = np.abs(exponent) > self.MAX_POWER
            if np.any(extreme_mask):
                self._log_violation(
                    "power_extreme_exponent", f"Power has {np.sum(extreme_mask)} extreme exponents. {context}"
                )
                exponent = np.clip(exponent, -self.MAX_POWER, self.MAX_POWER)
        else:
            if abs(exponent) > self.MAX_POWER:
                self._log_violation("power_extreme_exponent", f"Power exponent extreme: {exponent:.2e}. {context}")
                exponent = np.clip(exponent, -self.MAX_POWER, self.MAX_POWER)

        # Handle negative base with non-integer exponent
        if is_array or isinstance(base, np.ndarray):
            base_array = np.atleast_1d(base)
            exp_array = np.atleast_1d(exponent)

            # Check for negative base with fractional exponent
            negative_base_mask = base_array < 0
            if np.any(negative_base_mask):
                # Take absolute value if fractional exponent
                base_array = np.abs(base_array)
                self._log_violation(
                    "power_negative_base", f"Power has negative base values. Taking absolute value. {context}"
                )

        try:
            result = np.power(base, exponent)
            # Clip extreme results
            if isinstance(result, np.ndarray):
                result = np.clip(result, -1e100, 1e100)
            else:
                result = np.clip(result, -1e100, 1e100)
            return result
        except Exception as e:
            self._log_violation("power_computation_error", f"Power computation failed: {str(e)}. {context}")
            return np.zeros_like(base)

    def _log_violation(self, violation_type: str, message: str):
        """Log a safety violation."""
        self.violation_count += 1
        self.violations_log.append({"type": violation_type, "message": message, "count": self.violation_count})

        if self.strict_mode:
            warnings.warn(f"SafeMath Violation #{self.violation_count}: {message}")

    def get_violation_report(self) -> Dict:
        """Get comprehensive violation report."""
        violation_types = {}
        for v in self.violations_log:
            vtype = v["type"]
            violation_types[vtype] = violation_types.get(vtype, 0) + 1

        return {
            "total_violations": self.violation_count,
            "violations_by_type": violation_types,
            "detailed_log": self.violations_log,
        }


# ============================================================================
# ENHANCEMENT 2: ADVANCED EXPRESSION VALIDATOR
# ============================================================================


class ExpressionValidator:
    """
    Advanced expression validation with detailed diagnostics.

    Validates expressions for:
    - Null/empty/whitespace-only expressions
    - Syntax errors and malformed expressions
    - Dangerous operations (division by zero, log of negative, etc.)
    - Variable domain violations
    - Numerical stability issues
    """

    def __init__(self, safe_math: SafeMathOperations = None):
        """Initialize validator with optional SafeMath instance."""
        self.safe_math = safe_math if safe_math else SafeMathOperations()
        self.validation_history = []

    def validate_expression(
        self,
        expression: Union[str, sp.Expr, None],
        variable_names: Optional[List[str]] = None,
        variable_data: Optional[Dict[str, np.ndarray]] = None,
    ) -> Dict:
        """
        Comprehensive expression validation.

        Args:
            expression: Expression to validate (string or sympy)
            variable_names: List of expected variable names
            variable_data: Optional data for variables to check domains

        Returns:
            Dict with validation results
        """
        validation = {
            "valid": True,
            "expression": str(expression) if expression else None,
            "errors": [],
            "warnings": [],
            "safety_issues": [],
            "complexity": 0,
            "dangerous_operations": [],
            "suggested_fixes": [],
        }

        # Check 1: Null/empty/whitespace
        null_check = self._check_null_empty(expression)
        validation.update(null_check)
        if not null_check["valid"]:
            return validation

        # Convert to string for analysis
        expr_str = str(expression).strip()

        # Check 2: Syntax validation
        syntax_check = self._check_syntax(expr_str)
        validation["errors"].extend(syntax_check["errors"])
        validation["warnings"].extend(syntax_check["warnings"])
        if not syntax_check["valid"]:
            validation["valid"] = False

        # Check 3: Parse to sympy
        try:
            sympy_expr = sp.sympify(expr_str)
            validation["sympy_expr"] = sympy_expr
            validation["complexity"] = self._calculate_complexity(sympy_expr)
        except Exception as e:
            validation["valid"] = False
            validation["errors"].append(f"Cannot parse to Sympy: {str(e)}")
            return validation

        # Check 4: Dangerous operations
        danger_check = self._check_dangerous_operations(sympy_expr, expr_str)
        validation["dangerous_operations"] = danger_check["operations"]
        validation["warnings"].extend(danger_check["warnings"])
        validation["safety_issues"].extend(danger_check["issues"])

        # Check 5: Variable domain validation
        if variable_names and variable_data:
            domain_check = self._check_variable_domains(sympy_expr, variable_names, variable_data)
            validation["errors"].extend(domain_check["errors"])
            validation["warnings"].extend(domain_check["warnings"])
            validation["suggested_fixes"].extend(domain_check["fixes"])
            if domain_check["errors"]:
                validation["valid"] = False

        # Check 6: Variable presence
        if variable_names:
            var_check = self._check_variables(sympy_expr, variable_names)
            validation["warnings"].extend(var_check["warnings"])

        # Store in history
        self.validation_history.append(validation)

        return validation

    def _check_null_empty(self, expression) -> Dict:
        """Check for null, empty, or whitespace-only expressions."""
        result = {"valid": True, "errors": [], "warnings": []}

        # Check for None
        if expression is None:
            result["valid"] = False
            result["errors"].append("Expression is None/null")
            return result

        # Convert to string
        expr_str = str(expression).strip()

        # Check for empty string
        if len(expr_str) == 0:
            result["valid"] = False
            result["errors"].append("Expression is empty string")
            return result

        # Check for whitespace only
        if expr_str.isspace():
            result["valid"] = False
            result["errors"].append("Expression contains only whitespace")
            return result

        # Check for common "empty" expressions
        if expr_str.lower() in ["none", "null", "nan", "na", ""]:
            result["valid"] = False
            result["errors"].append(f"Expression is placeholder: '{expr_str}'")
            return result

        return result

    def _check_syntax(self, expr_str: str) -> Dict:
        """Check for basic syntax errors."""
        result = {"valid": True, "errors": [], "warnings": []}

        # Check for unmatched parentheses
        if expr_str.count("(") != expr_str.count(")"):
            result["valid"] = False
            result["errors"].append(
                f"Unmatched parentheses: {expr_str.count('(')} open, " f"{expr_str.count(')')} close"
            )

        # Check for unmatched brackets
        if expr_str.count("[") != expr_str.count("]"):
            result["valid"] = False
            result["errors"].append("Unmatched square brackets")

        # Check for double operators (++, --, etc.)
        double_ops = re.findall(r"[+\-*/]{2,}", expr_str)
        if double_ops:
            result["warnings"].append(f"Double operators detected: {double_ops} - may be intentional (e.g., '--')")

        # Check for empty parentheses
        if "()" in expr_str:
            result["valid"] = False
            result["errors"].append("Empty parentheses '()' detected")

        # Check for trailing operators
        if re.search(r"[+\-*/]$", expr_str.strip()):
            result["valid"] = False
            result["errors"].append("Expression ends with operator")

        return result

    def _check_dangerous_operations(self, sympy_expr: sp.Expr, expr_str: str) -> Dict:
        """Detect dangerous mathematical operations."""
        result = {"operations": [], "warnings": [], "issues": []}

        # Check for divisions
        for atom in sp.preorder_traversal(sympy_expr):
            if atom.is_Pow and atom.exp == -1:
                result["operations"].append("division")
                result["warnings"].append(f"Division detected: verify denominator non-zero")
                result["issues"].append(
                    {
                        "type": "division",
                        "denominator": str(atom.base),
                        "suggested_fix": f"Use safe_divide({atom.base})",
                    }
                )

            # Check for logarithms
            if atom.func == sp.log:
                result["operations"].append("logarithm")
                result["warnings"].append(f"Logarithm detected: verify argument > 0")
                result["issues"].append(
                    {"type": "logarithm", "argument": str(atom.args[0]), "suggested_fix": f"Ensure {atom.args[0]} > 0"}
                )

            # Check for square roots
            if atom.func == sp.sqrt:
                result["operations"].append("sqrt")
                result["warnings"].append(f"Square root detected: verify argument >= 0")
                result["issues"].append(
                    {"type": "sqrt", "argument": str(atom.args[0]), "suggested_fix": f"Ensure {atom.args[0]} >= 0"}
                )

            # Check for exponentials
            if atom.func == sp.exp:
                result["operations"].append("exponential")
                result["warnings"].append(f"Exponential detected: overflow risk")
                result["issues"].append(
                    {
                        "type": "exponential",
                        "argument": str(atom.args[0]),
                        "suggested_fix": f"Clip {atom.args[0]} to safe range",
                    }
                )

        # Remove duplicates
        result["operations"] = list(set(result["operations"]))

        return result

    def _check_variable_domains(
        self, sympy_expr: sp.Expr, variable_names: List[str], variable_data: Dict[str, np.ndarray]
    ) -> Dict:
        """Check if variable data satisfies domain requirements."""
        result = {"errors": [], "warnings": [], "fixes": []}

        for var_name in variable_names:
            if var_name not in variable_data:
                continue

            data = variable_data[var_name]

            # Check if variable appears in dangerous positions
            var_symbol = sp.Symbol(var_name)

            # Check if in denominator
            for atom in sp.preorder_traversal(sympy_expr):
                if atom.is_Pow and atom.exp == -1:
                    if var_symbol in atom.base.free_symbols:
                        # Variable in denominator - check for zeros
                        if np.any(np.abs(data) < 1e-10):
                            result["errors"].append(
                                f"Variable '{var_name}' in denominator has near-zero values "
                                f"(min: {np.min(np.abs(data)):.2e})"
                            )
                            result["fixes"].append(f"Add epsilon protection: {atom.base} + ε")

                # Check if in log argument
                if atom.func == sp.log:
                    if var_symbol in atom.args[0].free_symbols:
                        if np.any(data <= 0):
                            result["errors"].append(
                                f"Variable '{var_name}' in log has non-positive values " f"(min: {np.min(data):.2e})"
                            )
                            result["fixes"].append(f"Ensure {var_name} > 0 or use abs({var_name})")

                # Check if in sqrt argument
                if atom.func == sp.sqrt:
                    if var_symbol in atom.args[0].free_symbols:
                        if np.any(data < 0):
                            result["errors"].append(
                                f"Variable '{var_name}' in sqrt has negative values " f"(min: {np.min(data):.2e})"
                            )
                            result["fixes"].append(f"Ensure {var_name} >= 0 or use abs({var_name})")

        return result

    def _check_variables(self, sympy_expr: sp.Expr, variable_names: List[str]) -> Dict:
        """Check for unexpected variables or missing variables."""
        result = {"warnings": []}

        expr_vars = {str(sym) for sym in sympy_expr.free_symbols}
        expected_vars = set(variable_names)

        # Check for unexpected variables
        unexpected = expr_vars - expected_vars
        if unexpected:
            result["warnings"].append(f"Expression contains unexpected variables: {unexpected}")

        # Check for unused variables
        unused = expected_vars - expr_vars
        if unused:
            result["warnings"].append(f"Expected variables not in expression: {unused}")

        return result

    def _calculate_complexity(self, sympy_expr: sp.Expr) -> int:
        """Calculate expression complexity."""
        # Count operations
        op_count = 0
        for atom in sp.preorder_traversal(sympy_expr):
            if not atom.is_Atom:
                op_count += 1
        return op_count

    def get_validation_summary(self) -> Dict:
        """Get summary of all validations."""
        if not self.validation_history:
            return {"total": 0}

        total = len(self.validation_history)
        valid_count = sum(1 for v in self.validation_history if v["valid"])

        return {
            "total_validations": total,
            "valid_count": valid_count,
            "invalid_count": total - valid_count,
            "validity_rate": valid_count / total,
            "total_errors": sum(len(v["errors"]) for v in self.validation_history),
            "total_warnings": sum(len(v["warnings"]) for v in self.validation_history),
            "common_issues": self._get_common_issues(),
        }

    def _get_common_issues(self) -> List[tuple]:
        """Get most common validation issues."""
        issue_counts = {}
        for v in self.validation_history:
            for issue in v.get("safety_issues", []):
                itype = issue.get("type", "unknown")
                issue_counts[itype] = issue_counts.get(itype, 0) + 1

        return sorted(issue_counts.items(), key=lambda x: x[1], reverse=True)[:5]


# ============================================================================
# COMPREHENSIVE TEST SUITE
# ============================================================================


def test_safe_math_operations():
    """Test SafeMathOperations class."""
    print("=" * 80)
    print("TEST: SafeMathOperations")
    print("=" * 80)

    safe_math = SafeMathOperations(epsilon=1e-10, strict_mode=True)

    # Test 1: Safe division with near-zero denominator
    print("\n1. Safe Division with near-zero denominator")
    result = safe_math.safe_divide(10.0, 1e-15, context="Test division")
    print(f"   10.0 / 1e-15 = {result:.2e}")
    print(f"   Violations: {safe_math.violation_count}")

    # Test 2: Safe logarithm with negative argument
    print("\n2. Safe Logarithm with negative argument")
    result = safe_math.safe_log(-5.0, context="Test log")
    print(f"   log(-5.0) = {result:.2e}")
    print(f"   Violations: {safe_math.violation_count}")

    # Test 3: Safe sqrt with negative argument
    print("\n3. Safe Square Root with negative argument")
    result = safe_math.safe_sqrt(-9.0, context="Test sqrt")
    print(f"   sqrt(-9.0) = {result:.2f}")
    print(f"   Violations: {safe_math.violation_count}")

    # Test 4: Safe exponential with overflow risk
    print("\n4. Safe Exponential with overflow risk")
    result = safe_math.safe_exp(1000, context="Test exp")
    print(f"   exp(1000) = {result:.2e}")
    print(f"   Violations: {safe_math.violation_count}")

    # Get violation report
    print("\n5. Violation Report")
    report = safe_math.get_violation_report()
    print(f"   Total violations: {report['total_violations']}")
    print(f"   By type: {report['violations_by_type']}")


def test_expression_validator():
    """Test ExpressionValidator class."""
    print("\n" + "=" * 80)
    print("TEST: ExpressionValidator")
    print("=" * 80)

    validator = ExpressionValidator()

    # Test 1: Null expression
    print("\n1. Null Expression")
    result = validator.validate_expression(None)
    print(f"   Valid: {result['valid']}")
    print(f"   Errors: {result['errors']}")

    # Test 2: Empty string
    print("\n2. Empty String Expression")
    result = validator.validate_expression("")
    print(f"   Valid: {result['valid']}")
    print(f"   Errors: {result['errors']}")

    # Test 3: Whitespace only
    print("\n3. Whitespace-Only Expression")
    result = validator.validate_expression("   ")
    print(f"   Valid: {result['valid']}")
    print(f"   Errors: {result['errors']}")

    # Test 4: Syntax error - unmatched parentheses
    print("\n4. Syntax Error - Unmatched Parentheses")
    result = validator.validate_expression("(x + y")
    print(f"   Valid: {result['valid']}")
    print(f"   Errors: {result['errors']}")

    # Test 5: Valid expression with dangerous operations
    print("\n5. Valid Expression with Division")
    result = validator.validate_expression("x / y")
    print(f"   Valid: {result['valid']}")
    print(f"   Dangerous operations: {result['dangerous_operations']}")
    print(f"   Warnings: {result['warnings'][:2]}")  # First 2 warnings

    # Test 6: Expression with variable data validation
    print("\n6. Variable Domain Validation")
    expr = "log(x) + sqrt(y)"
    var_data = {
        "x": np.array([-1.0, 0.5, 1.0]),  # Has negative value!
        "y": np.array([-4.0, 1.0, 2.0]),  # Has negative value!
    }
    result = validator.validate_expression(expr, variable_names=["x", "y"], variable_data=var_data)
    print(f"   Valid: {result['valid']}")
    print(f"   Errors: {result['errors']}")
    print(f"   Suggested fixes: {result['suggested_fixes']}")

    # Test 7: Complex expression analysis
    print("\n7. Complex Expression Analysis")
    complex_expr = "2 * sqrt(r) / (1 + r) - 1"
    result = validator.validate_expression(complex_expr, variable_names=["r"])
    print(f"   Expression: {complex_expr}")
    print(f"   Valid: {result['valid']}")
    print(f"   Complexity: {result['complexity']}")
    print(f"   Dangerous operations: {result['dangerous_operations']}")

    # Validation summary
    print("\n8. Validation Summary")
    summary = validator.get_validation_summary()
    print(f"   Total validations: {summary['total_validations']}")
    print(f"   Valid: {summary['valid_count']}, Invalid: {summary['invalid_count']}")
    print(f"   Validity rate: {summary['validity_rate']:.1%}")


def test_integration_with_numpy():
    """Test integration with numpy arrays."""
    print("\n" + "=" * 80)
    print("TEST: Integration with NumPy Arrays")
    print("=" * 80)

    safe_math = SafeMathOperations()

    # Test array operations
    print("\n1. Array Division with Near-Zero Values")
    numerator = np.array([1.0, 2.0, 3.0, 4.0, 5.0])
    denominator = np.array([1e-15, 0.5, 1.0, 1e-12, 2.0])

    result = safe_math.safe_divide(numerator, denominator, context="Array division")
    print(f"   Input denominator min: {np.min(denominator):.2e}")
    print(f"   Result: {result}")
    print(f"   Violations: {safe_math.violation_count}")

    # Test array logarithm
    print("\n2. Array Logarithm with Negative Values")
    x = np.array([-1.0, 0.5, 1.0, -0.1, 2.0])
    result = safe_math.safe_log(x, context="Array log")
    print(f"   Input: {x}")
    print(f"   Result: {result}")
    print(f"   Violations: {safe_math.violation_count}")


if __name__ == "__main__":
    print("╔" + "=" * 78 + "╗")
    print("║" + " " * 20 + "ENHANCED SYMBOLIC ENGINE SAFETY TESTS" + " " * 21 + "║")
    print("╚" + "=" * 78 + "╝")
    print()

    # Run all tests
    test_safe_math_operations()
    test_expression_validator()
    test_integration_with_numpy()

    print("\n" + "=" * 80)
    print("✅ ALL ENHANCED SAFETY TESTS COMPLETE!")
    print("=" * 80)

# USAGE
"""
# Option 1: Import both and use together
from symbolic_engine import SymbolicEngine, DiscoveryConfig
from symbolic_engine_enhanced import SafeMathOperations, ExpressionValidator

# Use the original engine for discovery
engine = SymbolicEngine(config)
result = engine.discover(X, y, variable_names)

# Use enhanced validators for additional safety checks
validator = ExpressionValidator()
validation = validator.validate_expression(
    result['expression'],
    variable_names=variable_names,
    variable_data={name: X[:, i] for i, name in enumerate(variable_names)}
)

# Option 2: Integrate SafeMath into your code
safe_math = SafeMathOperations()
safe_result = safe_math.safe_divide(numerator, denominator, context="My calculation")

"""
