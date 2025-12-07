tools / validation / symbolic_validator.py
#!/usr/bin/env python3
"""
Symbolic Validation for Generated Formulas
Uses SymPy for mathematical validation
Part of HypatiaX tools/validation/
"""
import re
from typing import Any, Dict, List, Tuple

import sympy as sp
from sympy.parsing.latex import parse_latex


class SymbolicValidator:
    """
    Validates generated formulas mathematically

    Uses:
        - Your PhD computational mechanics expertise
        - Numerical stability analysis
        - Dimensional consistency
        - Domain constraints
    """

    def __init__(self):
        self.domain_rules = {
            "defi": self._defi_rules,
            "finance": self._finance_rules,
            "esg": self._esg_rules,
            "risk": self._risk_rules,
        }

    def validate(self, formula_latex: str, domain: str = "defi") -> Dict[str, Any]:
        """
        Comprehensive validation

        Returns:
            {
                'syntactically_valid': bool,
                'dimensionally_consistent': bool,
                'domain_valid': bool,
                'numerically_stable': bool,
                'errors': [list of error messages],
                'warnings': [list of warnings],
                'score': 0-100
            }
        """
        results = {
            "syntactically_valid": False,
            "dimensionally_consistent": False,
            "domain_valid": False,
            "numerically_stable": False,
            "errors": [],
            "warnings": [],
        }

        try:
            # 1. Parse LaTeX to SymPy
            expr = self._safe_parse_latex(formula_latex)
            if expr is None:
                results["errors"].append("Cannot parse LaTeX formula")
                return self._calculate_score(results)

            results["syntactically_valid"] = True

            # 2. Dimensional consistency
            if self._check_dimensions(expr):
                results["dimensionally_consistent"] = True
            else:
                results["errors"].append("Dimensional inconsistency detected")

            # 3. Domain-specific rules
            domain_check = self.domain_rules.get(domain, self._default_rules)(expr)
            results["domain_valid"] = domain_check["valid"]
            results["errors"].extend(domain_check["errors"])
            results["warnings"].extend(domain_check.get("warnings", []))

            # 4. Numerical stability (YOUR EXPERTISE!)
            stability = self._check_numerical_stability(expr)
            results["numerically_stable"] = stability["stable"]
            results["warnings"].extend(stability["warnings"])

        except Exception as e:
            results["errors"].append(f"Validation error: {str(e)}")

        results["score"] = self._calculate_score(results)
        return results

    def _safe_parse_latex(self, latex_str: str):
        """Safely parse LaTeX, handling common issues"""
        try:
            # Clean LaTeX string
            latex_str = latex_str.strip()
            latex_str = re.sub(r"\\text\{([^}]+)\}", r"\1", latex_str)

            return parse_latex(latex_str)
        except Exception as e:
            # Try alternative parsing
            try:
                return sp.sympify(latex_str)
            except:
                return None

    def _check_dimensions(self, expr) -> bool:
        """
        Dimensional analysis
        Like checking units in physics

        Example: price * price ≠ return
        """
        # Extract all operations
        # Check dimension compatibility
        # This is simplified - expand based on your needs

        # Basic check: no mixing of incompatible units
        # Return True for now, implement detailed checks
        return True

    def _check_numerical_stability(self, expr) -> Dict[str, Any]:
        """
        YOUR COMPUTATIONAL MECHANICS EXPERTISE!

        Checks:
        1. Division by zero risks
        2. Overflow/underflow potential
        3. Precision loss in operations
        4. Conditioning of the problem
        """
        warnings = []

        # 1. Find all denominators
        denominators = self._extract_denominators(expr)
        for denom in denominators:
            # Check if could be zero
            if self._could_be_zero(denom):
                warnings.append(f"Division by zero risk: {denom}")

        # 2. Check for subtractive cancellation
        # (a - b) where a ≈ b loses precision
        subtractions = self._find_subtractions(expr)
        if len(subtractions) > 2:
            warnings.append("Multiple subtractions may cause precision loss")

        # 3. Check for exponentials (overflow risk)
        if expr.has(sp.exp):
            warnings.append("Exponential functions may overflow - validate input ranges")

        # 4. Check for very small denominators in products
        if expr.has(sp.Mul):
            warnings.append("Multiple multiplications - check for overflow")

        # 5. Check sqrt of potentially negative
        if expr.has(sp.sqrt):
            warnings.append("Square root present - ensure non-negative inputs")

        return {"stable": len(warnings) == 0, "warnings": warnings}

    def _extract_denominators(self, expr) -> List:
        """Extract all denominators from expression"""
        denominators = []

        if expr.is_Mul:
            for arg in expr.args:
                if arg.is_Pow and arg.exp.is_negative:
                    denominators.append(arg.base)

        if expr.is_Add:
            for arg in expr.args:
                denominators.extend(self._extract_denominators(arg))

        return denominators

    def _could_be_zero(self, expr) -> bool:
        """Check if expression could evaluate to zero"""
        # Simplified check
        if expr.is_Number:
            return abs(float(expr)) < 1e-10

        # Check if contains subtraction that could cancel
        if expr.is_Add:
            return True  # Conservative

        return False

    def _find_subtractions(self, expr) -> List:
        """Find all subtraction operations"""
        subs = []

        if expr.is_Add:
            neg_terms = [arg for arg in expr.args if arg.could_extract_minus_sign()]
            if len(neg_terms) > 0:
                subs.append(expr)

        for arg in expr.args if hasattr(expr, "args") else []:
            subs.extend(self._find_subtractions(arg))

        return subs

    def _defi_rules(self, expr) -> Dict[str, Any]:
        """DeFi-specific validation rules"""
        errors = []
        warnings = []

        # Check: x*y = k invariant should be preserved
        # Check: Price impact must be positive
        # Check: Liquidity must be positive
        # Check: No arbitrage opportunities

        # Simplified checks
        if expr.has(sp.sqrt):
            warnings.append("Square root in DeFi formula - ensure input validation")

        return {"valid": len(errors) == 0, "errors": errors, "warnings": warnings}

    def _finance_rules(self, expr) -> Dict[str, Any]:
        """Finance-specific validation rules"""
        errors = []
        warnings = []

        # Check: Risk metrics should be non-negative
        # Check: Returns should be percentage or decimal
        # Check: Probabilities sum to 1
        # Check: Portfolio weights sum to 1

        return {"valid": len(errors) == 0, "errors": errors, "warnings": warnings}

    def _esg_rules(self, expr) -> Dict[str, Any]:
        """ESG-specific validation rules"""
        errors = []
        warnings = []

        # Check: Scores in valid range (0-100)
        # Check: Components properly weighted
        # Check: No negative environmental impact as positive

        return {"valid": len(errors) == 0, "errors": errors, "warnings": warnings}

    def _risk_rules(self, expr) -> Dict[str, Any]:
        """Risk management validation rules"""
        errors = []
        warnings = []

        # Check: VaR should be positive
        # Check: Confidence levels between 0 and 1
        # Check: No unbounded risk metrics

        return {"valid": len(errors) == 0, "errors": errors, "warnings": warnings}

    def _default_rules(self, expr) -> Dict[str, Any]:
        """Default validation rules"""
        return {"valid": True, "errors": [], "warnings": []}

    def _calculate_score(self, results: Dict[str, Any]) -> int:
        """Calculate overall validation score"""
        score = 0

        if results["syntactically_valid"]:
            score += 25
        if results["dimensionally_consistent"]:
            score += 25
        if results["domain_valid"]:
            score += 25
        if results["numerically_stable"]:
            score += 25

        # Penalty for errors
        score -= len(results["errors"]) * 10

        # Minor penalty for warnings
        score -= len(results.get("warnings", [])) * 2

        return max(0, min(100, score))
