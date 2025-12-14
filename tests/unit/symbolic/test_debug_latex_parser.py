#!/usr/bin/env python3
"""
Quick debug script to test LaTeX parsing
"""
import re

import sympy as sp
from sympy.parsing.latex import parse_latex


def test_parse(latex_str):
    """Test parsing with debug output"""
    print(f"\n{'='*60}")
    print(f"Testing: {repr(latex_str)}")
    print(f"{'='*60}")

    # Try parse_latex directly
    try:
        result = parse_latex(latex_str)
        print(f"✓ parse_latex worked: {result}")
        return result
    except Exception as e:
        print(f"✗ parse_latex failed: {e}")

    # Try sympify
    try:
        result = sp.sympify(latex_str, evaluate=False)
        print(f"✓ sympify worked: {result}")
        return result
    except Exception as e:
        print(f"✗ sympify failed: {e}")

    return None


# Test cases
test_cases = [
    "x+1",
    "x + y",
    r"\frac{1}{0}",
    r"\frac{x}{y}",
    r"e^{x}",
    r"x^{-1}",
    "1e150",
    "a - b",
    r"\sqrt{x}",
    r"\log(x)",
]

for test in test_cases:
    result = test_parse(test)
    if result is None:
        print("⚠ FAILED TO PARSE")

print("\n" + "=" * 60)
print("CHECKING SYMPY VERSION")
print("=" * 60)
print(f"SymPy version: {sp.__version__}")

# Check if parse_latex is available
try:
    from sympy.parsing.latex import parse_latex

    print("✓ parse_latex is available")
except ImportError as e:
    print(f"✗ parse_latex not available: {e}")
