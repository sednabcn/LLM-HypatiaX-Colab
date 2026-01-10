#!/usr/bin/env python3
"""
Comprehensive debug to trace the exact failure point
"""
import re

import sympy as sp
from sympy.parsing.latex import parse_latex
from sympy.parsing.sympy_parser import (
    convert_xor,
    implicit_multiplication_application,
    parse_expr,
    standard_transformations,
)


def auto_symbolize(expr_str: str):
    """Test the auto_symbolize function"""
    tokens = re.findall(r"[A-Za-z_]\w*", expr_str)

    locals_dict = {}

    # Common built-in functions that should use SymPy's versions
    builtin_functions = {
        "exp": sp.exp,
        "log": sp.log,
        "sqrt": sp.sqrt,
        "sin": sp.sin,
        "cos": sp.cos,
        "tan": sp.tan,
        "sinh": sp.sinh,
        "cosh": sp.cosh,
        "tanh": sp.tanh,
    }

    # Constants
    builtin_constants = {
        "E": sp.E,
        "pi": sp.pi,
        "I": sp.I,
    }

    # Greek letters that should be symbols
    greek_symbols = {
        "sigma",
        "mu",
        "alpha",
        "beta",
        "gamma",
        "delta",
        "Delta",
        "lambda_var",
        "Phi",
        "phi",
        "theta",
        "tau",
        "rho",
        "epsilon",
        "kappa",
        "nu",
        "omega",
        "Omega",
        "zeta",
        "eta",
        "xi",
        "Xi",
        "psi",
        "Psi",
        "chi",
    }

    # Add all built-in functions to locals_dict
    locals_dict.update(builtin_functions)
    locals_dict.update(builtin_constants)

    for t in tokens:
        # Skip if already defined
        if t in locals_dict:
            continue

        # Skip if it's a builtin we already handled
        if t in builtin_functions or t in builtin_constants:
            continue

        # Greek letters should be symbols
        if t in greek_symbols:
            locals_dict[t] = sp.Symbol(t)
        # If token appears like a function: N(d1), Phi(x)
        elif re.search(rf"{t}\s*\(", expr_str):
            locals_dict[t] = sp.Function(t)
        else:
            locals_dict[t] = sp.Symbol(t)

    return locals_dict


def latex_to_python(latex_str: str) -> str:
    """Convert LaTeX notation to Python/SymPy format"""
    current = latex_str

    # Handle Greek letters and special symbols FIRST
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

    # Replace operators EARLY
    current = current.replace("\\cdot", "*")
    current = current.replace("\\times", "*")
    current = current.replace("\\div", "/")

    # Handle fractions
    max_iterations = 10
    for _ in range(max_iterations):
        new = re.sub(
            r"\\frac\{([^{}]*(?:\{[^{}]*\}[^{}]*)*)\}\{([^{}]*(?:\{[^{}]*\}[^{}]*)*)\}",
            r"((\1)/(\2))",
            current,
        )
        if new == current:
            break
        current = new

    # Handle square roots
    current = re.sub(r"\\sqrt\{([^{}]+)\}", r"sqrt(\1)", current)

    # Handle subscripts
    current = re.sub(r"([a-zA-Z])_\{([^{}]+)\}", r"\1\2", current)
    current = re.sub(r"([a-zA-Z])_([a-zA-Z0-9]+)", r"\1\2", current)

    # Handle powers
    current = re.sub(r"\^\{([^{}]+)\}", r"**(\1)", current)
    current = re.sub(r"\^([a-zA-Z0-9])", r"**\1", current)

    # Function replacements
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

    # Final cleanup
    current = current.replace("{", "(").replace("}", ")")

    return current


def test_safe_parse():
    """Test the complete parsing pipeline"""
    latex_str = r"\sigma \cdot \sqrt{t}"

    print(f"Input: {latex_str}")
    print("=" * 70)

    # Step 1: LaTeX to Python
    print("\n1. LaTeX to Python conversion:")
    try:
        py_str = latex_to_python(latex_str)
        print(f"   SUCCESS: {py_str}")
    except Exception as e:
        print(f"   FAILED: {e}")
        import traceback

        traceback.print_exc()
        return None

    # Step 2: Auto-symbolize
    print("\n2. Auto-symbolize:")
    try:
        locals_dict = auto_symbolize(py_str)
        print(f"   SUCCESS: Created {len(locals_dict)} symbols/functions")
        print(f"   Keys: {list(locals_dict.keys())}")
    except Exception as e:
        print(f"   FAILED: {e}")
        import traceback

        traceback.print_exc()
        return None

    # Step 3: Sympify
    print("\n3. Sympify with locals:")
    try:
        expr = sp.sympify(py_str, locals=locals_dict, evaluate=False)
        print(f"   SUCCESS: {expr}")
        print(f"   Type: {type(expr)}")
        print(f"   Is None: {expr is None}")
        print(f"   Is valid Expr: {isinstance(expr, sp.Expr)}")
        return expr
    except Exception as e:
        print(f"   FAILED: {e}")
        import traceback

        traceback.print_exc()
        return None


if __name__ == "__main__":
    result = test_safe_parse()

    print("\n" + "=" * 70)
    if result is not None and isinstance(result, sp.Expr):
        print(f"✓ PARSING SUCCESSFUL")
        print(f"Final expression: {result}")
    else:
        print(f"✗ PARSING FAILED")
        print(f"Result: {result}")
