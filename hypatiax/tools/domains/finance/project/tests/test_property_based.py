# tests/test_property_based.py
import math

import pytest
from hypothesis import given
from hypothesis import strategies as st
from uniswap_v2_formulas_extended import EPSILON, DeFiAdvancedCalculator

calc = DeFiAdvancedCalculator()


@given(st.integers(min_value=-887272, max_value=887272))
def test_uniswap_monotonicity(tick):
    # monotonic: price increases with tick (local check using tick and tick+1)
    p = calc.uniswap_v3_tick_to_price(tick)
    if tick < 887272:
        p_next = calc.uniswap_v3_tick_to_price(tick + 1)
        assert p_next >= p


@given(
    st.floats(min_value=1e-6, max_value=1e6),
    st.floats(min_value=0.0, max_value=1.0),
    st.floats(min_value=0.0, max_value=10.0),
)
def test_il_with_fees_consistency(price_ratio, fee_apr, t):
    res = calc.il_with_fees_net(price_ratio, fee_apr, t)
    # net_result_pct should be finite number
    assert math.isfinite(res["net_result_pct"])
    # time_years is echoed
    assert abs(res["time_years"] - t) < 1e-9


@given(st.floats(min_value=0.01, max_value=0.99))
def test_leverage_ratio_positive(ltv):
    lev = calc.leverage_ratio(ltv)
    assert lev >= 1.0
