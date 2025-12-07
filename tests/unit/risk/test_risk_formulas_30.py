# tests/test_risk_formulas_30.py
import math

import numpy as np
import pytest

from hypatiax.tools.domains.finance.risk.risk_formulas_30_full import (
    EPSILON,
    ComprehensiveRiskAnalyzer,
    PortfolioPosition,
)
from hypatiax.tools.domains.finance.risk.risk_metrics import (
    Asset,
    RiskBudget,
    RiskLevel,
    RiskMetrics,
    StressScenario,
    TimeHorizon,
)

# Create a small synthetic dataset used across tests
np.random.seed(0)
simple_returns = np.random.normal(0.0005, 0.01, 252)  # daily returns ~ 0.05% mean
market_returns = np.random.normal(0.0004, 0.009, 252)

# quick helper to ensure arrays
r = np.asarray(simple_returns)
b = np.asarray(market_returns)


def test_var_and_cvar_basic():
    v = RiskMetrics.var_parametric(r)
    assert "var" in v
    assert isinstance(v["var"], float)
    c = RiskMetrics.cvar_historical(r)
    assert "cvar" in c
    assert isinstance(c["cvar"], float)


def test_sharpe_sortino():
    s = RiskMetrics.sharpe_ratio(r, 0.01)
    assert isinstance(s["sharpe"], float)
    so = RiskMetrics.sortino_ratio(r, 0.0)
    assert "sortino" in so


def test_beta_treynor_information():
    be = RiskMetrics.beta(r, b)
    assert "beta" in be
    tr = RiskMetrics.treynor_ratio(r, b, 0.01)
    assert "treynor" in tr
    ir = RiskMetrics.information_ratio(r, b)
    assert "information_ratio" in ir


def test_max_drawdown_and_related():
    m = RiskMetrics.max_drawdown(r)
    assert "max_drawdown" in m
    assert m["max_drawdown"] >= 0.0
    cal = RiskMetrics.calmar_ratio(r)
    assert "calmar" in cal
    ui = RiskMetrics.ulcer_index(r)
    assert "ulcer_index" in ui


def test_var99_modified_sharpe():
    v99 = RiskMetrics.var_parametric_99(r)
    assert "var99" in v99
    ms = RiskMetrics.modified_sharpe(r, 0.01)
    assert "modified_sharpe" in ms
    assert isinstance(ms["skew"], float)


def test_ulcer_martin_drawdown_duration():
    ui = RiskMetrics.ulcer_index(r)
    mr = RiskMetrics.martin_ratio(r)
    ddur = RiskMetrics.drawdown_duration(r)
    assert "ulcer_index" in ui
    assert "martin" in mr
    assert "avg_drawdown_duration" in ddur


def test_kappa_gainloss_upr():
    k3 = RiskMetrics.kappa_3(r)
    gl = RiskMetrics.gain_loss_ratio(r)
    upr = RiskMetrics.upside_potential_ratio(r)
    assert "kappa3" in k3
    assert "gain_loss" in gl
    assert "upr" in upr


def test_sterling_pain():
    st = RiskMetrics.sterling_ratio(r)
    pr = RiskMetrics.pain_ratio(r)
    assert "sterling" in st
    assert "pain_ratio" in pr


def test_cdar_tail_m2_prospect_rachev():
    cd = RiskMetrics.cdar(r)
    tr = RiskMetrics.tail_ratio(r)
    m2 = RiskMetrics.m_squared(r, 0.01, 10.0)
    pr = RiskMetrics.prospect_ratio(r)
    rc = RiskMetrics.rachev_ratio(r)
    assert "cdar" in cd or "dar" in cd
    assert "tail_ratio" in tr
    assert "m2_pct" in m2
    assert "prospect" in pr
    assert "rachev" in rc


def test_d_ratio_romad_serenity_stability_recovery():
    d = RiskMetrics.d_ratio(r)
    rom = RiskMetrics.romad(r)
    ser = RiskMetrics.serenity_ratio(r, 0.01)
    st = RiskMetrics.stability_index(r)
    rec = RiskMetrics.recovery_factor(r, 100000.0)
    assert "d_ratio" in d
    assert "romad" in rom
    assert "serenity" in ser
    assert "stability" in st
    assert "recovery_factor" in rec


def test_comprehensive_analyzer_runs():
    pos = PortfolioPosition(
        name="Test",
        initial_value=100000.0,
        current_value=110000.0,
        returns=r.tolist(),
        benchmark_returns=b.tolist(),
        risk_free_rate=0.01,
        target_return=0.05,
    )
    an = ComprehensiveRiskAnalyzer()
    res = an.analyze(pos)
    # Ensure key metrics are present
    assert "sharpe" in res
    assert "max_drawdown" in res
    assert "cdar" in res
    assert "recovery_factor" in res


def test_edge_cases_small_arrays():
    tiny = np.array([0.01, -0.005])
    # beta length mismatch should raise
    with pytest.raises(ValueError):
        RiskMetrics.beta(tiny, np.array([0.01]))
    # functions should handle tiny arrays gracefully
    assert isinstance(RiskMetrics.var_parametric(tiny)["var"], float)
    assert isinstance(RiskMetrics.cvar_historical(tiny)["cvar"], float)


def test_no_div_by_zero_in_gain_loss():
    zero = np.array([-0.01, -0.02, -0.03])
    gl = RiskMetrics.gain_loss_ratio(zero)
    assert math.isfinite(gl["gain_loss"])
    assert gl["avg_win"] == 0.0


def test_recovery_factor_when_no_drawdown():
    # all positive returns -> small drawdown -> recovery factor finite
    pos_returns = np.full(252, 0.001)
    rec = RiskMetrics.recovery_factor(pos_returns, 1000.0)
    assert math.isfinite(rec["recovery_factor"])


# If you want to run these tests only:
# pytest -q tests/test_risk_formulas_30.py
