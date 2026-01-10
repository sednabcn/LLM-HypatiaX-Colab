"""
Unit Tests - Chemistry Validation
==================================

Comprehensive unit tests for chemistry domain validations including:
- Rate equations: rate laws, integrated laws, Arrhenius
- Equilibrium: Kc, Ka, Kb, Ksp, buffers
- Half-lives and reaction orders

Tests cover:
- Edge cases and boundary conditions
- Invalid input validation
- Error message verification
- Chemical constraint enforcement
"""

import math
import sys
from pathlib import Path

import pytest

# Add parent directory to path for imports
sys.path.insert(0, str(Path(__file__).parent.parent.parent))

# Import chemistry modules
try:
    from equilibrium_formulas import (
        WATER_ION_PRODUCT_25C,
        AcidBaseEquilibriumCalculator,
        EquilibriumCalculator,
        EquilibriumConstantCalculator,
        SolubilityCalculator,
    )
    from rate_equations import (
        GAS_CONSTANT,
        ArrheniusCalculator,
        HalfLifeCalculator,
        IntegratedRateLawCalculator,
        KineticsCalculator,
        RateEquationCalculator,
    )
except ImportError as e:
    pytest.skip(f"Required modules not found: {e}", allow_module_level=True)


# ============================================================================
# RATE EQUATIONS TESTS
# ============================================================================


class TestRateEquationValidation:
    """Test rate equation calculations validation."""

    def test_rate_negative_rate_constant_raises_error(self):
        """Test that negative rate constant raises ValueError."""
        calc = RateEquationCalculator()
        with pytest.raises(ValueError, match="Rate constant cannot be negative"):
            calc.zero_order_rate(rate_constant=-0.05)

    def test_first_order_negative_concentration_raises_error(self):
        """Test that negative concentration raises ValueError."""
        calc = RateEquationCalculator()
        with pytest.raises(ValueError, match="Concentration cannot be negative"):
            calc.first_order_rate(rate_constant=0.1, concentration=-2.0)

    def test_second_order_negative_concentration_raises_error(self):
        """Test that negative concentration raises ValueError."""
        calc = RateEquationCalculator()
        with pytest.raises(ValueError, match="Concentration cannot be negative"):
            calc.second_order_rate(rate_constant=0.1, concentration=-1.5)

    def test_general_rate_law_mismatched_lengths_raises_error(self):
        """Test that mismatched concentrations and orders raises error."""
        calc = RateEquationCalculator()
        with pytest.raises(ValueError, match="must match number of orders"):
            calc.general_rate_law(
                rate_constant=0.1, concentrations=[1.0, 2.0], orders=[1, 2, 1]
            )  # Length mismatch

    def test_general_rate_law_negative_order_raises_error(self):
        """Test that negative reaction order raises ValueError."""
        calc = RateEquationCalculator()
        with pytest.raises(ValueError, match="Orders cannot be negative"):
            calc.general_rate_law(
                rate_constant=0.1, concentrations=[1.0, 2.0], orders=[-1, 2]
            )  # Negative order

    def test_zero_order_rate_constant_equals_rate(self):
        """Test that zero-order rate equals rate constant."""
        calc = RateEquationCalculator()
        result = calc.zero_order_rate(rate_constant=0.05)
        assert result["rate"] == 0.05


class TestIntegratedRateLawValidation:
    """Test integrated rate law validation."""

    def test_zero_order_missing_parameter_raises_error(self):
        """Test that missing time or concentration raises error."""
        calc = IntegratedRateLawCalculator()
        with pytest.raises(ValueError, match="Provide exactly one"):
            calc.zero_order_integrated(initial_concentration=2.0, rate_constant=0.1)

    def test_zero_order_negative_time_raises_error(self):
        """Test that negative time raises ValueError."""
        calc = IntegratedRateLawCalculator()
        with pytest.raises(ValueError, match="Time cannot be negative"):
            calc.zero_order_integrated(
                initial_concentration=2.0, rate_constant=0.1, time=-5.0
            )

    def test_zero_order_final_exceeds_initial_raises_error(self):
        """Test that final > initial concentration raises error."""
        calc = IntegratedRateLawCalculator()
        with pytest.raises(ValueError, match="cannot exceed initial"):
            calc.zero_order_integrated(
                initial_concentration=1.0, rate_constant=0.1, final_concentration=2.0
            )

    def test_first_order_zero_initial_raises_error(self):
        """Test that zero initial concentration raises ValueError."""
        calc = IntegratedRateLawCalculator()
        with pytest.raises(ValueError, match="must be positive"):
            calc.first_order_integrated(
                initial_concentration=0.0, rate_constant=0.1, time=10.0
            )

    def test_first_order_final_exceeds_initial_raises_error(self):
        """Test that final > initial concentration raises error."""
        calc = IntegratedRateLawCalculator()
        with pytest.raises(ValueError, match="cannot exceed initial"):
            calc.first_order_integrated(
                initial_concentration=1.0, rate_constant=0.1, final_concentration=1.5
            )

    def test_second_order_negative_concentration_raises_error(self):
        """Test that negative concentration raises ValueError."""
        calc = IntegratedRateLawCalculator()
        with pytest.raises(ValueError, match="must be positive"):
            calc.second_order_integrated(
                initial_concentration=-1.0, rate_constant=0.5, time=2.0
            )

    def test_first_order_exponential_decay(self):
        """Test that first-order follows exponential decay."""
        calc = IntegratedRateLawCalculator()

        # After one half-life, should be 50% remaining
        k = 0.693  # Such that t_1/2 = 1.0 s
        result = calc.first_order_integrated(
            initial_concentration=1.0, rate_constant=k, time=1.0
        )  # One half-life
        assert abs(result["final_concentration"] - 0.5) < 0.01


class TestArrheniusValidation:
    """Test Arrhenius equation validation."""

    def test_arrhenius_negative_activation_energy_raises_error(self):
        """Test that negative activation energy raises ValueError."""
        calc = ArrheniusCalculator()
        with pytest.raises(ValueError, match="Activation energy cannot be negative"):
            calc.arrhenius_equation(
                activation_energy=-50000,
                temperature=298.15,
                pre_exponential_factor=1e10,
            )

    def test_arrhenius_zero_temperature_raises_error(self):
        """Test that zero Kelvin raises ValueError."""
        calc = ArrheniusCalculator()
        with pytest.raises(ValueError, match="Temperature must be positive"):
            calc.arrhenius_equation(
                activation_energy=50000, temperature=0.0, pre_exponential_factor=1e10
            )

    def test_arrhenius_negative_pre_exponential_raises_error(self):
        """Test that negative pre-exponential factor raises error."""
        calc = ArrheniusCalculator()
        with pytest.raises(ValueError, match="Pre-exponential factor must be positive"):
            calc.arrhenius_equation(
                activation_energy=50000,
                temperature=298.15,
                pre_exponential_factor=-1e10,
            )

    def test_activation_energy_same_temperatures_raises_error(self):
        """Test that identical temperatures raises ValueError."""
        calc = ArrheniusCalculator()
        with pytest.raises(ValueError, match="Temperatures must be different"):
            calc.activation_energy_from_two_temperatures(
                rate_constant_1=0.01,
                temperature_1=298.0,
                rate_constant_2=0.05,
                temperature_2=298.0,  # Same temperature
            )

    def test_activation_energy_negative_rate_constant_raises_error(self):
        """Test that negative rate constant raises ValueError."""
        calc = ArrheniusCalculator()
        with pytest.raises(ValueError, match="Rate constants must be positive"):
            calc.activation_energy_from_two_temperatures(
                rate_constant_1=-0.01,
                temperature_1=298.0,
                rate_constant_2=0.05,
                temperature_2=318.0,
            )

    def test_higher_temperature_increases_rate_constant(self):
        """Test that increasing temperature increases rate constant."""
        calc = ArrheniusCalculator()

        k_298 = calc.arrhenius_equation(
            activation_energy=50000, temperature=298.15, pre_exponential_factor=1e10
        )

        k_308 = calc.arrhenius_equation(
            activation_energy=50000,
            temperature=308.15,
            pre_exponential_factor=1e10,  # 10 K higher
        )

        assert k_308["rate_constant"] > k_298["rate_constant"]

    def test_collision_frequency_negative_temperature_raises_error(self):
        """Test that negative temperature raises ValueError."""
        calc = ArrheniusCalculator()
        with pytest.raises(ValueError, match="Temperature must be positive"):
            calc.collision_frequency_factor(
                temperature=-298.0, molecular_diameter=3e-10, molecular_mass=0.032
            )


class TestHalfLifeValidation:
    """Test half-life calculations validation."""

    def test_zero_order_half_life_negative_concentration_raises_error(self):
        """Test that negative concentration raises ValueError."""
        calc = HalfLifeCalculator()
        with pytest.raises(ValueError, match="must be positive"):
            calc.zero_order_half_life(initial_concentration=-2.0, rate_constant=0.1)

    def test_first_order_half_life_negative_rate_constant_raises_error(self):
        """Test that negative rate constant raises ValueError."""
        calc = HalfLifeCalculator()
        with pytest.raises(ValueError, match="Rate constant must be positive"):
            calc.first_order_half_life(rate_constant=-0.1)

    def test_second_order_half_life_zero_concentration_raises_error(self):
        """Test that zero concentration raises ValueError."""
        calc = HalfLifeCalculator()
        with pytest.raises(ValueError, match="must be positive"):
            calc.second_order_half_life(initial_concentration=0.0, rate_constant=0.1)

    def test_number_of_half_lives_final_exceeds_initial_raises_error(self):
        """Test that final > initial raises ValueError."""
        calc = HalfLifeCalculator()
        with pytest.raises(ValueError, match="cannot exceed initial"):
            calc.number_of_half_lives(
                initial_concentration=100.0, final_concentration=150.0
            )

    def test_concentration_after_half_lives_negative_n_raises_error(self):
        """Test that negative n raises ValueError."""
        calc = HalfLifeCalculator()
        with pytest.raises(ValueError, match="cannot be negative"):
            calc.concentration_after_n_half_lives(
                initial_concentration=80.0, n_half_lives=-2.0
            )

    def test_first_order_half_life_concentration_independent(self):
        """Test that first-order half-life is concentration independent."""
        calc = HalfLifeCalculator()
        k = 0.1  # s^-1

        result = calc.first_order_half_life(rate_constant=k)
        expected = math.log(2) / k

        assert abs(result["half_life"] - expected) < 1e-10
        assert result["concentration_dependent"] == False

    def test_zero_order_half_life_concentration_dependent(self):
        """Test that zero-order half-life depends on concentration."""
        calc = HalfLifeCalculator()

        # Higher concentration = longer half-life for zero-order
        result1 = calc.zero_order_half_life(
            initial_concentration=2.0, rate_constant=0.1
        )

        result2 = calc.zero_order_half_life(
            initial_concentration=4.0, rate_constant=0.1
        )

        assert result2["half_life"] > result1["half_life"]
        assert result1["concentration_dependent"] == True

    def test_second_order_half_life_increases_with_time(self):
        """Test that second-order half-life increases with each half-life."""
        calc = HalfLifeCalculator()
        result = calc.second_order_half_life(
            initial_concentration=1.0, rate_constant=0.1
        )

        # Second half-life should be 2× first half-life
        assert result["half_life_ratio"] == 2.0

    def test_concentration_after_3_half_lives(self):
        """Test that concentration after 3 half-lives is 12.5%."""
        calc = HalfLifeCalculator()
        result = calc.concentration_after_n_half_lives(
            initial_concentration=100.0, n_half_lives=3.0
        )

        # After 3 half-lives: 100% → 50% → 25% → 12.5%
        assert abs(result["final_concentration"] - 12.5) < 0.01
        assert abs(result["percent_remaining"] - 12.5) < 0.01


# ============================================================================
# EQUILIBRIUM TESTS
# ============================================================================


class TestEquilibriumConstantValidation:
    """Test equilibrium constant validation."""

    def test_equilibrium_constant_negative_concentration_raises_error(self):
        """Test that negative concentration raises ValueError."""
        calc = EquilibriumConstantCalculator()
        with pytest.raises(ValueError, match="cannot be negative"):
            calc.equilibrium_constant_from_concentrations(
                product_concentrations=[0.5, -0.2],
                product_coefficients=[1, 1],
                reactant_concentrations=[1.0, 1.0],
                reactant_coefficients=[1, 1],
            )

    def test_equilibrium_constant_mismatched_lengths_raises_error(self):
        """Test that mismatched lists raise ValueError."""
        calc = EquilibriumConstantCalculator()
        with pytest.raises(ValueError, match="Mismatch"):
            calc.equilibrium_constant_from_concentrations(
                product_concentrations=[0.5, 0.5],
                product_coefficients=[1],  # Wrong length
                reactant_concentrations=[1.0, 1.0],
                reactant_coefficients=[1, 1],
            )

    def test_equilibrium_constant_zero_reactant_raises_error(self):
        """Test that zero reactant concentration raises ValueError."""
        calc = EquilibriumConstantCalculator()
        with pytest.raises(ValueError, match="too close to zero"):
            calc.equilibrium_constant_from_concentrations(
                product_concentrations=[0.5, 0.5],
                product_coefficients=[1, 1],
                reactant_concentrations=[0.0, 1.0],  # Zero reactant
                reactant_coefficients=[1, 1],
            )

    def test_kp_from_kc_negative_temperature_raises_error(self):
        """Test that negative temperature raises ValueError."""
        calc = EquilibriumConstantCalculator()
        with pytest.raises(ValueError, match="must be positive"):
            calc.kp_from_kc(kc=0.5, temperature=-298.0, delta_n=2)

    def test_gibbs_negative_k_raises_error(self):
        """Test that negative K raises ValueError."""
        calc = EquilibriumConstantCalculator()
        with pytest.raises(ValueError, match="must be positive"):
            calc.gibbs_free_energy_from_k(
                equilibrium_constant=-100.0, temperature=298.15
            )

    def test_reaction_quotient_predicts_direction(self):
        """Test that Q correctly predicts reaction direction."""
        calc = EquilibriumConstantCalculator()

        # Q < K: forward reaction
        result_forward = calc.reaction_quotient(
            product_concentrations=[0.1, 0.1],
            product_coefficients=[1, 1],
            reactant_concentrations=[1.0, 1.0],
            reactant_coefficients=[1, 1],
            equilibrium_constant=1.0,
        )
        assert "forward" in result_forward["direction"]

        # Q > K: reverse reaction
        result_reverse = calc.reaction_quotient(
            product_concentrations=[2.0, 2.0],
            product_coefficients=[1, 1],
            reactant_concentrations=[0.5, 0.5],
            reactant_coefficients=[1, 1],
            equilibrium_constant=1.0,
        )
        assert "reverse" in result_reverse["direction"]


class TestAcidBaseEquilibriumValidation:
    """Test acid-base equilibrium validation."""

    def test_ka_from_ph_invalid_ph_raises_error(self):
        """Test that pH outside [0, 14] raises ValueError."""
        calc = AcidBaseEquilibriumCalculator()
        with pytest.raises(ValueError, match="pH must be between 0 and 14"):
            calc.ka_from_ph(pH=15.0, initial_concentration=0.1)

    def test_ka_from_ph_negative_concentration_raises_error(self):
        """Test that negative concentration raises ValueError."""
        calc = AcidBaseEquilibriumCalculator()
        with pytest.raises(ValueError, match="must be positive"):
            calc.ka_from_ph(pH=3.0, initial_concentration=-0.1)

    def test_pH_from_ka_negative_ka_raises_error(self):
        """Test that negative Ka raises ValueError."""
        calc = AcidBaseEquilibriumCalculator()
        with pytest.raises(ValueError, match="Ka must be positive"):
            calc.pH_from_ka(ka=-1.8e-5, initial_concentration=0.1)

    def test_ka_kb_missing_parameter_raises_error(self):
        """Test that neither Ka nor Kb raises error."""
        calc = AcidBaseEquilibriumCalculator()
        with pytest.raises(ValueError, match="Provide exactly one"):
            calc.ka_kb_relationship()

    def test_ka_kb_both_parameters_raises_error(self):
        """Test that providing both Ka and Kb raises error."""
        calc = AcidBaseEquilibriumCalculator()
        with pytest.raises(ValueError, match="Provide exactly one"):
            calc.ka_kb_relationship(ka=1e-5, kb=1e-9)

    def test_henderson_hasselbalch_missing_parameters_raises_error(self):
        """Test that missing required parameters raises error."""
        calc = AcidBaseEquilibriumCalculator()
        with pytest.raises(ValueError, match="Provide either"):
            calc.henderson_hasselbalch(pka=4.76)

    def test_henderson_hasselbalch_equal_concentrations(self):
        """Test that equal concentrations give pH = pKa."""
        calc = AcidBaseEquilibriumCalculator()
        result = calc.henderson_hasselbalch(
            pka=4.76, acid_concentration=0.1, base_concentration=0.1
        )
        assert abs(result["pH"] - 4.76) < 1e-10

    def test_buffer_capacity_negative_concentration_raises_error(self):
        """Test that negative concentration raises ValueError."""
        calc = AcidBaseEquilibriumCalculator()
        with pytest.raises(ValueError, match="must be positive"):
            calc.buffer_capacity(acid_concentration=-0.1, base_concentration=0.1)

    def test_ka_kb_relationship_product_equals_kw(self):
        """Test that Ka × Kb = Kw."""
        calc = AcidBaseEquilibriumCalculator()
        result = calc.ka_kb_relationship(ka=1.8e-5)

        product = result["Ka"] * result["Kb"]
        assert abs(product - WATER_ION_PRODUCT_25C) < 1e-20


class TestSolubilityValidation:
    """Test solubility equilibrium validation."""

    def test_ksp_from_solubility_negative_raises_error(self):
        """Test that negative solubility raises ValueError."""
        calc = SolubilityCalculator()
        with pytest.raises(ValueError, match="cannot be negative"):
            calc.ksp_from_solubility(
                solubility=-1e-5, cation_coefficient=1, anion_coefficient=1
            )

    def test_ksp_from_solubility_zero_coefficient_raises_error(self):
        """Test that zero coefficient raises ValueError."""
        calc = SolubilityCalculator()
        with pytest.raises(ValueError, match="must be positive"):
            calc.ksp_from_solubility(
                solubility=1e-5, cation_coefficient=0, anion_coefficient=1
            )

    def test_solubility_from_ksp_negative_ksp_raises_error(self):
        """Test that negative Ksp raises ValueError."""
        calc = SolubilityCalculator()
        with pytest.raises(ValueError, match="cannot be negative"):
            calc.solubility_from_ksp(
                ksp=-1.8e-10, cation_coefficient=1, anion_coefficient=1
            )

    def test_common_ion_negative_concentration_raises_error(self):
        """Test that negative common ion concentration raises error."""
        calc = SolubilityCalculator()
        with pytest.raises(ValueError, match="cannot be negative"):
            calc.common_ion_effect(
                ksp=1.8e-10,
                common_ion_concentration=-0.1,
                ion_coefficient=1,
                other_ion_coefficient=1,
            )

    def test_common_ion_reduces_solubility(self):
        """Test that common ion effect reduces solubility."""
        calc = SolubilityCalculator()
        result = calc.common_ion_effect(
            ksp=1.8e-10,
            common_ion_concentration=0.1,
            ion_coefficient=1,
            other_ion_coefficient=1,
        )

        # Solubility with common ion should be less than pure water
        assert result["solubility_with_common_ion"] < result["solubility_pure_water"]
        assert result["reduction_factor"] > 1.0

    def test_ksp_solubility_relationship_reversible(self):
        """Test that Ksp ↔ solubility conversions are reversible."""
        calc = SolubilityCalculator()

        # Start with Ksp
        ksp_original = 1.8e-10

        # Convert to solubility
        result1 = calc.solubility_from_ksp(
            ksp=ksp_original, cation_coefficient=1, anion_coefficient=1
        )

        # Convert back to Ksp
        result2 = calc.ksp_from_solubility(
            solubility=result1["solubility"], cation_coefficient=1, anion_coefficient=1
        )

        assert abs(result2["Ksp"] - ksp_original) < 1e-15


# ============================================================================
# EDGE CASES AND BOUNDARY CONDITIONS
# ============================================================================


class TestChemistryEdgeCases:
    """Test edge cases and boundary conditions."""

    def test_zero_concentration_gives_zero_rate(self):
        """Test that zero concentration gives zero rate."""
        calc = RateEquationCalculator()
        result = calc.first_order_rate(rate_constant=0.1, concentration=0.0)
        assert result["rate"] == 0.0

    def test_very_small_ka_gives_high_ph(self):
        """Test that very weak acid gives pH near 7."""
        calc = AcidBaseEquilibriumCalculator()
        result = calc.pH_from_ka(ka=1e-14, initial_concentration=0.01)  # Very weak acid
        # Should be close to neutral
        assert result["pH"] > 6.5

    def test_complete_dissociation_detection(self):
        """Test that complete dissociation is detected."""
        calc = AcidBaseEquilibriumCalculator()
        # Very high pH indicates complete dissociation
        with pytest.raises(ValueError, match="Complete dissociation"):
            calc.ka_from_ph(pH=1.0, initial_concentration=0.01)  # Too small for this pH

    def test_first_order_at_time_zero(self):
        """Test that concentration at t=0 equals initial."""
        calc = IntegratedRateLawCalculator()
        result = calc.first_order_integrated(
            initial_concentration=2.0, rate_constant=0.1, time=0.0
        )
        assert abs(result["final_concentration"] - 2.0) < 1e-10

    def test_extremely_high_activation_energy(self):
        """Test that very high Ea gives very small rate constant."""
        calc = ArrheniusCalculator()
        result = calc.arrhenius_equation(
            activation_energy=500000,
            temperature=298.15,
            pre_exponential_factor=1e10,  # Very high
        )
        # Should be extremely small
        assert result["rate_constant"] < 1e-50

    def test_zero_activation_energy(self):
        """Test that Ea=0 gives k=A."""
        calc = ArrheniusCalculator()
        A = 1e10
        result = calc.arrhenius_equation(
            activation_energy=0.0,
            temperature=298.15,
            pre_exponential_factor=A,  # No barrier
        )
        assert abs(result["rate_constant"] - A) < 1e-5


class TestKineticsOrderDetermination:
    """Test reaction order determination from data."""

    def test_order_determination_too_few_points_raises_error(self):
        """Test that less than 3 points raises error."""
        calc = KineticsCalculator()
        with pytest.raises(ValueError, match="Need at least 3 data points"):
            calc.determine_reaction_order(concentrations=[1.0, 0.9], times=[0, 10])

    def test_order_determination_mismatched_lengths_raises_error(self):
        """Test that mismatched lists raise error."""
        calc = KineticsCalculator()
        with pytest.raises(ValueError, match="must have same length"):
            calc.determine_reaction_order(
                concentrations=[1.0, 0.9, 0.8], times=[0, 10]
            )  # Length mismatch

    def test_order_determination_negative_time_raises_error(self):
        """Test that negative time raises error."""
        calc = KineticsCalculator()
        with pytest.raises(ValueError, match="cannot be negative"):
            calc.determine_reaction_order(
                concentrations=[1.0, 0.9, 0.8], times=[0, -10, 20]
            )

    def test_first_order_data_detected(self):
        """Test that first-order data is correctly identified."""
        calc = KineticsCalculator()

        # Generate perfect first-order data
        k = 0.1
        times = [0, 10, 20, 30, 40]
        concentrations = [1.0 * math.exp(-k * t) for t in times]

        result = calc.determine_reaction_order(
            concentrations=concentrations, times=times
        )

        # First-order should have highest correlation
        assert result["likely_order"] == 1
        assert result["first_order_correlation"] > 0.99


# ============================================================================
# RUN TESTS
# ============================================================================

if __name__ == "__main__":
    pytest.main([__file__, "-v", "--tb=short"])
