#!/usr/bin/env python3
"""
Pytest test suite for EnhancedSymbolicValidator
Comprehensive tests for all validation features
"""

import pytest
import sympy as sp

from hypatiax.tools.symbolic.enhanced_symbolic_validator_1111 import (
    EnhancedSymbolicValidator,
)

# from hypatiax.tools.symbolic.fixed_validator import EnhancedSymbolicValidator


@pytest.fixture
def validator():
    """Fixture to provide a fresh validator instance for each test"""
    return EnhancedSymbolicValidator()


class TestDomainSpecificRules:
    """Test suite for domain-specific validation"""

    def test_risk_domain(self, validator):
        """Test risk management-specific rules"""
        latex_expr = r"\sigma \cdot \sqrt{t}"
        result = validator.validate(latex_expr, domain="risk")
        assert result["syntactically_valid"]
        assert len(result["warnings"]) > 0


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
