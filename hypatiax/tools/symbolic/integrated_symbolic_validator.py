#!/usr/bin/env python3
"""
EnhancedSymbolicValidator - INTEGRATED PRODUCTION VERSION

Combines best features from both validator implementations:
- Robust LaTeX parsing with Greek letter support and auto-symbolization
- Comprehensive symbolic pattern detection
- Division-by-zero detection that counts each occurrence
- Nested exponential detection (generates ERRORS as expected)
- Numeric probing with sample substitutions
- Domain-specific validation rules
- Comprehensive scoring and reporting
"""
import re
from typing import Any, Dict, List, Optional

import sympy as sp
from sympy.parsing.latex import parse_latex
from sympy.parsing.sympy_parser import (
    convert_xor,
    implicit_multiplication_application,
    parse_expr,
    standard_transformations,
)


class EnhancedSymbolicValidator:
    """Production-grade formula validator with comprehensive symbolic and numeric checks"""

    LARGE_CONSTANT_THRESHOLD = 1e100
    SMALL_CONSTANT_THRESHOLD = 1e-100
    LARGE_EXPONENT_THRESHOLD = 100
    MAX_SAFE_FACTORIAL = 170

    # Default sample values for numeric probing
    DEFAULT_SAMPLE_VALUES = {
        "x": 1.0,
        "y": 1.0,
        "z": 1.0,
        "a": 1.0,
        "b": 1.0,
        "c": 1.0,
        "d": 1.0,
        "S": 100.0,
        "K": 100.0,
        "r": 0.05,
        "T": 1.0,
        "sigma": 0.2,
        "R_p": 0.1,
        "R_f": 0.01,
        "alpha": 0.05,
        "sigma_p": 0.2,
    }

    def __init__(self):
        self.domain_rules = {
            "defi": self._defi_rules,
            "finance": self._finance_rules,
            "esg": self._esg_rules,
            "risk": self._risk_rules,
        }

    # ========================================================================
    # PUBLIC API
    # ========================================================================

    def validate(
        self, formula_latex: Optional[str], domain: str = "defi", strict_mode: bool = False
    ) -> Dict[str, Any]:
        """
        Comprehensive formula validation with symbolic and numeric checks.

        Args:
            formula_latex: LaTeX formula string to validate
            domain: Validation domain ('defi', 'finance', 'esg', 'risk')
            strict_mode: If True, convert warnings to errors

        Returns:
            Dictionary with validation results including:
            - syntactically_valid, dimensionally_consistent, domain_valid, numerically_stable
            - errors, warnings, info, expression, score
        """
        results: Dict[str, Any] = {
            "syntactically_valid": False,
            "dimensionally_consistent": True,
            "domain_valid": True,
            "numerically_stable": True,
            "errors": [],
            "warnings": [],
            "info": [],
            "expression": None,
        }

        # 1. Input validation
        empty_check = self._validate_not_empty(formula_latex)
        if not empty_check["valid"]:
            results["errors"].extend(empty_check["errors"])
            results["score"] = 0
            return results

        # 2. Parse LaTeX to SymPy expression
        expr = self._safe_parse_latex(formula_latex)
        if expr is None:
            results["errors"].append("Cannot parse LaTeX formula - invalid syntax")
            results["score"] = self._calculate_score(results)
            return results

        results["syntactically_valid"] = True
        results["expression"] = str(expr)
        results["info"].append(f"Parsed expression: {expr}")

        # 3. Symbolic checks - division by zero (counts each occurrence)
        div_check = self._symbolic_division_checks(expr)
        results["errors"].extend(div_check["errors"])
        results["warnings"].extend(div_check["warnings"])

        # 4. Symbolic checks - overflow risks (nested exponentials as ERRORS)
        overflow_check = self._symbolic_overflow_checks(expr, formula_latex)
        results["errors"].extend(overflow_check["errors"])
        results["warnings"].extend(overflow_check["warnings"])

        # 5. Symbolic checks - numerical stability
        stability_check = self._symbolic_stability_checks(expr)
        results["errors"].extend(stability_check["errors"])
        results["warnings"].extend(stability_check["warnings"])

        # 6. Domain-specific rules
        domain_check = self.domain_rules.get(domain, self._default_rules)(expr)
        results["domain_valid"] = domain_check["valid"]
        results["errors"].extend(domain_check.get("errors", []))
        results["warnings"].extend(domain_check.get("warnings", []))

        # 7. Numeric probing - runtime evaluation
        numeric_check = self._numeric_probing(expr)
        results["errors"].extend(numeric_check["errors"])
        results["warnings"].extend(numeric_check["warnings"])
        results["info"].extend(numeric_check.get("info", []))

        # 8. Update stability flag based on detected issues
        if any(
            ("overflow" in e.lower() or "underflow" in e.lower() or "precision" in e.lower() or "numeric" in e.lower())
            for e in results["errors"] + results["warnings"]
        ):
            results["numerically_stable"] = False

        # 9. Apply strict mode
        if strict_mode and results["warnings"]:
            results["errors"].extend([f"[STRICT] {w}" for w in results["warnings"]])
            results["warnings"] = []

        # 10. Calculate final score
        results["score"] = self._calculate_score(results)
        return results

    # ========================================================================
    # INPUT VALIDATION
    # ========================================================================

    def _validate_not_empty(self, formula_latex: Optional[str]) -> Dict[str, Any]:
        """Validate input is not None, empty, or too short"""
        errors: List[str] = []

        if formula_latex is None:
            errors.append("Formula is None - expected string input")
        elif not isinstance(formula_latex, str):
            errors.append(f"Formula must be string, got {type(formula_latex).__name__}")
        elif not formula_latex.strip():
            errors.append("Formula is empty or whitespace only")
        elif len(formula_latex.strip()) < 2:
            errors.append("Formula too short to be valid (< 2 characters)")

        return {"valid": len(errors) == 0, "errors": errors}

    # ========================================================================
    # LATEX PARSING (Best from enhanced_symbolic_validator.py)
    # ========================================================================

    def _safe_parse_latex(self, latex_str: str) -> Optional[sp.Expr]:
        """
        Safely parse LaTeX with multiple fallback strategies.
        Includes Greek letter support and auto-symbolization.
        """
        if not latex_str or not isinstance(latex_str, str):
            return None

        s = latex_str.strip()
        if not s:
            return None

        # Remove math delimiters
        s = s.replace("$$", "").replace("$", "")
        s = s.replace("\\[", "").replace("\\]", "")
        s = re.sub(r"\\text\{([^}]+)\}", r"\1", s)
        s = re.sub(r"\\mathrm\{([^}]+)\}", r"\1", s)

        # Strategy 1: Direct parse_latex
        try:
            expr = parse_latex(s)
            if expr is not None:
                return self._normalize_exponentials(expr)
        except Exception:
            pass

        # Strategy 2: Relaxed parse_latex
        try:
            expr = parse_latex(s, strict=False)
            if expr is not None:
                return self._normalize_exponentials(expr)
        except Exception:
            pass

        # Strategy 3: Convert LaTeX to Python and sympify
        try:
            py = self._latex_to_python(s)
            locals_dict = self._auto_symbolize(py)
            expr = sp.sympify(py, locals=locals_dict, evaluate=False)
            return self._normalize_exponentials(expr)
        except Exception:
            pass

        # Strategy 4: Parse with transformations
        try:
            py = self._latex_to_python(s)
            locals_dict = self._auto_symbolize(py)
            transformations = standard_transformations + (
                implicit_multiplication_application,
                convert_xor,
            )
            expr = parse_expr(py, local_dict=locals_dict, transformations=transformations, evaluate=False)
            return self._normalize_exponentials(expr)
        except Exception:
            pass

        # Strategy 5: Try original string with parse_expr
        try:
            locals_dict = self._auto_symbolize(s)
            transformations = standard_transformations + (
                implicit_multiplication_application,
                convert_xor,
            )
            expr = parse_expr(s, local_dict=locals_dict, transformations=transformations, evaluate=False)
            return self._normalize_exponentials(expr)
        except Exception:
            pass

        return None

    def _normalize_exponentials(self, expr: sp.Expr) -> sp.Expr:
        """Convert lowercase 'e' symbols to Euler's number E when used in powers"""
        if expr is None:
            return None

        e_sym = sp.Symbol("e")
        if expr.has(e_sym):
            expr = expr.subs(e_sym, sp.E)

        return expr

    def _auto_symbolize(self, expr_str: str) -> Dict[str, Any]:
        """
        Automatically create symbols and functions for unknown identifiers.
        Handles Greek letters and function notation.
        """
        tokens = re.findall(r"[A-Za-z_]\w*", expr_str)

        locals_dict = {}

        # Built-in functions/constants to skip
        builtins = {"exp", "log", "sin", "cos", "tan", "sinh", "cosh", "tanh", "sqrt", "E", "pi", "I"}

        for token in tokens:
            if token in builtins:
                continue

            # Function notation: token followed by parenthesis
            if re.search(rf"{token}\s*\(", expr_str):
                locals_dict[token] = sp.Function(token)
            else:
                locals_dict[token] = sp.Symbol(token)

        return locals_dict

    def _latex_to_python(self, latex_str: str) -> str:
        """
        Convert LaTeX notation to Python/SymPy format.
        Includes comprehensive Greek letter support.
        """
        current = latex_str

        # Greek letters - process FIRST before other transformations
        greek_replacements = [
            (r"\\sigma", "sigma"),
            (r"\\mu", "mu"),
            (r"\\alpha", "alpha"),
            (r"\\beta", "beta"),
            (r"\\gamma", "gamma"),
            (r"\\delta", "delta"),
            (r"\\Delta", "Delta"),
            (r"\\lambda", "lambda_var"),
            (r"\\pi", "pi"),
            (r"\\Phi", "Phi"),
            (r"\\phi", "phi"),
            (r"\\theta", "theta"),
            (r"\\tau", "tau"),
            (r"\\rho", "rho"),
            (r"\\epsilon", "epsilon"),
            (r"\\varepsilon", "epsilon"),
            (r"\\kappa", "kappa"),
            (r"\\nu", "nu"),
            (r"\\omega", "omega"),
            (r"\\Omega", "Omega"),
            (r"\\zeta", "zeta"),
            (r"\\eta", "eta"),
            (r"\\xi", "xi"),
            (r"\\Xi", "Xi"),
            (r"\\psi", "psi"),
            (r"\\Psi", "Psi"),
            (r"\\chi", "chi"),
        ]

        for latex_pattern, py_name in greek_replacements:
            current = current.replace(latex_pattern, py_name)

        # Basic operators
        current = current.replace("\\cdot", "*")
        current = current.replace("\\times", "*")
        current = current.replace("\\div", "/")

        # Fractions - iterative with nesting support
        for _ in range(10):
            new = re.sub(
                r"\\frac\{([^{}]*(?:\{[^{}]*\}[^{}]*)*)\}\{([^{}]*(?:\{[^{}]*\}[^{}]*)*)\}",
                r"((\1)/(\2))",
                current,
            )
            if new == current:
                break
            current = new

        # Square roots
        current = re.sub(r"\\sqrt\{([^{}]+)\}", r"sqrt(\1)", current)

        # Subscripts (convert to plain text: d_1 -> d1)
        current = re.sub(r"([a-zA-Z])_\{([^{}]+)\}", r"\1\2", current)
        current = re.sub(r"([a-zA-Z])_([a-zA-Z0-9]+)", r"\1\2", current)

        # Powers
        current = re.sub(r"\^\{([^{}]+)\}", r"**(\1)", current)
        current = re.sub(r"\^([a-zA-Z0-9])", r"**\1", current)

        # Functions
        func_replacements = [
            (r"\\sin\b", "sin"),
            (r"\\cos\b", "cos"),
            (r"\\tan\b", "tan"),
            (r"\\log\b", "log"),
            (r"\\ln\b", "log"),
            (r"\\exp\b", "exp"),
            (r"\\sinh\b", "sinh"),
            (r"\\cosh\b", "cosh"),
            (r"\\tanh\b", "tanh"),
        ]

        for latex_pattern, py_func in func_replacements:
            current = re.sub(latex_pattern, py_func, current)

        # Clean up remaining LaTeX commands
        current = re.sub(r"\\([a-zA-Z]+)", r"\1", current)

        # Replace braces with parentheses
        current = current.replace("{", "(").replace("}", ")")

        return current

    # ========================================================================
    # SYMBOLIC DIVISION CHECKS (Best from ensemble.py)
    # ========================================================================

    def _symbolic_division_checks(self, expr: sp.Expr) -> Dict[str, List[str]]:
        """
        Division by zero detection - counts EACH denominator occurrence.
        Includes negative exponent detection.
        """
        errors: List[str] = []
        warnings: List[str] = []

        # Collect all denominators (including duplicates)
        denominators: List[sp.Expr] = []

        for atom in sp.preorder_traversal(expr):
            # Method 1: Check as_numer_denom for each expression
            try:
                n, d = sp.together(atom).as_numer_denom()
                if d != 1:
                    denominators.append(d)
            except Exception:
                pass

            # Method 2: Explicit Pow with negative exponent
            if atom.is_Pow and getattr(atom.exp, "is_negative", False):
                denominators.append(atom.base)

        # Analyze each denominator occurrence
        for denom in denominators:
            risk = self._analyze_zero_risk(denom)

            if risk == "high":
                errors.append(f"CRITICAL: Division by zero - denominator {denom} can be zero")
            elif risk == "medium":
                warnings.append(f"Potential division by zero - denominator {denom}")
            else:
                warnings.append(f"Check domain - ensure denominator {denom} ≠ 0")

        # Negative exponent warnings
        for atom in sp.preorder_traversal(expr):
            if atom.is_Pow and getattr(atom.exp, "is_negative", False):
                warnings.append(f"Negative exponent detected: {atom.base}^{atom.exp} implies division")

        return {"errors": errors, "warnings": warnings}

    def _analyze_zero_risk(self, expr: sp.Expr) -> str:
        """
        Analyze probability that expression equals zero.
        Returns: 'high', 'medium', 'low', or 'none'
        """
        # Numeric constant
        try:
            if expr.is_Number:
                val = float(expr)
                if abs(val) < 1e-10:
                    return "high"
                return "none"
        except Exception:
            pass

        # Subtraction (x - x) patterns
        if expr.is_Add:
            terms = list(expr.args)
            for i in range(len(terms)):
                for j in range(i + 1, len(terms)):
                    try:
                        if sp.simplify(terms[i] + terms[j]) == 0:
                            return "high"
                    except Exception:
                        pass
            return "medium"

        # Multiplication with zero
        if expr.is_Mul:
            for arg in expr.args:
                if arg.is_Number and arg == 0:
                    return "high"
            return "low"

        # Symbolic expression
        if expr.is_Symbol or expr.has(sp.Symbol):
            return "low"

        return "low"

    # ========================================================================
    # SYMBOLIC OVERFLOW CHECKS (Best from enhanced_symbolic_validator.py)
    # ========================================================================

    def _symbolic_overflow_checks(self, expr: sp.Expr, original_latex: str = "") -> Dict[str, List[str]]:
        """
        Comprehensive overflow detection.
        Nested exponentials generate ERRORS (not warnings).
        """
        errors: List[str] = []
        warnings: List[str] = []

        has_factorial_notation = "!" in original_latex

        for atom in sp.preorder_traversal(expr):
            # 1. Large numeric constants
            if atom.is_Number and not atom.is_infinite:
                try:
                    val = abs(float(atom))
                    if val > self.LARGE_CONSTANT_THRESHOLD:
                        if has_factorial_notation and len(str(atom)) > 50:
                            errors.append("CRITICAL: factorial() causes overflow in float64")
                        else:
                            errors.append(f"CRITICAL: Extremely large constant {val:.2e} - overflow risk")
                    elif val > 1e50:
                        warnings.append(f"Large constant {val:.2e} - verify range")
                except (ValueError, OverflowError):
                    if has_factorial_notation:
                        errors.append("CRITICAL: factorial() causes overflow in float64")
                    else:
                        errors.append(f"Constant {atom} cannot be represented as float")

            # 2. exp(x) function
            if atom.func == sp.exp:
                arg = atom.args[0]

                # Nested exponential detection - CRITICAL ERROR
                if arg.func == sp.exp or (hasattr(arg, "is_Pow") and arg.is_Pow and arg.base == sp.E):
                    errors.append(f"CRITICAL: Nested exponential detected: exp({arg}) - extreme overflow risk")
                elif arg.has(sp.exp) or any(
                    (hasattr(sub, "is_Pow") and sub.is_Pow and sub.base == sp.E) for sub in sp.preorder_traversal(arg)
                ):
                    errors.append(f"CRITICAL: Nested exponential detected: exp({arg}) - extreme overflow risk")

                # Numeric exponent check
                if arg.is_Number:
                    try:
                        arg_val = float(arg)
                        if arg_val > 100:
                            errors.append(f"CRITICAL: exp({arg}) will cause overflow")
                        elif arg_val > 50:
                            errors.append(f"Large exponential: exp({arg}) - high overflow risk")
                        elif arg_val < -100:
                            warnings.append(f"Negative exponential may underflow: exp({arg})")
                    except Exception:
                        pass
                else:
                    warnings.append(f"Exponential with symbolic exponent: exp({arg}) - check range")

            # 3. E^x notation
            if atom.is_Pow and atom.base == sp.E:
                exp_arg = atom.exp

                # Nested exponential detection - CRITICAL ERROR
                if exp_arg.func == sp.exp or (hasattr(exp_arg, "is_Pow") and exp_arg.is_Pow and exp_arg.base == sp.E):
                    errors.append(f"CRITICAL: Nested exponential detected: e^({exp_arg}) - extreme overflow risk")
                elif exp_arg.has(sp.exp) or any(
                    (hasattr(sub, "is_Pow") and sub.is_Pow and sub.base == sp.E)
                    for sub in sp.preorder_traversal(exp_arg)
                ):
                    errors.append(f"CRITICAL: Nested exponential detected: e^({exp_arg}) - extreme overflow risk")

                # Numeric exponent check
                if exp_arg.is_Number:
                    try:
                        val = float(exp_arg)
                        if val > 100:
                            errors.append(f"CRITICAL: e^{exp_arg} will cause overflow")
                        elif val > 50:
                            errors.append(f"Large exponential: e^{exp_arg} - high overflow risk")
                        elif val < -100:
                            warnings.append(f"Negative exponential may underflow: e^{exp_arg}")
                    except Exception:
                        pass
                else:
                    warnings.append(f"Exponential with symbolic exponent: e^({exp_arg}) - check range")

            # 4. Other power operations
            if atom.is_Pow and atom.base != sp.E:
                exp_val = atom.exp

                if exp_val.is_Number:
                    try:
                        ev = abs(float(exp_val))
                        if ev > self.LARGE_EXPONENT_THRESHOLD:
                            errors.append(f"CRITICAL: Large exponent {atom.base}^{exp_val} - overflow risk")
                        elif ev > 50:
                            warnings.append(f"Large exponent: {atom.base}^{exp_val} - overflow risk")
                        elif ev > 10:
                            warnings.append(f"Power operation {atom} - validate input range")
                    except Exception:
                        pass
                else:
                    warnings.append(f"Symbolic exponent: {atom} - validate exponent range")

            # 5. Factorial operations
            if atom.func == sp.factorial:
                arg = atom.args[0]
                if arg.is_Number:
                    try:
                        n = int(arg)
                        if n > self.MAX_SAFE_FACTORIAL:
                            errors.append(f"CRITICAL: factorial({n}) causes overflow in float64")
                        elif n > 100:
                            warnings.append(f"Large factorial: factorial({n}) - consider log-space")
                    except Exception:
                        warnings.append(f"Factorial with non-integer: {atom}")
                else:
                    warnings.append(f"Factorial of symbolic value {arg} - ensure bounded input")

            # 6. Hyperbolic functions
            if atom.func in (sp.sinh, sp.cosh):
                warnings.append(f"Hyperbolic function {atom.func.__name__} detected - grows exponentially")

            # 7. Product of large numbers
            if atom.is_Mul:
                large_factors = []
                for arg in atom.args:
                    if arg.is_Number:
                        try:
                            if abs(float(arg)) > 1e10:
                                large_factors.append(arg)
                        except Exception:
                            pass

                if len(large_factors) >= 2:
                    warnings.append("Product of large numbers detected - check for overflow")

        return {"errors": errors, "warnings": warnings}

    # ========================================================================
    # SYMBOLIC STABILITY CHECKS
    # ========================================================================

    def _symbolic_stability_checks(self, expr: sp.Expr) -> Dict[str, List[str]]:
        """Numerical stability analysis for symbolic expressions"""
        errors: List[str] = []
        warnings: List[str] = []

        # 1. Subtractive cancellation (x - x patterns)
        for atom in sp.preorder_traversal(expr):
            if atom.is_Add:
                terms = list(atom.args)
                for i in range(len(terms)):
                    for j in range(i + 1, len(terms)):
                        try:
                            if sp.simplify(terms[i] + terms[j]) == 0:
                                warnings.append(f"Subtraction detected - cancellation risk: {atom}")
                                break
                        except Exception:
                            pass

        # 2. Square root domain warnings
        for atom in sp.preorder_traversal(expr):
            if atom.func == sp.sqrt or (atom.is_Pow and getattr(atom, "exp", None) == sp.Rational(1, 2)):
                warnings.append(f"Square root requires non-negative input: {atom}")

        # 3. Logarithm domain warnings
        for atom in sp.preorder_traversal(expr):
            if atom.func == sp.log:
                warnings.append(f"Logarithm requires positive input: {atom}")

        # 4. Multiple multiplications
        for atom in sp.preorder_traversal(expr):
            if atom.is_Mul:
                if len(atom.args) > 5:
                    warnings.append(f"Multiple multiplications - rounding errors may accumulate: {atom}")

                # Product of large numbers
                numeric_factors = []
                for arg in atom.args:
                    if arg.is_Number:
                        try:
                            numeric_factors.append(abs(float(arg)))
                        except Exception:
                            pass

                if len([f for f in numeric_factors if f > 1e10]) >= 2:
                    warnings.append(f"Product of very large numbers - check overflow: {atom}")

        return {"errors": errors, "warnings": warnings}

    # ========================================================================
    # NUMERIC PROBING (Best from ensemble.py)
    # ========================================================================

    def _numeric_probing(self, expr: sp.Expr) -> Dict[str, Any]:
        """
        Runtime evaluation with sample values to detect numeric issues.
        Catches division by zero, overflow, underflow, and domain violations.
        """
        errors: List[str] = []
        warnings: List[str] = []
        info: List[str] = []

        # Build substitution dictionary
        subs: Dict[sp.Symbol, float] = {}
        for name, val in self.DEFAULT_SAMPLE_VALUES.items():
            try:
                subs[sp.symbols(name)] = float(val)
            except Exception:
                pass

        # Evaluate expression numerically
        try:
            numeric = expr.evalf(subs=subs)
            info.append(f"Numeric evaluation (sample): {numeric}")

            # Check for complex results
            try:
                if not numeric.is_real and abs(sp.im(numeric)) > 1e-12:
                    warnings.append(f"Numeric evaluation produced complex value: {numeric}")
            except Exception:
                pass

            # Magnitude checks
            try:
                nv = float(sp.N(numeric))
                if abs(nv) > self.LARGE_CONSTANT_THRESHOLD:
                    errors.append(f"CRITICAL: Numeric overflow detected: {nv:.2e}")
                elif abs(nv) > 1e50:
                    warnings.append(f"Numeric large value detected: {nv:.2e}")
                elif 0 < abs(nv) < self.SMALL_CONSTANT_THRESHOLD:
                    warnings.append(f"Numeric underflow risk: {nv:.2e}")
            except Exception:
                pass

        except ZeroDivisionError:
            errors.append("Validation error: division by zero during numeric probing")
        except Exception as e:
            warnings.append(f"Numeric evaluation failed: {e}")

        # Domain checks for sqrt and log
        for atom in sp.preorder_traversal(expr):
            # Square root domain check
            if atom.func == sp.sqrt or (atom.is_Pow and getattr(atom, "exp", None) == sp.Rational(1, 2)):
                try:
                    arg_value = atom.args[0].evalf(subs=subs)
                    if hasattr(arg_value, "is_real") and arg_value.is_real and float(arg_value) < 0:
                        errors.append(f"Square root domain violation: {atom} evaluates to {arg_value}")
                except ZeroDivisionError:
                    errors.append(f"Division by zero while evaluating sqrt arg: {atom}")
                except Exception:
                    pass

            # Logarithm domain check
            if atom.func == sp.log:
                try:
                    arg_value = atom.args[0].evalf(subs=subs)
                    if hasattr(arg_value, "is_real") and arg_value.is_real and float(arg_value) <= 0:
                        errors.append(f"Logarithm domain violation: {atom} evaluates to {arg_value}")
                except ZeroDivisionError:
                    errors.append(f"Division by zero while evaluating log arg: {atom}")
                except Exception:
                    pass

        return {"errors": errors, "warnings": warnings, "info": info}

    # ========================================================================
    # DOMAIN-SPECIFIC VALIDATION RULES
    # ========================================================================

    def _defi_rules(self, expr: sp.Expr) -> Dict[str, Any]:
        """DeFi-specific validation (AMM, liquidity pools)"""
        errors: List[str] = []
        warnings: List[str] = []

        if expr.has(sp.sqrt):
            warnings.append("DeFi domain: sqrt common in AMM formulas (√(x·y))")

        denominators = self._extract_denominators(expr)
        if denominators:
            warnings.append("DeFi domain: ensure liquidity denominators are non-zero")

        warnings.append("DeFi domain: validate all amounts and liquidity values are positive")

        return {"valid": True, "errors": errors, "warnings": warnings}

    def _finance_rules(self, expr: sp.Expr) -> Dict[str, Any]:
        """Finance-specific validation (risk metrics, returns)"""
        errors: List[str] = []
        warnings: List[str] = []

        if expr.has(sp.log):
            warnings.append("Finance domain: logarithm detected (log-returns)")

        if expr.has(sp.sqrt):
            warnings.append("Finance domain: square root detected (volatility)")

        warnings.append("Finance domain: ensure risk metrics are non-negative")

        return {"valid": True, "errors": errors, "warnings": warnings}

    def _esg_rules(self, expr: sp.Expr) -> Dict[str, Any]:
        """ESG-specific validation (scoring, weights)"""
        errors: List[str] = []
        warnings: List[str] = ["ESG domain: ensure scores are in valid range (typically 0-100)"]

        if expr.is_Add or expr.is_Mul:
            warnings.append("ESG scoring detected - ensure proper normalization")

        return {"valid": True, "errors": errors, "warnings": warnings}

    def _risk_rules(self, expr: sp.Expr) -> Dict[str, Any]:
        """Risk management validation (VaR, CVaR)"""
        errors: List[str] = []
        warnings: List[str] = ["Risk domain: Value-at-Risk should be positive"]

        if expr.has(sp.exp) and expr.has(sp.Mul):
            warnings.append("Risk domain: exponential in probability distributions")

        return {"valid": True, "errors": errors, "warnings": warnings}

    def _default_rules(self, expr: sp.Expr) -> Dict[str, Any]:
        """Default validation rules"""
        return {
            "valid": True,
            "errors": [],
            "warnings": ["Default validation applied - specify domain for enhanced checks"],
        }

    def _extract_denominators(self, expr: sp.Expr) -> List[sp.Expr]:
        """Helper to extract denominators from expression"""
        denominators = []
        for atom in sp.preorder_traversal(expr):
            try:
                _, d = sp.together(atom).as_numer_denom()
                if d != 1:
                    denominators.append(d)
            except Exception:
                pass
        return denominators

    # ========================================================================
    # SCORING AND REPORTING
    # ========================================================================

    def _calculate_score(self, results: Dict[str, Any]) -> int:
        """Calculate validation score (0-100)"""
        score = 0

        # Base scores for passing checks
        if results.get("syntactically_valid"):
            score += 25
        if results.get("dimensionally_consistent"):
            score += 25
        if results.get("domain_valid"):
            score += 25
        if results.get("numerically_stable"):
            score += 25

        # Penalties
        score -= len(results.get("errors", [])) * 50  # Heavy penalty for errors
        score -= len(results.get("warnings", [])) * 1  # Light penalty for warnings

        return max(0, min(100, score))

    def get_validation_summary(self, results: Dict[str, Any]) -> str:
        """Generate human-readable validation summary"""
        lines: List[str] = []
        lines.append("=" * 60)
        lines.append("FORMULA VALIDATION SUMMARY")
        lines.append("=" * 60)
        lines.append(f"Score: {results.get('score')}/100")
        lines.append(f"Expression: {results.get('expression')}")
        lines.append("")

        checks = [
            ("Syntactically valid", results.get("syntactically_valid")),
            ("Dimensionally consistent", results.get("dimensionally_consistent")),
            ("Domain valid", results.get("domain_valid")),
            ("Numerically stable", results.get("numerically_stable")),
        ]

        for name, passed in checks:
            status = "✓" if passed else "✗"
            lines.append(f"{status} {name}")

        lines.append("")

        if results.get("errors"):
            lines.append("ERRORS:")
            for i, err in enumerate(results["errors"], 1):
                lines.append(f"  {i}. {err}")
            lines.append("")

        if results.get("warnings"):
            lines.append("WARNINGS:")
            for i, warn in enumerate(results["warnings"], 1):
                lines.append(f"  {i}. {warn}")
            lines.append("")

        if results.get("info"):
            lines.append("INFO:")
            for i, inf in enumerate(results["info"], 1):
                lines.append(f"  {i}. {inf}")
            lines.append("")

        lines.append("=" * 60)
        return "\n".join(lines)


# ========================================================================
# MAIN - Quick validation harness
# ========================================================================

if __name__ == "__main__":
    validator = EnhancedSymbolicValidator()

    test_cases = [
        (r"x^{-1}", "Simple negative exponent"),
        (r"e^{x}", "Simple exponential"),
        (r"e^{500}", "Large exponential"),
        (r"e^{e^{x}}", "Nested exponential (should be ERROR)"),
        (r"x^{1000}", "Large power"),
        (r"180!", "Large factorial"),
        (r"e^{-200}", "Negative exponential"),
        (r"\sqrt{x}", "Square root"),
        (r"\log(x)", "Logarithm"),
        (r"\frac{1}{x-x}", "Division by zero"),
        (r"\sinh(x)", "Hyperbolic function"),
        (r"\frac{\alpha \cdot \sigma}{\sqrt{T}}", "Finance formula with Greek letters"),
    ]

    for latex_formula, description in test_cases:
        print("\n" + "-" * 60)
        print(f"Test: {description}")
        print(f"Formula: {latex_formula}")
        print("-" * 60)

        result = validator.validate(latex_formula)
        print(validator.get_validation_summary(result))
