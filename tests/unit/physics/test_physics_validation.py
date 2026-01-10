"""
Unit Tests - Physics Validation
================================

Comprehensive unit tests for physics domain validations including:
- Mechanics: kinematics, dynamics, energy, momentum
- Thermodynamics: ideal gas, heat transfer, entropy
- Electromagnetism: circuits, fields, induction

Tests cover:
- Edge cases and boundary conditions
- Invalid input validation
- Error message verification
- Physical constraint enforcement
"""

import math
import sys
from pathlib import Path

import pytest

# Add parent directory to path for imports
sys.path.insert(0, str(Path(__file__).parent.parent.parent))

# Import physics modules (adjust paths as needed)
try:
    from electromagnetism_formulas import (
        CircuitsCalculator,
        ElectromagnetismCalculator,
        ElectrostaticsCalculator,
        MagnetismCalculator,
        epsilon_0,
        k_e,
        mu_0,
    )
    from mechanics_formulas import (
        GRAVITATIONAL_CONSTANT,
        STANDARD_GRAVITY,
        DynamicsCalculator,
        EnergyCalculator,
        KinematicsCalculator,
        MechanicsCalculator,
        MomentumCalculator,
    )
    from thermodynamics_formulas import (
        GAS_CONSTANT,
        STEFAN_BOLTZMANN_CONSTANT,
        EntropyCalculator,
        HeatTransferCalculator,
        IdealGasCalculator,
        ThermodynamicCycleCalculator,
    )
except ImportError as e:
    pytest.skip(f"Required modules not found: {e}", allow_module_level=True)


# ============================================================================
# MECHANICS TESTS
# ============================================================================


class TestKinematicsValidation:
    """Test kinematics calculations validation."""

    def test_velocity_negative_time_raises_error(self):
        """Test that negative time raises ValueError."""
        calc = KinematicsCalculator()
        with pytest.raises(ValueError, match="Time cannot be negative"):
            calc.velocity_from_displacement(displacement=10.0, time=-5.0)

    def test_velocity_zero_time_raises_error(self):
        """Test that zero time raises ValueError."""
        calc = KinematicsCalculator()
        with pytest.raises(ValueError, match="Time must be positive"):
            calc.velocity_from_displacement(displacement=10.0, time=0.0)

    def test_projectile_negative_velocity_raises_error(self):
        """Test that negative initial velocity raises ValueError."""
        calc = KinematicsCalculator()
        with pytest.raises(ValueError, match="Initial velocity must be positive"):
            calc.projectile_motion(initial_velocity=-10.0, angle_degrees=45.0)

    def test_projectile_invalid_angle_raises_error(self):
        """Test that angle outside [-90, 90] raises ValueError."""
        calc = KinematicsCalculator()
        with pytest.raises(ValueError, match="Angle must be between"):
            calc.projectile_motion(initial_velocity=50.0, angle_degrees=100.0)

    def test_projectile_negative_height_raises_error(self):
        """Test that negative initial height raises ValueError."""
        calc = KinematicsCalculator()
        with pytest.raises(ValueError, match="Initial height cannot be negative"):
            calc.projectile_motion(
                initial_velocity=50.0, angle_degrees=45.0, initial_height=-5.0
            )

    def test_circular_motion_negative_radius_raises_error(self):
        """Test that negative radius raises ValueError."""
        calc = KinematicsCalculator()
        with pytest.raises(ValueError, match="Radius must be positive"):
            calc.circular_motion(radius=-5.0, period=10.0)

    def test_circular_motion_no_parameter_raises_error(self):
        """Test that missing period/frequency/angular_velocity raises error."""
        calc = KinematicsCalculator()
        with pytest.raises(ValueError, match="Must provide exactly one"):
            calc.circular_motion(radius=5.0)

    def test_circular_motion_multiple_parameters_raises_error(self):
        """Test that providing multiple parameters raises error."""
        calc = KinematicsCalculator()
        with pytest.raises(ValueError, match="Must provide exactly one"):
            calc.circular_motion(radius=5.0, period=10.0, frequency=0.1)

    def test_velocity_squared_impossible_deceleration(self):
        """Test that impossible deceleration raises ValueError."""
        calc = KinematicsCalculator()
        with pytest.raises(ValueError, match="No real solution"):
            # Object starting at 10 m/s cannot stop in 1 m with -10 m/s²
            calc.velocity_squared_formula(
                initial_velocity=10.0,
                acceleration=-100.0,
                displacement=1.0,  # Too much deceleration
            )

    def test_displacement_boundary_zero_time(self):
        """Test displacement at t=0 returns zero displacement."""
        calc = KinematicsCalculator()
        result = calc.displacement_constant_acceleration(
            initial_velocity=10.0, acceleration=5.0, time=0.0
        )
        assert result["displacement"] == 0.0
        assert result["final_velocity"] == 10.0


class TestDynamicsValidation:
    """Test dynamics calculations validation."""

    def test_newtons_law_negative_mass_raises_error(self):
        """Test that negative mass raises ValueError."""
        calc = DynamicsCalculator()
        with pytest.raises(ValueError, match="Mass must be positive"):
            calc.newtons_second_law(mass=-10.0, acceleration=5.0)

    def test_newtons_law_zero_mass_raises_error(self):
        """Test that zero mass raises ValueError."""
        calc = DynamicsCalculator()
        with pytest.raises(ValueError, match="Mass must be positive"):
            calc.newtons_second_law(mass=0.0, acceleration=5.0)

    def test_gravitational_force_negative_distance_raises_error(self):
        """Test that negative distance raises ValueError."""
        calc = DynamicsCalculator()
        with pytest.raises(ValueError, match="Distance must be positive"):
            calc.gravitational_force(mass1=100.0, mass2=50.0, distance=-10.0)

    def test_friction_negative_coefficient_raises_error(self):
        """Test that negative friction coefficient raises ValueError."""
        calc = DynamicsCalculator()
        with pytest.raises(
            ValueError, match="Coefficient of friction cannot be negative"
        ):
            calc.friction_force(normal_force=100.0, coefficient=-0.5)

    def test_spring_force_negative_constant_raises_error(self):
        """Test that negative spring constant raises ValueError."""
        calc = DynamicsCalculator()
        with pytest.raises(ValueError, match="Spring constant must be positive"):
            calc.spring_force(spring_constant=-100.0, displacement=0.5)

    def test_friction_boundary_zero_coefficient(self):
        """Test friction with zero coefficient returns zero force."""
        calc = DynamicsCalculator()
        result = calc.friction_force(normal_force=100.0, coefficient=0.0)
        assert result["friction_force"] == 0.0


class TestEnergyValidation:
    """Test energy calculations validation."""

    def test_kinetic_energy_negative_mass_raises_error(self):
        """Test that negative mass raises ValueError."""
        calc = EnergyCalculator()
        with pytest.raises(ValueError, match="Mass must be positive"):
            calc.kinetic_energy(mass=-5.0, velocity=10.0)

    def test_potential_energy_negative_gravity_raises_error(self):
        """Test that negative gravity raises ValueError."""
        calc = EnergyCalculator()
        with pytest.raises(ValueError, match="Gravity must be positive"):
            calc.gravitational_potential_energy(mass=10.0, height=5.0, gravity=-9.8)

    def test_work_negative_force_raises_error(self):
        """Test that negative force magnitude raises ValueError."""
        calc = EnergyCalculator()
        with pytest.raises(ValueError, match="Force magnitude cannot be negative"):
            calc.work_done(force=-50.0, displacement=10.0)

    def test_power_negative_time_raises_error(self):
        """Test that negative time raises ValueError."""
        calc = EnergyCalculator()
        with pytest.raises(ValueError, match="Time must be positive"):
            calc.power(work=500.0, time=-5.0)

    def test_efficiency_output_exceeds_input_raises_error(self):
        """Test that work output > input raises ValueError."""
        calc = EnergyCalculator()
        with pytest.raises(ValueError, match="cannot exceed input"):
            calc.mechanical_efficiency(work_output=1500.0, work_input=1000.0)

    def test_work_perpendicular_force_returns_zero(self):
        """Test that perpendicular force (90°) does zero work."""
        calc = EnergyCalculator()
        result = calc.work_done(force=100.0, displacement=10.0, angle_degrees=90.0)
        assert abs(result["work"]) < 1e-10  # Near zero due to cos(90°)


class TestMomentumValidation:
    """Test momentum calculations validation."""

    def test_momentum_negative_mass_raises_error(self):
        """Test that negative mass raises ValueError."""
        calc = MomentumCalculator()
        with pytest.raises(ValueError, match="Mass must be positive"):
            calc.linear_momentum(mass=-5.0, velocity=10.0)

    def test_impulse_negative_time_raises_error(self):
        """Test that negative time raises ValueError."""
        calc = MomentumCalculator()
        with pytest.raises(ValueError, match="Time must be positive"):
            calc.impulse(force=100.0, time=-2.0)

    def test_elastic_collision_negative_mass_raises_error(self):
        """Test that negative mass raises ValueError."""
        calc = MomentumCalculator()
        with pytest.raises(ValueError, match="Masses must be positive"):
            calc.elastic_collision_1d(m1=-10.0, v1_initial=5.0, m2=5.0, v2_initial=0.0)

    def test_elastic_collision_conservation_laws(self):
        """Test that elastic collision conserves momentum and energy."""
        calc = MomentumCalculator()
        result = calc.elastic_collision_1d(
            m1=2.0, v1_initial=5.0, m2=3.0, v2_initial=-2.0
        )

        # Check momentum conservation
        assert result["momentum_conserved"] == True

        # Check energy conservation
        assert result["energy_conserved"] == True

        # Verify within numerical tolerance
        p_initial = result["momentum_initial"]
        p_final = result["momentum_final"]
        assert abs(p_final - p_initial) < 1e-10


# ============================================================================
# THERMODYNAMICS TESTS
# ============================================================================


class TestIdealGasValidation:
    """Test ideal gas law validation."""

    def test_ideal_gas_wrong_parameter_count_raises_error(self):
        """Test that providing wrong number of parameters raises error."""
        calc = IdealGasCalculator()

        # Too few parameters
        with pytest.raises(ValueError, match="Must provide exactly 3 parameters"):
            calc.ideal_gas_law(pressure=101325, volume=0.0224)

        # All parameters provided
        with pytest.raises(ValueError, match="Must provide exactly 3 parameters"):
            calc.ideal_gas_law(
                pressure=101325, volume=0.0224, n_moles=1.0, temperature=273.15
            )

    def test_ideal_gas_negative_pressure_raises_error(self):
        """Test that negative pressure raises ValueError."""
        calc = IdealGasCalculator()
        with pytest.raises(ValueError, match="Pressure .* must be positive"):
            calc.ideal_gas_law(pressure=-101325, volume=0.0224, n_moles=1.0)

    def test_ideal_gas_negative_volume_raises_error(self):
        """Test that negative volume raises ValueError."""
        calc = IdealGasCalculator()
        with pytest.raises(ValueError, match="Volume .* must be positive"):
            calc.ideal_gas_law(pressure=101325, volume=-0.0224, n_moles=1.0)

    def test_isothermal_process_missing_final_parameter_raises_error(self):
        """Test that missing final state parameter raises error."""
        calc = IdealGasCalculator()
        with pytest.raises(ValueError, match="Provide exactly one"):
            calc.isothermal_process(
                pressure_initial=200000, volume_initial=0.01, n_moles=1.0
            )

    def test_adiabatic_process_invalid_gamma_raises_error(self):
        """Test that gamma <= 1 raises ValueError."""
        calc = IdealGasCalculator()
        with pytest.raises(ValueError, match="Gamma must be > 1"):
            calc.adiabatic_process(
                pressure_initial=200000,
                volume_initial=0.01,
                volume_final=0.02,
                gamma=0.8,  # Invalid gamma
            )

    def test_isothermal_expansion_work_sign(self):
        """Test that isothermal expansion does positive work."""
        calc = IdealGasCalculator()
        result = calc.isothermal_process(
            pressure_initial=200000,
            volume_initial=0.01,
            volume_final=0.02,
            n_moles=1.0,  # Expansion: V_f > V_i
        )
        # Expansion does positive work
        assert result["work_done"] > 0


class TestHeatTransferValidation:
    """Test heat transfer validation."""

    def test_heat_capacity_negative_mass_raises_error(self):
        """Test that negative mass raises ValueError."""
        calc = HeatTransferCalculator()
        with pytest.raises(ValueError, match="Mass must be positive"):
            calc.heat_capacity(
                mass=-10.0, specific_heat=4186.0, temperature_change=20.0
            )

    def test_conduction_negative_thermal_conductivity_raises_error(self):
        """Test that negative thermal conductivity raises ValueError."""
        calc = HeatTransferCalculator()
        with pytest.raises(ValueError, match="Thermal conductivity must be positive"):
            calc.conduction(
                thermal_conductivity=-0.8,
                area=10.0,
                temperature_difference=20.0,
                thickness=0.1,
            )

    def test_radiation_emissivity_out_of_range_raises_error(self):
        """Test that emissivity outside [0,1] raises ValueError."""
        calc = HeatTransferCalculator()

        # Emissivity > 1
        with pytest.raises(ValueError, match="Emissivity must be between 0 and 1"):
            calc.radiation(
                emissivity=1.5, area=1.0, temperature=400.0, ambient_temperature=300.0
            )

        # Emissivity < 0
        with pytest.raises(ValueError, match="Emissivity must be between 0 and 1"):
            calc.radiation(
                emissivity=-0.5, area=1.0, temperature=400.0, ambient_temperature=300.0
            )

    def test_radiation_negative_temperature_raises_error(self):
        """Test that negative absolute temperature raises ValueError."""
        calc = HeatTransferCalculator()
        with pytest.raises(ValueError, match="Temperature must be positive"):
            calc.radiation(
                emissivity=0.9, area=1.0, temperature=-50.0, ambient_temperature=300.0
            )  # Invalid Kelvin


class TestThermodynamicCyclesValidation:
    """Test thermodynamic cycles validation."""

    def test_heat_engine_missing_parameters_raises_error(self):
        """Test that missing required parameters raises error."""
        calc = ThermodynamicCycleCalculator()
        with pytest.raises(ValueError, match="Provide"):
            calc.heat_engine_efficiency(heat_input=2000.0)

    def test_heat_engine_heat_output_exceeds_input_raises_error(self):
        """Test that heat output > input raises ValueError."""
        calc = ThermodynamicCycleCalculator()
        with pytest.raises(ValueError, match="cannot exceed"):
            calc.heat_engine_efficiency(
                heat_input=1000.0, heat_output=1500.0
            )  # Violates energy conservation

    def test_carnot_cold_temp_exceeds_hot_raises_error(self):
        """Test that T_cold >= T_hot raises ValueError."""
        calc = ThermodynamicCycleCalculator()
        with pytest.raises(ValueError, match="Cold temperature must be less than hot"):
            calc.carnot_efficiency(
                temperature_hot=300.0, temperature_cold=400.0
            )  # Invalid

    def test_carnot_efficiency_zero_kelvin_raises_error(self):
        """Test that zero or negative Kelvin raises ValueError."""
        calc = ThermodynamicCycleCalculator()
        with pytest.raises(ValueError, match="must be positive"):
            calc.carnot_efficiency(
                temperature_hot=300.0, temperature_cold=0.0
            )  # Absolute zero

    def test_carnot_efficiency_upper_bound(self):
        """Test that Carnot efficiency is always less than 100%."""
        calc = ThermodynamicCycleCalculator()
        result = calc.carnot_efficiency(temperature_hot=600.0, temperature_cold=300.0)
        assert result["carnot_efficiency_percent"] < 100.0
        assert result["carnot_efficiency_percent"] == 50.0  # (600-300)/600 * 100


# ============================================================================
# ELECTROMAGNETISM TESTS
# ============================================================================


class TestElectrostaticsValidation:
    """Test electrostatics validation."""

    def test_coulombs_law_zero_distance_raises_error(self):
        """Test that zero distance raises ValueError."""
        calc = ElectrostaticsCalculator()
        with pytest.raises(ValueError, match="distance must be > 0"):
            calc.coulombs_law(charge1=1e-6, charge2=2e-6, distance=0.0)

    def test_electric_field_negative_distance_raises_error(self):
        """Test that negative distance raises ValueError."""
        calc = ElectrostaticsCalculator()
        with pytest.raises(ValueError, match="distance must be > 0"):
            calc.electric_field_point_charge(charge=5e-9, distance=-0.05)

    def test_capacitance_wrong_parameter_count_raises_error(self):
        """Test that wrong number of parameters raises error."""
        calc = ElectrostaticsCalculator()

        # Only one parameter
        with pytest.raises(ValueError, match="Must provide exactly 2 of 3"):
            calc.capacitance(charge=1e-3)

        # All three parameters
        with pytest.raises(ValueError, match="Must provide exactly 2 of 3"):
            calc.capacitance(charge=1e-3, voltage=12.0, capacitance_value=100e-6)

    def test_parallel_plate_negative_area_raises_error(self):
        """Test that negative area raises ValueError."""
        calc = ElectrostaticsCalculator()
        with pytest.raises(ValueError, match="area must be > 0"):
            calc.parallel_plate_capacitor(area=-0.01, separation=0.001)

    def test_parallel_plate_dielectric_less_than_one_raises_error(self):
        """Test that dielectric constant < 1 raises ValueError."""
        calc = ElectrostaticsCalculator()
        with pytest.raises(ValueError, match="dielectric_constant must be ≥ 1"):
            calc.parallel_plate_capacitor(
                area=0.01, separation=0.001, dielectric_constant=0.5
            )  # Invalid


class TestMagnetismValidation:
    """Test magnetism validation."""

    def test_magnetic_force_negative_velocity_raises_error(self):
        """Test that negative velocity raises ValueError."""
        calc = MagnetismCalculator()
        with pytest.raises(ValueError, match="velocity must be ≥ 0"):
            calc.magnetic_force_on_charge(
                charge=1.6e-19, velocity=-1e6, magnetic_field=0.5
            )

    def test_magnetic_force_invalid_angle_raises_error(self):
        """Test that angle outside [0, 180] raises ValueError."""
        calc = MagnetismCalculator()
        with pytest.raises(ValueError, match="angle must be in"):
            calc.magnetic_force_on_charge(
                charge=1.6e-19,
                velocity=1e6,
                magnetic_field=0.5,
                angle_degrees=200.0,  # Invalid
            )

    def test_faradays_law_negative_turns_raises_error(self):
        """Test that negative or zero turns raises ValueError."""
        calc = MagnetismCalculator()
        with pytest.raises(ValueError, match="n_turns must be > 0"):
            calc.faradays_law(n_turns=0, flux_change=0.01, time_interval=0.1)

    def test_solenoid_negative_current_raises_error(self):
        """Test that negative current raises ValueError."""
        calc = MagnetismCalculator()
        with pytest.raises(ValueError, match="current must be ≥ 0"):
            calc.magnetic_field_solenoid(current=-5.0, n_turns=500, length=0.2)


class TestCircuitsValidation:
    """Test circuit calculations validation."""

    def test_ohms_law_wrong_parameter_count_raises_error(self):
        """Test that wrong number of parameters raises error."""
        calc = CircuitsCalculator()

        # Only one parameter
        with pytest.raises(ValueError, match="Must provide exactly 2 of 3"):
            calc.ohms_law(voltage=12.0)

        # All three parameters
        with pytest.raises(ValueError, match="Must provide exactly 2 of 3"):
            calc.ohms_law(voltage=12.0, current=0.5, resistance=24.0)

    def test_ohms_law_negative_voltage_raises_error(self):
        """Test that negative voltage raises ValueError."""
        calc = CircuitsCalculator()
        with pytest.raises(ValueError, match="voltage must be ≥ 0"):
            calc.ohms_law(voltage=-12.0, resistance=100.0)

    def test_resistors_series_too_few_raises_error(self):
        """Test that less than 2 resistors raises error."""
        calc = CircuitsCalculator()
        with pytest.raises(ValueError, match="Need at least 2 resistors"):
            calc.resistors_series(resistances=[100.0])

    def test_resistors_parallel_negative_resistance_raises_error(self):
        """Test that negative resistance raises ValueError."""
        calc = CircuitsCalculator()
        with pytest.raises(ValueError, match="All resistances must be > 0"):
            calc.resistors_parallel(resistances=[100.0, -50.0, 200.0])

    def test_rc_circuit_negative_capacitance_raises_error(self):
        """Test that negative capacitance raises ValueError."""
        calc = CircuitsCalculator()
        with pytest.raises(ValueError, match="capacitance must be > 0"):
            calc.rc_circuit_charging(
                voltage=5.0, resistance=10000.0, capacitance=-100e-6, time=1.0
            )

    def test_rc_circuit_time_constant(self):
        """Test that time constant is calculated correctly."""
        calc = CircuitsCalculator()
        result = calc.rc_circuit_charging(
            voltage=5.0,
            resistance=10000.0,
            capacitance=100e-6,
            time=1.0,  # 10 kΩ  # 100 μF
        )
        expected_tau = 10000.0 * 100e-6  # R * C = 1.0 s
        assert abs(result["time_constant_tau"] - expected_tau) < 1e-10


# ============================================================================
# EDGE CASES AND BOUNDARY CONDITIONS
# ============================================================================


class TestPhysicsEdgeCases:
    """Test edge cases and boundary conditions."""

    def test_zero_velocity_kinetic_energy(self):
        """Test that zero velocity gives zero kinetic energy."""
        calc = EnergyCalculator()
        result = calc.kinetic_energy(mass=10.0, velocity=0.0)
        assert result["kinetic_energy"] == 0.0

    def test_zero_height_potential_energy(self):
        """Test that zero height gives zero potential energy."""
        calc = EnergyCalculator()
        result = calc.gravitational_potential_energy(mass=10.0, height=0.0)
        assert result["potential_energy"] == 0.0

    def test_180_degree_work_negative(self):
        """Test that force opposite to displacement does negative work."""
        calc = EnergyCalculator()
        result = calc.work_done(force=100.0, displacement=10.0, angle_degrees=180.0)
        assert result["work"] < 0

    def test_equal_masses_elastic_collision_velocity_exchange(self):
        """Test that equal mass elastic collision exchanges velocities."""
        calc = MomentumCalculator()
        result = calc.elastic_collision_1d(
            m1=5.0, v1_initial=10.0, m2=5.0, v2_initial=0.0
        )
        # Equal masses: velocities should exchange
        assert abs(result["v1_final"] - 0.0) < 1e-10
        assert abs(result["v2_final"] - 10.0) < 1e-10

    def test_very_large_distance_gravitational_force_approaches_zero(self):
        """Test that gravitational force decreases with distance squared."""
        calc = DynamicsCalculator()

        # Force at 1 m
        result1 = calc.gravitational_force(mass1=100.0, mass2=50.0, distance=1.0)

        # Force at 10 m (should be 1/100 of force at 1 m)
        result2 = calc.gravitational_force(mass1=100.0, mass2=50.0, distance=10.0)

        ratio = result1["gravitational_force"] / result2["gravitational_force"]
        assert abs(ratio - 100.0) < 1e-8  # 10^2 = 100


# ============================================================================
# RUN TESTS
# ============================================================================

if __name__ == "__main__":
    pytest.main([__file__, "-v", "--tb=short"])
