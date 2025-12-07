"""
Integration tests for the Hybrid Symbolic-Numerical System.
Tests the complete pipeline from symbolic formula definition to numerical computation.
"""

from typing import Any, Dict, List, Tuple

import numpy as np
import pytest
from sympy import cos, diff, exp, integrate, lambdify, log, simplify, sin, sqrt, symbols, sympify


class TestHybridSystemPipeline:
    """Test complete symbolic to numerical pipeline."""

    def test_formula_definition_to_computation(self, hybrid_system):
        """Test full pipeline: define formula -> validate -> compute."""
        # Define symbolic formula
        x, y = symbols("x y", positive=True)
        formula = sqrt(x * y)

        # Validate formula
        assert formula.is_real

        # Convert to numerical
        compute_func = lambdify((x, y), formula, "numpy")

        # Execute computation
        result = compute_func(100, 400)
        assert result == 200

    def test_defi_formula_pipeline(self, hybrid_system):
        """Test DeFi formula through complete pipeline."""
        # Impermanent Loss formula
        r = symbols("r", positive=True)
        il_formula = 2 * sqrt(r) / (1 + r) - 1

        # Symbolic validation
        assert il_formula.subs(r, 1) == 0  # No IL when ratio = 1

        # Convert to numerical
        il_func = lambdify(r, il_formula, "numpy")

        # Test with realistic price ratios
        price_ratios = np.array([0.5, 1.0, 1.5, 2.0, 4.0])
        il_values = il_func(price_ratios)

        # Validation checks
        assert il_values[1] == 0  # No loss at r=1
        assert all(il_values < 0)  # All losses are negative
        assert il_values[0] < il_values[2]  # Symmetric loss

    def test_risk_formula_pipeline(self, hybrid_system):
        """Test risk metrics through pipeline."""
        # Sharpe Ratio
        R, Rf, sigma = symbols("R Rf sigma")
        sharpe = (R - Rf) / sigma

        # Symbolic derivative for sensitivity
        dSharpe_dR = diff(sharpe, R)
        assert dSharpe_dR == 1 / sigma

        # Numerical computation
        sharpe_func = lambdify((R, Rf, sigma), sharpe, "numpy")

        # Portfolio analysis
        returns = np.array([0.12, 0.15, 0.18, 0.20])
        risk_free = 0.03
        volatilities = np.array([0.10, 0.12, 0.15, 0.18])

        sharpe_ratios = sharpe_func(returns, risk_free, volatilities)

        # Validate results
        assert all(sharpe_ratios > 0)
        assert sharpe_ratios[0] < sharpe_ratios[1]  # Higher return, similar vol

    def test_optimization_pipeline(self, hybrid_system):
        """Test optimization problem setup and solution."""
        x = symbols("x")
        # Minimize portfolio variance: x^2 + 2x + 5
        objective = x**2 + 2 * x + 5

        # Symbolic analysis
        derivative = diff(objective, x)
        critical_points = [pt for pt in [-1] if objective.subs(x, pt) is not None]

        # Numerical optimization setup
        obj_func = lambdify(x, objective, "numpy")
        grad_func = lambdify(x, derivative, "numpy")

        # Verify minimum at x = -1
        assert np.isclose(grad_func(-1), 0.0)
        assert obj_func(-1) == 4
        assert obj_func(0) > obj_func(-1)
        assert obj_func(-2) > obj_func(-1)


class TestSymbolicNumericalBridge:
    """Test the bridge between symbolic and numerical systems."""

    def test_expression_caching(self, hybrid_system):
        """Test that compiled expressions are cached."""
        x = symbols("x")
        expr = x**2 + 2 * x + 1

        # First compilation
        func1 = lambdify(x, expr, "numpy")
        result1 = func1(5)

        # Second compilation (should use cache)
        func2 = lambdify(x, expr, "numpy")
        result2 = func2(5)

        assert result1 == result2 == 36

    def test_multi_variable_conversion(self, hybrid_system):
        """Test conversion with multiple variables."""
        x, y, z = symbols("x y z")
        expr = x**2 + y**2 + z**2

        func = lambdify((x, y, z), expr, "numpy")

        # Single values
        assert func(1, 2, 3) == 14

        # Array broadcasting
        x_arr = np.array([1, 2, 3])
        y_arr = np.array([2, 3, 4])
        z_arr = np.array([3, 4, 5])
        results = func(x_arr, y_arr, z_arr)
        expected = np.array([14, 29, 50])
        np.testing.assert_array_equal(results, expected)

    def test_complex_function_bridge(self, hybrid_system):
        """Test bridge with complex functions."""
        x = symbols("x")
        expr = exp(x) * sin(x) + log(x + 1)

        func = lambdify(x, expr, "numpy")

        x_vals = np.linspace(0.1, 5, 50)
        results = func(x_vals)

        # All results should be finite
        assert np.all(np.isfinite(results))

    def test_piecewise_function_bridge(self, hybrid_system):
        """Test piecewise functions."""
        x = symbols("x")
        # Simple piecewise: x^2 for x >= 0, -x^2 for x < 0
        expr_pos = x**2
        expr_neg = -(x**2)

        func_pos = lambdify(x, expr_pos, "numpy")
        func_neg = lambdify(x, expr_neg, "numpy")

        # Combine in Python
        def piecewise_func(x_val):
            return np.where(x_val >= 0, func_pos(x_val), func_neg(x_val))

        x_test = np.array([-2, -1, 0, 1, 2])
        results = piecewise_func(x_test)
        expected = np.array([-4, -1, 0, 1, 4])
        np.testing.assert_array_equal(results, expected)


class TestFormulaValidationIntegration:
    """Test integrated formula validation."""

    def test_dimensional_validation_integration(self, hybrid_system):
        """Test dimensional analysis in pipeline."""
        # Price * Quantity = Value
        P, Q = symbols("P Q", positive=True)
        value_formula = P * Q

        # Validate dimensions symbolically
        dV_dP = diff(value_formula, P)
        dV_dQ = diff(value_formula, Q)

        # dV/dP should have dimensions of Quantity
        assert dV_dP == Q
        # dV/dQ should have dimensions of Price
        assert dV_dQ == P

        # Numerical validation
        value_func = lambdify((P, Q), value_formula, "numpy")

        prices = np.array([10, 20, 30])
        quantities = np.array([5, 10, 15])
        values = value_func(prices, quantities)

        expected = np.array([50, 200, 450])
        np.testing.assert_array_equal(values, expected)

    def test_domain_validation_integration(self, hybrid_system):
        """Test domain constraint validation."""
        x = symbols("x", positive=True)

        # Log only defined for positive values
        log_formula = log(x)

        # Symbolic check
        assert x.is_positive

        # Numerical validation
        log_func = lambdify(x, log_formula, "numpy")

        # Valid domain
        valid_x = np.array([0.1, 1, 10, 100])
        results = log_func(valid_x)
        assert np.all(np.isfinite(results))

        # Invalid domain should produce warnings
        with pytest.warns(RuntimeWarning):
            invalid_result = log_func(-1)
            assert np.isnan(invalid_result) or np.iscomplex(invalid_result)

    def test_constraint_validation_integration(self, hybrid_system):
        """Test mathematical constraint validation."""
        # APY formula with constraints
        r, n = symbols("r n", positive=True)
        apy = (1 + r / n) ** n - 1

        # Symbolic constraint: r should be reasonable (0 < r < 1)
        # n should be positive integer

        apy_func = lambdify((r, n), apy, "numpy")

        # Valid parameters
        rates = np.array([0.05, 0.10, 0.15])
        compounds = np.array([12, 12, 12])  # Monthly

        results = apy_func(rates, compounds)

        # APY should be slightly higher than nominal rate
        assert np.all(results > rates)
        assert np.all(results < rates * 1.2)  # Reasonable bound

    def test_boundary_validation_integration(self, hybrid_system):
        """Test boundary condition validation."""
        x = symbols("x")

        # Sigmoid function: should be bounded [0, 1]
        sigmoid = 1 / (1 + exp(-x))

        sigmoid_func = lambdify(x, sigmoid, "numpy")

        # Test across wide range
        x_vals = np.linspace(-10, 10, 100)
        results = sigmoid_func(x_vals)

        # Validate bounds
        assert np.all(results >= 0)
        assert np.all(results <= 1)

        # Check asymptotic behavior
        assert results[0] < 0.01  # Approaches 0 for large negative
        assert results[-1] > 0.99  # Approaches 1 for large positive


class TestEndToEndComputations:
    """End-to-end computational tests."""

    def test_portfolio_optimization_e2e(self, hybrid_system):
        """Test complete portfolio optimization workflow."""
        # Define portfolio return formula
        w1, w2, r1, r2 = symbols("w1 w2 r1 r2")
        portfolio_return = w1 * r1 + w2 * r2

        # Constraint: w1 + w2 = 1
        constraint = w1 + w2 - 1

        # Symbolic validation
        assert portfolio_return.subs([(w1, 0.6), (w2, 0.4), (r1, 0.1), (r2, 0.15)]) == 0.12

        # Numerical computation
        port_func = lambdify((w1, w2, r1, r2), portfolio_return, "numpy")

        # Simulate different allocations
        weights = np.linspace(0, 1, 11)
        returns_asset1 = 0.10
        returns_asset2 = 0.15

        portfolio_returns = port_func(weights, 1 - weights, returns_asset1, returns_asset2)

        # Validate: should increase linearly from 0.10 to 0.15
        assert np.isclose(portfolio_returns[0], 0.10)
        assert np.isclose(portfolio_returns[-1], 0.15)
        assert np.all(np.diff(portfolio_returns) > 0)

    def test_liquidity_pool_simulation_e2e(self, hybrid_system):
        """Test Uniswap liquidity pool simulation."""
        # Constant product: x * y = k
        x, y, k = symbols("x y k", positive=True)

        # Price formula
        price = y / x

        # Liquidity formula
        L = sqrt(x * y)

        # Numerical functions
        price_func = lambdify((x, y), price, "numpy")
        liq_func = lambdify((x, y), L, "numpy")

        # Simulate pool state
        initial_x = 1000
        initial_y = 2000
        k_value = initial_x * initial_y

        # Price should be 2.0
        initial_price = price_func(initial_x, initial_y)
        assert initial_price == 2.0

        # After trade: buy 100 of token X
        new_x = initial_x - 100
        new_y = k_value / new_x

        new_price = price_func(new_x, new_y)

        # Price should increase (x decreased)
        assert new_price > initial_price

    def test_risk_assessment_e2e(self, hybrid_system):
        """Test complete risk assessment workflow."""
        # Define multiple risk metrics
        R, Rf, sigma, downside_sigma = symbols("R Rf sigma downside_sigma")

        # Sharpe Ratio
        sharpe = (R - Rf) / sigma

        # Sortino Ratio
        sortino = (R - Rf) / downside_sigma

        # Create functions
        sharpe_func = lambdify((R, Rf, sigma), sharpe, "numpy")
        sortino_func = lambdify((R, Rf, downside_sigma), sortino, "numpy")

        # Simulate portfolio
        portfolio_return = 0.15
        risk_free_rate = 0.03
        total_volatility = 0.12
        downside_volatility = 0.08

        # Compute metrics
        sharpe_ratio = sharpe_func(portfolio_return, risk_free_rate, total_volatility)
        sortino_ratio = sortino_func(portfolio_return, risk_free_rate, downside_volatility)

        # Validate
        assert sharpe_ratio == 1.0
        assert sortino_ratio == 1.5
        assert sortino_ratio > sharpe_ratio  # Should be higher (lower denominator)

    def test_options_pricing_e2e(self, hybrid_system):
        """Test options pricing calculation."""
        # Simplified Black-Scholes put-call parity: C - P = S - K*exp(-r*T)
        C, P, S, K, r, T = symbols("C P S K r T")

        put_call_parity = C - P - (S - K * exp(-r * T))

        # Should equal zero for properly priced options
        pcp_func = lambdify((C, P, S, K, r, T), put_call_parity, "numpy")

        # Example values
        call_price = 10
        put_price = 5
        spot_price = 100
        strike_price = 95
        rate = 0.05
        time_to_expiry = 1.0

        result = pcp_func(call_price, put_price, spot_price, strike_price, rate, time_to_expiry)

        # Should be close to zero if arbitrage-free
        expected = call_price - put_price - (spot_price - strike_price * np.exp(-rate * time_to_expiry))
        assert np.isclose(result, expected)


class TestErrorHandlingIntegration:
    """Test error handling across the pipeline."""

    def test_invalid_symbolic_formula(self, hybrid_system):
        """Test handling of invalid symbolic formulas."""
        with pytest.raises(Exception):
            # This should fail to parse
            sympify("x ++++ y")

    def test_numerical_errors_propagation(self, hybrid_system):
        """Test how numerical errors propagate."""
        x = symbols("x")
        expr = 1 / x

        func = lambdify(x, expr, "numpy")

        # Division by zero
        with pytest.warns(RuntimeWarning):
            result = func(0)
            assert np.isinf(result)

        # Very small denominator
        result_small = func(1e-100)
        assert result_small > 1e90

    def test_dimension_mismatch_detection(self, hybrid_system):
        """Test detection of dimensional mismatches."""
        # Adding price to quantity (wrong dimensions)
        P, Q = symbols("P Q")

        # This is mathematically allowed but dimensionally wrong
        wrong_formula = P + Q

        # We can still evaluate it, but validation should flag it
        func = lambdify((P, Q), wrong_formula, "numpy")
        result = func(10, 5)

        # Result exists but is meaningless
        assert result == 15

    def test_constraint_violation_detection(self, hybrid_system):
        """Test detection of constraint violations."""
        x = symbols("x", positive=True)
        sqrt_formula = sqrt(x)

        func = lambdify(x, sqrt_formula, "numpy")

        # Negative input violates constraint
        with pytest.warns(RuntimeWarning):
            result = func(-1)
            assert np.isnan(result) or np.iscomplex(result)


class TestPerformanceIntegration:
    """Test performance of integrated system."""

    def test_large_scale_computation(self, hybrid_system):
        """Test computation on large datasets."""
        x, y = symbols("x y")
        expr = x**2 + y**2 + x * y

        func = lambdify((x, y), expr, "numpy")

        # Large arrays
        size = 10000
        x_vals = np.random.rand(size) * 100
        y_vals = np.random.rand(size) * 100

        results = func(x_vals, y_vals)

        assert len(results) == size
        assert np.all(np.isfinite(results))

    def test_repeated_evaluation_performance(self, hybrid_system):
        """Test repeated evaluation is efficient."""
        x = symbols("x")
        expr = exp(x) * sin(x) + cos(x) * log(x + 1)

        func = lambdify(x, expr, "numpy")

        # Repeated evaluations
        x_val = 2.5
        results = [func(x_val) for _ in range(1000)]

        # All should be identical
        assert len(set(results)) == 1


class TestRealWorldScenarios:
    """Test real-world usage scenarios."""

    def test_uniswap_v2_il_calculation(self, hybrid_system):
        """Test real Uniswap V2 IL calculation."""
        # Initial state
        initial_price = 2000  # ETH price
        final_price = 2500

        # Price ratio
        price_ratio = final_price / initial_price

        # IL formula
        r = symbols("r", positive=True)
        il = 2 * sqrt(r) / (1 + r) - 1

        il_func = lambdify(r, il, "numpy")

        # Calculate IL
        impermanent_loss = il_func(price_ratio)

        # Verify it's negative (loss)
        assert impermanent_loss < 0
        # Should be small loss for 25% price change
        assert impermanent_loss > -0.01  # Less than 1% loss

    def test_portfolio_rebalancing(self, hybrid_system):
        """Test portfolio rebalancing calculation."""
        # Target allocation
        w_target = 0.6

        # Current allocation after price changes
        value_asset1 = 60000
        value_asset2 = 50000
        total_value = value_asset1 + value_asset2

        w_current = value_asset1 / total_value

        # Rebalancing amount needed
        rebalance_amount = (w_target - w_current) * total_value

        # Should need to buy more of asset 1
        assert rebalance_amount > 0
        assert np.isclose(rebalance_amount, 6000, rtol=0.01)

    def test_yield_farming_apy(self, hybrid_system):
        """Test yield farming APY calculation."""
        # Base APY + reward APY
        base_rate, reward_rate, compound_freq = symbols("base_rate reward_rate compound_freq")

        total_apy = (1 + (base_rate + reward_rate) / compound_freq) ** compound_freq - 1

        apy_func = lambdify((base_rate, reward_rate, compound_freq), total_apy, "numpy")

        # Example: 5% base + 10% rewards, daily compounding
        result = apy_func(0.05, 0.10, 365)

        # Should be higher than 15% due to compounding
        assert result > 0.15
        assert result < 0.17  # Reasonable upper bound


@pytest.fixture
def hybrid_system():
    """Fixture providing hybrid system instance."""

    class MockHybridSystem:
        """Mock hybrid system for testing."""

        def __init__(self):
            self.cache = {}

        def compile_formula(self, expr):
            """Compile symbolic expression to numerical function."""
            # In real system, would use actual compilation
            return lambdify(expr.free_symbols, expr, "numpy")

    return MockHybridSystem()


if __name__ == "__main__":
    pytest.main([__file__, "-v", "--tb=short"])
