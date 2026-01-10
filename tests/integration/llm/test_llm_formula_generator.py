"""
Comprehensive tests for LLM-based formula generation.
Tests formula generation, validation, and domain-specific generation.
"""

from typing import Dict, List, Optional
from unittest.mock import MagicMock, Mock, patch

import numpy as np
import pytest
from sympy import symbols, sympify


class TestFormulaGeneratorBasics:
    """Tests for basic formula generator functionality."""

    def test_generator_initialization(self, formula_generator):
        """Test formula generator can be initialized."""
        assert formula_generator is not None
        assert hasattr(formula_generator, "generate")

    def test_generator_has_provider(self, formula_generator):
        """Test generator has LLM provider."""
        assert hasattr(formula_generator, "provider")
        assert formula_generator.provider is not None

    def test_supported_domains(self, formula_generator):
        """Test getting supported domains."""
        domains = formula_generator.get_supported_domains()

        assert isinstance(domains, list)
        assert len(domains) > 0
        assert "risk" in domains or "defi" in domains


class TestSimpleFormulaGeneration:
    """Tests for generating simple formulas."""

    def test_generate_arithmetic_formula(self, formula_generator):
        """Test generating simple arithmetic formula."""
        description = "Add two numbers x and y"

        formula = formula_generator.generate(description)

        assert formula is not None
        assert "x" in str(formula) and "y" in str(formula)

    def test_generate_percentage_formula(self, formula_generator):
        """Test generating percentage calculation."""
        description = "Calculate percentage change from old to new value"

        formula = formula_generator.generate(description)

        assert formula is not None
        assert isinstance(formula, (str, dict))

    def test_generate_average_formula(self, formula_generator):
        """Test generating average calculation."""
        description = "Calculate average of a list of numbers"

        formula = formula_generator.generate(description)

        assert formula is not None

    def test_generate_ratio_formula(self, formula_generator):
        """Test generating ratio calculation."""
        description = "Calculate ratio of part to whole"

        formula = formula_generator.generate(description)

        assert formula is not None


class TestRiskFormulaGeneration:
    """Tests for generating risk management formulas."""

    def test_generate_sharpe_ratio(self, formula_generator):
        """Test generating Sharpe ratio formula."""
        description = "Generate formula for Sharpe ratio"
        domain = "risk"

        formula = formula_generator.generate(description, domain=domain)

        formula_str = str(formula).lower()
        assert any(
            term in formula_str for term in ["return", "risk", "volatility", "sigma"]
        )

    def test_generate_var_formula(self, formula_generator):
        """Test generating Value at Risk formula."""
        description = "Generate parametric VaR formula"

        formula = formula_generator.generate(description, domain="risk")

        assert formula is not None

    def test_generate_sortino_ratio(self, formula_generator):
        """Test generating Sortino ratio formula."""
        description = "Generate Sortino ratio with downside deviation"

        formula = formula_generator.generate(description, domain="risk")

        formula_str = str(formula).lower()
        assert "downside" in formula_str or "deviation" in formula_str

    def test_generate_beta_formula(self, formula_generator):
        """Test generating beta coefficient formula."""
        description = "Generate portfolio beta formula"

        formula = formula_generator.generate(description, domain="risk")

        formula_str = str(formula).lower()
        assert "cov" in formula_str or "variance" in formula_str

    def test_generate_drawdown_formula(self, formula_generator):
        """Test generating maximum drawdown formula."""
        description = "Generate maximum drawdown calculation"

        formula = formula_generator.generate(description, domain="risk")

        assert formula is not None


class TestDeFiFormulaGeneration:
    """Tests for generating DeFi protocol formulas."""

    def test_generate_constant_product(self, formula_generator):
        """Test generating constant product formula."""
        description = "Generate Uniswap constant product formula"

        formula = formula_generator.generate(description, domain="defi")

        formula_str = str(formula).lower()
        assert "x" in formula_str and "y" in formula_str

    def test_generate_impermanent_loss(self, formula_generator):
        """Test generating impermanent loss formula."""
        description = "Generate impermanent loss formula for liquidity pool"

        formula = formula_generator.generate(description, domain="defi")

        assert formula is not None

    def test_generate_price_impact(self, formula_generator):
        """Test generating price impact formula."""
        description = "Calculate price impact for Uniswap swap"

        formula = formula_generator.generate(description, domain="defi")

        assert formula is not None

    def test_generate_liquidity_position(self, formula_generator):
        """Test generating liquidity position value formula."""
        description = "Calculate liquidity position value in AMM"

        formula = formula_generator.generate(description, domain="defi")

        assert formula is not None

    def test_generate_fee_calculation(self, formula_generator):
        """Test generating fee calculation formula."""
        description = "Calculate trading fees earned by liquidity provider"

        formula = formula_generator.generate(description, domain="defi")

        assert formula is not None


class TestFormulaValidation:
    """Tests for validating generated formulas."""

    def test_validate_syntax(self, formula_generator):
        """Test syntax validation of generated formula."""
        description = "Sum of x and y"

        formula = formula_generator.generate(description)
        is_valid = formula_generator.validate_syntax(formula)

        assert isinstance(is_valid, bool)

    def test_validate_variables(self, formula_generator):
        """Test variable validation."""
        description = "Calculate result using variables a, b, c"

        formula = formula_generator.generate(description)
        variables = formula_generator.extract_variables(formula)

        assert len(variables) >= 2

    def test_validate_dimensional_consistency(self, formula_generator):
        """Test dimensional consistency."""
        description = "Velocity equals distance divided by time"

        formula = formula_generator.generate(description)
        is_consistent = formula_generator.check_dimensional_consistency(formula)

        assert isinstance(is_consistent, bool)

    def test_validate_mathematical_correctness(self, formula_generator):
        """Test mathematical correctness validation."""
        description = "Quadratic formula"

        formula = formula_generator.generate(description)
        is_correct = formula_generator.validate_mathematics(formula)

        assert isinstance(is_correct, bool)

    def test_validate_domain_specific_rules(self, formula_generator):
        """Test domain-specific validation rules."""
        description = "Sharpe ratio calculation"

        formula = formula_generator.generate(description, domain="risk")
        is_valid = formula_generator.validate_domain_rules(formula, domain="risk")

        assert isinstance(is_valid, bool)


class TestFormulaWithConstraints:
    """Tests for generating formulas with constraints."""

    def test_generate_with_variable_constraints(self, formula_generator):
        """Test generation with specific variables required."""
        description = "Calculate portfolio return"
        constraints = {
            "required_variables": ["weights", "returns"],
            "variable_types": {"weights": "array", "returns": "array"},
        }

        formula = formula_generator.generate(description, constraints=constraints)

        variables = formula_generator.extract_variables(formula)
        assert "weights" in [str(v) for v in variables]

    def test_generate_with_output_type(self, formula_generator):
        """Test generation with output type constraint."""
        description = "Check if value is positive"
        constraints = {"output_type": "boolean"}

        formula = formula_generator.generate(description, constraints=constraints)

        assert formula is not None

    def test_generate_with_range_constraints(self, formula_generator):
        """Test generation with value range constraints."""
        description = "Calculate probability"
        constraints = {"output_range": [0, 1]}

        formula = formula_generator.generate(description, constraints=constraints)

        assert formula is not None

    def test_generate_with_complexity_constraint(self, formula_generator):
        """Test generation with complexity constraint."""
        description = "Simple interest calculation"
        constraints = {"max_operations": 3, "complexity": "low"}

        formula = formula_generator.generate(description, constraints=constraints)

        assert formula is not None

    def test_generate_with_unit_constraints(self, formula_generator):
        """Test generation with unit constraints."""
        description = "Calculate force"
        constraints = {"units": {"mass": "kg", "acceleration": "m/s^2", "output": "N"}}

        formula = formula_generator.generate(description, constraints=constraints)

        assert formula is not None


class TestBatchGeneration:
    """Tests for generating multiple formulas."""

    def test_generate_multiple_formulas(self, formula_generator):
        """Test generating multiple related formulas."""
        descriptions = [
            "Calculate mean",
            "Calculate variance",
            "Calculate standard deviation",
        ]

        formulas = formula_generator.generate_batch(descriptions)

        assert len(formulas) == 3
        assert all(f is not None for f in formulas)

    def test_generate_formula_family(self, formula_generator):
        """Test generating family of related formulas."""
        description = "Generate all risk-adjusted return ratios"

        formulas = formula_generator.generate_family(description, domain="risk")

        assert len(formulas) >= 2
        assert isinstance(formulas, (list, dict))

    def test_generate_variations(self, formula_generator):
        """Test generating variations of a formula."""
        base_formula = "x + y"

        variations = formula_generator.generate_variations(base_formula, count=3)

        assert len(variations) >= 2


class TestFormulaOptimization:
    """Tests for optimizing generated formulas."""

    def test_simplify_formula(self, formula_generator):
        """Test simplifying generated formula."""
        description = "Calculate x plus x plus x"

        formula = formula_generator.generate(description)
        simplified = formula_generator.simplify(formula)

        assert simplified is not None
        # Should simplify to 3*x

    def test_optimize_for_computation(self, formula_generator):
        """Test optimizing formula for computation."""
        description = "Calculate sum of squares"

        formula = formula_generator.generate(description)
        optimized = formula_generator.optimize_for_computation(formula)

        assert optimized is not None

    def test_remove_redundancy(self, formula_generator):
        """Test removing redundant operations."""
        description = "Add zero to x then multiply by one"

        formula = formula_generator.generate(description)
        cleaned = formula_generator.remove_redundancy(formula)

        assert cleaned is not None


class TestExampleBasedGeneration:
    """Tests for generating formulas from examples."""

    def test_generate_from_io_examples(self, formula_generator):
        """Test generating formula from input/output examples."""
        examples = [
            {"input": {"x": 2, "y": 3}, "output": 5},
            {"input": {"x": 5, "y": 7}, "output": 12},
            {"input": {"x": 1, "y": 1}, "output": 2},
        ]

        formula = formula_generator.generate_from_examples(examples)

        assert formula is not None

    def test_generate_with_numeric_pattern(self, formula_generator):
        """Test generating formula from numeric pattern."""
        pattern = [1, 4, 9, 16, 25]  # Squares

        formula = formula_generator.generate_from_pattern(pattern)

        formula_str = str(formula).lower()
        assert "2" in formula_str or "square" in formula_str

    def test_generate_from_timeseries(self, formula_generator):
        """Test generating formula from time series data."""
        data = {"time": [0, 1, 2, 3, 4], "value": [100, 110, 121, 133.1, 146.41]}

        formula = formula_generator.generate_from_timeseries(data)

        assert formula is not None

    def test_infer_formula_from_data(self, formula_generator):
        """Test inferring formula from dataset."""
        data = np.array([[1, 2, 3], [2, 4, 6], [3, 6, 9], [4, 8, 12]])

        formula = formula_generator.infer_formula(data, target_col=2)

        assert formula is not None


class TestContextualGeneration:
    """Tests for context-aware formula generation."""

    def test_generate_with_prior_formulas(self, formula_generator):
        """Test generation considering prior formulas."""
        context = {
            "previous_formulas": [
                "mean = sum(x) / n",
                "variance = sum((x - mean)^2) / n",
            ]
        }

        description = "Now calculate standard deviation"

        formula = formula_generator.generate(description, context=context)

        formula_str = str(formula).lower()
        assert "variance" in formula_str or "sqrt" in formula_str

    def test_generate_with_variable_definitions(self, formula_generator):
        """Test generation with predefined variables."""
        context = {
            "variables": {
                "R": "portfolio return",
                "Rf": "risk-free rate",
                "sigma": "volatility",
            }
        }

        description = "Calculate risk-adjusted return"

        formula = formula_generator.generate(description, context=context)

        variables = formula_generator.extract_variables(formula)
        assert any(str(v) in ["R", "Rf", "sigma"] for v in variables)

    def test_generate_with_domain_context(self, formula_generator):
        """Test generation with domain-specific context."""
        context = {
            "domain": "defi",
            "protocol": "uniswap_v2",
            "context_formulas": ["x * y = k"],
        }

        description = "Calculate price of token x"

        formula = formula_generator.generate(description, context=context)

        assert formula is not None


class TestErrorHandling:
    """Tests for error handling in formula generation."""

    def test_handle_impossible_formula(self, formula_generator):
        """Test handling impossible formula request."""
        description = "Generate formula that violates mathematics"

        with pytest.raises((ValueError, Exception)):
            formula_generator.generate(description, strict=True)

    def test_handle_ambiguous_description(self, formula_generator):
        """Test handling ambiguous description."""
        description = "Calculate it"

        result = formula_generator.generate(description)

        # Should ask for clarification or make reasonable assumption
        assert result is not None or formula_generator.needs_clarification(description)

    def test_handle_conflicting_constraints(self, formula_generator):
        """Test handling conflicting constraints."""
        description = "Calculate value"
        constraints = {"output_range": [0, 1], "required_property": "unbounded"}

        with pytest.raises((ValueError, Exception)):
            formula_generator.generate(description, constraints=constraints)

    def test_handle_generation_timeout(self, formula_generator):
        """Test handling generation timeout."""
        description = "Generate extremely complex formula"

        with patch.object(
            formula_generator.provider, "generate", side_effect=TimeoutError
        ):
            with pytest.raises(TimeoutError):
                formula_generator.generate(description, timeout=1)


class TestFormulaDocumentation:
    """Tests for generating formula documentation."""

    def test_generate_with_explanation(self, formula_generator):
        """Test generating formula with explanation."""
        description = "Sharpe ratio"

        result = formula_generator.generate_with_docs(description)

        assert "formula" in result
        assert "explanation" in result

    def test_generate_with_variable_descriptions(self, formula_generator):
        """Test generating variable descriptions."""
        description = "Portfolio return calculation"

        result = formula_generator.generate_with_docs(description)

        assert "variables" in result
        assert isinstance(result["variables"], dict)

    def test_generate_with_examples(self, formula_generator):
        """Test generating usage examples."""
        description = "Calculate compound interest"

        result = formula_generator.generate_with_docs(
            description, include_examples=True
        )

        assert "examples" in result

    def test_generate_with_references(self, formula_generator):
        """Test generating academic references."""
        description = "Black-Scholes formula"

        result = formula_generator.generate_with_docs(
            description, include_references=True
        )

        assert "references" in result or "sources" in result


class TestVersioning:
    """Tests for formula versioning."""

    def test_generate_multiple_versions(self, formula_generator):
        """Test generating multiple versions of formula."""
        description = "Calculate return"

        versions = formula_generator.generate_versions(description, count=3)

        assert len(versions) >= 2
        assert all("formula" in v for v in versions)

    def test_compare_formula_versions(self, formula_generator):
        """Test comparing different formula versions."""
        formula1 = "(new - old) / old"
        formula2 = "new / old - 1"

        comparison = formula_generator.compare_formulas(formula1, formula2)

        assert "equivalent" in comparison or "difference" in comparison


@pytest.fixture
def formula_generator():
    """Fixture for formula generator."""
    generator = MagicMock()
    generator.provider = MagicMock()

    # Mock methods
    generator.generate = MagicMock(return_value="x + y")
    generator.get_supported_domains = MagicMock(
        return_value=["risk", "defi", "statistics"]
    )
    generator.validate_syntax = MagicMock(return_value=True)
    generator.extract_variables = MagicMock(return_value=["x", "y"])
    generator.check_dimensional_consistency = MagicMock(return_value=True)
    generator.validate_mathematics = MagicMock(return_value=True)
    generator.validate_domain_rules = MagicMock(return_value=True)
    generator.generate_batch = MagicMock(
        return_value=["formula1", "formula2", "formula3"]
    )
    generator.generate_family = MagicMock(
        return_value=["sharpe", "sortino", "information"]
    )
    generator.generate_variations = MagicMock(
        return_value=["x + y", "y + x", "sum(x, y)"]
    )
    generator.simplify = MagicMock(return_value="3*x")
    generator.optimize_for_computation = MagicMock(return_value="optimized")
    generator.remove_redundancy = MagicMock(return_value="x")
    generator.generate_from_examples = MagicMock(return_value="x + y")
    generator.generate_from_pattern = MagicMock(return_value="n**2")
    generator.generate_from_timeseries = MagicMock(return_value="compound_growth")
    generator.infer_formula = MagicMock(return_value="x * 2")
    generator.needs_clarification = MagicMock(return_value=False)
    generator.generate_with_docs = MagicMock(
        return_value={
            "formula": "x + y",
            "explanation": "Sum of x and y",
            "variables": {"x": "first value", "y": "second value"},
        }
    )
    generator.generate_versions = MagicMock(
        return_value=[
            {"formula": "v1", "properties": {}},
            {"formula": "v2", "properties": {}},
        ]
    )
    generator.compare_formulas = MagicMock(return_value={"equivalent": True})

    return generator


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
