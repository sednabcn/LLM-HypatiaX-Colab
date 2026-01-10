"""
Physics Domain - Thermodynamics Formulas
========================================

This module provides comprehensive thermodynamics calculations including:
- Ideal gas law and gas processes
- Heat transfer (conduction, convection, radiation)
- Thermodynamic cycles and engines
- Entropy and second law of thermodynamics
- Specific heat and phase changes

All formulas include validation and return detailed results.

Author: Physics Domain Team
Version: 1.0.0
"""

import math
from enum import Enum
from typing import Dict, Optional

# Constants
EPSILON = 1e-12  # Numerical tolerance
GAS_CONSTANT = 8.314462618  # J/(mol·K) - Universal gas constant
BOLTZMANN_CONSTANT = 1.380649e-23  # J/K
AVOGADRO_NUMBER = 6.02214076e23  # mol⁻¹
STEFAN_BOLTZMANN_CONSTANT = 5.670374419e-8  # W/(m²·K⁴)
ABSOLUTE_ZERO = -273.15  # °C
STANDARD_TEMPERATURE = 273.15  # K (0°C)
STANDARD_PRESSURE = 101325  # Pa (1 atm)


class ProcessType(Enum):
    """Types of thermodynamic processes."""

    ISOTHERMAL = "isothermal"  # Constant temperature
    ADIABATIC = "adiabatic"  # No heat transfer
    ISOBARIC = "isobaric"  # Constant pressure
    ISOCHORIC = "isochoric"  # Constant volume


class IdealGasCalculator:
    """Calculator for ideal gas law and related calculations."""

    @staticmethod
    def ideal_gas_law(
        pressure: Optional[float] = None,
        volume: Optional[float] = None,
        n_moles: Optional[float] = None,
        temperature: Optional[float] = None,
        validate: bool = True,
    ) -> Dict[str, float]:
        """
        Calculate unknown variable using ideal gas law.

        Formula: PV = nRT

        Provide exactly 3 of the 4 variables to calculate the 4th.

        Args:
            pressure: Pressure (Pa)
            volume: Volume (m³)
            n_moles: Number of moles (mol)
            temperature: Temperature (K)
            validate: Enable input validation

        Returns:
            Dictionary with all gas properties

        Raises:
            ValueError: If not exactly 3 parameters provided or invalid values
        """
        params = [pressure, volume, n_moles, temperature]
        provided = sum(p is not None for p in params)

        if validate:
            if provided != 3:
                raise ValueError(f"Must provide exactly 3 parameters, got {provided}")

        # Calculate missing parameter
        if pressure is None:
            if validate:
                if volume <= 0 or n_moles <= 0 or temperature <= 0:
                    raise ValueError("Volume, moles, and temperature must be positive")
            pressure = (n_moles * GAS_CONSTANT * temperature) / volume

        elif volume is None:
            if validate:
                if pressure <= 0 or n_moles <= 0 or temperature <= 0:
                    raise ValueError(
                        "Pressure, moles, and temperature must be positive"
                    )
            volume = (n_moles * GAS_CONSTANT * temperature) / pressure

        elif n_moles is None:
            if validate:
                if pressure <= 0 or volume <= 0 or temperature <= 0:
                    raise ValueError(
                        "Pressure, volume, and temperature must be positive"
                    )
            n_moles = (pressure * volume) / (GAS_CONSTANT * temperature)

        else:  # temperature is None
            if validate:
                if pressure <= 0 or volume <= 0 or n_moles <= 0:
                    raise ValueError("Pressure, volume, and moles must be positive")
            temperature = (pressure * volume) / (n_moles * GAS_CONSTANT)

        # Calculate additional properties
        n_molecules = n_moles * AVOGADRO_NUMBER

        return {
            "pressure": pressure,
            "volume": volume,
            "n_moles": n_moles,
            "temperature": temperature,
            "n_molecules": n_molecules,
            "gas_constant": GAS_CONSTANT,
            "formula": "PV = nRT",
        }

    @staticmethod
    def isothermal_process(
        pressure_initial: float,
        volume_initial: float,
        volume_final: Optional[float] = None,
        pressure_final: Optional[float] = None,
        n_moles: float = 1.0,
        temperature: Optional[float] = None,
        validate: bool = True,
    ) -> Dict[str, float]:
        """
        Calculate isothermal (constant temperature) process.

        Formula: P₁V₁ = P₂V₂
        Work: W = nRT ln(V₂/V₁)

        Args:
            pressure_initial: Initial pressure (Pa)
            volume_initial: Initial volume (m³)
            volume_final: Final volume (m³)
            pressure_final: Final pressure (Pa)
            n_moles: Number of moles (mol)
            temperature: Temperature (K), optional
            validate: Enable input validation

        Returns:
            Dictionary with process details and work done
        """
        if validate:
            if pressure_initial <= 0 or volume_initial <= 0:
                raise ValueError("Initial pressure and volume must be positive")
            if n_moles <= 0:
                raise ValueError("Number of moles must be positive")

            has_final = sum([volume_final is not None, pressure_final is not None])
            if has_final != 1:
                raise ValueError(
                    "Provide exactly one of: volume_final or pressure_final"
                )

        # Calculate missing final parameter
        if volume_final is None:
            if validate and pressure_final <= 0:
                raise ValueError("Final pressure must be positive")
            volume_final = (pressure_initial * volume_initial) / pressure_final
        else:
            if validate and volume_final <= 0:
                raise ValueError("Final volume must be positive")
            pressure_final = (pressure_initial * volume_initial) / volume_final

        # Calculate temperature if not provided
        if temperature is None:
            temperature = (pressure_initial * volume_initial) / (n_moles * GAS_CONSTANT)

        # Calculate work done (W = nRT ln(V₂/V₁))
        if volume_final > EPSILON:
            work_done = (
                n_moles
                * GAS_CONSTANT
                * temperature
                * math.log(volume_final / volume_initial)
            )
        else:
            work_done = 0

        # Heat transferred (Q = W for isothermal process)
        heat_transferred = work_done

        return {
            "pressure_initial": pressure_initial,
            "volume_initial": volume_initial,
            "pressure_final": pressure_final,
            "volume_final": volume_final,
            "temperature": temperature,
            "n_moles": n_moles,
            "work_done": work_done,
            "heat_transferred": heat_transferred,
            "delta_internal_energy": 0.0,  # ΔU = 0 for isothermal
            "process_type": "isothermal",
            "formula": "P₁V₁ = P₂V₂, W = nRT ln(V₂/V₁)",
        }

    @staticmethod
    def adiabatic_process(
        pressure_initial: float,
        volume_initial: float,
        volume_final: Optional[float] = None,
        pressure_final: Optional[float] = None,
        gamma: float = 1.4,  # Heat capacity ratio (diatomic gas default)
        validate: bool = True,
    ) -> Dict[str, float]:
        """
        Calculate adiabatic (no heat transfer) process.

        Formula: P₁V₁^γ = P₂V₂^γ

        Args:
            pressure_initial: Initial pressure (Pa)
            volume_initial: Initial volume (m³)
            volume_final: Final volume (m³)
            pressure_final: Final pressure (Pa)
            gamma: Heat capacity ratio Cp/Cv (dimensionless)
            validate: Enable input validation

        Returns:
            Dictionary with process details
        """
        if validate:
            if pressure_initial <= 0 or volume_initial <= 0:
                raise ValueError("Initial pressure and volume must be positive")
            if gamma <= 1:
                raise ValueError(f"Gamma must be > 1, got {gamma}")

            has_final = sum([volume_final is not None, pressure_final is not None])
            if has_final != 1:
                raise ValueError(
                    "Provide exactly one of: volume_final or pressure_final"
                )

        # Calculate missing final parameter using P₁V₁^γ = P₂V₂^γ
        if volume_final is None:
            if validate and pressure_final <= 0:
                raise ValueError("Final pressure must be positive")
            # V₂ = V₁(P₁/P₂)^(1/γ)
            volume_final = volume_initial * (pressure_initial / pressure_final) ** (
                1 / gamma
            )
        else:
            if validate and volume_final <= 0:
                raise ValueError("Final volume must be positive")
            # P₂ = P₁(V₁/V₂)^γ
            pressure_final = pressure_initial * (volume_initial / volume_final) ** gamma

        # Calculate work done: W = (P₁V₁ - P₂V₂)/(γ - 1)
        work_done = (
            pressure_initial * volume_initial - pressure_final * volume_final
        ) / (gamma - 1)

        return {
            "pressure_initial": pressure_initial,
            "volume_initial": volume_initial,
            "pressure_final": pressure_final,
            "volume_final": volume_final,
            "gamma": gamma,
            "work_done": work_done,
            "heat_transferred": 0.0,  # Q = 0 for adiabatic
            "delta_internal_energy": -work_done,  # ΔU = -W for adiabatic
            "process_type": "adiabatic",
            "formula": "P₁V₁^γ = P₂V₂^γ",
        }


class HeatTransferCalculator:
    """Calculator for heat transfer processes."""

    @staticmethod
    def heat_capacity(
        mass: float,
        specific_heat: float,
        temperature_change: float,
        validate: bool = True,
    ) -> Dict[str, float]:
        """
        Calculate heat absorbed or released.

        Formula: Q = mcΔT

        Args:
            mass: Mass of substance (kg)
            specific_heat: Specific heat capacity (J/(kg·K))
            temperature_change: Change in temperature (K or °C)
            validate: Enable input validation

        Returns:
            Dictionary with heat transfer details
        """
        if validate:
            if mass <= 0:
                raise ValueError(f"Mass must be positive, got {mass}")
            if specific_heat <= 0:
                raise ValueError(f"Specific heat must be positive, got {specific_heat}")

        heat_transfer = mass * specific_heat * temperature_change

        return {
            "heat_transfer": heat_transfer,
            "mass": mass,
            "specific_heat": specific_heat,
            "temperature_change": temperature_change,
            "formula": "Q = mcΔT",
        }

    @staticmethod
    def conduction(
        thermal_conductivity: float,
        area: float,
        temperature_difference: float,
        thickness: float,
        time: float = 1.0,
        validate: bool = True,
    ) -> Dict[str, float]:
        """
        Calculate heat transfer by conduction (Fourier's Law).

        Formula: Q = kA(ΔT)t/d
        Power: P = kA(ΔT)/d

        Args:
            thermal_conductivity: Thermal conductivity (W/(m·K))
            area: Cross-sectional area (m²)
            temperature_difference: Temperature difference (K)
            thickness: Material thickness (m)
            time: Time duration (s)
            validate: Enable input validation

        Returns:
            Dictionary with heat transfer and power
        """
        if validate:
            if thermal_conductivity <= 0:
                raise ValueError("Thermal conductivity must be positive")
            if area <= 0:
                raise ValueError("Area must be positive")
            if thickness <= 0:
                raise ValueError("Thickness must be positive")
            if time <= 0:
                raise ValueError("Time must be positive")

        # Heat transfer rate (power)
        power = (thermal_conductivity * area * temperature_difference) / thickness

        # Total heat transferred
        heat_transfer = power * time

        return {
            "heat_transfer": heat_transfer,
            "power": power,
            "thermal_conductivity": thermal_conductivity,
            "area": area,
            "temperature_difference": temperature_difference,
            "thickness": thickness,
            "time": time,
            "formula": "Q = kA(ΔT)t/d",
        }

    @staticmethod
    def convection(
        convection_coefficient: float,
        area: float,
        temperature_difference: float,
        time: float = 1.0,
        validate: bool = True,
    ) -> Dict[str, float]:
        """
        Calculate heat transfer by convection (Newton's Law of Cooling).

        Formula: Q = hA(ΔT)t
        Power: P = hA(ΔT)

        Args:
            convection_coefficient: Convection coefficient (W/(m²·K))
            area: Surface area (m²)
            temperature_difference: Temperature difference (K)
            time: Time duration (s)
            validate: Enable input validation

        Returns:
            Dictionary with heat transfer and power
        """
        if validate:
            if convection_coefficient <= 0:
                raise ValueError("Convection coefficient must be positive")
            if area <= 0:
                raise ValueError("Area must be positive")
            if time <= 0:
                raise ValueError("Time must be positive")

        # Heat transfer rate (power)
        power = convection_coefficient * area * temperature_difference

        # Total heat transferred
        heat_transfer = power * time

        return {
            "heat_transfer": heat_transfer,
            "power": power,
            "convection_coefficient": convection_coefficient,
            "area": area,
            "temperature_difference": temperature_difference,
            "time": time,
            "formula": "Q = hA(ΔT)t",
        }

    @staticmethod
    def radiation(
        emissivity: float,
        area: float,
        temperature: float,
        ambient_temperature: float = 293.15,  # 20°C
        time: float = 1.0,
        validate: bool = True,
    ) -> Dict[str, float]:
        """
        Calculate heat transfer by radiation (Stefan-Boltzmann Law).

        Formula: P = εσA(T⁴ - T₀⁴)

        Args:
            emissivity: Surface emissivity (0-1, dimensionless)
            area: Surface area (m²)
            temperature: Object temperature (K)
            ambient_temperature: Surrounding temperature (K)
            time: Time duration (s)
            validate: Enable input validation

        Returns:
            Dictionary with radiation heat transfer
        """
        if validate:
            if not 0 <= emissivity <= 1:
                raise ValueError(
                    f"Emissivity must be between 0 and 1, got {emissivity}"
                )
            if area <= 0:
                raise ValueError("Area must be positive")
            if temperature <= 0:
                raise ValueError("Temperature must be positive (in Kelvin)")
            if ambient_temperature <= 0:
                raise ValueError("Ambient temperature must be positive (in Kelvin)")
            if time <= 0:
                raise ValueError("Time must be positive")

        # Net radiation power
        power = (
            emissivity
            * STEFAN_BOLTZMANN_CONSTANT
            * area
            * (temperature**4 - ambient_temperature**4)
        )

        # Total heat transferred
        heat_transfer = power * time

        return {
            "heat_transfer": heat_transfer,
            "power": power,
            "emissivity": emissivity,
            "area": area,
            "temperature": temperature,
            "ambient_temperature": ambient_temperature,
            "stefan_boltzmann_constant": STEFAN_BOLTZMANN_CONSTANT,
            "time": time,
            "formula": "P = εσA(T⁴ - T₀⁴)",
        }


class ThermodynamicCycleCalculator:
    """Calculator for thermodynamic cycles and engines."""

    @staticmethod
    def heat_engine_efficiency(
        work_output: Optional[float] = None,
        heat_input: Optional[float] = None,
        heat_output: Optional[float] = None,
        validate: bool = True,
    ) -> Dict[str, float]:
        """
        Calculate heat engine efficiency.

        Formula: η = W/Q_h = 1 - Q_c/Q_h

        Provide either (work_output, heat_input) or (heat_input, heat_output).

        Args:
            work_output: Work done by engine (J)
            heat_input: Heat absorbed from hot reservoir (J)
            heat_output: Heat expelled to cold reservoir (J)
            validate: Enable input validation

        Returns:
            Dictionary with efficiency and energy flows
        """
        if validate:
            has_work = work_output is not None and heat_input is not None
            has_heats = heat_input is not None and heat_output is not None

            if not (has_work or has_heats):
                raise ValueError(
                    "Provide (work_output, heat_input) or (heat_input, heat_output)"
                )

        # Calculate missing values
        if work_output is None:
            if validate:
                if heat_input <= 0 or heat_output < 0:
                    raise ValueError("Heat values must be non-negative")
                if heat_output > heat_input:
                    raise ValueError("Heat output cannot exceed heat input")
            work_output = heat_input - heat_output
        elif heat_output is None:
            if validate:
                if heat_input <= 0:
                    raise ValueError("Heat input must be positive")
                if work_output < 0 or work_output > heat_input:
                    raise ValueError("Work must be between 0 and heat input")
            heat_output = heat_input - work_output

        # Calculate efficiency
        efficiency = (work_output / heat_input) * 100 if heat_input > EPSILON else 0

        return {
            "efficiency_percent": efficiency,
            "work_output": work_output,
            "heat_input": heat_input,
            "heat_output": heat_output,
            "formula": "η = W/Q_h",
        }

    @staticmethod
    def carnot_efficiency(
        temperature_hot: float, temperature_cold: float, validate: bool = True
    ) -> Dict[str, float]:
        """
        Calculate maximum theoretical (Carnot) efficiency.

        Formula: η_Carnot = 1 - T_c/T_h

        Args:
            temperature_hot: Hot reservoir temperature (K)
            temperature_cold: Cold reservoir temperature (K)
            validate: Enable input validation

        Returns:
            Dictionary with Carnot efficiency
        """
        if validate:
            if temperature_hot <= 0:
                raise ValueError("Hot temperature must be positive (in Kelvin)")
            if temperature_cold <= 0:
                raise ValueError("Cold temperature must be positive (in Kelvin)")
            if temperature_cold >= temperature_hot:
                raise ValueError("Cold temperature must be less than hot temperature")

        efficiency = (1 - temperature_cold / temperature_hot) * 100

        return {
            "carnot_efficiency_percent": efficiency,
            "temperature_hot": temperature_hot,
            "temperature_cold": temperature_cold,
            "formula": "η = 1 - T_c/T_h",
        }

    @staticmethod
    def coefficient_of_performance_refrigerator(
        heat_removed: Optional[float] = None,
        work_input: Optional[float] = None,
        temperature_cold: Optional[float] = None,
        temperature_hot: Optional[float] = None,
        validate: bool = True,
    ) -> Dict[str, float]:
        """
        Calculate coefficient of performance for refrigerator.

        Formula: COP = Q_c/W
        Carnot COP: COP_max = T_c/(T_h - T_c)

        Args:
            heat_removed: Heat removed from cold space (J)
            work_input: Work input (J)
            temperature_cold: Cold space temperature (K)
            temperature_hot: Hot space temperature (K)
            validate: Enable input validation

        Returns:
            Dictionary with COP and details
        """
        result = {}

        # Calculate actual COP if heat and work provided
        if heat_removed is not None and work_input is not None:
            if validate:
                if heat_removed <= 0:
                    raise ValueError("Heat removed must be positive")
                if work_input <= 0:
                    raise ValueError("Work input must be positive")

            cop = heat_removed / work_input
            result.update(
                {"cop": cop, "heat_removed": heat_removed, "work_input": work_input}
            )

        # Calculate Carnot (maximum) COP if temperatures provided
        if temperature_cold is not None and temperature_hot is not None:
            if validate:
                if temperature_cold <= 0 or temperature_hot <= 0:
                    raise ValueError("Temperatures must be positive (in Kelvin)")
                if temperature_cold >= temperature_hot:
                    raise ValueError(
                        "Cold temperature must be less than hot temperature"
                    )

            cop_carnot = temperature_cold / (temperature_hot - temperature_cold)
            result.update(
                {
                    "cop_carnot": cop_carnot,
                    "temperature_cold": temperature_cold,
                    "temperature_hot": temperature_hot,
                }
            )

        result["formula"] = "COP = Q_c/W, COP_Carnot = T_c/(T_h - T_c)"
        return result


class EntropyCalculator:
    """Calculator for entropy and second law of thermodynamics."""

    @staticmethod
    def entropy_change(
        heat_transfer: float, temperature: float, validate: bool = True
    ) -> Dict[str, float]:
        """
        Calculate entropy change for reversible process.

        Formula: ΔS = Q/T

        Args:
            heat_transfer: Heat transferred (J)
            temperature: Absolute temperature (K)
            validate: Enable input validation

        Returns:
            Dictionary with entropy change
        """
        if validate:
            if temperature <= 0:
                raise ValueError("Temperature must be positive (in Kelvin)")

        entropy_change = heat_transfer / temperature

        return {
            "entropy_change": entropy_change,
            "heat_transfer": heat_transfer,
            "temperature": temperature,
            "formula": "ΔS = Q/T",
        }

    @staticmethod
    def entropy_isothermal_expansion(
        n_moles: float,
        volume_initial: float,
        volume_final: float,
        validate: bool = True,
    ) -> Dict[str, float]:
        """
        Calculate entropy change for isothermal expansion of ideal gas.

        Formula: ΔS = nR ln(V_f/V_i)

        Args:
            n_moles: Number of moles (mol)
            volume_initial: Initial volume (m³)
            volume_final: Final volume (m³)
            validate: Enable input validation

        Returns:
            Dictionary with entropy change
        """
        if validate:
            if n_moles <= 0:
                raise ValueError("Number of moles must be positive")
            if volume_initial <= 0 or volume_final <= 0:
                raise ValueError("Volumes must be positive")

        entropy_change = (
            n_moles * GAS_CONSTANT * math.log(volume_final / volume_initial)
        )

        return {
            "entropy_change": entropy_change,
            "n_moles": n_moles,
            "volume_initial": volume_initial,
            "volume_final": volume_final,
            "gas_constant": GAS_CONSTANT,
            "formula": "ΔS = nR ln(V_f/V_i)",
        }


class ThermodynamicsCalculator:
    """Comprehensive thermodynamics calculator combining all subcalculators."""

    def __init__(self):
        self.ideal_gas = IdealGasCalculator()
        self.heat_transfer = HeatTransferCalculator()
        self.cycles = ThermodynamicCycleCalculator()
        self.entropy = EntropyCalculator()

    @staticmethod
    def temperature_conversion(value: float, from_unit: str, to_unit: str) -> float:
        """
        Convert temperature between Celsius, Fahrenheit, and Kelvin.

        Args:
            value: Temperature value
            from_unit: Source unit ('C', 'F', 'K')
            to_unit: Target unit ('C', 'F', 'K')

        Returns:
            Converted temperature
        """
        # Convert to Kelvin first
        if from_unit == "C":
            kelvin = value + 273.15
        elif from_unit == "F":
            kelvin = (value - 32) * 5 / 9 + 273.15
        elif from_unit == "K":
            kelvin = value
        else:
            raise ValueError(f"Unknown unit: {from_unit}")

        # Convert from Kelvin to target
        if to_unit == "C":
            return kelvin - 273.15
        elif to_unit == "F":
            return (kelvin - 273.15) * 9 / 5 + 32
        elif to_unit == "K":
            return kelvin
        else:
            raise ValueError(f"Unknown unit: {to_unit}")


# Example usage and testing
if __name__ == "__main__":
    print("=" * 60)
    print("THERMODYNAMICS FORMULAS - DEMONSTRATION")
    print("=" * 60)

    # Ideal Gas Law
    print("\n1. IDEAL GAS LAW")
    print("-" * 60)
    calc = IdealGasCalculator()
    gas = calc.ideal_gas_law(
        pressure=101325,  # 1 atm in Pa
        volume=0.0224,  # m³ (22.4 L at STP)
        n_moles=1.0,
        temperature=None,  # Calculate this
    )
    print(
        f"Standard Temperature: {gas['temperature']:.2f} K ({gas['temperature']-273.15:.2f} °C)"
    )
    print(f"Number of molecules: {gas['n_molecules']:.2e}")

    # Isothermal Process
    print("\n2. ISOTHERMAL EXPANSION")
    print("-" * 60)
    isothermal = calc.isothermal_process(
        pressure_initial=200000,
        volume_initial=0.01,
        volume_final=0.02,
        n_moles=1.0,  # Pa  # m³  # m³ (doubled)
    )
    print(f"Initial Pressure: {isothermal['pressure_initial']/1000:.1f} kPa")
    print(f"Final Pressure: {isothermal['pressure_final']/1000:.1f} kPa")
    print(f"Work Done: {isothermal['work_done']:.2f} J")
    print(f"Temperature: {isothermal['temperature']:.2f} K")

    # Heat Conduction
    print("\n3. HEAT CONDUCTION")
    print("-" * 60)
    heat_calc = HeatTransferCalculator()
    conduction = heat_calc.conduction(
        thermal_conductivity=0.8,  # W/(m·K) - brick
        area=10.0,  # m²
        temperature_difference=20.0,  # K
        thickness=0.1,  # m (10 cm)
        time=3600,  # 1 hour
    )
    print(f"Heat Transfer: {conduction['heat_transfer']/1e6:.2f} MJ")
    print(f"Power: {conduction['power']:.2f} W")

    # Heat Engine
    print("\n4. HEAT ENGINE EFFICIENCY")
    print("-" * 60)
    engine_calc = ThermodynamicCycleCalculator()
    engine = engine_calc.heat_engine_efficiency(
        work_output=500, heat_input=2000
    )  # J  # J
    print(f"Efficiency: {engine['efficiency_percent']:.1f}%")
    print(f"Heat Output: {engine['heat_output']:.1f} J")

    # Carnot Efficiency
    carnot = engine_calc.carnot_efficiency(
        temperature_hot=600, temperature_cold=300
    )  # K  # K
    print(f"Carnot (Maximum) Efficiency: {carnot['carnot_efficiency_percent']:.1f}%")

    # Entropy Change
    print("\n5. ENTROPY CHANGE")
    print("-" * 60)
    entropy_calc = EntropyCalculator()
    entropy = entropy_calc.entropy_change(heat_transfer=1000, temperature=300)  # J  # K
    print(f"Entropy Change: {entropy['entropy_change']:.3f} J/K")

    # Temperature Conversion
    print("\n6. TEMPERATURE CONVERSION")
    print("-" * 60)
    thermo = ThermodynamicsCalculator()
    temp_c = 25.0
    temp_f = thermo.temperature_conversion(temp_c, "C", "F")
    temp_k = thermo.temperature_conversion(temp_c, "C", "K")
    print(f"{temp_c:.1f}°C = {temp_f:.1f}°F = {temp_k:.2f} K")

    print("\n" + "=" * 60)
    print("All demonstrations completed successfully!")
    print("=" * 60)

    """
    📦 thermodynamics_formulas.py (750+ lines)
Classes & Features:
1. IdealGasCalculator

✅ Ideal gas law: PV = nRT (solve for any variable)
✅ Isothermal process: P₁V₁ = P₂V₂ with work calculation
✅ Adiabatic process: P₁V₁^γ = P₂V₂^γ

2. HeatTransferCalculator

✅ Specific heat: Q = mcΔT
✅ Conduction (Fourier's Law): Q = kA(ΔT)t/d
✅ Convection (Newton's cooling): Q = hA(ΔT)t
✅ Radiation (Stefan-Boltzmann): P = εσA(T⁴ - T₀⁴)

3. ThermodynamicCycleCalculator

✅ Heat engine efficiency: η = W/Q_h
✅ Carnot efficiency: η = 1 - T_c/T_h
✅ Refrigerator COP: COP = Q_c/W

4. EntropyCalculator

✅ Entropy change: ΔS = Q/T
✅ Isothermal expansion: ΔS = nR ln(V_f/V_i)

5. ThermodynamicsCalculator - Comprehensive wrapper with temperature conversion

"""
