import csv
from dataclasses import dataclass
from datetime import datetime
from typing import Dict, List

import numpy as np
from scipy import stats

# ============================================================================
# MATHEMATICAL FORMULAS
# ============================================================================
"""
1. VALUE AT RISK (VaR) 95%:
   VaR = μ - 1.96 × σ × √t

2. CONDITIONAL VaR (CVaR / Expected Shortfall):
   CVaR = μ - 2.063 × σ × √t

3. SHARPE RATIO:
   Sharpe = (R - Rf) / σ

4. SORTINO RATIO:
   Sortino = (R - Rt) / σd (downside deviation)

5. BETA (Systematic Risk):
   β = Cov(Asset, Market) / Var(Market)

6. TREYNOR RATIO:
   Treynor = (R - Rf) / β

7. INFORMATION RATIO:
   IR = Active Return / Tracking Error

8. MAXIMUM DRAWDOWN:
   MDD = (Trough - Peak) / Peak
"""


@dataclass
class PortfolioPosition:
    """Represents a portfolio position for risk analysis"""

    name: str
    initial_value: float
    current_value: float
    returns: List[float]  # Historical returns
    benchmark_returns: List[float]  # Market/benchmark returns
    risk_free_rate: float = 0.03  # 3% annual
    target_return: float = 0.05  # 5% target


class RiskCalculator:
    """Core risk metric calculations"""

    @staticmethod
    def calculate_var_95(returns: np.ndarray, confidence: float = 0.95) -> Dict:
        """
        Calculate Value at Risk at 95% confidence

        Formula: VaR = μ - z × σ
        """
        mu = np.mean(returns)
        sigma = np.std(returns)
        z_score = stats.norm.ppf(confidence)  # 1.96 for 95%

        var_95 = mu - z_score * sigma
        var_dollar = var_95 * 100000  # Assuming $100k portfolio

        return {
            "var_95_pct": var_95 * 100,
            "var_95_dollar": var_dollar,
            "confidence": confidence,
            "mean_return": mu,
            "volatility": sigma,
        }

    @staticmethod
    def calculate_cvar_95(returns: np.ndarray, confidence: float = 0.95) -> Dict:
        """
        Calculate Conditional VaR (Expected Shortfall)

        CVaR is the expected loss given that loss exceeds VaR
        """
        sorted_returns = np.sort(returns)
        cutoff_index = int((1 - confidence) * len(sorted_returns))
        tail_losses = sorted_returns[:cutoff_index]

        cvar = np.mean(tail_losses) if len(tail_losses) > 0 else sorted_returns[0]
        cvar_dollar = cvar * 100000

        return {
            "cvar_95_pct": cvar * 100,
            "cvar_95_dollar": cvar_dollar,
            "confidence": confidence,
            "tail_observations": len(tail_losses),
        }

    @staticmethod
    def calculate_sharpe_ratio(returns: np.ndarray, risk_free_rate: float) -> Dict:
        """
        Calculate Sharpe Ratio

        Formula: (R - Rf) / σ
        """
        excess_returns = returns - risk_free_rate
        sharpe = np.mean(excess_returns) / np.std(returns) if np.std(returns) > 0 else 0

        # Annualize (assuming daily returns)
        sharpe_annual = sharpe * np.sqrt(252)

        return {
            "sharpe_ratio": sharpe_annual,
            "excess_return": np.mean(excess_returns) * 100,
            "volatility": np.std(returns) * 100,
            "risk_free_rate": risk_free_rate * 100,
        }

    @staticmethod
    def calculate_sortino_ratio(returns: np.ndarray, target_return: float) -> Dict:
        """
        Calculate Sortino Ratio (focuses on downside risk)

        Formula: (R - Rt) / σd
        """
        excess_returns = returns - target_return
        downside_returns = returns[returns < target_return]
        downside_dev = (
            np.std(downside_returns) if len(downside_returns) > 0 else np.std(returns)
        )

        sortino = np.mean(excess_returns) / downside_dev if downside_dev > 0 else 0
        sortino_annual = sortino * np.sqrt(252)

        return {
            "sortino_ratio": sortino_annual,
            "downside_deviation": downside_dev * 100,
            "target_return": target_return * 100,
            "downside_days": len(downside_returns),
        }

    @staticmethod
    def calculate_beta(asset_returns: np.ndarray, market_returns: np.ndarray) -> Dict:
        """
        Calculate Beta (systematic risk)

        Formula: β = Cov(Asset, Market) / Var(Market)
        """
        if len(asset_returns) != len(market_returns):
            raise ValueError("Asset and market returns must have same length")

        covariance = np.cov(asset_returns, market_returns)[0, 1]
        market_variance = np.var(market_returns)

        beta = covariance / market_variance if market_variance > 0 else 1.0

        # Interpret beta
        interpretation = "Neutral"
        if beta > 1.2:
            interpretation = "High volatility (aggressive)"
        elif beta > 1.0:
            interpretation = "More volatile than market"
        elif beta < 0.8:
            interpretation = "Defensive"

        return {
            "beta": beta,
            "covariance": covariance,
            "market_variance": market_variance,
            "interpretation": interpretation,
        }

    @staticmethod
    def calculate_treynor_ratio(
        returns: np.ndarray, market_returns: np.ndarray, risk_free_rate: float
    ) -> Dict:
        """
        Calculate Treynor Ratio

        Formula: (R - Rf) / β
        """
        beta_result = RiskCalculator.calculate_beta(returns, market_returns)
        beta = beta_result["beta"]

        excess_return = np.mean(returns) - risk_free_rate
        treynor = excess_return / beta if beta != 0 else 0
        treynor_annual = treynor * 252  # Annualize

        return {
            "treynor_ratio": treynor_annual,
            "beta": beta,
            "excess_return": excess_return * 100,
            "risk_free_rate": risk_free_rate * 100,
        }

    @staticmethod
    def calculate_information_ratio(
        returns: np.ndarray, benchmark_returns: np.ndarray
    ) -> Dict:
        """
        Calculate Information Ratio

        Formula: Active Return / Tracking Error
        """
        active_returns = returns - benchmark_returns
        active_return = np.mean(active_returns)
        tracking_error = np.std(active_returns)

        ir = active_return / tracking_error if tracking_error > 0 else 0
        ir_annual = ir * np.sqrt(252)

        return {
            "information_ratio": ir_annual,
            "active_return": active_return * 100,
            "tracking_error": tracking_error * 100,
            "correlation": np.corrcoef(returns, benchmark_returns)[0, 1],
        }

    @staticmethod
    def calculate_maximum_drawdown(cumulative_returns: np.ndarray) -> Dict:
        """
        Calculate Maximum Drawdown

        Formula: (Trough - Peak) / Peak
        """
        cumulative_wealth = (1 + cumulative_returns).cumprod()
        running_max = np.maximum.accumulate(cumulative_wealth)
        drawdown = (cumulative_wealth - running_max) / running_max

        max_dd = np.min(drawdown)
        max_dd_idx = np.argmin(drawdown)

        # Find peak before drawdown
        peak_idx = (
            np.argmax(cumulative_wealth[: max_dd_idx + 1]) if max_dd_idx > 0 else 0
        )

        recovery_days = 0
        if max_dd_idx < len(cumulative_wealth) - 1:
            peak_value = cumulative_wealth[peak_idx]
            for i in range(max_dd_idx + 1, len(cumulative_wealth)):
                if cumulative_wealth[i] >= peak_value:
                    recovery_days = i - max_dd_idx
                    break

        return {
            "max_drawdown_pct": max_dd * 100,
            "peak_date_idx": peak_idx,
            "trough_date_idx": max_dd_idx,
            "recovery_days": recovery_days if recovery_days > 0 else "Not recovered",
            "current_drawdown_pct": drawdown[-1] * 100,
        }


class ComprehensiveRiskAnalyzer:
    """Analyze portfolio with all risk metrics"""

    def __init__(self, calculator: RiskCalculator = None):
        self.calculator = calculator or RiskCalculator()

    def analyze_portfolio(self, position: PortfolioPosition) -> Dict:
        """
        Complete risk analysis for a portfolio position
        """
        returns = np.array(position.returns)
        benchmark_returns = np.array(position.benchmark_returns)

        # Calculate all metrics
        var_result = self.calculator.calculate_var_95(returns)
        cvar_result = self.calculator.calculate_cvar_95(returns)
        sharpe_result = self.calculator.calculate_sharpe_ratio(
            returns, position.risk_free_rate / 252
        )
        sortino_result = self.calculator.calculate_sortino_ratio(
            returns, position.target_return / 252
        )
        beta_result = self.calculator.calculate_beta(returns, benchmark_returns)
        treynor_result = self.calculator.calculate_treynor_ratio(
            returns, benchmark_returns, position.risk_free_rate / 252
        )
        ir_result = self.calculator.calculate_information_ratio(
            returns, benchmark_returns
        )
        mdd_result = self.calculator.calculate_maximum_drawdown(returns)

        # Overall assessment
        total_return = (
            position.current_value - position.initial_value
        ) / position.initial_value

        return {
            "position_name": position.name,
            "total_return_pct": total_return * 100,
            "var_95_pct": var_result["var_95_pct"],
            "cvar_95_pct": cvar_result["cvar_95_pct"],
            "sharpe_ratio": sharpe_result["sharpe_ratio"],
            "sortino_ratio": sortino_result["sortino_ratio"],
            "beta": beta_result["beta"],
            "treynor_ratio": treynor_result["treynor_ratio"],
            "information_ratio": ir_result["information_ratio"],
            "max_drawdown_pct": mdd_result["max_drawdown_pct"],
            "volatility": var_result["volatility"] * 100 * np.sqrt(252),  # Annualized
            "risk_rating": self._assess_risk_rating(
                sharpe_result["sharpe_ratio"],
                beta_result["beta"],
                mdd_result["max_drawdown_pct"],
            ),
        }

    def _assess_risk_rating(self, sharpe: float, beta: float, mdd: float) -> str:
        """Assess overall risk rating"""
        score = 0

        # Sharpe component
        if sharpe > 2.0:
            score += 3
        elif sharpe > 1.0:
            score += 2
        elif sharpe > 0.5:
            score += 1

        # Beta component
        if 0.8 <= beta <= 1.2:
            score += 2
        elif 0.6 <= beta <= 1.4:
            score += 1

        # Drawdown component
        if mdd > -10:
            score += 3
        elif mdd > -20:
            score += 2
        elif mdd > -30:
            score += 1

        if score >= 7:
            return "Excellent"
        elif score >= 5:
            return "Good"
        elif score >= 3:
            return "Moderate"
        else:
            return "Poor"


# ============================================================================
# TEST SCENARIOS: 10 REALISTIC PORTFOLIO POSITIONS
# ============================================================================


def generate_test_positions() -> List[PortfolioPosition]:
    """Generate 10 realistic portfolio positions with varied risk profiles"""

    np.random.seed(42)

    positions = []

    # Position 1: Conservative Bonds Portfolio
    bond_returns = np.random.normal(0.0002, 0.0005, 252)  # Low vol, positive
    market_returns = np.random.normal(0.0004, 0.002, 252)
    positions.append(
        PortfolioPosition(
            name="Conservative Bonds",
            initial_value=100000,
            current_value=105000,
            returns=bond_returns.tolist(),
            benchmark_returns=market_returns.tolist(),
            risk_free_rate=0.03,
        )
    )

    # Position 2: Aggressive Tech Stocks
    tech_returns = np.random.normal(0.0008, 0.025, 252)  # High vol
    positions.append(
        PortfolioPosition(
            name="Aggressive Tech",
            initial_value=100000,
            current_value=120000,
            returns=tech_returns.tolist(),
            benchmark_returns=market_returns.tolist(),
            risk_free_rate=0.03,
        )
    )

    # Position 3: Balanced 60/40 Portfolio
    balanced_returns = np.random.normal(0.0004, 0.012, 252)
    positions.append(
        PortfolioPosition(
            name="Balanced 60/40",
            initial_value=100000,
            current_value=110000,
            returns=balanced_returns.tolist(),
            benchmark_returns=market_returns.tolist(),
            risk_free_rate=0.03,
        )
    )

    # Position 4: High Dividend Value Stocks
    dividend_returns = np.random.normal(0.0003, 0.008, 252)
    positions.append(
        PortfolioPosition(
            name="High Dividend Value",
            initial_value=100000,
            current_value=108000,
            returns=dividend_returns.tolist(),
            benchmark_returns=market_returns.tolist(),
            risk_free_rate=0.03,
        )
    )

    # Position 5: Emerging Markets (High Risk)
    em_returns = np.random.normal(0.0005, 0.03, 252)
    positions.append(
        PortfolioPosition(
            name="Emerging Markets",
            initial_value=100000,
            current_value=112000,
            returns=em_returns.tolist(),
            benchmark_returns=market_returns.tolist(),
            risk_free_rate=0.03,
        )
    )

    # Position 6: Gold/Commodities Hedge
    gold_returns = np.random.normal(0.0001, 0.015, 252)
    positions.append(
        PortfolioPosition(
            name="Gold & Commodities",
            initial_value=100000,
            current_value=102500,
            returns=gold_returns.tolist(),
            benchmark_returns=market_returns.tolist(),
            risk_free_rate=0.03,
        )
    )

    # Position 7: S&P 500 Index Fund
    sp500_returns = np.random.normal(0.0004, 0.01, 252)
    positions.append(
        PortfolioPosition(
            name="S&P 500 Index",
            initial_value=100000,
            current_value=110000,
            returns=sp500_returns.tolist(),
            benchmark_returns=market_returns.tolist(),
            risk_free_rate=0.03,
        )
    )

    # Position 8: Crypto Portfolio (Extreme Volatility)
    crypto_returns = np.random.normal(0.001, 0.05, 252)
    positions.append(
        PortfolioPosition(
            name="Crypto Portfolio",
            initial_value=100000,
            current_value=125000,
            returns=crypto_returns.tolist(),
            benchmark_returns=market_returns.tolist(),
            risk_free_rate=0.03,
        )
    )

    # Position 9: Real Estate Investment Trust
    reit_returns = np.random.normal(0.0003, 0.01, 252)
    positions.append(
        PortfolioPosition(
            name="REIT Portfolio",
            initial_value=100000,
            current_value=107500,
            returns=reit_returns.tolist(),
            benchmark_returns=market_returns.tolist(),
            risk_free_rate=0.03,
        )
    )

    # Position 10: Market Neutral Strategy
    neutral_returns = np.random.normal(0.0002, 0.004, 252)
    positions.append(
        PortfolioPosition(
            name="Market Neutral",
            initial_value=100000,
            current_value=105000,
            returns=neutral_returns.tolist(),
            benchmark_returns=market_returns.tolist(),
            risk_free_rate=0.03,
        )
    )

    return positions


def export_results_to_csv(
    results: List[Dict], filename: str = "risk_analysis_results.csv"
):
    """Export analysis results to CSV"""
    if not results:
        return

    keys = results[0].keys()
    with open(filename, "w", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=keys)
        writer.writeheader()
        writer.writerows(results)
    print(f"\n✅ Results exported to {filename}")


# ============================================================================
# MAIN EXECUTION
# ============================================================================

if __name__ == "__main__":
    print("=" * 80)
    print("COMPREHENSIVE RISK ANALYSIS - PORTFOLIO RISK METRICS")
    print("=" * 80)
    print()

    # Generate test positions
    positions = generate_test_positions()
    analyzer = ComprehensiveRiskAnalyzer()

    # Analyze all positions
    results = []
    print(
        f"{'Portfolio':<25} {'Return':>8} {'Sharpe':>8} {'Beta':>8} {'Max DD':>8} {'VaR 95%':>9} {'Rating':>12}"
    )
    print("-" * 100)

    for position in positions:
        result = analyzer.analyze_portfolio(position)
        results.append(result)

        print(
            f"{result['position_name']:<25} {result['total_return_pct']:>7.2f}% "
            f"{result['sharpe_ratio']:>8.2f} {result['beta']:>8.2f} "
            f"{result['max_drawdown_pct']:>7.2f}% {result['var_95_pct']:>8.2f}% "
            f"{result['risk_rating']:>12}"
        )

    print("-" * 100)
    print()

    # Summary statistics
    avg_sharpe = np.mean([r["sharpe_ratio"] for r in results])
    avg_return = np.mean([r["total_return_pct"] for r in results])
    best_sharpe = max(results, key=lambda x: x["sharpe_ratio"])
    worst_dd = min(results, key=lambda x: x["max_drawdown_pct"])

    print(f"SUMMARY STATISTICS")
    print(f"  Total Portfolios: {len(results)}")
    print(f"  Average Return: {avg_return:.2f}%")
    print(f"  Average Sharpe Ratio: {avg_sharpe:.2f}")
    print(
        f"  Best Risk-Adjusted Return: {best_sharpe['position_name']} (Sharpe: {best_sharpe['sharpe_ratio']:.2f})"
    )
    print(
        f"  Largest Drawdown: {worst_dd['position_name']} ({worst_dd['max_drawdown_pct']:.2f}%)"
    )
    print()

    # Export to CSV
    export_results_to_csv(results)
