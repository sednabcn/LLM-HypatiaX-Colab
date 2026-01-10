import csv
from dataclasses import dataclass
from datetime import datetime
from typing import Dict, List, Optional

import numpy as np
from scipy import stats

# ============================================================================
# EXTENDED RISK FORMULAS - 30 TOTAL (20 ORIGINAL + 10 NEW)
# ============================================================================
"""
ORIGINAL FORMULAS (1-20):
1. VaR 95%, 2. CVaR, 3. Sharpe, 4. Sortino, 5. Beta, 6. Treynor,
7. Information Ratio, 8. Maximum Drawdown
---

### 9. Calmar Ratio
**Formula:** `Calmar = R_annual / MDD`

**Arguments:**
- `R_annual` (annual_return): Annualized return (percent)
- `MDD` (max_drawdown): Maximum drawdown (percent, positive value)

**Usage:** Return relative to worst drawdown. Higher values indicate better performance relative to largest loss. Commonly used in hedge fund evaluation. Ratio > 3 is considered excellent.

---

### 10. Omega Ratio
**Formula:** `Ω = (Gains + ε) / (Losses + ε)` (simplified with epsilon for stability)

**Arguments:**
- `Gains` (gains): Expected gains above threshold (percent)
- `Losses` (losses): Expected losses below threshold (percent)

**Usage:** Probability-weighted ratio of gains to losses relative to a threshold. Ω > 1 means gains exceed losses. Captures all moments of return distribution, unlike Sharpe which only uses first two moments.

---

### 11. Value at Risk (VaR) 99%
**Formula:** `VaR₉₉ = μ - 2.576 × σ × √t`

**Arguments:**
- `μ` (mu): Expected return (percent)
- `σ` (sigma): Volatility (percent, annualized)
- `t`: Time horizon (days)

**Usage:** Maximum expected loss at 99% confidence level. More conservative than VaR₉₅. Used for regulatory capital requirements and extreme risk assessment. Only 1% chance of exceeding this loss.

---

### 12. Modified Sharpe Ratio
**Formula:** `Modified Sharpe = (R - Rf) / (σ × (1 + S/6))`

**Arguments:**
- `R` (returns): Portfolio returns (percent, annualized)
- `Rf` (risk_free): Risk-free rate (percent, annualized)
- `σ` (volatility): Volatility (percent, annualized)
- `S` (skewness): Return distribution skewness (dimensionless)

**Usage:** Adjusts traditional Sharpe ratio for skewness in returns. Negative skew increases denominator (penalizes), positive skew decreases it (rewards). Better for non-normal return distributions.

---

### 13. Ulcer Index
**Formula:** `UI = √(Σ(DD²) / n)`

**Arguments:**
- `DD²_sum` (dd_squared_sum): Sum of squared drawdowns (percent²)
- `n` (periods): Number of periods (dimensionless)

**Usage:** Measures depth and duration of drawdowns. Unlike standard deviation, it only considers downside volatility. Lower values indicate less stress/pain from declines. Used in Martin Ratio calculation.

---

### 14. Martin Ratio (Ulcer Performance Index)
**Formula:** `Martin = R / UI`

**Arguments:**
- `R` (returns): Portfolio returns (percent, annualized)
- `UI` (ulcer_index): Ulcer Index (percent)

**Usage:** Return per unit of downside risk as measured by Ulcer Index. Similar concept to Sharpe but uses Ulcer Index instead of standard deviation. Preferred for measuring stress-adjusted returns.

---

### 15. Kappa 3 Ratio
**Formula:** `Kappa₃ = R / LPM₃^(1/3)`

**Arguments:**
- `R` (returns): Portfolio returns (percent)
- `LPM₃` (lpm3): Lower Partial Moment of 3rd order (percent³)

**Usage:** Risk-adjusted return using 3rd order lower partial moment. Emphasizes larger losses more heavily than smaller ones. Part of Kappa family; higher orders give more weight to extreme losses.

---

### 16. Gain-Loss Ratio
**Formula:** `G/L = Average_Win / Average_Loss`

**Arguments:**
- `Average_Win` (avg_gain): Average gain per winning trade (percent)
- `Average_Loss` (avg_loss): Average loss per losing trade (percent)

**Usage:** Average size of wins versus losses. Ratio > 1 means average win exceeds average loss. Combined with win rate to evaluate trading strategy quality. Used extensively in systematic trading.

---

### 17. Upside Potential Ratio
**Formula:** `UPR = Upside_Potential / Downside_Risk`

**Arguments:**
- `Upside_Potential` (upside_potential): Expected gains above MAR (percent)
- `Downside_Risk` (downside_risk): Downside deviation below MAR (percent)

**Usage:** Measures upside potential relative to downside risk, both measured against Minimum Acceptable Return (MAR). Higher values preferred. Useful when investors have specific return targets.

---

### 18. Sterling Ratio
**Formula:** `Sterling = (R - 10%) / AvgDD`

**Arguments:**
- `R` (annual_return): Annualized return (percent)
- `AvgDD` (avg_drawdown): Average of largest drawdowns (percent)

**Usage:** Return above 10% threshold per unit of average drawdown. Originally used 10% as minimum acceptable return. Higher ratios indicate better performance relative to typical drawdown magnitude.

---

### 19. Burke Ratio
**Formula:** `Burke = Excess_Return / √(Σ DD²)`

**Arguments:**
- `Excess_Return` (excess_return): Return above risk-free rate (percent)
- `√(Σ DD²)` (sqrt_sum_dd): Square root of sum of squared drawdowns (percent)

**Usage:** Excess return per unit of drawdown magnitude. Similar to Calmar but uses multiple drawdowns rather than just maximum. Provides more comprehensive view of drawdown risk.

---

### 20. Pain Ratio
**Formula:** `Pain = R / Pain_Index`

**Arguments:**
- `R` (returns): Portfolio returns (percent)
- `Pain_Index` (pain_index): Average drawdown over evaluation period (percent)

**Usage:** Return per unit of average pain/drawdown. Pain Index measures average depth of underwater periods. Higher ratios indicate better return for experienced drawdowns. Simple but effective drawdown-adjusted metric.


NEW FORMULAS (21-30):
21. CDaR (Conditional Drawdown at Risk)
22. Tail Ratio
23. M² (Modigliani-Modigliani)
24. Prospect Ratio
25. Rachev Ratio
26. D-Ratio
27. RoMaD (Return over Maximum Drawdown)
28. Serenity Ratio
29. Stability Index
30. Recovery Factor
"""


@dataclass
class PortfolioPosition:
    """Represents a portfolio position for risk analysis"""

    name: str
    initial_value: float
    current_value: float
    returns: List[float]
    benchmark_returns: List[float]
    risk_free_rate: float = 0.03
    target_return: float = 0.05


class RiskCalculator:
    """Extended risk metric calculations"""

    # ========================================================================
    # ORIGINAL FORMULAS
    # ========================================================================

    @staticmethod
    def calculate_var_95(returns: np.ndarray, confidence: float = 0.95) -> Dict:
        """Formula 1: Value at Risk at 95% confidence"""
        mu = np.mean(returns)
        sigma = np.std(returns)
        z_score = stats.norm.ppf(confidence)

        var_95 = mu - z_score * sigma
        var_dollar = var_95 * 100000

        return {
            "var_95_pct": var_95 * 100,
            "var_95_dollar": var_dollar,
            "confidence": confidence,
            "mean_return": mu,
            "volatility": sigma,
        }

    @staticmethod
    def calculate_cvar_95(returns: np.ndarray, confidence: float = 0.95) -> Dict:
        """Formula 2: Conditional VaR (Expected Shortfall)"""
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
        """Formula 3: Sharpe Ratio"""
        excess_returns = returns - risk_free_rate
        sharpe = np.mean(excess_returns) / np.std(returns) if np.std(returns) > 0 else 0
        sharpe_annual = sharpe * np.sqrt(252)

        return {
            "sharpe_ratio": sharpe_annual,
            "excess_return": np.mean(excess_returns) * 100,
            "volatility": np.std(returns) * 100,
            "risk_free_rate": risk_free_rate * 100,
        }

    @staticmethod
    def calculate_sortino_ratio(returns: np.ndarray, target_return: float) -> Dict:
        """Formula 4: Sortino Ratio"""
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
        """Formula 5: Beta (systematic risk)"""
        if len(asset_returns) != len(market_returns):
            raise ValueError("Asset and market returns must have same length")

        covariance = np.cov(asset_returns, market_returns)[0, 1]
        market_variance = np.var(market_returns)
        beta = covariance / market_variance if market_variance > 0 else 1.0

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
        """Formula 6: Treynor Ratio"""
        beta_result = RiskCalculator.calculate_beta(returns, market_returns)
        beta = beta_result["beta"]

        excess_return = np.mean(returns) - risk_free_rate
        treynor = excess_return / beta if beta != 0 else 0
        treynor_annual = treynor * 252

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
        """Formula 7: Information Ratio"""
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
        """Formula 8: Maximum Drawdown"""
        cumulative_wealth = (1 + cumulative_returns).cumprod()
        running_max = np.maximum.accumulate(cumulative_wealth)
        drawdown = (cumulative_wealth - running_max) / running_max

        max_dd = np.min(drawdown)
        max_dd_idx = np.argmin(drawdown)
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
            "drawdown_series": drawdown,
        }

    # ========================================================================
    # NEW FORMULAS (21-30)
    # ========================================================================

    @staticmethod
    def calculate_cdar(returns: np.ndarray, confidence: float = 0.95) -> Dict:
        """Formula 21: Conditional Drawdown at Risk"""
        cumulative_wealth = (1 + returns).cumprod()
        running_max = np.maximum.accumulate(cumulative_wealth)
        drawdowns = (cumulative_wealth - running_max) / running_max

        # Calculate DaR (Drawdown at Risk)
        dar = np.percentile(drawdowns, (1 - confidence) * 100)

        # CDaR: expected drawdown given it exceeds DaR
        tail_drawdowns = drawdowns[drawdowns <= dar]
        cdar = np.mean(tail_drawdowns) if len(tail_drawdowns) > 0 else dar

        return {
            "cdar_pct": cdar * 100,
            "dar_pct": dar * 100,
            "confidence": confidence,
            "tail_observations": len(tail_drawdowns),
            "interpretation": (
                "Good" if cdar > -0.15 else "Moderate" if cdar > -0.25 else "High Risk"
            ),
        }

    @staticmethod
    def calculate_tail_ratio(returns: np.ndarray) -> Dict:
        """Formula 22: Tail Ratio"""
        percentile_95 = np.percentile(returns, 95)
        percentile_5 = np.percentile(returns, 5)

        tail_ratio = abs(percentile_95) / abs(percentile_5) if percentile_5 != 0 else 0

        interpretation = "Symmetric"
        if tail_ratio > 1.2:
            interpretation = "Positive skew (fatter right tail)"
        elif tail_ratio < 0.8:
            interpretation = "Negative skew (fatter left tail)"

        return {
            "tail_ratio": tail_ratio,
            "percentile_95": percentile_95 * 100,
            "percentile_5": percentile_5 * 100,
            "interpretation": interpretation,
        }

    @staticmethod
    def calculate_m_squared(
        returns: np.ndarray, risk_free_rate: float, benchmark_vol: float
    ) -> Dict:
        """Formula 23: M² (Modigliani-Modigliani)"""
        sharpe_result = RiskCalculator.calculate_sharpe_ratio(returns, risk_free_rate)
        sharpe = sharpe_result["sharpe_ratio"]

        # M² = Rf + Sharpe × σ_benchmark
        m_squared = risk_free_rate * 100 + sharpe * benchmark_vol

        return {
            "m_squared_pct": m_squared,
            "sharpe_ratio": sharpe,
            "benchmark_vol": benchmark_vol,
            "risk_free_rate": risk_free_rate * 100,
            "interpretation": f"Return at benchmark risk: {m_squared:.2f}%",
        }

    @staticmethod
    def calculate_prospect_ratio(returns: np.ndarray) -> Dict:
        """Formula 24: Prospect Ratio"""
        wins = returns[returns > 0]
        losses = returns[returns < 0]

        p_win = len(wins) / len(returns) if len(returns) > 0 else 0
        p_loss = len(losses) / len(returns) if len(returns) > 0 else 0
        avg_win = np.mean(wins) if len(wins) > 0 else 0
        avg_loss = abs(np.mean(losses)) if len(losses) > 0 else 1

        # Prospect = (P_win × Avg_win²) / (P_loss × Avg_loss²)
        numerator = p_win * (avg_win**2)
        denominator = p_loss * (avg_loss**2) if p_loss > 0 and avg_loss > 0 else 1
        prospect = numerator / denominator if denominator > 0 else 0

        return {
            "prospect_ratio": prospect,
            "win_rate": p_win * 100,
            "avg_win_pct": avg_win * 100,
            "avg_loss_pct": avg_loss * 100,
            "interpretation": "Favorable" if prospect > 1 else "Unfavorable",
        }

    @staticmethod
    def calculate_rachev_ratio(returns: np.ndarray, alpha: float = 0.95) -> Dict:
        """Formula 25: Rachev Ratio (Tail Risk Ratio)"""
        # CVaR of gains (upper tail)
        gains = returns[returns > 0]
        cvar_gains = (
            np.mean(np.percentile(gains, [alpha * 100, 100])) if len(gains) > 0 else 0
        )

        # CVaR of losses (lower tail)
        losses = returns[returns < 0]
        cvar_losses = (
            abs(np.mean(np.percentile(losses, [0, (1 - alpha) * 100])))
            if len(losses) > 0
            else 1
        )

        rachev = cvar_gains / cvar_losses if cvar_losses > 0 else 0

        return {
            "rachev_ratio": rachev,
            "cvar_gains_pct": cvar_gains * 100,
            "cvar_losses_pct": cvar_losses * 100,
            "alpha": alpha,
            "interpretation": "Good" if rachev > 1 else "Poor",
        }

    @staticmethod
    def calculate_d_ratio(returns: np.ndarray) -> Dict:
        """Formula 26: D-Ratio (Downside Risk over Time)"""
        cumulative_wealth = (1 + returns).cumprod()
        running_max = np.maximum.accumulate(cumulative_wealth)
        underwater = (cumulative_wealth - running_max) / running_max

        # Average underwater depth
        avg_underwater = np.mean(abs(underwater))
        total_vol = np.std(returns)

        d_ratio = avg_underwater / total_vol if total_vol > 0 else 0

        return {
            "d_ratio": d_ratio,
            "avg_underwater_pct": avg_underwater * 100,
            "total_volatility": total_vol * 100,
            "interpretation": (
                "Excellent" if d_ratio < 0.5 else "Good" if d_ratio < 1.0 else "Poor"
            ),
        }

    @staticmethod
    def calculate_romad(returns: np.ndarray) -> Dict:
        """Formula 27: Return over Maximum Drawdown (RoMaD)"""
        annual_return = np.mean(returns) * 252 * 100
        mdd_result = RiskCalculator.calculate_maximum_drawdown(returns)
        max_dd = abs(mdd_result["max_drawdown_pct"])

        romad = annual_return / max_dd if max_dd > 0 else 0

        return {
            "romad": romad,
            "annual_return_pct": annual_return,
            "max_drawdown_pct": max_dd,
            "interpretation": (
                "Excellent" if romad > 5 else "Good" if romad > 2 else "Moderate"
            ),
        }

    @staticmethod
    def calculate_serenity_ratio(returns: np.ndarray, risk_free_rate: float) -> Dict:
        """Formula 28: Serenity Ratio"""
        annual_return = np.mean(returns) * 252

        # Calculate underwater periods
        cumulative_wealth = (1 + returns).cumprod()
        running_max = np.maximum.accumulate(cumulative_wealth)
        underwater = (cumulative_wealth - running_max) / running_max
        underwater_periods = underwater[underwater < 0]

        avg_underwater = (
            abs(np.mean(underwater_periods)) if len(underwater_periods) > 0 else 0.01
        )

        excess_return = annual_return - risk_free_rate
        serenity = excess_return / avg_underwater if avg_underwater > 0 else 0

        return {
            "serenity_ratio": serenity,
            "excess_return_pct": excess_return * 100,
            "avg_underwater_pct": avg_underwater * 100,
            "interpretation": (
                "Strong" if serenity > 1.5 else "Moderate" if serenity > 0.5 else "Weak"
            ),
        }

    @staticmethod
    def calculate_stability_index(returns: np.ndarray) -> Dict:
        """Formula 29: Stability Index (R² of equity curve)"""
        cumulative_returns = (1 + returns).cumprod()
        x = np.arange(len(cumulative_returns))

        # Linear regression
        slope, intercept, r_value, p_value, std_err = stats.linregress(
            x, cumulative_returns
        )
        r_squared = r_value**2

        interpretation = "Excellent"
        if r_squared < 0.7:
            interpretation = "Poor"
        elif r_squared < 0.85:
            interpretation = "Moderate"
        elif r_squared < 0.95:
            interpretation = "Good"

        return {
            "stability_index": r_squared,
            "r_squared": r_squared,
            "slope": slope,
            "interpretation": interpretation,
        }

    @staticmethod
    def calculate_recovery_factor(
        returns: np.ndarray, initial_capital: float = 100000
    ) -> Dict:
        """Formula 30: Recovery Factor"""
        # Net profit
        final_value = initial_capital * (1 + returns).prod()
        net_profit = final_value - initial_capital

        # Maximum drawdown in dollars
        mdd_result = RiskCalculator.calculate_maximum_drawdown(returns)
        max_dd_pct = abs(mdd_result["max_drawdown_pct"]) / 100
        max_dd_dollar = initial_capital * max_dd_pct

        recovery = net_profit / max_dd_dollar if max_dd_dollar > 0 else 0

        return {
            "recovery_factor": recovery,
            "net_profit": net_profit,
            "max_drawdown_dollar": max_dd_dollar,
            "interpretation": (
                "Excellent" if recovery > 5 else "Good" if recovery > 3 else "Moderate"
            ),
        }


class ComprehensiveRiskAnalyzer:
    """Analyze portfolio with ALL 30 risk metrics"""

    def __init__(self, calculator: RiskCalculator = None):
        self.calculator = calculator or RiskCalculator()

    def analyze_portfolio_complete(self, position: PortfolioPosition) -> Dict:
        """
        Complete risk analysis with all 30 formulas
        """
        returns = np.array(position.returns)
        benchmark_returns = np.array(position.benchmark_returns)

        # Calculate all original metrics (1-8)
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

        # Calculate all new metrics (21-30)
        cdar_result = self.calculator.calculate_cdar(returns)
        tail_result = self.calculator.calculate_tail_ratio(returns)
        m2_result = self.calculator.calculate_m_squared(
            returns,
            position.risk_free_rate / 252,
            np.std(benchmark_returns) * np.sqrt(252) * 100,
        )
        prospect_result = self.calculator.calculate_prospect_ratio(returns)
        rachev_result = self.calculator.calculate_rachev_ratio(returns)
        d_ratio_result = self.calculator.calculate_d_ratio(returns)
        romad_result = self.calculator.calculate_romad(returns)
        serenity_result = self.calculator.calculate_serenity_ratio(
            returns, position.risk_free_rate / 252
        )
        stability_result = self.calculator.calculate_stability_index(returns)
        recovery_result = self.calculator.calculate_recovery_factor(
            returns, position.initial_value
        )

        # Overall assessment
        total_return = (
            position.current_value - position.initial_value
        ) / position.initial_value

        return {
            "position_name": position.name,
            "total_return_pct": total_return * 100,
            # Original metrics
            "var_95_pct": var_result["var_95_pct"],
            "cvar_95_pct": cvar_result["cvar_95_pct"],
            "sharpe_ratio": sharpe_result["sharpe_ratio"],
            "sortino_ratio": sortino_result["sortino_ratio"],
            "beta": beta_result["beta"],
            "treynor_ratio": treynor_result["treynor_ratio"],
            "information_ratio": ir_result["information_ratio"],
            "max_drawdown_pct": mdd_result["max_drawdown_pct"],
            # New metrics
            "cdar_pct": cdar_result["cdar_pct"],
            "tail_ratio": tail_result["tail_ratio"],
            "m_squared_pct": m2_result["m_squared_pct"],
            "prospect_ratio": prospect_result["prospect_ratio"],
            "rachev_ratio": rachev_result["rachev_ratio"],
            "d_ratio": d_ratio_result["d_ratio"],
            "romad": romad_result["romad"],
            "serenity_ratio": serenity_result["serenity_ratio"],
            "stability_index": stability_result["stability_index"],
            "recovery_factor": recovery_result["recovery_factor"],
            "volatility": var_result["volatility"] * 100 * np.sqrt(252),
            "risk_rating": self._assess_comprehensive_risk_rating(
                sharpe_result["sharpe_ratio"],
                beta_result["beta"],
                mdd_result["max_drawdown_pct"],
                stability_result["stability_index"],
                recovery_result["recovery_factor"],
            ),
        }

    def _assess_comprehensive_risk_rating(
        self, sharpe: float, beta: float, mdd: float, stability: float, recovery: float
    ) -> str:
        """Enhanced risk rating with new metrics"""
        score = 0

        # Sharpe
        if sharpe > 2.0:
            score += 3
        elif sharpe > 1.0:
            score += 2
        elif sharpe > 0.5:
            score += 1

        # Beta
        if 0.8 <= beta <= 1.2:
            score += 2
        elif 0.6 <= beta <= 1.4:
            score += 1

        # Drawdown
        if mdd > -10:
            score += 3
        elif mdd > -20:
            score += 2
        elif mdd > -30:
            score += 1

        # Stability Index (NEW)
        if stability > 0.95:
            score += 2
        elif stability > 0.85:
            score += 1

        # Recovery Factor (NEW)
        if recovery > 5:
            score += 2
        elif recovery > 3:
            score += 1

        if score >= 11:
            return "Exceptional"
        elif score >= 9:
            return "Excellent"
        elif score >= 7:
            return "Good"
        elif score >= 5:
            return "Moderate"
        else:
            return "Poor"


# ============================================================================
# TEST SCENARIOS
# ============================================================================


def generate_test_positions() -> List[PortfolioPosition]:
    """Generate 10 realistic portfolio positions"""
    np.random.seed(42)
    positions = []
    market_returns = np.random.normal(0.0004, 0.002, 252)

    # Position 1: Conservative Bonds
    bond_returns = np.random.normal(0.0002, 0.0005, 252)
    positions.append(
        PortfolioPosition(
            name="Conservative Bonds",
            initial_value=100000,
            current_value=105000,
            returns=bond_returns.tolist(),
            benchmark_returns=market_returns.tolist(),
        )
    )

    # Position 2: Aggressive Tech
    tech_returns = np.random.normal(0.0008, 0.025, 252)
    positions.append(
        PortfolioPosition(
            name="Aggressive Tech",
            initial_value=100000,
            current_value=120000,
            returns=tech_returns.tolist(),
            benchmark_returns=market_returns.tolist(),
        )
    )

    # Position 3: Balanced 60/40
    balanced_returns = np.random.normal(0.0004, 0.012, 252)
    positions.append(
        PortfolioPosition(
            name="Balanced 60/40",
            initial_value=100000,
            current_value=110000,
            returns=balanced_returns.tolist(),
            benchmark_returns=market_returns.tolist(),
        )
    )

    # Position 4: High Dividend Value
    dividend_returns = np.random.normal(0.0003, 0.008, 252)
    positions.append(
        PortfolioPosition(
            name="High Dividend Value",
            initial_value=100000,
            current_value=108000,
            returns=dividend_returns.tolist(),
            benchmark_returns=market_returns.tolist(),
        )
    )

    # Position 5: Emerging Markets
    em_returns = np.random.normal(0.0005, 0.03, 252)
    positions.append(
        PortfolioPosition(
            name="Emerging Markets",
            initial_value=100000,
            current_value=112000,
            returns=em_returns.tolist(),
            benchmark_returns=market_returns.tolist(),
        )
    )

    # Position 6: Gold/Commodities
    gold_returns = np.random.normal(0.0001, 0.015, 252)
    positions.append(
        PortfolioPosition(
            name="Gold & Commodities",
            initial_value=100000,
            current_value=102500,
            returns=gold_returns.tolist(),
            benchmark_returns=market_returns.tolist(),
        )
    )

    # Position 7: S&P 500 Index
    sp500_returns = np.random.normal(0.0004, 0.01, 252)
    positions.append(
        PortfolioPosition(
            name="S&P 500 Index",
            initial_value=100000,
            current_value=110000,
            returns=sp500_returns.tolist(),
            benchmark_returns=market_returns.tolist(),
        )
    )

    # Position 8: Crypto Portfolio
    crypto_returns = np.random.normal(0.001, 0.05, 252)
    positions.append(
        PortfolioPosition(
            name="Crypto Portfolio",
            initial_value=100000,
            current_value=125000,
            returns=crypto_returns.tolist(),
            benchmark_returns=market_returns.tolist(),
        )
    )

    # Position 9: REIT Portfolio
    reit_returns = np.random.normal(0.0003, 0.01, 252)
    positions.append(
        PortfolioPosition(
            name="REIT Portfolio",
            initial_value=100000,
            current_value=107500,
            returns=reit_returns.tolist(),
            benchmark_returns=market_returns.tolist(),
        )
    )

    # Position 10: Market Neutral
    neutral_returns = np.random.normal(0.0002, 0.004, 252)
    positions.append(
        PortfolioPosition(
            name="Market Neutral",
            initial_value=100000,
            current_value=105000,
            returns=neutral_returns.tolist(),
            benchmark_returns=market_returns.tolist(),
        )
    )

    return positions


def export_results_to_csv(
    results: List[Dict], filename: str = "extended_risk_analysis.csv"
):
    """Export results to CSV"""
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
    print("=" * 100)
    print("EXTENDED RISK ANALYSIS - 30 FORMULAS (20 ORIGINAL + 10 NEW)")
    print("=" * 100)
    print()

    positions = generate_test_positions()
    analyzer = ComprehensiveRiskAnalyzer()

    results = []
    print(
        f"{'Portfolio':<25} {'Return':>8} {'Sharpe':>8} {'Beta':>8} {'RoMaD':>8} {'Stability':>10} {'Rating':>12}"
    )
    print("-" * 105)

    for position in positions:
        result = analyzer.analyze_portfolio_complete(position)
        results.append(result)

        print(
            f"{result['position_name']:<25} {result['total_return_pct']:>7.2f}% "
            f"{result['sharpe_ratio']:>8.2f} {result['beta']:>8.2f} "
            f"{result['romad']:>8.2f} {result['stability_index']:>10.3f} "
            f"{result['risk_rating']:>12}"
        )

    print("-" * 105)
    print()

    # Summary
    print("COMPREHENSIVE SUMMARY (30 METRICS)")
    print(f"  Total Portfolios: {len(results)}")
    print(f"  Average Return: {np.mean([r['total_return_pct'] for r in results]):.2f}%")
    print(f"  Average Sharpe: {np.mean([r['sharpe_ratio'] for r in results]):.2f}")
    print(
        f"  Average Stability: {np.mean([r['stability_index'] for r in results]):.3f}"
    )
    print(f"  Average RoMaD: {np.mean([r['romad'] for r in results]):.2f}")
    print()
    best = max(results, key=lambda x: x["sharpe_ratio"])
    print(f"  Best Sharpe: {best['position_name']} ({best['sharpe_ratio']:.2f})")

    most_stable = max(results, key=lambda x: x["stability_index"])
    print(
        f"  Most Stable: {most_stable['position_name']} (R²={most_stable['stability_index']:.3f})"
    )

    best_recovery = max(results, key=lambda x: x["recovery_factor"])
    print(
        f"  Best Recovery: {best_recovery['position_name']} ({best_recovery['recovery_factor']:.2f}x)"
    )
    print()

export_results_to_csv(results)
print("\n✅ Extended risk analysis complete with 30 formulas!")
