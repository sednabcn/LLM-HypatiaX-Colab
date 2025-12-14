#!/usr/bin/env python3
"""
EnhancedSymbolicValidator - Full rewrite with symbolic + numeric checks

Drop-in replacement for hypatiax.tools.symbolic.enhanced_symbolic_validator.EnhancedSymbolicValidator
Features:
 - Robust LaTeX -> SymPy parsing (parse_latex with sympify fallback)
 - Symbolic pattern detection: negative exponents, nested exp, factorials, x-x, etc.
 - Division-by-zero detection that counts each denominator occurrence
 - Numeric probing using default sample substitutions to catch overflow/underflow + domain errors
 - Domain-specific rules (defi, finance, esg, risk)
 - Scoring and human-readable summary
"""
import re
from typing import Any, Dict, List, Optional, Tuple

import sympy as sp
from sympy.parsing.latex import parse_latex


class EnhancedSymbolicValidator:
    LARGE_CONSTANT_THRESHOLD = 1e100
    SMALL_CONSTANT_THRESHOLD = 1e-100
    LARGE_EXPONENT_THRESHOLD = 100
    MAX_SAFE_FACTORIAL = 170

    # Default sample values used for numeric probing
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

    # -----------------------------
    # Public API
    # -----------------------------
    def validate(self, formula_latex: Optional[str], domain: str = "defi", strict_mode: bool = False) -> Dict[str, Any]:
        """
        Validate a LaTeX formula with symbolic and numeric checks.
        Returns a dictionary with keys:
            syntactically_valid, dimensionally_consistent, domain_valid,
            numerically_stable, errors, warnings, info, expression, score
        """
        results: Dict[str, Any] = {
            "syntactically_valid": False,
            "dimensionally_consistent": True,  # optimistic default
            "domain_valid": True,
            "numerically_stable": True,
            "errors": [],
            "warnings": [],
            "info": [],
            "expression": None,
        }

        # Input validation
        empty_check = self._validate_not_empty(formula_latex)
        if not empty_check["valid"]:
            results["errors"].extend(empty_check["errors"])
            results["score"] = 0
            return results

        # Parse to SymPy
        expr = self._safe_parse_latex(formula_latex)
        if expr is None:
            results["errors"].append("Cannot parse LaTeX formula - invalid syntax")
            results["score"] = self._calculate_score(results)
            return results

        results["syntactically_valid"] = True
        results["expression"] = str(expr)
        results["info"].append(f"Parsed expression: {expr}")

        # Symbolic checks
        div_res = self._symbolic_division_checks(expr)
        results["errors"].extend(div_res["errors"])
        results["warnings"].extend(div_res["warnings"])

        overflow_res = self._symbolic_overflow_checks(expr)
        results["errors"].extend(overflow_res["errors"])
        results["warnings"].extend(overflow_res["warnings"])

        stability_res = self._symbolic_stability_checks(expr)
        results["errors"].extend(stability_res["errors"])
        results["warnings"].extend(stability_res["warnings"])

        # Domain-specific rules
        domain_res = self.domain_rules.get(domain, self._default_rules)(expr)
        results["domain_valid"] = domain_res["valid"]
        results["errors"].extend(domain_res.get("errors", []))
        results["warnings"].extend(domain_res.get("warnings", []))

        # Numeric probing to detect runtime issues
        numeric_res = self._numeric_probing(expr)
        results["errors"].extend(numeric_res["errors"])
        results["warnings"].extend(numeric_res["warnings"])
        results["info"].extend(numeric_res.get("info", []))

        # Adjust numerically_stable: if any overflow/underflow/precision issues exist
        if any(
            ("overflow" in e.lower() or "underflow" in e.lower() or "precision" in e.lower() or "numeric" in e.lower())
            for e in results["errors"] + results["warnings"]
        ):
            results["numerically_stable"] = False

        # Strict mode: convert warnings to errors
        if strict_mode and results["warnings"]:
            results["errors"].extend([f"[STRICT] {w}" for w in results["warnings"]])
            results["warnings"] = []

        # Score and return
        results["score"] = self._calculate_score(results)
        return results

    # -----------------------------
    # Input validation
    # -----------------------------
    def _validate_not_empty(self, formula_latex: Optional[str]) -> Dict[str, Any]:
        errors: List[str] = []
        if formula_latex is None:
            errors.append("Formula is None - expected string input")
        elif not isinstance(formula_latex, str):
            errors.append(f"Formula must be string, got {type(formula_latex).__name__}")
        elif not formula_latex.strip():
            errors.append("Formula is empty or whitespace only")
        elif len(formula_latex.strip()) < 2:
            # Tests expect single-character formulas to be considered too short
            errors.append("Formula too short to be valid (< 2 characters)")
        return {"valid": len(errors) == 0, "errors": errors}

    # -----------------------------
    # Parsing helpers
    # -----------------------------
    def _safe_parse_latex(self, latex_str: str) -> Optional[sp.Expr]:
        if not latex_str or not isinstance(latex_str, str):
            return None
        s = latex_str.strip()
        # remove common math delimiters and wrappers
        s = s.replace("$$", "").replace("$", "")
        s = s.replace("\\[", "").replace("\\]", "")
        s = re.sub(r"\\text\{([^}]+)\}", r"\1", s)
        s = re.sub(r"\\mathrm\{([^}]+)\}", r"\1", s)

        # try parse_latex first
        try:
            parsed = parse_latex(s)
            return parsed
        except Exception:
            pass

        # fallback: convert some LaTeX to python-like expression and sympify
        try:
            py = self._latex_to_python(s)
            return sp.sympify(py, evaluate=False)
        except Exception:
            return None

    def _latex_to_python(self, s: str) -> str:
        cur = s
        # repeated fraction replacement
        for _ in range(8):
            new = re.sub(r"\\frac\{([^{}]+)\}\{([^{}]+)\}", r"((\1)/(\2))", cur)
            if new == cur:
                break
            cur = new
        cur = cur.replace("\\cdot", "*").replace("\\times", "*").replace("\\div", "/")
        cur = re.sub(r"\\sqrt\{([^{}]+)\}", r"sqrt(\1)", cur)
        cur = re.sub(r"\^\{([^{}]+)\}", r"**(\1)", cur)
        cur = re.sub(r"\^([a-zA-Z0-9])", r"**\1", cur)
        cur = re.sub(r"([a-zA-Z])_\{([^{}]+)\}", r"\1_\2", cur)
        mapping = [
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
        for pat, repl in mapping:
            cur = re.sub(pat, repl, cur)
        cur = re.sub(r"\\([a-zA-Z]+)", r"\1", cur)
        cur = cur.replace("{", "(").replace("}", ")")
        return cur

    # -----------------------------
    # Symbolic division checks (count each denominator occurrence)
    # -----------------------------
    def _symbolic_division_checks(self, expr: sp.Expr) -> Dict[str, List[str]]:
        errors: List[str] = []
        warnings: List[str] = []

        # collect denominators by inspecting as_numer_denom() for each sub-expression
        denominators: List[sp.Expr] = []
        for atom in sp.preorder_traversal(expr):
            try:
                n, d = sp.together(atom).as_numer_denom()
                if d != 1:
                    # append the denominator expression occurrence (do not deduplicate)
                    denominators.append(d)
            except Exception:
                # fallback: negative powers and Pow with negative exponent
                if atom.is_Pow and getattr(atom.exp, "is_negative", False):
                    denominators.append(atom.base)

        # For each denominator occurrence, analyze zero risk and create per-occurrence messages
        for d in denominators:
            risk = self._analyze_zero_risk(d)
            if risk == "high":
                errors.append(f"CRITICAL: Division by zero - denominator {d} can be zero")
            elif risk == "medium":
                warnings.append(f"Potential division by zero - denominator {d}")
            else:
                warnings.append(f"Check domain - ensure denominator {d} ≠ 0")

        # implicit negative exponent warnings (one per occurrence)
        for atom in sp.preorder_traversal(expr):
            if atom.is_Pow and getattr(atom.exp, "is_negative", False):
                warnings.append(f"Negative exponent detected: {atom.base}^{atom.exp} implies division")

        return {"errors": errors, "warnings": warnings}

    def _analyze_zero_risk(self, expr: sp.Expr) -> str:
        """
        Return 'high'/'medium'/'low'/'none' for how likely expr can be zero.
        """
        try:
            if expr.is_Number:
                val = float(expr)
                if abs(val) < 1e-10:
                    return "high"
                return "none"
        except Exception:
            pass

        # subtraction cancellation (x - x) -> high
        if expr.is_Add:
            terms = list(expr.args)
            n = len(terms)
            for i in range(n):
                for j in range(i + 1, n):
                    try:
                        if sp.simplify(terms[i] + terms[j]) == 0:
                            return "high"
                    except Exception:
                        pass
            return "medium"

        # multiplication contains explicit zero
        if expr.is_Mul:
            for a in expr.args:
                if a.is_Number and a == 0:
                    return "high"
            return "low"

        # symbol -> low risk (needs domain constraints)
        if expr.is_Symbol:
            return "low"

        return "low"

    # -----------------------------
    # Symbolic overflow and risky constructs
    # -----------------------------
    def _symbolic_overflow_checks(self, expr: sp.Expr) -> Dict[str, List[str]]:
        errors: List[str] = []
        warnings: List[str] = []

        for atom in sp.preorder_traversal(expr):
            # numeric constants
            if atom.is_Number:
                try:
                    v = abs(float(atom))
                    if v > self.LARGE_CONSTANT_THRESHOLD:
                        errors.append(f"CRITICAL: Extremely large constant {atom} - overflow risk")
                    elif v > 1e50:
                        warnings.append(f"Large constant {atom} - verify range")
                    elif 0 < v < self.SMALL_CONSTANT_THRESHOLD:
                        warnings.append(f"Very small constant {atom} - underflow risk")
                except Exception:
                    pass

            # exponential: exp(x) or E**x
            if atom.func == sp.exp or (atom.is_Pow and atom.base == sp.E):
                # get exponent
                exponent = atom.args[0] if atom.func == sp.exp else atom.exp
                # nested exp detection
                if exponent.has(sp.exp) or (exponent.is_Pow and exponent.base == sp.E):
                    errors.append(f"CRITICAL: Nested exponential detected: {atom}")
                # numeric exponent checks
                if exponent.is_Number:
                    try:
                        ev = float(exponent)
                        if ev > self.LARGE_EXPONENT_THRESHOLD:
                            errors.append(f"CRITICAL: Large exponential will overflow: {atom}")
                        elif ev > 50:
                            warnings.append(f"Large exponential - overflow risk: {atom}")
                        elif ev < -100:
                            warnings.append(f"Negative exponential may underflow: {atom}")
                    except Exception:
                        pass
                else:
                    warnings.append(f"Exponential detected (symbolic exponent): {atom} - check exponent range")

            # other powers (non-e base)
            if atom.is_Pow and not (atom.base == sp.E):
                exp_val = atom.exp
                if exp_val.is_Number:
                    try:
                        ev = abs(float(exp_val))
                        if ev > self.LARGE_EXPONENT_THRESHOLD:
                            errors.append(f"CRITICAL: Large exponent overflow risk: {atom}")
                        elif ev > 50:
                            warnings.append(f"Large exponent: overflow risk: {atom}")
                        elif ev > 10:
                            warnings.append(f"Power operation with exponent {ev} - validate input range: {atom}")
                    except Exception:
                        pass
                else:
                    warnings.append(f"Symbolic exponent: {atom} - validate exponent range")

            # factorial
            if atom.func == sp.factorial:
                arg = atom.args[0]
                if arg.is_Number:
                    try:
                        n = int(arg)
                        if n > self.MAX_SAFE_FACTORIAL:
                            errors.append(f"CRITICAL: Factorial overflow - factorial({n}) exceeds float64 capacity")
                        elif n > 100:
                            warnings.append(f"Large factorial: factorial({n}) - consider log-space computation")
                    except Exception:
                        warnings.append(f"Factorial with non-integer numeric arg: {atom}")
                else:
                    warnings.append(f"Factorial of symbolic value {arg} - ensure bounded input")

            # hyperbolic functions
            if atom.func in (sp.sinh, sp.cosh):
                warnings.append(f"Hyperbolic function {atom.func.__name__} detected - grows exponentially")

        return {"errors": errors, "warnings": warnings}

    # -----------------------------
    # Symbolic numerical-stability checks
    # -----------------------------
    def _symbolic_stability_checks(self, expr: sp.Expr) -> Dict[str, List[str]]:
        errors: List[str] = []
        warnings: List[str] = []

        # Subtractive cancellation detection (x - x)
        for atom in sp.preorder_traversal(expr):
            if atom.is_Add:
                terms = list(atom.args)
                n = len(terms)
                for i in range(n):
                    for j in range(i + 1, n):
                        try:
                            if sp.simplify(terms[i] + terms[j]) == 0:
                                warnings.append(f"Subtraction detected - cancellation risk: {atom}")
                                break
                        except Exception:
                            pass

        # Square root and log symbolic warnings
        for atom in sp.preorder_traversal(expr):
            # sqrt
            if atom.func == sp.sqrt or (atom.is_Pow and getattr(atom, "exp", None) == sp.Rational(1, 2)):
                warnings.append(f"Square root requires non-negative input: {atom}")
            # log
            if atom.func == sp.log:
                warnings.append(f"Logarithm requires positive input: {atom}")

        # multiple multiplications
        for atom in sp.preorder_traversal(expr):
            if atom.is_Mul:
                if len(atom.args) > 5:
                    warnings.append(f"Multiple multiplications - rounding errors may accumulate: {atom}")
                # product of large numeric factors
                numeric_factors = []
                for a in atom.args:
                    if a.is_Number:
                        try:
                            numeric_factors.append(abs(float(a)))
                        except Exception:
                            pass
                if len([f for f in numeric_factors if f > 1e10]) >= 2:
                    warnings.append(f"Product of very large numbers detected - check for overflow: {atom}")

        return {"errors": errors, "warnings": warnings}

    # -----------------------------
    # Numeric probing (substitute sample values)
    # -----------------------------
    def _numeric_probing(self, expr: sp.Expr) -> Dict[str, Any]:
        errors: List[str] = []
        warnings: List[str] = []
        info: List[str] = []

        # build substitution mapping of sympy Symbols -> sample floats
        subs: Dict[sp.Symbol, float] = {}
        for name, val in self.DEFAULT_SAMPLE_VALUES.items():
            try:
                subs[sp.symbols(name)] = float(val)
            except Exception:
                pass

        # Evaluate the whole expression numerically
        try:
            numeric = expr.evalf(subs=subs)
            info.append(f"Numeric evaluation (sample): {numeric}")

            # complex results
            try:
                if not numeric.is_real and abs(sp.im(numeric)) > 1e-12:
                    warnings.append(f"Numeric evaluation produced complex value: {numeric}")
            except Exception:
                pass

            # magnitude checks
            try:
                nv = float(sp.N(numeric))
                if abs(nv) > self.LARGE_CONSTANT_THRESHOLD:
                    errors.append(f"CRITICAL: Numeric overflow detected: {nv}")
                elif abs(nv) > 1e50:
                    warnings.append(f"Numeric large value detected: {nv}")
                elif 0 < abs(nv) < self.SMALL_CONSTANT_THRESHOLD:
                    warnings.append(f"Numeric underflow risk detected: {nv}")
            except Exception:
                # numeric not convertible to float
                pass

        except ZeroDivisionError:
            errors.append("Validation error: division by zero during numeric probing")
        except Exception as e:
            # numeric evaluation errors are warnings unless they are division by zero
            warnings.append(f"Numeric evaluation failed: {e}")

        # Domain checks for sqrt and log using the subs
        for atom in sp.preorder_traversal(expr):
            # sqrt domain
            if atom.func == sp.sqrt or (atom.is_Pow and getattr(atom, "exp", None) == sp.Rational(1, 2)):
                try:
                    arg_value = atom.args[0].evalf(subs=subs)
                    # if we got a numeric and it's negative -> error
                    if hasattr(arg_value, "is_real") and arg_value.is_real and float(arg_value) < 0:
                        errors.append(f"Square root domain violation: {atom} evaluates to {arg_value}")
                except ZeroDivisionError:
                    errors.append(f"Division by zero while evaluating sqrt arg: {atom}")
                except Exception:
                    pass

            # log domain
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

    # -----------------------------
    # Domain-specific rules
    # -----------------------------
    def _defi_rules(self, expr: sp.Expr) -> Dict[str, Any]:
        errors: List[str] = []
        warnings: List[str] = []
        if expr.has(sp.sqrt):
            warnings.append("DeFi domain: sqrt common in AMM formulas (√(x·y))")
        if self._symbolic_divisors(expr):
            warnings.append("DeFi domain: ensure liquidity denominators are non-zero")
        warnings.append("DeFi domain: validate all amounts and liquidity values are positive")
        return {"valid": True, "errors": errors, "warnings": warnings}

    def _finance_rules(self, expr: sp.Expr) -> Dict[str, Any]:
        errors: List[str] = []
        warnings: List[str] = []
        if expr.has(sp.log):
            warnings.append("Finance domain: logarithm detected (log-returns)")
        if expr.has(sp.sqrt):
            warnings.append("Finance domain: square root detected (volatility)")
        warnings.append("Finance domain: ensure risk metrics are non-negative")
        return {"valid": True, "errors": errors, "warnings": warnings}

    def _esg_rules(self, expr: sp.Expr) -> Dict[str, Any]:
        errors: List[str] = []
        warnings: List[str] = ["ESG domain: ensure scores are in valid range (typically 0-100)"]
        if expr.is_Add or expr.is_Mul:
            warnings.append("ESG scoring detected - ensure proper normalization")
        return {"valid": True, "errors": errors, "warnings": warnings}

    def _risk_rules(self, expr: sp.Expr) -> Dict[str, Any]:
        errors: List[str] = []
        warnings: List[str] = ["Risk domain: Value-at-Risk should be positive"]
        if expr.has(sp.exp) and expr.has(sp.Mul):
            warnings.append("Risk domain: exponential in probability distributions")
        return {"valid": True, "errors": errors, "warnings": warnings}

    def _default_rules(self, expr: sp.Expr) -> Dict[str, Any]:
        return {
            "valid": True,
            "errors": [],
            "warnings": ["Default validation applied - specify domain for enhanced checks"],
        }

    # -----------------------------
    # Scoring & summary
    # -----------------------------
    def _calculate_score(self, results: Dict[str, Any]) -> int:
        score = 0
        if results.get("syntactically_valid"):
            score += 25
        if results.get("dimensionally_consistent"):
            score += 25
        if results.get("domain_valid"):
            score += 25
        if results.get("numerically_stable"):
            score += 25

        # penalties (errors are heavy)
        score -= len(results.get("errors", [])) * 50
        score -= len(results.get("warnings", [])) * 1

        return max(0, min(100, score))

    def get_validation_summary(self, results: Dict[str, Any]) -> str:
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
        for name, ok in checks:
            lines.append(f"{'✓' if ok else '✗'} {name}")
        lines.append("")
        if results.get("errors"):
            lines.append("ERRORS:")
            for i, e in enumerate(results["errors"], 1):
                lines.append(f"  {i}. {e}")
            lines.append("")
        if results.get("warnings"):
            lines.append("WARNINGS:")
            for i, w in enumerate(results["warnings"], 1):
                lines.append(f"  {i}. {w}")
            lines.append("")
        if results.get("info"):
            lines.append("INFO:")
            for i, inf in enumerate(results["info"], 1):
                lines.append(f"  {i}. {inf}")
            lines.append("")
        lines.append("=" * 60)
        return "\n".join(lines)


# If executed directly, run a quick sanity harness (does not replace pytest)
if __name__ == "__main__":
    v = EnhancedSymbolicValidator()
    samples = [
        r"x^{-1}",
        r"e^{x}",
        r"e^{500}",
        r"x^{1000}",
        "180!",
        r"e^{e^{x}}",
        r"e^{-200}",
        r"\sqrt{x}",
        r"a * b * c * d * e * f * g",
        r"\frac{1}{x-x}",
        r"\sinh(x)",
        r"\log(x)",
    ]
    for s in samples:
        print("\n" + "-" * 60)
        print("Formula:", s)
        res = v.validate(s)
        print(v.get_validation_summary(res))
