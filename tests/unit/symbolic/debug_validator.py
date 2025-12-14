#!/usr/bin/env python3
"""
Debug script to understand parsing behavior and create working fixes
"""
import sympy as sp
from sympy.parsing.latex import parse_latex


def debug_parse(latex_str):
    """Debug what SymPy actually parses"""
    print(f"\n{'='*60}")
    print(f"Testing: {latex_str}")
    print(f"{'='*60}")

    try:
        expr = parse_latex(latex_str)
        print(f"✓ Parsed successfully: {expr}")
        print(f"  Type: {type(expr)}")
        print(f"  Expr type: {expr.__class__.__name__}")

        # Analyze structure
        print(f"\n  Structure analysis:")
        for atom in sp.preorder_traversal(expr):
            if atom.is_Pow:
                print(f"    Power: {atom} = {atom.base}^{atom.exp}")
                print(f"      Base: {atom.base} (type: {atom.base.__class__.__name__})")
                print(f"      Exp: {atom.exp} (type: {atom.exp.__class__.__name__})")
                print(f"      Base is E: {atom.base == sp.E}")
                print(f"      Exp is negative: {atom.exp.is_negative if hasattr(atom.exp, 'is_negative') else 'N/A'}")
            elif atom.func == sp.exp:
                print(f"    Exp function: {atom}")
                print(f"      Arg: {atom.args[0]}")
            elif atom.func == sp.factorial:
                print(f"    Factorial: {atom}")
                print(f"      Arg: {atom.args[0]}")

        return expr
    except Exception as e:
        print(f"✗ Parse failed: {e}")
        return None


def test_all_cases():
    """Test all the problematic cases"""
    test_cases = [
        r"x^{-1}",  # Negative exponent
        r"e^{500}",  # Large exponential E^x
        r"x^{1000}",  # Large exponent
        "180!",  # Factorial
        r"e^{e^{x}}",  # Nested exponential
        r"e^{-200}",  # Underflow
        r"\exp(500)",  # exp function
        r"S \cdot N(d_1) - K \cdot e^{-r \cdot t} \cdot N(d_2)",  # Black-Scholes
    ]

    for case in test_cases:
        debug_parse(case)


if __name__ == "__main__":
    print("DEBUGGING SYMPY PARSING BEHAVIOR")
    test_all_cases()

    print("\n\n" + "=" * 60)
    print("KEY FINDINGS:")
    print("=" * 60)

    # Test specific parsing issues
    print("\n1. Testing e^{500} parsing:")
    expr = parse_latex(r"e^{500}")
    print(f"   Result: {expr}")
    print(f"   Is Pow? {expr.is_Pow if hasattr(expr, 'is_Pow') else False}")
    if hasattr(expr, "base"):
        print(f"   Base: {expr.base}")
        print(f"   Base == sp.E? {expr.base == sp.E}")
        print(f"   Base == sp.exp(1)? {expr.base == sp.exp(1)}")

    print("\n2. Testing x^{-1} parsing:")
    expr = parse_latex(r"x^{-1}")
    print(f"   Result: {expr}")
    print(f"   Is Pow? {expr.is_Pow}")
    print(f"   Exponent: {expr.exp}")
    print(f"   Exp is negative? {expr.exp.is_negative}")

    print("\n3. Testing 180! parsing:")
    expr = parse_latex("180!")
    print(f"   Result: {expr}")
    print(f"   Func: {expr.func}")
    print(f"   Is factorial? {expr.func == sp.factorial}")
