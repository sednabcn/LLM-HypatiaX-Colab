from mechanics_formulas import MechanicsCalculator
from thermodynamics_formulas import ThermodynamicsCalculator

# Projectile motion

mech = MechanicsCalculator()
projectile = mech.kinematics.projectile_motion(
    initial_velocity=50,  # m/s
    angle_degrees=45
)
print(f"Range: {projectile['range_horizontal']:.1f} m")

# Ideal gas law

thermo = ThermodynamicsCalculator()
gas = thermo.ideal_gas.ideal_gas_law(
    pressure=101325,  # Pa
    volume=0.0224,    # m³
    n_moles=1,
    temperature=None  # Calculate this
)
print(f"Temperature: {gas['temperature']:.2f} K")
