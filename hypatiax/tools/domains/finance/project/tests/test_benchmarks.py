# tests/test_benchmarks.py
import pytest
from uniswap_v2_formulas_extended import DeFiAdvancedCalculator

calc = DeFiAdvancedCalculator()


@pytest.mark.benchmark
def test_benchmark_uniswap_tick(benchmark):
    # benchmark tick->price
    benchmark(calc.uniswap_v3_tick_to_price, 10000)


@pytest.mark.benchmark
def test_benchmark_curve_d(benchmark):
    benchmark(calc.curve_stableswap_d, [1e6, 1e6, 1e6], 200)
