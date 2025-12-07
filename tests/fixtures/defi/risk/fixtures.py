"""DeFi risk calculation fixtures"""

import pytest


@pytest.fixture
def risk_metrics():
    """Standard risk metrics"""
    return {
        "volatility": 0.15,
        "var_95": 0.025,
        "var_99": 0.05,
        "sharpe_ratio": 1.5,
        "sortino_ratio": 2.0,
        "max_drawdown": 0.20,
        "beta": 1.2,
        "alpha": 0.03,
    }


@pytest.fixture
def risk_free_rate():
    """Risk-free rate for calculations"""
    return 0.04  # 4%


@pytest.fixture
def market_conditions():
    """Market condition scenarios"""
    return {
        "bull_market": {"trend": "up", "volatility": 0.10, "sentiment": 0.8},
        "bear_market": {"trend": "down", "volatility": 0.25, "sentiment": 0.2},
        "sideways": {"trend": "neutral", "volatility": 0.12, "sentiment": 0.5},
    }
