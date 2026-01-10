#!/usr/bin/env python3
"""
Test suite for Enhanced Domain Validator
tests/test_enhanced_domain_validator.py

Comprehensive tests covering:
- DeFi edge cases (IL, AMM, fees)
- Constraint validation (bounds, positivity)
- Formula-specific validation
- Error detection and scoring
- Remediation guidance
"""

# Import the validator
import sys
from typing import Any, Dict

import numpy as np
import pytest
import sympy as sp

sys.path.append("tools/validation")
from hypatiax.tools.validation.enhanced_domain_validator import (
    ConstraintType,
    EnhancedDomainValidator,
)


class TestBasicValidation:
    """Test basic validation functionality."""

    def test_validator_initialization(self):
        """Test validator initializes correctly."""
        validator = EnhancedDomainValidator(domain="defi")
        assert validator.domain == "defi"
        assert len(validator.constraints) > 0
        assert len(validator.validation_history) == 0

    def test_validator_invalid_domain(self):
        """Test validator handles unknown domain gracefully."""
        validator = EnhancedDomainValidator(domain="unknown")
        assert validator.domain == "unknown"
        assert len(validator.constraints) == 0

    def test_simple_expression_parsing(self):
        """Test basic expression parsing."""
        validator = EnhancedDomainValidator(domain="defi")
        result = validator.validate(
            expression_str="x + y",
            variable_definitions={"x": "Variable x", "y": "Variable y"},
        )
        assert result["valid"] == True
        assert "Parsed expression" in str(result["info"])

    def test_invalid_expression_syntax(self):
        """Test handling of invalid expression syntax."""
        validator = EnhancedDomainValidator(domain="defi")
        result = validator.validate(
            expression_str="x + + y",
            variable_definitions={
                "x": "Variable x",
                "y": "Variable y",
            },  # Invalid syntax
        )
        assert result["valid"] == False
        assert len(result["errors"]) > 0
        assert result["score"] == 0


class TestDeFiEdgeCases:
    """Test DeFi-specific edge cases."""

    def test_impermanent_loss_valid_data(self):
        """Test IL formula with valid positive ratio."""
        validator = EnhancedDomainValidator(domain="defi")

        il_formula = "2 * sqrt(r) / (1 + r) - 1"
        il_vars = {"r": "Price ratio"}
        il_constraints = {
            "r": {"type": "strictly_positive", "min": 0, "reason": "Denominator (1+r)"}
        }
        test_data = {"r": np.array([0.5, 1.0, 1.5, 2.0, 3.0])}

        result = validator.validate(
            il_formula,
            il_vars,
            il_constraints,
            test_data,
            formula_type="impermanent_loss",
        )

        assert result["valid"] == True
        assert result["score"] >= 70  # Should have high score
        assert "il_ratio" in str(result.get("edge_cases_detected", []))

    def test_impermanent_loss_negative_ratio(self):
        """Test IL formula with negative ratio (critical error)."""
        validator = EnhancedDomainValidator(domain="defi")

        il_formula = "2 * sqrt(r) / (1 + r) - 1"
        il_vars = {"r": "Price ratio"}
        il_constraints = {"r": {"type": "strictly_positive", "min": 0}}
        test_data = {"r": np.array([-0.5, 0.5, 1.0])}  # Negative r!

        result = validator.validate(
            il_formula,
            il_vars,
            il_constraints,
            test_data,
            formula_type="impermanent_loss",
        )

        assert result["valid"] == False
        assert len(result["errors"]) > 0
        assert result["score"] < 50  # Should be heavily penalized
        assert any("r" in err.lower() for err in result["errors"])

    def test_impermanent_loss_ratio_near_minus_one(self):
        """Test IL formula with r close to -1 (division by zero risk)."""
        validator = EnhancedDomainValidator(domain="defi")

        il_formula = "2 * sqrt(r) / (1 + r) - 1"
        il_vars = {"r": "Price ratio"}
        test_data = {"r": np.array([-0.999, 0.5, 1.0])}

        result = validator.validate(il_formula, il_vars, None, test_data)

        assert result["valid"] == False
        assert len(result["errors"]) > 0

    def test_fee_at_100_percent(self):
        """Test swap formula with 100% fee (edge case)."""
        validator = EnhancedDomainValidator(domain="defi")

        swap_formula = "y * dx * (1 - fee) / (x + dx * (1 - fee))"
        swap_vars = {
            "y": "Output reserve",
            "x": "Input reserve",
            "dx": "Input amount",
            "fee": "Swap fee",
        }
        swap_constraints = {"fee": {"type": "percentage_strict", "max": 1.0}}
        test_data = {
            "x": np.array([1000.0]),
            "y": np.array([2000.0]),
            "dx": np.array([10.0]),
            "fee": np.array([1.0]),  # 100% fee - breaks (1-fee)
        }

        result = validator.validate(
            swap_formula, swap_vars, swap_constraints, test_data
        )

        assert result["valid"] == False
        assert len(result["errors"]) > 0
        assert any("fee" in err.lower() for err in result["errors"])
        assert "fee_at_100_percent" in result.get("edge_cases_detected", [])

    def test_zero_reserves(self):
        """Test AMM formula with zero reserves (critical error)."""
        validator = EnhancedDomainValidator(domain="defi")

        amm_formula = "x * y"
        amm_vars = {"x": "Reserve X", "y": "Reserve Y"}
        test_data = {
            "x": np.array([0.0, 100.0, 200.0]),
            "y": np.array([200.0, 150.0, 100.0]),
        }  # Zero reserve!

        result = validator.validate(amm_formula, amm_vars, None, test_data)

        assert result["valid"] == False
        assert len(result["errors"]) > 0
        assert any(
            "reserve" in err.lower() or "x" in err.lower() for err in result["errors"]
        )


class TestConstraintValidation:
    """Test variable constraint validation."""

    def test_strictly_positive_constraint_valid(self):
        """Test strictly positive constraint with valid data."""
        validator = EnhancedDomainValidator(domain="defi")

        expr = "x + y"
        vars_def = {"x": "Reserve X", "y": "Reserve Y"}
        test_data = {"x": np.array([1.0, 2.0, 3.0]), "y": np.array([4.0, 5.0, 6.0])}

        result = validator.validate(expr, vars_def, None, test_data)

        assert result["valid"] == True
        assert "x_strictly_positive" in result["constraints_checked"]
        assert "y_strictly_positive" in result["constraints_checked"]

    def test_strictly_positive_constraint_violated(self):
        """Test strictly positive constraint with zero/negative values."""
        validator = EnhancedDomainValidator(domain="defi")

        expr = "x + y"
        vars_def = {"x": "Reserve X", "y": "Reserve Y"}
        test_data = {
            "x": np.array([0.0, 2.0, 3.0]),
            "y": np.array([-1.0, 5.0, 6.0]),
        }  # Zero!  # Negative!

        result = validator.validate(expr, vars_def, None, test_data)

        assert result["valid"] == False
        assert len(result["errors"]) >= 2  # Both x and y violations
        assert len(result["constraint_violations"]) >= 2

    def test_bounded_constraint_strict(self):
        """Test strict bounded constraint (0 < fee < 1)."""
        validator = EnhancedDomainValidator(domain="defi")

        expr = "amount * (1 - fee)"
        vars_def = {"amount": "Amount", "fee": "Fee"}
        test_data = {
            "amount": np.array([100.0]),
            "fee": np.array([0.003]),
        }  # Valid: 0.3%

        result = validator.validate(expr, vars_def, None, test_data)

        assert result["valid"] == True
        assert "fee_bounded" in result["constraints_checked"]

    def test_bounded_constraint_violated_upper(self):
        """Test strict bounded constraint with upper bound violation."""
        validator = EnhancedDomainValidator(domain="defi")

        expr = "amount * (1 - fee)"
        vars_def = {"amount": "Amount", "fee": "Fee"}
        test_data = {
            "amount": np.array([100.0]),
            "fee": np.array([1.5]),
        }  # Invalid: > 1.0

        result = validator.validate(expr, vars_def, None, test_data)

        assert result["valid"] == False
        assert any("fee" in err.lower() for err in result["errors"])

    def test_bounded_constraint_violated_lower(self):
        """Test strict bounded constraint with lower bound violation."""
        validator = EnhancedDomainValidator(domain="defi")

        expr = "amount * (1 - fee)"
        vars_def = {"amount": "Amount", "fee": "Fee"}
        test_data = {
            "amount": np.array([100.0]),
            "fee": np.array([-0.1]),
        }  # Invalid: < 0

        result = validator.validate(expr, vars_def, None, test_data)

        assert result["valid"] == False
        assert len(result["errors"]) > 0

    def test_explicit_constraint_validation(self):
        """Test explicit variable constraints."""
        validator = EnhancedDomainValidator(domain="defi")

        expr = "sqrt(r)"
        vars_def = {"r": "Ratio"}
        constraints = {
            "r": {
                "type": "strictly_positive",
                "min": 0.1,
                "reason": "Must be positive for sqrt",
            }
        }
        test_data = {"r": np.array([0.5, 1.0, 2.0])}

        result = validator.validate(expr, vars_def, constraints, test_data)

        assert result["valid"] == True
        assert "r_explicit" in result["constraints_checked"]

    def test_explicit_constraint_violation(self):
        """Test explicit constraint violation."""
        validator = EnhancedDomainValidator(domain="defi")

        expr = "sqrt(r)"
        vars_def = {"r": "Ratio"}
        constraints = {
            "r": {
                "type": "strictly_positive",
                "min": 0.1,
                "reason": "Must be positive for sqrt",
            }
        }
        test_data = {"r": np.array([-0.5, 1.0, 2.0])}  # Negative!

        result = validator.validate(expr, vars_def, constraints, test_data)

        assert result["valid"] == False
        assert any("r" in err.lower() for err in result["errors"])


class TestFormulaDetection:
    """Test formula type detection."""

    def test_detect_impermanent_loss(self):
        """Test detection of IL formula."""
        validator = EnhancedDomainValidator(domain="defi")

        il_formula = "2 * sqrt(r) / (1 + r) - 1"
        detected = validator._detect_formula_type(il_formula)

        assert detected == "impermanent_loss"

    def test_detect_constant_product(self):
        """Test detection of constant product formula."""
        validator = EnhancedDomainValidator(domain="defi")

        cp_formula = "x * y"
        detected = validator._detect_formula_type(cp_formula)

        assert detected == "constant_product"

    def test_detect_swap_output(self):
        """Test detection of swap output formula."""
        validator = EnhancedDomainValidator(domain="defi")

        swap_formula = "dy = dx * (1 - fee)"
        detected = validator._detect_formula_type(swap_formula)

        assert detected == "swap_output"


class TestEpsilonProtection:
    """Test epsilon protection detection."""

    def test_division_without_epsilon(self):
        """Test detection of unprotected division."""
        validator = EnhancedDomainValidator(domain="defi")

        expr = "x / y"
        vars_def = {"x": "Numerator", "y": "Denominator"}

        result = validator.validate(expr, vars_def)

        # Should warn about missing epsilon protection
        assert any("epsilon" in warn.lower() for warn in result["warnings"])

    def test_division_with_epsilon(self):
        """Test detection of epsilon-protected division."""
        validator = EnhancedDomainValidator(domain="defi")

        expr = "x / (y + 1e-10)"
        vars_def = {"x": "Numerator", "y": "Denominator"}

        result = validator.validate(expr, vars_def)

        # Should recognize epsilon protection
        assert any("epsilon" in info.lower() for info in result["info"])


class TestFinanceDomain:
    """Test finance domain validation."""

    def test_sharpe_ratio_valid(self):
        """Test Sharpe ratio with valid volatility."""
        validator = EnhancedDomainValidator(domain="finance")

        sharpe = "(r - rf) / sigma"
        vars_def = {"r": "Return", "rf": "Risk-free rate", "sigma": "Volatility"}
        test_data = {
            "r": np.array([0.10]),
            "rf": np.array([0.02]),
            "sigma": np.array([0.15]),  # Valid positive volatility
        }

        result = validator.validate(sharpe, vars_def, None, test_data)

        assert result["valid"] == True

    def test_sharpe_ratio_zero_volatility(self):
        """Test Sharpe ratio with zero volatility (division by zero)."""
        validator = EnhancedDomainValidator(domain="finance")

        sharpe = "(r - rf) / sigma"
        vars_def = {"r": "Return", "rf": "Risk-free rate", "sigma": "Volatility"}
        test_data = {
            "r": np.array([0.10]),
            "rf": np.array([0.02]),
            "sigma": np.array([0.0]),
        }  # Zero volatility!

        result = validator.validate(sharpe, vars_def, None, test_data)

        assert result["valid"] == False
        assert any("sigma" in err.lower() for err in result["errors"])


class TestValidationHistory:
    """Test validation history and reporting."""

    def test_history_accumulation(self):
        """Test that validation history accumulates."""
        validator = EnhancedDomainValidator(domain="defi", max_history=10)

        for i in range(5):
            validator.validate(
                expression_str=f"x{i} + y{i}",
                variable_definitions={f"x{i}": "X", f"y{i}": "Y"},
            )

        assert len(validator.validation_history) == 5

    def test_history_max_limit(self):
        """Test that history respects max limit."""
        validator = EnhancedDomainValidator(domain="defi", max_history=3)

        for i in range(5):
            validator.validate(
                expression_str=f"x{i} + y{i}",
                variable_definitions={f"x{i}": "X", f"y{i}": "Y"},
            )

        assert len(validator.validation_history) == 3  # Limited to 3

    def test_validation_summary(self):
        """Test validation summary generation."""
        validator = EnhancedDomainValidator(domain="defi")

        # Valid validation
        validator.validate("x + y", {"x": "X", "y": "Y"})

        # Invalid validation
        validator.validate("x + + y", {"x": "X", "y": "Y"})

        summary = validator.get_validation_summary()

        assert summary["total_validations"] == 2
        assert summary["valid_count"] == 1
        assert summary["invalid_count"] == 1
        assert summary["validity_rate"] == 0.5
        assert "average_score" in summary

    def test_clear_history(self):
        """Test clearing validation history."""
        validator = EnhancedDomainValidator(domain="defi")

        validator.validate("x + y", {"x": "X", "y": "Y"})
        validator.validate("a + b", {"a": "A", "b": "B"})

        assert len(validator.validation_history) == 2

        validator.clear_history()

        assert len(validator.validation_history) == 0


class TestRiskDomain:
    """Test risk domain validation."""

    def test_var_positive_values(self):
        """Test VaR with positive values (loss magnitude)."""
        validator = EnhancedDomainValidator(domain="risk")

        expr = "VaR"
        vars_def = {"VaR": "Value at Risk"}
        test_data = {"VaR": np.array([100.0, 150.0, 200.0])}

        result = validator.validate(expr, vars_def, None, test_data)

        assert result["valid"] == True

    def test_confidence_level_bounds(self):
        """Test confidence level must be in (0, 1)."""
        validator = EnhancedDomainValidator(domain="risk")

        expr = "alpha * VaR"
        vars_def = {"alpha": "Confidence level", "VaR": "Value at Risk"}
        test_data = {"alpha": np.array([0.95]), "VaR": np.array([100.0])}  # Valid

        result = validator.validate(expr, vars_def, None, test_data)

        assert result["valid"] == True


class TestEdgeCaseDetection:
    """Test comprehensive edge case detection."""

    def test_very_small_positive_values(self):
        """Test detection of very small positive values."""
        validator = EnhancedDomainValidator(domain="defi")

        expr = "x * y"
        vars_def = {"x": "Reserve X", "y": "Reserve Y"}
        test_data = {
            "x": np.array([1e-10, 1.0]),
            "y": np.array([1.0, 1.0]),
        }  # Very small value

        result = validator.validate(expr, vars_def, None, test_data)

        # Should warn about numerical instability
        assert len(result["warnings"]) > 0

    def test_multiple_constraint_violations(self):
        """Test handling of multiple simultaneous violations."""
        validator = EnhancedDomainValidator(domain="defi")

        il_formula = "2 * sqrt(r) / (1 + r) - 1"
        test_data = {"r": np.array([-1.0, 0.0, -0.5])}  # Multiple bad values

        result = validator.validate(il_formula, {"r": "Price ratio"}, None, test_data)

        assert result["valid"] == False
        assert len(result["errors"]) > 0
        assert len(result["constraint_violations"]) > 0


class TestRemediationGuidance:
    """Test remediation guidance generation."""

    def test_remediation_steps_provided(self):
        """Test that remediation steps are provided for errors."""
        validator = EnhancedDomainValidator(domain="defi")

        il_formula = "2 * sqrt(r) / (1 + r) - 1"
        test_data = {"r": np.array([-0.5])}  # Invalid

        result = validator.validate(
            il_formula,
            {"r": "Price ratio"},
            {"r": {"type": "strictly_positive"}},
            test_data,
        )

        assert len(result["remediation_steps"]) > 0
        assert any("constraint" in step.lower() for step in result["remediation_steps"])

    def test_suggested_constraints(self):
        """Test that constraints are suggested when missing."""
        validator = EnhancedDomainValidator(domain="defi")

        expr = "x / y"
        vars_def = {"x": "Numerator", "y": "Denominator"}

        result = validator.validate(expr, vars_def)

        assert len(result["suggested_constraints"]) > 0


# Pytest fixtures
@pytest.fixture
def defi_validator():
    """Fixture for DeFi validator."""
    return EnhancedDomainValidator(domain="defi")


@pytest.fixture
def finance_validator():
    """Fixture for finance validator."""
    return EnhancedDomainValidator(domain="finance")


@pytest.fixture
def valid_il_data():
    """Fixture for valid IL test data."""
    return {"r": np.array([0.5, 1.0, 1.5, 2.0, 3.0])}


@pytest.fixture
def invalid_il_data():
    """Fixture for invalid IL test data."""
    return {"r": np.array([-0.5, 0.5, 1.0])}


# Integration tests
class TestIntegration:
    """Integration tests combining multiple features."""

    def test_full_defi_validation_pipeline(self, defi_validator, valid_il_data):
        """Test complete DeFi validation pipeline."""
        il_formula = "2 * sqrt(r) / (1 + r) - 1"
        il_vars = {"r": "Price ratio"}
        il_constraints = {
            "r": {"type": "strictly_positive", "min": 0, "reason": "IL denominator"}
        }

        result = defi_validator.validate(
            il_formula,
            il_vars,
            il_constraints,
            valid_il_data,
            formula_type="impermanent_loss",
        )

        # Should pass all checks
        assert result["valid"] == True
        assert result["score"] >= 70
        assert len(result["errors"]) == 0
        assert "impermanent_loss" in str(result["formula_type"])

    def test_multi_violation_scoring(self, defi_validator):
        """Test that multiple violations compound penalties."""
        bad_formula = "sqrt(r) / (1 + r)"
        bad_data = {"r": np.array([-1.0, 0.0, -0.5])}  # Multiple violations

        result = defi_validator.validate(bad_formula, {"r": "Ratio"}, None, bad_data)

        assert result["valid"] == False
        assert result["score"] < 50  # Heavily penalized
        assert len(result["errors"]) > 0


if __name__ == "__main__":
    pytest.main([__file__, "-v", "--tb=short"])


"""
Test Coverage:

Basic Validation - Initialization, parsing, invalid syntax
DeFi Edge Cases - IL ratio, 100% fees, zero reserves
Constraint Validation - Strictly positive, bounded, explicit constraints
Formula Detection - Auto-detection of IL, AMM, swap formulas
Epsilon Protection - Division safety checks
Finance Domain - Sharpe ratio, volatility checks
Validation History - History tracking, summaries, limits
Risk Domain - VaR, confidence levels
Edge Case Detection - Small values, multiple violations
Remediation Guidance - Suggested fixes, constraints
Integration Tests - Full pipeline testing

Run with:
bashpy

test test_enhanced_domain_validator.py -v
"""
