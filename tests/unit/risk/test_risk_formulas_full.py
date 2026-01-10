# tests/test_risk_formulas_full.py
import math

import numpy as np
import pytest

from hypatiax.tools.domains.finance.risk.risk_formulas_30_full import (
    DAYS_PER_YEAR,
    EPSILON,
    ComprehensiveRiskAnalyzer,
    PortfolioPosition,
    RiskCalculator,
    generate_test_positions,
)


# fixtures
@pytest.fixture
def rng():
    np.random.seed(123)
    return np.random.default_rng(123)


# -------------------------
# Basic function smoke tests and edge cases
# -------------------------
def test_var_and_cvar_basic():
    r = np.array([-0.02, -0.01, 0.0, 0.01, 0.02])
    var = RiskCalculator.var_parametric(r, confidence=0.95)
    assert "var" in var
    cvar = RiskCalculator.cvar_historical(r, confidence=0.95)
    assert "cvar" in cvar


def test_sharpe_sortino_positive():
    r = np.array([0.001, 0.002, 0.0, -0.001, 0.003])
    sharpe = RiskCalculator.sharpe_ratio(r, 0.01)
    assert isinstance(sharpe["sharpe"], float)
    sortino = RiskCalculator.sortino_ratio(r, 0.0)
    assert isinstance(sortino["sortino"], float)


def test_beta_and_treynor():
    asset = np.array([0.01, 0.02, -0.01, 0.0, 0.03])
    market = np.array([0.005, 0.015, -0.005, 0.001, 0.02])
    b = RiskCalculator.beta(asset, market)
    t = RiskCalculator.treynor_ratio(asset, market, 0.01)
    assert abs(b["beta"]) >= 0.0
    assert "treynor" in t


def test_information_ratio_and_max_drawdown():
    r = np.random.normal(0.0005, 0.01, 252)
    m = np.random.normal(0.0004, 0.009, 252)
    ir = RiskCalculator.information_ratio(r, m)
    mdd = RiskCalculator.maximum_drawdown(r)
    assert "information_ratio" in ir
    assert 0.0 <= mdd["max_drawdown"] <= 2.0  # drawdown fraction


def test_cornish_fisher_and_es():
    r = np.random.normal(0.0, 0.02, 1000)
    cf = RiskCalculator.var_cornish_fisher(r, confidence=0.99)
    es = RiskCalculator.expected_shortfall_parametric(r, confidence=0.99)
    assert "var_cf" in cf and "es" in es


def test_var_long_horizon_methods():
    r = np.random.normal(0.0, 0.02, 252)
    v1 = RiskCalculator.var_long_horizon(r, days=10, method="sqrt")
    v2 = RiskCalculator.var_long_horizon(r, days=10, method="linear")
    assert v1["days"] == 10 and v2["days"] == 10


def test_modified_sharpe_ulcer_martin():
    r = np.random.normal(0.0003, 0.01, 252)
    ms = RiskCalculator.modified_sharpe(r, 0.01)
    ui = RiskCalculator.ulcer_index(r)
    mr = RiskCalculator.martin_ratio(r)
    assert "modified_sharpe" in ms
    assert "ulcer_index" in ui
    assert "martin_ratio" in mr


def test_drawdown_duration_gain_loss_upside():
    r = np.concatenate(
        [np.zeros(10), np.array([-0.02] * 5), np.zeros(10), np.array([-0.01] * 3)]
    )
    dd = RiskCalculator.drawdown_duration(r)
    gl = RiskCalculator.gain_loss_ratio(r)
    upr = RiskCalculator.upside_potential_ratio(r, mar=0.0)
    assert "avg_duration" in dd
    assert "gain_loss_ratio" in gl
    assert "upr" in upr


def test_sterling_burke_pain():
    r = np.random.normal(0.0004, 0.01, 252)
    st = RiskCalculator.sterling_ratio(r)
    bur = RiskCalculator.burke_ratio(r, 0.01)
    pain = RiskCalculator.pain_ratio(r)
    assert "sterling_ratio" in st
    assert "burke_ratio" in bur
    assert "pain_ratio" in pain


def test_tail_m2_prospect_rachev_d_romad_serenity_stability_recovery():
    r = np.random.normal(0.0005, 0.02, 252)
    t = RiskCalculator.tail_ratio(r)
    m2 = RiskCalculator.m_squared(r, 0.01, 15.0)
    p = RiskCalculator.prospect_ratio(r)
    ra = RiskCalculator.rachev_ratio(r)
    d = RiskCalculator.d_ratio(r)
    ro = RiskCalculator.romad(r)
    se = RiskCalculator.serenity_ratio(r, 0.01)
    si = RiskCalculator.stability_index(r)
    rec = RiskCalculator.recovery_factor(r, initial_capital=100000.0)
    # check keys exist and numeric types
    assert all(k in t for k in ["tail_ratio", "p95_pct"])
    assert "m_squared_pct" in m2
    assert "prospect_ratio" in p
    assert "rachev_ratio" in ra
    assert "d_ratio" in d
    assert "romad" in ro
    assert "serenity" in se
    assert "stability_index" in si
    assert "recovery_factor" in rec


# -------------------------
# Analyzer and integration tests
# -------------------------
def test_comprehensive_analyzer_runs():
    positions = generate_test_positions(seed=1)
    analyzer = ComprehensiveRiskAnalyzer()
    for pos in positions:
        report = analyzer.analyze(pos)
        # confirm a couple of expected fields present
        assert "position_name" in report
        assert "total_return_pct" in report
        assert "sharpe" in report


def test_edge_case_constant_returns():
    # zero volatility
    r = np.zeros(252)
    b = np.zeros(252)
    pos = PortfolioPosition(
        "ZeroVol", 100000.0, 105000.0, r.tolist(), b.tolist(), risk_free_rate=0.01
    )
    analyzer = ComprehensiveRiskAnalyzer()
    report = analyzer.analyze(pos)
    # Sharpe should be finite (division by EPSILON handled)
    assert math.isfinite(report["sharpe"])
    assert report["max_drawdown_pct"] == 0.0


def test_recovery_factor_infinite_when_no_mdd():
    r = np.ones(252) * 0.001  # continuous positive returns -> no drawdown
    rec = RiskCalculator.recovery_factor(r, initial_capital=100000.0)
    assert rec["recovery_factor"] == float("inf") or rec["recovery_factor"] > 1e6


# -------------------------
# Property-like checks
# -------------------------
def test_romad_monotonicity_with_mdd():
    r = np.random.normal(0.0005, 0.02, 252)
    base = RiskCalculator.romad(r)["romad"]
    # Add a catastrophic drop to increase MDD -> reduce RoMaD
    r2 = r.copy()
    r2[100] -= 0.5
    worse = RiskCalculator.romad(r2)["romad"]
    assert worse <= base + 1e-9
