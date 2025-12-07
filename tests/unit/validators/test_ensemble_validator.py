"""
HypatiaX Ensemble Validator Test Suite (UPDATED - Week 2, Day 3)

Tests for the recalibrated ensemble validator addressing:
- Threshold alignment (94.0 → 85.0)
- Domain validator weight adjustments
- Edge case penalty system
- Acceptance criteria documentation

Priority: CRITICAL (Week 2, Day 3)
Related Files: validation/ensemble_validator.py

Path: tests/unit/test_ensemble_validator.py
"""

from typing import Any, Dict

import numpy as np
import pytest

from hypatiax.tools.validation.ensemble_validator import EnsembleValidator


class TestThresholdCalibration:
    """Test that validation thresholds are properly calibrated"""

    def test_minimum_score_threshold(self):
        """Test that minimum passing score is 85.0 (not 94.0 or 70.0)"""
        validator = EnsembleValidator(domain="defi")

        # Check threshold is documented correctly
        assert validator.VALIDATION_THRESHOLDS["minimum_total_score"] == 85.0

    def test_score_85_should_pass(self):
        """Expression with score exactly 85.0 should pass"""
        validator = EnsembleValidator(domain="defi")

        # This would need a mock or actual expression that scores exactly 85.0
        # For now, test the threshold logic
        result = validator._check_acceptance_criteria(
            total_score=85.0,
            symbolic={"valid": True, "score": 85.0},
            dimensional={"valid": True, "score": 85.0},
            domain={"valid": True, "score": 85.0},
            edge_cases=[],
        )
        assert result == True

    def test_score_84_should_fail(self):
        """Expression with score 84.9 should fail"""
        validator = EnsembleValidator(domain="defi")

        result = validator._check_acceptance_criteria(
            total_score=84.9,
            symbolic={"valid": True, "score": 85.0},
            dimensional={"valid": True, "score": 85.0},
            domain={"valid": True, "score": 85.0},
            edge_cases=[],
        )
        assert result == False

    def test_score_94_should_pass(self):
        """Expression with score 94.0 should definitely pass"""
        validator = EnsembleValidator(domain="defi")

        result = validator._check_acceptance_criteria(
            total_score=94.0,
            symbolic={"valid": True, "score": 95.0},
            dimensional={"valid": True, "score": 95.0},
            domain={"valid": True, "score": 92.0},
            edge_cases=[],
        )
        assert result == True


class TestWeightRecalibration:
    """Test that validator weights have been properly adjusted"""

    def test_default_weights_sum_to_one(self):
        """Default weights must sum to exactly 1.0"""
        validator = EnsembleValidator(domain="defi")

        weight_sum = sum(validator.weights.values())
        assert np.isclose(weight_sum, 1.0)

    def test_dimensional_weight_increased(self):
        """Dimensional weight should be 0.30 (increased from 0.25)"""
        validator = EnsembleValidator(domain="defi")

        assert validator.weights["dimensional"] == 0.30

    def test_symbolic_weight_decreased(self):
        """Symbolic weight should be 0.30 (decreased from 0.35)"""
        validator = EnsembleValidator(domain="defi")

        assert validator.weights["symbolic"] == 0.30

    def test_domain_weight_maintained(self):
        """Domain weight should remain 0.30"""
        validator = EnsembleValidator(domain="defi")

        assert validator.weights["domain"] == 0.30

    def test_custom_weights_validation(self):
        """Custom weights that don't sum to 1.0 should raise error"""
        with pytest.raises(ValueError, match="must sum to 1.0"):
            EnsembleValidator(
                domain="defi", weights={"symbolic": 0.5, "dimensional": 0.3, "domain": 0.3, "numerical": 0.1}
            )


class TestEdgeCaseDetection:
    """Test enhanced edge case detection"""

    def test_division_by_zero_detection(self):
        """Should detect division by zero as critical edge case"""
        validator = EnsembleValidator(domain="defi")

        symbolic_result = {"valid": False, "score": 50.0, "errors": ["Division by zero detected in expression"]}
        dimensional_result = {"valid": True, "score": 95.0, "errors": []}
        domain_result = {"valid": True, "score": 90.0, "errors": []}
        numerical_result = {"score": 100.0, "errors": [], "warnings": []}

        edge_cases = validator._detect_edge_cases(symbolic_result, dimensional_result, domain_result, numerical_result)

        assert len(edge_cases) > 0
        assert any("CRITICAL" in case and "division by zero" in case.lower() for case in edge_cases)

    def test_empty_expression_detection(self):
        """Should detect empty expressions as critical edge case"""
        validator = EnsembleValidator(domain="defi")

        symbolic_result = {"valid": False, "score": 0.0, "errors": ["Empty expression provided"]}
        dimensional_result = {"valid": False, "score": 0.0, "errors": []}
        domain_result = {"valid": False, "score": 0.0, "errors": []}
        numerical_result = {"score": 100.0, "errors": [], "warnings": []}

        edge_cases = validator._detect_edge_cases(symbolic_result, dimensional_result, domain_result, numerical_result)

        assert any("CRITICAL" in case and "empty" in case.lower() for case in edge_cases)

    def test_nan_production_detection(self):
        """Should detect NaN production as critical edge case"""
        validator = EnsembleValidator(domain="defi")

        symbolic_result = {"valid": True, "score": 90.0, "errors": []}
        dimensional_result = {"valid": True, "score": 95.0, "errors": []}
        domain_result = {"valid": True, "score": 90.0, "errors": []}
        numerical_result = {"score": 50.0, "errors": ["Expression produces NaN values (3/10 samples)"], "warnings": []}

        edge_cases = validator._detect_edge_cases(symbolic_result, dimensional_result, domain_result, numerical_result)

        assert any("CRITICAL" in case and "nan" in case.lower() for case in edge_cases)

    def test_overflow_warning_detection(self):
        """Should detect overflow as warning edge case"""
        validator = EnsembleValidator(domain="defi")

        symbolic_result = {"valid": True, "score": 90.0, "errors": []}
        dimensional_result = {"valid": True, "score": 95.0, "errors": []}
        domain_result = {"valid": True, "score": 90.0, "errors": []}
        numerical_result = {"score": 85.0, "errors": [], "warnings": ["Potential numerical overflow detected"]}

        edge_cases = validator._detect_edge_cases(symbolic_result, dimensional_result, domain_result, numerical_result)

        assert any("WARNING" in case and "overflow" in case.lower() for case in edge_cases)

    def test_dimensional_inconsistency_detection(self):
        """Should detect dimensional inconsistencies as edge cases"""
        validator = EnsembleValidator(domain="defi")

        symbolic_result = {"valid": True, "score": 90.0, "errors": []}
        dimensional_result = {"valid": False, "score": 60.0, "errors": ["Dimensional inconsistency: USD + ETH"]}
        domain_result = {"valid": True, "score": 90.0, "errors": []}
        numerical_result = {"score": 100.0, "errors": [], "warnings": []}

        edge_cases = validator._detect_edge_cases(symbolic_result, dimensional_result, domain_result, numerical_result)

        assert any("DIMENSIONAL" in case for case in edge_cases)


class TestPenaltySystem:
    """Test the penalty application system"""

    def test_critical_edge_case_penalty(self):
        """Critical edge cases should incur 15-point penalty"""
        validator = EnsembleValidator(domain="defi")

        base_score = 100.0
        edge_cases = ["CRITICAL: Division by zero detected"]
        dimensional_result = {"errors": []}

        penalized_score = validator._apply_penalties(base_score, edge_cases, dimensional_result)

        assert penalized_score == 85.0  # 100 - 15

    def test_multiple_critical_penalties(self):
        """Multiple critical edge cases should stack penalties"""
        validator = EnsembleValidator(domain="defi")

        base_score = 100.0
        edge_cases = [
            "CRITICAL: Division by zero detected",
            "CRITICAL: Empty expression",
            "CRITICAL: Expression produces NaN values",
        ]
        dimensional_result = {"errors": []}

        penalized_score = validator._apply_penalties(base_score, edge_cases, dimensional_result)

        assert penalized_score == 55.0  # 100 - (3 * 15)

    def test_warning_edge_case_penalty(self):
        """Warning edge cases should incur 5-point penalty"""
        validator = EnsembleValidator(domain="defi")

        base_score = 100.0
        edge_cases = ["WARNING: Potential numerical overflow"]
        dimensional_result = {"errors": []}

        penalized_score = validator._apply_penalties(base_score, edge_cases, dimensional_result)

        assert penalized_score == 95.0  # 100 - 5

    def test_dimensional_inconsistency_penalty(self):
        """Dimensional inconsistencies should incur 20-point penalty"""
        validator = EnsembleValidator(domain="defi")

        base_score = 100.0
        edge_cases = ["DIMENSIONAL: Dimensional inconsistency: USD + ETH"]
        dimensional_result = {"errors": []}

        penalized_score = validator._apply_penalties(base_score, edge_cases, dimensional_result)

        assert penalized_score == 80.0  # 100 - 20

    def test_penalty_floor_at_zero(self):
        """Score should not go below 0 after penalties"""
        validator = EnsembleValidator(domain="defi")

        base_score = 30.0
        edge_cases = [
            "CRITICAL: Division by zero detected",
            "CRITICAL: Empty expression",
            "CRITICAL: Expression produces NaN values",
            "CRITICAL: Expression produces infinite values",
        ]
        dimensional_result = {"errors": []}

        penalized_score = validator._apply_penalties(base_score, edge_cases, dimensional_result)

        assert penalized_score == 0.0  # Can't go negative


class TestAcceptanceCriteria:
    """Test the acceptance criteria validation"""

    def test_all_criteria_met(self):
        """Should pass when all criteria are met"""
        validator = EnsembleValidator(domain="defi")

        result = validator._check_acceptance_criteria(
            total_score=90.0,
            symbolic={"valid": True, "score": 92.0},
            dimensional={"valid": True, "score": 90.0},
            domain={"valid": True, "score": 88.0},
            edge_cases=[],
        )

        assert result == True

    def test_score_too_low(self):
        """Should fail when score below 85.0"""
        validator = EnsembleValidator(domain="defi")

        result = validator._check_acceptance_criteria(
            total_score=84.0,
            symbolic={"valid": True, "score": 85.0},
            dimensional={"valid": True, "score": 85.0},
            domain={"valid": True, "score": 82.0},
            edge_cases=[],
        )

        assert result == False

    def test_symbolic_invalid(self):
        """Should fail when symbolic validation fails"""
        validator = EnsembleValidator(domain="defi")

        result = validator._check_acceptance_criteria(
            total_score=90.0,
            symbolic={"valid": False, "score": 70.0},
            dimensional={"valid": True, "score": 95.0},
            domain={"valid": True, "score": 95.0},
            edge_cases=[],
        )

        assert result == False

    def test_dimensional_invalid(self):
        """Should fail when dimensional validation fails"""
        validator = EnsembleValidator(domain="defi")

        result = validator._check_acceptance_criteria(
            total_score=90.0,
            symbolic={"valid": True, "score": 95.0},
            dimensional={"valid": False, "score": 70.0},
            domain={"valid": True, "score": 95.0},
            edge_cases=[],
        )

        assert result == False

    def test_critical_edge_cases_present(self):
        """Should fail when critical edge cases are present"""
        validator = EnsembleValidator(domain="defi")

        result = validator._check_acceptance_criteria(
            total_score=90.0,
            symbolic={"valid": True, "score": 92.0},
            dimensional={"valid": True, "score": 90.0},
            domain={"valid": True, "score": 88.0},
            edge_cases=["CRITICAL: Division by zero detected"],
        )

        assert result == False

    def test_warning_edge_cases_allowed(self):
        """Should pass with warning edge cases (not critical)"""
        validator = EnsembleValidator(domain="defi")

        result = validator._check_acceptance_criteria(
            total_score=90.0,
            symbolic={"valid": True, "score": 92.0},
            dimensional={"valid": True, "score": 90.0},
            domain={"valid": True, "score": 88.0},
            edge_cases=["WARNING: Potential overflow"],
        )

        assert result == True

    def test_strict_mode_requires_domain_valid(self):
        """In strict mode, domain validation must also pass"""
        validator = EnsembleValidator(domain="defi", strict_mode=True)

        result = validator._check_acceptance_criteria(
            total_score=90.0,
            symbolic={"valid": True, "score": 92.0},
            dimensional={"valid": True, "score": 90.0},
            domain={"valid": False, "score": 75.0},
            edge_cases=[],
        )

        assert result == False

    def test_non_strict_mode_allows_domain_invalid(self):
        """In non-strict mode, domain can be invalid if score is high"""
        validator = EnsembleValidator(domain="defi", strict_mode=False)

        result = validator._check_acceptance_criteria(
            total_score=90.0,
            symbolic={"valid": True, "score": 95.0},
            dimensional={"valid": True, "score": 95.0},
            domain={"valid": False, "score": 75.0},
            edge_cases=[],
        )

        assert result == True


class TestCompleteValidation:
    """Test complete validation workflow"""

    def test_valid_defi_expression(self):
        """Test a valid DeFi expression passes with new thresholds"""
        validator = EnsembleValidator(domain="defi")

        result = validator.validate_complete(
            expression_str="sqrt(reserve0 * reserve1)",
            variable_definitions={"reserve0": "Token 0 reserves", "reserve1": "Token 1 reserves"},
            variable_units={"reserve0": "USD", "reserve1": "USD"},
            test_data={"reserve0": np.array([100, 200, 300]), "reserve1": np.array([100, 200, 300])},
        )

        # Should pass with high score
        assert result["total_score"] >= 85.0
        assert result["acceptance_criteria"]["minimum_score_met"] == True
        assert result["acceptance_criteria"]["threshold_used"] == 85.0

    def test_division_by_zero_fails(self):
        """Test that division by zero is properly caught"""
        validator = EnsembleValidator(domain="defi")

        result = validator.validate_complete(expression_str="1 / 0", variable_definitions={}, variable_units={})

        # Should fail
        assert result["valid"] == False
        assert len(result["edge_cases_detected"]) > 0
        assert any("division by zero" in case.lower() for case in result["edge_cases_detected"])

    def test_result_includes_acceptance_criteria(self):
        """Test that results include acceptance criteria details"""
        validator = EnsembleValidator(domain="defi")

        result = validator.validate_complete(
            expression_str="x + y",
            variable_definitions={"x": "Variable X", "y": "Variable Y"},
            variable_units={"x": "USD", "y": "USD"},
        )

        assert "acceptance_criteria" in result
        assert "minimum_score_met" in result["acceptance_criteria"]
        assert "symbolic_valid" in result["acceptance_criteria"]
        assert "dimensional_valid" in result["acceptance_criteria"]
        assert "domain_valid" in result["acceptance_criteria"]
        assert "no_critical_edge_cases" in result["acceptance_criteria"]
        assert "threshold_used" in result["acceptance_criteria"]
        assert result["acceptance_criteria"]["threshold_used"] == 85.0

    def test_result_includes_base_and_penalized_scores(self):
        """Test that results show both base and penalized scores"""
        validator = EnsembleValidator(domain="defi")

        result = validator.validate_complete(
            expression_str="x + y",
            variable_definitions={"x": "Variable X", "y": "Variable Y"},
            variable_units={"x": "USD", "y": "USD"},
        )

        assert "base_score" in result
        assert "total_score" in result
        # Total score should be <= base score (penalties applied)
        assert result["total_score"] <= result["base_score"]


class TestStatistics:
    """Test statistics gathering with new thresholds"""

    def test_statistics_include_threshold(self):
        """Statistics should document which threshold was used"""
        validator = EnsembleValidator(domain="defi")

        # Run a validation
        validator.validate_complete(
            expression_str="x + y", variable_definitions={"x": "X", "y": "Y"}, variable_units={"x": "USD", "y": "USD"}
        )

        stats = validator.get_statistics()
        assert "threshold_used" in stats
        assert stats["threshold_used"] == 85.0

    def test_success_rate_calculation(self):
        """Test that success rate is calculated correctly"""
        validator = EnsembleValidator(domain="defi")

        # Run multiple validations
        expressions = [
            ("x + y", True),  # Should pass
            ("1 / 0", False),  # Should fail
            ("sqrt(x)", True),  # Should pass
        ]

        for expr, _ in expressions:
            validator.validate_complete(
                expression_str=expr, variable_definitions={"x": "X", "y": "Y"}, variable_units={"x": "USD", "y": "USD"}
            )

        stats = validator.get_statistics()
        assert "success_rate" in stats
        assert 0 <= stats["success_rate"] <= 1.0


class TestRecommendations:
    """Test recommendation generation"""

    def test_edge_case_recommendations_prioritized(self):
        """Edge case fixes should be highest priority recommendations"""
        validator = EnsembleValidator(domain="defi")

        symbolic = {"valid": False, "score": 50.0, "errors": ["Division by zero"]}
        dimensional = {"valid": True, "score": 95.0, "errors": [], "warnings": []}
        domain = {"valid": True, "score": 90.0, "errors": [], "warnings": []}
        numerical = {"score": 100.0, "errors": [], "warnings": []}
        edge_cases = ["CRITICAL: Division by zero detected"]

        recommendations = validator._generate_recommendations(symbolic, dimensional, domain, numerical, edge_cases)

        # First recommendation should be about critical edge cases
        assert len(recommendations) > 0
        assert "CRITICAL" in recommendations[0] or "🔴" in recommendations[0]

    def test_no_issues_gives_success_message(self):
        """When no issues exist, should get success message"""
        validator = EnsembleValidator(domain="defi")

        symbolic = {"valid": True, "score": 95.0, "errors": [], "warnings": []}
        dimensional = {"valid": True, "score": 95.0, "errors": [], "warnings": []}
        domain = {"valid": True, "score": 95.0, "errors": [], "warnings": []}
        numerical = {"score": 100.0, "errors": [], "warnings": []}
        edge_cases = []

        recommendations = validator._generate_recommendations(symbolic, dimensional, domain, numerical, edge_cases)

        assert len(recommendations) == 1
        assert "✅" in recommendations[0] or "pass" in recommendations[0].lower()


# Fixtures


@pytest.fixture
def defi_validator():
    """Fixture providing a DeFi domain validator"""
    return EnsembleValidator(domain="defi")


@pytest.fixture
def strict_validator():
    """Fixture providing a strict mode validator"""
    return EnsembleValidator(domain="defi", strict_mode=True)


@pytest.fixture
def sample_valid_expression():
    """Fixture providing a valid test expression"""
    return {
        "expression_str": "sqrt(reserve0 * reserve1)",
        "variable_definitions": {"reserve0": "Token 0 reserves", "reserve1": "Token 1 reserves"},
        "variable_units": {"reserve0": "USD", "reserve1": "USD"},
        "test_data": {"reserve0": np.array([100, 200, 300]), "reserve1": np.array([100, 200, 300])},
    }


@pytest.fixture
def sample_invalid_expression():
    """Fixture providing an invalid test expression"""
    return {"expression_str": "1 / 0", "variable_definitions": {}, "variable_units": {}, "test_data": None}


if __name__ == "__main__":
    # Run tests with pytest
    pytest.main([__file__, "-v", "--tb=short"])
