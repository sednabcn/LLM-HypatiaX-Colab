"""
Electromagnetism Formulas
==========================

Comprehensive electromagnetic theory calculations including:
- Electric fields and forces (Coulomb's law)
- Electric potential and capacitance
- Magnetic fields and forces
- Electromagnetic induction
- Circuits (Ohm's law, RC, RL circuits)
- Maxwell's equations applications

All formulas with rigorous validation and SI units.
"""

import math
from dataclasses import dataclass
from enum import Enum
from typing import Dict, List, Optional, Tuple

EPSILON = 1e-12

# Physical Constants
epsilon_0 = 8.8541878128e-12  # Permittivity of free space (F/m)
mu_0 = 1.25663706212e-6  # Permeability of free space (H/m)
c = 299792458.0  # Speed of light (m/s)
e = 1.602176634e-19  # Elementary charge (C)
k_e = 8.9875517923e9  # Coulomb's constant (N·m²/C²)


class CircuitType(Enum):
    """Types of electrical circuits."""

    SERIES = "series"
    PARALLEL = "parallel"
    RC = "rc"
    RL = "rl"
    RLC = "rlc"


@dataclass
class Vector3D:
    """3D vector for fields and forces."""

    x: float
    y: float
    z: float

    def magnitude(self) -> float:
        """Calculate vector magnitude."""
        return math.sqrt(self.x**2 + self.y**2 + self.z**2)

    def dot(self, other: "Vector3D") -> float:
        """Dot product with another vector."""
        return self.x * other.x + self.y * other.y + self.z * other.z

    def cross(self, other: "Vector3D") -> "Vector3D":
        """Cross product with another vector."""
        return Vector3D(
            self.y * other.z - self.z * other.y,
            self.z * other.x - self.x * other.z,
            self.x * other.y - self.y * other.x,
        )


class ElectrostaticsCalculator:
    """
    Electrostatics formulas - electric charges, fields, and potential.
    """

    @staticmethod
    def coulombs_law(
        charge1: float,
        charge2: float,
        distance: float,
        k: float = k_e,
        validate: bool = True,
    ) -> Dict:
        """
        Calculate electrostatic force between two charges.
        Formula: F = k|q₁q₂|/r²

        CONSTRAINTS:
        - distance > 0
        - k > 0

        Args:
            charge1: First charge (C)
            charge2: Second charge (C)
            distance: Separation distance (m)
            k: Coulomb's constant (default: 8.988×10⁹ N·m²/C²)
            validate: Enable validation

        Returns:
            Dict with force magnitude, direction, and potential energy
        """
        if validate:
            if distance <= 0:
                raise ValueError(f"distance must be > 0, got {distance}")
            if k <= 0:
                raise ValueError(f"k must be > 0, got {k}")

        # Force magnitude
        force_magnitude = k * abs(charge1 * charge2) / max(distance**2, EPSILON)

        # Electric potential energy: U = kq₁q₂/r
        potential_energy = k * charge1 * charge2 / max(distance, EPSILON)

        # Determine if attractive or repulsive
        interaction = "attractive" if (charge1 * charge2) < 0 else "repulsive"

        return {
            "charge1": charge1,
            "charge2": charge2,
            "distance": distance,
            "coulomb_constant": k,
            "force_magnitude": force_magnitude,
            "potential_energy": potential_energy,
            "interaction_type": interaction,
        }

    @staticmethod
    def electric_field_point_charge(
        charge: float, distance: float, k: float = k_e, validate: bool = True
    ) -> Dict:
        """
        Calculate electric field from a point charge.
        Formula: E = kq/r²

        CONSTRAINTS:
        - distance > 0
        - k > 0

        Returns:
            Electric field magnitude and direction
        """
        if validate:
            if distance <= 0:
                raise ValueError(f"distance must be > 0, got {distance}")
            if k <= 0:
                raise ValueError(f"k must be > 0, got {k}")

        # Field magnitude
        field_magnitude = k * abs(charge) / max(distance**2, EPSILON)

        # Electric potential: V = kq/r
        potential = k * charge / max(distance, EPSILON)

        # Field direction
        direction = "outward" if charge > 0 else "inward"

        return {
            "charge": charge,
            "distance": distance,
            "field_magnitude": field_magnitude,
            "field_direction": direction,
            "electric_potential": potential,
            "units": "N/C or V/m",
        }

    @staticmethod
    def electric_potential_energy(
        charge: float, potential: float, validate: bool = True
    ) -> Dict:
        """
        Calculate potential energy of a charge in an electric field.
        Formula: U = qV

        Args:
            charge: Charge (C)
            potential: Electric potential (V)

        Returns:
            Potential energy in Joules
        """
        energy = charge * potential

        # Energy in electron volts (useful for atomic scale)
        energy_eV = energy / e

        return {
            "charge": charge,
            "potential": potential,
            "energy_joules": energy,
            "energy_eV": energy_eV,
        }

    @staticmethod
    def capacitance(
        charge: float = None,
        voltage: float = None,
        capacitance_value: float = None,
        validate: bool = True,
    ) -> Dict:
        """
        Capacitor relationship: Q = CV
        Provide 2 of 3 parameters.

        CONSTRAINTS:
        - C > 0 (Farads)
        - V ≥ 0 (Volts)
        - Q ≥ 0 (Coulombs)

        Returns:
            All capacitor parameters and energy stored
        """
        params_given = sum(
            [charge is not None, voltage is not None, capacitance_value is not None]
        )

        if params_given != 2:
            raise ValueError("Must provide exactly 2 of 3 parameters")

        # Calculate missing parameter
        if charge is None:
            charge = capacitance_value * voltage
        elif voltage is None:
            voltage = charge / max(capacitance_value, EPSILON)
        elif capacitance_value is None:
            capacitance_value = charge / max(voltage, EPSILON)

        if validate:
            if capacitance_value <= 0:
                raise ValueError(f"capacitance must be > 0, got {capacitance_value}")
            if voltage < 0:
                raise ValueError(f"voltage must be ≥ 0, got {voltage}")
            if charge < 0:
                raise ValueError(f"charge must be ≥ 0, got {charge}")

        # Energy stored: U = ½CV²
        energy_stored = 0.5 * capacitance_value * voltage**2

        return {
            "capacitance": capacitance_value,
            "capacitance_uF": capacitance_value * 1e6,
            "voltage": voltage,
            "charge": charge,
            "energy_stored": energy_stored,
            "energy_stored_mJ": energy_stored * 1000,
        }

    @staticmethod
    def parallel_plate_capacitor(
        area: float,
        separation: float,
        dielectric_constant: float = 1.0,
        epsilon_0_val: float = epsilon_0,
        validate: bool = True,
    ) -> Dict:
        """
        Parallel plate capacitor capacitance.
        Formula: C = ε₀εᵣA/d

        CONSTRAINTS:
        - area > 0 (m²)
        - separation > 0 (m)
        - dielectric_constant ≥ 1

        Returns:
            Capacitance and electric field between plates
        """
        if validate:
            if area <= 0:
                raise ValueError(f"area must be > 0, got {area}")
            if separation <= 0:
                raise ValueError(f"separation must be > 0, got {separation}")
            if dielectric_constant < 1:
                raise ValueError(
                    f"dielectric_constant must be ≥ 1, got {dielectric_constant}"
                )

        # Capacitance
        capacitance = epsilon_0_val * dielectric_constant * area / separation

        return {
            "area": area,
            "separation": separation,
            "dielectric_constant": dielectric_constant,
            "capacitance": capacitance,
            "capacitance_pF": capacitance * 1e12,
            "note": "Assumes uniform field between plates",
        }


class MagnetismCalculator:
    """
    Magnetic fields, forces, and electromagnetic induction.
    """

    @staticmethod
    def magnetic_force_on_charge(
        charge: float,
        velocity: float,
        magnetic_field: float,
        angle_degrees: float = 90.0,
        validate: bool = True,
    ) -> Dict:
        """
        Lorentz force on a moving charge in a magnetic field.
        Formula: F = qvB sin(θ)

        CONSTRAINTS:
        - velocity ≥ 0
        - magnetic_field ≥ 0 (Tesla)
        - angle ∈ [0, 180] degrees

        Returns:
            Force magnitude and direction
        """
        if validate:
            if velocity < 0:
                raise ValueError(f"velocity must be ≥ 0, got {velocity}")
            if magnetic_field < 0:
                raise ValueError(f"magnetic_field must be ≥ 0, got {magnetic_field}")
            if not (0 <= angle_degrees <= 180):
                raise ValueError(f"angle must be in [0, 180], got {angle_degrees}")

        angle_rad = math.radians(angle_degrees)

        # Force magnitude
        force = abs(charge) * velocity * magnetic_field * math.sin(angle_rad)

        # Maximum force occurs at 90 degrees
        force_max = abs(charge) * velocity * magnetic_field

        return {
            "charge": charge,
            "velocity": velocity,
            "magnetic_field": magnetic_field,
            "angle_degrees": angle_degrees,
            "force": force,
            "force_max": force_max,
            "perpendicular": abs(angle_degrees - 90) < 1,
        }

    @staticmethod
    def magnetic_force_on_wire(
        current: float,
        length: float,
        magnetic_field: float,
        angle_degrees: float = 90.0,
        validate: bool = True,
    ) -> Dict:
        """
        Force on a current-carrying wire in a magnetic field.
        Formula: F = ILB sin(θ)

        CONSTRAINTS:
        - current ≥ 0 (Amperes)
        - length > 0 (meters)
        - magnetic_field ≥ 0 (Tesla)
        - angle ∈ [0, 180] degrees

        Returns:
            Force magnitude
        """
        if validate:
            if current < 0:
                raise ValueError(f"current must be ≥ 0, got {current}")
            if length <= 0:
                raise ValueError(f"length must be > 0, got {length}")
            if magnetic_field < 0:
                raise ValueError(f"magnetic_field must be ≥ 0, got {magnetic_field}")
            if not (0 <= angle_degrees <= 180):
                raise ValueError(f"angle must be in [0, 180], got {angle_degrees}")

        angle_rad = math.radians(angle_degrees)
        force = current * length * magnetic_field * math.sin(angle_rad)

        return {
            "current": current,
            "length": length,
            "magnetic_field": magnetic_field,
            "angle_degrees": angle_degrees,
            "force": force,
        }

    @staticmethod
    def faradays_law(
        n_turns: int, flux_change: float, time_interval: float, validate: bool = True
    ) -> Dict:
        """
        Electromagnetic induction (Faraday's Law).
        Formula: ε = -N(ΔΦ/Δt)

        CONSTRAINTS:
        - n_turns > 0
        - time_interval > 0

        Args:
            n_turns: Number of coil turns
            flux_change: Change in magnetic flux (Wb)
            time_interval: Time for change (s)

        Returns:
            Induced EMF (voltage)
        """
        if validate:
            if n_turns <= 0:
                raise ValueError(f"n_turns must be > 0, got {n_turns}")
            if time_interval <= 0:
                raise ValueError(f"time_interval must be > 0, got {time_interval}")

        # Induced EMF (magnitude)
        emf = n_turns * abs(flux_change) / time_interval

        # Rate of flux change
        flux_rate = flux_change / time_interval

        return {
            "n_turns": n_turns,
            "flux_change": flux_change,
            "time_interval": time_interval,
            "induced_emf": emf,
            "flux_rate": flux_rate,
            "lenz_law": "EMF opposes the change causing it",
        }

    @staticmethod
    def magnetic_field_solenoid(
        current: float,
        n_turns: float,
        length: float,
        mu_0_val: float = mu_0,
        validate: bool = True,
    ) -> Dict:
        """
        Magnetic field inside a solenoid.
        Formula: B = μ₀nI
        where n = N/L (turns per unit length)

        CONSTRAINTS:
        - current ≥ 0
        - n_turns > 0
        - length > 0

        Returns:
            Magnetic field strength (Tesla)
        """
        if validate:
            if current < 0:
                raise ValueError(f"current must be ≥ 0, got {current}")
            if n_turns <= 0:
                raise ValueError(f"n_turns must be > 0, got {n_turns}")
            if length <= 0:
                raise ValueError(f"length must be > 0, got {length}")

        # Turns per unit length
        n = n_turns / length

        # Magnetic field
        B = mu_0_val * n * current

        return {
            "current": current,
            "n_turns": n_turns,
            "length": length,
            "turns_per_meter": n,
            "magnetic_field": B,
            "magnetic_field_mT": B * 1000,
        }


class CircuitsCalculator:
    """
    DC and AC circuit analysis.
    """

    @staticmethod
    def ohms_law(
        voltage: float = None,
        current: float = None,
        resistance: float = None,
        validate: bool = True,
    ) -> Dict:
        """
        Ohm's Law: V = IR
        Provide 2 of 3 parameters.

        CONSTRAINTS:
        - V ≥ 0 (Volts)
        - I ≥ 0 (Amperes)
        - R > 0 (Ohms)

        Returns:
            All circuit parameters and power
        """
        params_given = sum(
            [voltage is not None, current is not None, resistance is not None]
        )

        if params_given != 2:
            raise ValueError("Must provide exactly 2 of 3 parameters")

        # Calculate missing parameter
        if voltage is None:
            voltage = current * resistance
        elif current is None:
            current = voltage / max(resistance, EPSILON)
        elif resistance is None:
            resistance = voltage / max(current, EPSILON)

        if validate:
            if voltage < 0:
                raise ValueError(f"voltage must be ≥ 0, got {voltage}")
            if current < 0:
                raise ValueError(f"current must be ≥ 0, got {current}")
            if resistance <= 0:
                raise ValueError(f"resistance must be > 0, got {resistance}")

        # Power dissipation: P = VI = I²R = V²/R
        power = voltage * current

        return {
            "voltage": voltage,
            "current": current,
            "current_mA": current * 1000,
            "resistance": resistance,
            "power": power,
            "power_mW": power * 1000,
        }

    @staticmethod
    def resistors_series(resistances: List[float], validate: bool = True) -> Dict:
        """
        Total resistance of resistors in series.
        Formula: R_total = R₁ + R₂ + ... + Rₙ

        CONSTRAINTS:
        - All resistances > 0
        - At least 2 resistors

        Returns:
            Total resistance
        """
        if validate:
            if len(resistances) < 2:
                raise ValueError(f"Need at least 2 resistors, got {len(resistances)}")
            if any(r <= 0 for r in resistances):
                raise ValueError("All resistances must be > 0")

        total = sum(resistances)

        return {
            "resistances": resistances,
            "n_resistors": len(resistances),
            "total_resistance": total,
            "configuration": "series",
        }

    @staticmethod
    def resistors_parallel(resistances: List[float], validate: bool = True) -> Dict:
        """
        Total resistance of resistors in parallel.
        Formula: 1/R_total = 1/R₁ + 1/R₂ + ... + 1/Rₙ

        CONSTRAINTS:
        - All resistances > 0
        - At least 2 resistors

        Returns:
            Total resistance
        """
        if validate:
            if len(resistances) < 2:
                raise ValueError(f"Need at least 2 resistors, got {len(resistances)}")
            if any(r <= 0 for r in resistances):
                raise ValueError("All resistances must be > 0")

        # Sum of reciprocals
        reciprocal_sum = sum(1 / max(r, EPSILON) for r in resistances)
        total = 1 / max(reciprocal_sum, EPSILON)

        return {
            "resistances": resistances,
            "n_resistors": len(resistances),
            "total_resistance": total,
            "configuration": "parallel",
            "note": "Total resistance is less than smallest individual resistance",
        }

    @staticmethod
    def rc_circuit_charging(
        voltage: float,
        resistance: float,
        capacitance: float,
        time: float,
        validate: bool = True,
    ) -> Dict:
        """
        RC circuit charging analysis.
        Formula: V(t) = V₀(1 - e^(-t/RC))
                 Q(t) = Q_max(1 - e^(-t/RC))

        CONSTRAINTS:
        - voltage > 0
        - resistance > 0
        - capacitance > 0
        - time ≥ 0

        Returns:
            Voltage and charge at time t
        """
        if validate:
            if voltage <= 0:
                raise ValueError(f"voltage must be > 0, got {voltage}")
            if resistance <= 0:
                raise ValueError(f"resistance must be > 0, got {resistance}")
            if capacitance <= 0:
                raise ValueError(f"capacitance must be > 0, got {capacitance}")
            if time < 0:
                raise ValueError(f"time must be ≥ 0, got {time}")

        # Time constant
        tau = resistance * capacitance

        # Maximum charge
        Q_max = capacitance * voltage

        # Voltage at time t
        v_t = voltage * (1 - math.exp(-time / tau))

        # Charge at time t
        q_t = Q_max * (1 - math.exp(-time / tau))

        # Current at time t
        i_t = (voltage / resistance) * math.exp(-time / tau)

        # Number of time constants elapsed
        time_constants = time / tau

        return {
            "voltage_source": voltage,
            "resistance": resistance,
            "capacitance": capacitance,
            "time_constant_tau": tau,
            "time": time,
            "time_constants_elapsed": time_constants,
            "voltage_at_t": v_t,
            "charge_at_t": q_t,
            "current_at_t": i_t,
            "percent_charged": (v_t / voltage) * 100,
        }

    @staticmethod
    def power_dissipation(
        voltage: float = None,
        current: float = None,
        resistance: float = None,
        validate: bool = True,
    ) -> Dict:
        """
        Calculate power dissipation in a resistor.
        Formulas: P = VI = I²R = V²/R
        Provide any 2 parameters.

        Returns:
            Power and all circuit parameters
        """
        # Use Ohm's law to get all parameters first
        ohm_result = CircuitsCalculator.ohms_law(
            voltage=voltage, current=current, resistance=resistance, validate=validate
        )

        # Power already calculated in ohms_law
        power = ohm_result["power"]

        # Energy dissipated per hour
        energy_per_hour = power * 3600  # Joules
        energy_per_hour_kWh = power * 1 / 1000  # kWh

        return {
            **ohm_result,
            "energy_per_hour_J": energy_per_hour,
            "energy_per_hour_kWh": energy_per_hour_kWh,
        }


class ElectromagnetismCalculator:
    """
    Comprehensive electromagnetism calculator.
    """

    def __init__(self):
        self.electrostatics = ElectrostaticsCalculator()
        self.magnetism = MagnetismCalculator()
        self.circuits = CircuitsCalculator()

    def electromagnetic_wave_properties(
        self, frequency: float = None, wavelength: float = None, validate: bool = True
    ) -> Dict:
        """
        Electromagnetic wave relationship.
        Formula: c = fλ

        CONSTRAINTS:
        - Provide exactly one of: frequency or wavelength
        - frequency > 0 (Hz)
        - wavelength > 0 (m)

        Returns:
            All wave properties
        """
        params_given = sum([frequency is not None, wavelength is not None])

        if params_given != 1:
            raise ValueError("Must provide exactly one of: frequency or wavelength")

        if frequency is not None:
            if validate and frequency <= 0:
                raise ValueError(f"frequency must be > 0, got {frequency}")
            wavelength = c / frequency
        else:
            if validate and wavelength <= 0:
                raise ValueError(f"wavelength must be > 0, got {wavelength}")
            frequency = c / wavelength

        # Period
        period = 1 / frequency

        # Angular frequency
        angular_frequency = 2 * math.pi * frequency

        # Wave number
        wave_number = 2 * math.pi / wavelength

        # Energy of photon: E = hf
        h = 6.62607015e-34  # Planck's constant
        photon_energy = h * frequency
        photon_energy_eV = photon_energy / e

        return {
            "frequency": frequency,
            "frequency_MHz": frequency / 1e6,
            "wavelength": wavelength,
            "wavelength_nm": wavelength * 1e9,
            "period": period,
            "angular_frequency": angular_frequency,
            "wave_number": wave_number,
            "photon_energy_J": photon_energy,
            "photon_energy_eV": photon_energy_eV,
            "speed": c,
        }


# Example usage and testing
if __name__ == "__main__":
    print("=" * 80)
    print("ELECTROMAGNETISM CALCULATOR - DEMO")
    print("=" * 80)

    calc = ElectromagnetismCalculator()

    # Example 1: Coulomb's Law
    print("\n1. COULOMB'S LAW (Two Charges)")
    print("-" * 40)
    force = calc.electrostatics.coulombs_law(
        charge1=1e-6, charge2=-2e-6, distance=0.1
    )  # 1 μC  # -2 μC  # 10 cm
    print(
        f"Charges: {force['charge1'] * 1e6:.1f} μC and {force['charge2'] * 1e6:.1f} μC"
    )
    print(f"Distance: {force['distance'] * 100:.0f} cm")
    print(f"Force: {force['force_magnitude']:.6f} N")
    print(f"Interaction: {force['interaction_type']}")

    # Example 2: Electric Field
    print("\n2. ELECTRIC FIELD (Point Charge)")
    print("-" * 40)
    field = calc.electrostatics.electric_field_point_charge(
        charge=5e-9, distance=0.05
    )  # 5 nC  # 5 cm
    print(f"Charge: {field['charge'] * 1e9:.1f} nC")
    print(f"Distance: {field['distance'] * 100:.0f} cm")
    print(f"Electric field: {field['field_magnitude']:.2f} N/C")
    print(f"Direction: {field['field_direction']}")

    # Example 3: Capacitor
    print("\n3. CAPACITOR")
    print("-" * 40)
    cap = calc.electrostatics.capacitance(
        capacitance_value=100e-6, voltage=12
    )  # 100 μF  # 12 V
    print(f"Capacitance: {cap['capacitance_uF']:.0f} μF")
    print(f"Voltage: {cap['voltage']:.0f} V")
    print(f"Charge stored: {cap['charge'] * 1e3:.2f} mC")
    print(f"Energy stored: {cap['energy_stored_mJ']:.2f} mJ")

    # Example 4: Magnetic Force
    print("\n4. MAGNETIC FORCE ON MOVING CHARGE")
    print("-" * 40)
    mag_force = calc.magnetism.magnetic_force_on_charge(
        charge=e,
        velocity=1e6,
        magnetic_field=0.5,
        angle_degrees=90,  # Electron charge  # 1 million m/s  # 0.5 Tesla
    )
    print(f"Charge: {mag_force['charge'] / e:.2f}e")
    print(f"Velocity: {mag_force['velocity']:.0e} m/s")
    print(f"B-field: {mag_force['magnetic_field']:.2f} T")
    print(f"Force: {mag_force['force']:.2e} N")

    # Example 5: Faraday's Law
    print("\n5. ELECTROMAGNETIC INDUCTION")
    print("-" * 40)
    emf = calc.magnetism.faradays_law(
        n_turns=500, flux_change=0.01, time_interval=0.1
    )  # 0.01 Wb  # 0.1 s
    print(f"Coil turns: {emf['n_turns']}")
    print(f"Flux change: {emf['flux_change']:.3f} Wb")
    print(f"Time: {emf['time_interval']:.2f} s")
    print(f"Induced EMF: {emf['induced_emf']:.1f} V")

    # Example 6: Ohm's Law
    print("\n6. OHM'S LAW")
    print("-" * 40)
    ohm = calc.circuits.ohms_law(voltage=9, resistance=1000)
    print(f"Voltage: {ohm['voltage']:.0f} V")
    print(f"Resistance: {ohm['resistance']:.0f} Ω")
    print(f"Current: {ohm['current_mA']:.1f} mA")
    print(f"Power: {ohm['power_mW']:.1f} mW")

    # Example 7: RC Circuit
    print("\n7. RC CIRCUIT CHARGING")
    print("-" * 40)
    rc = calc.circuits.rc_circuit_charging(
        voltage=5,
        resistance=10000,
        capacitance=100e-6,
        time=1.0,  # 10 kΩ  # 100 μF  # 1 second
    )
    print(f"Source: {rc['voltage_source']:.0f} V")
    print(f"Time constant τ: {rc['time_constant_tau']:.3f} s")
    print(
        f"After {rc['time']:.1f}s: {rc['voltage_at_t']:.2f} V ({rc['percent_charged']:.1f}% charged)"
    )

    # Example 8: EM Wave
    print("\n8. ELECTROMAGNETIC WAVE")
    print("-" * 40)
    wave = calc.electromagnetic_wave_properties(frequency=100e6)  # 100 MHz (FM radio)
    print(f"Frequency: {wave['frequency_MHz']:.1f} MHz")
    print(f"Wavelength: {wave['wavelength']:.2f} m")
    print(f"Period: {wave['period'] * 1e9:.2f} ns")
    print(f"Photon energy: {wave['photon_energy_eV']:.2e} eV")

    print("\n" + "=" * 80)
