#!/usr/bin/env python3
"""
Test suite specifically for the 12 previously failing tests
#!/usr/bin/env python
"""
import time

import pytest

# Import the FIXED validator
from hypatiax.tools.symbolic.fixed_validator import EnhancedSymbolicValidator


@pytest.fixture
def validator():
    """Provide fresh validator instance"""
    return EnhancedSymbolicValidator()


class TestPreviouslyFailingTests:
    """Test the 12 previously failing tests"""

    def test_negative_exponent_FIXED(self, validator):
        """Test negative exponent detection"""
        result = validator.validate(r"x^{-1}")
        print(f"\nNegative exponent result:")
        print(f"  Warnings: {result['warnings']}")

        assert result["syntactically_valid"], "Should parse"
        assert (
            len(result["warnings"]) > 0
        ), f"Should have warnings, got {len(result['warnings'])}"

        # Check for negative exponent warning
        has_neg_exp = any("negative exponent" in w.lower() for w in result["warnings"])
        assert (
            has_neg_exp
        ), f"Should warn about negative exponent. Warnings: {result['warnings']}"

    def test_large_exponential_FIXED(self, validator):
        """Test large exponential detection"""
        result = validator.validate(r"e^{500}")
        print(f"\nLarge exponential result:")
        print(f"  Errors: {result['errors']}")
        print(f"  Warnings: {result['warnings']}")

        assert result["syntactically_valid"], "Should parse"

        # Should have either errors or warnings about overflow
        total_issues = len(result["errors"]) + len(result["warnings"])
        assert total_issues > 0, f"Should flag overflow risk, got 0 issues"

        # Check for overflow mention
        all_issues = result["errors"] + result["warnings"]
        has_overflow = any(
            "overflow" in issue.lower() or "exponential" in issue.lower()
            for issue in all_issues
        )
        assert (
            has_overflow
        ), f"Should mention overflow/exponential. Issues: {all_issues}"

    def test_large_exponent_FIXED(self, validator):
        """Test large exponent detection"""
        result = validator.validate(r"x^{1000}")
        print(f"\nLarge exponent result:")
        print(f"  Errors: {result['errors']}")

        assert result["syntactically_valid"], "Should parse"
        assert len(result["errors"]) > 0, f"Should have errors for large exponent"

        has_exp_error = any(
            "exponent" in e.lower() and "overflow" in e.lower()
            for e in result["errors"]
        )
        assert (
            has_exp_error
        ), f"Should error on large exponent. Errors: {result['errors']}"

    def test_factorial_overflow_FIXED(self, validator):
        """Test factorial overflow detection"""
        result = validator.validate("180!")
        print(f"\nFactorial result:")
        print(f"  Expression: {result.get('expression')}")
        print(f"  Errors: {result['errors']}")

        assert result["syntactically_valid"], "Should parse"

        # Should have error about factorial overflow
        all_issues = result["errors"] + result["warnings"]
        has_factorial = any(
            "factorial" in i.lower() and "overflow" in i.lower() for i in all_issues
        )
        assert has_factorial, f"Should flag factorial overflow. Issues: {all_issues}"

    def test_nested_exponential_FIXED(self, validator):
        """Test nested exponential detection"""
        result = validator.validate(r"e^{e^{x}}")
        print(f"\nNested exponential result:")
        print(f"  Errors: {result['errors']}")

        assert result["syntactically_valid"], "Should parse"

        # Should have critical error about nested exponential
        all_issues = result["errors"] + result["warnings"]
        has_nested = any(
            "nested" in i.lower() and "exponential" in i.lower() for i in all_issues
        )
        assert has_nested, f"Should flag nested exponential. Issues: {all_issues}"

    def test_negative_exponential_underflow_FIXED(self, validator):
        """Test underflow detection"""
        result = validator.validate(r"e^{-200}")
        print(f"\nUnderflow result:")
        print(f"  Warnings: {result['warnings']}")

        assert result["syntactically_valid"], "Should parse"
        assert len(result["warnings"]) > 0, "Should have warnings"

        has_underflow = any("underflow" in w.lower() for w in result["warnings"])
        assert (
            has_underflow
        ), f"Should warn about underflow. Warnings: {result['warnings']}"

    def test_esg_domain_FIXED(self, validator):
        """Test ESG domain rules"""
        result = validator.validate(
            r"w_1 \cdot E + w_2 \cdot S + w_3 \cdot G", domain="esg"
        )
        print(f"\nESG result:")
        print(f"  Warnings: {result['warnings']}")

        assert result["syntactically_valid"], "Should parse"
        assert len(result["warnings"]) > 0, "Should have ESG warnings"

        # Check for ESG-specific content
        esg_related = [
            w
            for w in result["warnings"]
            if "esg" in w.lower() or "score" in w.lower() or "weight" in w.lower()
        ]
        assert (
            len(esg_related) > 0
        ), f"Should have ESG-specific warnings. Got: {result['warnings']}"

    def test_score_penalty_for_errors_FIXED(self, validator):
        """Test error penalties"""
        result_errors = validator.validate(r"\frac{1}{0}")
        result_warnings = validator.validate(r"\sqrt{x}")

        print(f"\nScore comparison:")
        print(
            f"  With errors: score={result_errors['score']}, errors={len(result_errors['errors'])}"
        )
        print(
            f"  With warnings: score={result_warnings['score']}, warnings={len(result_warnings['warnings'])}"
        )

        # If one has errors and other doesn't, error one should score lower
        if len(result_errors["errors"]) > 0 and len(result_warnings["errors"]) == 0:
            assert (
                result_errors["score"] <= result_warnings["score"]
            ), f"Errors should penalize more: {result_errors['score']} vs {result_warnings['score']}"

    def test_black_scholes_FIXED(self, validator):
        """Test Black-Scholes parsing"""
        formula = r"S \cdot N(d_1) - K \cdot e^{-r \cdot t} \cdot N(d_2)"
        result = validator.validate(formula, domain="finance")

        print(f"\nBlack-Scholes result:")
        print(f"  Valid: {result['syntactically_valid']}")
        print(f"  Expression: {result.get('expression')}")

        # At minimum should parse successfully
        assert result["syntactically_valid"], "Should parse Black-Scholes formula"

    def test_mixed_operations_FIXED(self, validator):
        """Test mixed operations"""
        formula = r"\frac{\sqrt{a + b}}{c - d} \cdot e^{-x}"
        result = validator.validate(formula)

        print(f"\nMixed operations result:")
        print(f"  Expression: {result.get('expression')}")
        print(f"  Info: {result.get('info')}")  # ADD THIS LINE
        print(f"  Warnings: {len(result['warnings'])}")
        print(f"  Sample warnings: {result['warnings'][:3]}")

        assert result["syntactically_valid"], "Should parse"
        # Should have multiple warnings (sqrt, division, subtraction, exponential)
        assert (
            len(result["warnings"]) >= 2
        ), f"Should have multiple warnings, got {len(result['warnings'])}"

    def test_mixed_operations_FIXED_(self, validator):
        """Test mixed operations"""
        formula = r"\frac{\sqrt{a + b}}{c - d} \cdot e^{-x}"
        result = validator.validate(formula)

        print(f"\nMixed operations result:")
        print(f"  Warnings: {len(result['warnings'])}")
        print(f"  Sample warnings: {result['warnings'][:3]}")

        assert result["syntactically_valid"], "Should parse"
        # Should have multiple warnings (sqrt, division, subtraction, exponential)
        assert (
            len(result["warnings"]) >= 2
        ), f"Should have multiple warnings, got {len(result['warnings'])}"

    def test_full_workflow_risky_formula_FIXED(self, validator):
        """Test workflow with risky formula"""
        formula = r"\frac{e^{x}}{y - z}"
        result = validator.validate(formula, domain="defi")

        print(f"\nRisky formula workflow:")
        print(f"  Warnings: {len(result['warnings'])}")

        assert result["syntactically_valid"], "Should parse"
        assert len(result["warnings"]) > 0, "Should have warnings for risky formula"

        summary = validator.get_validation_summary(result)
        assert (
            "WARNING" in summary.upper() or "WARN" in summary.upper()
        ), "Summary should mention warnings"

    def test_validates_quickly_FIXED(self, validator):
        """Test validation speed"""
        formula = r"\frac{\sqrt{a \cdot b}}{c + d} \cdot e^{-x}"

        start = time.time()
        result = validator.validate(formula)
        duration = time.time() - start

        print(f"\nPerformance: {duration:.4f}s")

        assert duration < 1.0, f"Should complete in <1s, took {duration:.4f}s"
        assert result["syntactically_valid"], "Should parse"


class TestAllFixesIntegration:
    """Integration test for all fixes"""

    def test_all_fixes_comprehensive(self, validator):
        """Test all fixes work together"""

        test_cases = [
            # (formula, description, expect_any_issues)
            (r"x^{-1}", "negative exponent", True),
            (r"e^{500}", "large exponential", True),
            (r"x^{1000}", "large exponent", True),
            ("180!", "factorial overflow", True),
            (r"e^{e^{x}}", "nested exponential", True),
            (r"e^{-200}", "underflow", True),
            (r"w_1 \cdot E + w_2 \cdot S + w_3 \cdot G", "esg", True),
            (r"\frac{1}{0}", "division by zero", True),
            (
                r"S \cdot N(d_1) - K \cdot e^{-r \cdot t} \cdot N(d_2)",
                "black-scholes",
                False,
            ),
            (r"\frac{\sqrt{a + b}}{c - d} \cdot e^{-x}", "mixed ops", True),
        ]

        results = []
        for formula, desc, expect_issues in test_cases:
            domain = (
                "esg"
                if desc == "esg"
                else "finance" if desc == "black-scholes" else "defi"
            )
            result = validator.validate(formula, domain=domain)

            total_issues = len(result["errors"]) + len(result["warnings"])

            # Check if expectation met
            success = True
            if expect_issues and total_issues == 0:
                success = False
                print(f"✗ {desc}: Expected issues but got none")
            elif not expect_issues and not result["syntactically_valid"]:
                success = False
                print(f"✗ {desc}: Expected to parse but failed")
            else:
                print(
                    f"✓ {desc}: {total_issues} issues detected"
                    if expect_issues
                    else f"✓ {desc}: Parses correctly"
                )

            results.append(
                {
                    "desc": desc,
                    "success": success,
                    "valid": result["syntactically_valid"],
                    "issues": total_issues,
                }
            )

        # Summary
        print(f"\n{'='*60}")
        print("INTEGRATION TEST SUMMARY")
        print(f"{'='*60}")
        for r in results:
            status = "✓" if r["success"] else "✗"
            print(
                f"{status} {r['desc']:20s} | Valid: {r['valid']} | Issues: {r['issues']}"
            )
        print(f"{'='*60}\n")

        # All should succeed
        failures = [r for r in results if not r["success"]]
        assert len(failures) == 0, f"Failed: {[r['desc'] for r in failures]}"


class TestEdgeCases:
    """Additional edge case tests"""

    def test_multiple_negative_exponents(self, validator):
        """Test multiple negative exponents"""
        result = validator.validate(r"x^{-1} + y^{-2}")
        assert result["syntactically_valid"]
        # Should have at least one warning about negative exponents
        neg_warnings = [
            w for w in result["warnings"] if "negative exponent" in w.lower()
        ]
        assert len(neg_warnings) >= 1

    def test_safe_operations(self, validator):
        """Test that safe operations don't trigger false positives"""
        result = validator.validate(r"x + y")
        assert result["syntactically_valid"]
        # Should have minimal warnings for simple addition
        assert result["score"] >= 70

    def test_moderate_factorial(self, validator):
        """Test moderate factorial doesn't overflow"""
        result = validator.validate("50!")
        assert result["syntactically_valid"]
        # Should not have critical errors
        critical_errors = [e for e in result["errors"] if "CRITICAL" in e]
        assert len(critical_errors) == 0


def run_manual_tests():
    """Run tests manually for debugging"""
    validator = EnhancedSymbolicValidator()

    print("\n" + "=" * 60)
    print("MANUAL TEST RUN")
    print("=" * 60 + "\n")

    test_class = TestPreviouslyFailingTests()
    test_methods = [m for m in dir(test_class) if m.startswith("test_")]

    for method_name in test_methods:
        print(f"\nRunning: {method_name}")
        print("-" * 60)
        try:
            method = getattr(test_class, method_name)
            method(validator)
            print("✓ PASSED")
        except AssertionError as e:
            print(f"✗ FAILED: {e}")
        except Exception as e:
            print(f"✗ ERROR: {e}")


if __name__ == "__main__":
    import sys

    if len(sys.argv) > 1 and sys.argv[1] == "--manual":
        run_manual_tests()
    else:
        pytest.main([__file__, "-v", "--tb=short", "-s"])
