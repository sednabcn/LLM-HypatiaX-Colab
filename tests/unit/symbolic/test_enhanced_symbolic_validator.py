#!/usr/bin/env python3
"""
Pytest test suite for EnhancedSymbolicValidator
Comprehensive tests for all validation features
"""

import pytest
import sympy as sp

from hypatiax.tools.symbolic.enhanced_symbolic_validator import (
    EnhancedSymbolicValidator,
)

# from hypatiax.tools.symbolic.fixed_validator import EnhancedSymbolicValidator


@pytest.fixture
def validator():
    """Fixture to provide a fresh validator instance for each test"""
    return EnhancedSymbolicValidator()


class TestEmptyExpressionValidation:
    """Test suite for empty expression validation"""

    def test_empty_string(self, validator):
        """Test that empty string is rejected"""
        result = validator.validate("")
        assert not result["syntactically_valid"]
        assert len(result["errors"]) > 0
        assert any("empty" in err.lower() for err in result["errors"])
        assert result["score"] == 0

    def test_whitespace_only(self, validator):
        """Test that whitespace-only string is rejected"""
        result = validator.validate("   \t\n  ")
        assert not result["syntactically_valid"]
        assert len(result["errors"]) > 0
        assert result["score"] == 0

    def test_none_input(self, validator):
        """Test that None input is rejected"""
        result = validator.validate(None)
        assert not result["syntactically_valid"]
        assert any("None" in err for err in result["errors"])
        assert result["score"] == 0

    def test_single_char(self, validator):
        """Test that single character is rejected as too short"""
        result = validator.validate("x")
        assert not result["syntactically_valid"]
        assert any("too short" in err.lower() for err in result["errors"])

    def test_valid_minimal(self, validator):
        """Test that minimal valid expression passes"""
        result = validator.validate("x+1")
        assert result["syntactically_valid"]
        assert result["score"] > 0


class TestDivisionByZeroDetection:
    """Test suite for division by zero detection"""

    def test_simple_division_by_zero(self, validator):
        """Test detection of explicit division by zero"""
        result = validator.validate(r"\frac{1}{0}")
        assert result["syntactically_valid"]
        assert len(result["errors"]) > 0
        assert any("division by zero" in err.lower() for err in result["errors"])

    def test_subtraction_cancellation(self, validator):
        """Test detection of x-x in denominator"""
        result = validator.validate(r"\frac{1}{x - x}")
        assert result["syntactically_valid"]
        # Should have warning or error about division by zero risk
        total_issues = len(result["errors"]) + len(result["warnings"])
        assert total_issues > 0
        issues = result["errors"] + result["warnings"]
        assert any("zero" in issue.lower() for issue in issues)

    def test_negative_exponent(self, validator):
        """Test detection of negative exponents (implicit division)"""
        result = validator.validate(r"x^{-1}")
        assert result["syntactically_valid"]
        # Should warn about negative exponent = division
        assert len(result["warnings"]) > 0
        assert any("negative exponent" in warn.lower() for warn in result["warnings"])

    def test_complex_denominator(self, validator):
        """Test detection of risky complex denominator"""
        result = validator.validate(r"\frac{a}{b - c}")
        assert result["syntactically_valid"]
        # Should warn about potential zero in subtraction
        issues = result["errors"] + result["warnings"]
        assert len(issues) > 0

    def test_safe_division(self, validator):
        """Test that division by constant is considered safe"""
        result = validator.validate(r"\frac{x}{2}")
        assert result["syntactically_valid"]
        # May have warnings but should not have critical errors
        critical_errors = [
            e for e in result["errors"] if "CRITICAL" in e and "zero" in e.lower()
        ]
        assert len(critical_errors) == 0

    def test_multiple_divisions(self, validator):
        """Test detection with multiple division operations"""
        result = validator.validate(r"\frac{x}{y} + \frac{a}{b}")
        assert result["syntactically_valid"]
        # Should warn about each division
        issues = result["errors"] + result["warnings"]
        assert len(issues) >= 2


class TestOverflowRiskChecks:
    """Test suite for overflow detection"""

    def test_large_constant(self, validator):
        """Test detection of extremely large constants"""
        result = validator.validate("1e150")
        assert result["syntactically_valid"]
        # Should error on large constant
        assert len(result["errors"]) > 0
        assert any(
            "large constant" in err.lower() or "overflow" in err.lower()
            for err in result["errors"]
        )

    def test_exponential_function(self, validator):
        """Test warning for exponential functions"""
        result = validator.validate(r"e^{x}")
        assert result["syntactically_valid"]
        # Should warn about exponential
        assert len(result["warnings"]) > 0
        assert any("exponential" in warn.lower() for warn in result["warnings"])

    def test_large_exponential(self, validator):
        """Test error for exponential with large argument"""
        result = validator.validate(r"e^{500}")
        assert result["syntactically_valid"]
        # Should have critical error
        assert len(result["errors"]) > 0
        assert any("overflow" in err.lower() for err in result["errors"])

    def test_large_exponent(self, validator):
        """Test detection of large power exponents"""
        result = validator.validate(r"x^{1000}")
        assert result["syntactically_valid"]
        # Should error on large exponent
        assert len(result["errors"]) > 0
        assert any(
            "exponent" in err.lower() and "overflow" in err.lower()
            for err in result["errors"]
        )

    def test_factorial_overflow(self, validator):
        """Test detection of factorial that overflows float64"""
        result = validator.validate("180!")
        assert result["syntactically_valid"]
        # Should error on large factorial
        assert len(result["errors"]) > 0
        assert any(
            "factorial" in err.lower() and "overflow" in err.lower()
            for err in result["errors"]
        )

    def test_safe_factorial(self, validator):
        """Test that small factorials don't trigger overflow warnings"""
        result = validator.validate("5!")
        assert result["syntactically_valid"]
        # Should not have overflow errors for small factorial
        overflow_errors = [e for e in result["errors"] if "overflow" in e.lower()]
        assert len(overflow_errors) == 0

    def test_nested_exponential(self, validator):
        """Test detection of nested exponentials (very dangerous)"""
        result = validator.validate(r"e^{e^{x}}")
        assert result["syntactically_valid"]
        # Should have critical error
        assert len(result["errors"]) > 0
        assert any("nested exponential" in err.lower() for err in result["errors"])

    def test_hyperbolic_functions(self, validator):
        """Test warning for hyperbolic functions"""
        result = validator.validate(r"\sinh(x)")
        assert result["syntactically_valid"]
        # Should warn about hyperbolic growth
        assert len(result["warnings"]) > 0
        assert any("hyperbolic" in warn.lower() for warn in result["warnings"])

    def test_product_of_large_numbers(self, validator):
        """Test detection of products that might overflow"""
        result = validator.validate("1e50 * 1e60")
        assert result["syntactically_valid"]
        # Should warn about product of large numbers
        issues = result["errors"] + result["warnings"]
        assert len(issues) > 0


class TestUnderflowRiskChecks:
    """Test suite for underflow detection"""

    def test_very_small_constant(self, validator):
        """Test detection of very small constants"""
        result = validator.validate("1e-150")
        assert result["syntactically_valid"]
        # Should warn about underflow
        assert len(result["warnings"]) > 0
        assert any(
            "small" in warn.lower() or "underflow" in warn.lower()
            for warn in result["warnings"]
        )

    def test_negative_exponential(self, validator):
        """Test detection of exp with large negative argument"""
        result = validator.validate(r"e^{-200}")
        assert result["syntactically_valid"]
        # Should warn about underflow
        assert len(result["warnings"]) > 0
        assert any("underflow" in warn.lower() for warn in result["warnings"])


class TestNumericalStability:
    """Test suite for numerical stability checks"""

    def test_subtraction_precision_loss(self, validator):
        """Test warning for subtractive cancellation"""
        result = validator.validate("a - b")
        assert result["syntactically_valid"]
        # Should warn about precision loss
        assert len(result["warnings"]) > 0
        assert any(
            "subtraction" in warn.lower() or "precision" in warn.lower()
            for warn in result["warnings"]
        )

    def test_square_root_domain(self, validator):
        """Test validation of square root domain"""
        result = validator.validate(r"\sqrt{x}")
        assert result["syntactically_valid"]
        # Should warn about non-negative requirement
        assert len(result["warnings"]) > 0
        assert any(
            "square root" in warn.lower() or "non-negative" in warn.lower()
            for warn in result["warnings"]
        )

    def test_logarithm_domain(self, validator):
        """Test validation of logarithm domain"""
        result = validator.validate(r"\log(x)")
        assert result["syntactically_valid"]
        # Should warn about positive requirement
        assert len(result["warnings"]) > 0
        assert any(
            "logarithm" in warn.lower() or "positive" in warn.lower()
            for warn in result["warnings"]
        )

    def test_multiple_multiplications(self, validator):
        """Test warning for accumulated rounding errors"""
        result = validator.validate("a * b * c * d * e * f * g")
        assert result["syntactically_valid"]
        # Should warn about rounding error accumulation
        assert len(result["warnings"]) > 0
        assert any(
            "multiplication" in warn.lower() or "rounding" in warn.lower()
            for warn in result["warnings"]
        )


class TestDomainSpecificRules:
    """Test suite for domain-specific validation"""

    def test_defi_domain(self, validator):
        """Test DeFi-specific rules"""
        result = validator.validate(r"\sqrt{x \cdot y}", domain="defi")
        assert result["syntactically_valid"]
        # Should have DeFi-specific warnings
        assert len(result["warnings"]) > 0
        defi_warnings = [
            w for w in result["warnings"] if "defi" in w.lower() or "amm" in w.lower()
        ]
        assert len(defi_warnings) > 0

    def test_finance_domain(self, validator):
        """Test finance-specific rules"""
        result = validator.validate(r"\log(S_t / S_0)", domain="finance")
        assert result["syntactically_valid"]
        # Should have finance-specific warnings
        assert len(result["warnings"]) > 0
        finance_warnings = [
            w
            for w in result["warnings"]
            if "finance" in w.lower() or "return" in w.lower()
        ]
        assert len(finance_warnings) > 0

    def test_esg_domain(self, validator):
        """Test ESG-specific rules"""
        result = validator.validate(
            r"w_1 \cdot E + w_2 \cdot S + w_3 \cdot G", domain="esg"
        )
        assert result["syntactically_valid"]
        # Should have ESG-specific warnings
        assert len(result["warnings"]) > 0
        esg_warnings = [
            w for w in result["warnings"] if "esg" in w.lower() or "score" in w.lower()
        ]
        assert len(esg_warnings) > 0

    def test_risk_domain(self, validator):
        """Test risk management-specific rules"""
        latex_expr = r"\sigma \cdot \sqrt{t}"
        result = validator.validate(latex_expr, domain="risk")
        assert result["syntactically_valid"]
        assert len(result["warnings"]) > 0


class TestScoringSystem:
    """Test suite for validation scoring"""

    def test_perfect_score(self, validator):
        """Test that valid simple formula gets high score"""
        result = validator.validate("x + y")
        assert result["score"] >= 75  # May have minor warnings

    def test_zero_score_empty(self, validator):
        """Test that empty formula gets zero score"""
        result = validator.validate("")
        assert result["score"] == 0

    def test_low_score_multiple_errors(self, validator):
        """Test that multiple errors reduce score significantly"""
        result = validator.validate(r"\frac{e^{500}}{x - x}")
        assert result["score"] < 50  # Multiple critical issues

    def test_score_penalty_for_errors(self, validator):
        """Test that errors reduce score more than warnings"""
        result_with_errors = validator.validate(r"\frac{1}{0}")
        result_with_warnings = validator.validate(r"\sqrt{x}")

        # Errors should penalize more than warnings
        if (
            len(result_with_errors["errors"]) > 0
            and len(result_with_warnings["errors"]) == 0
        ):
            assert result_with_errors["score"] < result_with_warnings["score"]


class TestStrictMode:
    """Test suite for strict mode validation"""

    def test_strict_mode_treats_warnings_as_errors(self, validator):
        """Test that strict mode converts warnings to errors"""
        formula = r"\sqrt{x}"

        result_normal = validator.validate(formula, strict_mode=False)
        result_strict = validator.validate(formula, strict_mode=True)

        # Strict mode should have more errors
        assert len(result_strict["errors"]) >= len(result_normal["errors"])

        # Strict mode should have fewer or no warnings
        assert len(result_strict["warnings"]) <= len(result_normal["warnings"])

    def test_strict_mode_lowers_score(self, validator):
        """Test that strict mode gives lower scores"""
        formula = r"e^{x}"  # Has warnings but no errors

        result_normal = validator.validate(formula, strict_mode=False)
        result_strict = validator.validate(formula, strict_mode=True)

        # If there were warnings in normal mode, strict should have lower score
        if result_normal["warnings"]:
            assert result_strict["score"] <= result_normal["score"]


class TestValidationSummary:
    """Test suite for human-readable summary generation"""

    def test_summary_contains_score(self, validator):
        """Test that summary includes score"""
        result = validator.validate("x + y")
        summary = validator.get_validation_summary(result)
        assert "Score" in summary or "score" in summary
        assert str(result["score"]) in summary

    def test_summary_contains_expression(self, validator):
        """Test that summary includes parsed expression"""
        result = validator.validate("x + y")
        summary = validator.get_validation_summary(result)
        assert "Expression" in summary or "expression" in summary

    def test_summary_lists_errors(self, validator):
        """Test that summary lists all errors"""
        result = validator.validate(r"\frac{1}{0}")
        summary = validator.get_validation_summary(result)
        assert "ERROR" in summary.upper()
        # Each error should appear in summary
        for error in result["errors"]:
            # At least part of the error message should appear
            assert any(word in summary for word in error.split()[:3])

    def test_summary_lists_warnings(self, validator):
        """Test that summary lists all warnings"""
        result = validator.validate(r"\sqrt{x}")
        summary = validator.get_validation_summary(result)
        if result["warnings"]:
            assert "WARNING" in summary.upper()


class TestComplexFormulas:
    """Test suite for complex real-world formulas"""

    def test_amm_constant_product(self, validator):
        """Test Uniswap constant product formula"""
        result = validator.validate(r"\sqrt{x \cdot y}", domain="defi")
        assert result["syntactically_valid"]
        assert result["score"] > 50  # Should be mostly valid

    def test_black_scholes(self, validator):
        """Test Black-Scholes-like formula"""
        formula = r"S \cdot N(d_1) - K \cdot e^{-r \cdot t} \cdot N(d_2)"
        result = validator.validate(formula, domain="finance")
        assert result["syntactically_valid"]
        # Should have warnings about exponential but be valid
        assert result["domain_valid"]

    def test_sharpe_ratio(self, validator):
        """Test Sharpe ratio formula"""
        result = validator.validate(r"\frac{R_p - R_f}{\sigma_p}", domain="finance")
        assert result["syntactically_valid"]
        # Should warn about division by volatility
        assert len(result["warnings"]) > 0

    def test_value_at_risk(self, validator):
        """Test VaR formula"""
        result = validator.validate(r"\mu - z_{\alpha} \cdot \sigma", domain="risk")
        assert result["syntactically_valid"]
        # Should have some risk-specific warnings
        assert len(result["warnings"]) > 0


class TestEdgeCases:
    """Test suite for edge cases and boundary conditions"""

    def test_unicode_characters(self, validator):
        """Test handling of unicode math symbols"""
        result = validator.validate("α + β")
        assert result["syntactically_valid"]

    def test_very_long_formula(self, validator):
        """Test handling of very long formulas"""
        long_formula = " + ".join([f"x_{i}" for i in range(100)])
        result = validator.validate(long_formula)
        assert result["syntactically_valid"]

    def test_nested_functions(self, validator):
        """Test deeply nested functions"""
        result = validator.validate(r"\sqrt{\log(\exp(x))}")
        assert result["syntactically_valid"]

    def test_mixed_operations(self, validator):
        """Test formula with mixed operations"""
        formula = r"\frac{\sqrt{a + b}}{c - d} \cdot e^{-x}"
        result = validator.validate(formula)
        assert result["syntactically_valid"]
        # Should have multiple warnings
        assert len(result["warnings"]) > 2


class TestParsingFallbacks:
    """Test suite for parsing fallback mechanisms"""

    def test_latex_with_text_wrapper(self, validator):
        """Test parsing with \\text{} wrapper"""
        result = validator.validate(r"\frac{\text{numerator}}{x}")
        # Should attempt to parse even with text wrappers
        assert result["syntactically_valid"] or len(result["errors"]) > 0

    def test_latex_with_display_math(self, validator):
        """Test parsing with display math delimiters"""
        result = validator.validate(r"$$x + y$$")
        assert result["syntactically_valid"]

    def test_sympify_fallback(self, validator):
        """Test that sympify fallback works"""
        result = validator.validate("x**2 + 2*x + 1")  # Python notation
        assert result["syntactically_valid"]


# Parametrized tests for multiple similar cases
@pytest.mark.parametrize(
    "formula,expected_valid",
    [
        ("x + y", True),
        ("x * y", True),
        ("x / y", True),
        (r"\frac{x}{y}", True),
        ("", False),
        ("   ", False),
        (None, False),
    ],
)
def test_basic_validity(validator, formula, expected_valid):
    """Parametrized test for basic validity checks"""
    result = validator.validate(formula)
    if expected_valid:
        assert result["syntactically_valid"]
    else:
        assert not result["syntactically_valid"]


@pytest.mark.parametrize(
    "risky_formula",
    [
        r"\frac{1}{0}",
        r"\frac{x}{x-x}",
        r"e^{1000}",
        r"x^{500}",
        r"200!",
        r"e^{e^{x}}",
    ],
)
def test_risky_formulas_have_issues(validator, risky_formula):
    """Parametrized test ensuring risky formulas are flagged"""
    result = validator.validate(risky_formula)
    # Should have errors or warnings
    total_issues = len(result["errors"]) + len(result["warnings"])
    assert total_issues > 0


@pytest.mark.parametrize("domain", ["defi", "finance", "esg", "risk"])
def test_all_domains_work(validator, domain):
    """Test that all domains are supported"""
    result = validator.validate("x + y", domain=domain)
    assert result["syntactically_valid"]
    assert result["domain_valid"]


# Integration tests
class TestIntegration:
    """Integration tests for complete validation workflow"""

    def test_full_workflow_valid_formula(self, validator):
        """Test complete workflow with valid formula"""
        formula = r"\frac{a + b}{2}"
        result = validator.validate(formula, domain="finance")

        # Should pass all checks
        assert result["syntactically_valid"]
        assert result["score"] > 50

        # Should have expression
        assert result["expression"] is not None

        # Summary should be generated
        summary = validator.get_validation_summary(result)
        assert len(summary) > 0

    def test_full_workflow_invalid_formula(self, validator):
        """Test complete workflow with invalid formula"""
        result = validator.validate("")

        # Should fail
        assert not result["syntactically_valid"]
        assert result["score"] == 0
        assert len(result["errors"]) > 0

        # Summary should still be generated
        summary = validator.get_validation_summary(result)
        assert len(summary) > 0

    def test_full_workflow_risky_formula(self, validator):
        """Test complete workflow with risky but valid formula"""
        formula = r"\frac{e^{x}}{y - z}"
        result = validator.validate(formula, domain="defi")

        # Should parse but have warnings
        assert result["syntactically_valid"]
        assert len(result["warnings"]) > 0

        # Summary should list warnings
        summary = validator.get_validation_summary(result)
        assert "WARNING" in summary.upper()


# Performance tests
class TestPerformance:
    """Basic performance tests"""

    def test_validates_quickly(self, validator):
        """Test that validation completes in reasonable time"""
        import time

        formula = r"\frac{\sqrt{a \cdot b}}{c + d} \cdot e^{-x}"

        start = time.time()
        result = validator.validate(formula)
        duration = time.time() - start

        # Should complete in under 1 second
        assert duration < 1.0
        assert result["syntactically_valid"]


if __name__ == "__main__":
    # Run tests with pytest
    pytest.main([__file__, "-v", "--tb=short"])


"""
Test Organization
1. Empty Expression Validation Tests (5 tests)

Empty strings, whitespace, None values, single characters
Ensures proper rejection of invalid inputs

2. Division-by-Zero Detection Tests (6 tests)

Explicit division by zero
Subtraction cancellation (x-x)
Negative exponents
Complex denominators
Safe divisions vs risky ones

3. Overflow Risk Tests (9 tests)

Large constants (>1e100)
Exponential functions
Large exponents (x^1000)
Factorial overflow (>170!)
Nested exponentials
Hyperbolic functions
Products of large numbers

4. Underflow Risk Tests (2 tests)

Very small constants (<1e-100)
Negative exponentials

5. Numerical Stability Tests (4 tests)

Subtractive cancellation
Square root domain validation
Logarithm domain validation
Accumulated rounding errors

6. Domain-Specific Tests (4 tests)

DeFi, Finance, ESG, and Risk domain rules

7. Scoring System Tests (4 tests)

Perfect scores, zero scores, error penalties

8. Strict Mode Tests (2 tests)

Warning-to-error conversion
Score reduction in strict mode

9. Complex Real-World Formulas (4 tests)

AMM constant product
Black-Scholes
Sharpe ratio
Value-at-Risk

10. Edge Cases & Integration Tests

Unicode handling
Very long formulas
Parsing fallbacks
Complete workflows
"""

# Running the Tests
# bash

# Run all tests with verbose output

# pytest test_enhanced_symbolic_validator.py -v

# Run specific test class
# pytest test_enhanced_symbolic_validator.py::TestDivisionByZeroDetection -v

# Run with coverage
# pytest test_enhanced_symbolic_validator.py --cov=enhanced_symbolic_validator --cov-report=html

# Run only fast tests (exclude performance)
# pytest test_enhanced_symbolic_validator.py -v -m "not slow"

# The test suite ensures the validator properly catches all the critical issues you specified: empty expressions, division-by-zero risks, and overflow conditions!
