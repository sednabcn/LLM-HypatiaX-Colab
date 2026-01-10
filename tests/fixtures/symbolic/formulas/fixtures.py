"""Symbolic formula fixtures"""

import pytest


@pytest.fixture
def basic_formulas():
    """Simple arithmetic formulas"""
    return ["a + b", "x * y", "(a + b) / c", "2 * pi * r", "x^2 + 2*x + 1"]


@pytest.fixture
def financial_formulas():
    """Financial calculation formulas"""
    return {
        "sharpe_ratio": "(return - risk_free_rate) / volatility",
        "compound_interest": "principal * (1 + rate)^time",
        "present_value": "future_value / (1 + rate)^periods",
        "var_95": "portfolio_value * volatility * 1.645 * sqrt(time)",
        "black_scholes": "S * N(d1) - K * exp(-r*T) * N(d2)",
        "capm": "risk_free + beta * (market_return - risk_free)",
    }


@pytest.fixture
def defi_formulas():
    """DeFi-specific formulas"""
    return {
        "impermanent_loss": "2*sqrt(price_ratio)/(1+price_ratio) - 1",
        "liquidity_ratio": "total_liquidity / total_volume",
        "apy": "(1 + apr/n)^n - 1",
        "tvl_ratio": "protocol_tvl / market_tvl",
        "utilization_rate": "borrowed / supplied",
    }


@pytest.fixture
def statistical_formulas():
    """Statistical formulas"""
    return {
        "mean": "sum(values) / count(values)",
        "variance": "sum((x - mean)^2) / n",
        "std_dev": "sqrt(variance)",
        "correlation": "covariance(x, y) / (std(x) * std(y))",
        "z_score": "(x - mean) / std_dev",
    }


@pytest.fixture
def invalid_formulas():
    """Formulas that should fail parsing"""
    return [
        "a +",  # Incomplete expression
        "/ b",  # Missing left operand
        "(a + b",  # Unmatched parenthesis
        "a ** ** b",  # Invalid operator sequence
        "sin(",  # Incomplete function call
        "a b",  # Missing operator
        "1 2 3",  # Multiple values without operators
    ]


@pytest.fixture
def formula_with_variables():
    """Formula paired with variable values"""
    return {
        "formula": "a * x^2 + b * x + c",
        "variables": {"a": 1, "b": -3, "c": 2, "x": 5},
        "expected_result": 12,  # 1*25 + (-3)*5 + 2 = 12
    }


@pytest.fixture
def formula_evaluation_cases():
    """Multiple formula evaluation test cases"""
    return [
        {"formula": "2 * x + 5", "variables": {"x": 3}, "expected": 11},
        {
            "formula": "(a + b) * c",
            "variables": {"a": 2, "b": 3, "c": 4},
            "expected": 20,
        },
        {"formula": "sqrt(x^2 + y^2)", "variables": {"x": 3, "y": 4}, "expected": 5.0},
    ]
