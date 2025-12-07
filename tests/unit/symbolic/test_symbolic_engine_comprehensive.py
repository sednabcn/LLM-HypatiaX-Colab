"""
Comprehensive tests for the Symbolic Engine module.
Tests symbolic computation, validation, and integration with numerical methods.
"""

from typing import Any, Dict, List

import numpy as np
import pytest
from sympy import (
    cos,
    diff,
    exp,
    expand,
    factor,
    integrate,
    lambdify,
    log,
    pi,
    simplify,
    sin,
    solve,
    sqrt,
    symbols,
    sympify,
    tan,
)


class TestSymbolicEngineCore:
    """Core functionality tests for symbolic engine."""

    def test_symbol_creation(self, symbolic_engine):
        """Test creation of symbolic variables."""
        x, y, z = symbols("x y z")
        assert x.is_symbol
        assert y.is_symbol
        assert z.is_symbol

    def test_multiple_symbol_creation(self, symbolic_engine):
        """Test creating multiple symbols at once."""
        vars = symbols("a b c d e")
        assert len(vars) == 5
        assert all(v.is_symbol for v in vars)

    def test_expression_parsing(self, symbolic_engine):
        """Test parsing of mathematical expressions."""
        expr_str = "x**2 + 2*x + 1"
        expr = sympify(expr_str)
        x = symbols("x")
        assert expr.subs(x, 0) == 1
        assert expr.subs(x, 1) == 4
        assert expr.subs(x, -1) == 0

    def test_complex_expression_parsing(self, symbolic_engine):
        """Test parsing complex expressions."""
        expr_str = "(x**2 + y**2) / (x + y)"
        expr = sympify(expr_str)
        x, y = symbols("x y")
        result = expr.subs([(x, 3), (y, 4)])
        assert result == 25 / 7

    def test_expression_simplification(self, symbolic_engine):
        """Test symbolic simplification."""
        x = symbols("x")
        expr = (x**2 - 1) / (x - 1)
        simplified = simplify(expr)
        assert simplified.subs(x, 2) == 3

    def test_trigonometric_simplification(self, symbolic_engine):
        """Test trig identity simplification."""
        x = symbols("x")
        expr = sin(x) ** 2 + cos(x) ** 2
        simplified = simplify(expr)
        assert simplified == 1

    def test_derivative_computation(self, symbolic_engine):
        """Test symbolic differentiation."""
        x = symbols("x")
        expr = x**3 + 2 * x**2 + x
        derivative = diff(expr, x)
        assert derivative.subs(x, 0) == 1
        assert derivative.subs(x, 1) == 7

    def test_partial_derivatives(self, symbolic_engine):
        """Test partial differentiation."""
        x, y = symbols("x y")
        expr = x**2 * y + x * y**2
        dx = diff(expr, x)
        dy = diff(expr, y)
        assert dx.subs([(x, 1), (y, 1)]) == 3
        assert dy.subs([(x, 1), (y, 1)]) == 3

    def test_integration(self, symbolic_engine):
        """Test symbolic integration."""
        x = symbols("x")
        expr = x**2
        integral = integrate(expr, x)
        assert diff(integral, x) == expr

    def test_definite_integration(self, symbolic_engine):
        """Test definite integration."""
        x = symbols("x")
        expr = x**2
        result = integrate(expr, (x, 0, 1))
        assert result == sympify("1/3")


class TestSymbolicToNumerical:
    """Tests for converting symbolic to numerical expressions."""

    def test_lambdify_single_variable(self, symbolic_engine):
        """Test lambdify with single variable."""
        x = symbols("x")
        expr = x**2 + 3 * x + 2
        f = lambdify(x, expr, "numpy")

        result = f(2)
        assert result == 12

        x_vals = np.array([0, 1, 2, 3])
        results = f(x_vals)
        expected = np.array([2, 6, 12, 20])
        np.testing.assert_array_equal(results, expected)

    def test_lambdify_multiple_variables(self, symbolic_engine):
        """Test lambdify with multiple variables."""
        x, y = symbols("x y")
        expr = x**2 + y**2
        f = lambdify((x, y), expr, "numpy")

        assert f(3, 4) == 25
        assert f(0, 0) == 0

    def test_lambdify_with_numpy_functions(self, symbolic_engine):
        """Test lambdify with special functions."""
        x = symbols("x")
        expr = sin(x) + cos(x)
        f = lambdify(x, expr, "numpy")

        result = f(0)
        assert np.isclose(result, 1.0)

        result = f(np.pi / 2)
        assert np.isclose(result, 1.0)

    def test_lambdify_exponential(self, symbolic_engine):
        """Test lambdify with exponential functions."""
        x = symbols("x")
        expr = exp(x)
        f = lambdify(x, expr, "numpy")

        assert np.isclose(f(0), 1.0)
        assert np.isclose(f(1), np.e)

    def test_lambdify_logarithm(self, symbolic_engine):
        """Test lambdify with logarithmic functions."""
        x = symbols("x", positive=True)
        expr = log(x)
        f = lambdify(x, expr, "numpy")

        assert np.isclose(f(1), 0.0)
        assert np.isclose(f(np.e), 1.0)

    def test_vectorized_operations(self, symbolic_engine):
        """Test vectorized operations on arrays."""
        x, y = symbols("x y")
        expr = x * y + x**2
        f = lambdify((x, y), expr, "numpy")

        x_arr = np.array([1, 2, 3])
        y_arr = np.array([4, 5, 6])
        results = f(x_arr, y_arr)
        expected = np.array([5, 14, 27])
        np.testing.assert_array_equal(results, expected)


class TestDeFiFormulas:
    """Tests for DeFi-specific formula handling."""

    def test_impermanent_loss_formula(self, symbolic_engine):
        """Test impermanent loss calculation."""
        r = symbols("r", positive=True)
        il_formula = 2 * sqrt(r) / (1 + r) - 1

        il_func = lambdify(r, il_formula, "numpy")

        assert np.isclose(il_func(1), 0.0)

        expected_il = 2 * np.sqrt(2) / 3 - 1
        assert np.isclose(il_func(2), expected_il)

    def test_impermanent_loss_extreme_cases(self, symbolic_engine):
        """Test IL at extreme price changes."""
        r = symbols("r", positive=True)
        il_formula = 2 * sqrt(r) / (1 + r) - 1
        il_func = lambdify(r, il_formula, "numpy")

        # 4x price increase
        il_4x = il_func(4)
        assert il_4x < 0  # Loss
        assert il_4x > -0.1  # Less than 10% loss

    def test_apy_formula(self, symbolic_engine):
        """Test APY calculation formula."""
        r, n = symbols("r n", positive=True)
        apy_formula = (1 + r / n) ** n - 1

        apy_func = lambdify((r, n), apy_formula, "numpy")

        result = apy_func(0.1, 365)
        expected = (1 + 0.1 / 365) ** 365 - 1
        assert np.isclose(result, expected)

    def test_continuous_compounding(self, symbolic_engine):
        """Test continuous compounding limit."""
        r, n = symbols("r n", positive=True)
        apy_formula = (1 + r / n) ** n - 1
        apy_func = lambdify((r, n), apy_formula, "numpy")

        # As n increases, should approach e^r - 1
        result_large_n = apy_func(0.1, 10000)
        continuous = np.exp(0.1) - 1
        assert np.isclose(result_large_n, continuous, rtol=1e-4)

    def test_liquidity_formula(self, symbolic_engine):
        """Test liquidity calculation."""
        x, y = symbols("x y", positive=True)
        liquidity = sqrt(x * y)

        liq_func = lambdify((x, y), liquidity, "numpy")

        assert liq_func(100, 100) == 100
        assert liq_func(100, 400) == 200

    def test_constant_product_formula(self, symbolic_engine):
        """Test constant product AMM formula."""
        x, y, k = symbols("x y k", positive=True)
        product = x * y - k

        # Solve for y given x and k
        y_solution = solve(product, y)[0]
        assert y_solution == k / x

    def test_price_impact_formula(self, symbolic_engine):
        """Test price impact calculation."""
        dx, x, y = symbols("dx x y", positive=True)
        # Price impact = dy/dx where x*y = k
        dy = y * dx / (x + dx)
        price_impact = dy / dx

        impact_func = lambdify((dx, x, y), price_impact, "numpy")

        # Small trade should have small impact
        small_impact = impact_func(1, 1000, 1000)
        assert 0 < small_impact < 1


class TestRiskFormulas:
    """Tests for risk metric formulas."""

    def test_sharpe_ratio_formula(self, symbolic_engine):
        """Test Sharpe ratio calculation."""
        R, Rf, sigma = symbols("R Rf sigma")
        sharpe = (R - Rf) / sigma

        sharpe_func = lambdify((R, Rf, sigma), sharpe, "numpy")

        assert sharpe_func(0.15, 0.05, 0.10) == 1.0
        assert sharpe_func(0.10, 0.05, 0.10) == 0.5

    def test_sharpe_ratio_negative(self, symbolic_engine):
        """Test Sharpe ratio with negative excess return."""
        R, Rf, sigma = symbols("R Rf sigma")
        sharpe = (R - Rf) / sigma
        sharpe_func = lambdify((R, Rf, sigma), sharpe, "numpy")

        result = sharpe_func(0.03, 0.05, 0.10)
        assert result == -0.2

    def test_var_formula(self, symbolic_engine):
        """Test Value at Risk formula."""
        mu, z, sigma = symbols("mu z sigma")
        var = mu - z * sigma

        var_func = lambdify((mu, z, sigma), var, "numpy")

        result = var_func(0.0, 1.645, 1.0)
        assert np.isclose(result, -1.645)

    def test_cvar_formula(self, symbolic_engine):
        """Test Conditional Value at Risk."""
        mu, z, sigma = symbols("mu z sigma")
        # Simplified CVaR for normal distribution
        cvar = mu - sigma * (exp(-(z**2) / 2) / (sqrt(2 * pi) * (1 - 0.95)))

        cvar_func = lambdify((mu, z, sigma), cvar, "numpy")
        result = cvar_func(0, 1.645, 1)
        assert result < -1.645  # CVaR should be worse than VaR

    def test_volatility_formula(self, symbolic_engine):
        """Test annualized volatility."""
        daily_vol, days = symbols("daily_vol days", positive=True)
        annual_vol = daily_vol * sqrt(days)

        vol_func = lambdify((daily_vol, days), annual_vol, "numpy")

        # Daily vol of 1% over 252 trading days
        result = vol_func(0.01, 252)
        expected = 0.01 * np.sqrt(252)
        assert np.isclose(result, expected)

    def test_maximum_drawdown_formula(self, symbolic_engine):
        """Test maximum drawdown calculation."""
        peak, trough = symbols("peak trough", positive=True)
        mdd = (trough - peak) / peak

        mdd_func = lambdify((peak, trough), mdd, "numpy")

        assert mdd_func(100, 80) == -0.2
        assert mdd_func(100, 50) == -0.5

    def test_sortino_ratio_formula(self, symbolic_engine):
        """Test Sortino ratio calculation."""
        R, Rf, downside_dev = symbols("R Rf downside_dev")
        sortino = (R - Rf) / downside_dev

        sortino_func = lambdify((R, Rf, downside_dev), sortino, "numpy")

        result = sortino_func(0.12, 0.02, 0.08)
        assert result == 1.25


class TestFormulaValidation:
    """Tests for formula validation and consistency."""

    def test_dimensional_consistency(self, symbolic_engine):
        """Test that formulas maintain dimensional consistency."""
        P, Q = symbols("P Q", positive=True)
        value = P * Q

        dV_dP = diff(value, P)
        assert dV_dP == Q

    def test_formula_substitution(self, symbolic_engine):
        """Test substitution in complex formulas."""
        x, y, z = symbols("x y z")
        expr = x**2 + y * z

        result = expr.subs(x, y + z)
        expected = (y + z) ** 2 + y * z
        assert expand(result) == expand(expected)

    def test_chain_substitution(self, symbolic_engine):
        """Test multiple sequential substitutions."""
        x, y, z = symbols("x y z")
        expr = x**2 + y**2 + z**2

        result = expr.subs([(x, 1), (y, 2), (z, 3)])
        assert result == 14

    def test_formula_bounds(self, symbolic_engine):
        """Test that formulas respect mathematical bounds."""
        x = symbols("x", positive=True)
        log_expr = log(x)

        func = lambdify(x, log_expr, "numpy")
        assert np.isclose(func(np.e), 1.0)

    def test_inequality_preservation(self, symbolic_engine):
        """Test that inequalities are preserved."""
        x = symbols("x", positive=True)
        expr = x**2

        # x^2 should be monotonically increasing for positive x
        func = lambdify(x, expr, "numpy")
        assert func(2) > func(1)
        assert func(3) > func(2)

    def test_formula_symmetry(self, symbolic_engine):
        """Test symmetric formulas."""
        x, y = symbols("x y")
        expr = x**2 + y**2

        # Should be symmetric in x and y
        assert expr.subs([(x, 3), (y, 4)]) == expr.subs([(x, 4), (y, 3)])


class TestEdgeCases:
    """Tests for edge cases and error handling."""

    def test_division_by_zero(self, symbolic_engine):
        """Test handling of division by zero."""
        x = symbols("x")
        expr = 1 / x
        func = lambdify(x, expr, "numpy")

        with pytest.warns(RuntimeWarning):
            result = func(0)
            assert np.isinf(result)

    def test_zero_division_in_formula(self, symbolic_engine):
        """Test formulas that could have zero division."""
        x, y = symbols("x y")
        expr = x / (y - x)
        func = lambdify((x, y), expr, "numpy")

        with pytest.warns(RuntimeWarning):
            result = func(5, 5)
            assert np.isinf(result) or np.isnan(result)

    def test_undefined_expressions(self, symbolic_engine):
        """Test handling of undefined expressions."""
        x = symbols("x")
        expr = sqrt(x)
        func = lambdify(x, expr, "numpy")

        result = func(-1)
        assert np.isnan(result) or np.iscomplex(result)

    def test_log_of_negative(self, symbolic_engine):
        """Test log of negative numbers."""
        x = symbols("x")
        expr = log(x)
        func = lambdify(x, expr, "numpy")

        with pytest.warns(RuntimeWarning):
            result = func(-1)
            assert np.isnan(result) or np.iscomplex(result)

    def test_numerical_overflow(self, symbolic_engine):
        """Test handling of numerical overflow."""
        x = symbols("x")
        expr = exp(x)
        func = lambdify(x, expr, "numpy")

        with pytest.warns(RuntimeWarning):
            result = func(1000)
            assert np.isinf(result)

    def test_numerical_underflow(self, symbolic_engine):
        """Test handling of numerical underflow."""
        x = symbols("x")
        expr = exp(x)
        func = lambdify(x, expr, "numpy")

        result = func(-1000)
        assert result == 0 or result < 1e-300

    def test_very_small_numbers(self, symbolic_engine):
        """Test operations with very small numbers."""
        x = symbols("x")
        expr = 1 / (1 + exp(-x))  # Sigmoid
        func = lambdify(x, expr, "numpy")

        # Should handle very large negative values
        result = func(-1000)
        assert np.isclose(result, 0.0, atol=1e-10)


class TestIntegrationWithNumerical:
    """Tests for integration between symbolic and numerical systems."""

    def test_optimization_setup(self, symbolic_engine):
        """Test setting up optimization problems."""
        x = symbols("x")
        objective = x**2 + 2 * x + 1

        derivative = diff(objective, x)

        obj_func = lambdify(x, objective, "numpy")
        grad_func = lambdify(x, derivative, "numpy")

        assert np.isclose(grad_func(-1), 0.0)
        assert np.isclose(obj_func(-1), 0.0)

    def test_constrained_optimization(self, symbolic_engine):
        """Test optimization with constraints."""
        x, y = symbols("x y")
        objective = x**2 + y**2
        constraint = x + y - 1

        # Lagrangian: L = f + lambda * g
        lam = symbols("lambda")
        lagrangian = objective + lam * constraint

        # Check that we can compute gradients
        dL_dx = diff(lagrangian, x)
        dL_dy = diff(lagrangian, y)

        assert dL_dx == 2 * x + lam
        assert dL_dy == 2 * y + lam

    def test_numerical_integration_setup(self, symbolic_engine):
        """Test setting up numerical integration."""
        x = symbols("x")
        expr = x**2

        integrand = lambdify(x, expr, "numpy")

        x_vals = np.linspace(0, 1, 1000)
        y_vals = integrand(x_vals)

        integral_approx = np.trapz(y_vals, x_vals)

        assert np.isclose(integral_approx, 1 / 3, rtol=1e-3)

    def test_ode_setup(self, symbolic_engine):
        """Test setting up ODE systems."""
        t, x = symbols("t x")
        # dx/dt = -x (exponential decay)
        dxdt = -x

        ode_func = lambdify((t, x), dxdt, "numpy")

        # At t=0, x=1, rate should be -1
        assert ode_func(0, 1) == -1

    def test_jacobian_computation(self, symbolic_engine):
        """Test Jacobian matrix computation."""
        x, y = symbols("x y")
        f1 = x**2 + y
        f2 = x * y

        # Jacobian matrix
        J11 = diff(f1, x)
        J12 = diff(f1, y)
        J21 = diff(f2, x)
        J22 = diff(f2, y)

        # Convert to numerical functions
        j11_func = lambdify((x, y), J11, "numpy")
        j22_func = lambdify((x, y), J22, "numpy")

        assert j11_func(2, 3) == 4
        assert j22_func(2, 3) == 2

    def test_hessian_computation(self, symbolic_engine):
        """Test Hessian matrix computation."""
        x, y = symbols("x y")
        f = x**2 * y + x * y**2

        # Hessian elements
        H11 = diff(f, x, 2)
        H12 = diff(diff(f, x), y)
        H22 = diff(f, y, 2)

        h11_func = lambdify((x, y), H11, "numpy")
        h22_func = lambdify((x, y), H22, "numpy")

        assert h11_func(1, 1) == 2
        assert h22_func(1, 1) == 2


class TestComplexExpressions:
    """Tests for complex mathematical expressions."""

    def test_polynomial_operations(self, symbolic_engine):
        """Test polynomial algebra."""
        x = symbols("x")
        p1 = x**2 + 2 * x + 1
        p2 = x - 1

        product = expand(p1 * p2)
        assert product == x**3 + x**2 - x - 1

    def test_rational_functions(self, symbolic_engine):
        """Test rational function operations."""
        x = symbols("x")
        f = (x**2 - 1) / (x**2 + 2 * x + 1)

        simplified = simplify(f)
        # Should simplify for x != -1
        func = lambdify(x, simplified, "numpy")
        assert np.isclose(func(2), 3 / 9)

    def test_trigonometric_expressions(self, symbolic_engine):
        """Test complex trig expressions."""
        x = symbols("x")
        expr = sin(2 * x)
        expanded = expr.rewrite(sin, cos)

        # sin(2x) = 2*sin(x)*cos(x)
        expected = 2 * sin(x) * cos(x)
        assert simplify(expanded - expected) == 0

    def test_exponential_logarithm_combo(self, symbolic_engine):
        """Test exp and log combinations."""
        x = symbols("x", positive=True)
        expr = log(exp(x))

        simplified = simplify(expr)
        assert simplified == x

    def test_nested_functions(self, symbolic_engine):
        """Test nested function expressions."""
        x = symbols("x")
        expr = sin(cos(x))

        func = lambdify(x, expr, "numpy")
        result = func(0)
        assert np.isclose(result, np.sin(1))


class TestSymbolicSolving:
    """Tests for symbolic equation solving."""

    def test_linear_equation(self, symbolic_engine):
        """Test solving linear equations."""
        x = symbols("x")
        eq = 2 * x + 3 - 7

        solution = solve(eq, x)
        assert solution[0] == 2

    def test_quadratic_equation(self, symbolic_engine):
        """Test solving quadratic equations."""
        x = symbols("x")
        eq = x**2 - 5 * x + 6

        solutions = solve(eq, x)
        assert set(solutions) == {2, 3}

    def test_system_of_equations(self, symbolic_engine):
        """Test solving system of equations."""
        x, y = symbols("x y")
        eq1 = x + y - 3
        eq2 = x - y - 1

        solution = solve([eq1, eq2], [x, y])
        assert solution[x] == 2
        assert solution[y] == 1

    def test_transcendental_equation(self, symbolic_engine):
        """Test handling of transcendental equations."""
        x = symbols("x")
        eq = exp(x) - 2

        # May return numerical approximation or symbolic form
        solutions = solve(eq, x)
        assert len(solutions) > 0


class TestPerformance:
    """Performance-related tests."""

    def test_large_polynomial(self, symbolic_engine):
        """Test handling large polynomials."""
        x = symbols("x")
        poly = sum(x**i for i in range(100))

        func = lambdify(x, poly, "numpy")
        result = func(0.5)
        assert result > 0

    def test_vectorized_performance(self, symbolic_engine):
        """Test vectorized operations are efficient."""
        x = symbols("x")
        expr = x**2 + sin(x) + exp(-x)
        func = lambdify(x, expr, "numpy")

        # Large array
        x_vals = np.linspace(0, 10, 10000)
        results = func(x_vals)

        assert len(results) == 10000
        assert np.all(np.isfinite(results))


@pytest.fixture
def symbolic_engine():
    """Fixture providing symbolic engine instance."""

    class MockSymbolicEngine:
        """Mock symbolic engine for testing."""

        pass

    return MockSymbolicEngine()


if __name__ == "__main__":
    pytest.main([__file__, "-v", "--tb=short"])
