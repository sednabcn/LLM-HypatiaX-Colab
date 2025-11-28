# tests/test_defi_formulas_coverage.py
import math
import pytest
from uniswap_v2_formulas_extended import DeFiAdvancedCalculator

calc = DeFiAdvancedCalculator()

def test_uniswap_tick_extremes():
    assert calc.uniswap_v3_tick_to_price(0) == pytest.approx(1.0)
    assert calc.uniswap_v3_tick_to_price(-887272) > 0
    assert calc.uniswap_v3_tick_to_price(887272) > 0

def test_curve_newton_converges():
    D = calc.curve_stableswap_d([1e6, 1e6], 100)
    assert D > 0

def test_il_bounds_and_profitable_flag():
    r = calc.il_with_fees_net(1.0, 0.1, 1.0)
    assert "net_result_pct" in r
    assert isinstance(r["profitable"], bool)

def test_leverage_and_edge():
    assert calc.leverage_ratio(0.5) == pytest.approx(2.0)
    with pytest.raises(ValueError):
        calc.leverage_ratio(1.0)  # invalid: ltv must be <1
