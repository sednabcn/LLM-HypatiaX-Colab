#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
risk_formulas_30_full.py

Full, production-ready implementation of 30 risk/performance formulas.
Includes:
 - RiskCalculator: static methods for each formula (1..30)
 - ComprehensiveRiskAnalyzer: aggregator that returns a unified report
 - generate_test_positions(): synthetic data generator
 - export_results_to_csv()

Dependencies:
 - numpy
 - scipy
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import Dict, List, Any, Optional
import csv
import numpy as np
from scipy import stats
import math

EPSILON = 1e-12
DAYS_PER_YEAR = 252


@dataclass
class PortfolioPosition:
    name: str
    initial_value: float
    current_value: float
    returns: List[float]            # periodic returns (decimal), e.g., daily
    benchmark_returns: List[float]  # same frequency
    risk_free_rate: float = 0.03    # annual decimal
    target_return: float = 0.05     # annual decimal


class RiskCalculator:
    """Implements 30 risk & performance formulas as safe static methods."""

    # -----------------------
    # 1: VaR (parametric, one-period)
    # -----------------------
    @staticmethod
    def var_parametric(returns: np.ndarray, confidence: float = 0.95) -> Dict[str, Any]:
        mu = float(np.mean(returns))
        sigma = float(np.std(returns, ddof=0))
        # lower tail z for 1-confidence
        z = stats.norm.ppf(1.0 - confidence)
        var = mu + z * sigma
        return {"var": var, "var_pct": var * 100.0, "mu": mu, "sigma": sigma, "confidence": confidence}

    # -----------------------
    # 2: CVaR (historical expected shortfall)
    # -----------------------
    @staticmethod
    def cvar_historical(returns: np.ndarray, confidence: float = 0.95) -> Dict[str, Any]:
        sorted_r = np.sort(returns)
        cutoff = int(np.ceil((1.0 - confidence) * len(sorted_r)))
        if cutoff < 1:
            cutoff = 1
        tail = sorted_r[:cutoff]
        cvar = float(np.mean(tail)) if tail.size > 0 else float(sorted_r[0])
        return {"cvar": cvar, "cvar_pct": cvar * 100.0, "tail_count": tail.size, "confidence": confidence}

    # -----------------------
    # 3: Sharpe Ratio (annualized)
    # -----------------------
    @staticmethod
    def sharpe_ratio(returns: np.ndarray, risk_free_rate_annual: float) -> Dict[str, Any]:
        rf_period = risk_free_rate_annual / DAYS_PER_YEAR
        excess = returns - rf_period
        mean_excess = float(np.mean(excess))
        sigma = float(np.std(returns, ddof=0))
        sharpe_period = mean_excess / (sigma + EPSILON)
        sharpe_annual = sharpe_period * math.sqrt(DAYS_PER_YEAR)
        return {"sharpe": sharpe_annual, "mean_excess": mean_excess, "volatility": sigma}

    # -----------------------
    # 4: Sortino Ratio (annualized)
    # -----------------------
    @staticmethod
    def sortino_ratio(returns: np.ndarray, target_period_return: float) -> Dict[str, Any]:
        excess = returns - target_period_return
        downside = returns[returns < target_period_return]
        if downside.size > 0:
            downside_dev = float(np.std(downside, ddof=0))
        else:
            downside_dev = float(np.std(returns, ddof=0))
        mean_excess = float(np.mean(excess))
        sortino_period = mean_excess / (downside_dev + EPSILON)
        sortino_annual = sortino_period * math.sqrt(DAYS_PER_YEAR)
        return {"sortino": sortino_annual, "downside_dev": downside_dev, "mean_excess": mean_excess}

    # -----------------------
    # 5: Beta
    # -----------------------
    @staticmethod
    def beta(asset_returns: np.ndarray, market_returns: np.ndarray) -> Dict[str, Any]:
        if asset_returns.size != market_returns.size:
            raise ValueError("asset_returns and market_returns must be same length")
        cov = float(np.cov(asset_returns, market_returns, ddof=0)[0, 1])
        var_m = float(np.var(market_returns, ddof=0))
        b = cov / (var_m + EPSILON)
        return {"beta": b, "covariance": cov, "market_variance": var_m}

    # -----------------------
    # 6: Treynor Ratio (annualized)
    # -----------------------
    @staticmethod
    def treynor_ratio(asset_returns: np.ndarray, market_returns: np.ndarray, risk_free_rate_annual: float) -> Dict[str, Any]:
        rf_period = risk_free_rate_annual / DAYS_PER_YEAR
        beta_res = RiskCalculator.beta(asset_returns, market_returns)
        b = beta_res["beta"]
        mean_asset = float(np.mean(asset_returns))
        excess = mean_asset - rf_period
        treynor_period = excess / (b + EPSILON)
        treynor_annual = treynor_period * DAYS_PER_YEAR
        return {"treynor": treynor_annual, "beta": b, "excess_period": excess}

    # -----------------------
    # 7: Information Ratio (annualized)
    # -----------------------
    @staticmethod
    def information_ratio(asset_returns: np.ndarray, benchmark_returns: np.ndarray) -> Dict[str, Any]:
        active = asset_returns - benchmark_returns
        ar = float(np.mean(active))
        te = float(np.std(active, ddof=0))
        ir_period = ar / (te + EPSILON)
        ir_annual = ir_period * math.sqrt(DAYS_PER_YEAR)
        corr = float(np.corrcoef(asset_returns, benchmark_returns)[0, 1]) if asset_returns.size > 1 else 0.0
        return {"information_ratio": ir_annual, "active_return": ar, "tracking_error": te, "corr": corr}

    # -----------------------
    # 8: Maximum Drawdown (percent positive)
    # -----------------------
    @staticmethod
    def maximum_drawdown(returns: np.ndarray) -> Dict[str, Any]:
        wealth = np.cumprod(1.0 + returns)
        running_max = np.maximum.accumulate(wealth)
        drawdowns = (running_max - wealth) / (running_max + EPSILON)  # positive fraction
        max_dd = float(np.max(drawdowns))
        trough_idx = int(np.argmax(drawdowns))
        peak_idx = int(np.argmax(wealth[:trough_idx + 1])) if trough_idx > 0 else 0
        return {"max_drawdown": max_dd, "max_drawdown_pct": max_dd * 100.0, "peak_idx": peak_idx, "trough_idx": trough_idx, "drawdown_series": drawdowns}

    # -----------------------
    # 9: Modified VaR (Cornish-Fisher) - better tail adjustment
    # -----------------------
    @staticmethod
    def var_cornish_fisher(returns: np.ndarray, confidence: float = 0.95) -> Dict[str, Any]:
        mu = float(np.mean(returns))
        sigma = float(np.std(returns, ddof=0))
        skew = float(stats.skew(returns))
        kurt = float(stats.kurtosis(returns, fisher=True))
        # standard z
        z = stats.norm.ppf(1.0 - confidence)
        # Cornish-Fisher expansion for left-tail quantile (approx)
        z_cf = (z +
                (1/6.0) * (z**2 - 1) * skew +
                (1/24.0) * (z**3 - 3*z) * kurt -
                (1/36.0) * (2*z**3 - 5*z) * (skew**2))
        var_cf = mu + z_cf * sigma
        return {"var_cf": var_cf, "var_cf_pct": var_cf * 100.0, "skew": skew, "kurtosis": kurt}

    # -----------------------
    # 10: Expected Shortfall param + hist (here provide parametric ES)
    # -----------------------
    @staticmethod
    def expected_shortfall_parametric(returns: np.ndarray, confidence: float = 0.95) -> Dict[str, Any]:
        mu = float(np.mean(returns))
        sigma = float(np.std(returns, ddof=0))
        z = stats.norm.ppf(1.0 - confidence)
        pdf_z = stats.norm.pdf(z)
        es = mu + sigma * (pdf_z / (1.0 - confidence)) * (-1.0)
        return {"es": es, "es_pct": es * 100.0, "confidence": confidence}

    # -----------------------
    # 11: Long-horizon VaR scaling (square-root and linear options)
    # -----------------------
    @staticmethod
    def var_long_horizon(returns: np.ndarray, days: int = 10, confidence: float = 0.95, method: str = "sqrt") -> Dict[str, Any]:
        mu = float(np.mean(returns)) * days
        sigma = float(np.std(returns, ddof=0)) * (math.sqrt(days) if method == "sqrt" else days)
        z = stats.norm.ppf(1.0 - confidence)
        var = mu + z * sigma
        return {"var_long": var, "days": days, "method": method, "var_long_pct": var * 100.0}

    # -----------------------
    # 12: Modified Sharpe (adjust for skewness)
    # -----------------------
    @staticmethod
    def modified_sharpe(returns: np.ndarray, risk_free_rate_annual: float) -> Dict[str, Any]:
        rf_period = risk_free_rate_annual / DAYS_PER_YEAR
        mean_excess = float(np.mean(returns - rf_period))
        sigma = float(np.std(returns, ddof=0))
        skew = float(stats.skew(returns))
        denom = sigma * (1.0 + (skew / 6.0))
        mod_sharpe = (mean_excess / (denom + EPSILON)) * math.sqrt(DAYS_PER_YEAR)
        return {"modified_sharpe": mod_sharpe, "mean_excess": mean_excess, "sigma": sigma, "skew": skew}

    # -----------------------
    # 13: Ulcer Index (UI)
    # -----------------------
    @staticmethod
    def ulcer_index(returns: np.ndarray) -> Dict[str, Any]:
        wealth = np.cumprod(1.0 + returns)
        running_max = np.maximum.accumulate(wealth)
        drawdowns = (running_max - wealth) / (running_max + EPSILON)
        ui = math.sqrt(float(np.mean(drawdowns ** 2)))
        return {"ulcer_index": ui, "ulcer_index_pct": ui * 100.0}

    # -----------------------
    # 14: Martin Ratio = annual_return / Ulcer Index
    # -----------------------
    @staticmethod
    def martin_ratio(returns: np.ndarray) -> Dict[str, Any]:
        annual_return = float(np.mean(returns)) * DAYS_PER_YEAR
        ui = RiskCalculator.ulcer_index(returns)["ulcer_index"]
        martin = annual_return / (ui + EPSILON)
        return {"martin_ratio": martin, "annual_return": annual_return, "ulcer_index": ui}

    # -----------------------
    # 15: Drawdown Duration (average length of drawdowns)
    # -----------------------
    @staticmethod
    def drawdown_duration(returns: np.ndarray) -> Dict[str, Any]:
        wealth = np.cumprod(1.0 + returns)
        running_max = np.maximum.accumulate(wealth)
        below = wealth < running_max - EPSILON
        durations = []
        i = 0
        n = len(below)
        while i < n:
            if below[i]:
                j = i
                while j < n and below[j]:
                    j += 1
                durations.append(j - i)
                i = j
            else:
                i += 1
        avg_duration = float(np.mean(durations)) if durations else 0.0
        max_duration = int(max(durations)) if durations else 0
        return {"avg_duration": avg_duration, "max_duration": max_duration, "durations": durations}

    # -----------------------
    # 16: Gain-Loss Ratio
    # -----------------------
    @staticmethod
    def gain_loss_ratio(returns: np.ndarray) -> Dict[str, Any]:
        wins = returns[returns > 0]
        losses = -returns[returns < 0]  # positive magnitudes
        avg_win = float(np.mean(wins)) if wins.size > 0 else 0.0
        avg_loss = float(np.mean(losses)) if losses.size > 0 else 0.0
        ratio = (avg_win / (avg_loss + EPSILON)) if avg_loss > 0 else float("inf") if avg_win > 0 else 0.0
        return {"gain_loss_ratio": ratio, "avg_win": avg_win, "avg_loss": avg_loss}

    # -----------------------
    # 17: Upside Potential Ratio (UPR)
    # -----------------------
    @staticmethod
    def upside_potential_ratio(returns: np.ndarray, mar: float = 0.0) -> Dict[str, Any]:
        gains = returns[returns > mar] - mar
        downside = returns[returns < mar] - mar
        upside = float(np.sum(gains ** 1)) / (gains.size + EPSILON)
        downside_risk = math.sqrt(float(np.mean((np.minimum(0.0, downside) ** 2)))) if downside.size > 0 else EPSILON
        upr = upside / (downside_risk + EPSILON)
        return {"upr": upr, "upside": upside, "downside_risk": downside_risk, "mar": mar}

    # -----------------------
    # 18: Sterling Ratio = (annual_return - 0.10) / avg_drawdown_above_10pct
    # We'll implement using a 10% baseline as described
    # -----------------------
    @staticmethod
    def sterling_ratio(returns: np.ndarray, baseline: float = 0.10) -> Dict[str, Any]:
        annual_return = float(np.mean(returns)) * DAYS_PER_YEAR
        # compute average of drawdowns above baseline (in decimal)
        wealth = np.cumprod(1.0 + returns)
        running_max = np.maximum.accumulate(wealth)
        drawdowns = (running_max - wealth) / (running_max + EPSILON)
        # use drawdowns expressed in decimal (not percent)
        drawdowns_above = drawdowns[drawdowns > baseline]
        avgdd = float(np.mean(drawdowns_above)) if drawdowns_above.size > 0 else float(np.mean(drawdowns))
        sterling = (annual_return - baseline) / (avgdd + EPSILON)
        return {"sterling_ratio": sterling, "annual_return": annual_return, "avg_drawdown": avgdd}

    # -----------------------
    # 19: Burke Ratio = excess_return / sqrt(sum(dd^2))
    # -----------------------
    @staticmethod
    def burke_ratio(returns: np.ndarray, risk_free_rate_annual: float) -> Dict[str, Any]:
        rf_period = risk_free_rate_annual / DAYS_PER_YEAR
        excess = float(np.mean(returns - rf_period)) * DAYS_PER_YEAR
        wealth = np.cumprod(1.0 + returns)
        running_max = np.maximum.accumulate(wealth)
        drawdowns = (running_max - wealth) / (running_max + EPSILON)
        sqrt_sum_sq = math.sqrt(float(np.sum(drawdowns ** 2))) + EPSILON
        burke = excess / sqrt_sum_sq
        return {"burke_ratio": burke, "excess_return": excess, "sqrt_sum_sq_dd": sqrt_sum_sq}

    # -----------------------
    # 20: Pain Ratio = annual_return / Pain Index
    # Pain Index: average drawdown depth (root-mean-square of drawdowns)
    # -----------------------
    @staticmethod
    def pain_ratio(returns: np.ndarray) -> Dict[str, Any]:
        annual_return = float(np.mean(returns)) * DAYS_PER_YEAR
        wealth = np.cumprod(1.0 + returns)
        running_max = np.maximum.accumulate(wealth)
        drawdowns = (running_max - wealth) / (running_max + EPSILON)
        pain_index = math.sqrt(float(np.mean(drawdowns ** 2)))
        pain = annual_return / (pain_index + EPSILON)
        return {"pain_ratio": pain, "annual_return": annual_return, "pain_index": pain_index}

    # -----------------------
    # 21: CDaR (Conditional Drawdown at Risk)
    # -----------------------
    @staticmethod
    def cdar(returns: np.ndarray, confidence: float = 0.95) -> Dict[str, Any]:
        wealth = np.cumprod(1.0 + returns)
        running_max = np.maximum.accumulate(wealth)
        drawdowns = (running_max - wealth) / (running_max + EPSILON)
        dar = float(np.percentile(drawdowns, confidence * 100.0))
        tail = drawdowns[drawdowns >= dar]
        cdar = float(np.mean(tail)) if tail.size > 0 else dar
        return {"dar": dar, "cdar": cdar, "dar_pct": dar * 100.0, "cdar_pct": cdar * 100.0, "tail_count": tail.size}

    # -----------------------
    # 22: Tail Ratio
    # -----------------------
    @staticmethod
    def tail_ratio(returns: np.ndarray) -> Dict[str, Any]:
        p95 = float(np.percentile(returns, 95))
        p5 = float(np.percentile(returns, 5))
        denom = abs(p5) if abs(p5) > EPSILON else EPSILON
        tr = abs(p95) / denom
        return {"tail_ratio": tr, "p95_pct": p95 * 100.0, "p5_pct": p5 * 100.0}

    # -----------------------
    # 23: M^2 (Modigliani-Modigliani) - returns in percent units for benchmark volatility input
    # M^2 = Rf + Sharpe * sigma_benchmark
    # -----------------------
    @staticmethod
    def m_squared(returns: np.ndarray, risk_free_rate_annual: float, benchmark_vol_pct: float) -> Dict[str, Any]:
        sr = RiskCalculator.sharpe_ratio(returns, risk_free_rate_annual)["sharpe"]
        m2 = risk_free_rate_annual * 100.0 + float(sr) * benchmark_vol_pct
        return {"m_squared_pct": m2, "sharpe": sr, "benchmark_vol_pct": benchmark_vol_pct}

    # -----------------------
    # 24: Prospect Ratio (P_win * avg_win^2) / (P_loss * avg_loss^2)
    # -----------------------
    @staticmethod
    def prospect_ratio(returns: np.ndarray) -> Dict[str, Any]:
        wins = returns[returns > 0]
        losses = returns[returns < 0]
        p_win = float(wins.size) / returns.size if returns.size > 0 else 0.0
        p_loss = float(losses.size) / returns.size if returns.size > 0 else 0.0
        avg_win = float(np.mean(wins)) if wins.size > 0 else 0.0
        avg_loss = abs(float(np.mean(losses))) if losses.size > 0 else 0.0
        denom = (p_loss * (avg_loss ** 2)) if p_loss > 0 and avg_loss > 0 else EPSILON
        prospect = (p_win * (avg_win ** 2)) / denom
        return {"prospect_ratio": prospect, "p_win": p_win, "avg_win": avg_win, "avg_loss": avg_loss}

    # -----------------------
    # 25: Rachev Ratio (upper-tail CVaR / lower-tail CVaR)
    # -----------------------
    @staticmethod
    def rachev_ratio(returns: np.ndarray, alpha: float = 0.95) -> Dict[str, Any]:
        gains = returns[returns > 0]
        losses = returns[returns < 0]
        if gains.size > 0:
            top_cut = np.percentile(gains, alpha * 100.0)
            top_tail = gains[gains >= top_cut]
            cvar_gains = float(np.mean(top_tail)) if top_tail.size > 0 else top_cut
        else:
            cvar_gains = 0.0
        if losses.size > 0:
            low_cut = np.percentile(losses, (1.0 - alpha) * 100.0)
            low_tail = losses[losses <= low_cut]
            cvar_losses = abs(float(np.mean(low_tail))) if low_tail.size > 0 else abs(low_cut)
        else:
            cvar_losses = EPSILON
        rachev = float(cvar_gains / (cvar_losses + EPSILON))
        return {"rachev_ratio": rachev, "cvar_gains": cvar_gains, "cvar_losses": cvar_losses}

    # -----------------------
    # 26: D-Ratio (avg underwater / volatility)
    # -----------------------
    @staticmethod
    def d_ratio(returns: np.ndarray) -> Dict[str, Any]:
        wealth = np.cumprod(1.0 + returns)
        running_max = np.maximum.accumulate(wealth)
        underwater = (running_max - wealth) / (running_max + EPSILON)
        avg_under = float(np.mean(underwater))
        vol = float(np.std(returns, ddof=0))
        d = avg_under / (vol + EPSILON)
        return {"d_ratio": d, "avg_underwater": avg_under, "volatility": vol}

    # -----------------------
    # 27: RoMaD (Return over Maximum Drawdown)
    # -----------------------
    @staticmethod
    def romad(returns: np.ndarray) -> Dict[str, Any]:
        ann_return = float(np.mean(returns)) * DAYS_PER_YEAR
        mdd = RiskCalculator.maximum_drawdown(returns)["max_drawdown"]
        romad_value = float(ann_return / (mdd + EPSILON)) if mdd > 0 else float("inf")
        return {"romad": romad_value, "annual_return": ann_return, "max_drawdown": mdd}

    # -----------------------
    # 28: Serenity Ratio (excess return / avg underwater magnitude)
    # -----------------------
    @staticmethod
    def serenity_ratio(returns: np.ndarray, risk_free_rate_annual: float) -> Dict[str, Any]:
        ann_return = float(np.mean(returns)) * DAYS_PER_YEAR
        rf_pct = risk_free_rate_annual * 100.0
        excess = ann_return - rf_pct
        wealth = np.cumprod(1.0 + returns)
        running_max = np.maximum.accumulate(wealth)
        underwater = (running_max - wealth) / (running_max + EPSILON)
        under_periods = underwater[underwater > 0]
        avg_under = float(np.mean(under_periods)) if under_periods.size > 0 else EPSILON
        serenity = excess / (avg_under * 100.0 + EPSILON)
        return {"serenity": serenity, "excess_return_pct": excess, "avg_underwater_pct": avg_under * 100.0}

    # -----------------------
    # 29: Stability Index (R^2 of equity curve vs time)
    # -----------------------
    @staticmethod
    def stability_index(returns: np.ndarray) -> Dict[str, Any]:
        cum = np.cumprod(1.0 + returns)
        x = np.arange(cum.size)
        if cum.size < 2:
            return {"stability_index": 0.0, "r_squared": 0.0}
        slope, intercept, r_value, p_value, std_err = stats.linregress(x, cum)
        r2 = float(r_value ** 2)
        return {"stability_index": r2, "slope": slope, "r_squared": r2}

    # -----------------------
    # 30: Recovery Factor = net profit / max drawdown ($)
    # -----------------------
    @staticmethod
    def recovery_factor(returns: np.ndarray, initial_capital: float = 100000.0) -> Dict[str, Any]:
        wealth = np.cumprod(1.0 + returns) * initial_capital
        final = float(wealth[-1])
        net_profit = final - initial_capital
        mdd_pct = RiskCalculator.maximum_drawdown(returns)["max_drawdown"]
        mdd_dollars = initial_capital * mdd_pct
        recovery = float(net_profit / (mdd_dollars + EPSILON)) if mdd_dollars > 0 else float("inf")
        return {"recovery_factor": recovery, "net_profit": net_profit, "max_drawdown_dollars": mdd_dollars}


class ComprehensiveRiskAnalyzer:
    """Runs a subset or all formulas and returns a consolidated report."""

    def __init__(self, calculator: Optional[RiskCalculator] = None):
        self.calc = calculator or RiskCalculator()

    def analyze(self, pos: PortfolioPosition) -> Dict[str, Any]:
        r = np.asarray(pos.returns, dtype=float)
        b = np.asarray(pos.benchmark_returns, dtype=float)

        out: Dict[str, Any] = {}
        out.update(RiskCalculator.var_parametric(r))
        out.update(RiskCalculator.cvar_historical(r))
        out.update(RiskCalculator.sharpe_ratio(r, pos.risk_free_rate))
        out.update(RiskCalculator.sortino_ratio(r, pos.target_return / DAYS_PER_YEAR))
        out.update(RiskCalculator.beta(r, b))
        out.update(RiskCalculator.treynor_ratio(r, b, pos.risk_free_rate))
        out.update(RiskCalculator.information_ratio(r, b))
        out.update(RiskCalculator.maximum_drawdown(r))

        # add others
        out.update(RiskCalculator.var_cornish_fisher(r))
        out.update(RiskCalculator.expected_shortfall_parametric(r))
        out.update(RiskCalculator.var_long_horizon(r))
        out.update(RiskCalculator.modified_sharpe(r, pos.risk_free_rate))
        out.update(RiskCalculator.ulcer_index(r))
        out.update(RiskCalculator.martin_ratio(r))
        out.update(RiskCalculator.drawdown_duration(r))
        out.update(RiskCalculator.gain_loss_ratio(r))
        out.update(RiskCalculator.upside_potential_ratio(r))
        out.update(RiskCalculator.sterling_ratio(r))
        out.update(RiskCalculator.burke_ratio(r, pos.risk_free_rate))
        out.update(RiskCalculator.pain_ratio(r))

        out.update(RiskCalculator.cdar(r))
        out.update(RiskCalculator.tail_ratio(r))
        bench_vol_pct = float(np.std(b, ddof=0) * math.sqrt(DAYS_PER_YEAR) * 100.0) if b.size > 0 else 0.0
        out.update(RiskCalculator.m_squared(r, pos.risk_free_rate, bench_vol_pct))
        out.update(RiskCalculator.prospect_ratio(r))
        out.update(RiskCalculator.rachev_ratio(r))
        out.update(RiskCalculator.d_ratio(r))
        out.update(RiskCalculator.romad(r))
        out.update(RiskCalculator.serenity_ratio(r, pos.risk_free_rate))
        out.update(RiskCalculator.stability_index(r))
        out.update(RiskCalculator.recovery_factor(r, pos.initial_value))

        # summary
        out["position_name"] = pos.name
        total_return = (pos.current_value - pos.initial_value) / (pos.initial_value + EPSILON)
        out["total_return_pct"] = total_return * 100.0
        out["volatility_annual_pct"] = float(np.std(r, ddof=0)) * math.sqrt(DAYS_PER_YEAR) * 100.0
        return out


# -----------------------
# Helpers: synthetic generator & export
# -----------------------
def generate_test_positions(seed: int = 42) -> List[PortfolioPosition]:
    np.random.seed(seed)
    positions: List[PortfolioPosition] = []
    market = np.random.normal(0.0004, 0.002, DAYS_PER_YEAR)
    def add(name, mu, sigma, init, factor):
        r = np.random.normal(mu, sigma, DAYS_PER_YEAR)
        positions.append(PortfolioPosition(name=name, initial_value=init, current_value=init*factor, returns=r.tolist(), benchmark_returns=market.tolist()))
    add("Conservative Bonds", 0.0002, 0.0006, 100000.0, 1.05)
    add("Aggressive Tech", 0.0008, 0.025, 100000.0, 1.20)
    add("Balanced 60/40", 0.0004, 0.012, 100000.0, 1.10)
    add("Value Dividend", 0.0003, 0.008, 100000.0, 1.08)
    add("Emerging Mkts", 0.0006, 0.03, 100000.0, 1.12)
    add("Gold & Commodities", 0.0001, 0.015, 100000.0, 1.025)
    add("S&P 500 Index", 0.0004, 0.01, 100000.0, 1.10)
    add("Crypto Portfolio", 0.001, 0.05, 100000.0, 1.25)
    add("REIT Portfolio", 0.0003, 0.01, 100000.0, 1.075)
    add("Market Neutral", 0.0002, 0.004, 100000.0, 1.05)
    return positions


def export_results_to_csv(results: List[Dict[str, Any]], filename: str = "risk_analysis_full.csv") -> None:
    if not results:
        return
    keys = list(results[0].keys())
    with open(filename, "w", newline="", encoding="utf-8") as f:
        w = csv.DictWriter(f, fieldnames=keys)
        w.writeheader()
        for r in results:
            # stringify arrays
            row = {k: (v.tolist() if isinstance(v, np.ndarray) else v) for k, v in r.items()}
            w.writerow(row)

# If run as script, produce a short demo
if __name__ == "__main__":
    pos = generate_test_positions()
    analyzer = ComprehensiveRiskAnalyzer()
    results = [analyzer.analyze(p) for p in pos]
    for r in results[:3]:
        print(f"{r['position_name']}: total_return_pct={r['total_return_pct']:.2f}, sharpe={r['sharpe']:.2f}, max_dd_pct={r['max_drawdown_pct']:.2f}")
    export_results_to_csv(results)
