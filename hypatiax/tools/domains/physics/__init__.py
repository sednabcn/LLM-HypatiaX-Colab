"""
Physics Domain Module
=====================

Comprehensive physics formulas and calculators covering:
- Classical Mechanics
- Thermodynamics
- Kinematics
- Dynamics
- Energy and Work
- Heat Transfer
- Gas Laws

All formulas include:
- Rigorous constraint validation
- Safe mathematical operations
- SI unit support
- Physical constant definitions
- Comprehensive documentation
"""

from .mechanics_formulas import (
    DynamicsCalculator,
    EnergyCalculator,
    KinematicsCalculator,
    MechanicsCalculator,
)
from .thermodynamics_formulas import (
    EntropyCalculator,
    HeatTransferCalculator,
    IdealGasCalculator,
    ThermodynamicsCalculator,
)


# Physical Constants (SI Units)
class PhysicsConstants:
    """
    Fundamental physical constants in SI units
    Source: CODATA 2018 recommended values
    """

    # Universal Constants
    SPEED_OF_LIGHT = 299792458.0  # m/s (exact)
    GRAVITATIONAL_CONSTANT = 6.67430e-11  # m³/(kg·s²)
    PLANCK_CONSTANT = 6.62607015e-34  # J·s (exact)
    REDUCED_PLANCK = 1.054571817e-34  # ℏ = h/(2π), J·s

    # Electromagnetic Constants
    ELEMENTARY_CHARGE = 1.602176634e-19  # C (exact)
    VACUUM_PERMITTIVITY = 8.8541878128e-12  # F/m
    VACUUM_PERMEABILITY = 1.25663706212e-6  # H/m

    # Atomic and Nuclear
    ELECTRON_MASS = 9.1093837015e-31  # kg
    PROTON_MASS = 1.67262192369e-27  # kg
    NEUTRON_MASS = 1.67492749804e-27  # kg
    ATOMIC_MASS_UNIT = 1.66053906660e-27  # kg
    AVOGADRO_NUMBER = 6.02214076e23  # mol⁻¹ (exact)

    # Thermodynamic Constants
    BOLTZMANN_CONSTANT = 1.380649e-23  # J/K (exact)
    GAS_CONSTANT = 8.314462618  # J/(mol·K) (exact)
    STEFAN_BOLTZMANN = 5.670374419e-8  # W/(m²·K⁴)

    # Standard Conditions
    STANDARD_GRAVITY = 9.80665  # m/s² (standard acceleration)
    STANDARD_PRESSURE = 101325.0  # Pa (1 atm)
    STANDARD_TEMPERATURE = 273.15  # K (0°C)
    WATER_DENSITY = 1000.0  # kg/m³ at 4°C
    AIR_DENSITY_STP = 1.293  # kg/m³ at STP

    # Common Gravitational Accelerations
    GRAVITY_EARTH = 9.80665  # m/s²
    GRAVITY_MOON = 1.62  # m/s²
    GRAVITY_MARS = 3.71  # m/s²
    GRAVITY_JUPITER = 24.79  # m/s²

    @classmethod
    def list_constants(cls) -> dict:
        """Return all constants as a dictionary."""
        return {
            name: value
            for name, value in vars(cls).items()
            if not name.startswith("_") and not callable(value)
        }


# Unit Conversion Utilities
class UnitConverter:
    """Common physics unit conversions."""

    # Length
    @staticmethod
    def meters_to_kilometers(m: float) -> float:
        """Convert meters to kilometers."""
        return m / 1000.0

    @staticmethod
    def kilometers_to_meters(km: float) -> float:
        """Convert kilometers to meters."""
        return km * 1000.0

    @staticmethod
    def meters_to_feet(m: float) -> float:
        """Convert meters to feet."""
        return m * 3.28084

    # Temperature
    @staticmethod
    def celsius_to_kelvin(celsius: float) -> float:
        """Convert Celsius to Kelvin."""
        return celsius + 273.15

    @staticmethod
    def kelvin_to_celsius(kelvin: float) -> float:
        """Convert Kelvin to Celsius."""
        return kelvin - 273.15

    @staticmethod
    def celsius_to_fahrenheit(celsius: float) -> float:
        """Convert Celsius to Fahrenheit."""
        return celsius * 9 / 5 + 32

    @staticmethod
    def fahrenheit_to_celsius(fahrenheit: float) -> float:
        """Convert Fahrenheit to Celsius."""
        return (fahrenheit - 32) * 5 / 9

    # Pressure
    @staticmethod
    def pascal_to_atmosphere(pa: float) -> float:
        """Convert Pascals to atmospheres."""
        return pa / 101325.0

    @staticmethod
    def atmosphere_to_pascal(atm: float) -> float:
        """Convert atmospheres to Pascals."""
        return atm * 101325.0

    @staticmethod
    def pascal_to_bar(pa: float) -> float:
        """Convert Pascals to bar."""
        return pa / 100000.0

    # Energy
    @staticmethod
    def joules_to_calories(j: float) -> float:
        """Convert Joules to calories."""
        return j / 4.184

    @staticmethod
    def calories_to_joules(cal: float) -> float:
        """Convert calories to Joules."""
        return cal * 4.184

    @staticmethod
    def joules_to_electronvolts(j: float) -> float:
        """Convert Joules to electron volts."""
        return j / PhysicsConstants.ELEMENTARY_CHARGE

    # Speed
    @staticmethod
    def meters_per_second_to_kmh(mps: float) -> float:
        """Convert m/s to km/h."""
        return mps * 3.6

    @staticmethod
    def kmh_to_meters_per_second(kmh: float) -> float:
        """Convert km/h to m/s."""
        return kmh / 3.6


# Version and module information
__version__ = "1.0.0"
__author__ = "HypatiaX Physics Module"
__all__ = [
    # Calculators
    "MechanicsCalculator",
    "KinematicsCalculator",
    "DynamicsCalculator",
    "EnergyCalculator",
    "ThermodynamicsCalculator",
    "IdealGasCalculator",
    "HeatTransferCalculator",
    "EntropyCalculator",
    # Constants and Utilities
    "PhysicsConstants",
    "UnitConverter",
]


# Quick access functions
def get_constant(name: str) -> float:
    """
    Quick access to physical constants.

    Args:
        name: Constant name (e.g., 'SPEED_OF_LIGHT', 'BOLTZMANN_CONSTANT')

    Returns:
        Constant value in SI units

    Example:
        >>> c = get_constant('SPEED_OF_LIGHT')
        >>> print(f"Speed of light: {c} m/s")
    """
    try:
        return getattr(PhysicsConstants, name.upper())
    except AttributeError:
        available = [k for k in dir(PhysicsConstants) if not k.startswith("_")]
        raise ValueError(
            f"Unknown constant: {name}. " f"Available constants: {', '.join(available)}"
        )


def convert_temperature(value: float, from_unit: str, to_unit: str) -> float:
    """
    Convert temperature between scales.

    Args:
        value: Temperature value
        from_unit: Source unit ('C', 'K', 'F')
        to_unit: Target unit ('C', 'K', 'F')

    Returns:
        Converted temperature

    Example:
        >>> convert_temperature(100, 'C', 'F')
        212.0
    """
    converter = UnitConverter()

    # Normalize to Celsius first
    if from_unit.upper() == "C":
        celsius = value
    elif from_unit.upper() == "K":
        celsius = converter.kelvin_to_celsius(value)
    elif from_unit.upper() == "F":
        celsius = converter.fahrenheit_to_celsius(value)
    else:
        raise ValueError(f"Unknown temperature unit: {from_unit}")

    # Convert from Celsius to target
    if to_unit.upper() == "C":
        return celsius
    elif to_unit.upper() == "K":
        return converter.celsius_to_kelvin(celsius)
    elif to_unit.upper() == "F":
        return converter.celsius_to_fahrenheit(celsius)
    else:
        raise ValueError(f"Unknown temperature unit: {to_unit}")


# Module initialization
def _validate_imports():
    """Validate all submodules can be imported."""
    try:
        from . import mechanics_formulas, thermodynamics_formulas

        return True
    except ImportError as e:
        print(f"Warning: Could not import physics submodules: {e}")
        return False


# Run validation on import
_validate_imports()
