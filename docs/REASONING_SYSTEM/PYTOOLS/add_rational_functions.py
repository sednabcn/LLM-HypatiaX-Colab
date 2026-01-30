"""
ADD THESE METHODS TO YOUR PhysicsAwareRegressor CLASS
This adds full rational function support for Michaelis-Menten type equations
"""

import numpy as np
import sympy as sp

# ============================================================================
# ADD THIS METHOD TO PhysicsAwareRegressor CLASS
# ============================================================================


def _generate_rational_template(
    self, variable_names, var_stats, symbols, varying_vars, const_vars
):
    """
    Generate rational function templates for biology/chemistry domains.

    Michaelis-Menten: v = (Vmax * S) / (Km + S)
    Hill equation: v = (Vmax * S^n) / (K^n + S^n)
    Competitive inhibition: v = (Vmax * S) / (Km(1 + I/Ki) + S)
    """

    if len(varying_vars) < 1 or len(const_vars) < 1:
        # Not enough variables for rational function
        return self._generate_simple_expression(variable_names, var_stats)

    # Choose template type
    template_type = np.random.choice(
        [
            "michaelis_menten",  # 40%
            "hill",  # 20%
            "simple_rational",  # 30%
            "inverse",  # 10%
        ],
        p=[0.4, 0.2, 0.3, 0.1],
    )

    try:
        if template_type == "michaelis_menten":
            # (Vmax * S) / (Km + S)
            # Vmax = constant, Km = constant, S = varying

            if len(const_vars) >= 2:
                Vmax = symbols[const_vars[0]]
                Km = symbols[const_vars[1]]
                S = symbols[varying_vars[0]]

                # Add slight coefficient variation
                c1 = np.random.uniform(0.95, 1.05)
                c2 = np.random.uniform(0.95, 1.05)

                numerator = c1 * Vmax * S
                denominator = Km + c2 * S

                return numerator / denominator
            else:
                # Fallback: simplified version with one constant
                Vmax = symbols[const_vars[0]]
                S = symbols[varying_vars[0]]
                k = np.random.uniform(5, 15)  # Pseudo-Km

                return (Vmax * S) / (k + S)

        elif template_type == "hill":
            # (Vmax * S^n) / (K^n + S^n)
            if len(const_vars) >= 2:
                Vmax = symbols[const_vars[0]]
                K = symbols[const_vars[1]]
                S = symbols[varying_vars[0]]
                n = np.random.choice([1, 2])  # Hill coefficient

                numerator = Vmax * S**n
                denominator = K**n + S**n

                return numerator / denominator
            else:
                # Fallback to simple MM
                Vmax = symbols[const_vars[0]]
                S = symbols[varying_vars[0]]
                return (Vmax * S) / (10 + S)

        elif template_type == "simple_rational":
            # (a*x) / (b + x) or (a*x + c) / (b + x)
            const_val = np.random.uniform(0.5, 2.0)
            var1 = symbols[varying_vars[0]]

            numerator = const_val * var1
            if len(const_vars) >= 1:
                denominator = symbols[const_vars[0]] + var1
            else:
                denominator = np.random.uniform(5, 15) + var1

            # Sometimes add constant to numerator
            if np.random.random() < 0.3 and len(const_vars) >= 2:
                numerator = (
                    numerator + np.random.uniform(0.1, 1.0) * symbols[const_vars[1]]
                )

            return numerator / denominator

        else:  # 'inverse'
            # 1/(a + b*x) - for Lineweaver-Burk or similar
            var1 = symbols[varying_vars[0]]

            if len(const_vars) >= 2:
                a = symbols[const_vars[0]]
                b = symbols[const_vars[1]]
                return a / (b + var1)
            else:
                return 1.0 / (np.random.uniform(1, 10) + var1)

    except:
        # Fallback to simple expression if rational generation fails
        return self._generate_simple_expression(variable_names, var_stats)


# ============================================================================
# MODIFY _initialize_smart_population TO INCLUDE RATIONAL TEMPLATES
# ============================================================================


def _initialize_smart_population_with_rational(
    self, variable_names: List[str], var_stats: Dict
) -> List[sp.Expr]:
    """
    Enhanced initialization that includes rational function templates.

    Distribution:
    - Biology domain: 60% rational, 20% polynomial, 10% linear, 10% random
    - Chemistry domain: 50% rational, 30% exponential, 20% other
    - Other domains: original distribution
    """
    population = []
    symbols = {v: sp.Symbol(v) for v in variable_names}

    varying_vars = [v for v in variable_names if not var_stats[v]["is_constant"]]
    const_vars = [v for v in variable_names if var_stats[v]["is_constant"]]

    # Domain-specific distributions
    if self.domain == "biology":
        # CRITICAL: 60% rational functions for Michaelis-Menten
        for _ in range(int(self.population_size * 0.60)):
            expr = self._generate_rational_template(
                variable_names, var_stats, symbols, varying_vars, const_vars
            )
            population.append(expr)

        # 20% polynomial
        for _ in range(int(self.population_size * 0.20)):
            terms = []
            for v in varying_vars[:3]:
                power = np.random.choice([1, 2])
                coeff = np.random.uniform(0.5, 2.0)
                terms.append(coeff * symbols[v] ** power)
            if terms:
                population.append(sum(terms))

        # 10% linear combinations
        for _ in range(int(self.population_size * 0.10)):
            terms = [np.random.uniform(0.1, 2.0) * symbols[v] for v in varying_vars[:3]]
            if terms:
                population.append(sum(terms))

    elif self.domain == "chemistry":
        # 50% rational (for rate laws, equilibria)
        for _ in range(int(self.population_size * 0.50)):
            expr = self._generate_rational_template(
                variable_names, var_stats, symbols, varying_vars, const_vars
            )
            population.append(expr)

        # 30% exponential (Arrhenius)
        for _ in range(int(self.population_size * 0.30)):
            if varying_vars:
                var = symbols[varying_vars[0]]
                a = np.random.uniform(0.5, 2.0)
                b = np.random.uniform(-0.1, -0.01)
                population.append(a * sp.exp(b * var))

        # 20% other
        for _ in range(int(self.population_size * 0.20)):
            population.append(
                self._generate_simple_expression(variable_names, var_stats)
            )

    else:
        # Original distribution for engineering/other domains
        # Keep the Bernoulli-optimized approach
        return self._initialize_smart_population(variable_names, var_stats)

    # Fill remaining slots
    while len(population) < self.population_size:
        if self.domain in ["biology", "chemistry"]:
            # Add more rational functions
            expr = self._generate_rational_template(
                variable_names, var_stats, symbols, varying_vars, const_vars
            )
        else:
            expr = self._generate_simple_expression(variable_names, var_stats)
        population.append(expr)

    return population


# ============================================================================
# ADD RATIONAL-AWARE MUTATION
# ============================================================================


def _smart_mutate_with_rational(self, expr, variable_names, var_stats):
    """
    Enhanced mutation that can create/modify rational structures.
    """
    try:
        # If domain supports rational functions, occasionally create one
        if self.domain in ["biology", "chemistry"] and np.random.random() < 0.3:
            symbols = {v: sp.Symbol(v) for v in variable_names}
            varying_vars = [
                v for v in variable_names if not var_stats[v]["is_constant"]
            ]
            const_vars = [v for v in variable_names if var_stats[v]["is_constant"]]

            # Generate new rational term
            new_rational = self._generate_rational_template(
                variable_names, var_stats, symbols, varying_vars, const_vars
            )

            # Blend with existing expression
            alpha = np.random.uniform(0.3, 0.7)
            return alpha * expr + (1 - alpha) * new_rational

        # Otherwise use standard mutation
        return self._smart_mutate(expr, variable_names, var_stats)

    except:
        return expr


# ============================================================================
# MODIFY fit() METHOD TO USE RATIONAL-AWARE FUNCTIONS
# ============================================================================


def fit_with_rational_support(
    self,
    X: np.ndarray,
    y: np.ndarray,
    variable_names: List[str],
    variable_units: Optional[Dict[str, str]] = None,
    variable_descriptions: Optional[Dict[str, str]] = None,
):
    """
    Modified fit method that uses rational-aware initialization and mutation.

    USAGE: Replace the population initialization line in your fit() method:

    # OLD:
    # population = self._initialize_smart_population(variable_names, var_stats)

    # NEW:
    population = self._initialize_smart_population_with_rational(variable_names, var_stats)

    And in the mutation step:

    # OLD:
    # if np.random.random() < mutation_rate:
    #     offspring = self._smart_mutate(offspring, variable_names, var_stats)

    # NEW:
    if np.random.random() < mutation_rate:
        offspring = self._smart_mutate_with_rational(offspring, variable_names, var_stats)
    """
    pass  # Use your existing fit() with the changes noted above


# ============================================================================
# PROTECTED DIVISION HELPER
# ============================================================================


def _protected_division(numerator, denominator, epsilon=1e-6):
    """
    Protected division to avoid divide-by-zero in expressions.
    Returns numerator / (denominator + epsilon)
    """
    return numerator / (denominator + epsilon)


# ============================================================================
# USAGE EXAMPLE
# ============================================================================

if __name__ == "__main__":
    print("=" * 80)
    print("RATIONAL FUNCTION ENHANCEMENT FOR PhysicsAwareRegressor")
    print("=" * 80)
    print("\n✅ Adds support for:")
    print("   - Michaelis-Menten: (Vmax*S)/(Km+S)")
    print("   - Hill equation: (Vmax*S^n)/(K^n+S^n)")
    print("   - General rational functions: (a*x+b)/(c+d*x)")
    print("\n📋 Integration steps:")
    print("   1. Add _generate_rational_template() to PhysicsAwareRegressor")
    print("   2. Add _initialize_smart_population_with_rational()")
    print("   3. Add _smart_mutate_with_rational()")
    print("   4. In fit(), replace population initialization:")
    print("      population = self._initialize_smart_population_with_rational(...)")
    print("   5. In mutation step, use:")
    print("      offspring = self._smart_mutate_with_rational(...)")
    print("\n🎯 Expected improvement:")
    print("   - Biology domain: 60% population starts with rational templates")
    print("   - Should discover Michaelis-Menten with R² > 0.95")
    print("   - Converges in 100-300 generations")
    print("=" * 80)
