# Physics Formulas Reference

**Version:** 1.0.0
**Domain:** Classical Physics
**Last Updated:** December 2024

---

## Table of Contents

1. [Overview](#overview)
2. [Classical Mechanics](#classical-mechanics)
3. [Thermodynamics](#thermodynamics)
4. [Physical Constants](#physical-constants)
5. [Usage Examples](#usage-examples)
6. [Validation & Constraints](#validation--constraints)

---

## Overview

The Physics domain provides comprehensive implementations of classical mechanics and thermodynamics formulas with:

- **Rigorous constraint validation** - All physical constraints enforced
- **Safe mathematical operations** - Epsilon guards for division
- **SI unit system** - All calculations in SI units
- **Physical constants** - CODATA 2018 recommended values
- **Comprehensive documentation** - Detailed docstrings and examples

### Module Structure

```
domains/physics/
├── __init__.py                    # Main module with constants
├── mechanics_formulas.py          # Classical mechanics
├── thermodynamics_formulas.py     # Thermodynamics
└── docs/
    └── physics_formulas.md        # This documentation
```

---

## Classical Mechanics

### Kinematics (Motion)

#### 1. Velocity from Displacement

```python
v = Δx / Δt
```

**Constraints:**

- `time > 0`

**Example:**

```python
from domains.physics import KinematicsCalculator

calc = KinematicsCalculator()
velocity = calc.velocity_from_displacement(
    displacement=100,  # meters
    time=10           # seconds
)
# Returns: 10 m/s
```

---

#### 2. Final Velocity (Constant Acceleration)

```python
v = v₀ + at
s = v₀t + ½at²
```

**Constraints:**

- `time ≥ 0`

**Example:**

```python
result = calc.final_velocity_constant_acceleration(
    initial_velocity=0,
    acceleration=9.8,  # m/s² (gravity)
    time=3
)
# Returns: {
#   'final_velocity': 29.4,
#   'displacement': 44.1,
#   'average_velocity': 14.7
# }
```

---

#### 3. Kinematic Equation (No Time)

```python
v² = v₀² + 2as
```

**Constraints:**

- `v₀² + 2as ≥ 0` (real solution exists)

**Example:**

```python
result = calc.velocity_from_kinetic_equation(
    initial_velocity=10,
    acceleration=-2,
    displacement=20
)
# Returns both forward and backward velocities
```

---

#### 4. Projectile Motion

```python
Range: R = (v₀² sin(2θ)) / g
Max Height: H = (v₀² sin²(θ)) / (2g)
Flight Time: t = 2v₀sin(θ) / g
```

**Constraints:**

- `initial_velocity ≥ 0`
- `angle ∈ [0, 90]` degrees
- `initial_height ≥ 0`
- `gravity > 0`

**Example:**

```python
projectile = calc.projectile_motion(
    initial_velocity=50,  # m/s
    angle_degrees=45,
    initial_height=2.0,
    gravity=9.8
)
# Returns complete trajectory analysis
```

---

#### 5. Circular Motion

```python
Angular velocity: ω = 2π/T = 2πf
Linear velocity: v = ωr
Centripetal acceleration: a = v²/r = ω²r
```

**Constraints:**

- `radius > 0`
- `period > 0` OR `angular_velocity ≥ 0` OR `linear_velocity ≥ 0`

**Example:**

```python
circular = calc.circular_motion(
    radius=5,
    period=10  # seconds
)
# Returns: {
#   'angular_velocity': 0.628 rad/s,
#   'linear_velocity': 3.14 m/s,
#   'centripetal_acceleration': 1.97 m/s²
# }
```

---

### Dynamics (Forces)

#### 6. Newton's Second Law

```python
F = ma
```

**Constraints:**

- `mass > 0`

**Example:**

```python
from domains.physics import DynamicsCalculator

calc = DynamicsCalculator()
force = calc.newtons_second_law(
    mass=10,          # kg
    acceleration=5    # m/s²
)
# Returns: force = 50 N
```

---

#### 7. Universal Gravitation

```python
F = G(m₁m₂)/r²
U = -G(m₁m₂)/r
```

**Constraints:**

- `mass1, mass2 > 0`
- `distance > 0`
- `G > 0` (default: 6.674×10⁻¹¹)

**Example:**

```python
gravity = calc.gravitational_force(
    mass1=5.972e24,   # Earth mass (kg)
    mass2=1000,       # Object mass (kg)
    distance=6.371e6  # Earth radius (m)
)
# Returns gravitational force and potential energy
```

---

#### 8. Friction Force

```python
f = μN
```

**Constraints:**

- `normal_force ≥ 0`
- `coefficient ≥ 0` (typically μ ∈ [0, 2])

**Example:**

```python
friction = calc.friction_force(
    normal_force=100,    # N
    coefficient=0.3,     # μ (kinetic)
    kinetic=True
)
# Returns: friction_force = 30 N
```

---

#### 9. Spring Force (Hooke's Law)

```python
F = -kx
U = ½kx²
```

**Constraints:**

- `spring_constant > 0`

**Example:**

```python
spring = calc.spring_force(
    displacement=0.1,      # m (10 cm)
    spring_constant=200    # N/m
)
# Returns: {
#   'force': -20 N,
#   'potential_energy': 1 J
# }
```

---

### Energy and Work

#### 10. Kinetic Energy

```python
KE = ½mv²
```

**Constraints:**

- `mass > 0`

**Example:**

```python
from domains.physics import EnergyCalculator

calc = EnergyCalculator()
ke = calc.kinetic_energy(mass=2, velocity=10)
# Returns: {
#   'kinetic_energy': 100 J,
#   'momentum': 20 kg·m/s
# }
```

---

#### 11. Gravitational Potential Energy

```python
PE = mgh
```

**Constraints:**

- `mass > 0`
- `gravity > 0`

**Example:**

```python
pe = calc.gravitational_potential_energy(
    mass=10,
    height=5,
    gravity=9.8
)
# Returns: potential_energy = 490 J
```

---

#### 12. Work Done

```python
W = F·d·cos(θ)
```

**Constraints:**

- `angle ∈ [0, 180]` degrees

**Example:**

```python
work = calc.work_done(
    force=100,
    displacement=5,
    angle_degrees=30
)
# Returns work in Joules
```

---

#### 13. Power

```python
P = W/t
```

**Constraints:**

- `time > 0`

**Example:**

```python
power = calc.power_from_work(work=1000, time=10)
# Returns: {
#   'power': 100 W,
#   'power_kilowatts': 0.1,
#   'power_horsepower': 0.134
# }
```

---

#### 14. Mechanical Efficiency

```python
η = (Useful Output / Total Input) × 100%
```

**Constraints:**

- `total_input > 0`
- `0 ≤ output ≤ input`

**Example:**

```python
efficiency = calc.efficiency(
    useful_output=750,
    total_input=1000
)
# Returns: efficiency_percent = 75%
```

---

## Thermodynamics

### Ideal Gas Law

#### 15. PV = nRT

```python
Pressure × Volume = n × R × Temperature
```

**Constraints:**

- `P, V, n, T > 0`
- Must provide exactly 3 of 4 parameters

**Example:**

```python
from domains.physics import IdealGasCalculator

calc = IdealGasCalculator()
gas = calc.ideal_gas_law(
    pressure=101325,  # Pa (1 atm)
    volume=0.0224,    # m³ (22.4 L)
    n_moles=1,
    temperature=None  # Will be calculated
)
# Returns: temperature = 273.15 K (0°C)
```

---

### Gas Processes

#### 16. Isothermal Process (Constant T)

```python
P₁V₁ = P₂V₂
W = nRT ln(V₂/V₁)
ΔU = 0, Q = W
```

**Constraints:**

- All `P, V, n, T > 0`

**Example:**

```python
iso = calc.isothermal_process(
    initial_pressure=200000,
    initial_volume=0.01,
    final_volume=0.02,
    n_moles=1,
    temperature=300
)
# Returns work done and final pressure
```

---

#### 17. Adiabatic Process (Q = 0)

```python
P₁V₁^γ = P₂V₂^γ
W = (P₁V₁ - P₂V₂)/(γ-1)
ΔU = -W
```

**Constraints:**

- `P, V > 0`
- `γ > 1` (typically 1.4 for diatomic gases)

**Example:**

```python
adiabatic = calc.adiabatic_process(
    initial_pressure=100000,
    initial_volume=0.01,
    final_volume=0.02,
    gamma=1.4
)
# Returns final pressure and work done
```

---

### Heat Transfer

#### 18. Conduction (Fourier's Law)

```python
Q = kA(ΔT)t/d
```

**Constraints:**

- `k > 0` (thermal conductivity)
- `A > 0` (area)
- `d > 0` (thickness)
- `T_hot > T_cold`
- `time > 0`

**Example:**

```python
from domains.physics import HeatTransferCalculator

calc = HeatTransferCalculator()
conduction = calc.conduction(
    thermal_conductivity=400,  # W/(m·K) - copper
    area=1.0,
    thickness=0.01,
    temp_hot=373.15,  # K (100°C)
    temp_cold=273.15, # K (0°C)
    time=3600
)
# Returns heat transferred in 1 hour
```

---

#### 19. Convection (Newton's Law of Cooling)

```python
Q = hA(ΔT)t
```

**Constraints:**

- `h > 0` (convection coefficient)
- `A > 0`
- `time > 0`

**Example:**

```python
convection = calc.convection(
    convection_coefficient=25,
    area=2.0,
    temp_surface=350,
    temp_fluid=300,
    time=60
)
```

---

#### 20. Radiation (Stefan-Boltzmann)

```python
Q = εσA(T₁⁴ - T₂⁴)t
```

**Constraints:**

- `ε ∈ (0, 1]` (emissivity)
- `A > 0`
- `T > 0` (Kelvin)
- `time > 0`

**Example:**

```python
radiation = calc.radiation(
    emissivity=0.9,
    area=1.0,
    temp_object=500,
    temp_surroundings=293.15,
    time=3600
)
```

---

### Entropy and Efficiency

#### 21. Entropy Change

```python
ΔS = Q/T
```

**Constraints:**

- `T > 0` (Kelvin)

**Example:**

```python
from domains.physics import EntropyCalculator

calc = EntropyCalculator()
entropy = calc.entropy_change_heat(
    heat=1000,
    temperature=300
)
# Returns: entropy_change = 3.33 J/K
```

---

#### 22. Carnot Efficiency

```python
η_carnot = 1 - T_c/T_h
```

**Constraints:**

- `T_h > T_c > 0`

**Example:**

```python
carnot = calc.carnot_efficiency(
    temp_hot=600,   # K
    temp_cold=300   # K
)
# Returns: efficiency = 50% (maximum theoretical)
```

---

## Physical Constants

### Universal Constants

```python
from domains.physics import PhysicsConstants

c = PhysicsConstants.SPEED_OF_LIGHT         # 299,792,458 m/s
G = PhysicsConstants.GRAVITATIONAL_CONSTANT # 6.674×10⁻¹¹ m³/(kg·s²)
h = PhysicsConstants.PLANCK_CONSTANT        # 6.626×10⁻³⁴ J·s
```

### Thermodynamic Constants

```python
R = PhysicsConstants.GAS_CONSTANT          # 8.314 J/(mol·K)
k_B = PhysicsConstants.BOLTZMANN_CONSTANT  # 1.381×10⁻²³ J/K
N_A = PhysicsConstants.AVOGADRO_NUMBER     # 6.022×10²³ mol⁻¹
σ = PhysicsConstants.STEFAN_BOLTZMANN      # 5.670×10⁻⁸ W/(m²·K⁴)
```

### Standard Conditions

```python
g = PhysicsConstants.STANDARD_GRAVITY      # 9.807 m/s²
P_std = PhysicsConstants.STANDARD_PRESSURE # 101,325 Pa
T_std = PhysicsConstants.STANDARD_TEMPERATURE # 273.15 K
```

### Accessing Constants

```python
from domains.physics import get_constant

c = get_constant('SPEED_OF_LIGHT')
g = get_constant('GRAVITY_EARTH')
```

---

## Usage Examples

### Example 1: Projectile Motion

```python
from domains.physics import MechanicsCalculator

calc = MechanicsCalculator()

# Baseball thrown at 45 degrees
result = calc.kinematics.projectile_motion(
    initial_velocity=40,  # m/s (~90 mph)
    angle_degrees=45,
    initial_height=2.0
)

print(f"Range: {result['range_horizontal']:.1f} m")
print(f"Max height: {result['max_height']:.1f} m")
print(f"Flight time: {result['total_flight_time']:.2f} s")
```

---

### Example 2: Free Fall

```python
# Object dropped from 100m
fall = calc.free_fall_analysis(height=100)

print(f"Time to ground: {fall['time_to_fall']:.2f} s")
print(f"Impact velocity: {fall['final_velocity']:.2f} m/s")
print(f"Impact velocity: {fall['final_velocity_kmh']:.1f} km/h")
```

---

### Example 3: Energy Conservation

```python
# Ball at 50m height
mass = 2  # kg
height = 50  # m

# Potential energy at top
pe_top = calc.energy.gravitational_potential_energy(mass, height)

# Kinetic energy at bottom (all PE converts to KE)
velocity_bottom = (2 * 9.8 * height)**0.5
ke_bottom = calc.energy.kinetic_energy(mass, velocity_bottom)

print(f"PE at top: {pe_top['potential_energy']:.0f} J")
print(f"KE at bottom: {ke_bottom['kinetic_energy']:.0f} J")
print(f"Energy conserved: {abs(pe_top['potential_energy'] - ke_bottom['kinetic_energy']) < 1}")
```

---

### Example 4: Heat Engine

```python
from domains.physics import ThermodynamicsCalculator

calc = ThermodynamicsCalculator()

# Steam engine analysis
engine = calc.heat_engine_analysis(
    heat_input=10000,   # J
    heat_output=7000    # J (waste heat)
)

print(f"Work output: {engine['work_output']} J")
print(f"Efficiency: {engine['efficiency_percent']:.1f}%")

# Compare to Carnot efficiency
carnot = calc.entropy.carnot_efficiency(
    temp_hot=500,  # K
    temp_cold=300  # K
)
print(f"Max theoretical efficiency: {carnot['efficiency_percent']:.1f}%")
```

---

### Example 5: Ideal Gas

```python
# Air at standard conditions
gas = calc.ideal_gas.ideal_gas_law(
    pressure=101325,    # Pa
    volume=1.0,         # m³
    n_moles=None,       # Calculate this
    temperature=293.15  # K (20°C)
)

print(f"Moles of air: {gas['n_moles']:.2f} mol")
print(f"Number of molecules: {gas['n_molecules']:.2e}")
print(f"RMS velocity: {gas['v_rms']:.0f} m/s")
```

---

## Validation & Constraints

### Constraint Philosophy

All formulas enforce **physical constraints** to prevent unphysical results:

1. **Positive quantities:** Mass, time, temperature (K), distances must be > 0
2. **Valid ranges:** Angles in appropriate ranges, efficiencies ≤ 100%
3. **Physical laws:** Energy conservation, second law of thermodynamics
4. **Safe math:** Epsilon guards prevent division by zero

### Example: Enforced Constraints

```python
# This will raise ValueError: time must be > 0
try:
    v = calc.velocity_from_displacement(100, time=-5)
except ValueError as e:
    print(f"Caught constraint violation: {e}")

# This will raise ValueError: efficiency > 100% violates physics
try:
    eff = calc.efficiency(useful_output=150, total_input=100)
except ValueError as e:
    print(f"Caught violation: {e}")
```

### Validation Parameter

All functions have `validate: bool = True` parameter:

```python
# With validation (default, recommended)
result = calc.some_formula(param1, param2, validate=True)

# Without validation (faster, use only if pre-validated)
result = calc.some_formula(param1, param2, validate=False)
```

---

## Unit Conversions

### Temperature

```python
from domains.physics import UnitConverter, convert_temperature

converter = UnitConverter()

# Manual conversion
kelvin = converter.celsius_to_kelvin(25)      # 298.15 K
fahrenheit = converter.celsius_to_fahrenheit(25)  # 77.0 °F

# Quick conversion
temp_k = convert_temperature(100, 'C', 'K')   # 373.15 K
temp_f = convert_temperature(373.15, 'K', 'F')  # 212.0 °F
```

### Length

```python
km = converter.meters_to_kilometers(5000)  # 5.0 km
feet = converter.meters_to_feet(10)        # 32.8 ft
```

### Pressure

```python
atm = converter.pascal_to_atmosphere(202650)  # 2.0 atm
bar = converter.pascal_to_bar(100000)         # 1.0 bar
```

### Energy

```python
cal = converter.joules_to_calories(4184)  # 1000 cal
eV = converter.joules_to_electronvolts(1.602e-19)  # 1.0 eV
```

### Speed

```python
kmh = converter.meters_per_second_to_kmh(27.78)  # 100 km/h
mps = converter.kmh_to_meters_per_second(100)    # 27.78 m/s
```

---

## Testing

### Running Tests

```bash
# Run all physics tests
pytest tests/domains/physics/ -v

# Run specific test files
pytest tests/domains/physics/test_mechanics.py -v
pytest tests/domains/physics/test_thermodynamics.py -v

# Run with coverage
pytest tests/domains/physics/ --cov=domains.physics --cov-report=html
```

### Example Test

```python
import pytest
from domains.physics import KinematicsCalculator

def test_projectile_motion():
    calc = KinematicsCalculator()

    # 45-degree launch should give maximum range
    result = calc.projectile_motion(
        initial_velocity=20,
        angle_degrees=45,
        initial_height=0
    )

    # Verify range formula: R = v₀²sin(2θ)/g
    expected_range = (20**2) / 9.8  # sin(90°) = 1
    assert abs(result['range_horizontal'] - expected_range) < 0.1

    # Max height at 45° should be v₀²/(4g)
    expected_height = (20**2) / (4 * 9.8)
    assert abs(result['max_height'] - expected_height) < 0.1
```

---

## References

1. **Physical Constants:** CODATA 2018 Recommended Values
2. **SI Units:** International System of Units (SI)
3. **Formulas:**
   - Halliday, Resnick & Walker - *Fundamentals of Physics*
   - Serway & Jewett - *Physics for Scientists and Engineers*
   - Cengel & Boles - *Thermodynamics: An Engineering Approach*

---

## Version History

- **v1.0.0** (December 2024)
  - Initial release
  - Classical mechanics implementation
  - Thermodynamics implementation
  - Physical constants from CODATA 2018
  - Comprehensive validation and constraints
  - Full documentation and examples

---

## Contributing

To add new formulas or improve existing ones:

1. Follow existing code patterns
2. Include rigorous constraint validation
3. Add comprehensive docstrings
4. Provide usage examples
5. Add unit tests
6. Update this documentation

---

## License

Part of the HypatiaX Physics Module.

---

**For questions or issues, please see the main project documentation.**
