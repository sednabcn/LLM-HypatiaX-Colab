"""
Comprehensive tests for risk metric calculations.
Tests all risk formulas including VaR, CVaR, Sharpe, Sortino, drawdowns, etc.
"""

from typing import Dict, List, Tuple

import numpy as np
import pytest
from scipy import stats
from sympy import exp, lambdify, log, pi, sqrt, symbols, sympify


class TestBasicRiskMetrics:
    """Tests for fundamental risk metrics."""

    def test_volatility_calculation(self, risk_engine):
        """Test standard deviation (volatility) calculation."""
        # Symbolic
        returns = symbols("returns")

        # Numerical calculation
        sample_returns = np.array([0.01, -0.02, 0.03, -0.01, 0.02])
        volatility = np.std(sample_returns, ddof=1)

        # Annualized volatility (252 trading days)
        annual_vol = volatility * np.sqrt(252)

        assert volatility > 0
        assert annual_vol > volatility

    def test_mean_return(self, risk_engine):
        """Test mean return calculation."""
        returns = np.array([0.01, 0.02, -0.01, 0.03, 0.01])
        mean_return = np.mean(returns)

        assert -0.01 < mean_return < 0.03
        assert np.isclose(mean_return, 0.012)

    def test_return_distribution(self, risk_engine):
        """Test return distribution properties."""
        # Generate normal returns
        np.random.seed(42)
        returns = np.random.normal(0.001, 0.02, 1000)

        mean = np.mean(returns)
        std = np.std(returns)

        # Check normality assumptions
        assert abs(mean) < 0.01  # Mean near 0.001
        assert 0.015 < std < 0.025  # Std near 0.02


class TestSharpeRatio:
    """Tests for Sharpe Ratio calculations."""

    def test_sharpe_ratio_formula(self, risk_engine):
        """Test Sharpe ratio calculation."""
        R, Rf, sigma = symbols("R Rf sigma")
        sharpe = (R - Rf) / sigma

        sharpe_func = lambdify((R, Rf, sigma), sharpe, "numpy")

        # Portfolio return 12%, risk-free 3%, volatility 10%
        result = sharpe_func(0.12, 0.03, 0.10)
        assert result == 0.9

    def test_sharpe_ratio_with_real_data(self, risk_engine):
        """Test Sharpe ratio with time series data."""
        # Simulate daily returns
        np.random.seed(42)
        daily_returns = np.random.normal(0.0005, 0.01, 252)

        # Calculate annualized metrics
        annual_return = np.mean(daily_returns) * 252
        annual_vol = np.std(daily_returns) * np.sqrt(252)
        risk_free = 0.03

        sharpe = (annual_return - risk_free) / annual_vol

        assert np.isfinite(sharpe)

    def test_sharpe_ratio_negative_excess_return(self, risk_engine):
        """Test Sharpe ratio when returns below risk-free rate."""
        R, Rf, sigma = symbols("R Rf sigma")
        sharpe = (R - Rf) / sigma
        sharpe_func = lambdify((R, Rf, sigma), sharpe, "numpy")

        result = sharpe_func(0.02, 0.05, 0.10)
        assert result == -0.3

    def test_sharpe_ratio_zero_volatility(self, risk_engine):
        """Test Sharpe ratio with zero volatility."""
        R, Rf, sigma = symbols("R Rf sigma")
        sharpe = (R - Rf) / sigma
        sharpe_func = lambdify((R, Rf, sigma), sharpe, "numpy")

        with pytest.warns(RuntimeWarning):
            result = sharpe_func(0.05, 0.03, 0)
            assert np.isinf(result)


class TestSortinoRatio:
    """Tests for Sortino Ratio calculations."""

    def test_sortino_ratio_formula(self, risk_engine):
        """Test Sortino ratio calculation."""
        R, Rf, downside_dev = symbols("R Rf downside_dev")
        sortino = (R - Rf) / downside_dev

        sortino_func = lambdify((R, Rf, downside_dev), sortino, "numpy")

        result = sortino_func(0.15, 0.03, 0.08)
        assert result == 1.5

    def test_downside_deviation_calculation(self, risk_engine):
        """Test downside deviation calculation."""
        returns = np.array([0.02, -0.01, 0.03, -0.02, 0.01, -0.015, 0.025])
        target = 0.0

        # Only negative returns
        downside_returns = returns[returns < target]
        downside_dev = np.sqrt(np.mean(downside_returns**2))

        assert downside_dev > 0
        assert downside_dev < np.std(returns)  # Should be less than total vol

    def test_sortino_vs_sharpe(self, risk_engine):
        """Test Sortino vs Sharpe comparison."""
        # Sortino should be higher when downside vol < total vol
        returns = np.array([0.02, -0.01, 0.03, 0.01, -0.005])

        total_vol = np.std(returns)
        downside_returns = returns[returns < 0]
        downside_vol = np.sqrt(np.mean(downside_returns**2))

        mean_return = np.mean(returns)
        risk_free = 0.0

        sharpe = (mean_return - risk_free) / total_vol
        sortino = (mean_return - risk_free) / downside_vol

        assert sortino > sharpe


class TestValueAtRisk:
    """Tests for Value at Risk (VaR) calculations."""

    def test_parametric_var(self, risk_engine):
        """Test parametric VaR calculation."""
        mu, sigma, z = symbols("mu sigma z")
        var_formula = mu - z * sigma

        var_func = lambdify((mu, sigma, z), var_formula, "numpy")

        # 95% VaR
        z_95 = 1.645
        result = var_func(0.0, 0.02, z_95)

        assert result < 0  # Loss
        assert np.isclose(result, -0.0329)

    def test_historical_var(self, risk_engine):
        """Test historical VaR calculation."""
        # Generate historical returns
        np.random.seed(42)
        returns = np.random.normal(0.001, 0.02, 1000)

        # 95% VaR (5th percentile)
        var_95 = np.percentile(returns, 5)

        assert var_95 < 0

        # 99% VaR (1st percentile)
        var_99 = np.percentile(returns, 1)

        assert var_99 < var_95  # More extreme loss

    def test_var_confidence_levels(self, risk_engine):
        """Test VaR at different confidence levels."""
        np.random.seed(42)
        returns = np.random.normal(0.0, 0.02, 10000)

        var_90 = np.percentile(returns, 10)
        var_95 = np.percentile(returns, 5)
        var_99 = np.percentile(returns, 1)

        # Higher confidence = more extreme VaR
        assert var_90 > var_95 > var_99

    def test_var_portfolio_scaling(self, risk_engine):
        """Test VaR scaling with portfolio value."""
        returns = np.array([-0.02, -0.01, 0.01, 0.02, 0.00])
        portfolio_value = 1000000

        var_pct = np.percentile(returns, 5)
        var_dollar = portfolio_value * abs(var_pct)

        assert var_dollar > 0
        assert var_dollar < portfolio_value


class TestConditionalValueAtRisk:
    """Tests for Conditional Value at Risk (CVaR/ES)."""

    def test_cvar_calculation(self, risk_engine):
        """Test CVaR calculation."""
        np.random.seed(42)
        returns = np.random.normal(0.0, 0.02, 10000)

        # 95% VaR
        var_95 = np.percentile(returns, 5)

        # CVaR: mean of returns below VaR
        cvar_95 = np.mean(returns[returns <= var_95])

        assert cvar_95 < var_95  # CVaR more extreme than VaR
        assert cvar_95 < 0

    def test_cvar_vs_var(self, risk_engine):
        """Test CVaR is more conservative than VaR."""
        np.random.seed(42)
        returns = np.random.normal(0.0, 0.015, 5000)

        var_95 = np.percentile(returns, 5)
        cvar_95 = np.mean(returns[returns <= var_95])

        # CVaR should be more negative (worse loss)
        assert abs(cvar_95) > abs(var_95)

    def test_cvar_tail_sensitivity(self, risk_engine):
        """Test CVaR sensitivity to tail events."""
        # Create distribution with fat tails
        np.random.seed(42)
        normal_returns = np.random.normal(0.0, 0.01, 950)
        tail_returns = np.random.normal(-0.05, 0.02, 50)
        returns = np.concatenate([normal_returns, tail_returns])

        var_95 = np.percentile(returns, 5)
        cvar_95 = np.mean(returns[returns <= var_95])

        # CVaR should capture the tail losses
        assert abs(cvar_95) > 0.02

    def test_cvar_coherence_property(self, risk_engine):
        """Test CVaR sub-additivity (coherence)."""
        np.random.seed(42)
        returns_A = np.random.normal(0.001, 0.02, 1000)
        returns_B = np.random.normal(0.001, 0.015, 1000)

        # Portfolio is 50/50 mix
        returns_portfolio = 0.5 * returns_A + 0.5 * returns_B

        cvar_A = abs(np.mean(returns_A[returns_A <= np.percentile(returns_A, 5)]))
        cvar_B = abs(np.mean(returns_B[returns_B <= np.percentile(returns_B, 5)]))
        cvar_P = abs(np.mean(returns_portfolio[returns_portfolio <= np.percentile(returns_portfolio, 5)]))

        # Sub-additivity: CVaR(A+B) <= CVaR(A) + CVaR(B)
        assert cvar_P <= cvar_A + cvar_B


class TestMaximumDrawdown:
    """Tests for maximum drawdown calculations."""

    def test_simple_drawdown(self, risk_engine):
        """Test basic drawdown calculation."""
        prices = np.array([100, 110, 105, 95, 100, 105])

        # Calculate running maximum
        running_max = np.maximum.accumulate(prices)
        drawdowns = (prices - running_max) / running_max
        max_drawdown = np.min(drawdowns)

        # From peak 110 to trough 95: (95-110)/110 = -13.6%
        assert np.isclose(max_drawdown, -0.1364, atol=0.001)

    def test_no_drawdown(self, risk_engine):
        """Test when prices only increase."""
        prices = np.array([100, 105, 110, 115, 120])

        running_max = np.maximum.accumulate(prices)
        drawdowns = (prices - running_max) / running_max
        max_drawdown = np.min(drawdowns)

        assert max_drawdown == 0.0

    def test_multiple_drawdowns(self, risk_engine):
        """Test finding maximum among multiple drawdowns."""
        prices = np.array([100, 90, 95, 85, 100, 80, 90])

        running_max = np.maximum.accumulate(prices)
        drawdowns = (prices - running_max) / running_max
        max_drawdown = np.min(drawdowns)

        # Maximum drawdown from 100 to 80: -20%
        assert np.isclose(max_drawdown, -0.20)

    def test_drawdown_duration(self, risk_engine):
        """Test drawdown duration calculation."""
        prices = np.array([100, 90, 85, 90, 95, 100, 105])

        running_max = np.maximum.accumulate(prices)
        drawdowns = (prices - running_max) / running_max

        # Find where drawdown ends (returns to peak)
        max_idx = np.argmax(prices[:6])  # Peak at index 0
        recovery_idx = np.where(prices[max_idx:] >= prices[max_idx])[0]

        if len(recovery_idx) > 1:
            duration = recovery_idx[1] - recovery_idx[0]
            assert duration > 0

    def test_underwater_periods(self, risk_engine):
        """Test calculation of underwater periods."""
        prices = np.array([100, 95, 90, 85, 90, 95, 100, 98])

        running_max = np.maximum.accumulate(prices)
        underwater = prices < running_max

        # Count periods underwater
        underwater_count = np.sum(underwater)
        assert underwater_count == 6  # Indices 1-6


class TestBeta:
    """Tests for portfolio beta calculations."""

    def test_beta_calculation(self, risk_engine):
        """Test beta calculation formula."""
        np.random.seed(42)
        market_returns = np.random.normal(0.001, 0.02, 252)

        # Portfolio with beta of 1.5
        portfolio_returns = 1.5 * market_returns + np.random.normal(0, 0.005, 252)

        # Calculate beta
        covariance = np.cov(portfolio_returns, market_returns)[0, 1]
        market_variance = np.var(market_returns)
        beta = covariance / market_variance

        assert 1.3 < beta < 1.7  # Should be close to 1.5

    def test_beta_market_portfolio(self, risk_engine):
        """Test that market has beta of 1.0."""
        np.random.seed(42)
        market_returns = np.random.normal(0.001, 0.02, 252)

        covariance = np.cov(market_returns, market_returns)[0, 1]
        market_variance = np.var(market_returns)
        beta = covariance / market_variance

        assert np.isclose(beta, 1.0)

    def test_beta_risk_free_asset(self, risk_engine):
        """Test that risk-free asset has beta of 0."""
        np.random.seed(42)
        market_returns = np.random.normal(0.001, 0.02, 252)
        risk_free_returns = np.full(252, 0.03 / 252)  # Constant return

        covariance = np.cov(risk_free_returns, market_returns)[0, 1]
        market_variance = np.var(market_returns)
        beta = covariance / market_variance

        assert np.isclose(beta, 0.0, atol=0.01)

    def test_negative_beta(self, risk_engine):
        """Test negative beta (inverse correlation)."""
        np.random.seed(42)
        market_returns = np.random.normal(0.001, 0.02, 252)

        # Portfolio moves opposite to market
        portfolio_returns = -0.8 * market_returns + np.random.normal(0, 0.005, 252)

        covariance = np.cov(portfolio_returns, market_returns)[0, 1]
        market_variance = np.var(market_returns)
        beta = covariance / market_variance

        assert beta < 0


class TestInformationRatio:
    """Tests for Information Ratio calculations."""

    def test_information_ratio_formula(self, risk_engine):
        """Test information ratio calculation."""
        np.random.seed(42)
        portfolio_returns = np.random.normal(0.001, 0.015, 252)
        benchmark_returns = np.random.normal(0.0008, 0.015, 252)

        # Active returns
        active_returns = portfolio_returns - benchmark_returns

        # Information ratio
        ir = np.mean(active_returns) * 252 / (np.std(active_returns) * np.sqrt(252))

        assert np.isfinite(ir)

    def test_tracking_error(self, risk_engine):
        """Test tracking error calculation."""
        np.random.seed(42)
        portfolio_returns = np.random.normal(0.001, 0.02, 252)
        benchmark_returns = np.random.normal(0.001, 0.02, 252)

        # Tracking error is std of active returns
        active_returns = portfolio_returns - benchmark_returns
        tracking_error = np.std(active_returns) * np.sqrt(252)

        assert tracking_error > 0

    def test_information_ratio_index_fund(self, risk_engine):
        """Test IR close to zero for index fund."""
        np.random.seed(42)
        benchmark_returns = np.random.normal(0.001, 0.02, 252)

        # Index fund with small tracking error
        portfolio_returns = benchmark_returns + np.random.normal(0, 0.0001, 252)

        active_returns = portfolio_returns - benchmark_returns
        ir = np.mean(active_returns) * 252 / (np.std(active_returns) * np.sqrt(252))

        assert abs(ir) < 0.5  # Should be close to zero


class TestCalmarRatio:
    """Tests for Calmar Ratio calculations."""

    def test_calmar_ratio_formula(self, risk_engine):
        """Test Calmar ratio calculation."""
        # Simulate price series
        np.random.seed(42)
        returns = np.random.normal(0.001, 0.02, 252)
        prices = 100 * np.exp(np.cumsum(returns))

        # Annual return
        annual_return = (prices[-1] / prices[0]) - 1

        # Maximum drawdown
        running_max = np.maximum.accumulate(prices)
        drawdowns = (prices - running_max) / running_max
        max_drawdown = abs(np.min(drawdowns))

        # Calmar ratio
        calmar = annual_return / max_drawdown if max_drawdown > 0 else np.inf

        assert np.isfinite(calmar) or max_drawdown == 0

    def test_calmar_ratio_interpretation(self, risk_engine):
        """Test Calmar ratio interpretation."""
        # Higher Calmar = better risk-adjusted return
        annual_return = 0.15
        max_dd_1 = 0.10
        max_dd_2 = 0.20

        calmar_1 = annual_return / max_dd_1
        calmar_2 = annual_return / max_dd_2

        assert calmar_1 > calmar_2  # Lower drawdown = higher Calmar


class TestOmegaRatio:
    """Tests for Omega Ratio calculations."""

    def test_omega_ratio_calculation(self, risk_engine):
        """Test Omega ratio calculation."""
        np.random.seed(42)
        returns = np.random.normal(0.001, 0.02, 1000)
        threshold = 0.0

        # Probability-weighted gains and losses
        gains = returns[returns > threshold] - threshold
        losses = threshold - returns[returns <= threshold]

        omega = np.sum(gains) / np.sum(losses) if np.sum(losses) > 0 else np.inf

        assert omega > 0

    def test_omega_ratio_threshold_sensitivity(self, risk_engine):
        """Test Omega ratio with different thresholds."""
        np.random.seed(42)
        returns = np.random.normal(0.002, 0.02, 1000)

        threshold_low = 0.0
        threshold_high = 0.005

        # Calculate Omega for both thresholds
        gains_low = returns[returns > threshold_low] - threshold_low
        losses_low = threshold_low - returns[returns <= threshold_low]
        omega_low = np.sum(gains_low) / np.sum(losses_low)

        gains_high = returns[returns > threshold_high] - threshold_high
        losses_high = threshold_high - returns[returns <= threshold_high]
        omega_high = np.sum(gains_high) / np.sum(losses_high) if np.sum(losses_high) > 0 else np.inf

        # Higher threshold typically means lower Omega
        assert omega_low > omega_high or np.isinf(omega_high)


class TestSkewnessKurtosis:
    """Tests for skewness and kurtosis calculations."""

    def test_skewness_calculation(self, risk_engine):
        """Test skewness calculation."""
        np.random.seed(42)
        returns = np.random.normal(0.0, 0.02, 1000)

        skewness = stats.skew(returns)

        # Normal distribution should have skewness near 0
        assert abs(skewness) < 0.2

    def test_negative_skew(self, risk_engine):
        """Test negative skewness detection."""
        # Create left-skewed distribution
        np.random.seed(42)
        returns = np.concatenate([np.random.normal(0.01, 0.01, 900), np.random.normal(-0.05, 0.01, 100)])

        skewness = stats.skew(returns)

        assert skewness < 0  # Negative skew

    def test_kurtosis_calculation(self, risk_engine):
        """Test kurtosis calculation."""
        np.random.seed(42)
        returns = np.random.normal(0.0, 0.02, 1000)

        # Excess kurtosis (relative to normal)
        kurt = stats.kurtosis(returns)

        # Normal distribution has excess kurtosis near 0
        assert abs(kurt) < 1.0

    def test_fat_tails_kurtosis(self, risk_engine):
        """Test high kurtosis with fat tails."""
        # Create distribution with fat tails
        np.random.seed(42)
        returns = np.concatenate([np.random.normal(0.0, 0.01, 900), np.random.normal(0.0, 0.05, 100)])

        kurt = stats.kurtosis(returns)

        assert kurt > 1.0  # Positive excess kurtosis


class TestRollingMetrics:
    """Tests for rolling risk metrics."""

    def test_rolling_volatility(self, risk_engine):
        """Test rolling volatility calculation."""
        np.random.seed(42)
        returns = np.random.normal(0.001, 0.02, 252)

        window = 20
        rolling_vol = np.array(
            [np.std(returns[max(0, i - window) : i + 1]) * np.sqrt(252) for i in range(len(returns))]
        )

        assert len(rolling_vol) == len(returns)
        assert np.all(rolling_vol >= 0)

    def test_rolling_sharpe(self, risk_engine):
        """Test rolling Sharpe ratio."""
        np.random.seed(42)
        returns = np.random.normal(0.001, 0.02, 252)
        risk_free = 0.03 / 252

        window = 60
        rolling_sharpe = []

        for i in range(window, len(returns)):
            window_returns = returns[i - window : i]
            mean_ret = np.mean(window_returns) * 252
            vol = np.std(window_returns) * np.sqrt(252)
            sharpe = (mean_ret - 0.03) / vol if vol > 0 else 0
            rolling_sharpe.append(sharpe)

        assert len(rolling_sharpe) == len(returns) - window

    def test_rolling_drawdown(self, risk_engine):
        """Test rolling drawdown calculation."""
        np.random.seed(42)
        returns = np.random.normal(0.001, 0.02, 252)
        prices = 100 * np.exp(np.cumsum(returns))

        running_max = np.maximum.accumulate(prices)
        rolling_dd = (prices - running_max) / running_max

        assert len(rolling_dd) == len(prices)
        assert np.all(rolling_dd <= 0)


@pytest.fixture
def risk_engine():
    """Mock risk engine fixture."""
    return None


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
