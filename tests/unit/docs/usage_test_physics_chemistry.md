test_physics_validation.py (700+ lines, 40+ tests)
Test Coverage:

Kinematics Tests (10 tests)

Negative/zero time validation
Invalid projectile angles
Negative initial heights
Circular motion parameter validation
Impossible deceleration detection
Boundary conditions at t=0

Dynamics Tests (6 tests)

Negative/zero mass validation
Negative distance in gravitational force
Negative friction coefficients
Negative spring constants
Zero coefficient boundary cases

Energy Tests (6 tests)

Negative mass validation
Negative gravity validation
Work calculation with negative forces
Efficiency > 100% detection
Perpendicular force (90°) returns zero work

Momentum Tests (4 tests)

Negative mass validation
Negative time validation
Momentum conservation verification
Energy conservation in elastic collisions

Thermodynamics Tests (9 tests)

Wrong parameter count detection
Negative P, V, T validation
Invalid gamma (γ ≤ 1)
Emissivity range [0,1] enforcement
Heat output > input detection
Carnot efficiency bounds

Electromagnetism Tests (9 tests)

Zero/negative distance validation
Capacitor parameter validation
Invalid dielectric constants
Angle range validation
RC circuit time constant verification

Edge Cases (6+ tests)

Zero velocity → zero KE
Equal mass collision velocity exchange
Gravitational force inverse-square law
180° work is negative

test_chemistry_validation.py (650+ lines, 40+ tests)
Test Coverage:

Rate Equations Tests (6 tests)

Negative rate constants
Negative concentrations
Mismatched lists
Negative reaction orders
Zero-order rate = k verification

Integrated Rate Laws Tests (7 tests)

Missing parameter detection
Negative time validation
Final > initial concentration detection
Zero initial concentration
Exponential decay verification

Arrhenius Tests (7 tests)

Negative activation energy
Zero Kelvin validation
Identical temperature detection
Temperature effect on rate constants
Negative pre-exponential factor

Half-Life Tests (9 tests)

Negative concentrations
Zero concentration validation
First-order concentration independence
Zero-order concentration dependence
Second-order half-life doubling
3 half-lives → 12.5% remaining

Equilibrium Constant Tests (6 tests)

Negative concentrations
Mismatched list lengths
Zero reactant detection
Q predicts reaction direction
ΔG° from K validation

Acid-Base Tests (9 tests)

pH range [0,14] enforcement
Ka/Kb parameter validation
Henderson-Hasselbalch validation
Equal concentrations → pH = pKa
Ka × Kb = Kw verification

Solubility Tests (6 tests)

Negative Ksp validation
Zero coefficients detection
Common ion effect verification
Ksp ↔ solubility reversibility

Edge Cases (6+ tests)

Zero concentration → zero rate
Very weak acids → pH ≈ 7
Zero activation energy → k = A
First-order data detection

Key Features:
✅ Comprehensive Coverage: 80+ tests covering all major calculations
✅ Error Message Validation: Uses pytest.raises(ValueError, match=...)
✅ Boundary Conditions: Tests edge cases like zero, negative, infinity
✅ Physical Laws: Verifies conservation laws and theoretical bounds
✅ Numerical Precision: Checks calculations within tolerance (1e-10)
✅ Clear Documentation: Each test has descriptive docstring
✅ Real-World Scenarios: Tests practical chemistry/physics problems
Running the Tests:
bash# Run all physics tests
pytest tests/unit/test_physics_validation.py -v

# Run all chemistry tests

pytest tests/unit/test_chemistry_validation.py -v

# Run specific test class

pytest tests/unit/test_physics_validation.py::TestKinematicsValidation -v

# Run with coverage

pytest tests/unit/ --cov=domains --cov-report=html
Both test suites are production-ready and follow pytest best practices! 🧪⚗️
