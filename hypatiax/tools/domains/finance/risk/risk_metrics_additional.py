#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Additional Risk Metrics Methods
Add these methods to the RiskMetrics class in risk_metrics.py

These are the 20+ additional risk formulas referenced in test_risk_formulas_30.py
Each method follows the pattern used in the original RiskMetrics class.
"""

import math

import numpy as np
from scipy import stats

# Add these methods to the RiskMetrics class
# Insert after the existing risk_limits_check method and before demo_risk_metrics()

    # ========================================================================
    # Additional Risk Metrics (Static Methods for Test Compatibility)
    # ========================================================================

    @staticmethod
    def var_parametric(returns: np.ndarray, confidence: float = 0.95) -> dict:
        """
        Parametric VaR using normal distribution

        Args:
            returns: Return series
            confidence: Confidence level (default 0.95)

        Returns:
            Dict with VaR metrics
        """
        returns = np.asarray(returns)
        if len(returns) == 0:
            return {"var": 0.0}

        mu = float(np.mean(returns))
        sigma = float(np.std(returns, ddof=1))
        z = stats.norm.ppf(1 - confidence)
        var = mu + z * sigma

        return {
            "var": var,
            "var_pct": var * 100,
            "confidence": confidence,
            "method": "parametric"
        }

    @staticmethod
    def cvar_historical(returns: np.ndarray, confidence: float = 0.95) -> dict:
        """
        Historical CVaR (Expected Shortfall)

        Args:
            returns: Return series
            confidence: Confidence level

        Returns:
            Dict with CVaR metrics
        """
        returns = np.asarray(returns)
        if len(returns) == 0:
            return {"cvar": 0.0}

        var = float(np.percentile(returns, (1 - confidence) * 100))
        tail = returns[returns <= var]

        if len(tail) == 0:
            cvar = var
        else:
            cvar = float(np.mean(tail))

        return {
            "cvar": cvar,
            "cvar_pct": cvar * 100,
            "var": var,
            "confidence": confidence,
            "tail_observations": len(tail)
        }

    @staticmethod
    def beta(returns: np.ndarray, benchmark_returns: np.ndarray) -> dict:
        """
        Calculate beta (systematic risk)

        Args:
            returns: Asset returns
            benchmark_returns: Benchmark returns

        Returns:
            Dict with beta and related metrics
        """
        returns = np.asarray(returns)
        benchmark_returns = np.asarray(benchmark_returns)

        if len(returns) != len(benchmark_returns):
            raise ValueError("Returns and benchmark must have same length")

        if len(returns) == 0:
            return {"beta": 0.0}

        # Calculate covariance and variance
        covar = float(np.cov(returns, benchmark_returns)[0, 1])
        bench_var = float(np.var(benchmark_returns, ddof=1))

        if bench_var < EPSILON:
            beta = 0.0
        else:
            beta = covar / bench_var

        # Calculate correlation
        corr = float(np.corrcoef(returns, benchmark_returns)[0, 1])

        return {
            "beta": beta,
            "correlation": corr,
            "covariance": covar,
            "benchmark_variance": bench_var
        }

    @staticmethod
    def treynor_ratio(returns: np.ndarray, benchmark_returns: np.ndarray,
                     risk_free_rate: float = 0.01) -> dict:
        """
        Calculate Treynor ratio (excess return per unit of systematic risk)

        Args:
            returns: Asset returns
            benchmark_returns: Benchmark returns
            risk_free_rate: Annual risk-free rate

        Returns:
            Dict with Treynor ratio
        """
        returns = np.asarray(returns)

        if len(returns) == 0:
            return {"treynor": 0.0}

        rf_period = risk_free_rate / DAYS_PER_YEAR
        excess_return = float(np.mean(returns - rf_period))

        beta_result = RiskMetrics.beta(returns, benchmark_returns)
        beta_val = beta_result["beta"]

        if abs(beta_val) < EPSILON:
            treynor = 0.0
        else:
            treynor = excess_return / beta_val
            treynor *= math.sqrt(DAYS_PER_YEAR)  # Annualize

        return {
            "treynor": treynor,
            "excess_return": excess_return,
            "beta": beta_val
        }

    @staticmethod
    def information_ratio(returns: np.ndarray, benchmark_returns: np.ndarray) -> dict:
        """
        Calculate Information Ratio (active return / tracking error)

        Args:
            returns: Asset returns
            benchmark_returns: Benchmark returns

        Returns:
            Dict with information ratio
        """
        returns = np.asarray(returns)
        benchmark_returns = np.asarray(benchmark_returns)

        if len(returns) == 0:
            return {"information_ratio": 0.0}

        active_returns = returns - benchmark_returns
        active_return = float(np.mean(active_returns))
        tracking_error = float(np.std(active_returns, ddof=1))

        if tracking_error < EPSILON:
            ir = 0.0
        else:
            ir = active_return / tracking_error
            ir *= math.sqrt(DAYS_PER_YEAR)  # Annualize

        return {
            "information_ratio": ir,
            "active_return": active_return,
            "tracking_error": tracking_error,
            "tracking_error_annualized": tracking_error * math.sqrt(DAYS_PER_YEAR)
        }

    @staticmethod
    def var_parametric_99(returns: np.ndarray) -> dict:
        """
        Parametric VaR at 99% confidence level

        Args:
            returns: Return series

        Returns:
            Dict with 99% VaR
        """
        return RiskMetrics.var_parametric(returns, confidence=0.99)

    @staticmethod
    def modified_sharpe(returns: np.ndarray, risk_free_rate: float = 0.01) -> dict:
        """
        Modified Sharpe ratio using Cornish-Fisher VaR
        Accounts for skewness and kurtosis

        Args:
            returns: Return series
            risk_free_rate: Annual risk-free rate

        Returns:
            Dict with modified Sharpe ratio
        """
        returns = np.asarray(returns)

        if len(returns) == 0:
            return {"modified_sharpe": 0.0}

        rf_period = risk_free_rate / DAYS_PER_YEAR
        excess = returns - rf_period
        mean_excess = float(np.mean(excess))

        # Calculate moments
        skew = float(stats.skew(returns))
        kurt = float(stats.kurtosis(returns, fisher=True))

        # Cornish-Fisher adjustment
        z = stats.norm.ppf(0.95)
        z_cf = (z + (1/6) * (z**2 - 1) * skew +
               (1/24) * (z**3 - 3*z) * kurt -
               (1/36) * (2*z**3 - 5*z) * skew**2)

        sigma = float(np.std(returns, ddof=1))
        modified_var = z_cf * sigma

        if abs(modified_var) < EPSILON:
            modified_sharpe = 0.0
        else:
            modified_sharpe = mean_excess / abs(modified_var)
            modified_sharpe *= math.sqrt(DAYS_PER_YEAR)

        return {
            "modified_sharpe": modified_sharpe,
            "skew": skew,
            "kurtosis": kurt,
            "modified_var": modified_var
        }

    @staticmethod
    def ulcer_index(returns: np.ndarray) -> dict:
        """
        Calculate Ulcer Index (measure of downside volatility)

        Args:
            returns: Return series

        Returns:
            Dict with Ulcer Index
        """
        returns = np.asarray(returns)

        if len(returns) == 0:
            return {"ulcer_index": 0.0}

        # Calculate drawdowns
        wealth = np.cumprod(1.0 + returns)
        running_max = np.maximum.accumulate(wealth)
        drawdown = (running_max - wealth) / (running_max + EPSILON)

        # Ulcer Index is RMS of drawdowns
        ulcer = float(np.sqrt(np.mean(drawdown ** 2)))

        return {
            "ulcer_index": ulcer,
            "ulcer_index_pct": ulcer * 100
        }

    @staticmethod
    def martin_ratio(returns: np.ndarray, risk_free_rate: float = 0.01) -> dict:
        """
        Calculate Martin Ratio (return / Ulcer Index)

        Args:
            returns: Return series
            risk_free_rate: Annual risk-free rate

        Returns:
            Dict with Martin ratio
        """
        returns = np.asarray(returns)

        if len(returns) == 0:
            return {"martin": 0.0}

        rf_period = risk_free_rate / DAYS_PER_YEAR
        excess_return = float(np.mean(returns - rf_period)) * DAYS_PER_YEAR

        ulcer = RiskMetrics.ulcer_index(returns)["ulcer_index"]

        if ulcer < EPSILON:
            martin = 0.0
        else:
            martin = excess_return / ulcer

        return {
            "martin": martin,
            "excess_return": excess_return,
            "ulcer_index": ulcer
        }

    @staticmethod
    def drawdown_duration(returns: np.ndarray) -> dict:
        """
        Calculate average drawdown duration

        Args:
            returns: Return series

        Returns:
            Dict with drawdown duration metrics
        """
        returns = np.asarray(returns)

        if len(returns) == 0:
            return {"avg_drawdown_duration": 0.0}

        wealth = np.cumprod(1.0 + returns)
        running_max = np.maximum.accumulate(wealth)
        drawdown = (running_max - wealth) / (running_max + EPSILON)

        # Find drawdown periods
        in_drawdown = drawdown > 0.001
        durations = []

        i = 0
        while i < len(in_drawdown):
            if in_drawdown[i]:
                start = i
                while i < len(in_drawdown) and in_drawdown[i]:
                    i += 1
                durations.append(i - start)
            else:
                i += 1

        avg_duration = float(np.mean(durations)) if durations else 0.0
        max_duration = float(np.max(durations)) if durations else 0.0

        return {
            "avg_drawdown_duration": avg_duration,
            "max_drawdown_duration": max_duration,
            "num_drawdown_periods": len(durations)
        }

    @staticmethod
    def kappa_3(returns: np.ndarray, risk_free_rate: float = 0.01,
                mar: float = 0.0) -> dict:
        """
        Calculate Kappa 3 ratio (generalized Sortino with cubic moment)

        Args:
            returns: Return series
            risk_free_rate: Annual risk-free rate
            mar: Minimum acceptable return

        Returns:
            Dict with Kappa 3
        """
        returns = np.asarray(returns)

        if len(returns) == 0:
            return {"kappa3": 0.0}

        rf_period = risk_free_rate / DAYS_PER_YEAR
        excess = returns - rf_period
        mean_excess = float(np.mean(excess))

        # Lower partial moment of order 3
        downside = returns[returns < mar] - mar
        if len(downside) == 0:
            lpm3 = float(np.std(returns, ddof=1)) ** 3
        else:
            lpm3 = float(np.mean(downside ** 3))

        if abs(lpm3) < EPSILON:
            kappa3 = 0.0
        else:
            kappa3 = mean_excess / abs(lpm3) ** (1/3)
            kappa3 *= math.sqrt(DAYS_PER_YEAR)

        return {
            "kappa3": kappa3,
            "mean_excess": mean_excess,
            "lpm3": lpm3
        }

    @staticmethod
    def gain_loss_ratio(returns: np.ndarray) -> dict:
        """
        Calculate gain-to-loss ratio

        Args:
            returns: Return series

        Returns:
            Dict with gain/loss ratio
        """
        returns = np.asarray(returns)

        if len(returns) == 0:
            return {"gain_loss": 0.0}

        gains = returns[returns > 0]
        losses = returns[returns < 0]

        avg_win = float(np.mean(gains)) if len(gains) > 0 else 0.0
        avg_loss = float(np.mean(losses)) if len(losses) > 0 else 0.0

        if abs(avg_loss) < EPSILON:
            gain_loss = 0.0 if avg_win == 0 else float('inf')
        else:
            gain_loss = avg_win / abs(avg_loss)

        return {
            "gain_loss": gain_loss if math.isfinite(gain_loss) else 0.0,
            "avg_win": avg_win,
            "avg_loss": avg_loss,
            "num_wins": len(gains),
            "num_losses": len(losses)
        }

    @staticmethod
    def upside_potential_ratio(returns: np.ndarray, mar: float = 0.0) -> dict:
        """
        Calculate Upside Potential Ratio

        Args:
            returns: Return series
            mar: Minimum acceptable return

        Returns:
            Dict with UPR
        """
        returns = np.asarray(returns)

        if len(returns) == 0:
            return {"upr": 0.0}

        upside = returns[returns > mar] - mar
        downside = returns[returns < mar] - mar

        upside_potential = float(np.mean(upside)) if len(upside) > 0 else 0.0

        if len(downside) == 0:
            downside_risk = float(np.std(returns, ddof=1))
        else:
            downside_risk = float(np.sqrt(np.mean(downside ** 2)))

        if downside_risk < EPSILON:
            upr = 0.0
        else:
            upr = upside_potential / downside_risk

        return {
            "upr": upr,
            "upside_potential": upside_potential,
            "downside_risk": downside_risk
        }

    @staticmethod
    def sterling_ratio(returns: np.ndarray, risk_free_rate: float = 0.01) -> dict:
        """
        Calculate Sterling Ratio (return / average drawdown)

        Args:
            returns: Return series
            risk_free_rate: Annual risk-free rate

        Returns:
            Dict with Sterling ratio
        """
        returns = np.asarray(returns)

        if len(returns) == 0:
            return {"sterling": 0.0}

        rf_period = risk_free_rate / DAYS_PER_YEAR
        excess_return = float(np.mean(returns - rf_period)) * DAYS_PER_YEAR

        # Calculate average drawdown
        wealth = np.cumprod(1.0 + returns)
        running_max = np.maximum.accumulate(wealth)
        drawdown = (running_max - wealth) / (running_max + EPSILON)
        avg_dd = float(np.mean(drawdown[drawdown > 0.001])) if np.any(drawdown > 0.001) else 0.01

        if avg_dd < EPSILON:
            sterling = 0.0
        else:
            sterling = excess_return / avg_dd

        return {
            "sterling": sterling,
            "excess_return": excess_return,
            "avg_drawdown": avg_dd
        }

    @staticmethod
    def pain_ratio(returns: np.ndarray, risk_free_rate: float = 0.01) -> dict:
        """
        Calculate Pain Ratio (return / pain index)
        Pain index is the average drawdown over all periods

        Args:
            returns: Return series
            risk_free_rate: Annual risk-free rate

        Returns:
            Dict with Pain ratio
        """
        returns = np.asarray(returns)

        if len(returns) == 0:
            return {"pain_ratio": 0.0}

        rf_period = risk_free_rate / DAYS_PER_YEAR
        excess_return = float(np.mean(returns - rf_period)) * DAYS_PER_YEAR

        # Pain index = average of all drawdowns
        wealth = np.cumprod(1.0 + returns)
        running_max = np.maximum.accumulate(wealth)
        drawdown = (running_max - wealth) / (running_max + EPSILON)
        pain_index = float(np.mean(drawdown))

        if pain_index < EPSILON:
            pain_ratio = 0.0
        else:
            pain_ratio = excess_return / pain_index

        return {
            "pain_ratio": pain_ratio,
            "pain_index": pain_index,
            "excess_return": excess_return
        }

    @staticmethod
    def cdar(returns: np.ndarray, confidence: float = 0.95) -> dict:
        """
        Calculate Conditional Drawdown at Risk (CDaR)

        Args:
            returns: Return series
            confidence: Confidence level

        Returns:
            Dict with CDaR
        """
        returns = np.asarray(returns)

        if len(returns) == 0:
            return {"cdar": 0.0, "dar": 0.0}

        # Calculate all drawdowns
        wealth = np.cumprod(1.0 + returns)
        running_max = np.maximum.accumulate(wealth)
        drawdowns = (running_max - wealth) / (running_max + EPSILON)

        # DaR (Drawdown at Risk)
        dar = float(np.percentile(drawdowns, confidence * 100))

        # CDaR (average of drawdowns beyond DaR)
        tail = drawdowns[drawdowns >= dar]
        cdar = float(np.mean(tail)) if len(tail) > 0 else dar

        return {
            "cdar": cdar,
            "dar": dar,
            "confidence": confidence,
            "cdar_pct": cdar * 100,
            "dar_pct": dar * 100
        }

    @staticmethod
    def tail_ratio(returns: np.ndarray, percentile: float = 95.0) -> dict:
        """
        Calculate tail ratio (right tail / left tail)

        Args:
            returns: Return series
            percentile: Percentile for tails (default 95)

        Returns:
            Dict with tail ratio
        """
        returns = np.asarray(returns)

        if len(returns) == 0:
            return {"tail_ratio": 0.0}

        right_tail = float(np.percentile(returns, percentile))
        left_tail = float(np.percentile(returns, 100 - percentile))

        if abs(left_tail) < EPSILON:
            tail_ratio = 0.0
        else:
            tail_ratio = abs(right_tail / left_tail)

        return {
            "tail_ratio": tail_ratio,
            "right_tail": right_tail,
            "left_tail": left_tail,
            "percentile": percentile
        }

    @staticmethod
    def m_squared(returns: np.ndarray, risk_free_rate: float = 0.01,
                  benchmark_vol: float = 10.0) -> dict:
        """
        Calculate M-squared (Modigliani-Modigliani measure)

        Args:
            returns: Return series
            risk_free_rate: Annual risk-free rate
            benchmark_vol: Benchmark volatility (annualized %)

        Returns:
            Dict with M-squared
        """
        returns = np.asarray(returns)

        if len(returns) == 0:
            return {"m2": 0.0, "m2_pct": 0.0}

        rf_period = risk_free_rate / DAYS_PER_YEAR

        # Calculate Sharpe ratio
        excess = returns - rf_period
        mean_excess = float(np.mean(excess))
        sigma = float(np.std(returns, ddof=1))

        if sigma < EPSILON:
            sharpe = 0.0
        else:
            sharpe = mean_excess / sigma * math.sqrt(DAYS_PER_YEAR)

        # M2 = Rf + Sharpe * benchmark_vol
        benchmark_vol_decimal = benchmark_vol / 100
        m2 = risk_free_rate + sharpe * benchmark_vol_decimal

        return {
            "m2": m2,
            "m2_pct": m2 * 100,
            "sharpe": sharpe,
            "benchmark_vol": benchmark_vol
        }

    @staticmethod
    def prospect_ratio(returns: np.ndarray, mar: float = 0.0,
                      lambda_param: float = 2.25) -> dict:
        """
        Calculate Prospect Ratio (behavioral finance measure)

        Args:
            returns: Return series
            mar: Minimum acceptable return
            lambda_param: Loss aversion parameter (default 2.25)

        Returns:
            Dict with Prospect ratio
        """
        returns = np.asarray(returns)

        if len(returns) == 0:
            return {"prospect": 0.0}

        gains = returns[returns > mar] - mar
        losses = returns[returns < mar] - mar

        gain_value = float(np.sum(gains)) if len(gains) > 0 else 0.0
        loss_value = float(np.sum(losses)) if len(losses) > 0 else 0.0

        # Prospect theory value
        prospect_value = gain_value - lambda_param * abs(loss_value)

        # Normalize by number of periods
        prospect_ratio = prospect_value / len(returns) if len(returns) > 0 else 0.0

        return {
            "prospect": prospect_ratio,
            "gain_value": gain_value,
            "loss_value": loss_value,
            "lambda": lambda_param
        }

    @staticmethod
    def rachev_ratio(returns: np.ndarray, alpha: float = 0.95,
                    beta: float = 0.95) -> dict:
        """
        Calculate Rachev ratio (Expected tail gain / Expected tail loss)

        Args:
            returns: Return series
            alpha: Upper tail percentile
            beta: Lower tail percentile

        Returns:
            Dict with Rachev ratio
        """
        returns = np.asarray(returns)

        if len(returns) == 0:
            return {"rachev": 0.0}

        # Upper tail (gains)
        upper_threshold = float(np.percentile(returns, alpha * 100))
        upper_tail = returns[returns >= upper_threshold]
        expected_gain = float(np.mean(upper_tail)) if len(upper_tail) > 0 else 0.0

        # Lower tail (losses)
        lower_threshold = float(np.percentile(returns, (1 - beta) * 100))
        lower_tail = returns[returns <= lower_threshold]
        expected_loss = float(np.mean(lower_tail)) if len(lower_tail) > 0 else 0.0

        if abs(expected_loss) < EPSILON:
            rachev = 0.0
        else:
            rachev = expected_gain / abs(expected_loss)

        return {
            "rachev": rachev,
            "expected_gain": expected_gain,
            "expected_loss": expected_loss,
            "alpha": alpha,
            "beta": beta
        }

    @staticmethod
    def d_ratio(returns: np.ndarray) -> dict:
        """
        Calculate D-Ratio (downside to upside capture)

        Args:
            returns: Return series

        Returns:
            Dict with D-ratio
        """
        returns = np.asarray(returns)

        if len(returns) == 0:
            return {"d_ratio": 0.0}

        positive = returns[returns > 0]
        negative = returns[returns < 0]

        sum_positive = float(np.sum(positive)) if len(positive) > 0 else EPSILON
        sum_negative = float(np.sum(np.abs(negative))) if len(negative) > 0 else EPSILON

        d_ratio = sum_negative / sum_positive if sum_positive > 0 else 0.0

        return {
            "d_ratio": d_ratio,
            "sum_gains": sum_positive,
            "sum_losses": sum_negative
        }

    @staticmethod
    def romad(returns: np.ndarray, risk_free_rate: float = 0.01) -> dict:
        """
        Calculate RoMaD (Return over Maximum Drawdown)

        Args:
            returns: Return series
            risk_free_rate: Annual risk-free rate

        Returns:
            Dict with RoMaD
        """
        returns = np.asarray(returns)

        if len(returns) == 0:
            return {"romad": 0.0}

        rf_period = risk_free_rate / DAYS_PER_YEAR
        excess_return = float(np.mean(returns - rf_period)) * DAYS_PER_YEAR

        # Max drawdown
        wealth = np.cumprod(1.0 + returns)
        running_max = np.maximum.accumulate(wealth)
        drawdown = (running_max - wealth) / (running_max + EPSILON)
        max_dd = float(np.max(drawdown))

        if max_dd < EPSILON:
            romad = 0.0
        else:
            romad = excess_return / max_dd

        return {
            "romad": romad,
            "excess_return": excess_return,
            "max_drawdown": max_dd
        }

    @staticmethod
    def serenity_ratio(returns: np.ndarray, risk_free_rate: float = 0.01) -> dict:
        """
        Calculate Serenity Ratio (modified Sortino with Ulcer Index)

        Args:
            returns: Return series
            risk_free_rate: Annual risk-free rate

        Returns:
            Dict with Serenity ratio
        """
        returns = np.asarray(returns)

        if len(returns) == 0:
            return {"serenity": 0.0}

        rf_period = risk_free_rate / DAYS_PER_YEAR
        excess_return = float(np.mean(returns - rf_period)) * DAYS_PER_YEAR

        ulcer = RiskMetrics.ulcer_index(returns)["ulcer_index"]

        if ulcer < EPSILON:
            serenity = 0.0
        else:
            serenity = excess_return / ulcer

        return {
            "serenity": serenity,
            "excess_return": excess_return,
            "ulcer_index": ulcer
        }

    @staticmethod
    def stability_index(returns: np.ndarray, window: int = 20) -> dict:
        """
        Calculate stability index (consistency of returns)

        Args:
            returns: Return series
            window: Rolling window size

        Returns:
            Dict with stability metrics
        """
        returns = np.asarray(returns)

        if len(returns) < window:
            return {"stability": 0.0}

        # Calculate rolling volatility
        rolling_vols = []
        for i in range(window, len(returns) + 1):
            window_returns = returns[i-window:i]
            vol = float(np.std(window_returns, ddof=1))
            rolling_vols.append(vol)

        rolling_vols = np.array(rolling_vols)

        # Stability = inverse of volatility of volatility
        vol_of_vol = float(np.std(rolling_vols, ddof=1))
        mean_vol = float(np.mean(rolling_vols))

        if mean_vol < EPSILON:
            stability = 0.0
        else:
            stability = 1.0 - (vol_of_vol / mean_vol)

        return {
            "stability": max(0.0, stability),
            "vol_of_vol": vol_of_vol,
            "mean_vol": mean_vol
        }

    @staticmethod
    def recovery_factor(returns: np.ndarray, initial_capital: float = 100000.0) -> dict:
        """
        Calculate recovery factor (total return / max drawdown)

        Args:
            returns: Return series
            initial_capital: Starting capital

        Returns:
            Dict with recovery factor
        """
        returns = np.asarray(returns)

        if len(returns) == 0:
            return {"recovery_factor": 0.0}

        # Total return
        final_value = initial_capital * np.prod(1.0 + returns)
        total_return = (final_value - initial_capital) / initial_capital

        # Max drawdown
        wealth = np.cumprod(1.0 + returns)
        running_max = np.maximum.accumulate(wealth)
        drawdown = (running_max - wealth) / (running_max + EPSILON)
        max_dd = float(np.max(drawdown))

        if max_dd < EPSILON:
            recovery_factor = 0.0 if total_return <= 0 else float('inf')
        else:
            recovery_factor = total_return / max_dd

        return {
            "recovery_factor": recovery_factor if math.isfinite(recovery_factor) else 0.0,
            "total_return": total_return,
            "total_return_pct": total_return * 100,
            "max_drawdown": max_dd,
            "final_value": float(final_value)
        }


# ========================================================================
# Constants needed for the methods above
# ========================================================================

EPSILON = 1e-10
DAYS_PER_YEAR = 252


# ========================================================================
# USAGE INSTRUCTIONS
# ========================================================================
"""
To add these methods to your RiskMetrics class:

1. Copy all the method definitions above (from @staticmethod var_parametric
   through recovery_factor)

2. In your risk_metrics.py file, locate the RiskMetrics class

3. Paste these methods inside the class, before the demo_risk_metrics() function

4. Make sure the constants EPSILON and DAYS_PER_YEAR are defined at the module
   level (outside any class) if they aren't already

5. The methods will then be available as:
   - RiskMetrics.var_parametric(returns, confidence=0.95)
   - RiskMetrics.cvar_historical(returns, confidence=0.95)
   - RiskMetrics.beta(returns, benchmark_returns)
   - RiskMetrics.treynor_ratio(returns, benchmark_returns, risk_free_rate=0.01)
   - RiskMetrics.information_ratio(returns, benchmark_returns)
   - ... and all the other 20+ methods

Example usage:
    import numpy as np
    from risk_metrics import RiskMetrics

    returns = np.random.normal(0.001, 0.02, 252)
    benchmark_returns = np.random.normal(0.0008, 0.015, 252)

    # Parametric VaR at 95% confidence
    var_result = RiskMetrics.var_parametric(returns, confidence=0.95)
    print(f"VaR (95%): {var_result['var_pct']:.2f}%")

    # Beta against benchmark
    beta_result = RiskMetrics.beta(returns, benchmark_returns)
    print(f"Beta: {beta_result['beta']:.3f}")

    # Treynor ratio
    treynor_result = RiskMetrics.treynor_ratio(returns, benchmark_returns)
    print(f"Treynor Ratio: {treynor_result['treynor']:.3f}")

    # Information ratio
    ir_result = RiskMetrics.information_ratio(returns, benchmark_returns)
    print(f"Information Ratio: {ir_result['information_ratio']:.3f}")

    # Modified Sharpe (accounts for skewness/kurtosis)
    mod_sharpe = RiskMetrics.modified_sharpe(returns)
    print(f"Modified Sharpe: {mod_sharpe['modified_sharpe']:.3f}")

    # Ulcer Index and Martin Ratio
    ulcer = RiskMetrics.ulcer_index(returns)
    martin = RiskMetrics.martin_ratio(returns)
    print(f"Ulcer Index: {ulcer['ulcer_index_pct']:.2f}%")
    print(f"Martin Ratio: {martin['martin']:.3f}")

    # Tail analysis
    tail = RiskMetrics.tail_ratio(returns)
    print(f"Tail Ratio: {tail['tail_ratio']:.3f}")

    # Conditional Drawdown at Risk
    cdar = RiskMetrics.cdar(returns, confidence=0.95)
    print(f"CDaR (95%): {cdar['cdar_pct']:.2f}%")

    # Recovery factor
    recovery = RiskMetrics.recovery_factor(returns)
    print(f"Recovery Factor: {recovery['recovery_factor']:.3f}")

Note: All these methods are static, so they don't require creating a
RiskMetrics instance. They can be called directly on the class.

These 20+ additional methods complement the existing RiskMetrics methods
and provide comprehensive risk analysis capabilities covering:
- Multiple VaR/CVaR variants
- Beta and systematic risk measures
- Advanced risk-adjusted ratios (Treynor, Information, Modified Sharpe)
- Downside risk metrics (Ulcer Index, Martin Ratio, Sortino variants)
- Drawdown analysis (CDaR, duration, recovery)
- Tail risk measures (tail ratio, Rachev ratio)
- Behavioral finance metrics (Prospect ratio)
- Performance consistency (stability index, gain/loss ratio)
"""
