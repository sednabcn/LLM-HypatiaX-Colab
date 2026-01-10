#!/usr/bin/env python3
"""
Debug script to isolate the risk domain parsing issue
"""
import re

import sympy as sp
from sympy.parsing.latex import parse_latex


def test_parse_sigma_sqrt():
    """Test parsing of \\sigma \\cdot \\sqrt{t}"""

    latex_str = r"\sigma \cdot \sqrt{t}"
    print(f"Original LaTeX: {latex_str}")
    print("=" * 60)

    # Try method 1: Direct parse_latex
    print("\n1. Direct parse_latex:")
    try:
        expr = parse_latex(latex_str)
        print(f"   SUCCESS: {expr}")
        return expr
    except Exception as e:
        print(f"   FAILED: {e}")

    # Try method 2: parse_latex with strict=False
    print("\n2. parse_latex(strict=False):")
    try:
        expr = parse_latex(latex_str, strict=False)
        print(f"   SUCCESS: {expr}")
        return expr
    except Exception as e:
        print(f"   FAILED: {e}")

    # Try method 3: Manual conversion
    print("\n3. Manual LaTeX to Python conversion:")
    try:
        # Step by step conversion
        current = latex_str
        print(f"   Start: {current}")

        # Greek letters first
        current = current.replace(r"\sigma", "sigma")
        print(f"   After Greek: {current}")

        # Operators
        current = current.replace(r"\cdot", "*")
        print(f"   After operators: {current}")

        # Square root
        current = re.sub(r"\\sqrt\{([^{}]+)\}", r"sqrt(\1)", current)
        print(f"   After sqrt: {current}")

        # Clean up remaining backslashes and braces
        current = re.sub(r"\\([a-zA-Z]+)", r"\1", current)
        current = current.replace("{", "(").replace("}", ")")
        print(f"   Final Python: {current}")

        # Try to parse with sympify
        locals_dict = {
            "sigma": sp.Symbol("sigma"),
            "t": sp.Symbol("t"),
            "sqrt": sp.sqrt,
        }
        expr = sp.sympify(current, locals=locals_dict, evaluate=False)
        print(f"   SUCCESS: {expr}")
        return expr
    except Exception as e:
        print(f"   FAILED: {e}")
        import traceback

        traceback.print_exc()

    return None


if __name__ == "__main__":
    result = test_parse_sigma_sqrt()
    if result:
        print("\n" + "=" * 60)
        print(f"FINAL RESULT: {result}")
        print(f"Type: {type(result)}")
        print(f"Is valid SymPy expression: {isinstance(result, sp.Expr)}")
    else:
        print("\n" + "=" * 60)
        print("PARSING FAILED")
