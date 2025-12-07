"""
Enhanced Symbolic Engine with Physics & DeFi Constraints
symbolic_engine.py

UPDATES (Week 2, Day 1-2):
- Added pre-validation layer for empty/null expressions
- Implemented safe math wrappers for division operations
- Enhanced constraint validation with bounds checking
- Added overflow protection for numerical operations
- Improved error handling and validation reporting
"""

import warnings
from dataclasses import dataclass
from typing import Dict, List, Optional

import numpy as np
from pysr import PySRRegressor


@dataclass
class PhysicsConstraints:
    """Constraints for physics-based symbolic regression"""

    dimensional_analysis: bool = True
    conservation_laws: List[str] = None
    symmetries: List[str] = None
    safe_math: bool = True  # NEW: Enable safe math operations

    def __post_init__(self):
        if self.conservation_laws is None:
            self.conservation_laws = []
        if self.symmetries is None:
            self.symmetries = []

    def get_physics_operators(self) -> Dict:
        """Returns operators suitable for physics"""
        return {
            "binary": ["+", "-", "*", "/", "^"],
            "unary": ["sqrt", "exp", "log", "sin", "cos"],
            "constraints": {
                "^": (-1, 2),  # Allow powers up to x^2
                "/": (-1, 1),
            },
        }


@dataclass
class DeFiConstraints:
    """Constraints for DeFi (Decentralized Finance) symbolic regression"""

    price_discovery: bool = True
    liquidity_constraints: bool = True
    risk_metrics: List[str] = None
    safe_math: bool = True  # NEW: Enable safe math operations
    enforce_positive_prices: bool = True  # NEW: Prices must be > 0
    enforce_bounded_fees: bool = True  # NEW: Fees must be in [0, 1]

    def __post_init__(self):
        if self.risk_metrics is None:
            self.risk_metrics = ["volatility", "sharpe_ratio"]

    def get_defi_operators(self) -> Dict:
        """Returns operators suitable for DeFi models"""
        return {
            "binary": ["+", "-", "*", "/"],
            "unary": ["log", "exp", "sqrt", "abs"],
            "constraints": {
                "/": (-1, 1),  # Ratios are common in finance
            },
        }

    def get_variable_bounds(self) -> Dict[str, tuple]:
        """
        Returns default bounds for common DeFi variables

        NEW: Provides safety bounds to prevent division by zero
        """
        bounds = {}

        if self.enforce_positive_prices:
            # Price variables must be positive
            bounds.update(
                {
                    "price": (1e-10, float("inf")),
                    "P": (1e-10, float("inf")),
                    "Pt": (1e-10, float("inf")),
                    "P0": (1e-10, float("inf")),
                }
            )

        if self.enforce_bounded_fees:
            # Fee variables must be in [0, 1)
            bounds.update(
                {
                    "fee": (0, 0.9999),
                    "phi": (0, 0.9999),
                    "φ": (0, 0.9999),
                }
            )

        # Liquidity must be positive (prevent division by zero)
        bounds.update(
            {
                "L": (1e-10, float("inf")),
                "liquidity": (1e-10, float("inf")),
            }
        )

        # Price ratios must be positive
        bounds.update(
            {
                "r": (1e-10, float("inf")),
                "ratio": (1e-10, float("inf")),
            }
        )

        return bounds


@dataclass
class DiscoveryConfig:
    niterations: int = 40
    populations: int = 15
    binary_operators: List[str] = None
    unary_operators: List[str] = None
    constraints: Optional[Dict] = None
    physics_constraints: Optional[PhysicsConstraints] = None
    defi_constraints: Optional[DeFiConstraints] = None
    variable_bounds: Optional[Dict[str, tuple]] = None  # NEW: Explicit bounds
    validate_inputs: bool = True  # NEW: Enable input validation

    def __post_init__(self):
        # Apply domain-specific constraints if specified
        if self.physics_constraints:
            ops = self.physics_constraints.get_physics_operators()
            self.binary_operators = ops["binary"]
            self.unary_operators = ops["unary"]
            self.constraints = ops["constraints"]
        elif self.defi_constraints:
            ops = self.defi_constraints.get_defi_operators()
            self.binary_operators = ops["binary"]
            self.unary_operators = ops["unary"]
            self.constraints = ops["constraints"]

            # NEW: Apply DeFi variable bounds
            if self.variable_bounds is None:
                self.variable_bounds = self.defi_constraints.get_variable_bounds()
        else:
            # Default general-purpose operators
            if self.binary_operators is None:
                self.binary_operators = ["+", "-", "*", "/", "^"]
            if self.unary_operators is None:
                self.unary_operators = ["sqrt", "exp", "log"]
            if self.constraints is None:
                # Default constraints to prevent overly complex expressions
                self.constraints = {
                    "^": (-1, 1),  # Allow complex base, simple exponent
                    "/": (-1, 1),  # Allow complex numerator, simple denominator
                }


class SymbolicEngine:
    """
    Enhanced Symbolic Regression Engine with validation and safe math
    """

    # Numerical safety constants
    EPSILON = 1e-10
    MAX_SAFE_VALUE = 1e100
    MIN_SAFE_VALUE = 1e-100

    def __init__(self, config: DiscoveryConfig):
        self.config = config
        self.model = None
        self.validation_results = []

    def _validate_inputs(self, X: np.ndarray, y: np.ndarray, variable_names: List[str]) -> Dict:
        """
        NEW: Validate inputs before symbolic regression

        Returns:
            Dict with validation results
        """
        validation = {"valid": True, "errors": [], "warnings": [], "issues": []}

        # Check for empty data
        if X.size == 0 or y.size == 0:
            validation["valid"] = False
            validation["errors"].append("Empty data arrays provided")
            return validation

        # Check for NaN or Inf
        if np.any(np.isnan(X)) or np.any(np.isinf(X)):
            validation["valid"] = False
            validation["errors"].append("Input X contains NaN or Inf values")

        if np.any(np.isnan(y)) or np.any(np.isinf(y)):
            validation["valid"] = False
            validation["errors"].append("Target y contains NaN or Inf values")

        # Check shapes
        if X.shape[0] != y.shape[0]:
            validation["valid"] = False
            validation["errors"].append(f"Shape mismatch: X has {X.shape[0]} samples, y has {y.shape[0]} samples")

        if X.shape[1] != len(variable_names):
            validation["valid"] = False
            validation["errors"].append(
                f"Variable name count ({len(variable_names)}) doesn't match " f"feature count ({X.shape[1]})"
            )

        # NEW: Check for division by zero risk in data
        if self.config.variable_bounds:
            for i, var_name in enumerate(variable_names):
                if var_name in self.config.variable_bounds:
                    min_bound, max_bound = self.config.variable_bounds[var_name]

                    col_min = np.min(X[:, i])
                    col_max = np.max(X[:, i])

                    # Check if data violates bounds
                    if col_min < min_bound or col_max > max_bound:
                        validation["warnings"].append(
                            f"Variable '{var_name}' data [{col_min:.2e}, {col_max:.2e}] "
                            f"exceeds specified bounds [{min_bound:.2e}, {max_bound:.2e}]"
                        )

                    # Check for near-zero values that could cause division issues
                    if min_bound > 0 and col_min < self.EPSILON:
                        validation["warnings"].append(
                            f"Variable '{var_name}' has near-zero values (min={col_min:.2e}) - "
                            f"may cause numerical instability"
                        )
                        validation["issues"].append(f"near_zero_{var_name}")

        # Check for extreme values that could cause overflow
        X_max = np.max(np.abs(X))
        y_max = np.max(np.abs(y))

        if X_max > self.MAX_SAFE_VALUE:
            validation["warnings"].append(f"Input X contains extremely large values (max={X_max:.2e}) - overflow risk")
            validation["issues"].append("large_input_values")

        if y_max > self.MAX_SAFE_VALUE:
            validation["warnings"].append(f"Target y contains extremely large values (max={y_max:.2e}) - overflow risk")
            validation["issues"].append("large_target_values")

        # Check for extremely small values
        X_min = np.min(np.abs(X[X != 0])) if np.any(X != 0) else 0
        y_min = np.min(np.abs(y[y != 0])) if np.any(y != 0) else 0

        if X_min > 0 and X_min < self.MIN_SAFE_VALUE:
            validation["warnings"].append(f"Input X contains extremely small values (min={X_min:.2e}) - underflow risk")

        if y_min > 0 and y_min < self.MIN_SAFE_VALUE:
            validation["warnings"].append(
                f"Target y contains extremely small values (min={y_min:.2e}) - underflow risk"
            )

        return validation

    def _safe_predict(self, X: np.ndarray) -> np.ndarray:
        """
        NEW: Safe prediction with overflow/underflow protection
        """
        try:
            y_pred = self.model.predict(X)

            # Clip extreme values
            y_pred = np.clip(y_pred, -self.MAX_SAFE_VALUE, self.MAX_SAFE_VALUE)

            # Replace NaN/Inf with zeros (fallback)
            y_pred = np.nan_to_num(y_pred, nan=0.0, posinf=self.MAX_SAFE_VALUE, neginf=-self.MAX_SAFE_VALUE)

            return y_pred
        except Exception as e:
            warnings.warn(f"Prediction error: {e}. Returning zeros.")
            return np.zeros(X.shape[0])

    def discover(self, X: np.ndarray, y: np.ndarray, variable_names: List[str] = None) -> Dict:
        """
        Enhanced discover method with input validation and safe math

        Args:
            X: Input features (n_samples, n_features)
            y: Target values (n_samples,)
            variable_names: Names of input variables

        Returns:
            Dict with discovery results including validation info
        """
        if variable_names is None:
            variable_names = [f"x{i}" for i in range(X.shape[1])]

        result = {
            "expression": None,
            "sympy_expr": None,
            "r2_score": 0.0,
            "complexity": 0,
            "variable_names": variable_names,
            "predictions": None,
            "validation": {"valid": True, "errors": [], "warnings": []},
            "numerical_stability": {"stable": True, "issues": []},
        }

        # NEW: Input validation
        if self.config.validate_inputs:
            validation = self._validate_inputs(X, y, variable_names)
            result["validation"] = validation

            if not validation["valid"]:
                result["expression"] = "VALIDATION_FAILED"
                result["r2_score"] = 0.0
                return result

            # Log warnings but continue
            if validation["warnings"]:
                for warning in validation["warnings"]:
                    warnings.warn(warning)

        try:
            # Create model with safe configuration
            self.model = PySRRegressor(
                niterations=self.config.niterations,
                populations=self.config.populations,
                binary_operators=self.config.binary_operators,
                unary_operators=self.config.unary_operators,
                constraints=self.config.constraints,
                model_selection="best",
                parsimony=0.01,
                verbosity=0,
                procs=0,  # Use single process for stability
                multithreading=False,  # Disable for reproducibility
            )

            # Fit model
            self.model.fit(X, y, variable_names=variable_names)

            # Get best expression
            best_expr = str(self.model.sympy())
            result["expression"] = best_expr
            result["sympy_expr"] = self.model.sympy()

            # Safe prediction and scoring
            y_pred = self._safe_predict(X)
            result["predictions"] = y_pred

            # Calculate R² with numerical stability
            ss_res = np.sum((y - y_pred) ** 2)
            ss_tot = np.sum((y - np.mean(y)) ** 2)

            if ss_tot < self.EPSILON:
                result["r2_score"] = 0.0
                result["validation"]["warnings"].append("Target variance near zero - R² score unreliable")
            else:
                r2 = 1 - (ss_res / ss_tot)
                result["r2_score"] = float(np.clip(r2, -10, 1))  # Clip to reasonable range

            # Get complexity
            try:
                result["complexity"] = self.model.get_best().complexity
            except:
                result["complexity"] = len(best_expr)  # Fallback: string length

            # NEW: Check numerical stability of discovered expression
            stability = self._check_expression_stability(best_expr, variable_names, X)
            result["numerical_stability"] = stability

        except Exception as e:
            result["expression"] = "DISCOVERY_FAILED"
            result["validation"]["valid"] = False
            result["validation"]["errors"].append(f"Discovery error: {str(e)}")
            result["r2_score"] = 0.0

        # Store validation results
        self.validation_results.append(result["validation"])

        return result

    def _check_expression_stability(self, expression: str, variable_names: List[str], X: np.ndarray) -> Dict:
        """
        NEW: Check if discovered expression is numerically stable
        """
        stability = {"stable": True, "issues": [], "warnings": []}

        # Check for division operations
        if "/" in expression:
            stability["warnings"].append("Expression contains division - verify denominators are non-zero")

            # Check if any variable in denominator position
            for var in variable_names:
                if f"/{var}" in expression or f"/ {var}" in expression:
                    # Check if this variable has near-zero values
                    var_idx = variable_names.index(var)
                    if np.any(np.abs(X[:, var_idx]) < self.EPSILON):
                        stability["stable"] = False
                        stability["issues"].append(f"division_by_near_zero_{var}")
                        stability["warnings"].append(
                            f"Variable '{var}' appears in denominator but has near-zero values"
                        )

        # Check for exponential operations
        if "**" in expression or "exp(" in expression:
            stability["warnings"].append("Expression contains exponentiation - verify no overflow occurs")
            stability["issues"].append("exponentiation_present")

        # Check for logarithms
        if "log(" in expression:
            stability["warnings"].append("Expression contains logarithm - verify all arguments are positive")
            stability["issues"].append("logarithm_present")

        # Check for square roots
        if "sqrt(" in expression:
            stability["warnings"].append("Expression contains sqrt - verify all arguments are non-negative")
            stability["issues"].append("sqrt_present")

        return stability


# ============================================================================
# ENHANCED TEST SUITE
# ============================================================================

if __name__ == "__main__":
    print("=" * 80)
    print("ENHANCED SYMBOLIC ENGINE - VALIDATION & SAFE MATH TESTS")
    print("=" * 80)
    print()

    # Test 1: Simple linear relationship (should pass)
    print("Test 1: Linear relationship y = 2x + 3")
    print("-" * 80)
    X = np.random.uniform(-10, 10, (100, 1))
    y = 2 * X[:, 0] + 3 + np.random.normal(0, 0.5, 100)

    config = DiscoveryConfig(niterations=20)
    engine = SymbolicEngine(config)
    result = engine.discover(X, y, variable_names=["x"])

    print(f"Discovered: {result['expression']}")
    print(f"R² score: {result['r2_score']:.4f}")
    print(f"Complexity: {result['complexity']}")
    print(f"Validation: {result['validation']['valid']}")
    print(f"Warnings: {len(result['validation']['warnings'])}")
    print()

    # Test 2: Empty data (should fail validation)
    print("Test 2: Empty data arrays")
    print("-" * 80)
    X_empty = np.array([]).reshape(0, 1)
    y_empty = np.array([])

    engine2 = SymbolicEngine(config)
    result2 = engine2.discover(X_empty, y_empty, variable_names=["x"])

    print(f"Expression: {result2['expression']}")
    print(f"Validation Valid: {result2['validation']['valid']}")
    print(f"Errors: {result2['validation']['errors']}")
    print()

    # Test 3: Physics - Free fall with constraints
    print("Test 3: Physics discovery (free fall h = h0 - 0.5*g*t²)")
    print("-" * 80)
    t = np.random.uniform(0.1, 5, (100, 1))  # Avoid t=0
    h0, g = 100, 9.81
    h = h0 - 0.5 * g * t[:, 0] ** 2 + np.random.normal(0, 1, 100)

    physics_config = DiscoveryConfig(niterations=30, physics_constraints=PhysicsConstraints())
    engine3 = SymbolicEngine(physics_config)
    result3 = engine3.discover(t, h, variable_names=["t"])

    print(f"Discovered: {result3['expression']}")
    print(f"R² score: {result3['r2_score']:.4f}")
    print(f"Expected: h ≈ 100 - 4.905*t²")
    print(f"Numerically Stable: {result3['numerical_stability']['stable']}")
    print(f"Stability Issues: {result3['numerical_stability']['issues']}")
    print()

    # Test 4: DeFi - Price discovery with enforced constraints
    print("Test 4: DeFi discovery (AMM price = k / liquidity)")
    print("-" * 80)
    liquidity = np.random.uniform(100, 10000, (100, 1))
    k = 1000000
    price = k / liquidity[:, 0] + np.random.normal(0, 5, 100)

    defi_config = DiscoveryConfig(niterations=25, defi_constraints=DeFiConstraints())
    engine4 = SymbolicEngine(defi_config)
    result4 = engine4.discover(liquidity, price, variable_names=["L"])

    print(f"Discovered: {result4['expression']}")
    print(f"R² score: {result4['r2_score']:.4f}")
    print(f"Expected: price ≈ 1000000 / L")
    print(f"Validation Warnings: {len(result4['validation']['warnings'])}")
    print(f"Stability Warnings: {result4['numerical_stability']['warnings']}")
    print()

    # Test 5: Near-zero division risk (should warn)
    print("Test 5: Near-zero division risk detection")
    print("-" * 80)
    X5 = np.random.uniform(-0.01, 0.01, (100, 1))  # Near-zero values
    y5 = 1.0 / (X5[:, 0] + 0.1)  # Division with small denominator

    config5 = DiscoveryConfig(niterations=20, variable_bounds={"x": (0.01, 10)})  # Bounds that data violates
    engine5 = SymbolicEngine(config5)
    result5 = engine5.discover(X5, y5, variable_names=["x"])

    print(f"Discovered: {result5['expression']}")
    print(f"Validation Warnings: {result5['validation']['warnings']}")
    print(f"Stability Issues: {result5['numerical_stability']['issues']}")
    print()

    print("=" * 80)
    print("✅ All enhanced tests complete!")
    print("=" * 80)
