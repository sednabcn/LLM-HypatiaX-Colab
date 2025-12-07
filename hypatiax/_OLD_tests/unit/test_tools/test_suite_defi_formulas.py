# test_defi_formulas.py
# ---------------------------------------------------------------------
# Test suite for uniswap_v2_formulas_extended.py
# Covers formulas 21–40, backtester, and scenario generator.
# ---------------------------------------------------------------------

import math

import pytest
from uniswap_v2_formulas_extended import DeFiAdvancedCalculator, DeFiBacktestAnalyzer, generate_defi_advanced_scenarios

calc = DeFiAdvancedCalculator()
analyzer = DeFiBacktestAnalyzer()


# ---------------------------------------------------------------------
# FORMULA 21 - Uniswap V3 Tick to Price
# ---------------------------------------------------------------------
def test_tick_to_price_basic():
    assert calc.uniswap_v3_tick_to_price(0) == pytest.approx(1.0)
    assert calc.uniswap_v3_tick_to_price(10000) > 1.0
    assert calc.uniswap_v3_tick_to_price(-10000) < 1.0


def test_tick_to_price_validation():
    with pytest.raises(ValueError):
        calc.uniswap_v3_tick_to_price(900000)  # out of valid range
    with pytest.raises(TypeError):
        calc.uniswap_v3_tick_to_price(3.5)  # must be int


# ---------------------------------------------------------------------
# FORMULA 22 - Constant Sum Output
# ---------------------------------------------------------------------
def test_constant_sum_output():
    out = calc.constant_sum_output(1000, 0.001)
    assert out == pytest.approx(999.0)


def test_constant_sum_invalid():
    with pytest.raises(ValueError):
        calc.constant_sum_output(-1, 0.003)
    with pytest.raises(ValueError):
        calc.constant_sum_output(100, 2.0)


# ---------------------------------------------------------------------
# FORMULA 23 - Curve StableSwap D
# ---------------------------------------------------------------------
def test_curve_stableswap_basic():
    D = calc.curve_stableswap_d([1e6, 1e6], 100)
    assert D > 0


def test_curve_stableswap_invalid():
    with pytest.raises(ValueError):
        calc.curve_stableswap_d([], 100)
    with pytest.raises(ValueError):
        calc.curve_stableswap_d([1e6], 100)


# ---------------------------------------------------------------------
# FORMULA 24 - Aave Variable Rate
# ---------------------------------------------------------------------
def test_aave_variable_rate():
    assert calc.aave_variable_rate(0.0) == pytest.approx(0.0)
    mid = calc.aave_variable_rate(0.8)
    assert mid > 0


def test_aave_rate_invalid():
    with pytest.raises(ValueError):
        calc.aave_variable_rate(-0.1)


# ---------------------------------------------------------------------
# FORMULA 25 - Compound APY with Rewards
# ---------------------------------------------------------------------
def test_compound_rewards():
    res = calc.compound_borrow_apy_with_rewards(
        borrow_apr=0.05, comp_per_block=0.01, comp_price=50, total_borrowed=1_000_000
    )
    assert "reward_apy" in res
    assert res["reward_apy"] >= 0


# ---------------------------------------------------------------------
# FORMULA 26 - Leverage Ratio
# ---------------------------------------------------------------------
def test_leverage_ratio():
    assert calc.leverage_ratio(0.5) == pytest.approx(2.0)
    assert calc.leverage_ratio(0.8) == pytest.approx(5.0)


def test_leverage_invalid():
    with pytest.raises(ValueError):
        calc.leverage_ratio(2)


# ---------------------------------------------------------------------
# FORMULA 27 - Protocol Revenue
# ---------------------------------------------------------------------
def test_protocol_revenue():
    rev = calc.protocol_revenue(1_000_000, 0.003, 0.5)
    assert rev == pytest.approx(1500.0)


# ---------------------------------------------------------------------
# FORMULA 28 - Maker Stability Fee
# ---------------------------------------------------------------------
def test_maker_fee():
    res = calc.maker_stability_fee(1000, 0.05, 1)
    assert res["total_debt"] > 1000
    assert res["fee_amount"] > 0


# ---------------------------------------------------------------------
# FORMULA 29 - Dilution Rate
# ---------------------------------------------------------------------
def test_dilution_rate():
    res = calc.dilution_rate(100_000, 1_000_000)
    assert res["dilution_pct"] == pytest.approx(10.0)


# ---------------------------------------------------------------------
# FORMULA 30 - Impermanent Loss With Fees
# ---------------------------------------------------------------------
def test_il_with_fees_net():
    res = calc.il_with_fees_net(1.5, 0.20, 1.0)
    assert "net_result_pct" in res


# ---------------------------------------------------------------------
# FORMULA 31 - Multi-hop Price Impact
# ---------------------------------------------------------------------
def test_multi_hop():
    imp = calc.multi_hop_impact([0.01, 0.02])
    assert imp > 0


def test_multi_hop_invalid():
    with pytest.raises(ValueError):
        calc.multi_hop_impact([])


# ---------------------------------------------------------------------
# FORMULA 32 - Black-Scholes Delta
# ---------------------------------------------------------------------
def test_black_scholes():
    res = calc.black_scholes_delta(spot=100, strike=100, rate=0.02, volatility=0.2, time_years=1)
    assert 0 < res["delta"] < 1


# ---------------------------------------------------------------------
# FORMULA 33 - Perpetual Basis
# ---------------------------------------------------------------------
def test_perpetual_basis():
    res = calc.perpetual_basis(105, 100, 1)
    assert res["premium_pct"] == pytest.approx(5.0)


# ---------------------------------------------------------------------
# FORMULA 34 - Flash Loan Net Profit
# ---------------------------------------------------------------------
def test_flashloan_profit():
    res = calc.flash_loan_net_profit(
        price_a=100,
        price_b=105,
        amount=10,
        fee_a=1,
        fee_b=1,
        gas_cost=5,
    )
    assert "net_profit" in res


# ---------------------------------------------------------------------
# FORMULA 35 - Vesting Cliff + Linear
# ---------------------------------------------------------------------
def test_vesting():
    res = calc.vesting_cliff_linear(total_tokens=1000, time_elapsed_days=200, cliff_days=100, vesting_days=300)
    assert res["vested_amount"] > 0


# ---------------------------------------------------------------------
# FORMULA 36 - Bancor Bonding Curve
# ---------------------------------------------------------------------
def test_bancor_bonding():
    res = calc.bancor_bonding_price(1000, 500, 0.5)
    assert res["price"] > 0


# ---------------------------------------------------------------------
# FORMULA 37 - Multi-asset Collateral
# ---------------------------------------------------------------------
def test_collateral_coverage():
    res = calc.collateral_coverage_multi(
        [{"value": 1000, "threshold": 0.8}, {"value": 2000, "threshold": 0.5}], total_debt=2000
    )
    assert "coverage_ratio" in res


# ---------------------------------------------------------------------
# FORMULA 38 - Yield Farming ROI
# ---------------------------------------------------------------------
def test_yield_farming():
    res = calc.yield_farming_roi(10000, 2000, 800, -300)
    assert res["roi_pct"] != 0


# ---------------------------------------------------------------------
# BACKTEST ANALYZER
# ---------------------------------------------------------------------
def test_backtest_range():
    prices = [1.0, 1.1, 0.9, 1.05]
    res = analyzer.backtest_uniswap_v3_range(
        initial_price=1.0, price_history=prices, lower_tick=-500, upper_tick=500, liquidity=10000
    )
    assert "in_range_pct" in res


def test_recursive_leverage():
    res = analyzer.simulate_recursive_leverage(1000, 0.7)
    assert res["actual_leverage"] > 1


def test_gas_threshold():
    res = analyzer.gas_profitability_threshold(20, 2000)
    assert "gas_cost_usd" in res
    assert res["gas_cost_usd"] > 0


# ---------------------------------------------------------------------
# SCENARIO GENERATOR
# ---------------------------------------------------------------------
def test_scenario_generation():
    scenarios = generate_defi_advanced_scenarios()
    assert isinstance(scenarios, list)
    assert len(scenarios) > 10
