"""
Chemistry Domain - Core Module
===============================

This module provides comprehensive chemistry calculations including:
- Chemical kinetics and rate equations
- Chemical equilibrium and equilibrium constants
- Thermodynamic properties
- Solution chemistry and concentrations

All formulas include validation and return detailed results.

Author: Chemistry Domain Team
Version: 1.0.0
"""

import math
from typing import Dict, List, Optional

# ============================================================================
# FUNDAMENTAL CONSTANTS (CODATA 2018)
# ============================================================================


class ChemistryConstants:
    """Fundamental constants for chemistry calculations."""

    # Universal Constants
    AVOGADRO_NUMBER = 6.02214076e23  # mol⁻¹
    GAS_CONSTANT = 8.314462618  # J/(mol·K)
    BOLTZMANN_CONSTANT = 1.380649e-23  # J/K
    PLANCK_CONSTANT = 6.62607015e-34  # J·s

    # Energy and Temperature
    STANDARD_TEMPERATURE = 298.15  # K (25°C)
    STANDARD_PRESSURE = 1.0e5  # Pa (1 bar)
    ABSOLUTE_ZERO_CELSIUS = -273.15  # °C

    # Electrochemistry
    FARADAY_CONSTANT = 96485.33212  # C/mol
    ELEMENTARY_CHARGE = 1.602176634e-19  # C

    # Other Standards
    STANDARD_MOLAR_VOLUME = 0.0224  # m³/mol at STP (22.4 L/mol)
    ATMOSPHERIC_PRESSURE = 101325  # Pa (1 atm)

    @classmethod
    def get_all_constants(cls) -> Dict[str, float]:
        """Return all constants as a dictionary."""
        return {
            "avogadro_number": cls.AVOGADRO_NUMBER,
            "gas_constant": cls.GAS_CONSTANT,
            "boltzmann_constant": cls.BOLTZMANN_CONSTANT,
            "planck_constant": cls.PLANCK_CONSTANT,
            "standard_temperature": cls.STANDARD_TEMPERATURE,
            "standard_pressure": cls.STANDARD_PRESSURE,
            "faraday_constant": cls.FARADAY_CONSTANT,
            "elementary_charge": cls.ELEMENTARY_CHARGE,
        }


# ============================================================================
# UNIT CONVERSIONS
# ============================================================================


class UnitConverter:
    """Unit conversion utilities for chemistry."""

    @staticmethod
    def temperature_to_kelvin(value: float, from_unit: str) -> float:
        """
        Convert temperature to Kelvin.

        Args:
            value: Temperature value
            from_unit: Source unit ('C', 'F', 'K')

        Returns:
            Temperature in Kelvin
        """
        if from_unit == "K":
            return value
        elif from_unit == "C":
            return value + 273.15
        elif from_unit == "F":
            return (value - 32) * 5 / 9 + 273.15
        else:
            raise ValueError(f"Unknown temperature unit: {from_unit}")

    @staticmethod
    def temperature_from_kelvin(value: float, to_unit: str) -> float:
        """
        Convert temperature from Kelvin.

        Args:
            value: Temperature in Kelvin
            to_unit: Target unit ('C', 'F', 'K')

        Returns:
            Converted temperature
        """
        if to_unit == "K":
            return value
        elif to_unit == "C":
            return value - 273.15
        elif to_unit == "F":
            return (value - 273.15) * 9 / 5 + 32
        else:
            raise ValueError(f"Unknown temperature unit: {to_unit}")

    @staticmethod
    def pressure_to_pascal(value: float, from_unit: str) -> float:
        """
        Convert pressure to Pascals.

        Args:
            value: Pressure value
            from_unit: Source unit ('Pa', 'kPa', 'atm', 'bar', 'mmHg', 'psi')

        Returns:
            Pressure in Pascals
        """
        conversions = {
            "Pa": 1.0,
            "kPa": 1000.0,
            "atm": 101325.0,
            "bar": 1.0e5,
            "mmHg": 133.322,
            "torr": 133.322,
            "psi": 6894.76,
        }

        if from_unit not in conversions:
            raise ValueError(f"Unknown pressure unit: {from_unit}")

        return value * conversions[from_unit]

    @staticmethod
    def concentration_to_molarity(
        value: float, from_unit: str, molar_mass: Optional[float] = None, density: Optional[float] = None
    ) -> float:
        """
        Convert concentration to molarity (mol/L).

        Args:
            value: Concentration value
            from_unit: Source unit ('M', 'mM', 'μM', 'g/L', 'mg/mL', 'ppm')
            molar_mass: Molar mass (g/mol) - required for mass-based units
            density: Solution density (g/mL) - required for ppm

        Returns:
            Concentration in molarity (mol/L)
        """
        if from_unit == "M":
            return value
        elif from_unit == "mM":
            return value / 1000.0
        elif from_unit == "μM" or from_unit == "uM":
            return value / 1.0e6
        elif from_unit == "g/L":
            if molar_mass is None:
                raise ValueError("Molar mass required for g/L conversion")
            return value / molar_mass
        elif from_unit == "mg/mL":
            if molar_mass is None:
                raise ValueError("Molar mass required for mg/mL conversion")
            return (value * 1000.0) / molar_mass  # mg/mL to g/L then to M
        elif from_unit == "ppm":
            if molar_mass is None or density is None:
                raise ValueError("Molar mass and density required for ppm conversion")
            # ppm = mg/L (assuming aqueous solution)
            return (value / 1000.0) / molar_mass
        else:
            raise ValueError(f"Unknown concentration unit: {from_unit}")

    @staticmethod
    def energy_to_joules(value: float, from_unit: str) -> float:
        """
        Convert energy to Joules.

        Args:
            value: Energy value
            from_unit: Source unit ('J', 'kJ', 'cal', 'kcal', 'eV')

        Returns:
            Energy in Joules
        """
        conversions = {
            "J": 1.0,
            "kJ": 1000.0,
            "cal": 4.184,
            "kcal": 4184.0,
            "eV": 1.602176634e-19,
        }

        if from_unit not in conversions:
            raise ValueError(f"Unknown energy unit: {from_unit}")

        return value * conversions[from_unit]


# ============================================================================
# HELPER FUNCTIONS
# ============================================================================


def get_constant(name: str) -> float:
    """
    Retrieve a chemistry constant by name.

    Args:
        name: Constant name (case-insensitive)

    Returns:
        Constant value

    Example:
        >>> R = get_constant('gas_constant')
        >>> Na = get_constant('avogadro_number')
    """
    name_lower = name.lower().replace(" ", "_")
    constants = ChemistryConstants.get_all_constants()

    if name_lower not in constants:
        raise ValueError(f"Unknown constant: {name}. " f"Available: {', '.join(constants.keys())}")

    return constants[name_lower]


def convert_temperature(value: float, from_unit: str, to_unit: str) -> float:
    """
    Convert temperature between units.

    Args:
        value: Temperature value
        from_unit: Source unit ('C', 'F', 'K')
        to_unit: Target unit ('C', 'F', 'K')

    Returns:
        Converted temperature

    Example:
        >>> celsius = convert_temperature(298.15, 'K', 'C')
        >>> fahrenheit = convert_temperature(25, 'C', 'F')
    """
    kelvin = UnitConverter.temperature_to_kelvin(value, from_unit)
    return UnitConverter.temperature_from_kelvin(kelvin, to_unit)


def moles_to_molecules(moles: float) -> float:
    """
    Convert moles to number of molecules.

    Args:
        moles: Amount in moles

    Returns:
        Number of molecules
    """
    return moles * ChemistryConstants.AVOGADRO_NUMBER


def molecules_to_moles(molecules: float) -> float:
    """
    Convert number of molecules to moles.

    Args:
        molecules: Number of molecules

    Returns:
        Amount in moles
    """
    return molecules / ChemistryConstants.AVOGADRO_NUMBER


def calculate_molarity(moles: float, volume_liters: float) -> float:
    """
    Calculate molarity (concentration).

    Formula: M = n/V

    Args:
        moles: Amount of solute (mol)
        volume_liters: Volume of solution (L)

    Returns:
        Molarity (mol/L)
    """
    if volume_liters <= 0:
        raise ValueError("Volume must be positive")

    return moles / volume_liters


def calculate_mass_from_moles(moles: float, molar_mass: float) -> float:
    """
    Calculate mass from moles.

    Formula: m = n × M

    Args:
        moles: Amount in moles
        molar_mass: Molar mass (g/mol)

    Returns:
        Mass in grams
    """
    if molar_mass <= 0:
        raise ValueError("Molar mass must be positive")

    return moles * molar_mass


def calculate_moles_from_mass(mass: float, molar_mass: float) -> float:
    """
    Calculate moles from mass.

    Formula: n = m/M

    Args:
        mass: Mass in grams
        molar_mass: Molar mass (g/mol)

    Returns:
        Amount in moles
    """
    if molar_mass <= 0:
        raise ValueError("Molar mass must be positive")

    return mass / molar_mass


def dilution_calculation(
    concentration_initial: float,
    volume_initial: float,
    concentration_final: Optional[float] = None,
    volume_final: Optional[float] = None,
) -> Dict[str, float]:
    """
    Calculate dilution using C₁V₁ = C₂V₂.

    Provide 3 of 4 parameters to calculate the 4th.

    Args:
        concentration_initial: Initial concentration (M)
        volume_initial: Initial volume (L)
        concentration_final: Final concentration (M)
        volume_final: Final volume (L)

    Returns:
        Dictionary with all dilution parameters
    """
    params = [concentration_initial, volume_initial, concentration_final, volume_final]
    provided = sum(p is not None for p in params)

    if provided != 3:
        raise ValueError("Must provide exactly 3 parameters")

    if concentration_initial is None:
        if volume_initial is None or concentration_final is None or volume_final is None:
            raise ValueError("Invalid parameter combination")
        concentration_initial = (concentration_final * volume_final) / volume_initial
    elif volume_initial is None:
        if concentration_initial is None or concentration_final is None or volume_final is None:
            raise ValueError("Invalid parameter combination")
        volume_initial = (concentration_final * volume_final) / concentration_initial
    elif concentration_final is None:
        concentration_final = (concentration_initial * volume_initial) / volume_final
    else:  # volume_final is None
        volume_final = (concentration_initial * volume_initial) / concentration_final

    dilution_factor = concentration_initial / concentration_final if concentration_final > 0 else 0
    volume_to_add = volume_final - volume_initial

    return {
        "concentration_initial": concentration_initial,
        "volume_initial": volume_initial,
        "concentration_final": concentration_final,
        "volume_final": volume_final,
        "dilution_factor": dilution_factor,
        "volume_to_add": volume_to_add,
        "formula": "C₁V₁ = C₂V₂",
    }


def pH_from_concentration(concentration: float, is_acid: bool = True) -> float:
    """
    Calculate pH from H⁺ or OH⁻ concentration.

    Args:
        concentration: Ion concentration (M)
        is_acid: True for H⁺ concentration, False for OH⁻

    Returns:
        pH value
    """
    if concentration <= 0:
        raise ValueError("Concentration must be positive")

    if is_acid:
        # pH = -log[H⁺]
        return -math.log10(concentration)
    else:
        # pOH = -log[OH⁻], pH = 14 - pOH
        pOH = -math.log10(concentration)
        return 14.0 - pOH


def concentration_from_pH(pH: float, is_acid: bool = True) -> float:
    """
    Calculate H⁺ or OH⁻ concentration from pH.

    Args:
        pH: pH value
        is_acid: True to calculate H⁺, False for OH⁻

    Returns:
        Ion concentration (M)
    """
    if not 0 <= pH <= 14:
        raise ValueError("pH must be between 0 and 14")

    if is_acid:
        # [H⁺] = 10^(-pH)
        return 10 ** (-pH)
    else:
        # pOH = 14 - pH, [OH⁻] = 10^(-pOH)
        pOH = 14.0 - pH
        return 10 ** (-pOH)


# ============================================================================
# MODULE EXPORTS
# ============================================================================

# Import calculators from submodules
try:
    from .equilibrium_formulas import (
        AcidBaseEquilibriumCalculator,
        EquilibriumCalculator,
        EquilibriumConstantCalculator,
        SolubilityCalculator,
    )
    from .rate_equations import ArrheniusCalculator, HalfLifeCalculator, KineticsCalculator, RateEquationCalculator

    __all__ = [
        # Constants and conversions
        "ChemistryConstants",
        "UnitConverter",
        # Helper functions
        "get_constant",
        "convert_temperature",
        "moles_to_molecules",
        "molecules_to_moles",
        "calculate_molarity",
        "calculate_mass_from_moles",
        "calculate_moles_from_mass",
        "dilution_calculation",
        "pH_from_concentration",
        "concentration_from_pH",
        # Rate equations module
        "RateEquationCalculator",
        "ArrheniusCalculator",
        "HalfLifeCalculator",
        "KineticsCalculator",
        # Equilibrium module
        "EquilibriumConstantCalculator",
        "AcidBaseEquilibriumCalculator",
        "SolubilityCalculator",
        "EquilibriumCalculator",
    ]

except ImportError:
    # Submodules not yet available
    __all__ = [
        "ChemistryConstants",
        "UnitConverter",
        "get_constant",
        "convert_temperature",
        "moles_to_molecules",
        "molecules_to_moles",
        "calculate_molarity",
        "calculate_mass_from_moles",
        "calculate_moles_from_mass",
        "dilution_calculation",
        "pH_from_concentration",
        "concentration_from_pH",
    ]


# ============================================================================
# DEMO AND TESTING
# ============================================================================

if __name__ == "__main__":
    print("=" * 70)
    print("CHEMISTRY DOMAIN - CORE MODULE DEMONSTRATION")
    print("=" * 70)

    # Constants
    print("\n1. FUNDAMENTAL CONSTANTS")
    print("-" * 70)
    print(f"Avogadro's number: {ChemistryConstants.AVOGADRO_NUMBER:.3e} mol⁻¹")
    print(f"Gas constant: {ChemistryConstants.GAS_CONSTANT:.6f} J/(mol·K)")
    print(f"Faraday constant: {ChemistryConstants.FARADAY_CONSTANT:.2f} C/mol")
    print(f"Standard temperature: {ChemistryConstants.STANDARD_TEMPERATURE:.2f} K")

    # Temperature conversion
    print("\n2. TEMPERATURE CONVERSION")
    print("-" * 70)
    temp_k = 298.15
    temp_c = convert_temperature(temp_k, "K", "C")
    temp_f = convert_temperature(temp_k, "K", "F")
    print(f"{temp_k:.2f} K = {temp_c:.2f} °C = {temp_f:.2f} °F")

    # Moles to molecules
    print("\n3. MOLES ↔ MOLECULES CONVERSION")
    print("-" * 70)
    n_moles = 2.5
    n_molecules = moles_to_molecules(n_moles)
    print(f"{n_moles} mol = {n_molecules:.3e} molecules")
    print(f"{n_molecules:.3e} molecules = {molecules_to_moles(n_molecules):.2f} mol")

    # Molarity calculation
    print("\n4. MOLARITY CALCULATION")
    print("-" * 70)
    moles = 0.5
    volume_L = 2.0
    molarity = calculate_molarity(moles, volume_L)
    print(f"{moles} mol in {volume_L} L → Molarity = {molarity} M")

    # Mass and moles
    print("\n5. MASS ↔ MOLES CONVERSION")
    print("-" * 70)
    mass_g = 18.0  # Water
    molar_mass = 18.015  # g/mol
    moles = calculate_moles_from_mass(mass_g, molar_mass)
    print(f"{mass_g} g of H₂O = {moles:.3f} mol")
    print(f"{moles:.3f} mol of H₂O = {calculate_mass_from_moles(moles, molar_mass):.2f} g")

    # Dilution
    print("\n6. DILUTION CALCULATION (C₁V₁ = C₂V₂)")
    print("-" * 70)
    dilution = dilution_calculation(
        concentration_initial=2.0, volume_initial=0.1, concentration_final=0.5, volume_final=None  # M  # L  # M
    )
    print(f"Initial: {dilution['concentration_initial']:.2f} M × {dilution['volume_initial']:.2f} L")
    print(f"Final: {dilution['concentration_final']:.2f} M × {dilution['volume_final']:.2f} L")
    print(f"Dilution factor: {dilution['dilution_factor']:.1f}×")
    print(f"Volume to add: {dilution['volume_to_add']:.2f} L")

    # pH calculations
    print("\n7. pH CALCULATIONS")
    print("-" * 70)
    h_concentration = 1.0e-7  # Neutral
    pH = pH_from_concentration(h_concentration)
    print(f"[H⁺] = {h_concentration:.1e} M → pH = {pH:.2f}")

    pH_value = 3.0  # Acidic
    h_conc = concentration_from_pH(pH_value)
    print(f"pH = {pH_value:.1f} → [H⁺] = {h_conc:.1e} M")

    # Unit conversions
    print("\n8. UNIT CONVERSIONS")
    print("-" * 70)
    pressure_atm = 1.0
    pressure_pa = UnitConverter.pressure_to_pascal(pressure_atm, "atm")
    print(f"{pressure_atm} atm = {pressure_pa:.0f} Pa")

    conc_mM = 500.0
    conc_M = UnitConverter.concentration_to_molarity(conc_mM, "mM")
    print(f"{conc_mM} mM = {conc_M} M")

    print("\n" + "=" * 70)
    print("Core module demonstration completed successfully!")
    print("=" * 70)
