#!/usr/bin/env python3
"""
Diagnostic script to understand what's happening with parsing
"""
import sympy as sp
from sympy.parsing.latex import parse_latex

test_cases = [
    (r"x^{-1}", "Negative exponent"),
    (r"e^{500}", "Large exponential"),
    (r"x^{1000}", "Large exponent"),
    ("180!", "Factorial"),
    (r"e^{e^{x}}", "Nested exponential"),
    (r"e^{-200}", "Underflow"),
    (r"w_1 \cdot E + w_2 \cdot S + w_3 \cdot G", "ESG"),
    (r"S \cdot N(d_1) - K \cdot e^{-r \cdot t} \cdot N(d_2)", "Black-Scholes"),
    (r"\frac{\sqrt{a + b}}{c - d} \cdot e^{-x}", "Mixed operations"),
]

print("=" * 70)
print("DIAGNOSTIC: Testing LaTeX Parsing")
print("=" * 70)

for latex_str, desc in test_cases:
    print(f"\n{desc}: {latex_str}")
    print("-" * 70)

    # Try direct parse_latex
    try:
        expr = parse_latex(latex_str)
        print(f"✓ parse_latex succeeded: {expr}")
        print(f"  Type: {type(expr)}")
        print(f"  Has E: {expr.has(sp.E)}")

        # Check for power operations
        powers = [atom for atom in sp.preorder_traversal(expr) if atom.is_Pow]
        print(f"  Power operations: {len(powers)}")
        for p in powers[:3]:
            print(f"    - {p.base}^{p.exp}")

        # Check for exponentials
        exps = [atom for atom in sp.preorder_traversal(expr) if atom.func == sp.exp]
        print(f"  Exponential functions: {len(exps)}")

        # Check for E^x
        e_pows = [
            atom
            for atom in sp.preorder_traversal(expr)
            if atom.is_Pow and atom.base == sp.E
        ]
        print(f"  E^x operations: {len(e_pows)}")
        for ep in e_pows[:3]:
            print(f"    - E^{ep.exp}")

        # Check for factorials
        facts = [
            atom for atom in sp.preorder_traversal(expr) if atom.func == sp.factorial
        ]
        print(f"  Factorials: {len(facts)}")

    except Exception as e:
        print(f"✗ parse_latex failed: {e}")

        # Try sympify
        try:
            expr = sp.sympify(latex_str, evaluate=False)
            print(f"✓ sympify succeeded: {expr}")
        except Exception as e2:
            print(f"✗ sympify also failed: {e2}")

print("\n" + "=" * 70)
print("DIAGNOSTIC: Testing Specific Parsing Issues")
print("=" * 70)

# Test e vs E
print("\n1. Testing 'e' notation:")
test_e = [
    "e^500",
    "E^500",
    r"e^{500}",
    r"E^{500}",
    "exp(500)",
]
for t in test_e:
    try:
        expr = (
            parse_latex(t) if "\\" in t or "^" in t else sp.sympify(t, evaluate=False)
        )
        has_E = expr.has(sp.E)
        has_exp = any(atom.func == sp.exp for atom in sp.preorder_traversal(expr))
        print(f"  {t:15s} -> {str(expr):20s} | has_E={has_E}, has_exp={has_exp}")
    except Exception as e:
        print(f"  {t:15s} -> FAILED: {e}")

# Test N() function in Black-Scholes
print("\n2. Testing N(x) function:")
try:
    expr = parse_latex(r"N(d_1)")
    print(f"  N(d_1) parsed as: {expr}, type: {type(expr)}")
except Exception as e:
    print(f"  N(d_1) failed: {e}")

# Test subscripts
print("\n3. Testing subscripts:")
test_subs = [r"w_1", r"d_1", r"w_{10}"]
for t in test_subs:
    try:
        expr = parse_latex(t)
        print(f"  {t:10s} -> {expr}")
    except Exception as e:
        print(f"  {t:10s} -> FAILED: {e}")
