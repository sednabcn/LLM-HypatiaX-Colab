#!/usr/bin/env python3
"""
Validator scaffold for symbolic + numeric validation.

Provides a small, reusable toolkit you can plug into domain validators:
- safe_sympify: parse with explicit locals (avoid ambiguous names)
- inspect_expr: structural inspection helpers (free symbols, denominators, atoms)
- lambdify_and_eval: safe numeric evaluation with exception capture
- ValidatorScaffold: small class orchestrating parse -> inspect -> numeric checks

Usage:
    from tools.validation.validator_scaffold import ValidatorScaffold
    scaffold = ValidatorScaffold(allowed_funcs={"sqrt": sp.sqrt})
    expr = scaffold.parse("(r - rf) / sigma", var_names=["r", "rf", "sigma"])
    info = scaffold.inspect(expr)
    numeric = scaffold.lambdify_and_eval(expr, {"r": np.array([0.1]), "rf": np.array([0.02]), "sigma": np.array([0.15])})
"""

import logging
from typing import Any, Dict, Iterable, List, Optional, Sequence, Tuple

import numpy as np
import sympy as sp

logger = logging.getLogger(__name__)


def safe_sympify(
    expression: str, var_names: Optional[Iterable[str]] = None, extra_funcs: Optional[Dict[str, Any]] = None
) -> sp.Expr:
    """
    Sympify expression using explicit symbol locals to avoid parsing ambiguities.
    - var_names: list of variable names to pre-declare as symbols
    - extra_funcs: mapping of allowed function names to SymPy callables (sqrt, sin, ...)
    """
    locals_d = {}
    if var_names:
        for n in var_names:
            # Use sp.symbols to allow multipart names and underscores safely
            try:
                locals_d[n] = sp.symbols(n)
            except Exception:
                locals_d[n] = sp.Symbol(n)
    if extra_funcs:
        locals_d.update(extra_funcs)
    # Common math functions for convenience (won't overwrite if provided in extra_funcs)
    for fn in ("sqrt", "sin", "cos", "log", "exp"):
        if fn not in locals_d:
            locals_d[fn] = getattr(sp, fn)
    return sp.sympify(expression, locals=locals_d)


def get_free_symbols(expr: sp.Expr) -> List[str]:
    """Return sorted list of free symbol names in expression."""
    return sorted({str(s) for s in expr.free_symbols})


def find_denominator_bases(expr: sp.Expr) -> List[sp.Expr]:
    """
    Return bases that appear as Pow(..., -1) or as factors with negative exponents.
    Example: 1/x -> returns [x]; a * b**-1 -> returns [b]
    """
    bases = []
    for atom in sp.preorder_traversal(expr):
        # Pow with negative exponent
        if getattr(atom, "is_Pow", False) and getattr(atom, "exp", None) is not None:
            try:
                if float(atom.exp) == -1.0:
                    bases.append(atom.base)
            except Exception:
                # Non-numeric exponent (e.g., -1 may be Integer), check equality to -1
                if atom.exp == -1:
                    bases.append(atom.base)
        # Mul with arg being a Pow(-1) will be seen via traversal but include defensive checks
    # Deduplicate preserving canonical string order
    seen = set()
    out = []
    for b in bases:
        key = str(b)
        if key not in seen:
            seen.add(key)
            out.append(b)
    return out


def pretty_expr(expr: sp.Expr) -> str:
    """Return a compact printable representation useful in logs and errors."""
    try:
        return sp.pretty(expr, use_unicode=False)
    except Exception:
        return str(expr)


def _ordered_symbol_list(expr: sp.Expr, prefer: Optional[Sequence[str]] = None) -> List[str]:
    """
    Return a deterministic ordering of symbol names to pass to lambdify.
    If 'prefer' supplied, try to put those names first (useful for tests).
    """
    syms = get_free_symbols(expr)
    if not prefer:
        return syms
    ordered = []
    for p in prefer:
        if p in syms:
            ordered.append(p)
    for s in syms:
        if s not in ordered:
            ordered.append(s)
    return ordered


def lambdify_and_eval(
    expr: sp.Expr,
    test_data: Dict[str, np.ndarray],
    symbol_order: Optional[Sequence[str]] = None,
    modules: Optional[str] = "numpy",
) -> Dict[str, Any]:
    """
    Safely lambdify the expression and evaluate it with provided test_data.
    Returns a dict:
      {
        "success": bool,
        "value": numpy array or None,
        "error": str or None,
        "exception": exception object or None,
        "symbol_order": list of symbols used
      }
    Behavior:
      - Aligns arguments using symbol_order or deterministic order from the expr.
      - If lambdify raises or evaluation raises (ZeroDivisionError, FloatingPointError, etc.),
        captures exception and returns success=False with diagnostic.
      - If evaluation returns non-finite values (nan/inf), still returns success=True but includes 'non_finite': True.
    """
    result: Dict[str, Any] = {
        "success": False,
        "value": None,
        "error": None,
        "exception": None,
        "symbol_order": None,
        "non_finite": False,
    }
    try:
        if symbol_order is None:
            symbol_order = _ordered_symbol_list(expr)
        else:
            symbol_order = list(symbol_order)
        result["symbol_order"] = symbol_order

        # Build argument list aligned to order, error if missing
        args = []
        for s in symbol_order:
            if s not in test_data:
                raise KeyError(f"Missing test_data for symbol '{s}' required by expression")
            args.append(test_data[s])

        # Lambdify
        f = sp.lambdify(symbol_order, expr, modules=modules)

        # Evaluate - allow numpy exceptions to be raised as Python exceptions
        try:
            value = f(*args)
        except Exception as e:
            # Some numpy ops raise warnings instead of errors; we still capture the exception
            result["error"] = f"Numeric evaluation error: {type(e).__name__}: {e}"
            result["exception"] = e
            return result

        # Convert to numpy array if scalar
        try:
            arr = np.array(value)
        except Exception:
            arr = value

        # Check finiteness
        try:
            if np.any(~np.isfinite(arr)):
                result["non_finite"] = True
        except Exception:
            # If arr isn't array-like, attempt scalar check
            try:
                if not np.isfinite(float(arr)):
                    result["non_finite"] = True
            except Exception:
                pass

        result["success"] = True
        result["value"] = arr
        return result

    except Exception as e:
        result["error"] = f"Preparation error: {type(e).__name__}: {e}"
        result["exception"] = e
        return result


class ValidatorScaffold:
    """
    Small orchestrator combining parsing, inspection and numeric testing.

    API:
      - parse(expression_str, var_names)
      - inspect(expr): returns dict with free_symbols and denominators
      - numeric_test(expr, test_data, prefer_order=None): returns lambdify_and_eval result
    """

    def __init__(self, allowed_funcs: Optional[Dict[str, Any]] = None):
        self.allowed_funcs = allowed_funcs or {}

    def parse(self, expression: str, var_names: Optional[Iterable[str]] = None) -> sp.Expr:
        """Parse safely, raising the underlying exception on failure."""
        return safe_sympify(expression, var_names=var_names, extra_funcs=self.allowed_funcs)

    def inspect(self, expr: sp.Expr) -> Dict[str, Any]:
        """Return quick inspection info useful for validations and diagnostics."""
        info: Dict[str, Any] = {}
        info["free_symbols"] = get_free_symbols(expr)
        denoms = find_denominator_bases(expr)
        info["denominators"] = [str(d) for d in denoms]
        info["pretty"] = pretty_expr(expr)
        return info

    def numeric_test(
        self, expr: sp.Expr, test_data: Dict[str, np.ndarray], prefer_order: Optional[Sequence[str]] = None
    ) -> Dict[str, Any]:
        """Run lambdified numeric tests and return the diagnostic dict from lambdify_and_eval."""
        order = prefer_order if prefer_order is not None else None
        return lambdify_and_eval(expr, test_data, symbol_order=order)
