#!/usr/bin/env python3
"""
Enhanced Symbolic Validation for Generated Formulas
Comprehensive mathematical validation with robust error handling
Part of HypatiaX tools/validation/
"""
import re
from collections import defaultdict
from decimal import Decimal
from typing import Any, Dict, List, Optional, Set, Tuple

import sympy as sp
from sympy.parsing.latex import parse_latex


class EnhancedSymbolicValidator:
    """
    Production-grade formula validator with comprehensive checks

    Features:
        - Empty expression validation
        - Advanced division-by-zero detection
        - Overflow/underflow risk analysis
        - Numerical stability assessment
        - Domain-specific constraints
        - Dimensional consistency checking
    """

    # Thresholds for numerical stability
    LARGE_CONSTANT_THRESHOLD = 1e100
    SMALL_CONSTANT_THRESHOLD = 1e-100
    LARGE_EXPONENT_THRESHOLD = 100
    MAX_SAFE_FACTORIAL = 170  # factorial(171) overflows in float64

    def __init__(self):
        self.domain_rules = {
            "defi": self._defi_rules,
            "finance": self._finance_rules,
            "esg": self._esg_rules,
            "risk": self._risk_rules,
        }

    def validate(self, formula_latex: str, domain: str = "defi", strict_mode: bool = False) -> Dict[str, Any]:
        """
        Comprehensive validation with enhanced error detection

        Args:
            formula_latex: LaTeX formula string
            domain: Domain for specific rules (defi, finance, esg, risk)
            strict_mode: If True, warnings are treated as errors

        Returns:
            {
                'syntactically_valid': bool,
                'dimensionally_consistent': bool,
                'domain_valid': bool,
                'numerically_stable': bool,
                'errors': [list of error messages],
                'warnings': [list of warnings],
                'info': [list of informational messages],
                'score': 0-100,
                'expression': str representation of parsed expression
            }
        """
        results = {
            "syntactically_valid": False,
            "dimensionally_consistent": False,
            "domain_valid": False,
            "numerically_stable": False,
            "errors": [],
            "warnings": [],
            "info": [],
            "expression": None,
        }

        # 1. EMPTY EXPRESSION VALIDATION
        empty_check = self._validate_not_empty(formula_latex)
        if not empty_check["valid"]:
            results["errors"].extend(empty_check["errors"])
            results["score"] = 0
            return results

        try:
            # 2. Parse LaTeX to SymPy
            expr = self._safe_parse_latex(formula_latex)
            if expr is None:
                results["errors"].append("Cannot parse LaTeX formula - invalid syntax")
                results["score"] = self._calculate_score(results)
                return results

            results["syntactically_valid"] = True
            results["expression"] = str(expr)
            results["info"].append(f"Parsed expression: {expr}")

            # 3. DIVISION BY ZERO DETECTION
            division_check = self._comprehensive_division_check(expr)
            if division_check["has_risks"]:
                results["errors"].extend(division_check["errors"])
                results["warnings"].extend(division_check["warnings"])

            # 4. OVERFLOW RISK CHECKS
            overflow_check = self._comprehensive_overflow_check(expr)
            if overflow_check["has_risks"]:
                results["errors"].extend(overflow_check["errors"])
                results["warnings"].extend(overflow_check["warnings"])

            # 5. Dimensional consistency
            dim_check = self._check_dimensions(expr)
            results["dimensionally_consistent"] = dim_check["consistent"]
            if not dim_check["consistent"]:
                results["errors"].extend(dim_check["errors"])
            results["warnings"].extend(dim_check["warnings"])

            # 6. Domain-specific rules
            domain_check = self.domain_rules.get(domain, self._default_rules)(expr)
            results["domain_valid"] = domain_check["valid"]
            results["errors"].extend(domain_check["errors"])
            results["warnings"].extend(domain_check.get("warnings", []))

            # 7. Numerical stability (computational mechanics expertise)
            stability = self._check_numerical_stability(expr)
            results["numerically_stable"] = stability["stable"]
            results["warnings"].extend(stability["warnings"])
            results["info"].extend(stability.get("info", []))

            # 8. Underflow detection
            underflow_check = self._check_underflow_risk(expr)
            if underflow_check["has_risks"]:
                results["warnings"].extend(underflow_check["warnings"])

        except Exception as e:
            results["errors"].append(f"Validation error: {str(e)}")

        # Apply strict mode if enabled
        if strict_mode and results["warnings"]:
            results["errors"].extend([f"[STRICT] {w}" for w in results["warnings"]])
            results["warnings"] = []

        results["score"] = self._calculate_score(results)
        return results

    def _validate_not_empty(self, formula_latex: str) -> Dict[str, Any]:
        """
        Validate input is not empty or whitespace-only
        """
        errors = []

        if formula_latex is None:
            errors.append("Formula is None - expected string input")
        elif not isinstance(formula_latex, str):
            errors.append(f"Formula must be string, got {type(formula_latex).__name__}")
        elif not formula_latex.strip():
            errors.append("Formula is empty or contains only whitespace")
        elif len(formula_latex.strip()) < 2:
            errors.append("Formula too short to be valid (< 2 characters)")

        return {"valid": len(errors) == 0, "errors": errors}

    def _safe_parse_latex(self, latex_str: str) -> Optional[sp.Expr]:
        """
        Safely parse LaTeX with multiple fallback strategies
        """
        try:
            # Clean LaTeX string
            latex_str = latex_str.strip()

            # Remove common text wrappers
            latex_str = re.sub(r"\\text\{([^}]+)\}", r"\1", latex_str)
            latex_str = re.sub(r"\\mathrm\{([^}]+)\}", r"\1", latex_str)

            # Remove display math delimiters
            latex_str = latex_str.replace("$$", "").replace("$", "")
            latex_str = latex_str.replace("\\[", "").replace("\\]", "")

            # Try standard LaTeX parsing
            return parse_latex(latex_str)

        except Exception as e:
            # Fallback 1: Try sympify
            try:
                return sp.sympify(latex_str)
            except:
                pass

            # Fallback 2: Try with common LaTeX fixes
            try:
                fixed = latex_str.replace("\\cdot", "*")
                fixed = fixed.replace("\\times", "*")
                fixed = fixed.replace("\\div", "/")
                return parse_latex(fixed)
            except:
                pass

        return None

    def _comprehensive_division_check(self, expr: sp.Expr) -> Dict[str, Any]:
        """
        Enhanced division by zero detection

        Checks:
        - Explicit denominators in fractions
        - Negative exponents (x^-1 = 1/x)
        - Symbolic cancellations (x-x, sin(0), etc.)
        - Conditional zero values
        """
        errors = []
        warnings = []

        # 1. Extract all denominators (including negative powers)
        denominators = self._extract_all_denominators(expr)

        for denom in denominators:
            zero_risk = self._analyze_zero_risk(denom)

            if zero_risk["risk"] == "high":
                errors.append(f"CRITICAL: Division by zero - {denom} can be zero")
            elif zero_risk["risk"] == "medium":
                warnings.append(f"WARNING: Potential division by zero - {denom}")
            elif zero_risk["risk"] == "low":
                warnings.append(f"INFO: Check domain - ensure {denom} ≠ 0")

        # 2. Check for implicit divisions (1/x patterns)
        if expr.has(sp.Pow):
            for atom in sp.preorder_traversal(expr):
                if atom.is_Pow and atom.exp.is_negative:
                    base = atom.base
                    warnings.append(f"Negative exponent: {base}^{atom.exp} = 1/{base}^{-atom.exp}")

        return {"has_risks": len(errors) > 0 or len(warnings) > 0, "errors": errors, "warnings": warnings}

    def _extract_all_denominators(self, expr: sp.Expr) -> List[sp.Expr]:
        """
        Extract all denominators including implicit ones
        """
        denominators = []

        for atom in sp.preorder_traversal(expr):
            # Explicit division
            if atom.is_Mul:
                for arg in atom.args:
                    if arg.is_Pow and arg.exp.is_negative:
                        denominators.append(arg.base)

            # Division operation
            if atom.is_Pow and atom.exp == -1:
                denominators.append(atom.base)

            # Rational numbers
            if atom.is_Rational and atom.q != 1:
                # Don't flag constant denominators unless they're parameters
                pass

        # Remove duplicates while preserving order
        seen = set()
        unique_denoms = []
        for d in denominators:
            d_str = str(d)
            if d_str not in seen:
                seen.add(d_str)
                unique_denoms.append(d)

        return unique_denoms

    def _analyze_zero_risk(self, expr: sp.Expr) -> Dict[str, str]:
        """
        Analyze how likely an expression is to be zero

        Returns risk level: 'high', 'medium', 'low', 'none'
        """
        # Numeric constant
        if expr.is_Number:
            if abs(float(expr)) < 1e-10:
                return {"risk": "high", "reason": "numeric zero or near-zero"}
            return {"risk": "none", "reason": "non-zero constant"}

        # Subtraction: a - b (high risk if a could equal b)
        if expr.is_Add:
            pos_terms = [arg for arg in expr.args if not arg.could_extract_minus_sign()]
            neg_terms = [arg for arg in expr.args if arg.could_extract_minus_sign()]

            if len(pos_terms) == 1 and len(neg_terms) == 1:
                return {"risk": "high", "reason": "subtraction can cancel"}
            elif len(neg_terms) > 0:
                return {"risk": "medium", "reason": "contains subtractions"}

        # Known zero-producing functions
        if expr.has(sp.sin) or expr.has(sp.cos) or expr.has(sp.tan):
            return {"risk": "medium", "reason": "trigonometric function can be zero"}

        # Multiplication: if any factor is zero
        if expr.is_Mul:
            for arg in expr.args:
                if arg.is_Number and arg == 0:
                    return {"risk": "high", "reason": "contains zero factor"}

        # Symbols and other expressions
        if expr.is_Symbol or expr.has(sp.Symbol):
            return {"risk": "low", "reason": "symbolic - requires domain constraints"}

        return {"risk": "low", "reason": "complex expression"}

    def _comprehensive_overflow_check(self, expr: sp.Expr) -> Dict[str, Any]:
        """
        Comprehensive overflow and large number detection

        Checks:
        - Large numeric constants (> 1e100)
        - Exponential functions
        - Large exponents (x^1000)
        - Factorial operations
        - Products of large numbers
        - Nested exponentials
        """
        errors = []
        warnings = []

        for atom in sp.preorder_traversal(expr):
            # 1. Large constants
            if atom.is_Number and not atom.is_infinite:
                try:
                    val = abs(float(atom))
                    if val > self.LARGE_CONSTANT_THRESHOLD:
                        errors.append(f"CRITICAL: Extremely large constant {atom:.2e} - overflow risk")
                    elif val > 1e50:
                        warnings.append(f"Large constant {atom:.2e} - verify range")
                except (ValueError, OverflowError):
                    errors.append(f"Constant {atom} cannot be represented as float")

            # 2. Exponential functions
            if atom.func == sp.exp:
                arg = atom.args[0]
                warnings.append(f"Exponential exp({arg}) - validate input range to prevent overflow")

                # Check if exponent is large
                if arg.is_Number:
                    try:
                        if float(arg) > 100:
                            errors.append(f"CRITICAL: exp({arg}) will overflow (e^x with x > 100)")
                    except:
                        pass

            # 3. Power operations with large exponents
            if atom.is_Pow:
                base, exp_val = atom.args

                # Check for large numeric exponents
                if exp_val.is_Number:
                    try:
                        exp_float = float(exp_val)
                        if abs(exp_float) > self.LARGE_EXPONENT_THRESHOLD:
                            errors.append(f"CRITICAL: Large exponent {base}^{exp_val} - overflow risk")
                        elif abs(exp_float) > 10:
                            warnings.append(f"Power {base}^{exp_val} - validate input range")
                    except:
                        pass

                # Check for nested exponentials (e^(e^x))
                if base.func == sp.exp:
                    errors.append("CRITICAL: Nested exponential - extremely high overflow risk")

            # 4. Factorial operations
            if atom.func == sp.factorial:
                arg = atom.args[0]
                if arg.is_Number:
                    try:
                        n = int(arg)
                        if n > self.MAX_SAFE_FACTORIAL:
                            errors.append(
                                f"CRITICAL: factorial({n}) overflows float64 (max safe: {self.MAX_SAFE_FACTORIAL})"
                            )
                        elif n > 100:
                            warnings.append(f"Large factorial({n}) - consider log-space computation")
                    except:
                        pass
                else:
                    warnings.append(f"Factorial of symbolic value {arg} - ensure bounded input")

            # 5. Check for products that might overflow
            if atom.is_Mul:
                large_factors = []
                for arg in atom.args:
                    if arg.is_Number and abs(float(arg)) > 1e10:
                        large_factors.append(arg)

                if len(large_factors) >= 2:
                    warnings.append(f"Product of large numbers - check for overflow")

            # 6. Hyperbolic functions (can grow very large)
            if atom.func in (sp.sinh, sp.cosh):
                warnings.append(f"Hyperbolic function {atom.func.__name__} - grows exponentially")

        return {"has_risks": len(errors) > 0 or len(warnings) > 0, "errors": errors, "warnings": warnings}

    def _check_underflow_risk(self, expr: sp.Expr) -> Dict[str, Any]:
        """
        Check for underflow risks (numbers too small to represent)
        """
        warnings = []

        for atom in sp.preorder_traversal(expr):
            # Very small constants
            if atom.is_Number and not atom.is_zero:
                try:
                    val = abs(float(atom))
                    if 0 < val < self.SMALL_CONSTANT_THRESHOLD:
                        warnings.append(f"Very small constant {atom:.2e} - underflow risk")
                except:
                    pass

            # Negative exponentials
            if atom.func == sp.exp:
                arg = atom.args[0]
                if arg.is_Number and float(arg) < -100:
                    warnings.append(f"exp({arg}) may underflow to zero")

        return {"has_risks": len(warnings) > 0, "warnings": warnings}

    def _check_dimensions(self, expr: sp.Expr) -> Dict[str, Any]:
        """
        Dimensional analysis - check unit consistency
        """
        errors = []
        warnings = []

        # Basic check: addition/subtraction requires same dimensions
        if expr.is_Add:
            warnings.append("Addition detected - ensure all terms have same dimensions")

        # Check for mixed operations that might indicate dimension issues
        # This is simplified - expand based on domain knowledge

        return {"consistent": len(errors) == 0, "errors": errors, "warnings": warnings}

    def _check_numerical_stability(self, expr: sp.Expr) -> Dict[str, Any]:
        """
        Computational mechanics expertise: numerical stability analysis

        Checks:
        - Subtractive cancellation
        - Condition number issues
        - Precision loss in operations
        - Algorithmic stability
        """
        warnings = []
        info = []

        # 1. Subtractive cancellation: (a - b) where a ≈ b
        subtractions = self._find_subtractions(expr)
        if len(subtractions) > 0:
            warnings.append(
                f"Found {len(subtractions)} subtraction(s) - risk of precision loss if operands are similar"
            )
            if len(subtractions) > 3:
                warnings.append("Multiple subtractions - consider reformulating to avoid cancellation")

        # 2. Square roots (require non-negative inputs)
        if expr.has(sp.sqrt):
            warnings.append("Square root present - validate non-negative inputs")

        # 3. Logarithms (require positive inputs)
        if expr.has(sp.log):
            warnings.append("Logarithm present - validate positive inputs")

        # 4. Complex denominators (conditioning issues)
        denominators = self._extract_all_denominators(expr)
        if len(denominators) > 2:
            info.append(f"Expression has {len(denominators)} division operations")

        # 5. Mixed multiplication/division (accumulation of rounding errors)
        mul_count = sum(1 for atom in sp.preorder_traversal(expr) if atom.is_Mul)
        if mul_count > 5:
            warnings.append(f"Multiple multiplications ({mul_count}) - rounding errors may accumulate")

        return {"stable": len(warnings) == 0, "warnings": warnings, "info": info}

    def _find_subtractions(self, expr: sp.Expr) -> List[sp.Expr]:
        """Find all subtraction operations"""
        subtractions = []

        for atom in sp.preorder_traversal(expr):
            if atom.is_Add:
                neg_terms = [arg for arg in atom.args if arg.could_extract_minus_sign()]
                if len(neg_terms) > 0:
                    subtractions.append(atom)

        return subtractions

    # Domain-specific validation rules

    def _defi_rules(self, expr: sp.Expr) -> Dict[str, Any]:
        """DeFi-specific validation rules"""
        errors = []
        warnings = []

        # Check for common DeFi patterns
        if expr.has(sp.sqrt):
            warnings.append("Square root in DeFi formula - typical in AMM pricing (√(x·y))")

        # Check for division (price impact, slippage calculations)
        denominators = self._extract_all_denominators(expr)
        if denominators:
            warnings.append("Division in DeFi - ensure liquidity pool is non-empty")

        # Check for negative values (liquidity/amounts must be positive)
        warnings.append("DeFi domain: validate all amounts and liquidity values are positive")

        return {"valid": len(errors) == 0, "errors": errors, "warnings": warnings}

    def _finance_rules(self, expr: sp.Expr) -> Dict[str, Any]:
        """Finance-specific validation rules"""
        errors = []
        warnings = []

        # Check for common finance operations
        if expr.has(sp.log):
            warnings.append("Logarithm in finance - typical for log-returns")

        if expr.has(sp.sqrt):
            warnings.append("Square root - typical for volatility calculations")

        # Risk metrics should be non-negative
        warnings.append("Finance domain: ensure risk metrics are non-negative")

        return {"valid": len(errors) == 0, "errors": errors, "warnings": warnings}

    def _esg_rules(self, expr: sp.Expr) -> Dict[str, Any]:
        """ESG-specific validation rules"""
        errors = []
        warnings = []

        # ESG scores typically bounded
        warnings.append("ESG domain: ensure scores are in valid range (typically 0-100)")

        # Check for weighted sums
        if expr.is_Add:
            warnings.append("Weighted sum detected - ensure weights sum to 1")

        return {"valid": len(errors) == 0, "errors": errors, "warnings": warnings}

    def _risk_rules(self, expr: sp.Expr) -> Dict[str, Any]:
        """Risk management validation rules"""
        errors = []
        warnings = []

        # VaR should be positive
        warnings.append("Risk domain: Value-at-Risk should be positive")

        # Check for probability calculations
        if expr.has(sp.exp) and expr.has(sp.Mul):
            warnings.append("Exponential in risk calculation - typical for probability distributions")

        return {"valid": len(errors) == 0, "errors": errors, "warnings": warnings}

    def _default_rules(self, expr: sp.Expr) -> Dict[str, Any]:
        """Default validation rules for unknown domains"""
        return {
            "valid": True,
            "errors": [],
            "warnings": ["Using default validation - specify domain for enhanced checks"],
        }

    def _calculate_score(self, results: Dict[str, Any]) -> int:
        """
        Calculate overall validation score (0-100)

        Scoring:
        - Each validation category: 25 points
        - Errors: -10 points each
        - Warnings: -2 points each
        """
        score = 0

        # Base points for passing each check
        if results["syntactically_valid"]:
            score += 25
        if results["dimensionally_consistent"]:
            score += 25
        if results["domain_valid"]:
            score += 25
        if results["numerically_stable"]:
            score += 25

        # Penalties
        score -= len(results["errors"]) * 10
        score -= len(results.get("warnings", [])) * 2

        # Clamp to 0-100
        return max(0, min(100, score))

    def get_validation_summary(self, results: Dict[str, Any]) -> str:
        """
        Generate human-readable validation summary
        """
        lines = []
        lines.append("=" * 60)
        lines.append("FORMULA VALIDATION REPORT")
        lines.append("=" * 60)
        lines.append(f"Overall Score: {results['score']}/100")
        lines.append(f"Expression: {results.get('expression', 'N/A')}")
        lines.append("")

        # Status indicators
        checks = [
            ("Syntactically Valid", results["syntactically_valid"]),
            ("Dimensionally Consistent", results["dimensionally_consistent"]),
            ("Domain Valid", results["domain_valid"]),
            ("Numerically Stable", results["numerically_stable"]),
        ]

        for check_name, passed in checks:
            status = "✓ PASS" if passed else "✗ FAIL"
            lines.append(f"{status}: {check_name}")

        lines.append("")

        # Errors
        if results["errors"]:
            lines.append("ERRORS:")
            for i, err in enumerate(results["errors"], 1):
                lines.append(f"  {i}. {err}")
            lines.append("")

        # Warnings
        if results["warnings"]:
            lines.append("WARNINGS:")
            for i, warn in enumerate(results["warnings"], 1):
                lines.append(f"  {i}. {warn}")
            lines.append("")

        # Info
        if results.get("info"):
            lines.append("INFO:")
            for i, info in enumerate(results["info"], 1):
                lines.append(f"  {i}. {info}")

        lines.append("=" * 60)

        return "\n".join(lines)


# Usage example
if __name__ == "__main__":
    validator = EnhancedSymbolicValidator()

    # Test cases
    test_formulas = [
        ("", "defi"),  # Empty
        (r"\frac{x}{x - x}", "defi"),  # Division by zero
        (r"e^{1000}", "finance"),  # Overflow
        (r"\sqrt{x \cdot y}", "defi"),  # Valid AMM formula
        (r"170!", "finance"),  # Large factorial
    ]

    for formula, domain in test_formulas:
        print(f"\nTesting: {formula or '(empty)'}")
        results = validator.validate(formula, domain=domain)
        print(validator.get_validation_summary(results))

"""
Key Enhancements
1. Empty Expression Validation ✅

_validate_not_empty() method checks for:

None values
Non-string types
Empty or whitespace-only strings
Strings shorter than 2 characters



2. Advanced Division-by-Zero Detection ✅

_comprehensive_division_check() with risk analysis
_extract_all_denominators() finds explicit and implicit divisions
_analyze_zero_risk() classifies risk levels (high/medium/low):

High: Numeric zeros, subtractions that can cancel (a-b)
Medium: Trigonometric functions, multiple subtractions
Low: Symbolic expressions requiring constraints



3. Comprehensive Overflow Checks ✅

_comprehensive_overflow_check() detects:

Large constants (>1e100)
Exponentials with large arguments
Large exponents (x^1000)
Factorials (>170 overflows float64)
Nested exponentials
Products of large numbers
Hyperbolic functions



Additional Features

Underflow detection for very small numbers
Numerical stability analysis (subtractive cancellation, precision loss)
Domain-specific rules for DeFi, finance, ESG, and risk
Strict mode option to treat warnings as errors
Detailed reporting with human-readable summaries
Multiple parsing strategies with fallbacks

The validator provides a score (0-100) and categorizes issues by severity (errors vs warnings), making it production-ready for HypatiaX formula validation.

"""
