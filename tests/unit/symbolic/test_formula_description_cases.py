import pytest
import sympy as sp

from hypatiax.tools.symbolic.ensemble import EnhancedSymbolicValidator

validator = EnhancedSymbolicValidator()

# Test cases: (formula, description, expected results)
test_cases = [
    (None, "Empty input (None)", {"syntactically_valid": False}),
    ("", "Empty string", {"syntactically_valid": False}),
    (" ", "Whitespace only", {"syntactically_valid": False}),
    (r"x^{-1}", "Negative exponent", {"syntactically_valid": True, "warnings": True}),
    (r"e^{x}", "Exponential function", {"syntactically_valid": True, "warnings": True}),
    (r"e^{500}", "Large exponential", {"syntactically_valid": True, "errors": True}),
    (r"x^{1000}", "Large exponent", {"syntactically_valid": True, "errors": True}),
    ("180!", "Factorial overflow", {"syntactically_valid": True, "errors": True}),
    (r"e^{e^{x}}", "Nested exponential", {"syntactically_valid": True, "errors": True}),
    (r"e^{-200}", "Underflow", {"syntactically_valid": True, "warnings": True}),
    (r"\sqrt{x}", "Square root", {"syntactically_valid": True, "warnings": True}),
    (
        "a * b * c * d * e * f * g",
        "Multiple multiplications",
        {"syntactically_valid": True, "warnings": True},
    ),
    (
        r"\frac{x}{0}",
        "Simple division by zero",
        {"syntactically_valid": True, "errors": True},
    ),
    (
        r"x - x",
        "Subtraction cancellation",
        {"syntactically_valid": True, "warnings": True},
    ),
    (
        r"\frac{x+y}{y - y}",
        "Complex denominator cancellation",
        {"syntactically_valid": True, "errors": True},
    ),
    ("1 / y", "Safe division", {"syntactically_valid": True, "errors": False}),
    (
        r"\frac{a}{b} * \frac{c}{d}",
        "Multiple divisions",
        {"syntactically_valid": True, "warnings": True},
    ),
    (
        r"\sinh(x)",
        "Hyperbolic function",
        {"syntactically_valid": True, "warnings": True},
    ),
    (r"\ln(x)", "Logarithm", {"syntactically_valid": True, "warnings": True}),
    (
        "x + y - z",
        "Subtraction for numerical stability",
        {"syntactically_valid": True, "warnings": True},
    ),
    (
        r"\sqrt{x + 1}",
        "Square root domain",
        {"syntactically_valid": True, "warnings": True},
    ),
    (r"\log(y)", "Logarithm domain", {"syntactically_valid": True, "warnings": True}),
    (
        "x * y / z",
        "Basic valid formula",
        {"syntactically_valid": True, "errors": False},
    ),
    (
        r"\sqrt{x * y}",
        "DeFi AMM constant product",
        {"syntactically_valid": True, "warnings": True},
    ),
    (
        r"S = K * exp(-r * T) * N(d2) - S0 * N(d1)",
        "Black-Scholes",
        {"syntactically_valid": True, "warnings": True},
    ),
    (
        r"Sharpe = (R_p - R_f)/\sigma_p",
        "Sharpe ratio",
        {"syntactically_valid": True, "warnings": True},
    ),
    (
        r"VaR = -\Phi^{-1}(\alpha) * \sigma_p * \sqrt{T}",
        "Value-at-Risk",
        {"syntactically_valid": True, "warnings": True},
    ),
    (
        r"\sqrt{\ln(x) + e^{y}}",
        "Nested functions",
        {"syntactically_valid": True, "warnings": True},
    ),
    (
        r"(a + b) * (c - d) / e",
        "Mixed operations",
        {"syntactically_valid": True, "warnings": True},
    ),
]


@pytest.mark.parametrize("formula,desc,expected", test_cases)
def test_enhanced_symbolic_validator(formula, desc, expected):
    result = validator.validate(formula)

    # Assert syntactic validity
    assert result["syntactically_valid"] == expected.get("syntactically_valid", True), (
        f"Failed {desc}"
    )

    # Assert errors exist if expected
    if expected.get("errors"):
        assert len(result["errors"]) > 0, f"Expected errors in {desc}"
    elif expected.get("errors") is False:
        assert len(result["errors"]) == 0, f"Did not expect errors in {desc}"

    # Assert warnings exist if expected
    if expected.get("warnings"):
        assert len(result["warnings"]) > 0, f"Expected warnings in {desc}"
    elif expected.get("warnings") is False:
        assert len(result["warnings"]) == 0, f"Did not expect warnings in {desc}"
