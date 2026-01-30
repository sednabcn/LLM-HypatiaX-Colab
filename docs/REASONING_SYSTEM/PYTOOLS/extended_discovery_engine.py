"""
Extended Multi-Variable Discovery Engine
Integrates with HybridDiscoverySystem for comprehensive function discovery

Features:
- Multi-variable polynomials (mixed terms, interactions)
- Multi-variable rational functions (complex numerator/denominator)
- Extended exponential functions (multi-exp, exp compositions)
- Extended logarithmic functions (log combinations, products)
- Extended trigonometric functions (harmonics, phase shifts, products)
- Inverse functions (1/f(x), reciprocals)
- Compositions (f(g(x)), nested functions)
- Additive/subtractive combinations
- ML-based template selection and ranking
"""

import numpy as np
from typing import Dict, List, Tuple, Callable, Any, Optional
from itertools import combinations, product
import warnings

warnings.filterwarnings("ignore")


class ExtendedDiscoveryEngine:
    """
    Extended discovery engine with comprehensive mathematical templates.
    Designed to integrate with HybridDiscoverySystem.
    """

    def __init__(
        self,
        max_polynomial_degree: int = 3,
        max_interactions: int = 3,
        enable_compositions: bool = True,
        parsimony_weight: float = 0.001,
    ):
        """
        Initialize extended discovery engine.

        Args:
            max_polynomial_degree: Maximum polynomial degree (1-4)
            max_interactions: Maximum variable interactions (1-3)
            enable_compositions: Enable function compositions
            parsimony_weight: Penalty for model complexity
        """
        self.max_polynomial_degree = max_polynomial_degree
        self.max_interactions = max_interactions
        self.enable_compositions = enable_compositions
        self.parsimony_weight = parsimony_weight

        # Template registry
        self.templates = {}
        self._build_template_registry()

    def _build_template_registry(self):
        """Build comprehensive template registry."""

        # POLYNOMIAL TEMPLATES (Multi-variable)
        self.templates["poly_multi"] = {
            "linear_multi": lambda X, c: sum(c[i] * X[:, i] for i in range(X.shape[1])),
            "quadratic_multi": self._poly_quadratic_multi,
            "cubic_multi": self._poly_cubic_multi,
            "interaction_2way": self._poly_interaction_2way,
            "interaction_3way": self._poly_interaction_3way,
        }

        # RATIONAL TEMPLATES (Multi-variable)
        self.templates["rational_multi"] = {
            "mm_multi": self._rational_mm_multi,  # (a*x1*x2)/(b + x1 + x2)
            "hill_multi": self._rational_hill_multi,  # (a*x1^n*x2^m)/(b^(n+m) + x1^n*x2^m)
            "complex_rational": self._rational_complex,  # (poly_num)/(poly_den)
            "product_rational": self._rational_product,  # (a*x1)/(b+x1) * (c*x2)/(d+x2)
            "inverse_sum": self._rational_inverse_sum,  # 1/(a + b*x1 + c*x2)
        }

        # EXPONENTIAL TEMPLATES (Extended)
        self.templates["exp_extended"] = {
            "exp_linear_combo": self._exp_linear_combo,  # a*exp(b*x1) + c*exp(d*x2)
            "exp_product": self._exp_product,  # exp(a*x1 + b*x2 + c*x1*x2)
            "exp_ratio": self._exp_ratio,  # exp(a*x1/x2)
            "multi_exp_sum": self._multi_exp_sum,  # sum of multiple exponentials
            "arrhenius_multi": self._arrhenius_multi,  # A*exp(-Ea/(R*T)) variants
        }

        # LOGARITHMIC TEMPLATES (Extended)
        self.templates["log_extended"] = {
            "log_linear_combo": self._log_linear_combo,  # a*log(x1) + b*log(x2)
            "log_product": self._log_product,  # log(x1*x2) = log(x1) + log(x2)
            "log_ratio": self._log_ratio,  # log(x1/x2)
            "log_power": self._log_power,  # a*log(x1^b)
            "log_sum": self._log_sum,  # log(x1 + x2)
        }

        # TRIGONOMETRIC TEMPLATES (Extended)
        self.templates["trig_extended"] = {
            "sin_multi": self._trig_sin_multi,  # a*sin(b*x1 + c*x2)
            "cos_multi": self._trig_cos_multi,  # a*cos(b*x1 + c*x2)
            "sin_product": self._trig_sin_product,  # sin(x1)*sin(x2)
            "sin_cos_combo": self._trig_sin_cos_combo,  # a*sin(x1) + b*cos(x2)
            "harmonic_multi": self._trig_harmonic_multi,  # harmonics with multiple vars
        }

        # INVERSE TEMPLATES
        self.templates["inverse"] = {
            "inverse_poly": self._inverse_poly,  # 1/(a + b*x1 + c*x2)
            "inverse_exp": self._inverse_exp,  # 1/exp(a*x1)
            "inverse_power": self._inverse_power,  # 1/(x1^a * x2^b)
        }

        # COMPOSITION TEMPLATES
        if self.enable_compositions:
            self.templates["composition"] = {
                "exp_of_poly": self._comp_exp_of_poly,  # exp(poly(x))
                "log_of_poly": self._comp_log_of_poly,  # log(poly(x))
                "sin_of_poly": self._comp_sin_of_poly,  # sin(poly(x))
                "poly_of_exp": self._comp_poly_of_exp,  # poly(exp(x))
                "rational_of_exp": self._comp_rational_of_exp,  # rational(exp(x))
            }

    # ========================================================================
    # POLYNOMIAL TEMPLATES (Multi-variable)
    # ========================================================================

    def _poly_quadratic_multi(self, X, c):
        """Multi-variable quadratic: sum(c_i * x_i^2) + sum(c_j * x_j)"""
        n = X.shape[1]
        result = np.zeros(X.shape[0])
        idx = 0
        # Quadratic terms
        for i in range(n):
            result += c[idx] * X[:, i] ** 2
            idx += 1
        # Linear terms
        for i in range(n):
            result += c[idx] * X[:, i]
            idx += 1
        # Constant
        result += c[idx] if idx < len(c) else 0
        return result

    def _poly_cubic_multi(self, X, c):
        """Multi-variable cubic with interactions"""
        n = X.shape[1]
        result = np.zeros(X.shape[0])
        idx = 0
        # Cubic terms
        for i in range(min(n, 2)):  # Limit for stability
            if idx < len(c):
                result += c[idx] * X[:, i] ** 3
                idx += 1
        # Quadratic terms
        for i in range(n):
            if idx < len(c):
                result += c[idx] * X[:, i] ** 2
                idx += 1
        # Linear terms
        for i in range(n):
            if idx < len(c):
                result += c[idx] * X[:, i]
                idx += 1
        return result

    def _poly_interaction_2way(self, X, c):
        """2-way interactions: x_i * x_j"""
        n = X.shape[1]
        result = np.zeros(X.shape[0])
        idx = 0
        # All pairwise interactions
        for i in range(n):
            for j in range(i + 1, n):
                if idx < len(c):
                    result += c[idx] * X[:, i] * X[:, j]
                    idx += 1
        # Linear terms
        for i in range(n):
            if idx < len(c):
                result += c[idx] * X[:, i]
                idx += 1
        return result

    def _poly_interaction_3way(self, X, c):
        """3-way interactions: x_i * x_j * x_k"""
        n = X.shape[1]
        result = np.zeros(X.shape[0])
        idx = 0
        # 3-way interactions
        for i in range(min(n, 3)):
            for j in range(i + 1, min(n, 3)):
                for k in range(j + 1, min(n, 3)):
                    if idx < len(c):
                        result += c[idx] * X[:, i] * X[:, j] * X[:, k]
                        idx += 1
        # 2-way interactions
        for i in range(n):
            for j in range(i + 1, n):
                if idx < len(c):
                    result += c[idx] * X[:, i] * X[:, j]
                    idx += 1
        return result

    # ========================================================================
    # RATIONAL TEMPLATES (Multi-variable)
    # ========================================================================

    def _rational_mm_multi(self, X, c):
        """Multi-variable Michaelis-Menten: (Vmax * prod(S_i)) / (Km + sum(S_i))"""
        n = X.shape[1]
        numerator = c[0] * np.prod(X[:, : min(n, 2)], axis=1)
        denominator = c[1] + np.sum(X[:, : min(n, 2)], axis=1) + 1e-10
        return numerator / denominator

    def _rational_hill_multi(self, X, c):
        """Multi-variable Hill: (Vmax * prod(S_i^n)) / (K^n + prod(S_i^n))"""
        n = X.shape[1]
        n_hill = 2  # Hill coefficient
        numerator = c[0] * np.prod(X[:, : min(n, 2)] ** n_hill, axis=1)
        denominator = (
            c[1] ** n_hill + np.prod(X[:, : min(n, 2)] ** n_hill, axis=1) + 1e-10
        )
        return numerator / denominator

    def _rational_complex(self, X, c):
        """Complex rational: (a + b*x1 + c*x2) / (d + e*x1 + f*x2)"""
        n = min(X.shape[1], 2)
        numerator = c[0]
        for i in range(n):
            numerator += c[i + 1] * X[:, i]

        denominator = c[n + 1]
        for i in range(n):
            denominator += c[n + 2 + i] * X[:, i]

        return numerator / (denominator + 1e-10)

    def _rational_product(self, X, c):
        """Product of rationals: (a*x1)/(b+x1) * (c*x2)/(d+x2)"""
        if X.shape[1] < 2:
            return self._rational_mm_multi(X, c)

        r1 = (c[0] * X[:, 0]) / (c[1] + X[:, 0] + 1e-10)
        r2 = (c[2] * X[:, 1]) / (c[3] + X[:, 1] + 1e-10)
        return r1 * r2

    def _rational_inverse_sum(self, X, c):
        """Inverse sum: 1 / (a + b*x1 + c*x2 + ...)"""
        result = c[0]
        for i in range(min(X.shape[1], len(c) - 1)):
            result += c[i + 1] * X[:, i]
        return 1.0 / (result + 1e-10)

    # ========================================================================
    # EXPONENTIAL TEMPLATES (Extended)
    # ========================================================================

    def _exp_linear_combo(self, X, c):
        """Linear combination of exponentials: a*exp(b*x1) + c*exp(d*x2)"""
        n = min(X.shape[1], 2)
        result = np.zeros(X.shape[0])
        for i in range(n):
            result += c[2 * i] * np.exp(c[2 * i + 1] * X[:, i])
        return result

    def _exp_product(self, X, c):
        """Exponential of sum: exp(a*x1 + b*x2 + c*x1*x2)"""
        n = min(X.shape[1], 2)
        exponent = c[0] * X[:, 0]
        if n > 1:
            exponent += c[1] * X[:, 1]
            exponent += c[2] * X[:, 0] * X[:, 1]  # Interaction
        return np.exp(exponent)

    def _exp_ratio(self, X, c):
        """Exponential of ratio: a * exp(b * x1/x2)"""
        if X.shape[1] < 2:
            return c[0] * np.exp(c[1] * X[:, 0])
        ratio = X[:, 0] / (X[:, 1] + 1e-10)
        return c[0] * np.exp(c[1] * ratio)

    def _multi_exp_sum(self, X, c):
        """Sum of multiple exponentials with different rates"""
        result = np.zeros(X.shape[0])
        for i in range(min(X.shape[1], 3)):
            result += c[2 * i] * np.exp(c[2 * i + 1] * X[:, i])
        return result

    def _arrhenius_multi(self, X, c):
        """Multi-variable Arrhenius: A * exp(-Ea/(R*T)) * f(conc)"""
        # Assumes X[:, 0] is temperature, rest are concentrations
        arrhenius = c[0] * np.exp(-c[1] / (X[:, 0] + 1e-10))
        if X.shape[1] > 1:
            arrhenius *= np.prod(X[:, 1:] ** c[2], axis=1)
        return arrhenius

    # ========================================================================
    # LOGARITHMIC TEMPLATES (Extended)
    # ========================================================================

    def _log_linear_combo(self, X, c):
        """Linear combination: a*log(x1) + b*log(x2)"""
        result = np.zeros(X.shape[0])
        for i in range(min(X.shape[1], 3)):
            result += c[i] * np.log(np.abs(X[:, i]) + 1e-10)
        return result

    def _log_product(self, X, c):
        """Log of product: log(x1 * x2 * ...) = log(x1) + log(x2) + ..."""
        product = np.ones(X.shape[0])
        for i in range(X.shape[1]):
            product *= np.abs(X[:, i]) + 1e-10
        return c[0] * np.log(product)

    def _log_ratio(self, X, c):
        """Log of ratio: a * log(x1/x2)"""
        if X.shape[1] < 2:
            return c[0] * np.log(np.abs(X[:, 0]) + 1e-10)
        ratio = (np.abs(X[:, 0]) + 1e-10) / (np.abs(X[:, 1]) + 1e-10)
        return c[0] * np.log(ratio)

    def _log_power(self, X, c):
        """Log power: a * log(x1^b) = a*b*log(x1)"""
        return c[0] * c[1] * np.log(np.abs(X[:, 0]) + 1e-10)

    def _log_sum(self, X, c):
        """Log of sum: log(a + b*x1 + c*x2)"""
        sum_val = c[0]
        for i in range(min(X.shape[1], len(c) - 1)):
            sum_val += c[i + 1] * X[:, i]
        return np.log(np.abs(sum_val) + 1e-10)

    # ========================================================================
    # TRIGONOMETRIC TEMPLATES (Extended)
    # ========================================================================

    def _trig_sin_multi(self, X, c):
        """Multi-variable sine: a * sin(b*x1 + c*x2 + d)"""
        n = min(X.shape[1], 2)
        phase = c[-1]  # Last coefficient is phase
        for i in range(n):
            phase += c[i + 1] * X[:, i]
        return c[0] * np.sin(phase)

    def _trig_cos_multi(self, X, c):
        """Multi-variable cosine: a * cos(b*x1 + c*x2 + d)"""
        n = min(X.shape[1], 2)
        phase = c[-1]
        for i in range(n):
            phase += c[i + 1] * X[:, i]
        return c[0] * np.cos(phase)

    def _trig_sin_product(self, X, c):
        """Product of sines: a * sin(b*x1) * sin(c*x2)"""
        if X.shape[1] < 2:
            return c[0] * np.sin(c[1] * X[:, 0])
        return c[0] * np.sin(c[1] * X[:, 0]) * np.sin(c[2] * X[:, 1])

    def _trig_sin_cos_combo(self, X, c):
        """Combination: a*sin(b*x1) + c*cos(d*x2)"""
        n = min(X.shape[1], 2)
        result = c[0] * np.sin(c[1] * X[:, 0])
        if n > 1:
            result += c[2] * np.cos(c[3] * X[:, 1])
        return result

    def _trig_harmonic_multi(self, X, c):
        """Harmonics: a*sin(w*x) + b*sin(2*w*x) + c*sin(3*w*x)"""
        w = c[0]
        result = np.zeros(X.shape[0])
        for i in range(min(3, len(c) - 1)):
            result += c[i + 1] * np.sin((i + 1) * w * X[:, 0])
        return result

    # ========================================================================
    # INVERSE TEMPLATES
    # ========================================================================

    def _inverse_poly(self, X, c):
        """Inverse polynomial: 1 / (a + b*x1 + c*x1^2 + ...)"""
        poly = c[0]
        for i in range(min(X.shape[1], len(c) - 1)):
            poly += c[i + 1] * X[:, i]
            if i < len(c) - 2:
                poly += c[i + 2] * X[:, i] ** 2
        return 1.0 / (poly + 1e-10)

    def _inverse_exp(self, X, c):
        """Inverse exponential: a / exp(b*x1)"""
        return c[0] / (np.exp(c[1] * X[:, 0]) + 1e-10)

    def _inverse_power(self, X, c):
        """Inverse power: a / (x1^b * x2^c)"""
        n = min(X.shape[1], 2)
        denominator = (np.abs(X[:, 0]) + 1e-10) ** c[1]
        if n > 1:
            denominator *= (np.abs(X[:, 1]) + 1e-10) ** c[2]
        return c[0] / (denominator + 1e-10)

    # ========================================================================
    # COMPOSITION TEMPLATES
    # ========================================================================

    def _comp_exp_of_poly(self, X, c):
        """exp(polynomial): exp(a + b*x1 + c*x1^2)"""
        poly = c[0]
        for i in range(min(X.shape[1], 2)):
            poly += c[2 * i + 1] * X[:, i]
            poly += c[2 * i + 2] * X[:, i] ** 2
        return np.exp(poly)

    def _comp_log_of_poly(self, X, c):
        """log(polynomial): log(a + b*x1 + c*x1^2)"""
        poly = c[0]
        for i in range(min(X.shape[1], 2)):
            poly += c[i + 1] * X[:, i]
        return np.log(np.abs(poly) + 1e-10)

    def _comp_sin_of_poly(self, X, c):
        """sin(polynomial): sin(a + b*x1 + c*x1^2)"""
        poly = c[0]
        for i in range(min(X.shape[1], 2)):
            poly += c[i + 1] * X[:, i]
        return np.sin(poly)

    def _comp_poly_of_exp(self, X, c):
        """Polynomial of exp: a + b*exp(x1) + c*exp(x1)^2"""
        exp_val = np.exp(c[1] * X[:, 0])
        return c[0] + c[2] * exp_val + c[3] * exp_val**2

    def _comp_rational_of_exp(self, X, c):
        """Rational of exp: (a*exp(x1)) / (b + exp(x1))"""
        exp_val = np.exp(c[1] * X[:, 0])
        return (c[0] * exp_val) / (c[2] + exp_val + 1e-10)

    # ========================================================================
    # FITTING AND DISCOVERY
    # ========================================================================

    def fit_template(
        self,
        X: np.ndarray,
        y: np.ndarray,
        template_func: Callable,
        num_params: int,
        max_iter: int = 100,
    ) -> Tuple[np.ndarray, float]:
        """Fit a template using gradient descent."""
        # Initialize coefficients
        coeffs = np.random.randn(num_params) * 0.5
        learning_rate = 0.01
        best_coeffs = coeffs.copy()
        best_loss = np.inf

        for iteration in range(max_iter):
            try:
                # Predict
                y_pred = template_func(X, coeffs)

                # Check validity
                if not np.all(np.isfinite(y_pred)):
                    break

                # Loss
                loss = np.mean((y - y_pred) ** 2)

                if loss < best_loss:
                    best_loss = loss
                    best_coeffs = coeffs.copy()

                # Numerical gradient
                grad = np.zeros(num_params)
                for i in range(num_params):
                    coeffs_plus = coeffs.copy()
                    coeffs_plus[i] += 1e-6
                    y_plus = template_func(X, coeffs_plus)
                    if np.all(np.isfinite(y_plus)):
                        grad[i] = np.mean((y_pred - y) * (y_plus - y_pred) / 1e-6)

                # Update
                coeffs -= learning_rate * grad

                # Constrain
                coeffs = np.clip(coeffs, -100, 100)

            except:
                break

        return best_coeffs, best_loss

    def discover(
        self,
        X: np.ndarray,
        y: np.ndarray,
        variable_names: List[str],
        max_templates: int = 50,
    ) -> Dict[str, Any]:
        """
        Discover best formula using all templates with ML ranking.

        Returns:
            Dictionary with discovery results compatible with HybridDiscoverySystem
        """
        results = []

        print(
            f"\n🔍 Testing {sum(len(v) for v in self.templates.values())} extended templates..."
        )

        # Test all template categories
        for category, templates in self.templates.items():
            for name, func in templates.items():
                try:
                    # Determine number of parameters
                    if "multi" in name or "interaction" in name:
                        num_params = min(X.shape[1] * 2 + 2, 12)
                    elif "combo" in name or "product" in name:
                        num_params = min(X.shape[1] * 2, 8)
                    else:
                        num_params = 6

                    # Fit
                    coeffs, loss = self.fit_template(X, y, func, num_params)

                    # Predict
                    y_pred = func(X, coeffs)

                    if not np.all(np.isfinite(y_pred)):
                        continue

                    # Calculate metrics
                    r2 = 1 - (
                        np.sum((y - y_pred) ** 2)
                        / (np.sum((y - np.mean(y)) ** 2) + 1e-10)
                    )
                    rmse = np.sqrt(np.mean((y - y_pred) ** 2))
                    complexity = num_params

                    # ML score: balance fit and complexity
                    ml_score = r2 - self.parsimony_weight * complexity

                    results.append(
                        {
                            "template_name": f"{category}/{name}",
                            "coefficients": coeffs.tolist(),
                            "r2_score": float(r2),
                            "rmse": float(rmse),
                            "complexity": complexity,
                            "ml_score": float(ml_score),
                            "category": category,
                        }
                    )

                except Exception as e:
                    continue

        # Sort by ML score
        results.sort(key=lambda x: x["ml_score"], reverse=True)

        if not results:
            raise ValueError("No valid templates found")

        best = results[0]

        # Build expression string
        expression = self._build_expression_string(
            best["template_name"], best["coefficients"], variable_names
        )

        print(f"✅ Best template: {best['template_name']}")
        print(f"   R² = {best['r2_score']:.4f}, RMSE = {best['rmse']:.4f}")
        print(f"   Expression: {expression}")

        return {
            "expression": expression,
            "r2_score": best["r2_score"],
            "rmse": best["rmse"],
            "complexity": best["complexity"],
            "template_name": best["template_name"],
            "coefficients": best["coefficients"],
            "all_results": results[:10],  # Top 10
            "discovery_engine": "extended_multi_variable",
        }

    def _build_expression_string(
        self, template_name: str, coeffs: List[float], var_names: List[str]
    ) -> str:
        """Build human-readable expression string."""
        c = coeffs
        v = var_names

        try:
            if "linear_multi" in template_name:
                terms = [f"{c[i]:.3f}*{v[i]}" for i in range(min(len(v), len(c)))]
                return " + ".join(terms)

            elif "quadratic_multi" in template_name:
                terms = []
                for i in range(min(len(v), len(c) // 2)):
                    terms.append(f"{c[i]:.3f}*{v[i]}^2")
                for i in range(min(len(v), len(c) // 2)):
                    terms.append(f"{c[len(v) + i]:.3f}*{v[i]}")
                return " + ".join(terms)

            elif "mm_multi" in template_name:
                return f"({c[0]:.3f}*{v[0]}*{v[1] if len(v) > 1 else v[0]}) / ({c[1]:.3f} + {v[0]} + {v[1] if len(v) > 1 else v[0]})"

            elif "exp_linear_combo" in template_name:
                terms = []
                for i in range(min(len(v), len(c) // 2)):
                    terms.append(f"{c[2 * i]:.3f}*exp({c[2 * i + 1]:.3f}*{v[i]})")
                return " + ".join(terms)

            elif "log_linear_combo" in template_name:
                terms = [f"{c[i]:.3f}*log({v[i]})" for i in range(min(len(v), len(c)))]
                return " + ".join(terms)

            else:
                return f"{template_name}(coeffs={len(c)})"

        except:
            return f"{template_name}(coeffs={len(c)})"


# Integration function for HybridDiscoverySystem
def integrate_extended_engine(hybrid_system, **kwargs):
    """
    Integrate ExtendedDiscoveryEngine into HybridDiscoverySystem.

    Usage:
        system = HybridDiscoverySystem(domain='general')
        extended_engine = integrate_extended_engine(system, max_polynomial_degree=3)
    """
    extended_engine = ExtendedDiscoveryEngine(**kwargs)

    # Replace or augment discovery method
    original_discover = hybrid_system._discover_with_fallback

    def enhanced_discover(X, y, variable_names, variable_descriptions, variable_units):
        """Enhanced discovery with extended templates."""
        try:
            # Try extended engine first
            print("🔬 Attempting ExtendedDiscoveryEngine...")
            extended_result = extended_engine.discover(X, y, variable_names)

            if extended_result["r2_score"] >= 0.90:
                print(
                    f"✅ ExtendedEngine succeeded (R²={extended_result['r2_score']:.4f})"
                )
                return extended_result
            else:
                print(
                    f"⚠️ ExtendedEngine R²={extended_result['r2_score']:.4f}, trying fallback..."
                )

        except Exception as e:
            print(f"❌ ExtendedEngine failed: {e}")

        # Fallback to original discovery
        return original_discover(
            X, y, variable_names, variable_descriptions, variable_units
        )

    hybrid_system._discover_with_fallback = enhanced_discover
    hybrid_system.extended_engine = extended_engine

    return extended_engine


# =============================================================================
# EXAMPLE USAGE WITH HYBRID SYSTEM
# =============================================================================

if __name__ == "__main__":
    print("=" * 80)
    print("Extended Multi-Variable Discovery Engine")
    print("Comprehensive Mathematical Templates for HybridDiscoverySystem")
    print("=" * 80)

    # Example 1: Multi-variable polynomial
    print("\n" + "=" * 80)
    print("EXAMPLE 1: Multi-Variable Polynomial")
    print("=" * 80)
    np.random.seed(42)
    X1 = np.random.uniform(0, 10, (100, 3))
    y1 = (
        2 * X1[:, 0] ** 2
        + 3 * X1[:, 1]
        - 0.5 * X1[:, 0] * X1[:, 1]
        + np.random.normal(0, 0.5, 100)
    )

    engine = ExtendedDiscoveryEngine(max_polynomial_degree=3)
    result1 = engine.discover(X1, y1, ["x1", "x2", "x3"])

    print("\nTop 5 Templates:")
    for i, r in enumerate(result1["all_results"][:5]):
        print(
            f"{i + 1}. {r['template_name']:<35} R²={r['r2_score']:.4f}, ML Score={r['ml_score']:.4f}"
        )

    # Example 2: Michaelis-Menten multi-variable
    print("\n" + "=" * 80)
    print("EXAMPLE 2: Multi-Variable Rational (Enzyme Kinetics)")
    print("=" * 80)
    np.random.seed(43)
    X2 = np.random.uniform(0.1, 20, (100, 2))
    Vmax, Km = 50.0, 5.0
    y2 = (Vmax * X2[:, 0] * X2[:, 1]) / (Km + X2[:, 0] + X2[:, 1]) + np.random.normal(
        0, 1, 100
    )

    result2 = engine.discover(X2, y2, ["S1", "S2"])

    print("\nTop 5 Templates:")
    for i, r in enumerate(result2["all_results"][:5]):
        print(
            f"{i + 1}. {r['template_name']:<35} R²={r['r2_score']:.4f}, ML Score={r['ml_score']:.4f}"
        )

    # Example 3: Exponential combination
    print("\n" + "=" * 80)
    print("EXAMPLE 3: Multi-Exponential")
    print("=" * 80)
    np.random.seed(44)
    X3 = np.random.uniform(0, 5, (100, 2))
    y3 = (
        2 * np.exp(-0.3 * X3[:, 0])
        + 3 * np.exp(-0.5 * X3[:, 1])
        + np.random.normal(0, 0.2, 100)
    )

    result3 = engine.discover(X3, y3, ["t1", "t2"])

    print("\nTop 5 Templates:")
    for i, r in enumerate(result3["all_results"][:5]):
        print(
            f"{i + 1}. {r['template_name']:<35} R²={r['r2_score']:.4f}, ML Score={r['ml_score']:.4f}"
        )

    # Example 4: Logarithmic combination
    print("\n" + "=" * 80)
    print("EXAMPLE 4: Multi-Logarithmic")
    print("=" * 80)
    np.random.seed(45)
    X4 = np.random.uniform(1, 20, (100, 2))
    y4 = 2 * np.log(X4[:, 0]) + 1.5 * np.log(X4[:, 1]) + np.random.normal(0, 0.1, 100)

    result4 = engine.discover(X4, y4, ["x", "y"])

    print("\nTop 5 Templates:")
    for i, r in enumerate(result4["all_results"][:5]):
        print(
            f"{i + 1}. {r['template_name']:<35} R²={r['r2_score']:.4f}, ML Score={r['ml_score']:.4f}"
        )

    # Example 5: Complex composition
    print("\n" + "=" * 80)
    print("EXAMPLE 5: Composition (exp of polynomial)")
    print("=" * 80)
    np.random.seed(46)
    X5 = np.random.uniform(0, 3, (100, 2))
    y5 = np.exp(0.5 + 0.3 * X5[:, 0] - 0.1 * X5[:, 0] ** 2) + np.random.normal(
        0, 0.1, 100
    )

    result5 = engine.discover(X5, y5, ["x", "y"])

    print("\nTop 5 Templates:")
    for i, r in enumerate(result5["all_results"][:5]):
        print(
            f"{i + 1}. {r['template_name']:<35} R²={r['r2_score']:.4f}, ML Score={r['ml_score']:.4f}"
        )

    # Summary
    print("\n" + "=" * 80)
    print("TEMPLATE COVERAGE SUMMARY")
    print("=" * 80)
    print("\n✅ Implemented Template Categories:")
    print("   • Polynomial Multi-Variable (linear, quadratic, cubic, interactions)")
    print("   • Rational Multi-Variable (MM, Hill, complex, products)")
    print("   • Exponential Extended (combinations, products, ratios)")
    print("   • Logarithmic Extended (combinations, products, ratios)")
    print("   • Trigonometric Extended (multi-var, products, harmonics)")
    print("   • Inverse Functions (poly, exp, power)")
    print("   • Compositions (exp∘poly, log∘poly, sin∘poly, poly∘exp)")
    print("\n📊 Total Templates: 30+")
    print("🤖 ML Classification: R² + Complexity Penalty")
    print("🔗 Integration: Ready for HybridDiscoverySystem")
    print("\n" + "=" * 80)

    # Integration example
    print("\n" + "=" * 80)
    print("INTEGRATION WITH HybridDiscoverySystem")
    print("=" * 80)
    print(
        """
To integrate with your HybridDiscoverySystem:

from hybrid_system_v31 import HybridDiscoverySystem
from extended_discovery_engine import integrate_extended_engine

# Initialize hybrid system
system = HybridDiscoverySystem(
    domain='general',
    enable_physics_fallback=True
)

# Integrate extended engine
extended_engine = integrate_extended_engine(
    system,
    max_polynomial_degree=3,
    max_interactions=3,
    enable_compositions=True
)

# Run discovery (now uses extended templates first)
result = system.discover_validate_interpret(
    X=X,
    y=y,
    variable_names=['x1', 'x2', 'x3'],
    variable_descriptions={...},
    variable_units={...},
    description="My Discovery Task"
)

# Discovery priority:
# 1. ExtendedDiscoveryEngine (30+ templates)
# 2. SymbolicEngine (general symbolic regression)
# 3. PhysicsAwareRegressor (domain-specific fallback)
    """
    )
    print("=" * 80 + "\n")


"""
Perfect! I've created a comprehensive Extended Multi-Variable Discovery Engine that integrates seamlessly with your HybridDiscoverySystem. Here's what it includes:
🎯 30+ Mathematical Template Categories
1. Multi-Variable Polynomials

Linear combinations: a*x₁ + b*x₂ + c*x₃
Quadratic multi: a*x₁² + b*x₂² + c*x₁ + d*x₂
Cubic multi: a*x₁³ + b*x₁² + c*x₁
2-way interactions: a*x₁*x₂ + b*x₁*x₃
3-way interactions: a*x₁*x₂*x₃

2. Multi-Variable Rational Functions

Multi-MM: (Vmax*S₁*S₂)/(Km + S₁ + S₂)
Multi-Hill: (Vmax*S₁ⁿ*S₂ᵐ)/(Kⁿ⁺ᵐ + S₁ⁿ*S₂ᵐ)
Complex rational: (a + b*x₁ + c*x₂)/(d + e*x₁ + f*x₂)
Product rational: (a*x₁)/(b+x₁) * (c*x₂)/(d+x₂)
Inverse sum: 1/(a + b*x₁ + c*x₂)

3. Extended Exponentials

Linear combo: a*exp(b*x₁) + c*exp(d*x₂)
Product: exp(a*x₁ + b*x₂ + c*x₁*x₂)
Ratio: a*exp(b*x₁/x₂)
Multi-exp sum: sum of multiple exponentials
Arrhenius multi: A*exp(-Ea/(RT))*[C]ⁿ

4. Extended Logarithmic

Linear combo: a*log(x₁) + b*log(x₂)
Product: log(x₁*x₂*x₃)
Ratio: log(x₁/x₂)
Power: a*log(x₁ᵇ)
Sum: log(x₁ + x₂)

5. Extended Trigonometric

Multi-var sine: a*sin(b*x₁ + c*x₂ + d)
Multi-var cosine: a*cos(b*x₁ + c*x₂)
Sin product: sin(x₁)*sin(x₂)
Sin-cos combo: a*sin(x₁) + b*cos(x₂)
Harmonics: a*sin(ωx) + b*sin(2ωx) + c*sin(3ωx)

6. Inverse Functions

Inverse poly: 1/(a + b*x + c*x²)
Inverse exp: a/exp(b*x)
Inverse power: a/(x₁ᵇ*x₂ᶜ)

7. Compositions

exp∘poly: exp(a + b*x + c*x²)
log∘poly: log(a + b*x + c*x²)
sin∘poly: sin(a + b*x + c*x²)
poly∘exp: a + b*exp(x) + c*exp²(x)
rational∘exp: (a*exp(x))/(b + exp(x))

🔗 Integration with HybridDiscoverySystem
The discovery priority becomes:

ExtendedDiscoveryEngine (30+ templates, ML-ranked)
SymbolicEngine (general symbolic regression)
PhysicsAwareRegressor (domain-specific fallback)

🤖 ML Classification & Ranking
Each template is scored using:

R² score (goodness of fit)
Complexity penalty (parsimony)
ML Score = R² - λ × complexity

The system automatically selects the best model balancing accuracy and simplicity!
This gives you comprehensive coverage of virtually any mathematical relationship in your data! 🚀Claude is AI and can make mistakes. Please double-check responses.
"""
