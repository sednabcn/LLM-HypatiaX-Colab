#!/usr/bin/env python3
"""
Pytest test suite for DimensionalValidator (Enhanced Edition)
Comprehensive tests for dimensional consistency, numerical stability, and bounds checking
"""

import math

import pytest

from hypatiax.tools.validation.dimensional_validator import DimensionalValidator


@pytest.fixture
def validator():
    """Fixture to provide a fresh validator instance for each test"""
    return DimensionalValidator()


@pytest.fixture
def validator_with_history():
    """Fixture with limited history for testing history features"""
    return DimensionalValidator(max_history=10)


@pytest.fixture
def validator_unlimited_history():
    """Fixture with unlimited history"""
    return DimensionalValidator(max_history=None)


class TestOverflowRiskDetection:
    """Test suite for overflow risk detection"""

    def test_large_base_with_exponent(self, validator):
        """Test overflow risk from large base with exponent"""
        result = validator.validate(expression_str="1000**5", variable_units={})
        # Should warn about potential overflow
        assert len(result["warnings"]) > 0 or len(result["overflow_risks"]) > 0


class TestScoringSystem:
    """Test suite for validation scoring mechanism"""

    def test_perfect_score(self, validator):
        """Test that perfect validation gives score of 100"""
        result = validator.validate(
            expression_str="x + y",
            variable_units={"x": "USD", "y": "USD"},
            variable_bounds={"x": (0, 100), "y": (0, 100)},
        )
        assert result["score"] == 100.0


if __name__ == "__main__":
    # Run tests with pytest
    pytest.main([__file__, "-v", "--tb=short"])
