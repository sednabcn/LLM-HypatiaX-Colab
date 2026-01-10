#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
risk_metrics.py

Enhanced RiskMetrics class providing:
 - Portfolio-level risk aggregation
 - Risk budgeting and attribution
 - Stress testing and scenario analysis
 - Real-time risk monitoring
 - Risk-adjusted performance metrics
 - Correlation and diversification analysis

Dependencies:
 - numpy
 - scipy
 - pandas (optional, for enhanced reporting)
"""

from __future__ import annotations

import math
from dataclasses import dataclass, field
from datetime import datetime
from enum import Enum
from typing import Any, Dict, List, Optional, Tuple

import numpy as np
from scipy import stats

EPSILON = 1e-12
DAYS_PER_YEAR = 252
MINUTES_PER_DAY = 390  # Trading minutes


class RiskLevel(Enum):
    """Risk level classification"""

    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    CRITICAL = "critical"


class TimeHorizon(Enum):
    """Time horizon for risk calculations"""

    INTRADAY = 1
    DAILY = 1
    WEEKLY = 5
    MONTHLY = 21
    QUARTERLY = 63
    YEARLY = 252


@dataclass
class Asset:
    """Individual asset with returns and metadata"""

    symbol: str
    returns: np.ndarray
    weight: float = 0.0
    market_value: float = 0.0
    beta: float = 1.0
    sector: str = "Unknown"

    def __post_init__(self):
        if isinstance(self.returns, list):
            self.returns = np.array(self.returns, dtype=float)


@dataclass
class RiskBudget:
    """Risk budget allocation"""

    asset: str
    allocated_risk: float  # Percentage of total risk
    actual_risk: float
    contribution: float
    utilization: float  # actual / allocated

    @property
    def is_over_budget(self) -> bool:
        return self.utilization > 1.0


@dataclass
class StressScenario:
    """Stress testing scenario"""

    name: str
    shock_type: str  # 'absolute', 'relative', 'correlation'
    parameters: Dict[str, float]
    description: str = ""


class RiskMetrics:
    """
    Comprehensive risk metrics calculator with portfolio-level analysis
    """

    def __init__(self, risk_free_rate: float = 0.03):
        """
        Initialize RiskMetrics calculator

        Args:
            risk_free_rate: Annual risk-free rate (decimal)
        """
        self.risk_free_rate = risk_free_rate
        self.assets: List[Asset] = []
        self.benchmark_returns: Optional[np.ndarray] = None

    # ========================================================================
    # Portfolio Construction & Management
    # ========================================================================

    def add_asset(self, asset: Asset) -> None:
        """Add asset to portfolio"""
        self.assets.append(asset)

    def set_benchmark(self, returns: np.ndarray) -> None:
        """Set benchmark returns for comparison"""
        self.benchmark_returns = np.array(returns, dtype=float)

    def get_portfolio_returns(self) -> np.ndarray:
        """Calculate weighted portfolio returns"""
        if not self.assets:
            return np.array([])

        # Normalize weights
        total_weight = sum(a.weight for a in self.assets)
        if total_weight == 0:
            return np.array([])

        # Calculate weighted returns
        min_length = min(len(a.returns) for a in self.assets)
        portfolio_returns = np.zeros(min_length)

        for asset in self.assets:
            normalized_weight = asset.weight / total_weight
            portfolio_returns += asset.returns[:min_length] * normalized_weight

        return portfolio_returns

    # ========================================================================
    # Core Risk Metrics
    # ========================================================================

    def volatility(
        self, returns: Optional[np.ndarray] = None, annualized: bool = True
    ) -> Dict[str, float]:
        """
        Calculate volatility (standard deviation)

        Args:
            returns: Return series (uses portfolio if None)
            annualized: Return annualized volatility

        Returns:
            Dict with volatility metrics
        """
        if returns is None:
            returns = self.get_portfolio_returns()

        if len(returns) == 0:
            return {"volatility": 0.0, "variance": 0.0}

        vol = float(np.std(returns, ddof=1))
        var = vol**2

        if annualized:
            vol *= math.sqrt(DAYS_PER_YEAR)
            var *= DAYS_PER_YEAR

        return {
            "volatility": vol,
            "volatility_pct": vol * 100,
            "variance": var,
            "annualized": annualized,
        }

    def downside_deviation(
        self, returns: Optional[np.ndarray] = None, mar: float = 0.0
    ) -> Dict[str, float]:
        """
        Calculate downside deviation (semi-deviation)

        Args:
            returns: Return series
            mar: Minimum acceptable return (MAR)

        Returns:
            Dict with downside metrics
        """
        if returns is None:
            returns = self.get_portfolio_returns()

        downside = returns[returns < mar] - mar

        if len(downside) == 0:
            downside_dev = 0.0
        else:
            downside_dev = float(np.sqrt(np.mean(downside**2)))

        return {
            "downside_deviation": downside_dev,
            "downside_deviation_pct": downside_dev * 100,
            "downside_periods": len(downside),
            "total_periods": len(returns),
            "downside_frequency": (
                len(downside) / len(returns) if len(returns) > 0 else 0
            ),
        }

    def value_at_risk(
        self,
        returns: Optional[np.ndarray] = None,
        confidence: float = 0.95,
        method: str = "historical",
    ) -> Dict[str, float]:
        """
        Calculate Value at Risk (VaR)

        Args:
            returns: Return series
            confidence: Confidence level (0.95 = 95%)
            method: 'historical', 'parametric', or 'cornish_fisher'

        Returns:
            Dict with VaR metrics
        """
        if returns is None:
            returns = self.get_portfolio_returns()

        if len(returns) == 0:
            return {"var": 0.0, "method": method}

        if method == "historical":
            var = float(np.percentile(returns, (1 - confidence) * 100))

        elif method == "parametric":
            mu = float(np.mean(returns))
            sigma = float(np.std(returns, ddof=1))
            z = stats.norm.ppf(1 - confidence)
            var = mu + z * sigma

        elif method == "cornish_fisher":
            mu = float(np.mean(returns))
            sigma = float(np.std(returns, ddof=1))
            skew = float(stats.skew(returns))
            kurt = float(stats.kurtosis(returns, fisher=True))

            z = stats.norm.ppf(1 - confidence)
            z_cf = (
                z
                + (1 / 6) * (z**2 - 1) * skew
                + (1 / 24) * (z**3 - 3 * z) * kurt
                - (1 / 36) * (2 * z**3 - 5 * z) * skew**2
            )
            var = mu + z_cf * sigma

        else:
            raise ValueError(f"Unknown VaR method: {method}")

        return {
            "var": var,
            "var_pct": var * 100,
            "confidence": confidence,
            "method": method,
        }

    def conditional_var(
        self, returns: Optional[np.ndarray] = None, confidence: float = 0.95
    ) -> Dict[str, float]:
        """
        Calculate Conditional Value at Risk (CVaR/Expected Shortfall)

        Args:
            returns: Return series
            confidence: Confidence level

        Returns:
            Dict with CVaR metrics
        """
        if returns is None:
            returns = self.get_portfolio_returns()

        if len(returns) == 0:
            return {"cvar": 0.0}

        var = self.value_at_risk(returns, confidence, "historical")["var"]
        tail = returns[returns <= var]

        if len(tail) == 0:
            cvar = var
        else:
            cvar = float(np.mean(tail))

        return {
            "cvar": cvar,
            "cvar_pct": cvar * 100,
            "var": var,
            "tail_observations": len(tail),
            "confidence": confidence,
        }

    # ========================================================================
    # Risk-Adjusted Performance
    # ========================================================================

    def sharpe_ratio(
        self, returns: Optional[np.ndarray] = None, annualized: bool = True
    ) -> Dict[str, float]:
        """Calculate Sharpe ratio"""
        if returns is None:
            returns = self.get_portfolio_returns()

        if len(returns) == 0:
            return {"sharpe": 0.0}

        rf_period = self.risk_free_rate / DAYS_PER_YEAR
        excess = returns - rf_period

        mean_excess = float(np.mean(excess))
        sigma = float(np.std(returns, ddof=1))

        if sigma < EPSILON:
            sharpe = 0.0
        else:
            sharpe = mean_excess / sigma
            if annualized:
                sharpe *= math.sqrt(DAYS_PER_YEAR)

        return {
            "sharpe": sharpe,
            "mean_excess_return": mean_excess,
            "volatility": sigma,
            "annualized": annualized,
        }

    def sortino_ratio(
        self,
        returns: Optional[np.ndarray] = None,
        mar: float = 0.0,
        annualized: bool = True,
    ) -> Dict[str, float]:
        """Calculate Sortino ratio"""
        if returns is None:
            returns = self.get_portfolio_returns()

        if len(returns) == 0:
            return {"sortino": 0.0}

        excess = returns - mar
        mean_excess = float(np.mean(excess))

        downside = returns[returns < mar] - mar
        if len(downside) == 0:
            downside_dev = float(np.std(returns, ddof=1))
        else:
            downside_dev = float(np.sqrt(np.mean(downside**2)))

        if downside_dev < EPSILON:
            sortino = 0.0
        else:
            sortino = mean_excess / downside_dev
            if annualized:
                sortino *= math.sqrt(DAYS_PER_YEAR)

        return {
            "sortino": sortino,
            "mean_excess_return": mean_excess,
            "downside_deviation": downside_dev,
            "mar": mar,
            "annualized": annualized,
        }

    def calmar_ratio(self, returns: Optional[np.ndarray] = None) -> Dict[str, float]:
        """Calculate Calmar ratio (return / max drawdown)"""
        if returns is None:
            returns = self.get_portfolio_returns()

        if len(returns) == 0:
            return {"calmar": 0.0}

        annual_return = float(np.mean(returns)) * DAYS_PER_YEAR
        max_dd = self._calculate_max_drawdown(returns)

        if max_dd < EPSILON:
            calmar = 0.0
        else:
            calmar = annual_return / max_dd

        return {
            "calmar": calmar,
            "annual_return": annual_return,
            "max_drawdown": max_dd,
        }

    # ========================================================================
    # Drawdown Analysis
    # ========================================================================

    def _calculate_max_drawdown(self, returns: np.ndarray) -> float:
        """Internal helper for max drawdown calculation"""
        wealth = np.cumprod(1.0 + returns)
        running_max = np.maximum.accumulate(wealth)
        drawdown = (running_max - wealth) / (running_max + EPSILON)
        return float(np.max(drawdown))

    def drawdown_analysis(self, returns: Optional[np.ndarray] = None) -> Dict[str, Any]:
        """
        Comprehensive drawdown analysis

        Returns:
            Dict with max drawdown, average drawdown, recovery time, etc.
        """
        if returns is None:
            returns = self.get_portfolio_returns()

        if len(returns) == 0:
            return {}

        wealth = np.cumprod(1.0 + returns)
        running_max = np.maximum.accumulate(wealth)
        drawdown = (running_max - wealth) / (running_max + EPSILON)

        # Find drawdown periods
        in_drawdown = drawdown > 0.001  # 0.1% threshold
        periods = []

        i = 0
        while i < len(in_drawdown):
            if in_drawdown[i]:
                start = i
                max_dd = drawdown[i]
                while i < len(in_drawdown) and in_drawdown[i]:
                    max_dd = max(max_dd, drawdown[i])
                    i += 1
                periods.append(
                    {
                        "start_idx": start,
                        "end_idx": i - 1,
                        "length": i - start,
                        "depth": max_dd,
                    }
                )
            else:
                i += 1

        if periods:
            max_dd_period = max(periods, key=lambda x: x["depth"])
            longest_period = max(periods, key=lambda x: x["length"])
            avg_depth = np.mean([p["depth"] for p in periods])
            avg_length = np.mean([p["length"] for p in periods])
        else:
            max_dd_period = {"depth": 0.0, "length": 0}
            longest_period = {"length": 0}
            avg_depth = 0.0
            avg_length = 0.0

        return {
            "max_drawdown": max_dd_period["depth"],
            "max_drawdown_pct": max_dd_period["depth"] * 100,
            "max_drawdown_length": max_dd_period["length"],
            "longest_drawdown_length": longest_period["length"],
            "num_drawdown_periods": len(periods),
            "avg_drawdown_depth": avg_depth,
            "avg_drawdown_length": avg_length,
            "current_drawdown": float(drawdown[-1]),
            "time_underwater_pct": np.sum(in_drawdown) / len(in_drawdown) * 100,
        }

    # ========================================================================
    # Correlation & Diversification
    # ========================================================================

    def correlation_matrix(self) -> Dict[str, Any]:
        """Calculate correlation matrix for all assets"""
        if len(self.assets) < 2:
            return {"correlation_matrix": np.array([]), "symbols": []}

        # Get minimum length
        min_len = min(len(a.returns) for a in self.assets)

        # Build returns matrix
        returns_matrix = np.column_stack([a.returns[:min_len] for a in self.assets])

        corr_matrix = np.corrcoef(returns_matrix.T)
        symbols = [a.symbol for a in self.assets]

        # Calculate average correlation
        n = len(symbols)
        if n > 1:
            avg_corr = (np.sum(corr_matrix) - n) / (n * (n - 1))
        else:
            avg_corr = 0.0

        return {
            "correlation_matrix": corr_matrix,
            "symbols": symbols,
            "average_correlation": float(avg_corr),
            "max_correlation": (
                float(np.max(corr_matrix[corr_matrix < 1.0])) if n > 1 else 0.0
            ),
            "min_correlation": (
                float(np.min(corr_matrix[corr_matrix < 1.0])) if n > 1 else 0.0
            ),
        }

    def diversification_ratio(self) -> Dict[str, float]:
        """
        Calculate portfolio diversification ratio
        DR = (weighted avg of volatilities) / (portfolio volatility)
        """
        if not self.assets:
            return {"diversification_ratio": 1.0}

        # Calculate individual volatilities
        total_weight = sum(a.weight for a in self.assets)
        if total_weight < EPSILON:
            return {"diversification_ratio": 1.0}

        weighted_vol_sum = 0.0
        for asset in self.assets:
            vol = float(np.std(asset.returns, ddof=1))
            weight = asset.weight / total_weight
            weighted_vol_sum += weight * vol

        # Portfolio volatility
        port_returns = self.get_portfolio_returns()
        port_vol = float(np.std(port_returns, ddof=1))

        if port_vol < EPSILON:
            dr = 1.0
        else:
            dr = weighted_vol_sum / port_vol

        return {
            "diversification_ratio": dr,
            "weighted_avg_volatility": weighted_vol_sum,
            "portfolio_volatility": port_vol,
            "diversification_benefit": (dr - 1.0) * 100,  # percentage benefit
        }

    # ========================================================================
    # Risk Attribution & Budgeting
    # ========================================================================

    def marginal_var(
        self, asset_index: int, confidence: float = 0.95
    ) -> Dict[str, float]:
        """
        Calculate marginal VaR for a specific asset

        Args:
            asset_index: Index of asset in portfolio
            confidence: VaR confidence level

        Returns:
            Dict with marginal VaR contribution
        """
        if asset_index >= len(self.assets):
            raise ValueError(f"Asset index {asset_index} out of range")

        # Current portfolio VaR
        port_returns = self.get_portfolio_returns()
        base_var = self.value_at_risk(port_returns, confidence)["var"]

        # Calculate VaR with small increase in asset weight
        delta = 0.001
        original_weight = self.assets[asset_index].weight
        self.assets[asset_index].weight += delta

        new_returns = self.get_portfolio_returns()
        new_var = self.value_at_risk(new_returns, confidence)["var"]

        # Restore original weight
        self.assets[asset_index].weight = original_weight

        # Marginal VaR
        mvar = (new_var - base_var) / delta

        return {
            "marginal_var": mvar,
            "asset": self.assets[asset_index].symbol,
            "base_var": base_var,
            "contribution": mvar * original_weight,
        }

    def component_var(self, confidence: float = 0.95) -> List[Dict[str, float]]:
        """Calculate VaR contribution for each asset"""
        contributions = []

        for i in range(len(self.assets)):
            mvar_result = self.marginal_var(i, confidence)
            contributions.append(
                {
                    "asset": self.assets[i].symbol,
                    "weight": self.assets[i].weight,
                    "marginal_var": mvar_result["marginal_var"],
                    "component_var": mvar_result["contribution"],
                    "component_var_pct": mvar_result["contribution"] * 100,
                }
            )

        return contributions

    def risk_budget_analysis(
        self, target_budgets: Dict[str, float]
    ) -> List[RiskBudget]:
        """
        Analyze risk budget utilization

        Args:
            target_budgets: Dict mapping asset symbols to target risk allocation (%)

        Returns:
            List of RiskBudget objects
        """
        # Get component VaR
        components = self.component_var()
        total_var = sum(abs(c["component_var"]) for c in components)

        budgets = []
        for comp in components:
            symbol = comp["asset"]
            actual_risk = (
                abs(comp["component_var"]) / total_var * 100 if total_var > 0 else 0
            )
            allocated_risk = target_budgets.get(symbol, 0.0)
            utilization = actual_risk / allocated_risk if allocated_risk > 0 else 0.0

            budgets.append(
                RiskBudget(
                    asset=symbol,
                    allocated_risk=allocated_risk,
                    actual_risk=actual_risk,
                    contribution=comp["component_var"],
                    utilization=utilization,
                )
            )

        return budgets

    # ========================================================================
    # Stress Testing & Scenario Analysis
    # ========================================================================

    def stress_test(self, scenario: StressScenario) -> Dict[str, Any]:
        """
        Apply stress scenario to portfolio

        Args:
            scenario: StressScenario object defining the shock

        Returns:
            Dict with stressed portfolio metrics
        """
        results = {
            "scenario_name": scenario.name,
            "description": scenario.description,
            "shock_type": scenario.shock_type,
        }

        if scenario.shock_type == "absolute":
            # Apply absolute return shock to all assets
            shock = scenario.parameters.get("shock", 0.0)
            stressed_returns = []

            for asset in self.assets:
                stressed = asset.returns + shock
                stressed_returns.append(stressed)

            # Calculate stressed portfolio
            min_len = min(len(r) for r in stressed_returns)
            total_weight = sum(a.weight for a in self.assets)

            port_stressed = np.zeros(min_len)
            for i, asset in enumerate(self.assets):
                weight = asset.weight / total_weight if total_weight > 0 else 0
                port_stressed += stressed_returns[i][:min_len] * weight

            results.update(
                {
                    "base_value": 1.0,
                    "stressed_value": float(np.prod(1 + port_stressed)),
                    "loss": float(np.prod(1 + port_stressed)) - 1.0,
                    "loss_pct": (float(np.prod(1 + port_stressed)) - 1.0) * 100,
                }
            )

        elif scenario.shock_type == "relative":
            # Apply percentage shock
            shock_pct = scenario.parameters.get("shock_pct", 0.0)
            base_value = 1.0
            stressed_value = base_value * (1 + shock_pct)

            results.update(
                {
                    "base_value": base_value,
                    "stressed_value": stressed_value,
                    "loss": stressed_value - base_value,
                    "loss_pct": shock_pct * 100,
                }
            )

        # Calculate stressed VaR
        if scenario.shock_type in ["absolute", "relative"]:
            stressed_var = self.value_at_risk(
                port_stressed
                if scenario.shock_type == "absolute"
                else self.get_portfolio_returns()
            )
            results["stressed_var"] = stressed_var["var"]
            results["stressed_var_pct"] = stressed_var["var_pct"]

        return results

    def monte_carlo_var(
        self,
        num_simulations: int = 10000,
        time_horizon: int = 1,
        confidence: float = 0.95,
    ) -> Dict[str, Any]:
        """
        Monte Carlo VaR simulation

        Args:
            num_simulations: Number of MC paths
            time_horizon: Days to simulate
            confidence: VaR confidence level

        Returns:
            Dict with MC VaR and simulation results
        """
        returns = self.get_portfolio_returns()

        if len(returns) == 0:
            return {"mc_var": 0.0}

        mu = float(np.mean(returns))
        sigma = float(np.std(returns, ddof=1))

        # Generate random scenarios
        simulated_returns = np.random.normal(
            mu * time_horizon, sigma * math.sqrt(time_horizon), num_simulations
        )

        # Calculate VaR
        mc_var = float(np.percentile(simulated_returns, (1 - confidence) * 100))
        mc_cvar = float(np.mean(simulated_returns[simulated_returns <= mc_var]))

        return {
            "mc_var": mc_var,
            "mc_var_pct": mc_var * 100,
            "mc_cvar": mc_cvar,
            "mc_cvar_pct": mc_cvar * 100,
            "num_simulations": num_simulations,
            "time_horizon": time_horizon,
            "confidence": confidence,
            "simulated_mean": float(np.mean(simulated_returns)),
            "simulated_std": float(np.std(simulated_returns)),
        }

    # ========================================================================
    # Real-time Risk Monitoring
    # ========================================================================

    def risk_dashboard(self) -> Dict[str, Any]:
        """
        Generate comprehensive risk dashboard

        Returns:
            Dict with all key risk metrics and warnings
        """
        returns = self.get_portfolio_returns()

        if len(returns) == 0:
            return {"error": "No portfolio data available"}

        # Core metrics
        vol = self.volatility(returns)
        var_95 = self.value_at_risk(returns, 0.95)
        cvar_95 = self.conditional_var(returns, 0.95)
        sharpe = self.sharpe_ratio(returns)
        sortino = self.sortino_ratio(returns)
        dd = self.drawdown_analysis(returns)

        # Diversification
        div_ratio = self.diversification_ratio()
        corr = self.correlation_matrix()

        # Risk level classification
        if dd["max_drawdown_pct"] > 30:
            risk_level = RiskLevel.CRITICAL
        elif dd["max_drawdown_pct"] > 20:
            risk_level = RiskLevel.HIGH
        elif dd["max_drawdown_pct"] > 10:
            risk_level = RiskLevel.MEDIUM
        else:
            risk_level = RiskLevel.LOW

        # Generate warnings
        warnings = []
        if dd["current_drawdown"] > 0.15:
            warnings.append("ALERT: Current drawdown exceeds 15%")
        if sharpe["sharpe"] < 0.5:
            warnings.append("WARNING: Sharpe ratio below 0.5")
        if corr["average_correlation"] > 0.8:
            warnings.append("WARNING: High average correlation reduces diversification")
        if vol["volatility_pct"] > 25:
            warnings.append("WARNING: High volatility detected")

        return {
            "timestamp": datetime.now().isoformat(),
            "risk_level": risk_level.value,
            "warnings": warnings,
            "volatility": vol,
            "var_95": var_95,
            "cvar_95": cvar_95,
            "sharpe_ratio": sharpe,
            "sortino_ratio": sortino,
            "drawdown": dd,
            "diversification": div_ratio,
            "correlation": {
                "average": corr["average_correlation"],
                "max": corr.get("max_correlation", 0.0),
                "min": corr.get("min_correlation", 0.0),
            },
            "num_assets": len(self.assets),
            "observation_periods": len(returns),
        }

    def risk_limits_check(self, limits: Dict[str, float]) -> Dict[str, Any]:
        """
        Check if portfolio exceeds risk limits

        Args:
            limits: Dict with limit names and values
                   e.g., {"max_drawdown": 0.20, "min_sharpe": 1.0}

        Returns:
            Dict with breach status for each limit
        """
        returns = self.get_portfolio_returns()
        breaches = []

        if "max_drawdown" in limits:
            dd = self.drawdown_analysis(returns)
            if dd["max_drawdown"] > limits["max_drawdown"]:
                breaches.append(
                    {
                        "limit": "max_drawdown",
                        "threshold": limits["max_drawdown"],
                        "actual": dd["max_drawdown"],
                        "breach_amount": dd["max_drawdown"] - limits["max_drawdown"],
                    }
                )

        if "min_sharpe" in limits:
            sharpe = self.sharpe_ratio(returns)
            if sharpe["sharpe"] < limits["min_sharpe"]:
                breaches.append(
                    {
                        "limit": "min_sharpe",
                        "threshold": limits["min_sharpe"],
                        "actual": sharpe["sharpe"],
                        "breach_amount": limits["min_sharpe"] - sharpe["sharpe"],
                    }
                )

        if "max_var_95" in limits:
            var = self.value_at_risk(returns, 0.95)
            if abs(var["var"]) > limits["max_var_95"]:
                breaches.append(
                    {
                        "limit": "max_var_95",
                        "threshold": limits["max_var_95"],
                        "actual": abs(var["var"]),
                        "breach_amount": abs(var["var"]) - limits["max_var_95"],
                    }
                )

        return {
            "compliant": len(breaches) == 0,
            "num_breaches": len(breaches),
            "breaches": breaches,
            "checked_limits": list(limits.keys()),
        }

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
            "method": "parametric",
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
            "tail_observations": len(tail),
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
            "benchmark_variance": bench_var,
        }

    @staticmethod
    def treynor_ratio(
        returns: np.ndarray, benchmark_returns: np.ndarray, risk_free_rate: float = 0.01
    ) -> dict:
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

        return {"treynor": treynor, "excess_return": excess_return, "beta": beta_val}

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
            "tracking_error_annualized": tracking_error * math.sqrt(DAYS_PER_YEAR),
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
        z_cf = (
            z
            + (1 / 6) * (z**2 - 1) * skew
            + (1 / 24) * (z**3 - 3 * z) * kurt
            - (1 / 36) * (2 * z**3 - 5 * z) * skew**2
        )

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
            "modified_var": modified_var,
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
        ulcer = float(np.sqrt(np.mean(drawdown**2)))

        return {"ulcer_index": ulcer, "ulcer_index_pct": ulcer * 100}

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

        return {"martin": martin, "excess_return": excess_return, "ulcer_index": ulcer}

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
            "num_drawdown_periods": len(durations),
        }

    @staticmethod
    def kappa_3(
        returns: np.ndarray, risk_free_rate: float = 0.01, mar: float = 0.0
    ) -> dict:
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
            lpm3 = float(np.mean(downside**3))

        if abs(lpm3) < EPSILON:
            kappa3 = 0.0
        else:
            kappa3 = mean_excess / abs(lpm3) ** (1 / 3)
            kappa3 *= math.sqrt(DAYS_PER_YEAR)

        return {"kappa3": kappa3, "mean_excess": mean_excess, "lpm3": lpm3}

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
            gain_loss = 0.0 if avg_win == 0 else float("inf")
        else:
            gain_loss = avg_win / abs(avg_loss)

        return {
            "gain_loss": gain_loss if math.isfinite(gain_loss) else 0.0,
            "avg_win": avg_win,
            "avg_loss": avg_loss,
            "num_wins": len(gains),
            "num_losses": len(losses),
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
            downside_risk = float(np.sqrt(np.mean(downside**2)))

        if downside_risk < EPSILON:
            upr = 0.0
        else:
            upr = upside_potential / downside_risk

        return {
            "upr": upr,
            "upside_potential": upside_potential,
            "downside_risk": downside_risk,
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
        avg_dd = (
            float(np.mean(drawdown[drawdown > 0.001]))
            if np.any(drawdown > 0.001)
            else 0.01
        )

        if avg_dd < EPSILON:
            sterling = 0.0
        else:
            sterling = excess_return / avg_dd

        return {
            "sterling": sterling,
            "excess_return": excess_return,
            "avg_drawdown": avg_dd,
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
            "excess_return": excess_return,
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
            "dar_pct": dar * 100,
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
            "percentile": percentile,
        }

    @staticmethod
    def m_squared(
        returns: np.ndarray, risk_free_rate: float = 0.01, benchmark_vol: float = 10.0
    ) -> dict:
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
            "benchmark_vol": benchmark_vol,
        }

    @staticmethod
    def prospect_ratio(
        returns: np.ndarray, mar: float = 0.0, lambda_param: float = 2.25
    ) -> dict:
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
            "lambda": lambda_param,
        }

    @staticmethod
    def rachev_ratio(
        returns: np.ndarray, alpha: float = 0.95, beta: float = 0.95
    ) -> dict:
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
            "beta": beta,
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
            "sum_losses": sum_negative,
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

        return {"romad": romad, "excess_return": excess_return, "max_drawdown": max_dd}

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
            "ulcer_index": ulcer,
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
            window_returns = returns[i - window : i]
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
            "mean_vol": mean_vol,
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
            recovery_factor = 0.0 if total_return <= 0 else float("inf")
        else:
            recovery_factor = total_return / max_dd

        return {
            "recovery_factor": (
                recovery_factor if math.isfinite(recovery_factor) else 0.0
            ),
            "total_return": total_return,
            "total_return_pct": total_return * 100,
            "max_drawdown": max_dd,
            "final_value": float(final_value),
        }


# ========================================================================
# Demo Usage
# ========================================================================


def demo_risk_metrics():
    """Demonstrate RiskMetrics capabilities"""

    print("=" * 80)
    print("RiskMetrics Demo - Portfolio Risk Analysis")
    print("=" * 80)

    # Create sample portfolio
    np.random.seed(42)

    rm = RiskMetrics(risk_free_rate=0.03)

    # Add assets
    rm.add_asset(
        Asset(
            "AAPL",
            np.random.normal(0.001, 0.02, 252),
            0.30,
            30000,
            beta=1.2,
            sector="Technology",
        )
    )
    rm.add_asset(
        Asset(
            "JPM",
            np.random.normal(0.0005, 0.020, 252),
            0.20,
            20000,
            beta=1.1,
            sector="Financials",
        )
    )
    rm.add_asset(
        Asset(
            "PG",
            np.random.normal(0.0004, 0.015, 252),
            0.20,
            20000,
            beta=0.8,
            sector="Consumer",
        )
    )
    rm.add_asset(
        Asset(
            "JNJ",
            np.random.normal(0.0005, 0.018, 252),
            0.20,
            20000,
            beta=0.9,
            sector="Healthcare",
        )
    )
    rm.add_asset(
        Asset(
            "AGG",
            np.random.normal(0.0002, 0.008, 252),
            0.10,
            10000,
            beta=0.3,
            sector="Fixed Income",
        )
    )

    print("\nPortfolio created with 5 assets:")
    for asset in rm.assets:
        print(
            f"  {asset.symbol}: {asset.weight*100:.0f}% weight, ${asset.market_value:,}, "
            f"sector={asset.sector}, β={asset.beta}"
        )

    # ========================================================================
    # Core Risk Metrics
    # ========================================================================
    print("\n" + "=" * 80)
    print("Core Risk Metrics")
    print("=" * 80)

    portfolio_returns = rm.get_portfolio_returns()

    # Volatility
    vol = rm.volatility()
    print(f"\nVolatility:")
    print(f"  Annualized: {vol['volatility_pct']:.2f}%")
    print(f"  Variance: {vol['variance']:.6f}")

    # Value at Risk
    var_hist = rm.value_at_risk(confidence=0.95, method="historical")
    var_param = rm.value_at_risk(confidence=0.95, method="parametric")
    var_cf = rm.value_at_risk(confidence=0.95, method="cornish_fisher")

    print(f"\nValue at Risk (95% confidence):")
    print(f"  Historical: {var_hist['var_pct']:.2f}%")
    print(f"  Parametric: {var_param['var_pct']:.2f}%")
    print(f"  Cornish-Fisher: {var_cf['var_pct']:.2f}%")

    # Conditional VaR
    cvar = rm.conditional_var(confidence=0.95)
    print(f"\nConditional VaR (CVaR/ES):")
    print(f"  CVaR (95%): {cvar['cvar_pct']:.2f}%")
    print(f"  Tail observations: {cvar['tail_observations']}")

    # Downside deviation
    downside = rm.downside_deviation()
    print(f"\nDownside Risk:")
    print(f"  Downside Deviation: {downside['downside_deviation_pct']:.2f}%")
    print(f"  Downside Frequency: {downside['downside_frequency']*100:.1f}%")

    # ========================================================================
    # Risk-Adjusted Performance
    # ========================================================================
    print("\n" + "=" * 80)
    print("Risk-Adjusted Performance")
    print("=" * 80)

    sharpe = rm.sharpe_ratio()
    print(f"\nSharpe Ratio: {sharpe['sharpe']:.3f}")

    sortino = rm.sortino_ratio()
    print(f"Sortino Ratio: {sortino['sortino']:.3f}")

    calmar = rm.calmar_ratio()
    print(f"Calmar Ratio: {calmar['calmar']:.3f}")
    print(f"  Annual Return: {calmar['annual_return']*100:.2f}%")
    print(f"  Max Drawdown: {calmar['max_drawdown']*100:.2f}%")

    # ========================================================================
    # Drawdown Analysis
    # ========================================================================
    print("\n" + "=" * 80)
    print("Drawdown Analysis")
    print("=" * 80)

    dd = rm.drawdown_analysis()
    print(f"\nMax Drawdown: {dd['max_drawdown_pct']:.2f}%")
    print(f"Max DD Duration: {dd['max_drawdown_length']} days")
    print(f"Longest Drawdown: {dd['longest_drawdown_length']} days")
    print(f"Number of DD Periods: {dd['num_drawdown_periods']}")
    print(f"Average DD Depth: {dd['avg_drawdown_depth']*100:.2f}%")
    print(f"Current Drawdown: {dd['current_drawdown']*100:.2f}%")
    print(f"Time Underwater: {dd['time_underwater_pct']:.1f}%")

    # ========================================================================
    # Correlation & Diversification
    # ========================================================================
    print("\n" + "=" * 80)
    print("Correlation & Diversification")
    print("=" * 80)

    corr = rm.correlation_matrix()
    print(f"\nAverage Correlation: {corr['average_correlation']:.3f}")
    print(f"Max Correlation: {corr['max_correlation']:.3f}")
    print(f"Min Correlation: {corr['min_correlation']:.3f}")

    print("\nCorrelation Matrix:")
    matrix = corr["correlation_matrix"]
    symbols = corr["symbols"]

    # Print header
    print("      ", end="")
    for sym in symbols:
        print(f"{sym:>7}", end="")
    print()

    # Print matrix
    for i, sym in enumerate(symbols):
        print(f"{sym:>5}", end="")
        for j in range(len(symbols)):
            print(f"{matrix[i,j]:>7.3f}", end="")
        print()

    div = rm.diversification_ratio()
    print(f"\nDiversification Ratio: {div['diversification_ratio']:.3f}")
    print(f"Diversification Benefit: {div['diversification_benefit']:.2f}%")

    # ========================================================================
    # Risk Attribution
    # ========================================================================
    print("\n" + "=" * 80)
    print("Risk Attribution (Component VaR)")
    print("=" * 80)

    comp_var = rm.component_var(confidence=0.95)
    print("\nAsset    Weight   Marginal VaR   Component VaR")
    print("-" * 55)

    for comp in comp_var:
        print(
            f"{comp['asset']:>5}   {comp['weight']:>6.1%}   {comp['marginal_var']:>11.6f}   "
            f"{comp['component_var']:>13.6f}"
        )

    # Risk budgeting
    print("\n" + "=" * 80)
    print("Risk Budget Analysis")
    print("=" * 80)

    target_budgets = {"AAPL": 30.0, "JPM": 20.0, "PG": 20.0, "JNJ": 20.0, "AGG": 10.0}

    risk_budgets = rm.risk_budget_analysis(target_budgets)
    print("\nAsset   Allocated   Actual   Utilization   Status")
    print("-" * 55)

    for rb in risk_budgets:
        status = "OVER" if rb.is_over_budget else "OK"
        print(
            f"{rb.asset:>5}   {rb.allocated_risk:>6.1f}%   {rb.actual_risk:>6.1f}%   "
            f"{rb.utilization:>8.1%}      {status}"
        )

    # ========================================================================
    # Stress Testing
    # ========================================================================
    print("\n" + "=" * 80)
    print("Stress Testing")
    print("=" * 80)

    # Market crash scenario
    crash = StressScenario(
        name="Market Crash",
        shock_type="absolute",
        parameters={"shock": -0.20},
        description="20% market decline",
    )

    crash_result = rm.stress_test(crash)
    print(f"\nScenario: {crash_result['scenario_name']}")
    print(f"  Loss: {crash_result['loss_pct']:.2f}%")
    print(f"  Stressed Value: {crash_result['stressed_value']:.4f}")

    # Monte Carlo VaR
    print("\n" + "=" * 80)
    print("Monte Carlo VaR Simulation")
    print("=" * 80)

    mc_var = rm.monte_carlo_var(num_simulations=10000, time_horizon=1, confidence=0.95)
    print(f"\nSimulations: {mc_var['num_simulations']:,}")
    print(f"MC VaR (95%): {mc_var['mc_var_pct']:.2f}%")
    print(f"MC CVaR (95%): {mc_var['mc_cvar_pct']:.2f}%")

    # ========================================================================
    # Risk Dashboard
    # ========================================================================
    print("\n" + "=" * 80)
    print("Risk Monitoring Dashboard")
    print("=" * 80)

    dashboard = rm.risk_dashboard()
    print(f"\nTimestamp: {dashboard['timestamp']}")
    print(f"Risk Level: {dashboard['risk_level'].upper()}")
    print(f"Number of Assets: {dashboard['num_assets']}")

    print("\nKey Metrics:")
    print(f"  Volatility: {dashboard['volatility']['volatility_pct']:.2f}%")
    print(f"  VaR (95%): {dashboard['var_95']['var_pct']:.2f}%")
    print(f"  Sharpe Ratio: {dashboard['sharpe_ratio']['sharpe']:.3f}")
    print(f"  Max Drawdown: {dashboard['drawdown']['max_drawdown_pct']:.2f}%")
    print(
        f"  Diversification Ratio: {dashboard['diversification']['diversification_ratio']:.3f}"
    )

    if dashboard["warnings"]:
        print("\n⚠️  WARNINGS:")
        for warning in dashboard["warnings"]:
            print(f"  • {warning}")
    else:
        print("\n✓ No warnings")

    # ========================================================================
    # Risk Limits Check
    # ========================================================================
    print("\n" + "=" * 80)
    print("Risk Limits Compliance")
    print("=" * 80)

    limits = {"max_drawdown": 0.25, "min_sharpe": 0.5, "max_var_95": 0.05}

    compliance = rm.risk_limits_check(limits)
    print(
        f"\nCompliance Status: {'✓ COMPLIANT' if compliance['compliant'] else '✗ BREACHES'}"
    )
    print(f"Number of Breaches: {compliance['num_breaches']}")

    if compliance["breaches"]:
        print("\nBreach Details:")
        for breach in compliance["breaches"]:
            print(f"  Limit: {breach['limit']}")
            print(
                f"  Threshold: {breach['threshold']:.4f}, Actual: {breach['actual']:.4f}"
            )
            print(f"  Breach Amount: {breach['breach_amount']:.4f}")

    print("\n" + "=" * 80)
    print("Demo Complete!")
    print("=" * 80)


if __name__ == "__main__":
    demo_risk_metrics()
