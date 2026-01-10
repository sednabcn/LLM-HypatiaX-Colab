"""
Chemistry Domain - Rate Equations
==================================

This module provides comprehensive chemical kinetics calculations including:
- Rate laws and reaction orders
- Arrhenius equation and activation energy
- Half-life calculations for different reaction orders
- Integrated rate laws
- Temperature dependence of reaction rates

All formulas include validation and return detailed results.

Author: Chemistry Domain Team
Version: 1.0.0
"""

import math
from enum import Enum
from typing import Dict, List, Optional, Tuple

# Constants
EPSILON = 1e-12
GAS_CONSTANT = 8.314462618  # J/(mol·K)


class ReactionOrder(Enum):
    """Reaction order types."""

    ZERO = 0
    FIRST = 1
    SECOND = 2


class RateEquationCalculator:
    """Calculator for reaction rate equations."""

    @staticmethod
    def zero_order_rate(
        rate_constant: float, validate: bool = True
    ) -> Dict[str, float]:
        """
        Calculate reaction rate for zero-order reaction.

        Formula: rate = k

        Args:
            rate_constant: Rate constant (M/s)
            validate: Enable input validation

        Returns:
            Dictionary with rate and details
        """
        if validate and rate_constant < 0:
            raise ValueError("Rate constant cannot be negative")

        return {
            "rate": rate_constant,
            "rate_constant": rate_constant,
            "order": 0,
            "formula": "rate = k",
        }

    @staticmethod
    def first_order_rate(
        rate_constant: float, concentration: float, validate: bool = True
    ) -> Dict[str, float]:
        """
        Calculate reaction rate for first-order reaction.

        Formula: rate = k[A]

        Args:
            rate_constant: Rate constant (s⁻¹)
            concentration: Reactant concentration (M)
            validate: Enable input validation

        Returns:
            Dictionary with rate and details
        """
        if validate:
            if rate_constant < 0:
                raise ValueError("Rate constant cannot be negative")
            if concentration < 0:
                raise ValueError("Concentration cannot be negative")

        rate = rate_constant * concentration

        return {
            "rate": rate,
            "rate_constant": rate_constant,
            "concentration": concentration,
            "order": 1,
            "formula": "rate = k[A]",
        }

    @staticmethod
    def second_order_rate(
        rate_constant: float, concentration: float, validate: bool = True
    ) -> Dict[str, float]:
        """
        Calculate reaction rate for second-order reaction (single reactant).

        Formula: rate = k[A]²

        Args:
            rate_constant: Rate constant (M⁻¹s⁻¹)
            concentration: Reactant concentration (M)
            validate: Enable input validation

        Returns:
            Dictionary with rate and details
        """
        if validate:
            if rate_constant < 0:
                raise ValueError("Rate constant cannot be negative")
            if concentration < 0:
                raise ValueError("Concentration cannot be negative")

        rate = rate_constant * concentration**2

        return {
            "rate": rate,
            "rate_constant": rate_constant,
            "concentration": concentration,
            "order": 2,
            "formula": "rate = k[A]²",
        }

    @staticmethod
    def second_order_rate_two_reactants(
        rate_constant: float,
        concentration_a: float,
        concentration_b: float,
        validate: bool = True,
    ) -> Dict[str, float]:
        """
        Calculate reaction rate for second-order reaction (two reactants).

        Formula: rate = k[A][B]

        Args:
            rate_constant: Rate constant (M⁻¹s⁻¹)
            concentration_a: Reactant A concentration (M)
            concentration_b: Reactant B concentration (M)
            validate: Enable input validation

        Returns:
            Dictionary with rate and details
        """
        if validate:
            if rate_constant < 0:
                raise ValueError("Rate constant cannot be negative")
            if concentration_a < 0 or concentration_b < 0:
                raise ValueError("Concentrations cannot be negative")

        rate = rate_constant * concentration_a * concentration_b

        return {
            "rate": rate,
            "rate_constant": rate_constant,
            "concentration_a": concentration_a,
            "concentration_b": concentration_b,
            "order": 2,
            "formula": "rate = k[A][B]",
        }

    @staticmethod
    def general_rate_law(
        rate_constant: float,
        concentrations: List[float],
        orders: List[int],
        validate: bool = True,
    ) -> Dict[str, float]:
        """
        Calculate reaction rate using general rate law.

        Formula: rate = k[A]^m[B]^n...

        Args:
            rate_constant: Rate constant
            concentrations: List of reactant concentrations (M)
            orders: List of reaction orders for each reactant
            validate: Enable input validation

        Returns:
            Dictionary with rate and details
        """
        if validate:
            if rate_constant < 0:
                raise ValueError("Rate constant cannot be negative")
            if len(concentrations) != len(orders):
                raise ValueError("Number of concentrations must match number of orders")
            if any(c < 0 for c in concentrations):
                raise ValueError("Concentrations cannot be negative")
            if any(o < 0 for o in orders):
                raise ValueError("Orders cannot be negative")

        rate = rate_constant
        for conc, order in zip(concentrations, orders):
            rate *= conc**order

        total_order = sum(orders)

        return {
            "rate": rate,
            "rate_constant": rate_constant,
            "concentrations": concentrations,
            "orders": orders,
            "total_order": total_order,
            "formula": "rate = k∏[Reactant]^order",
        }


class IntegratedRateLawCalculator:
    """Calculator for integrated rate laws."""

    @staticmethod
    def zero_order_integrated(
        initial_concentration: float,
        rate_constant: float,
        time: Optional[float] = None,
        final_concentration: Optional[float] = None,
        validate: bool = True,
    ) -> Dict[str, float]:
        """
        Calculate using zero-order integrated rate law.

        Formula: [A]ₜ = [A]₀ - kt

        Provide either time or final_concentration.

        Args:
            initial_concentration: Initial concentration (M)
            rate_constant: Rate constant (M/s)
            time: Time (s)
            final_concentration: Final concentration (M)
            validate: Enable input validation

        Returns:
            Dictionary with concentration and time
        """
        if validate:
            if initial_concentration < 0:
                raise ValueError("Initial concentration cannot be negative")
            if rate_constant < 0:
                raise ValueError("Rate constant cannot be negative")

            provided = sum([time is not None, final_concentration is not None])
            if provided != 1:
                raise ValueError("Provide exactly one of: time or final_concentration")

        if time is not None:
            if validate and time < 0:
                raise ValueError("Time cannot be negative")
            final_concentration = initial_concentration - rate_constant * time
            if validate and final_concentration < 0:
                raise ValueError("Concentration cannot be negative (reaction complete)")
        else:
            if validate and final_concentration < 0:
                raise ValueError("Final concentration cannot be negative")
            if validate and final_concentration > initial_concentration:
                raise ValueError("Final concentration cannot exceed initial")
            time = (initial_concentration - final_concentration) / rate_constant

        return {
            "initial_concentration": initial_concentration,
            "final_concentration": max(0, final_concentration),
            "rate_constant": rate_constant,
            "time": time,
            "order": 0,
            "formula": "[A]ₜ = [A]₀ - kt",
        }

    @staticmethod
    def first_order_integrated(
        initial_concentration: float,
        rate_constant: float,
        time: Optional[float] = None,
        final_concentration: Optional[float] = None,
        validate: bool = True,
    ) -> Dict[str, float]:
        """
        Calculate using first-order integrated rate law.

        Formula: ln[A]ₜ = ln[A]₀ - kt  or  [A]ₜ = [A]₀e^(-kt)

        Provide either time or final_concentration.

        Args:
            initial_concentration: Initial concentration (M)
            rate_constant: Rate constant (s⁻¹)
            time: Time (s)
            final_concentration: Final concentration (M)
            validate: Enable input validation

        Returns:
            Dictionary with concentration and time
        """
        if validate:
            if initial_concentration <= 0:
                raise ValueError("Initial concentration must be positive")
            if rate_constant < 0:
                raise ValueError("Rate constant cannot be negative")

            provided = sum([time is not None, final_concentration is not None])
            if provided != 1:
                raise ValueError("Provide exactly one of: time or final_concentration")

        if time is not None:
            if validate and time < 0:
                raise ValueError("Time cannot be negative")
            final_concentration = initial_concentration * math.exp(
                -rate_constant * time
            )
        else:
            if validate:
                if final_concentration <= 0:
                    raise ValueError("Final concentration must be positive")
                if final_concentration > initial_concentration:
                    raise ValueError("Final concentration cannot exceed initial")
            time = math.log(initial_concentration / final_concentration) / rate_constant

        return {
            "initial_concentration": initial_concentration,
            "final_concentration": final_concentration,
            "rate_constant": rate_constant,
            "time": time,
            "order": 1,
            "formula": "[A]ₜ = [A]₀e^(-kt)",
        }

    @staticmethod
    def second_order_integrated(
        initial_concentration: float,
        rate_constant: float,
        time: Optional[float] = None,
        final_concentration: Optional[float] = None,
        validate: bool = True,
    ) -> Dict[str, float]:
        """
        Calculate using second-order integrated rate law.

        Formula: 1/[A]ₜ = 1/[A]₀ + kt

        Provide either time or final_concentration.

        Args:
            initial_concentration: Initial concentration (M)
            rate_constant: Rate constant (M⁻¹s⁻¹)
            time: Time (s)
            final_concentration: Final concentration (M)
            validate: Enable input validation

        Returns:
            Dictionary with concentration and time
        """
        if validate:
            if initial_concentration <= 0:
                raise ValueError("Initial concentration must be positive")
            if rate_constant < 0:
                raise ValueError("Rate constant cannot be negative")

            provided = sum([time is not None, final_concentration is not None])
            if provided != 1:
                raise ValueError("Provide exactly one of: time or final_concentration")

        if time is not None:
            if validate and time < 0:
                raise ValueError("Time cannot be negative")
            final_concentration = 1.0 / (
                1.0 / initial_concentration + rate_constant * time
            )
        else:
            if validate:
                if final_concentration <= 0:
                    raise ValueError("Final concentration must be positive")
                if final_concentration > initial_concentration:
                    raise ValueError("Final concentration cannot exceed initial")
            time = (
                1.0 / final_concentration - 1.0 / initial_concentration
            ) / rate_constant

        return {
            "initial_concentration": initial_concentration,
            "final_concentration": final_concentration,
            "rate_constant": rate_constant,
            "time": time,
            "order": 2,
            "formula": "1/[A]ₜ = 1/[A]₀ + kt",
        }


class ArrheniusCalculator:
    """Calculator for Arrhenius equation and activation energy."""

    @staticmethod
    def arrhenius_equation(
        activation_energy: float,
        temperature: float,
        pre_exponential_factor: float,
        validate: bool = True,
    ) -> Dict[str, float]:
        """
        Calculate rate constant using Arrhenius equation.

        Formula: k = Ae^(-Ea/RT)

        Args:
            activation_energy: Activation energy (J/mol)
            temperature: Temperature (K)
            pre_exponential_factor: Pre-exponential factor A (units vary)
            validate: Enable input validation

        Returns:
            Dictionary with rate constant and details
        """
        if validate:
            if activation_energy < 0:
                raise ValueError("Activation energy cannot be negative")
            if temperature <= 0:
                raise ValueError("Temperature must be positive (in Kelvin)")
            if pre_exponential_factor <= 0:
                raise ValueError("Pre-exponential factor must be positive")

        # k = A * exp(-Ea/RT)
        exponent = -activation_energy / (GAS_CONSTANT * temperature)
        rate_constant = pre_exponential_factor * math.exp(exponent)

        return {
            "rate_constant": rate_constant,
            "activation_energy": activation_energy,
            "activation_energy_kJ_mol": activation_energy / 1000.0,
            "temperature": temperature,
            "temperature_celsius": temperature - 273.15,
            "pre_exponential_factor": pre_exponential_factor,
            "gas_constant": GAS_CONSTANT,
            "formula": "k = Ae^(-Ea/RT)",
        }

    @staticmethod
    def activation_energy_from_two_temperatures(
        rate_constant_1: float,
        temperature_1: float,
        rate_constant_2: float,
        temperature_2: float,
        validate: bool = True,
    ) -> Dict[str, float]:
        """
        Calculate activation energy from rate constants at two temperatures.

        Formula: ln(k₂/k₁) = (Ea/R)(1/T₁ - 1/T₂)

        Args:
            rate_constant_1: Rate constant at T₁
            temperature_1: Temperature 1 (K)
            rate_constant_2: Rate constant at T₂
            temperature_2: Temperature 2 (K)
            validate: Enable input validation

        Returns:
            Dictionary with activation energy
        """
        if validate:
            if rate_constant_1 <= 0 or rate_constant_2 <= 0:
                raise ValueError("Rate constants must be positive")
            if temperature_1 <= 0 or temperature_2 <= 0:
                raise ValueError("Temperatures must be positive (in Kelvin)")
            if abs(temperature_1 - temperature_2) < EPSILON:
                raise ValueError("Temperatures must be different")

        # Ea = R * ln(k2/k1) / (1/T1 - 1/T2)
        ln_ratio = math.log(rate_constant_2 / rate_constant_1)
        temp_term = 1.0 / temperature_1 - 1.0 / temperature_2

        activation_energy = GAS_CONSTANT * ln_ratio / temp_term

        # Calculate pre-exponential factor using k₁
        # A = k₁ * exp(Ea/RT₁)
        pre_exponential_factor = rate_constant_1 * math.exp(
            activation_energy / (GAS_CONSTANT * temperature_1)
        )

        return {
            "activation_energy": activation_energy,
            "activation_energy_kJ_mol": activation_energy / 1000.0,
            "pre_exponential_factor": pre_exponential_factor,
            "rate_constant_1": rate_constant_1,
            "temperature_1": temperature_1,
            "rate_constant_2": rate_constant_2,
            "temperature_2": temperature_2,
            "formula": "ln(k₂/k₁) = (Ea/R)(1/T₁ - 1/T₂)",
        }

    @staticmethod
    def rate_constant_at_new_temperature(
        rate_constant_initial: float,
        temperature_initial: float,
        temperature_new: float,
        activation_energy: float,
        validate: bool = True,
    ) -> Dict[str, float]:
        """
        Calculate rate constant at a new temperature.

        Formula: ln(k₂/k₁) = (Ea/R)(1/T₁ - 1/T₂)

        Args:
            rate_constant_initial: Initial rate constant
            temperature_initial: Initial temperature (K)
            temperature_new: New temperature (K)
            activation_energy: Activation energy (J/mol)
            validate: Enable input validation

        Returns:
            Dictionary with new rate constant
        """
        if validate:
            if rate_constant_initial <= 0:
                raise ValueError("Rate constant must be positive")
            if temperature_initial <= 0 or temperature_new <= 0:
                raise ValueError("Temperatures must be positive (in Kelvin)")
            if activation_energy < 0:
                raise ValueError("Activation energy cannot be negative")

        # k₂ = k₁ * exp[(Ea/R)(1/T₁ - 1/T₂)]
        exponent = (activation_energy / GAS_CONSTANT) * (
            1.0 / temperature_initial - 1.0 / temperature_new
        )
        rate_constant_new = rate_constant_initial * math.exp(exponent)

        # Calculate ratio
        rate_ratio = rate_constant_new / rate_constant_initial

        # Temperature change
        temp_change = temperature_new - temperature_initial

        return {
            "rate_constant_new": rate_constant_new,
            "rate_constant_initial": rate_constant_initial,
            "temperature_initial": temperature_initial,
            "temperature_new": temperature_new,
            "temperature_change": temp_change,
            "activation_energy": activation_energy,
            "activation_energy_kJ_mol": activation_energy / 1000.0,
            "rate_ratio": rate_ratio,
            "percent_change": (rate_ratio - 1.0) * 100,
            "formula": "k₂ = k₁exp[(Ea/R)(1/T₁ - 1/T₂)]",
        }

    @staticmethod
    def collision_frequency_factor(
        temperature: float,
        molecular_diameter: float,
        molecular_mass: float,
        validate: bool = True,
    ) -> Dict[str, float]:
        """
        Calculate collision frequency factor from collision theory.

        Formula: Z = πd²√(8kT/πμ) × N_A

        Args:
            temperature: Temperature (K)
            molecular_diameter: Molecular diameter (m)
            molecular_mass: Molecular mass (kg/mol)
            validate: Enable input validation

        Returns:
            Dictionary with collision frequency
        """
        if validate:
            if temperature <= 0:
                raise ValueError("Temperature must be positive")
            if molecular_diameter <= 0:
                raise ValueError("Molecular diameter must be positive")
            if molecular_mass <= 0:
                raise ValueError("Molecular mass must be positive")

        k_b = 1.380649e-23  # Boltzmann constant (J/K)
        N_A = 6.02214076e23  # Avogadro's number

        # Reduced mass (assuming same molecules)
        reduced_mass = molecular_mass / (2.0 * N_A)

        # Average velocity
        avg_velocity = math.sqrt(8 * k_b * temperature / (math.pi * reduced_mass))

        # Collision cross-section
        cross_section = math.pi * molecular_diameter**2

        # Collision frequency per molecule per unit concentration
        Z = cross_section * avg_velocity * N_A

        return {
            "collision_frequency": Z,
            "temperature": temperature,
            "molecular_diameter": molecular_diameter,
            "molecular_mass": molecular_mass,
            "average_velocity": avg_velocity,
            "cross_section": cross_section,
            "formula": "Z = πd²√(8kT/πμ) × N_A",
        }


class HalfLifeCalculator:
    """Calculator for reaction half-lives."""

    @staticmethod
    def zero_order_half_life(
        initial_concentration: float, rate_constant: float, validate: bool = True
    ) -> Dict[str, float]:
        """
        Calculate half-life for zero-order reaction.

        Formula: t₁/₂ = [A]₀/(2k)

        Args:
            initial_concentration: Initial concentration (M)
            rate_constant: Rate constant (M/s)
            validate: Enable input validation

        Returns:
            Dictionary with half-life
        """
        if validate:
            if initial_concentration <= 0:
                raise ValueError("Initial concentration must be positive")
            if rate_constant <= 0:
                raise ValueError("Rate constant must be positive")

        half_life = initial_concentration / (2 * rate_constant)

        # Time to complete reaction
        time_complete = initial_concentration / rate_constant

        return {
            "half_life": half_life,
            "initial_concentration": initial_concentration,
            "rate_constant": rate_constant,
            "time_to_completion": time_complete,
            "order": 0,
            "concentration_dependent": True,
            "formula": "t₁/₂ = [A]₀/(2k)",
        }

    @staticmethod
    def first_order_half_life(
        rate_constant: float, validate: bool = True
    ) -> Dict[str, float]:
        """
        Calculate half-life for first-order reaction.

        Formula: t₁/₂ = ln(2)/k = 0.693/k

        Args:
            rate_constant: Rate constant (s⁻¹)
            validate: Enable input validation

        Returns:
            Dictionary with half-life
        """
        if validate:
            if rate_constant <= 0:
                raise ValueError("Rate constant must be positive")

        half_life = math.log(2) / rate_constant

        # Additional useful time constants
        time_90_percent = math.log(10) / rate_constant  # Time for 90% decay
        time_99_percent = math.log(100) / rate_constant  # Time for 99% decay

        return {
            "half_life": half_life,
            "rate_constant": rate_constant,
            "time_90_percent_decay": time_90_percent,
            "time_99_percent_decay": time_99_percent,
            "order": 1,
            "concentration_dependent": False,
            "ln_2": math.log(2),
            "formula": "t₁/₂ = ln(2)/k",
        }

    @staticmethod
    def second_order_half_life(
        initial_concentration: float, rate_constant: float, validate: bool = True
    ) -> Dict[str, float]:
        """
        Calculate half-life for second-order reaction.

        Formula: t₁/₂ = 1/(k[A]₀)

        Args:
            initial_concentration: Initial concentration (M)
            rate_constant: Rate constant (M⁻¹s⁻¹)
            validate: Enable input validation

        Returns:
            Dictionary with half-life
        """
        if validate:
            if initial_concentration <= 0:
                raise ValueError("Initial concentration must be positive")
            if rate_constant <= 0:
                raise ValueError("Rate constant must be positive")

        half_life = 1.0 / (rate_constant * initial_concentration)

        # Second half-life (different for 2nd order!)
        second_half_life = 1.0 / (rate_constant * initial_concentration / 2.0)

        return {
            "half_life": half_life,
            "second_half_life": second_half_life,
            "initial_concentration": initial_concentration,
            "rate_constant": rate_constant,
            "order": 2,
            "concentration_dependent": True,
            "half_life_ratio": second_half_life / half_life,
            "formula": "t₁/₂ = 1/(k[A]₀)",
        }

    @staticmethod
    def number_of_half_lives(
        initial_concentration: float, final_concentration: float, validate: bool = True
    ) -> Dict[str, float]:
        """
        Calculate number of half-lives elapsed (first-order only).

        Formula: n = log₂([A]₀/[A]ₜ)

        Args:
            initial_concentration: Initial concentration (M)
            final_concentration: Final concentration (M)
            validate: Enable input validation

        Returns:
            Dictionary with number of half-lives
        """
        if validate:
            if initial_concentration <= 0:
                raise ValueError("Initial concentration must be positive")
            if final_concentration <= 0:
                raise ValueError("Final concentration must be positive")
            if final_concentration > initial_concentration:
                raise ValueError("Final concentration cannot exceed initial")

        ratio = initial_concentration / final_concentration
        n_half_lives = math.log2(ratio)

        # Calculate percent remaining
        percent_remaining = (final_concentration / initial_concentration) * 100
        percent_reacted = 100.0 - percent_remaining

        return {
            "n_half_lives": n_half_lives,
            "initial_concentration": initial_concentration,
            "final_concentration": final_concentration,
            "concentration_ratio": ratio,
            "percent_remaining": percent_remaining,
            "percent_reacted": percent_reacted,
            "formula": "n = log₂([A]₀/[A]ₜ)",
        }

    @staticmethod
    def concentration_after_n_half_lives(
        initial_concentration: float, n_half_lives: float, validate: bool = True
    ) -> Dict[str, float]:
        """
        Calculate concentration after n half-lives (first-order).

        Formula: [A]ₜ = [A]₀/2ⁿ

        Args:
            initial_concentration: Initial concentration (M)
            n_half_lives: Number of half-lives
            validate: Enable input validation

        Returns:
            Dictionary with concentration
        """
        if validate:
            if initial_concentration <= 0:
                raise ValueError("Initial concentration must be positive")
            if n_half_lives < 0:
                raise ValueError("Number of half-lives cannot be negative")

        final_concentration = initial_concentration / (2**n_half_lives)
        percent_remaining = (final_concentration / initial_concentration) * 100

        return {
            "final_concentration": final_concentration,
            "initial_concentration": initial_concentration,
            "n_half_lives": n_half_lives,
            "percent_remaining": percent_remaining,
            "formula": "[A]ₜ = [A]₀/2ⁿ",
        }


class KineticsCalculator:
    """Comprehensive kinetics calculator combining all subcalculators."""

    def __init__(self):
        self.rate_equation = RateEquationCalculator()
        self.integrated = IntegratedRateLawCalculator()
        self.arrhenius = ArrheniusCalculator()
        self.half_life = HalfLifeCalculator()

    def determine_reaction_order(
        self, concentrations: List[float], times: List[float], validate: bool = True
    ) -> Dict[str, any]:
        """
        Attempt to determine reaction order from concentration vs time data.

        Tests zero, first, and second order fits.

        Args:
            concentrations: List of concentrations at different times (M)
            times: List of corresponding times (s)
            validate: Enable input validation

        Returns:
            Dictionary with likely order and analysis
        """
        if validate:
            if len(concentrations) != len(times):
                raise ValueError("Concentrations and times must have same length")
            if len(concentrations) < 3:
                raise ValueError("Need at least 3 data points")
            if any(c <= 0 for c in concentrations):
                raise ValueError("Concentrations must be positive")
            if any(t < 0 for t in times):
                raise ValueError("Times cannot be negative")

        n = len(concentrations)

        # Test zero-order: [A] vs t (linear)
        # Calculate correlation
        def calculate_linearity(x_vals, y_vals):
            n = len(x_vals)
            mean_x = sum(x_vals) / n
            mean_y = sum(y_vals) / n

            numerator = sum(
                (x_vals[i] - mean_x) * (y_vals[i] - mean_y) for i in range(n)
            )
            denominator = math.sqrt(
                sum((x_vals[i] - mean_x) ** 2 for i in range(n))
                * sum((y_vals[i] - mean_y) ** 2 for i in range(n))
            )

            return abs(numerator / denominator) if denominator > EPSILON else 0

        # Zero order: [A] vs t
        zero_order_r = calculate_linearity(times, concentrations)

        # First order: ln[A] vs t
        ln_concentrations = [math.log(c) for c in concentrations]
        first_order_r = calculate_linearity(times, ln_concentrations)

        # Second order: 1/[A] vs t
        inverse_concentrations = [1.0 / c for c in concentrations]
        second_order_r = calculate_linearity(times, inverse_concentrations)

        # Determine best fit
        correlations = {0: zero_order_r, 1: first_order_r, 2: second_order_r}

        best_order = max(correlations, key=correlations.get)

        return {
            "likely_order": best_order,
            "zero_order_correlation": zero_order_r,
            "first_order_correlation": first_order_r,
            "second_order_correlation": second_order_r,
            "best_correlation": correlations[best_order],
            "data_points": n,
            "note": "Higher correlation indicates better fit",
        }


# Example usage and testing
if __name__ == "__main__":
    print("=" * 70)
    print("RATE EQUATIONS - COMPREHENSIVE DEMONSTRATION")
    print("=" * 70)

    # 1. Rate laws
    print("\n1. RATE LAWS")
    print("-" * 70)
    rate_calc = RateEquationCalculator()

    first_order = rate_calc.first_order_rate(
        rate_constant=0.05, concentration=2.0
    )  # s⁻¹  # M
    print(f"First-order: rate = {first_order['rate']:.3f} M/s")
    print(f"Formula: {first_order['formula']}")

    second_order = rate_calc.second_order_rate(
        rate_constant=0.1, concentration=2.0
    )  # M⁻¹s⁻¹  # M
    print(f"Second-order: rate = {second_order['rate']:.3f} M/s")

    two_reactants = rate_calc.second_order_rate_two_reactants(
        rate_constant=0.05, concentration_a=1.5, concentration_b=2.0
    )
    print(f"Two reactants: rate = {two_reactants['rate']:.3f} M/s")

    # 2. Integrated rate laws
    print("\n2. INTEGRATED RATE LAWS")
    print("-" * 70)
    integrated_calc = IntegratedRateLawCalculator()

    print("Zero-order reaction:")
    zero_int = integrated_calc.zero_order_integrated(
        initial_concentration=2.0, rate_constant=0.1, time=5.0  # M  # M/s  # s
    )
    print(f"  [A]₀ = {zero_int['initial_concentration']:.2f} M")
    print(f"  After {zero_int['time']}s: [A] = {zero_int['final_concentration']:.2f} M")

    print("\nFirst-order reaction:")
    first_int = integrated_calc.first_order_integrated(
        initial_concentration=1.0, rate_constant=0.1, time=10.0  # M  # s⁻¹  # s
    )
    print(f"  [A]₀ = {first_int['initial_concentration']:.2f} M")
    print(
        f"  After {first_int['time']}s: [A] = {first_int['final_concentration']:.4f} M"
    )

    print("\nSecond-order reaction:")
    second_int = integrated_calc.second_order_integrated(
        initial_concentration=1.0, rate_constant=0.5, time=2.0  # M  # M⁻¹s⁻¹  # s
    )
    print(f"  [A]₀ = {second_int['initial_concentration']:.2f} M")
    print(
        f"  After {second_int['time']}s: [A] = {second_int['final_concentration']:.3f} M"
    )

    # 3. Arrhenius equation
    print("\n3. ARRHENIUS EQUATION")
    print("-" * 70)
    arrhenius_calc = ArrheniusCalculator()

    k = arrhenius_calc.arrhenius_equation(
        activation_energy=75000,
        temperature=298.15,
        pre_exponential_factor=1e10,  # J/mol  # K (25°C)  # s⁻¹
    )
    print(f"Activation energy: {k['activation_energy_kJ_mol']:.1f} kJ/mol")
    print(f"Temperature: {k['temperature']:.2f} K ({k['temperature_celsius']:.2f}°C)")
    print(f"Rate constant: {k['rate_constant']:.3e} s⁻¹")

    # Activation energy from two temperatures
    print("\nCalculate Ea from two temperatures:")
    ea = arrhenius_calc.activation_energy_from_two_temperatures(
        rate_constant_1=0.01,  # s⁻¹
        temperature_1=298,  # K (25°C)
        rate_constant_2=0.05,  # s⁻¹
        temperature_2=318,  # K (45°C)
    )
    print(f"  k₁ = {ea['rate_constant_1']:.3f} s⁻¹ at {ea['temperature_1']:.0f} K")
    print(f"  k₂ = {ea['rate_constant_2']:.3f} s⁻¹ at {ea['temperature_2']:.0f} K")
    print(f"  Ea = {ea['activation_energy_kJ_mol']:.2f} kJ/mol")
    print(f"  A = {ea['pre_exponential_factor']:.2e}")

    # Rate constant at new temperature
    print("\nPredict k at new temperature:")
    new_k = arrhenius_calc.rate_constant_at_new_temperature(
        rate_constant_initial=0.01,
        temperature_initial=298,
        temperature_new=308,  # 10°C increase
        activation_energy=50000,  # J/mol
    )
    print(
        f"  Initial: k = {new_k['rate_constant_initial']:.3f} at {new_k['temperature_initial']:.0f} K"
    )
    print(
        f"  New: k = {new_k['rate_constant_new']:.3f} at {new_k['temperature_new']:.0f} K"
    )
    print(f"  Rate increases by {new_k['percent_change']:.1f}%")
    print(f"  Rate ratio: {new_k['rate_ratio']:.2f}×")

    # 4. Half-life calculations
    print("\n4. HALF-LIFE CALCULATIONS")
    print("-" * 70)
    half_life_calc = HalfLifeCalculator()

    print("Zero-order:")
    t_half_zero = half_life_calc.zero_order_half_life(
        initial_concentration=2.0, rate_constant=0.1
    )
    print(f"  t₁/₂ = {t_half_zero['half_life']:.2f} s")
    print(f"  Time to completion = {t_half_zero['time_to_completion']:.2f} s")
    print(f"  Concentration dependent: {t_half_zero['concentration_dependent']}")

    print("\nFirst-order:")
    t_half_first = half_life_calc.first_order_half_life(rate_constant=0.1)  # s⁻¹
    print(f"  t₁/₂ = {t_half_first['half_life']:.2f} s")
    print(f"  Time for 90% decay = {t_half_first['time_90_percent_decay']:.2f} s")
    print(f"  Time for 99% decay = {t_half_first['time_99_percent_decay']:.2f} s")
    print(f"  Concentration independent: {not t_half_first['concentration_dependent']}")

    print("\nSecond-order:")
    t_half_second = half_life_calc.second_order_half_life(
        initial_concentration=1.0, rate_constant=0.1
    )  # M  # M⁻¹s⁻¹
    print(f"  First t₁/₂ = {t_half_second['half_life']:.2f} s")
    print(f"  Second t₁/₂ = {t_half_second['second_half_life']:.2f} s")
    print(f"  Ratio = {t_half_second['half_life_ratio']:.1f}× (increases with time)")

    # Number of half-lives
    print("\nNumber of half-lives elapsed:")
    n_half = half_life_calc.number_of_half_lives(
        initial_concentration=100.0,
        final_concentration=12.5,  # M  # M (after 3 half-lives)
    )
    print(
        f"  [A]₀ = {n_half['initial_concentration']:.1f} M → [A] = {n_half['final_concentration']:.1f} M"
    )
    print(f"  Number of half-lives: {n_half['n_half_lives']:.1f}")
    print(f"  Percent remaining: {n_half['percent_remaining']:.1f}%")
    print(f"  Percent reacted: {n_half['percent_reacted']:.1f}%")

    # Concentration after n half-lives
    print("\nConcentration after specific half-lives:")
    conc_after = half_life_calc.concentration_after_n_half_lives(
        initial_concentration=80.0, n_half_lives=4.0
    )
    print(f"  After {conc_after['n_half_lives']:.1f} half-lives:")
    print(f"  [A] = {conc_after['final_concentration']:.2f} M")
    print(f"  ({conc_after['percent_remaining']:.2f}% remaining)")

    # 5. Comprehensive kinetics analysis
    print("\n5. REACTION ORDER DETERMINATION")
    print("-" * 70)
    kinetics_calc = KineticsCalculator()

    # Simulated first-order data
    times = [0, 10, 20, 30, 40, 50]
    concentrations = [1.0, 0.9048, 0.8187, 0.7408, 0.6703, 0.6065]

    order_analysis = kinetics_calc.determine_reaction_order(
        concentrations=concentrations, times=times
    )
    print(f"Data points: {order_analysis['data_points']}")
    print(f"Likely reaction order: {order_analysis['likely_order']}")
    print(f"\nLinearity analysis (R²):")
    print(f"  Zero-order:  {order_analysis['zero_order_correlation']:.4f}")
    print(f"  First-order: {order_analysis['first_order_correlation']:.4f}")
    print(f"  Second-order: {order_analysis['second_order_correlation']:.4f}")
    print(f"Best correlation: {order_analysis['best_correlation']:.4f}")

    # 6. Collision theory
    print("\n6. COLLISION THEORY")
    print("-" * 70)
    collision = arrhenius_calc.collision_frequency_factor(
        temperature=298,
        molecular_diameter=3.0e-10,
        molecular_mass=0.032,  # K  # m (3 Å)  # kg/mol (O₂)
    )
    print(f"Temperature: {collision['temperature']:.0f} K")
    print(f"Molecular diameter: {collision['molecular_diameter']*1e10:.1f} Å")
    print(f"Collision frequency: {collision['collision_frequency']:.3e} M⁻¹s⁻¹")
    print(f"Average molecular velocity: {collision['average_velocity']:.1f} m/s")
    print(f"Cross-section: {collision['cross_section']*1e20:.2f} Å²")

    # 7. Complete reaction example
    print("\n7. COMPLETE REACTION ANALYSIS")
    print("-" * 70)
    print("Decomposition of N₂O₅ (first-order)")
    print("2 N₂O₅(g) → 4 NO₂(g) + O₂(g)")

    # Given data
    k_rxn = 0.0005  # s⁻¹ at 45°C
    initial_conc = 0.1  # M

    # Calculate half-life
    t_half = kinetics_calc.half_life.first_order_half_life(k_rxn)
    print(f"\nRate constant: {k_rxn:.4f} s⁻¹")
    print(f"Half-life: {t_half['half_life']:.1f} s ({t_half['half_life']/60:.1f} min)")

    # Calculate concentration after 1 hour
    time_1hr = 3600  # seconds
    final_conc = kinetics_calc.integrated.first_order_integrated(
        initial_concentration=initial_conc, rate_constant=k_rxn, time=time_1hr
    )
    print(f"\nAfter 1 hour:")
    print(f"  [N₂O₅] = {final_conc['final_concentration']:.4f} M")
    print(f"  ({(final_conc['final_concentration']/initial_conc)*100:.1f}% remaining)")

    # How many half-lives?
    n_half_lives = kinetics_calc.half_life.number_of_half_lives(
        initial_concentration=initial_conc,
        final_concentration=final_conc["final_concentration"],
    )
    print(f"  Number of half-lives: {n_half_lives['n_half_lives']:.2f}")

    print("\n" + "=" * 70)
    print("All demonstrations completed successfully!")
    print("=" * 70)

    """
    1. Enhanced ArrheniusCalculator:

✅ Collision frequency factor from collision theory
✅ Temperature in both Kelvin and Celsius
✅ Activation energy in both J/mol and kJ/mol
✅ Percent change in rate constant with temperature
✅ Average molecular velocity calculations

2. Expanded HalfLifeCalculator:

✅ Time for 90% and 99% decay (first-order)
✅ Second half-life for second-order (doubles!)
✅ Time to completion for zero-order
✅ concentration_after_n_half_lives() - new function
✅ Percent reacted in addition to percent remaining

3. New KineticsCalculator Method:

✅ determine_reaction_order() - Analyzes concentration vs time data
✅ Tests zero, first, and second-order fits
✅ Returns correlation coefficients (R²)
✅ Identifies likely reaction order from experimental data

4. Comprehensive Demo:
The demonstration now includes 7 complete sections:

Rate laws (all orders)
Integrated rate laws (complete analysis)
Arrhenius equation (3 scenarios)
Half-life calculations (all details)
Reaction order determination (from data)
Collision theory (molecular-level)
Complete reaction example (N₂O₅ decomposition)

📊 Key Improvements:

More detailed return dictionaries with additional calculated values
Better validation and error messages
Temperature conversions included automatically
Multiple time constants (t₁/₂, t₉₀%, t₉₉%)
Ratio analysis for second-order reactions
Real-world example with complete analysis

The rewritten module is now even more comprehensive and ready for production use! 🧪⚗️
    """
